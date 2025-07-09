from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response, current_app, session
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity,
    set_access_cookies, unset_jwt_cookies, create_refresh_token,
    set_refresh_cookies, get_jwt, verify_jwt_in_request
)
from flask_login import login_required, login_user, logout_user, current_user
from flask_mail import Message
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from app.extensions.extensions import csrf
from sqlalchemy import func
from datetime import datetime, timedelta
from decimal import Decimal
from functools import wraps
from app.extensions.extensions import db, mail
from app.models import (
    Client, Payment, Withdrawal, WithdrawalRequest, PaymentStatus,
    Invoice, ClientDocument, ClientNotificationPreference, ClientPackage
)
from app.models.api_key import ClientApiKey, ApiKeyUsageLog
from app.models.document import Document
from app.models.withdrawal import WithdrawalStatus
from app.forms.withdrawal import WithdrawalForm
from app.decorators import track_activity, audit_log, client_required, feature_required
from app.forms.client_forms import (
    ClientRegistrationForm, PaymentForm, InvoiceForm,
    DocumentUploadForm, NotificationPreferenceForm,
    ClientApiKeyForm, ClientApiKeyEditForm, ClientApiKeyRevokeForm
)
from app.models.audit import AuditTrail, AuditActionType
from app.models.notification import NotificationType, NotificationEvent
from app.utils.finance import FinanceCalculator
from app.models.client_wallet import WalletType
import os

# Constants
WITHDRAWAL_FEE = Decimal('0.0005')  # 0.0005 BTC fee per withdrawal
MIN_WITHDRAWAL = Decimal('0.0001')   # Minimum withdrawal amount
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB max file size
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}


def get_client_balance(client_id):
    """Calculate client's available balance (total deposits - approved withdrawals)"""
    total_deposits = db.session.query(
        db.func.coalesce(db.func.sum(Payment.amount), Decimal('0'))
    ).filter(
        Payment.client_id == client_id,
        Payment.status == PaymentStatus.APPROVED
    ).scalar() or Decimal('0')
    
    total_withdrawals = db.session.query(
        db.func.coalesce(db.func.sum(WithdrawalRequest.amount), Decimal('0'))
    ).filter(
        WithdrawalRequest.client_id == client_id,
        (WithdrawalRequest.status == WithdrawalStatus.APPROVED) | 
        (WithdrawalRequest.status == WithdrawalStatus.PENDING)
    ).scalar() or Decimal('0')
    
    return float(total_deposits - total_withdrawals)

# Create client blueprint first
client_bp = Blueprint('client', __name__, url_prefix='/client', template_folder='templates/client')

@client_bp.route('/login', methods=['GET', 'POST'])
@csrf.exempt  # Completely exempt login route from CSRF protection
def login():
    """Client login with proper Flask-Login integration
    
    Supports both direct client login and integration with User model for Flask-Login
    Completely exempt from CSRF for testing purposes
    """
    from flask_login import login_user
    from flask_wtf.csrf import generate_csrf
    from flask import session
    
    # Force CSRF exemption via session flag
    session['_csrf_exempt'] = True

    # Add extensive logging for debugging
    current_app.logger.debug(f"[LOGIN] Starting login process - method: {request.method}")
    current_app.logger.debug(f"[LOGIN] Current user: {current_user}")
    
    # If already logged in, redirect to dashboard
    if current_user.is_authenticated:
        current_app.logger.debug(f"[LOGIN] User already authenticated: {current_user.username}")
        
        # Check if user is a client
        if hasattr(current_user, 'is_client') and current_user.is_client():
            current_app.logger.debug(f"[LOGIN] User is client, redirecting to dashboard")
            return redirect(url_for('client.dashboard'))
        else:
            current_app.logger.debug(f"[LOGIN] User is not a client")
            # For non-client users, show login form
        
    # Ensure CSRF token is available in session for form rendering
    if request.method == 'GET':
        # Force generation of a new CSRF token if needed
        csrf_token = generate_csrf()
        current_app.logger.debug(f"[LOGIN] Generated CSRF token for login page: {csrf_token[:10]}...")
    
    if request.method == 'POST':
        # Log the request details for debugging
        current_app.logger.debug(f"[LOGIN] Login attempt: headers={dict(request.headers)}")
        current_app.logger.debug(f"[LOGIN] Login attempt: form={dict(request.form)}")
        
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'  # Convert checkbox value to boolean
        
        current_app.logger.debug(f"[LOGIN] Attempting login for: {username}")
        
        if not username or not password:
            current_app.logger.warning(f"[LOGIN] Missing username or password")
            flash('Username and password are required', 'danger')
            return render_template('client/login.html'), 400
            
        # Find client by username or email
        client = Client.query.filter(
            (Client.email == username) | 
            (Client.username == username) | 
            (Client.company_name == username)
        ).first()
        
        current_app.logger.debug(f"[LOGIN] Found client: {client}")
        
        if not client or not client.check_password(password):
            # Track failed login attempts
            if client:
                client.login_attempts = (client.login_attempts or 0) + 1
                db.session.commit()
                current_app.logger.warning(f"[LOGIN] Failed login attempt for {username}. Attempts: {client.login_attempts}")
                
                # Lock account after too many failed attempts
                if client.login_attempts >= 5:
                    current_app.logger.warning(f"[LOGIN] Account locked due to too many failed attempts: {client.username}")
                    flash('Too many failed login attempts. Your account has been temporarily locked. Please contact support.', 'danger')
                    return render_template('client/login.html'), 401
            else:
                current_app.logger.warning(f"[LOGIN] No client found with username/email: {username}")
            
            flash('Invalid username or password. Please try again.', 'danger')
            return render_template('client/login.html'), 401
        
        if not client.is_active:
            current_app.logger.warning(f"[LOGIN] Inactive account attempt: {client.username}")
            flash('Your account has been deactivated. Please contact support.', 'danger')
            return render_template('client/login.html', 401)
        
        # Update last login and reset failed attempts
        client.last_login_at = datetime.utcnow()
        client.login_attempts = 0
        db.session.commit()
        
        # Create or get associated User for Flask-Login
        user = None
        
        # Try to get user from client first
        if hasattr(client, 'user') and client.user:
            user = client.user
            current_app.logger.debug(f"[LOGIN] Found user from client.user: {user.id} - {user.username}")
        else:
            # Try to find user by email directly
            from app.models.user import User
            user = User.query.filter_by(email=client.email).first()
            if user:
                current_app.logger.debug(f"[LOGIN] Found user by email: {user.id} - {user.username}")
                # Link the user to client if not already linked
                if not client.user_id:
                    current_app.logger.debug(f"[LOGIN] Linking existing user to client")
                    client.user_id = user.id
                    db.session.commit()
        
        # If still no user, create a new one
        if not user:
            # Create a user if it doesn't exist (for legacy clients)
            from app.models.user import User
            current_app.logger.info(f"[LOGIN] Creating new User for client: {client.email}")
            
            # Generate a unique username if email is already taken as username
            username = client.email
            if User.query.filter_by(username=username).first():
                # Use email with client id as username
                username = f"{client.email}_{client.id}"
                current_app.logger.debug(f"[LOGIN] Generated unique username: {username}")
            
            user = User(
                username=username,
                email=client.email
            )
            user.set_password(password)  # This won't be used, just for consistency
            db.session.add(user)
            db.session.flush()  # Get the ID without committing
            client.user_id = user.id
            db.session.commit()
            
            current_app.logger.debug(f"[LOGIN] Created new User with ID: {user.id}")
        
        try:
            # Log in the user with Flask-Login
            login_successful = login_user(user, remember=remember_me)
            current_app.logger.debug(f"[LOGIN] login_user result: {login_successful}")
            
            if not login_successful:
                current_app.logger.error(f"[LOGIN] Flask-Login failed for user: {user.id}")
                flash('Authentication failed. Please try again.', 'danger')
                return render_template('client/login.html', 401)
                
        except Exception as e:
            current_app.logger.error(f"[LOGIN] Exception in login_user: {str(e)}")
            flash('An error occurred during login. Please try again.', 'danger')
            return render_template('client/login.html', 500)
        
        # Create JWT tokens in case they're needed
        try:
            # This is a hybrid approach supporting both authentication methods
            additional_claims = {
                'type': 'client',
                'id': client.id,
                'email': client.email
            }
            access_token = create_access_token(identity=str(client.id), additional_claims=additional_claims)
            refresh_token = create_refresh_token(identity=str(client.id), additional_claims=additional_claims)
            current_app.logger.debug(f"[LOGIN] JWT tokens created successfully")
        except Exception as e:
            current_app.logger.error(f"[LOGIN] Failed to create JWT tokens: {str(e)}")
            # Continue without JWT tokens - we'll rely on Flask-Login
        
        # Log the successful login
        current_app.logger.info(f"[LOGIN] Successful login for client: {client.username}")
        
        # Add audit log for successful login
        try:
            from app.models.audit import AuditTrail, AuditActionType
            
            AuditTrail.log_action(
                user_id=user.id,  # Use the User ID instead of client ID
                action_type=AuditActionType.LOGIN.value,
                entity_type='client',
                entity_id=client.id,
                request=request
            )
            db.session.commit()  # Make sure to commit the audit log
            current_app.logger.debug(f"[LOGIN] Audit log recorded successfully")
        except Exception as e:
            current_app.logger.error(f"[LOGIN] Failed to log audit trail: {str(e)}")
            db.session.rollback()  # Rollback but continue with login
        
        # Get the next URL for redirect
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/client/'):
            next_page = url_for('client.dashboard')
            
        current_app.logger.debug(f"[LOGIN] Redirecting to: {next_page}")
            
        response = redirect(next_page)
        
        # Set JWT cookies
        try:
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            current_app.logger.debug(f"[LOGIN] JWT cookies set successfully")
        except Exception as e:
            current_app.logger.error(f"[LOGIN] Failed to set JWT cookies: {str(e)}")
            # Continue without JWT cookies - we'll rely on Flask-Login session
        
        flash(f'Welcome back, {client.contact_person or client.company_name}!', 'success')
        return response
        
    return render_template('client/login.html')

# Initialize client routes
def init_app(app):
    """Initialize client routes with the Flask app"""
    # Add middleware for client blueprint
    @client_bp.before_request
    def check_client_session():
        """Check for client authentication and setup necessary context
        
        This allows public routes like login to work without restrictions
        while logging useful information for all client routes
        """
        from flask import request, current_app
        
        # Skip authentication checks for public routes
        public_routes = ['client.login', 'client.register', 'client.forgot_password']
        if request.endpoint in public_routes:
            current_app.logger.debug(f"[CLIENT_BP] Accessing public route: {request.endpoint}")
            return None
            
        # For protected routes, log access attempts for debugging
        current_app.logger.debug(f"[CLIENT_BP] Request to protected route: {request.endpoint}")
        
        # No need to enforce authentication here - that's handled by decorators
        # This is just for logging and context setup
        
        # Set up any required context for all client routes here
        
    app.register_blueprint(client_bp)
    
    # Register error handler for client routes
    @client_bp.errorhandler(401)
    def handle_client_unauthorized(error):
        """Handle unauthorized access to client routes"""
        from flask import flash, redirect, url_for
        flash('You need to log in to access this page.', 'warning')
        return redirect(url_for('client.login'))
        
    return app

@client_bp.route('/dashboard', endpoint='dashboard')
@client_required  # Use our enhanced client_required decorator 
@track_activity(action="view_dashboard")
@audit_log(action="viewed_dashboard", details={"page": "dashboard"})
def dashboard(client=None):  # Accept client from decorator
    import traceback
    try:
        # Client is provided by the decorator, but we'll add a fallback
        if not client:
            if not hasattr(current_user, 'client') or not current_user.client:
                current_app.logger.error(f"User {current_user.id} is marked as client but has no client profile")
                flash('Your account is not properly linked to a client profile. Please contact support.', 'error')
                return redirect(url_for('client.login'))
            client = current_user.client
        current_app.logger.info(f"Client dashboard accessed by: {client.company_name} (ID: {client.id})")
        
        # Get client package information
        package = client.get_current_package()
        client_type = client.get_client_type() if package else None
        
        current_app.logger.debug(f"Client type: {client_type}, Package: {package.name if package else 'None'}")
        
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('ITEMS_PER_PAGE', 10)
        
        # Get recent payments
        payments = Payment.query.filter_by(client_id=client.id)\
            .order_by(Payment.created_at.desc())\
            .paginate(page=page, per_page=per_page)
        
        # Get recent withdrawals
        withdrawals = WithdrawalRequest.query.filter_by(client_id=client.id)\
            .order_by(WithdrawalRequest.created_at.desc())\
            .paginate(page=page, per_page=per_page)
        
        # Calculate balance and commissions
        balance = FinanceCalculator.calculate_client_balance(client.id)
        deposit_commission, withdrawal_commission, total_commission = FinanceCalculator.calculate_commission(client.id)
        
        # Get total deposits and withdrawals
        total_deposits = db.session.query(func.sum(Payment.amount))\
            .filter_by(client_id=client.id, status='completed')\
            .scalar() or Decimal('0')
            
        total_withdrawals = db.session.query(func.sum(WithdrawalRequest.amount))\
            .filter_by(client_id=client.id, status='approved')\
            .scalar() or Decimal('0')
        
        # Calculate monthly transactions for the stats card
        from sqlalchemy import extract
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        monthly_transactions = db.session.query(func.count(Payment.id))\
            .filter(
                Payment.client_id == client.id,
                extract('month', Payment.created_at) == current_month,
                extract('year', Payment.created_at) == current_year
            ).scalar() or 0
        
        # Get available features based on client package
        available_features = []
        if package:
            available_features = [pf.feature for pf in package.package_features if pf.is_included]
            
        # Get API usage stats if client has API feature
        api_stats = None
        if client.has_feature('api_basic'):
            # Calculate API usage stats for this month
            from app.models.api_usage import ApiUsage
            api_stats = {
                'calls_this_month': ApiUsage.get_usage_count(client.id, current_month, current_year),
                'limit': package.max_api_calls_per_month if package else 1000,
                'last_call': ApiUsage.get_last_call(client.id)
            }
        
        return render_template('client/dashboard.html',
                             client=client,
                             package=package,
                             client_type=client_type,
                             payments=payments,
                             withdrawals=withdrawals,
                             balance=balance,
                             deposit_commission=deposit_commission,
                             withdrawal_commission=withdrawal_commission,
                             total_commission=total_commission,
                             total_deposits=total_deposits,
                             total_withdrawals=total_withdrawals,
                             monthly_transactions=monthly_transactions,
                             available_features=available_features,
                             api_stats=api_stats)
    except Exception as e:
        current_app.logger.error(f"DASHBOARD ERROR: {str(e)}\n{traceback.format_exc()}")

@client_bp.route('/payments/new', methods=['GET', 'POST'])
@login_required
def new_payment():
    """Create a new payment for the logged-in client"""
    from app.forms.client_forms import PaymentForm
    from app.models.payment import Payment
    from app.models.enums import PaymentStatus
    from app.models.client_package import ClientSubscription, ClientType
    from datetime import datetime, timedelta
    from decimal import Decimal
    from flask import session
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info("New payment route accessed")
    logger.info(f"Session data: {dict(session)}")
    
    # Get client
    client = current_user.client
    if not client:
        logger.error(f"No client found for user {current_user.id}")
        flash('Client account not found', 'error')
        return redirect(url_for('client.dashboard'))
    
    # Get package assignment from session or database
    package_assignment = None
    package = None
    amount = Decimal('0.00')
    description = "Payment"
    
    # Check for package in session first (for new registrations)
    if 'selected_package_id' in session:
        logger.info(f"Found selected_package_id in session: {session['selected_package_id']}")
        package = ClientPackage.query.get(session['selected_package_id'])
        if package:
            logger.info(f"Found package from session: {package.name} (ID: {package.id})")
            # Create a temporary subscription
            package_assignment = ClientSubscription(
                client_id=client.id,
                package_id=package.id,
                start_date=datetime.utcnow(),
                monthly_fee=package.monthly_price,
                commission_rate=package.commission_rate,
                is_active=False  # Will be activated after payment
            )
    
    # If no package in session, try to find an existing assignment
    if not package_assignment:
        logger.info("No package in session, checking for existing assignments")
        package_assignment = ClientSubscription.query.filter_by(
            client_id=client.id,
            is_active=True
        ).first()
        
        if package_assignment:
            package = package_assignment.package
            logger.info(f"Found existing package assignment: {package.name} (ID: {package.id})")
    
    if not package_assignment or not package:
        logger.error(f"No active package found for client {client.id}")
        flash('No package selected. Please select a package first.', 'error')
        return redirect(url_for('client.pricing'))
    
    # Calculate amount based on package type
    if package.client_type == ClientType.FLAT_RATE:
        amount = package.monthly_price if package.monthly_price else Decimal('0.00')
        description = f"{package.name} - Monthly Subscription"
    else:  # COMMISSION
        amount = package.setup_fee if package.setup_fee and package.setup_fee > 0 else Decimal('0.00')
        description = f"{package.name} - Setup Fee"
    
    logger.info(f"Calculated payment amount: {amount} for package: {package.name}")
    
    # Initialize form
    form = PaymentForm()
    
    # Set default payment method if not set
    if not form.payment_method.data:
        form.payment_method.data = 'stripe'  # Default to Stripe
    
    try:
        if form.validate_on_submit():
            # If this is a new assignment, save it to the database
            if not hasattr(package_assignment, 'id') or not package_assignment.id:
                db.session.add(package_assignment)
                db.session.flush()
                logger.info(f"Created new package assignment: {package_assignment.id}")
            
            # Create payment record with subscription ID in description
            payment = Payment(
                client_id=client.id,
                fiat_amount=amount,
                fiat_currency='USD',
                payment_method=form.payment_method.data,
                status=PaymentStatus.PENDING,
                description=f"{description} (Subscription ID: {package_assignment.id})",
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            
            # Store subscription ID in the payment record (if there's a field for it)
            # If there's a dedicated field for subscription_id, use:
            # payment.subscription_id = package_assignment.id
            
            db.session.add(payment)
            
            # Clear package from session if it exists
            if 'selected_package_id' in session:
                del session['selected_package_id']
            
            db.session.commit()
            logger.info(f"Created payment {payment.id} for client {client.id}")
            
            # Redirect to dashboard after successful payment creation
            flash('Payment created successfully!', 'success')
            return redirect(url_for('client.dashboard'))
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error creating payment: {str(e)}', exc_info=True)
        flash('An error occurred while processing your payment. Please try again.', 'error')
    
    # Using absolute template path to ensure it's found
    return render_template('payment_form.html',
                         form=form,
                         package=package,
                         amount=amount,
                         description=description,
                         client=client)

@client_bp.route('/invoices/new', methods=['GET', 'POST'])
@login_required
def new_invoice():
    """Create a new invoice"""
    current_user_id = get_jwt_identity()
    client = Client.query.get(current_user_id)
    
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    form = InvoiceForm()
    if form.validate_on_submit():
        try:
            invoice = Invoice(
                client_id=client.id,
                amount=form.amount.data,
                currency=form.currency.data,
                due_date=form.due_date.data,
                status='pending'
            )
            
            db.session.add(invoice)
            db.session.commit()
            
            # Log audit trail
            AuditTrail.log_action(
                user_id=client.id,
                action_type=AuditActionType.CREATE.value,
                entity_type='invoice',
                entity_id=invoice.id,
                old_value=None,
                new_value=invoice.to_dict(),
                request=request
            )
            
            flash('Invoice created successfully', 'success')
            return redirect(url_for('client.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating invoice: {str(e)}', 'error')
    
    return render_template('client/invoice_form.html', form=form)

@client_bp.route('/documents/upload', methods=['GET', 'POST'])
@login_required
def upload_document():
    """Upload client documents"""
    current_user_id = get_jwt_identity()
    client = Client.query.get(current_user_id)
    
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    form = DocumentUploadForm()
    if form.validate_on_submit():
        try:
            # Save file
            file = form.file.data
            if file and Document.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                document = ClientDocument(
                    client_id=client.id,
                    document_type=form.document_type.data,
                    file_path=file_path,
                    description=form.description.data
                )
                
                db.session.add(document)
                db.session.commit()
                
                flash('Document uploaded successfully', 'success')
                return redirect(url_for('client.dashboard'))
            else:
                flash('Invalid file type', 'error')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error uploading document: {str(e)}', 'error')
    
    return render_template('client/document_upload.html', form=form)

@client_bp.route('/notifications/preferences', methods=['GET', 'POST'])
@login_required
def notification_preferences():
    """Manage notification preferences"""
    current_user_id = get_jwt_identity()
    client = Client.query.get(current_user_id)
    
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    form = NotificationPreferenceForm()
    if form.validate_on_submit():
        try:
            # Update preferences
            for field in form:
                if field.type == 'BooleanField':
                    preference = ClientNotificationPreference.query.filter_by(
                        client_id=client.id,
                        notification_type=field.name
                    ).first()
                    if not preference:
                        preference = ClientNotificationPreference(
                            client_id=client.id,
                            notification_type=field.name,
                            channel='email'  # Default channel
                        )
                    preference.enabled = field.data
                    db.session.add(preference)
            
            db.session.commit()
            
            # Log audit trail
            AuditTrail.log_action(
                user_id=client.id,
                action_type=AuditActionType.UPDATE.value,
                entity_type='notification_preferences',
                entity_id=client.id,
                old_value=None,
                new_value=form.data,
                request=request
            )
            
            flash('Notification preferences updated successfully', 'success')
            return redirect(url_for('client.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating preferences: {str(e)}', 'error')
    
    return render_template('client/notification_preferences.html', form=form)

@client_bp.route('/withdraw', methods=['GET', 'POST'], endpoint='withdraw')
@login_required
@client_required
def withdraw(client):
    client_id = client.id
    balance = FinanceCalculator.calculate_client_balance(client_id)
    
    form = WithdrawalForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        # Validate withdrawal amount
        if not FinanceCalculator.validate_withdrawal_amount(client_id, form.amount.data):
            flash('Insufficient balance. Available balance: %.8f USDT' % balance, 'danger')
            return redirect(url_for('client.withdraw', client_id=client_id))
        
        amount = Decimal(str(form.amount.data))
        total_amount = amount + WITHDRAWAL_FEE
        
        # Additional validation
        if amount < MIN_WITHDRAWAL:
            flash(f'Minimum withdrawal amount is {MIN_WITHDRAWAL} BTC', 'danger')
            return render_template('client/withdraw.html', form=form, balance=balance)
            
        if total_amount > Decimal(str(balance)):
            flash('Insufficient balance to cover the withdrawal amount and fee', 'danger')
            return render_template('client/withdraw.html', form=form, balance=balance)
        
        # Create withdrawal request
        withdrawal = WithdrawalRequest(
            client_id=client_id,
            amount=float(amount),
            coin=form.coin.data.lower() if form.coin.data else '',
            address=form.address.data.strip() if form.address.data else ''
        )
        
        try:
            db.session.add(withdrawal)
            db.session.commit()
            
            # Here you would typically integrate with your payment processor
            # to actually process the withdrawal
            
            flash('Withdrawal request submitted successfully! It will be processed shortly.', 'success')
            return redirect(url_for('client.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating withdrawal: {str(e)}')
            flash('An error occurred while processing your request. Please try again.', 'danger')
    
    # Pre-fill form with GET parameters if any
    if request.method == 'GET' and request.args.get('amount'):
        try:
            from decimal import Decimal
            amount_value = request.args.get('amount', 0)
            form.amount.data = Decimal(str(amount_value))
            form.coin.data = request.args.get('coin', 'btc')
        except (ValueError, TypeError):
            pass
    
    return render_template('client/withdraw.html', form=form, balance=balance)

@client_bp.route('/withdrawal-history', endpoint='withdrawal_history')
@login_required
@client_required
@track_activity
@audit_log("Viewed withdrawal history")
def withdrawal_history():
    """Show client's withdrawal history"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEMS_PER_PAGE']
    
    withdrawals = WithdrawalRequest.query.filter_by(client_id=current_user.id)\
        .order_by(WithdrawalRequest.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    # Calculate commission information
    deposit_commission, withdrawal_commission, total_commission = FinanceCalculator.calculate_commission(current_user.id)
    
    return render_template(
        'client/withdrawal_history.html', 
        withdrawals=withdrawals,
        deposit_commission=deposit_commission,
        withdrawal_commission=withdrawal_commission,
        total_commission=total_commission
    )

@client_bp.route('/withdrawals/<int:withdrawal_id>/cancel', methods=['POST'], endpoint='cancel_withdrawal')
@login_required
@client_required
def cancel_withdrawal(withdrawal_id):
    client_id = get_jwt_identity()
    withdrawal = WithdrawalRequest.query.filter_by(
        id=withdrawal_id,
        client_id=client_id,
        status=PaymentStatus.PENDING.value
    ).first_or_404()
    
    try:
        withdrawal.status = WithdrawalStatus.CANCELLED
        withdrawal.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Withdrawal request has been cancelled.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error cancelling withdrawal: {str(e)}')
        flash('Failed to cancel withdrawal request. Please try again.', 'danger')
    
    return redirect(url_for('client.withdrawal_history'))


@client_bp.route('/logout', endpoint='logout')
@login_required
@audit_log(action="client_logout")
def logout():
    """Client logout with proper Flask-Login integration and JWT cleanup"""
    try:
        # Log the logout for auditing
        current_app.logger.info(f"Client logout: {current_user.username if hasattr(current_user, 'username') else 'unknown'}")
        
        # Log out the user with Flask-Login
        logout_user()
        
        # Prepare response for redirection
        response = make_response(redirect(url_for('client.login')))
        
        # Clear JWT cookies (if any)
        try:
            unset_jwt_cookies(response)
        except Exception as e:
            current_app.logger.error(f"Error clearing JWT cookies: {str(e)}")
        
        # Clear additional cookies
        for cookie_name in ['csrf_access_token', 'csrf_refresh_token', 'access_token_cookie', 'refresh_token_cookie']:
            response.delete_cookie(cookie_name)
            
        # Clear session data as well
        from flask import session
        session.clear()
        
        flash('You have been logged out successfully.', 'info')
        return response
    except Exception as e:
        current_app.logger.error(f"Error during logout: {str(e)}")
        flash('An error occurred during logout. Please try again.', 'warning')
        return redirect(url_for('client.login'))

@client_bp.route('/dashboard/stats', endpoint='dashboard_stats')
@login_required
@client_required
def dashboard_stats():
    """API endpoint for real-time dashboard stats"""
    try:
        client = current_user.client
        
        # Check if client has real-time dashboard access
        if not client.has_feature('dashboard_realtime'):
            return jsonify({
                'success': False,
                'error': 'Real-time dashboard stats are available only for Professional plans.'
            }), 403
        
        # Calculate current balance
        balance = FinanceCalculator.calculate_client_balance(client.id)
        
        # Get monthly transaction count
        current_month = datetime.now().replace(day=1)
        monthly_transactions = Payment.query.filter(
            Payment.client_id == client.id,
            Payment.created_at >= current_month
        ).count()
        
        # Get recent transactions count
        recent_count = Payment.query.filter_by(client_id=client.id).count()
        
        return jsonify({
            'success': True,
            'balance': float(balance),
            'monthly_transactions': monthly_transactions,
            'total_transactions': recent_count,
            'last_updated': datetime.utcnow().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f'Error fetching dashboard stats: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@client_bp.route('/payments', endpoint='payments')
@login_required
@client_required
def payments(client):
    """List all payments for the client"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
    
    payments = Payment.query.filter_by(client_id=client.id)\
        .order_by(Payment.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('client/payments.html', payments=payments, client=client)

@client_bp.route('/payments/<int:payment_id>', endpoint='view_payment')
@login_required
@client_required
def view_payment(payment_id):
    """View a specific payment"""
    client = current_user.client
    payment = Payment.query.filter_by(id=payment_id, client_id=client.id).first_or_404()
    
    return render_template('client/payment_detail.html', payment=payment, client=client)

@client_bp.route('/api-docs', endpoint='api_docs')
@login_required
@client_required
@feature_required('api_basic', "API documentation is available only for plans with API access.")
def api_docs():
    """API documentation for the client"""
    client = current_user.client
    return render_template('client/api_docs.html', client=client)

@client_bp.route('/api-keys', endpoint='api_keys')
@login_required
@client_required
@feature_required('api_basic', "API key management is available only for plans with API access.")
def api_keys(client):
    """Manage API keys"""
    # client is injected by decorator
    api_keys = ClientApiKey.query.filter_by(client_id=client.id).order_by(ClientApiKey.created_at.desc()).all()
    key_stats = {}
    for key in api_keys:
        usage_logs = ApiKeyUsageLog.query.filter_by(api_key_id=key.id).order_by(ApiKeyUsageLog.timestamp.desc()).limit(10).all()
        key_stats[key.id] = {
            'recent_usage': usage_logs,
            'total_usage': key.usage_count,
            'last_used': key.last_used_at
        }
    
    return render_template('client/api_keys.html', 
                         client=client, 
                         api_keys=api_keys, 
                         key_stats=key_stats)


@client_bp.route('/api-keys/create', methods=['GET', 'POST'], endpoint='create_api_key')
@login_required
@client_required
@feature_required('api_basic', "API key creation is available only for plans with API access.")
def create_api_key():
    """Create a new API key"""
    client = current_user.client
    form = ClientApiKeyForm()
    
    if form.validate_on_submit():
        try:
            # Create permissions array based on client type
            permissions = []
            client_type = 'commission' if client.is_commission_based() else 'flat_rate'
            
            if client_type == 'commission':
                # Commission-based client permissions
                if form.perm_commission_payment_create.data:
                    permissions.append('commission:payment:create')
                if form.perm_commission_payment_read.data:
                    permissions.append('commission:payment:read')
                if form.perm_commission_balance_read.data:
                    permissions.append('commission:balance:read')
                if form.perm_commission_status_check.data:
                    permissions.append('commission:status:check')
            else:
                # Flat-rate client permissions
                if form.perm_flat_rate_payment_create.data:
                    permissions.append('flat_rate:payment:create')
                if form.perm_flat_rate_payment_read.data:
                    permissions.append('flat_rate:payment:read')
                if form.perm_flat_rate_payment_update.data:
                    permissions.append('flat_rate:payment:update')
                if form.perm_flat_rate_withdrawal_create.data:
                    permissions.append('flat_rate:withdrawal:create')
                if form.perm_flat_rate_withdrawal_read.data:
                    permissions.append('flat_rate:withdrawal:read')
                if form.perm_flat_rate_withdrawal_approve.data:
                    permissions.append('flat_rate:withdrawal:approve')
                if form.perm_flat_rate_balance_read.data:
                    permissions.append('flat_rate:balance:read')
                if form.perm_flat_rate_balance_update.data:
                    permissions.append('flat_rate:balance:update')
                if form.perm_flat_rate_wallet_manage.data:
                    permissions.append('flat_rate:wallet:manage')
                if form.perm_flat_rate_webhook_manage.data:
                    permissions.append('flat_rate:webhook:manage')
                if form.perm_flat_rate_user_manage.data:
                    permissions.append('flat_rate:user:manage')
                if form.perm_flat_rate_invoice_create.data:
                    permissions.append('flat_rate:invoice:create')
                if form.perm_flat_rate_invoice_read.data:
                    permissions.append('flat_rate:invoice:read')
                if form.perm_flat_rate_profile_read.data:
                    permissions.append('flat_rate:profile:read')
                if form.perm_flat_rate_profile_update.data:
                    permissions.append('flat_rate:profile:update')
            
            # Calculate expiry date
            expires_at = None
            if form.expires_in_days.data:
                expires_at = datetime.utcnow() + timedelta(days=int(form.expires_in_days.data))
            
            # Validate rate limit based on client type
            max_rate_limit = 60 if client.is_commission_based() else 1000
            if form.rate_limit.data > max_rate_limit:
                form.rate_limit.data = max_rate_limit
                flash(f'Rate limit adjusted to maximum allowed for your account type: {max_rate_limit} req/min', 'warning')
            
            # Parse allowed IPs for flat-rate clients
            allowed_ips = []
            if client.is_flat_rate() and form.allowed_ips.data:
                allowed_ips = [ip.strip() for ip in form.allowed_ips.data.split(',') if ip.strip()]
            
            # Create the API key with client type awareness
            api_key = ClientApiKey.create_for_client_by_type(
                client=client,
                name=form.name.data,
                permissions=permissions,
                rate_limit=form.rate_limit.data,
                expires_at=expires_at
            )
            
            # Set IP restrictions for flat-rate clients
            if allowed_ips:
                api_key.allowed_ips = allowed_ips
            
            db.session.add(api_key)
            db.session.commit()
            
            # Log the creation
            AuditTrail.log_action(
                user_id=current_user.id,
                action_type=AuditActionType.API_KEY_CREATED.value,
                entity_type='ClientApiKey',
                entity_id=api_key.id,
                new_value={'name': form.name.data, 'permissions': permissions}
            )
            
            flash(f'API key "{form.name.data}" created successfully! Keep the key secure - it will not be shown again.', 'success')
            return redirect(url_for('client.api_key_details', key_id=api_key.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating API key: {str(e)}', 'error')
    
    return render_template('client/create_api_key.html', form=form, client=client)


@client_bp.route('/api-keys/<int:key_id>', endpoint='api_key_details')
@login_required
@client_required
@feature_required('api_basic', "API key management is available only for plans with API access.")
def api_key_details(key_id):
    """View API key details"""
    client = current_user.client
    api_key = ClientApiKey.query.filter_by(id=key_id, client_id=client.id).first_or_404()
    
    # Get usage statistics
    usage_logs = ApiKeyUsageLog.query.filter_by(api_key_id=key_id).order_by(ApiKeyUsageLog.timestamp.desc()).limit(50).all()
    
    return render_template('client/api_key_details.html', 
                         api_key=api_key, 
                         client=client,
                         usage_logs=usage_logs)


@client_bp.route('/api-keys/<int:key_id>/edit', methods=['GET', 'POST'], endpoint='edit_api_key')
@login_required
@client_required
@feature_required('api_basic', "API key management is available only for plans with API access.")
def edit_api_key(key_id):
    """Edit an existing API key"""
    client = current_user.client
    api_key = ClientApiKey.query.filter_by(id=key_id, client_id=client.id).first_or_404()
    
    form = ClientApiKeyEditForm(obj=api_key)
    
    if request.method == 'GET':
        # Populate permission checkboxes
        permissions = api_key.permissions or []
        form.perm_payments_read.data = 'payments:read' in permissions
        form.perm_payments_create.data = 'payments:create' in permissions
        form.perm_withdrawals_read.data = 'withdrawals:read' in permissions
        form.perm_withdrawals_create.data = 'withdrawals:create' in permissions
        form.perm_invoices_read.data = 'invoices:read' in permissions
        form.perm_invoices_create.data = 'invoices:create' in permissions
        form.perm_balance_read.data = 'balance:read' in permissions
        form.perm_profile_read.data = 'profile:read' in permissions
    
    if form.validate_on_submit():
        try:
            # Update permissions
            permissions = []
            if form.perm_payments_read.data:
                permissions.append('payments:read')
            if form.perm_payments_create.data:
                permissions.append('payments:create')
            if form.perm_withdrawals_read.data:
                permissions.append('withdrawals:read')
            if form.perm_withdrawals_create.data:
                permissions.append('withdrawals:create')
            if form.perm_invoices_read.data:
                permissions.append('invoices:read')
            if form.perm_invoices_create.data:
                permissions.append('invoices:create')
            if form.perm_balance_read.data:
                permissions.append('balance:read')
            if form.perm_profile_read.data:
                permissions.append('profile:read')
            
            # Update the API key
            api_key.name = form.name.data
            api_key.permissions = permissions
            api_key.rate_limit = form.rate_limit.data
            api_key.is_active = form.is_active.data
            api_key.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # Log the update
            AuditTrail.log_action(
                user_id=current_user.id,
                action_type=AuditActionType.API_KEY_UPDATED.value,
                entity_type='ClientApiKey',
                entity_id=api_key.id,
                new_value={'name': form.name.data, 'permissions': permissions, 'active': form.is_active.data}
            )
            
            flash(f'API key "{form.name.data}" updated successfully!', 'success')
            return redirect(url_for('client.api_key_details', key_id=api_key.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating API key: {str(e)}', 'error')
    
    return render_template('client/edit_api_key.html', form=form, api_key=api_key, client=client)


@client_bp.route('/api-keys/<int:key_id>/revoke', methods=['POST'], endpoint='revoke_api_key')
@login_required
@client_required
@feature_required('api_basic', "API key management is available only for plans with API access.")
def revoke_api_key(key_id):
    """Revoke an API key"""
    client = current_user.client
    api_key = ClientApiKey.query.filter_by(id=key_id, client_id=client.id).first_or_404()
    
    form = ClientApiKeyRevokeForm()
    
    if form.validate_on_submit():
        try:
            api_key.is_active = False
            api_key.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # Log the revocation
            AuditTrail.log_action(
                user_id=current_user.id,
                action_type=AuditActionType.API_KEY_REVOKED.value,
                entity_type='ClientApiKey',
                entity_id=api_key.id,
                new_value={'name': api_key.name, 'revoked': True}
            )
            
            flash(f'API key "{api_key.name}" has been revoked successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error revoking API key: {str(e)}', 'error')
    else:
        flash('Invalid form submission', 'error')
    
    return redirect(url_for('client.api_keys'))


@client_bp.route('/api-keys/<int:key_id>/regenerate', methods=['POST'], endpoint='regenerate_api_key')
@login_required
@client_required
@feature_required('api_basic', "API key management is available only for plans with API access.")
def regenerate_api_key(key_id):
    """Regenerate an API key"""
    client = current_user.client
    api_key = ClientApiKey.query.filter_by(id=key_id, client_id=client.id).first_or_404()
    
    if not api_key.is_active:
        flash('Cannot regenerate an inactive API key', 'error')
        return redirect(url_for('client.api_keys'))
    
    try:
        # Generate new key
        new_key = ClientApiKey.generate_key()
        new_hash = ClientApiKey.hash_key(new_key)
        
        api_key.key = new_key
        api_key.key_hash = new_hash
        api_key.key_prefix = new_key[:8] + '...'
        api_key.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log the regeneration
        AuditTrail.log_action(
            user_id=current_user.id,
            action_type=AuditActionType.API_KEY_REGENERATED.value,
            entity_type='ClientApiKey',
            entity_id=api_key.id,
            new_value={'name': api_key.name, 'regenerated': True}
        )
        
        flash(f'API key "{api_key.name}" has been regenerated successfully! Keep the new key secure.', 'success')
        return redirect(url_for('client.api_key_details', key_id=api_key.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error regenerating API key: {str(e)}', 'error')
    
    return redirect(url_for('client.api_keys'))

@client_bp.route('/profile', endpoint='profile')
@login_required
@client_required
def profile():
    """Client profile management"""
    client = current_user.client
    return render_template('client/profile.html', client=client)

@client_bp.route('/settings', endpoint='settings')
@login_required
@client_required
def settings():
    """Client settings"""
    client = current_user.client
    return render_template('client/settings.html', client=client)

@client_bp.route('/support', endpoint='support')
@login_required
@client_required
def support():
    """Support center"""
    client = current_user.client
    return render_template('client/support.html', client=client)

@client_bp.route('/invoices', endpoint='invoices')
@login_required
@client_required
def invoices(client):
    """List all invoices"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
    invoices = Invoice.query.filter_by(client_id=client.id)\
        .order_by(Invoice.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    return render_template('client/invoices.html', invoices=invoices, client=client)

@client_bp.route('/payment-history', endpoint='payment_history')
@login_required
@client_required
def payment_history():
    """Payment history - alias for payments"""
    return redirect(url_for('client.payments'))

@client_bp.route('/documents', endpoint='documents')
@login_required
@client_required
def documents(client):
    """Document management"""
    documents = ClientDocument.query.filter_by(client_id=client.id)\
        .order_by(ClientDocument.created_at.desc()).all()
    return render_template('client/documents.html', documents=documents, client=client)

@client_bp.route('/wallet/configure')
@login_required
def wallet_configure(client):
    """
    Wallet configuration page - only for clients with wallet management feature
    """
    # Check if client has wallet management feature
    if not client.has_feature('wallet_management'):
        flash('Wallet management is available only for Basic plans and above.', 'warning')
        return redirect(url_for('client.dashboard'))
    
    # Legacy check for commission-based clients
    if not client or client.is_commission_based():
        flash('Access denied. This feature is only available for custom wallet clients.', 'error')
        return redirect(url_for('client.dashboard'))
        
    wallets = client.wallets if not hasattr(client.wallets, 'all') else client.wallets.all()
    return render_template('client/wallet_configure.html', 
                         client=client, 
                         wallets=wallets,
                         wallet_types=WalletType)

@client_bp.route('/wallet/configure', methods=['POST'])
@login_required
def wallet_configure_add():
    """Add a new wallet configuration"""
    client = current_user.client
    
    # Check permissions
    if not client.has_feature('wallet_management') or client.is_commission_based():
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        from app.models.client_wallet import ClientWallet, WalletStatus
        
        # Get form data
        wallet_name = request.form.get('wallet_name')
        wallet_type = request.form.get('wallet_type')
        
        if not wallet_name or not wallet_type:
            return jsonify({'success': False, 'message': 'Wallet name and type are required'}), 400
        
        # Create new wallet
        wallet = ClientWallet(
            client_id=client.id,
            wallet_name=wallet_name,
            wallet_type=WalletType(wallet_type),
            status=WalletStatus.PENDING_VERIFICATION
        )
        
        # Handle different wallet types
        if wallet_type == 'custom_api':
            wallet.api_key = request.form.get('api_key')
            wallet.api_secret = request.form.get('api_secret')
            wallet.api_endpoint = request.form.get('api_endpoint')
            wallet.webhook_url = request.form.get('webhook_url')
        elif wallet_type == 'custom_manual':
            wallet_addresses = request.form.get('wallet_addresses')
            if wallet_addresses:
                try:
                    import json
                    addresses = json.loads(wallet_addresses)
                    wallet.settings = {'addresses': addresses}
                except json.JSONDecodeError:
                    return jsonify({'success': False, 'message': 'Invalid wallet addresses format'}), 400
        
        # Handle supported currencies
        currencies = request.form.getlist('supported_currencies')
        if currencies:
            wallet.supported_currencies = currencies
        
        db.session.add(wallet)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Wallet added successfully'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding wallet for client {client.id}: {str(e)}")
        return jsonify({'success': False, 'message': 'Error adding wallet'}), 500

@client_bp.route('/wallet/configure/<int:wallet_id>/test', methods=['POST'])
@login_required
def wallet_test(wallet_id):
    """Test wallet connection"""
    client = current_user.client
    
    # Check permissions
    if not client.has_feature('wallet_management') or client.is_commission_based():
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        from app.models.client_wallet import ClientWallet
        
        wallet = ClientWallet.query.filter_by(id=wallet_id, client_id=client.id).first()
        if not wallet:
            return jsonify({'success': False, 'message': 'Wallet not found'}), 404
        
        # For now, implement basic test logic
        # In production, this would actually test the wallet connection
        if wallet.wallet_type == WalletType.CUSTOM_API:
            if not wallet.api_key or not wallet.api_endpoint:
                return jsonify({'success': False, 'message': 'Missing API credentials'})
            # TODO: Implement actual API test
            return jsonify({'success': True, 'message': 'API wallet connection test successful'})
        elif wallet.wallet_type == WalletType.CUSTOM_MANUAL:
            if not wallet.settings or not wallet.settings.get('addresses'):
                return jsonify({'success': False, 'message': 'No wallet addresses configured'})
            # TODO: Implement address validation
            return jsonify({'success': True, 'message': 'Manual wallet addresses validated'})
        else:
            return jsonify({'success': False, 'message': 'Unknown wallet type'})
            
    except Exception as e:
        current_app.logger.error(f"Error testing wallet {wallet_id}: {str(e)}")
        return jsonify({'success': False, 'message': 'Error testing wallet connection'}), 500

@client_bp.route('/wallet/configure/<int:wallet_id>', methods=['DELETE'])
@login_required
def wallet_delete(wallet_id):
    """Delete a wallet configuration"""
    client = current_user.client
    
    # Check permissions
    if not client.has_feature('wallet_management') or client.is_commission_based():
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        from app.models.client_wallet import ClientWallet
        
        wallet = ClientWallet.query.filter_by(id=wallet_id, client_id=client.id).first()
        if not wallet:
            return jsonify({'success': False, 'message': 'Wallet not found'}), 404
        
        # Check if this is the last wallet for flat-rate clients
        if client.is_flat_rate():
            remaining_wallets = ClientWallet.query.filter_by(client_id=client.id).count()
            if remaining_wallets <= 1:
                return jsonify({'success': False, 'message': 'Cannot delete last wallet - flat-rate clients must have at least one wallet'}), 400
        
        db.session.delete(wallet)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Wallet deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting wallet {wallet_id}: {str(e)}")
        return jsonify({'success': False, 'message': 'Error deleting wallet'}), 500

@client_bp.route('/withdrawal-requests')
@login_required
def withdrawal_requests():
    """View withdrawal requests for flat-rate clients"""
    client = current_user.client
    
    # Only flat-rate clients with wallet management can access this
    if not client.is_flat_rate() or not client.has_feature('wallet_management'):
        flash('This feature is only available for flat-rate clients with wallet management.', 'warning')
        return redirect(url_for('client.dashboard'))
    
    try:
        from app.models.withdrawal import WithdrawalRequest, WithdrawalStatus
        
        # Get filter parameters
        status = request.args.get('status', 'pending')
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        # Build query for this client's withdrawal requests
        query = WithdrawalRequest.query.filter_by(client_id=client.id)
        query = WithdrawalRequest.query.filter_by(client_id=client.id)
        
        # Apply status filter
        if status.lower() != 'all':
            try:
                status_enum = WithdrawalStatus(status.lower())
                query = query.filter(WithdrawalRequest.status == status_enum)
            except ValueError:
                pass
        
        # Order by creation date (newest first)
        query = query.order_by(WithdrawalRequest.created_at.desc())
        
        # Paginate results
        withdrawal_requests = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Get status counts
        status_counts = {
            'ALL': WithdrawalRequest.query.filter_by(client_id=client.id).count(),
            'PENDING': WithdrawalRequest.query.filter_by(client_id=client.id, status=WithdrawalStatus.PENDING).count(),
            'APPROVED': WithdrawalRequest.query.filter_by(client_id=client.id, status=WithdrawalStatus.APPROVED).count(),
            'COMPLETED': WithdrawalRequest.query.filter_by(client_id=client.id, status=WithdrawalStatus.COMPLETED).count(),
            'REJECTED': WithdrawalRequest.query.filter_by(client_id=client.id, status=WithdrawalStatus.REJECTED).count(),
        }
        
        return render_template('client/withdrawal_requests.html', 
                             client=client,
                             withdrawal_requests=withdrawal_requests,
                             status=status,
                             status_counts=status_counts,
                             WithdrawalStatus=WithdrawalStatus)
                             
    except Exception as e:
        current_app.logger.error(f"Error loading withdrawal requests for client {client.id}: {str(e)}")
        flash("Error loading withdrawal requests. Please try again later.", "error")
        return redirect(url_for('client.dashboard'))

@client_bp.route('/withdrawal-requests/create', methods=['GET', 'POST'])
@login_required
def create_withdrawal_request():
    """Create a new withdrawal request for flat-rate clients"""
    client = current_user.client
    
    # Only flat-rate clients with wallet management can access this
    if not client.is_flat_rate() or not client.has_feature('wallet_management'):
        flash('This feature is only available for flat-rate clients with wallet management.', 'warning')
        return redirect(url_for('client.dashboard'))
    
    if request.method == 'POST':
        try:
            from app.models.withdrawal import WithdrawalRequest, WithdrawalStatus, WithdrawalType
            
            # Get form data
            amount = float(request.form.get('amount', 0))
            currency = request.form.get('currency', '').upper()
            user_wallet_address = request.form.get('user_wallet_address', '').strip()
            user_id = request.form.get('user_id', '').strip()
            notes = request.form.get('notes', '').strip()
            
            # Validation
            if amount <= 0:
                return jsonify({'success': False, 'message': 'Amount must be greater than 0'})
                
            if not currency:
                return jsonify({'success': False, 'message': 'Currency is required'})
                
            if not user_wallet_address:
                return jsonify({'success': False, 'message': 'User wallet address is required'})
            
            # Create withdrawal request
            withdrawal_request = WithdrawalRequest(
                client_id=client.id,
                amount=amount,
                currency=currency,
                crypto_address=user_wallet_address,  # This is the user's address
                user_wallet_address=user_wallet_address,
                user_id=user_id if user_id else None,
                withdrawal_type=WithdrawalType.USER_REQUEST,
                status=WithdrawalStatus.PENDING,
                fee=0.0,  # Fee will be calculated later
                net_amount=amount  # Initial net amount
            )
            
            db.session.add(withdrawal_request)
            db.session.commit()
            
            # Log the withdrawal request creation for admin notification
            current_app.logger.info(f"New withdrawal request created: Client {client.name} - {amount} {currency}")
            
            # TODO: Implement notification system for admin dashboard
            
            if request.content_type == 'application/json':
                return jsonify({'success': True, 'message': 'Withdrawal request created successfully'})
            else:
                flash('Withdrawal request created successfully. It will be reviewed by administrators.', 'success')
                return redirect(url_for('client.withdrawal_requests'))
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating withdrawal request: {str(e)}")
            if request.content_type == 'application/json':
                return jsonify({'success': False, 'message': 'Error creating withdrawal request'})
            else:
                flash('Error creating withdrawal request. Please try again.', 'error')
    
    return render_template('client/create_withdrawal_request.html', client=client)

@client_bp.route('/withdrawal-requests/<int:request_id>')
@login_required
def view_withdrawal_request(request_id):
    client = current_user.client
    
    # Only flat-rate clients with wallet management can access this
    if not client.is_flat_rate() or not client.has_feature('wallet_management'):
        flash('This feature is only available for flat-rate clients with wallet management.', 'warning')
        return redirect(url_for('client.dashboard'))
    
    try:
        from app.models.withdrawal import WithdrawalRequest
        
        withdrawal_request = WithdrawalRequest.query.filter_by(
            id=request_id, 
            client_id=client.id
        ).first()
        
        if not withdrawal_request:
            flash('Withdrawal request not found.', 'error')
            return redirect(url_for('client.withdrawal_requests'))
        
        return render_template('client/withdrawal_request_details.html', 
                             client=client,
                             withdrawal_request=withdrawal_request)
                             
    except Exception as e:
        current_app.logger.error(f"Error viewing withdrawal request {request_id}: {str(e)}")
        flash("Error loading withdrawal request details.", "error")
        return redirect(url_for('client.withdrawal_requests'))

@client_bp.route('/withdrawal-analytics', methods=['GET'], endpoint='withdrawal_analytics')
@login_required
@client_required
def withdrawal_analytics(client):
    """Analytics and reporting for withdrawal requests (flat-rate clients only)"""
    # client is injected by decorator
    if not client.has_feature('wallet_management'):
        flash('This feature is only available for flat-rate clients with wallet management.', 'warning')
        return redirect(url_for('client.dashboard'))
    
    try:
        from app.models.withdrawal import WithdrawalRequest, WithdrawalStatus
        from sqlalchemy import func, extract
        from datetime import datetime, timedelta
        import calendar
        
        # Date range filters
        days_filter = request.args.get('days', '30')
        try:
            days = int(days_filter)
        except ValueError:
            days = 30
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Basic statistics
        total_requests = WithdrawalRequest.query.filter_by(client_id=client.id).count()
        
        # Requests in date range
        requests_in_range = WithdrawalRequest.query.filter(
            WithdrawalRequest.client_id == client.id,
            WithdrawalRequest.created_at >= start_date
        ).all()
        
        # Status breakdown
        status_breakdown = {
            'pending': len([r for r in requests_in_range if r.status == WithdrawalStatus.PENDING]),
            'approved': len([r for r in requests_in_range if r.status == WithdrawalStatus.APPROVED]),
            'completed': len([r for r in requests_in_range if r.status == WithdrawalStatus.COMPLETED]),
            'rejected': len([r for r in requests_in_range if r.status == WithdrawalStatus.REJECTED]),
        }
        
        # Amount statistics
        total_amount = sum(float(r.amount) for r in requests_in_range if r.amount)
        completed_amount = sum(float(r.amount) for r in requests_in_range 
                             if r.status == WithdrawalStatus.COMPLETED and r.amount)
        
        avg_amount = total_amount / len(requests_in_range) if requests_in_range else 0
        avg_processing_time = 0
        
        # Calculate average processing time for completed requests
        completed_requests = [r for r in requests_in_range if r.status == WithdrawalStatus.COMPLETED and r.processed_at]
        if completed_requests:
            processing_times = [(r.processed_at - r.created_at).total_seconds() / 3600 
                              for r in completed_requests]  # Convert to hours
            avg_processing_time = sum(processing_times) / len(processing_times)
        
        # Monthly breakdown for chart data
        monthly_data = {}
        for request in requests_in_range:
            month_key = request.created_at.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'total': 0,
                    'completed': 0,
                    'amount': 0.0
                }
            monthly_data[month_key]['total'] += 1
            if request.status == WithdrawalStatus.COMPLETED:
                monthly_data[month_key]['completed'] += 1
                monthly_data[month_key]['amount'] += float(request.amount or 0)
        
        # Recent activity (last 10 requests)
        recent_requests = WithdrawalRequest.query.filter_by(client_id=client.id)\
            .order_by(WithdrawalRequest.created_at.desc())\
            .limit(10).all()
        
        analytics_data = {
            'total_requests': total_requests,
            'requests_in_range': len(requests_in_range),
            'status_breakdown': status_breakdown,
            'total_amount': total_amount,
            'completed_amount': completed_amount,
            'avg_amount': avg_amount,
            'avg_processing_time': avg_processing_time,
            'monthly_data': monthly_data,
            'recent_requests': recent_requests,
            'date_range': {
                'start': start_date,
                'end': datetime.utcnow(),
                'days': days
            }
        };
        
        return render_template('client/withdrawal_analytics.html', 
                             client=client,
                             analytics=analytics_data)
                             
    except Exception as e:
        current_app.logger.error(f"Error generating withdrawal analytics for client {client.id}: {str(e)}")
        flash("Error loading withdrawal analytics. Please try again later.", "error")
        return redirect(url_for('client.withdrawal_requests'))

@client_bp.route('/withdrawal-requests/<int:request_id>/edit-amount', methods=['POST'])
@login_required
@client_required
def edit_withdrawal_amount(request_id):
    """Edit withdrawal amount (client can only edit pending requests)"""
    client = current_user.client
    
    # Check if client has wallet management feature
    if not client.has_feature('wallet_management'):
        flash('This feature is only available for flat-rate clients with wallet management.', 'warning')
        return redirect(url_for('client.dashboard'))
    
    try:
        from app.models.withdrawal import WithdrawalRequest, WithdrawalStatus
        
        withdrawal_request = WithdrawalRequest.query.filter_by(
            id=request_id, 
            client_id=client.id,
            status=WithdrawalStatus.PENDING  # Only allow editing pending requests
        ).first()
        
        if not withdrawal_request:
            flash('Withdrawal request not found or cannot be edited.', 'error')
            return redirect(url_for('client.withdrawal_requests'))
        
        new_amount = request.form.get('new_amount')
        edit_reason = request.form.get('edit_reason', '').strip()
        
        if not new_amount:
            flash('New amount is required.', 'danger')
            return redirect(url_for('client.withdrawal_request_details', request_id=request_id))
        
        try:
            new_amount = float(new_amount)
            if new_amount <= 0:
                flash('Amount must be greater than 0.', 'danger')
                return redirect(url_for('client.withdrawal_request_details', request_id=request_id))
        except ValueError:
            flash('Invalid amount format.', 'danger')
            return redirect(url_for('client.withdrawal_request_details', request_id=request_id))
        
        # Check client balance
        if new_amount > client.balance:
            flash(f'Insufficient balance. Available: ${client.balance:.2f}, Requested: ${new_amount:.2f}', 'danger')
            return redirect(url_for('client.withdrawal_request_details', request_id=request_id))
        
        old_amount = withdrawal_request.amount
        withdrawal_request.amount = new_amount
        withdrawal_request.updated_at = datetime.utcnow()
        
        # Add edit history note
        edit_note = f"Amount edited by client from ${old_amount:.2f} to ${new_amount:.2f}"
        if edit_reason:
            edit_note += f". Reason: {edit_reason}"
        withdrawal_request.client_note = edit_note
        
        db.session.commit()
        
        flash(f'Withdrawal amount updated successfully from ${old_amount:.2f} to ${new_amount:.2f}.', 'success')
        return redirect(url_for('client.withdrawal_request_details', request_id=request_id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error editing withdrawal amount for client {client.id}, request {request_id}: {str(e)}")
        flash("Error updating withdrawal amount. Please try again later.", "error")
        return redirect(url_for('client.withdrawal_request_details', request_id=request_id))
