from functools import wraps
from flask import request, jsonify, redirect, url_for, current_app, flash, abort
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, get_jwt
from app import db # <--- CRITICAL CHANGE HERE: from app import db
import jwt # This is python-jwt, not Flask-JWT-Extended's internal jwt object
from datetime import datetime
from flask_login import current_user # Keep if Flask-Login is still used for some logic

__all__ = [
    'require_api_key',
    'track_activity',
    'audit_log',
    'admin_login_required', # Keep if needed for Flask-Login based admin
    'admin_required',       # Keep for JWT-based admin
    'client_required',
    'secure_admin_required' # New secure admin decorator
]


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Testing hook - bypass all checks if in testing mode
        if current_app.config.get('TESTING'):
            return f(*args, **kwargs)
            
        from app.models.client import Client  # Corrected absolute import
        
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            return jsonify({'error': 'API key missing'}), 401

        client = Client.query.filter_by(api_key=api_key).first()
        if not client:
            return jsonify({'error': 'Invalid API key'}), 403

        if not client.check_rate_limit():
            current_app.logger.warning(f"Rate limit exceeded for client {client.id}")
            return jsonify({
                'error': 'Rate limit exceeded',
                'limit': client.rate_limit,
                'message': 'You have exceeded your daily request limit'
            }), 429

        # Assuming client.log_request exists and works with the new db setup
        # It's better to pass `request` to the method if it needs request details
        client.log_request() # Update this if log_request needs arguments
        return f(*args, **kwargs)
    return decorated

def track_activity(action=None):
    """
    Decorator to track user activity in the audit log.
    
    Args:
        action (str, optional): The action being performed. If not provided, 
                             it will use the function name as the action.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.models.audit import AuditTrail # Corrected absolute import
            from flask import current_app

            # Get the action from the decorator or use the function name
            action_name = action or f.__name__.replace('_', ' ').title()
            
            # Get user ID from JWT token if available
            user_id = None
            user_type = None
            
            # First check for Flask-Login authentication
            if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                user_id = current_user.id
                
                # Determine user type based on attributes
                if hasattr(current_user, 'is_client') and current_user.is_client():
                    user_type = 'client'
                elif hasattr(current_user, 'is_admin') and current_user.is_admin():
                    user_type = 'admin'
                else:
                    user_type = 'user'
                    
                current_app.logger.debug(f"Flask-Login auth detected: user_id={user_id}, user_type={user_type}")
            else:
                # Try JWT if Flask-Login is not authenticated
                try:
                    # Try to get user ID from JWT
                    identity = get_jwt_identity()
                    if identity and isinstance(identity, dict):
                        user_id = identity.get('id')
                        user_type = identity.get('type', 'unknown')
                    elif identity:
                        # Handle case where identity is just an ID (e.g., from sub claim)
                        user_id = identity
                        user_type = 'client'  # Default to client if type not specified
                        
                    current_app.logger.debug(f"JWT auth detected: user_id={user_id}, user_type={user_type}")
                except Exception as e:
                    current_app.logger.debug(f"No authentication found: {str(e)}")
                    pass
                
            # Get IP address and user agent
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            
            # Record the activity
            if user_id:
                audit = AuditTrail(
                    user_id=user_id,
                    action_type=action_name,
                    entity_type='activity',
                    entity_id=user_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    new_value={
                        'endpoint': request.endpoint,
                        'method': request.method,
                        'path': request.path,
                        'args': dict(request.args),
                        'timestamp': datetime.utcnow().isoformat(),
                        'user_type': user_type  # Add user_type to details instead
                    }
                )
                db.session.add(audit)
                try:
                    db.session.commit()
                except Exception as e:
                    current_app.logger.error(f"Failed to log activity: {str(e)}")
                    db.session.rollback()
            
            # Call the original function
            return f(*args, **kwargs)
        return decorated_function
        
    # Return the decorator function
    return decorator

def audit_log(action=None, details=None):
    """
    Decorator to log actions to the audit trail.
    
    Args:
        action (str, optional): The action being performed. If not provided,
                             it will use the function name as the action.
        details (dict, optional): Additional details to include in the audit log.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.models.audit import AuditTrail, AuditActionType # Corrected absolute import
            from flask import current_app

            # Get the action from the decorator or use the function name
            action_name = action or f.__name__.replace('_', ' ').title()
            
            # Get user ID from JWT token if available
            user_id = None
            user_type = None
            entity_id = None
            entity_type = None
            
            # First check for Flask-Login authentication
            if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                user_id = current_user.id
                
                # Determine user type based on attributes
                if hasattr(current_user, 'is_client') and current_user.is_client():
                    user_type = 'client'
                    if hasattr(current_user, 'client') and current_user.client:
                        entity_id = current_user.client.id
                        entity_type = 'client'
                elif hasattr(current_user, 'is_admin') and current_user.is_admin():
                    user_type = 'admin'
                else:
                    user_type = 'user'
                    
                current_app.logger.debug(f"Flask-Login auth in audit_log: user_id={user_id}, user_type={user_type}")
            else:
                # Try JWT if Flask-Login is not authenticated
                try:
                    # Try to get user ID from JWT
                    identity = get_jwt_identity()
                    if identity and isinstance(identity, dict):
                        user_id = identity.get('id')
                        user_type = identity.get('type', 'unknown')
                    elif identity:
                        user_id = identity
                        user_type = 'client'
                        
                    current_app.logger.debug(f"JWT auth detected in audit_log: user_id={user_id}, user_type={user_type}")
                except Exception as e:
                    current_app.logger.debug(f"No JWT authentication found: {str(e)}")
                    pass
                
            # Get IP address and user agent
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            
            # Prepare audit details
            audit_details = {
                'endpoint': request.endpoint,
                'method': request.method,
                'path': request.path,
                'args': dict(request.args),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Add any additional details
            if details and isinstance(details, dict):
                audit_details.update(details)
            
            # Record the audit trail
            if user_id:
                audit = AuditTrail(
                    user_id=user_id,
                    action_type=action_name,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    new_value=audit_details
                )
                db.session.add(audit)
                try:
                    db.session.commit()
                except Exception as e:
                    current_app.logger.error(f"Failed to log audit trail: {str(e)}")
                    db.session.rollback()
            
            # Call the original function
            return f(*args, **kwargs)
        return decorated_function
        
    # Return the decorator function
    return decorator

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from app.models.admin import AdminUser
        
        try:
            # Verify JWT token and get admin ID
            verify_jwt_in_request()
            admin_id = get_jwt_identity()
            
            # Get admin user from database
            admin = AdminUser.query.get(admin_id)
            if not admin:
                return jsonify({'error': 'Admin not found'}), 401
            
            # Pass the admin object to the decorated function
            return f(admin, *args, **kwargs)
            
        except Exception as e:
            current_app.logger.error(f"Admin authentication error: {str(e)}")
            return jsonify({'error': 'Unauthorized', 'details': str(e)}), 401
    return decorated

def admin_login_required(f):
    """
    Decorator to verify admin authentication and authorization using Flask-Login.
    
    Redirects to admin login if not authenticated.
    
    This decorator should be used for views that require admin access.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Log the current user state
        current_app.logger.debug(f"[ADMIN CHECK] User: {current_user}")
        current_app.logger.debug(f"[ADMIN CHECK] Is authenticated: {current_user.is_authenticated}")
        current_app.logger.debug(f"[ADMIN CHECK] Is admin: {hasattr(current_user, 'is_admin') and current_user.is_admin}")
        
        # Check authentication
        if not current_user.is_authenticated:
            current_app.logger.warning("[ADMIN CHECK] User not authenticated")
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('admin.admin_login', next=request.url))
        
        # Check admin privileges
        if not hasattr(current_user, 'is_superuser') or not current_user.is_superuser:
            current_app.logger.warning("[ADMIN CHECK] User lacks admin privileges")
            flash('You need admin privileges to access this page.', 'error')
            # If user is already on the login page, don't redirect to avoid loop
            if request.endpoint != 'admin.admin_login':
                return redirect(url_for('admin.admin_login', next=request.url))
            return "Unauthorized: Admin access required", 403
        
        current_app.logger.debug("[ADMIN CHECK] Admin access granted")
        return f(*args, **kwargs)
    return decorated_function

def client_required(f):
    """
    Decorator to verify if the current user is a client.
    
    Supports our B2B workflow with multiple client types (COMMISSION/FLAT_RATE).
    Uses Flask-Login authentication with fallback to JWT and session.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session, request, redirect, url_for, flash
        from flask_login import current_user
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
        
        # Debug logging
        current_app.logger.info(f"client_required: Starting authentication check")
        current_app.logger.info(f"client_required: Session: {dict(session)}")
        current_app.logger.info(f"client_required: Current user: {current_user}")
        
        # 1. Check if user is authenticated via Flask-Login
        if current_user.is_authenticated:
            current_app.logger.info("client_required: User authenticated with Flask-Login")
            client = None
            
            # Try to get client from user relationship
            if hasattr(current_user, 'client'):
                client = current_user.client
                current_app.logger.info(f"client_required: Found client from user relationship: {client.id}")
            
            # If no client found, try to find by user ID
            if not client:
                from app.models.client import Client
                client = Client.query.filter_by(user_id=current_user.id).first()
                if client:
                    current_app.logger.info(f"client_required: Found client by user ID: {client.id}")
            
            # If we have a client, verify it's active
            if client:
                if not client.is_active:
                    current_app.logger.warning(f"client_required: Inactive client: {client.id}")
                    flash('Your account is inactive. Please contact support.', 'warning')
                    return redirect(url_for('auth.login'))
                
                kwargs['client'] = client
                return f(*args, **kwargs)
        
        # 2. Try JWT authentication if Flask-Login didn't work
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            
            if not user_id:
                # Try to get user ID from session as fallback
                user_id = session.get('user_id')
                if user_id:
                    current_app.logger.info(f"client_required: Using user_id from session: {user_id}")
            
            if user_id:
                current_app.logger.info(f"client_required: JWT identity found: {user_id}")
                
                # Log the JWT claims for debugging
                try:
                    jwt_data = get_jwt()
                    current_app.logger.info(f"client_required: JWT data: {jwt_data}")
                except Exception as e:
                    current_app.logger.warning(f"client_required: Could not get JWT data: {str(e)}")
                
                # Get client from database
                from app.models.client import Client
                client = Client.query.get(user_id)
                
                if client:
                    if not client.is_active:
                        current_app.logger.warning(f"client_required: Inactive client: {client.id}")
                        flash('Your account is inactive. Please contact support.', 'warning')
                        return redirect(url_for('auth.login'))
                    
                    kwargs['client'] = client
                    current_app.logger.info(f"client_required: Authentication successful for client: {client.id}")
                    return f(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"client_required: JWT verification failed: {str(e)}")
            current_app.logger.exception(e)
        
        # 3. No valid authentication found
        current_app.logger.warning("client_required: No valid authentication found")
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('auth.login'))
    
    return decorated_function

def secure_admin_required(f):
    """
    Enhanced admin decorator that returns 404 for non-admins to prevent enumeration.
    This decorator provides better security by not revealing that an admin route exists.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import abort, session
        from flask_login import current_user
        
        # Check if user is authenticated and is actually an admin
        if not current_user.is_authenticated:
            # Return 404 instead of redirecting to login
            current_app.logger.warning(f"Unauthenticated access attempt to admin route: {request.path}")
            abort(404)
        
        # Check if user is an admin through session or user model
        is_admin = False
        
        # Check session admin flag (set during admin login)
        if session.get('is_admin'):
            is_admin = True
        
        # Double-check with user model if it has admin capabilities
        if hasattr(current_user, 'is_admin') and callable(getattr(current_user, 'is_admin')):
            if current_user.is_admin():
                is_admin = True
        elif hasattr(current_user, 'is_admin') and current_user.is_admin:
            is_admin = True
        
        # Check if user is AdminUser type (for dual user system)
        from app.models import AdminUser
        if isinstance(current_user, AdminUser):
            is_admin = True
            
        if not is_admin:
            # Log potential attack attempt
            current_app.logger.warning(f"Non-admin user {current_user.id} attempted to access admin route: {request.path}")
            current_app.logger.warning(f"User type: {type(current_user)}, Session admin: {session.get('is_admin')}")
            # Return 404 to hide the existence of admin routes
            abort(404)
        
        return f(*args, **kwargs)
    return decorated_function

from functools import wraps
from flask import flash, redirect, url_for, jsonify, request

def feature_required(feature_name, flash_message=None, redirect_endpoint='client.dashboard'):
    """
    Decorator to require a specific feature for route access.
    
    Args:
        feature_name (str): Name of the required feature
        flash_message (str): Custom message to flash on access denied
        redirect_endpoint (str): Where to redirect on access denied
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('client.login'))
            
            client = current_user.client
            if not client:
                flash("Client account required.", "error")
                return redirect(url_for('client.login'))
            
            if not client.has_feature(feature_name):
                # Custom message or default
                message = flash_message
                if not message:
                    feature_display = feature_name.replace('_', ' ').title()
                    message = f"{feature_display} is not available in your current plan."
                
                # Handle AJAX requests differently
                if request.is_json or 'application/json' in request.headers.get('Accept', ''):
                    return jsonify({
                        'success': False,
                        'error': message
                    }), 403
                
                flash(message, "warning")
                return redirect(url_for(redirect_endpoint))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

