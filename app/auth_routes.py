import logging
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app, session
from flask_login import login_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from datetime import datetime
from app.models.user import User
from app.models.client import Client
from app.models.client_package import ClientSubscription
from wtforms.validators import DataRequired, Email

# Set up logging
logger = logging.getLogger(__name__)

from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies,
    get_jwt_identity, jwt_required, get_jwt
)
from app.models.client_package import PackageStatus
from flask_login import login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import os

from app.extensions import db, login_manager
from app.models.client import Client
from app.models.audit import AuditTrail
from app.models.user import User, UserMixin
from app.utils.email import send_verification_email, send_password_reset_email
from app.decorators import client_required


# Create auth blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates')

@bp.route('/determine-login')
def determine_login_redirect():
    """
    Smart login redirect that determines whether to redirect to client or admin login
    based on the requested URL path
    """
    from flask import request, redirect, url_for
    
    # Get the original URL that triggered the login requirement
    next_url = request.args.get('next', '')
    
    # Determine login type based on the requested path
    if '/client/' in next_url or '/client' == next_url:
        # Redirect to client login if trying to access client area
        return redirect(url_for('client.login', next=next_url))
    elif '/admin/' in next_url or '/admin' == next_url:
        # Redirect to admin login if trying to access admin area
        return redirect(url_for('admin.admin_login', next=next_url))
    else:
        # Default to client login for general access
        return redirect(url_for('client.login', next=next_url))

# Initialize auth routes
def init_app(app):
    """Initialize auth routes with the Flask app"""
    app.register_blueprint(bp)
    return app

# Create uploads directory if it doesn't exist
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user and create a client account"""
    from app.forms.auth_forms import RegistrationForm
    from app.models.client import Client
    from app.models.client_package import ClientPackage, ClientType
    from app.utils.audit import log_audit
    from app.utils.email import send_verification_email
    from flask import current_app, flash, redirect, render_template, request, url_for, session
    from flask_jwt_extended import (
        create_access_token,
        create_refresh_token,
        set_access_cookies,
        set_refresh_cookies,
    )
    from flask_login import current_user, login_user
    from sqlalchemy import or_

    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('client.dashboard'))

    logger = current_app.logger
    logger.info(f"Register route called with args: {request.args}")

    # Initialize form
    form = RegistrationForm()
    selected_package = None
    commission_package = None
    
    # Get package info from both GET and POST requests
    package_id = request.form.get('package_id') or request.args.get('package_id')
    package_key = request.form.get('package_key') or request.args.get('package_key')
    
    # Store package info in session for form resubmission
    if 'package_info' not in session and (package_id or package_key):
        session['package_info'] = {
            'package_id': package_id,
            'package_key': package_key
        }
    elif 'package_info' in session:
        # Use session data if available
        package_id = package_id or session['package_info'].get('package_id')
        package_key = package_key or session['package_info'].get('package_key')

    # First try to get package by ID (new method)
    if package_id and package_id.isdigit():
        logger.info("Looking up package by ID: %s", package_id)
        selected_package = ClientPackage.query.get(int(package_id))
        logger.info("Package by ID result: %s", selected_package)
    
    # Fall back to old slug-based lookup for backward compatibility
    if not selected_package:
        package_slug = request.args.get('package')
        if package_slug:
            logger.info("Looking up package by slug: %s", package_slug)
            # Normalize the package slug for comparison
            norm = lambda s: s.lower().strip().replace(' ', '_') if isinstance(s, str) else ''
            normalized_slug = norm(package_slug)
            
            # 1. Check flat-rate packages by slug
            logger.info("Querying flat-rate packages...")
            from app.models.client_package import ClientType
            flat_rate_pkgs = ClientPackage.query.filter(ClientPackage.client_type == ClientType.FLAT_RATE).all()
            logger.info("Found %d flat-rate packages", len(flat_rate_pkgs))
            
            for idx, pkg in enumerate(flat_rate_pkgs, 1):
                package_slug = getattr(pkg, 'slug', '')
                logger.info("Package %d - ID: %d, Name: '%s', Slug: '%s', Client Type: '%s'", 
                           idx, pkg.id, pkg.name, package_slug, pkg.client_type)
                if norm(package_slug) == normalized_slug or norm(pkg.name) == normalized_slug:
                    selected_package = pkg
                    logger.info("Matched flat-rate package: %s (ID: %d)", pkg.name, pkg.id)
                    break
            
            # 2. Check commission packages by slug or name
            if not selected_package:
                logger.info("No flat-rate match, checking commission packages...")
                for key, pkg in COMMISSION_BASED_PACKAGES.items():
                    if norm(key) == normalized_slug or norm(pkg.get('name', '')) == normalized_slug:
                        commission_package = pkg
                        logger.info("Matched commission package: %s", pkg.get('name'))
                        break
    
    # If no valid package found by either method, redirect to pricing
    if not selected_package and not commission_package:
        logger.warning("No matching package found for request args: %s", dict(request.args))
        flash('Please select a valid package to continue.', 'error')
        return redirect(url_for('main.pricing'))
    
    # Set package ID in form
    if selected_package:
        form.package_id.data = selected_package.id
        logger.info("Selected package: %s (ID: %d)", selected_package.name, selected_package.id)
    elif commission_package:
        form.package_id.data = commission_package.get('key', '')
        logger.info("Selected commission package: %s", commission_package.get('name'))

    
    # Handle form submission and package lookup
    if request.method == 'POST':
        logger.info("Form submitted with data: %s", {k: v for k, v in request.form.items() if k not in ['password', 'confirm_password']})
        
        # Get package from form data if not already set
        if not selected_package and not commission_package:
            package_id = request.form.get('package_id')
            package_key = request.form.get('package_key')
            
            if package_id and package_id.isdigit():
                selected_package = ClientPackage.query.get(int(package_id))
                logger.info("Found package from form data - ID: %s, Package: %s", package_id, selected_package)
                # Set the package_id in the form data
                form.package_id.data = package_id
            elif package_key:
                commission_package = COMMISSION_BASED_PACKAGES.get(package_key)
                logger.info("Found commission package from form data - Key: %s, Package: %s", package_key, commission_package)
                # Set the package_key in the form data
                form.package_id.data = package_key
        
        # Log form validation status
        is_valid = form.validate()
        logger.info("Form validation status: %s", is_valid)
        
        if not is_valid:
            logger.warning("Form validation errors: %s", form.errors)
            # Return the form with errors
            return render_template('auth/register.html', 
                               form=form, 
                               selected_package=selected_package,
                               commission_package=commission_package)
    
    # Handle form submission
    if form.validate_on_submit():
        logger.info("Form validation successful, processing registration...")
        
        # Check for existing user/email
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            logger.warning(f"Username {form.username.data} already exists")
            flash('Username already exists. Please choose a different username.', 'error')
            return render_template('auth/register.html', 
                               form=form, 
                               selected_package=selected_package,
                               commission_package=commission_package)
        
        # Check for existing email
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            logger.warning(f"Email {form.email.data} is already registered")
            flash('This email is already registered. Please use a different email or log in.', 'error')
            return render_template('auth/register.html', 
                               form=form, 
                               selected_package=selected_package,
                               commission_package=commission_package)
        
        try:
            logger.info("Starting user registration process...")
            
            # Check if package is still valid
            package = None
            if package_id and package_id.isdigit():
                package = ClientPackage.query.get(int(package_id))
                logger.info(f"Found package by ID {package_id}: {package}")
            elif package_key:
                package = ClientPackage.query.filter_by(key=package_key).first()
                logger.info(f"Found package by key {package_key}: {package}")
            
            logger.info("Creating user record...")
            try:
                logger.debug(f"Creating user with username: {form.username.data}, email: {form.email.data}")
                # Create user with only the basic required fields
                user = User(
                    username=form.username.data,
                    email=form.email.data
                )
                logger.debug("User object created, setting password...")
                # Set the hashed password
                user.set_password(form.password.data)
                
                # The UserMixin provides is_active and is_authenticated properties
                # but they don't have setters - they're based on the user's state
                # Additional user info will be stored in the client record
                
                logger.debug("Adding user to session...")
                db.session.add(user)
                logger.debug("Flushing session to get user ID...")
                db.session.flush()  # Get the user ID
                logger.info(f"Successfully created user with ID: {user.id}")
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}", exc_info=True)
                db.session.rollback()
                flash('An error occurred while creating your account. Please try again.', 'error')
                return render_template('auth/register.html', 
                                   form=form, 
                                   selected_package=selected_package,
                                   commission_package=commission_package)

            logger.info("Creating client record...")
            try:
                # Log form data for debugging
                logger.debug(f"Form data: {form.data}")
                
                # Prepare client data
                client_data = {
                    'user_id': user.id,
                    'company_name': form.company_name.data,
                    'contact_person': form.contact_person.data,
                    'name': f"{form.first_name.data} {form.last_name.data}",
                    'phone': form.phone.data,
                    'email': form.email.data,
                    'contact_email': form.contact_email.data if hasattr(form, 'contact_email') else form.email.data,
                    'contact_phone': form.contact_phone.data if hasattr(form, 'contact_phone') else form.phone.data,
                    'website': form.website.data if hasattr(form, 'website') and form.website.data else None,
                    'address': form.address.data,
                    'city': form.city.data if hasattr(form, 'city') else None,
                    # Removed 'state' as it's not a field in the Client model
                    'country': form.country.data if hasattr(form, 'country') else None,
                    'tax_id': form.tax_id.data if hasattr(form, 'tax_id') and form.tax_id.data else None,
                    'vat_number': form.vat_number.data if hasattr(form, 'vat_number') and form.vat_number.data else None,
                    'is_active': True,
                    'is_verified': False,
                    'settings': {
                        'registration_date': datetime.utcnow().isoformat(),
                        'initial_package_id': package.id if package else None,
                        # Store state in settings if needed
                        'state': form.state.data if hasattr(form, 'state') and form.state.data else None
                    }
                }
                
                logger.debug(f"Creating client with data: {client_data}")
                
                # Create client with all contact and personal information
                client = Client(**client_data)
                
                logger.debug("Adding client to session...")
                db.session.add(client)
                db.session.flush()
                logger.info(f"Successfully created client with ID: {client.id}")
            except Exception as e:
                logger.error(f"Error creating client: {str(e)}", exc_info=True)
                db.session.rollback()
                flash('An error occurred while creating your client profile. Please try again.', 'error')
                return render_template('auth/register.html', 
                                   form=form, 
                                   selected_package=selected_package,
                                   commission_package=commission_package)

            # Assign package if selected
            if package:
                logger.info(f"Assigning package {package.id} to client {client.id}")
                try:
                    subscription = ClientSubscription(
                        client_id=client.id,
                        package_id=package.id,
                        start_date=datetime.utcnow(),
                        monthly_fee=package.monthly_price,
                        commission_rate=package.commission_rate,
                        is_active=False  # Will be activated after payment
                    )
                    db.session.add(subscription)
                    logger.info(f"Created client subscription: {subscription}")
                    
                    # Store package info in session for payment
                    session['selected_package_id'] = package.id
                    session['client_id'] = client.id
                    session['subscription_id'] = subscription.id
                except Exception as e:
                    logger.error(f"Error assigning package: {str(e)}", exc_info=True)
                    # Don't fail registration if package assignment fails
                    db.session.rollback()
                    # Continue without package assignment

            logger.info("Logging user creation in audit trail...")
            try:
                # Get first and last name from the form data since they're not on the User model
                first_name = form.first_name.data
                last_name = form.last_name.data
                
                log_audit(
                    action='create',
                    model='User',
                    model_id=user.id,
                    description=f'User {user.username} registered',
                    new_values={
                        'username': user.username,
                        'email': user.email,
                        'first_name': first_name,
                        'last_name': last_name,
                        'phone': form.phone.data
                    }
                )
                logger.info("Successfully logged user creation in audit trail")
            except Exception as e:
                logger.error(f"Error in user creation audit logging: {str(e)}", exc_info=True)
                # Don't fail registration if audit logging fails
                db.session.rollback()
            
            logger.info("Logging client creation in audit trail...")
            try:
                log_audit(
                    action='create',
                    model='Client',
                    model_id=client.id,
                    description=f'Client {client.company_name} created for user {user.username}',
                    new_values={
                        'company_name': client.company_name,
                        'contact_person': client.contact_person,
                        'email': client.email,
                        'phone': client.phone,
                        'is_active': client.is_active,
                        'is_verified': client.is_verified
                    }
                )
                logger.info("Successfully logged client creation in audit trail")
            except Exception as e:
                logger.error(f"Error in client creation audit logging: {str(e)}", exc_info=True)
                # Don't fail registration if audit logging fails
                db.session.rollback()
            
            # Log package assignment if applicable
            if package:
                logger.info("Logging package assignment in audit trail...")
                try:
                    log_audit(
                        action='assign',
                        model='ClientSubscription',
                        model_id=subscription.id,
                        description=f'Package {package.name} assigned to client {client.company_name}',
                        new_values={
                            'client_id': client.id,
                            'package_id': package.id,
                            'monthly_fee': float(subscription.monthly_fee) if subscription.monthly_fee else None,
                            'commission_rate': float(subscription.commission_rate) if subscription.commission_rate else None,
                            'is_active': subscription.is_active
                        }
                    )
                    logger.info("Successfully logged package assignment in audit trail")
                except Exception as e:
                    logger.error(f"Error in package assignment audit logging: {str(e)}", exc_info=True)
                    # Don't fail registration if audit logging fails
                    db.session.rollback()
            
            # Final commit of all changes
            db.session.commit()
            logger.info("Database changes committed successfully")
            
            # Set session variables for post-registration flow
            session['is_post_registration'] = True
            session['pending_username'] = form.username.data
            
            # Clear any package info from session
            if 'package_info' in session:
                del session['package_info']
            
            logger.info(f"User {form.username.data} registration completed, redirecting to login")
            flash('Registration successful! Please log in with your new credentials.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}", exc_info=True)
            db.session.rollback()
            
            # More specific error messages based on exception type
            error_msg = 'Registration failed. Please try again.'
            if 'duplicate key' in str(e).lower():
                error_msg = 'This username or email is already registered.'
            elif 'constraint' in str(e).lower():
                error_msg = 'Invalid data provided. Please check your information and try again.'
            
            flash(error_msg, 'error')

            # Return to registration form with existing data
            return render_template('auth/register.html', 
                               form=form, 
                               selected_package=selected_package,
                               commission_package=commission_package)
    
    # For GET requests or failed POST, show registration form
    return render_template('auth/register.html', 
                         form=form, 
                         selected_package=selected_package,
                         commission_package=commission_package)

@bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    user = User.query.filter_by(email_verification_token=token).first()
    
    if not user:
        return jsonify({'error': 'Invalid or expired verification token'}), 400
    
    if user.is_verified:
        return jsonify({'message': 'Email already verified'}), 200
    
    user.is_verified = True
    user.email_verification_token = None
    
    # Also update the associated client's verification status if it exists
    if hasattr(user, 'client') and user.client:
        user.client.is_verified = True
    
    db.session.commit()
    
    return jsonify({'message': 'Email verified successfully'}), 200

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Authenticate a client user and return JWT tokens
    """
    # Handle GET request - show login form
    if request.method == 'GET':
        # Check if user is already authenticated
        if current_user.is_authenticated:
            logger.info(f"User {current_user.id} is already authenticated")
            # If this is a post-registration flow, redirect to payment
            if session.get('is_post_registration'):
                return redirect(url_for('client.new_payment'))
            # Otherwise, redirect to client dashboard
            return redirect(url_for('client.dashboard'))
            
        # Create form instance for GET request
        form = LoginForm()
        
        # Pre-fill username if in post-registration flow
        if session.get('is_post_registration') and session.get('pending_username'):
            form.username.data = session['pending_username']
        
        # Prepare template context
        template_context = {
            'form': form,
            'is_post_registration': session.get('is_post_registration', False),
            'pending_username': session.get('pending_username')
        }
        
        # Check if this is an admin login request
        if request.path.startswith('/admin'):
            return render_template('auth/login.html', form=form)
            
        # Otherwise, use the client login template with context
        return render_template('auth/client_login.html', **template_context)
    
    # Handle POST request - process login
    form = LoginForm()
    
    # Check if this is a JSON request
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Username and password are required'
            }), 400
            
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Create JWT token for API response
            access_token = create_access_token(identity={
                'id': str(user.id),
                'type': 'user',
                'client_id': str(user.client.id) if hasattr(user, 'client') and user.client else None
            })
            
            return jsonify({
                'success': True,
                'access_token': access_token,
                'user_id': user.id,
                'is_post_registration': session.get('is_post_registration', False)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid username or password'
            }), 401
    
    # Handle form submission
    if form.validate_on_submit():
        # Find user by username
        user = User.query.filter_by(username=form.username.data).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(form.password.data):
            # Log the user in
            login_user(user, remember=form.remember.data)
            
            # Create JWT tokens
            access_token = create_access_token(identity={
                'id': str(user.id),
                'type': 'user',
                'client_id': str(user.client.id) if hasattr(user, 'client') and user.client else None,
                'is_post_registration': session.get('is_post_registration', False)
            })
            
            # Set up response
            if session.get('is_post_registration'):
                response = redirect(url_for('client.new_payment'))
            else:
                response = redirect(url_for('client.dashboard'))
            
            # Set JWT cookies
            set_access_cookies(response, access_token)
            
            # Clear post-registration flags
            if 'is_post_registration' in session:
                session.pop('is_post_registration')
            if 'pending_email' in session:
                session.pop('pending_email')
                
            return response
        
        # If we get here, login failed
        flash('Invalid username or password', 'error')
    
    # If we get here, either form validation failed or login failed
    # Prepare template context for re-rendering the form with errors
    template_context = {
        'form': form,
        'is_post_registration': session.get('is_post_registration', False),
        'pending_username': session.get('pending_username')
    }
    
    return render_template('auth/client_login.html', **template_context)

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            send_password_reset_email(user)
        
        # Always return success to prevent email enumeration
        flash('If an account exists with that email, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(password_reset_token=token).first()
    
    if not user or user.password_reset_expires < datetime.utcnow():
        flash('Invalid or expired password reset token', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.reset_password', token=token))
        
        user.set_password(password)
        user.password_reset_token = None
        user.password_reset_expires = None
        db.session.commit()
        
        flash('Your password has been reset successfully', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token)

@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """General logout route that works for both GET and POST requests"""
    from flask_login import logout_user
    
    # Log out the user with Flask-Login
    logout_user()
    
    if request.method == 'POST':
        # For API/AJAX requests, return JSON
        response = jsonify({'message': 'Successfully logged out'})
    else:
        # For GET requests, redirect to login page
        response = redirect(url_for('main.index'))
    
    # Clear JWT cookies
    unset_jwt_cookies(response)
    return response

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity, additional_claims={"type": "client"})
    
    response = jsonify({'access_token': access_token})
    set_access_cookies(response, access_token)
    return response
