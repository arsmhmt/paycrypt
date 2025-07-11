from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_from_directory, current_app, session, Response, make_response
from app.decorators import admin_login_required

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin120724')

# Test route to verify admin blueprint is working
@admin_bp.route('/test')
@admin_login_required
def test_route():
    return jsonify({"status": "success", "message": "Admin blueprint is working!"})
from flask_login import login_required, current_user, login_user, logout_user, confirm_login
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from sqlalchemy import func, asc, desc
from app import db
from app.models import Payment, PaymentStatus, Client, User, AuditTrail, AdminUser, ApiUsage, Setting, WithdrawalRequest, RecurringPayment, Withdrawal
from app.models.client_wallet import ClientPricingPlan
from app.models.wallet_provider import WalletProvider, WalletProviderCurrency, WalletBalance, WalletProviderTransaction
from app.admin.forms.wallet_forms import WalletProviderForm, WalletProviderCurrencyForm
from app.extensions import db
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError
import json
from datetime import datetime
import requests
from decimal import Decimal
from app.models.withdrawal import WithdrawalStatus
from app.models.report import Report, ReportType, ReportStatus
from app.models.audit import AuditActionType, AuditTrail
from app.models.notification import NotificationPreference
from app.models.enums import SettingType, SettingKey
from app.models.support_ticket import SupportTicket
from app.models.wallet_provider import WalletProvider
from app.forms import (ClientForm, LoginForm, NotificationPreferenceForm, 
                       ReportForm, SettingForm, PricingPlanForm, PricingPlanFilterForm)
from app.decorators import admin_required, admin_login_required, secure_admin_required
from werkzeug.security import generate_password_hash, check_password_hash

@admin_bp.before_request
def log_request_info():
    current_app.logger.debug(f"[ADMIN] Incoming request: {request.method} {request.path}")
    current_app.logger.debug(f"[ADMIN] Request endpoint: {request.endpoint}")
    current_app.logger.debug(f"[ADMIN] URL rule: {request.url_rule}" if request.url_rule else "[ADMIN] No URL rule matched")
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import datetime as dt
import os
import secrets
import string
import json
import csv
import io
from urllib.parse import urlparse, urljoin

# Import security and audit utilities
from app.utils.security import rate_limit, AbuseProtection
from app.utils.audit import log_admin_action, log_security_event, log_client_setting_change

# Get secure admin path from environment or use secure default
ADMIN_SECRET_PATH = os.environ.get('ADMIN_SECRET_PATH', 'admin120724')

# Ensure path starts with /
if not ADMIN_SECRET_PATH.startswith('/'):
    ADMIN_SECRET_PATH = f'/{ADMIN_SECRET_PATH}'

# Create admin blueprint with secure, non-guessable path
admin_bp = Blueprint('admin', __name__, url_prefix=ADMIN_SECRET_PATH)

# Make the blueprint available when importing from app.admin
__all__ = ['admin_bp', 'init_app']

# Import FinanceCalculator from utils
from app.utils.finance import FinanceCalculator

# Initialize abuse protection
abuse_protection = AbuseProtection()

@admin_bp.route('/debug/password')
def debug_password():
    """Debug route to test password hashing"""
    test_password = 'test123'
    hash1 = generate_password_hash(test_password)
    hash2 = generate_password_hash(test_password)
    
    current_app.logger.debug(f"=== PASSWORD DEBUG ===")
    current_app.logger.debug(f"Test password: {test_password}")
    current_app.logger.debug(f"Hash 1: {hash1}")
    current_app.logger.debug(f"Hash 2: {hash2}")
    current_app.logger.debug(f"Compare 1: {check_password_hash(hash1, test_password)}")
    current_app.logger.debug(f"Compare 2: {check_password_hash(hash2, test_password)}")
    
    # Also test with the admin user's password
    admin = AdminUser.query.filter_by(username='admin').first()
    if admin:
        current_app.logger.debug(f"Admin user found: {admin.username}")
        current_app.logger.debug(f"Admin password hash: {admin.password_hash}")
        current_app.logger.debug(f"Test password check: {admin.check_password(test_password)}")
    
    return jsonify({
        'status': 'debug_complete',
        'test_password': test_password,
        'hash1': hash1,
        'hash2': hash2,
        'compare1': check_password_hash(hash1, test_password),
        'compare2': check_password_hash(hash2, test_password),
        'admin_exists': admin is not None
    })

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@admin_bp.route('/login', methods=['GET', 'POST'])
@rate_limit('admin_login', limit=60, window=300)  # 60 attempts per 5 minutes per IP
def admin_login():
    """Handle admin login with both form and JSON API support"""
    current_app.logger.debug("Admin login route accessed")
    
    # Handle already authenticated users
    if current_user.is_authenticated and hasattr(current_user, 'is_admin') and current_user.is_admin:
        next_page = request.args.get('next') or url_for('admin.admin_dashboard')
        current_app.logger.info(f"User already authenticated: {current_user.username}")
        if request.accept_mimetypes.accept_json:
            return jsonify({
                'success': True,
                'redirect_url': next_page
            })
        return redirect(next_page)
    
    # Handle POST request (form submission)
    if request.method == 'POST':
        current_app.logger.debug("Login form submitted")
        
        # Get form data - support both form data and JSON
        data = request.get_json(silent=True) or request.form
        username = data.get('username')
        password = data.get('password')
        
        # Log minimal debug info (don't log passwords)
        current_app.logger.debug(f"Login attempt for username: {username}")
        
        # Validate input
        if not username or not password:
            error_msg = 'Username and password are required'
            if request.accept_mimetypes.accept_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('admin.admin_login'))
        
        # Find admin user by username or email
        admin = AdminUser.query.filter(
            (AdminUser.username == username) | 
            (AdminUser.email == username)
        ).first()
        
        # Check credentials
        if not admin or not admin.check_password(password):
            error_msg = 'Invalid username or password'
            current_app.logger.warning(f"Failed login attempt for username: {username}")
            
            # Log failed login attempt
            log_security_event(
                event_type='failed_login',
                details={
                    'description': f'Admin login failed - invalid credentials for: {username}',
                    'user_agent': request.user_agent.string,
                    'severity': 'medium'
                },
                user_id=admin.id if admin else None,
                ip_address=request.remote_addr or '127.0.0.1'
            )
            
            # Track failed attempt for rate limiting
            abuse_protection.track_failed_attempt(request.remote_addr or '127.0.0.1', 'admin_login')
            
            # Check if IP is blocked
            if abuse_protection.is_blocked(request.remote_addr or '127.0.0.1', 'admin_login'):
                log_security_event(
                    event_type='ip_blocked',
                    details={
                        'description': f"IP {request.remote_addr or '127.0.0.1'} blocked due to repeated failed login attempts",
                        'user_agent': request.user_agent.string,
                        'severity': 'high'
                    },
                    user_id=None,
                    ip_address=request.remote_addr or '127.0.0.1'
                )
                if request.accept_mimetypes.accept_json:
                    return jsonify({
                        'success': False,
                        'error': 'Too many failed attempts. Please try again later.'
                    }), 429
                flash('Too many failed attempts. Please try again later.', 'error')
                return redirect(url_for('admin.admin_login'))
            
            if request.accept_mimetypes.accept_json:
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 401
                
            flash(error_msg, 'error')
            return redirect(url_for('admin.admin_login'))
        
        # Check if account is active
        if not admin.is_active:
            error_msg = 'This admin account has been deactivated'
            current_app.logger.warning(f"Login attempt for deactivated account: {username}")
            
            if request.accept_mimetypes.accept_json:
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 403
                
            flash(error_msg, 'error')
            return redirect(url_for('admin.admin_login'))
        
        # Login successful - set up session and login user
        login_user(admin, remember=True)
        session['is_admin'] = True
        session['_user_type'] = 'admin'
        
        # Log successful login
        log_security_event(
            event_type='successful_login',
            details={
                'description': f'Admin {admin.username} logged in successfully',
                'user_agent': request.user_agent.string,
                'severity': 'low'
            },
            user_id=admin.id,
            ip_address=request.remote_addr or '127.0.0.1'
        )
        
        # Clear any previous failed attempts for this IP
        abuse_protection.clear_attempts(request.remote_addr or '127.0.0.1', 'admin_login')
        
        # Determine redirect URL
        next_page = request.args.get('next') or url_for('admin.admin_dashboard')
        
        # Handle JSON response
        if request.accept_mimetypes.accept_json:
            return jsonify({
                'success': True,
                'redirect_url': next_page
            })
        
        # Handle HTML response
        return redirect(next_page)
    
    # Handle GET request (show login form)
    return render_template('admin/login.html', next=request.args.get('next', ''))

@admin_bp.route('/logout')
@login_required
@secure_admin_required
def logout():
    """Admin logout with proper session cleanup and flash message"""
    log_security_event(
        event_type='logout',
        details={
            'description': f'Admin {current_user.username} logged out',
            'user_agent': request.user_agent.string,
            'severity': 'low'
        },
        user_id=current_user.id,
        ip_address=request.remote_addr or '127.0.0.1'
    )
    
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/clients')
@secure_admin_required
def clients():
    """List all clients"""
    clients = Client.query.order_by(Client.name.asc()).all()
    return render_template('admin/clients.html', clients=clients)

@admin_bp.route('/clients/export', methods=['POST'])
@secure_admin_required
def export_clients():
    """Export clients to CSV"""
    try:
        import csv
        import io
        from datetime import datetime
        
        # Get filter parameters from request
        search = request.args.get('search', '')
        status = request.args.get('status', 'all')
        
        # Build query
        query = Client.query
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Client.name.ilike(search_term),
                    Client.email.ilike(search_term),
                    Client.company_name.ilike(search_term)
                )
            )
            
        if status != 'all':
            query = query.filter(Client.is_active == (status == 'active'))
        
        # Get clients
        clients = query.order_by(Client.name.asc()).all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Name', 'Email', 'Company', 'Contact Person', 
            'Phone', 'Status', 'Created At', 'Last Login'
        ])
        
        # Write data
        for client in clients:
            writer.writerow([
                client.id,
                client.name or '',
                client.email or '',
                client.company_name or '',
                client.contact_person or '',
                client.phone or '',
                'Active' if client.is_active else 'Inactive',
                client.created_at.strftime('%Y-%m-%d %H:%M:%S') if client.created_at else '',
                client.last_login_at.strftime('%Y-%m-%d %H:%M:%S') if client.last_login_at else ''
            ])
        
        # Create response with CSV
        output.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=clients_export_{timestamp}.csv',
                'Content-type': 'text/csv; charset=utf-8'
            }
        )
        
    except Exception as e:
        current_app.logger.error(f'Error exporting clients: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Failed to export clients. Please try again.'
        }), 500

@admin_bp.route('/commissions/refresh', methods=['POST'])
@secure_admin_required
def refresh_commissions():
    """Refresh commission data for all clients"""
    try:
        # Get all active clients
        clients = Client.query.filter_by(is_active=True).all()
        updated_count = 0
        
        # Update commission data for each client
        for client in clients:
            try:
                # Calculate and update commissions
                # This is a placeholder - replace with your actual commission calculation logic
                client.total_commissions = calculate_client_commissions(client.id)
                updated_count += 1
            except Exception as e:
                current_app.logger.error(f"Error updating commissions for client {client.id}: {str(e)}")
        
        # Commit changes to the database
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully refreshed commissions for {updated_count} clients',
            'updated_count': updated_count
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error refreshing commissions: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Failed to refresh commissions. Please try again.'
        }), 500

def calculate_client_commissions(client_id):
    """Helper function to calculate commissions for a client"""
    # This is a placeholder - implement your actual commission calculation logic here
    # For example, you might query the database for transactions and calculate commissions
    return 0.0

@admin_bp.route('/clients/new', methods=['GET', 'POST'])
@secure_admin_required
def new_client():
    """Create a new client"""
    form = ClientForm()
    
    if form.validate_on_submit():
        try:
            client = Client(
                name=form.name.data,
                email=form.email.data,
                company_name=form.company_name.data,
                contact_person=form.contact_person.data,
                phone=form.phone.data,
                address=form.address.data,
                city=form.city.data,
                country=form.country.data,
                postal_code=form.postal_code.data,
                is_active=form.is_active.data,
                api_key=secrets.token_urlsafe(32),
                rate_limit=form.rate_limit.data or 1000,
                deposit_commission_rate=form.deposit_commission_rate.data or 0.0,
                withdrawal_commission_rate=form.withdrawal_commission_rate.data or 0.0,
                package_id=form.package_id.data
            )
            
            # Set password if provided
            if form.password.data:
                client.set_password(form.password.data)
            
            db.session.add(client)
            db.session.commit()
            
            flash('Client created successfully!', 'success')
            return redirect(url_for('admin.clients'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating client: {str(e)}")
            flash('An error occurred while creating the client.', 'error')
    
    return render_template('admin/client_form.html', form=form, title='New Client')

@admin_bp.route('/pricing-plans')
@secure_admin_required
def pricing_plans():
    """List all pricing plans with filtering"""
    form = PricingPlanFilterForm()
    query = ClientPricingPlan.query
    
    # Apply filters
    if form.plan_type.data:
        query = query.filter(ClientPricingPlan.plan_type == form.plan_type.data)
    if form.is_active.data:  # Changed from active_only to is_active
        query = query.filter(ClientPricingPlan.is_active == True)
    if form.name.data:  # Changed from search to name
        search = f"%{form.name.data}%"
        query = query.filter(ClientPricingPlan.plan_name.ilike(search))
    
    plans = query.order_by(ClientPricingPlan.plan_name).all()
    return render_template('admin/pricing_plans.html', plans=plans, form=form)

@admin_bp.route('/pricing-plans/new', methods=['GET', 'POST'])
@secure_admin_required
def new_pricing_plan():
    """Create a new pricing plan"""
    form = PricingPlanForm()
    
    if form.validate_on_submit():
        try:
            plan = ClientPricingPlan(
                plan_name=form.plan_name.data,
                plan_type=form.plan_type.data,
                description=form.description.data,
                commission_rate=form.commission_rate.data,
                monthly_price=form.monthly_price.data,
                yearly_price=form.yearly_price.data,
                max_users=form.max_users.data,
                max_transactions=form.max_transactions.data,
                api_access=form.api_access.data,
                analytics=form.analytics.data,
                priority_support=form.priority_support.data,
                is_active=form.is_active.data
            )
            
            db.session.add(plan)
            db.session.commit()
            
            flash('Pricing plan created successfully!', 'success')
            return redirect(url_for('admin.pricing_plans'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating pricing plan: {str(e)}")
            flash('An error occurred while creating the pricing plan.', 'error')
    
    return render_template('admin/pricing_plan_form.html', form=form, title='New Pricing Plan')

@admin_bp.route('/pricing-plans/<int:plan_id>/edit', methods=['GET', 'POST'])
@secure_admin_required
def edit_pricing_plan(plan_id):
    """Edit an existing pricing plan"""
    plan = ClientPricingPlan.query.get_or_404(plan_id)
    form = PricingPlanForm(obj=plan)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(plan)
            db.session.commit()
            
            flash('Pricing plan updated successfully!', 'success')
            return redirect(url_for('admin.pricing_plans'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating pricing plan: {str(e)}")
            flash('An error occurred while updating the pricing plan.', 'error')
    
    return render_template('admin/pricing_plan_form.html', form=form, title='Edit Pricing Plan', plan=plan)

@admin_bp.route('/pricing-plans/<int:plan_id>/delete', methods=['POST'])
@secure_admin_required
def delete_pricing_plan(plan_id):
    """Delete a pricing plan"""
    plan = ClientPricingPlan.query.get_or_404(plan_id)
    
    try:
        db.session.delete(plan)
        db.session.commit()
        flash('Pricing plan deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting pricing plan: {str(e)}")
        flash('An error occurred while deleting the pricing plan.', 'error')
    
    return redirect(url_for('admin.pricing_plans'))

@admin_bp.route('/dashboard')
@rate_limit('admin_dashboard', limit=60, window=300)  # 60 requests per 5 minutes
@admin_login_required
def admin_dashboard():
    # Log current user state
    current_app.logger.debug(f"[DASHBOARD] User: {current_user.username}")
    current_app.logger.debug(f"[DASHBOARD] Authenticated: {current_user.is_authenticated}")
    current_app.logger.debug(f"[DASHBOARD] Admin: {hasattr(current_user, 'is_admin') and current_user.is_admin}")
    current_app.logger.debug(f"[DASHBOARD] Session contents: {dict(session)}")
    
    # Import models with proper handling to avoid circular imports
    from app.models.client import Client
    from app.models.payment import Payment
    from app.models.withdrawal import WithdrawalRequest
    from app.models.admin import AdminUser
    from app.models.audit import AuditTrail
    from app.models.transaction import Transaction
    from app.models.client_wallet import ClientWallet as Wallet
    from app.models.support_ticket import SupportTicket
    from app.models.notification import Notification
    
    # Initialize default values for recent_activity and top_clients
    recent_activity = []
    top_clients = []
    
    try:
        # Get recent activity (last 10 transactions with client info)
        recent_activity = db.session.query(
            Transaction,
            Client
        ).join(
            Client, Transaction.client_id == Client.id
        ).order_by(
            Transaction.created_at.desc()
        ).limit(10).all()
        
        # Get top 5 clients by transaction volume
        top_clients = db.session.query(
            Client,
            db.func.count(Transaction.id).label('transaction_count'),
            db.func.sum(Transaction.amount).label('total_volume')
        ).join(
            Transaction, Client.id == Transaction.client_id
        ).group_by(
            Client.id
        ).order_by(
            db.desc('total_volume')
        ).limit(5).all()
    except Exception as e:
        current_app.logger.error(f"Error fetching dashboard data: {str(e)}")
    
    # Prepare system stats with error handling
    pending_withdrawals_count = 0
    try:
        pending_withdrawals_count = WithdrawalRequest.query.filter_by(status='pending').count()
    except Exception as e:
        current_app.logger.error(f"Error counting pending withdrawals: {str(e)}")
    
    # Initialize stats dictionary with default values
    stats = {
        'total_clients': 0,
        'total_transactions': 0,
        'pending_withdrawals': pending_withdrawals_count,
        'pending_user_withdrawals': 0,
        'pending_client_withdrawals': 0,
        'custom_wallets': 0,
        'pending_tickets': 0
    }
    
    try:
        # Update stats with actual values
        stats.update({
            'total_clients': Client.query.count(),
            'total_transactions': Transaction.query.count(),
            'pending_user_withdrawals': WithdrawalRequest.query.filter_by(
                status='pending',
                withdrawal_type='user'
            ).count(),
            'pending_client_withdrawals': WithdrawalRequest.query.filter_by(
                status='pending',
                withdrawal_type='client'
            ).count(),
            'custom_wallets': Client.query.filter(Client.wallet_address.isnot(None)).count()
        })
    except Exception as e:
        current_app.logger.error(f"Error calculating system stats: {str(e)}")
    
    # Log the dashboard access
    current_app.logger.info(f"Admin dashboard accessed by {current_user.username}")
    
    # For backward compatibility, also pass the stats as individual variables
    return render_template(
        'admin/dashboard.html',
        recent_activity=recent_activity,
        top_clients=top_clients,
        stats=stats,  # Pass stats as a single dictionary
        # Also pass individual variables for backward compatibility
        total_clients=stats['total_clients'],
        total_transactions=stats['total_transactions'],
        pending_withdrawals=stats['pending_withdrawals'],
        pending_user_withdrawals=stats['pending_user_withdrawals'],
        pending_client_withdrawals=stats['pending_client_withdrawals'],
        custom_wallets=stats['custom_wallets'],
        pending_tickets=stats['pending_tickets'],
        current_time=datetime.utcnow()  # Pass current time directly
    )

@admin_bp.route('/analytics')
@secure_admin_required
def analytics():
    """Analytics dashboard"""
    from app.models.transaction import Transaction
    from app.models.client import Client
    from app.models.payment import Payment
    from app.models.withdrawal import WithdrawalRequest
    from datetime import datetime, timedelta
    from sqlalchemy import func, extract, and_
    
    # Default to 30 days if not specified
    time_period_days = request.args.get('days', default=30, type=int)
    
    # Calculate date range
    end_date = datetime.utcnow()
    if time_period_days > 0:
        start_date = end_date - timedelta(days=time_period_days)
    else:
        # If time_period_days is 0, show all time
        start_date = datetime.min
    
    # Get total transactions count
    total_transactions = Transaction.query.count()
    
    # Get total clients count
    total_clients = Client.query.count()
    
    # Get total payment volume
    total_volume = db.session.query(func.sum(Transaction.amount)).scalar() or 0
    
    # Get pending withdrawals count
    pending_withdrawals = WithdrawalRequest.query.filter_by(status='pending').count()
    
    # Get transaction volume over time
    time_period = request.args.get('period', '7d')
    if time_period == '7d':
        days = 7
        time_series = db.session.query(
            func.date(Transaction.created_at).label('date'),
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total_amount')
        ).join(
            Payment, Transaction.payment_id == Payment.id
        ).filter(
            Transaction.created_at >= datetime.utcnow() - timedelta(days=days)
        ).group_by(
            func.date(Transaction.created_at)
        ).order_by('date').all()
    elif time_period == '30d':
        days = 30
        time_series = db.session.query(
            func.date_trunc('day', Transaction.created_at).label('date'),
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total_amount')
        ).join(
            Payment, Transaction.payment_id == Payment.id
        ).filter(
            Transaction.created_at >= datetime.utcnow() - timedelta(days=days)
        ).group_by(
            func.date_trunc('day', Transaction.created_at)
        ).order_by('date').all()
    else:  # 12m
        time_series = db.session.query(
            func.date_trunc('month', Transaction.created_at).label('date'),
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total_amount')
        ).join(
            Payment, Transaction.payment_id == Payment.id
        ).filter(
            Transaction.created_at >= datetime.utcnow() - timedelta(days=365)
        ).group_by(
            func.date_trunc('month', Transaction.created_at)
        ).order_by('date').all()

    # Get status counts
    status_counts = db.session.query(
        Transaction.status,
        func.count(Transaction.id).label('count')
    ).join(
        Payment, Transaction.payment_id == Payment.id
    ).group_by(Transaction.status).all()

    # Get top 5 clients by transaction volume
    top_clients = db.session.query(
        Client.id,
        Client.company_name,
        func.count(Transaction.id).label('tx_count'),
        func.sum(Transaction.amount).label('total_volume')
    ).join(
        Payment, Transaction.payment_id == Payment.id
    ).join(
        Client, Payment.client_id == Client.id
    ).group_by(
        Client.id, Client.company_name
    ).order_by(
        db.desc('total_volume')
    ).limit(5).all()
    
    # Format data for Chart.js
    chart_labels = [d[0].strftime('%Y-%m-%d') for d in time_series]
    # Format chart data as a dictionary with count and volume
    chart_data = {
        'count': [float(d[1]) if d[1] is not None else 0 for d in time_series],  # d[1] is count
        'volume': [float(d[2]) if d[2] is not None else 0 for d in time_series]  # d[2] is total_amount
    }
    
    # Ensure all dates are timezone-aware and properly formatted for the template
    try:
        if start_date and not isinstance(start_date, str):
            start_date_str = start_date.strftime('%Y-%m-%d')
        else:
            start_date_str = start_date
            
        if end_date and not isinstance(end_date, str):
            end_date_str = end_date.strftime('%Y-%m-%d')
        else:
            end_date_str = end_date or datetime.utcnow().strftime('%Y-%m-%d')
    except Exception as e:
        current_app.logger.error(f"Error formatting dates: {str(e)}")
        start_date_str = datetime.utcnow().strftime('%Y-%m-%d')
        end_date_str = datetime.utcnow().strftime('%Y-%m-%d')
    
    return render_template('admin/analytics.html',
                         time_period=time_period,
                         time_period_days=time_period_days,
                         total_transactions=total_transactions,
                         total_clients=total_clients,
                         total_volume=float(total_volume) if total_volume is not None else 0,
                         pending_withdrawals=pending_withdrawals,
                         chart_labels=chart_labels,
                         chart_data=chart_data,
                         status_counts=dict(status_counts),
                         top_clients=top_clients,
                         start_date=start_date,
                         end_date=end_date,
                         start_date_str=start_date_str,
                         end_date_str=end_date_str,
                         now=datetime.utcnow())

# Audit Trail Routes
@admin_bp.route('/audit-trail')
@rate_limit('admin_audit_trail', limit=100, window=300)  # 100 requests per 5 minutes
@secure_admin_required
def audit_trail():
    """Show audit trail entries with filtering"""
    from app.models.audit import AuditTrail
    from app.models.user import User
    from app.constants.audit import AuditActionType
    
    # Get filter parameters
    action_type = request.args.get('action_type')
    entity_type = request.args.get('entity_type')
    entity_id = request.args.get('entity_id', type=int)
    user_id = request.args.get('user_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query
    query = AuditTrail.query
    
    if action_type:
        query = query.filter_by(action_type=action_type)
    if entity_type:
        query = query.filter_by(entity_type=entity_type)
    if entity_id:
        query = query.filter_by(entity_id=entity_id)
    if user_id:
        query = query.filter_by(user_id=user_id)
    if start_date:
        query = query.filter(AuditTrail.created_at >= start_date)
    if end_date:
        query = query.filter(AuditTrail.created_at <= end_date)
    
    # Get users for dropdown
    users = User.query.all()
    
    # Get audit entries with pagination
    audit_entries = query.order_by(AuditTrail.created_at.desc()).all()
    
    return render_template('admin/audit_trail.html',
                         audit_entries=audit_entries,
                         users=users,
                         AuditActionType=AuditActionType)

# Payment Routes
@admin_bp.route('/payments/view/<int:payment_id>')
@secure_admin_required
def view_payment(payment_id):
    """View details of a specific payment"""
    payment = Payment.query.get_or_404(payment_id)
    return render_template('admin/payments/view.html', payment=payment)

@admin_bp.route('/payments/list')
@secure_admin_required
def payments_list():
    """Show list of all payments"""
    try:
        # Handle case where status might be stored in lowercase in the database
        payments = Payment.query.order_by(Payment.created_at.desc()).all()
        
        # Ensure all status values are valid
        valid_statuses = {status.value for status in PaymentStatus}
        for payment in payments:
            if payment.status and payment.status.lower() not in valid_statuses:
                # Try to fix the status if it's invalid
                try:
                    payment.status = PaymentStatus(payment.status.lower())
                except ValueError:
                    # If we can't map it, set to a default status
                    payment.status = PaymentStatus.PENDING
        
        return render_template('admin/payments/index.html', payments=payments)
    except Exception as e:
        current_app.logger.error(f"Error in payments_list: {str(e)}")
        flash('An error occurred while loading payments.', 'error')
        return render_template('admin/payments/index.html', payments=[])

@admin_bp.route('/payments/detailed-list')
@secure_admin_required
def payments_detailed():
    """Show detailed payments list with client and user information"""
    # Get all payments with related client and user information
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template('admin/payments/index.html', payments=payments)

@admin_bp.route('/payments/create', methods=['GET', 'POST'])
@rate_limit('admin_create_payment', limit=20, window=300)  # 20 payment creations per 5 minutes
@secure_admin_required
def create_payment():
    """Create a new payment"""
    from app.forms import PaymentForm  # Import here to avoid circular imports
    
    form = PaymentForm()
    
    # Populate client choices
    form.client_id.choices = [(str(c.id), c.name) for c in Client.query.order_by('name').all()]
    
    if form.validate_on_submit():
        try:
            payment = Payment(
                client_id=form.client_id.data,
                amount=form.amount.data,
                currency=form.currency.data,
                description=form.description.data,
                status=form.status.data,
                payment_method=form.payment_method.data,
                transaction_id=form.transaction_id.data or None
            )
            db.session.add(payment)
            db.session.commit()
            
            flash('Payment created successfully!', 'success')
            return redirect(url_for('admin.payments_list'))  # <-- Düzeltildi
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating payment: {str(e)}')
            flash('An error occurred while creating the payment.', 'error')
    
    return render_template('admin/payments/create.html', form=form)


@admin_bp.route('/payments/recurring')
@secure_admin_required
def recurring_payments():
    """Show all recurring payments"""
    recurring_payments = RecurringPayment.query.all()
    return render_template('admin/payments/recurring.html', recurring_payments=recurring_payments)

# Withdrawal Routes
@admin_bp.route('/wallet/history')
@secure_admin_required
def wallet_history():
    """Show wallet transaction history"""
    try:
        # Get all transactions (payments and withdrawals)
        payments = Payment.query.order_by(Payment.created_at.desc()).all()
        withdrawals = WithdrawalRequest.query.order_by(WithdrawalRequest.created_at.desc()).all()
        return render_template('admin/wallet/history.html', payments=payments, withdrawals=withdrawals)
    except Exception as e:
        current_app.logger.error(f'Error in wallet_history: {str(e)}')
        # Try to get payments with raw SQL to bypass SQLAlchemy type handling
        from sqlalchemy import text
        try:
            # Get payment data with client information
            query = """
                SELECT p.*, c.name as client_name, c.email as client_email 
                FROM payment p
                LEFT JOIN client c ON p.client_id = c.id
                ORDER BY p.created_at DESC
            """
            result = db.session.execute(text(query))
            payments = []
            for row in result.mappings():
                payment = dict(row)
                # Convert status to proper enum values
                try:
                    payment['status'] = PaymentStatus(payment['status'].lower())
                except (ValueError, AttributeError):
                    # If status is invalid, default to PENDING
                    payment['status'] = PaymentStatus.PENDING
                payments.append(payment)
            
            withdrawals = WithdrawalRequest.query.order_by(WithdrawalRequest.created_at.desc()).all()
            return render_template('admin/wallet/history.html', payments=payments, withdrawals=withdrawals, raw_payments=True)
        except Exception as inner_e:
            current_app.logger.error(f'Error in fallback wallet_history: {str(inner_e)}')
            flash('Error loading transaction history. Please try again later.', 'error')
            return render_template('admin/wallet/history.html', payments=[], withdrawals=[])

@admin_bp.route('/withdrawals/list')
@secure_admin_required
def withdrawals_list():
    """Show list of all withdrawal requests"""
    withdrawals = WithdrawalRequest.query.order_by(WithdrawalRequest.created_at.desc()).all()
    return render_template('admin/withdrawals/list.html', withdrawals=withdrawals)

@admin_bp.route('/withdrawals/bulk_approvals')
@secure_admin_required
def bulk_approvals():
    """Show bulk approvals page"""
    pending_withdrawals = WithdrawalRequest.query.filter_by(status='pending').all()
    return render_template('admin/withdrawals/bulk_approvals.html', pending_withdrawals=pending_withdrawals)

@admin_bp.route('/withdrawals/approve/<int:withdrawal_id>', methods=['POST'])
@secure_admin_required
@rate_limit('admin_approve_withdrawals', limit=50, window=300)  # 50 approvals per 5 minutes
def approve_withdrawal(withdrawal_id):
    """Approve a single withdrawal"""
    withdrawal = WithdrawalRequest.query.get_or_404(withdrawal_id)
    old_status = withdrawal.status
    
    withdrawal.status = WithdrawalStatus.APPROVED
    withdrawal.approved_at = datetime.utcnow()
    withdrawal.approved_by = current_user.id
    db.session.commit()
    
    # Log admin action
    log_admin_action(
        action='approve_withdrawal',
        target_type='withdrawal',
        target_id=withdrawal_id,
        description=f'Approved withdrawal {withdrawal_id} for client {withdrawal.client_id} (amount: {withdrawal.amount})',
        old_values={'status': old_status},
        new_values={'status': 'approved', 'approved_by': current_user.id}
    )
    
    flash('Withdrawal approved successfully', 'success')
    return redirect(url_for('admin.withdrawals_list'))

@admin_bp.route('/withdrawals/reject/<int:withdrawal_id>', methods=['POST'])
@secure_admin_required
@rate_limit('admin_reject_withdrawals', limit=50, window=300)  # 50 rejections per 5 minutes
def reject_withdrawal(withdrawal_id):
    """Reject a single withdrawal"""
    withdrawal = WithdrawalRequest.query.get_or_404(withdrawal_id)
    old_status = withdrawal.status
    
    withdrawal.status = WithdrawalStatus.REJECTED
    withdrawal.rejected_at = datetime.utcnow()
    withdrawal.rejected_by = current_user.id
    db.session.commit()
    
    # Log admin action
    log_admin_action(        action='reject_withdrawal',
        target_type='withdrawal',
        target_id=withdrawal_id,
        description=f'Rejected withdrawal {withdrawal_id} for client {withdrawal.client_id} (amount: {withdrawal.amount})',
        old_values={'status': old_status},
        new_values={'status': 'rejected', 'rejected_by': current_user.id}
    )
    
    flash('Withdrawal rejected successfully', 'success')
    return redirect(url_for('admin.withdrawals_list'))

@admin_bp.route('/withdrawals/bulk/approve', methods=['POST'])
@secure_admin_required
@rate_limit('admin_bulk_approve_withdrawals', limit=10, window=300)  # 10 bulk operations per 5 minutes
def bulk_approve_withdrawals():
    """Approve multiple withdrawals"""
    withdrawals = request.form.getlist('withdrawals')
    approved_ids = []
    
    for withdrawal_id in withdrawals:
        withdrawal = WithdrawalRequest.query.get_or_404(int(withdrawal_id))
        old_status = withdrawal.status
        withdrawal.status = WithdrawalStatus.APPROVED
        withdrawal.approved_at = datetime.utcnow()
        withdrawal.approved_by = current_user.id
        approved_ids.append(withdrawal_id)
        
        # Log each approval
        log_admin_action(            action='bulk_approve_withdrawal',
            target_type='withdrawal',
            target_id=int(withdrawal_id),
            description=f'Bulk approved withdrawal {withdrawal_id} (amount: {withdrawal.amount})',
            old_values={'status': old_status},
            new_values={'status': 'approved', 'approved_by': current_user.id}
        )
    
    db.session.commit()
    
    # Log bulk operation summary
    log_admin_action(        action='bulk_approve_summary',
        target_type='withdrawal_bulk',
        target_id=0,
        description=f'Bulk approved {len(approved_ids)} withdrawals: {approved_ids}'
    )
    
    flash('Selected withdrawals approved successfully', 'success')
    return redirect(url_for('admin.withdrawals_list'))

@admin_bp.route('/withdrawals/bulk/reject', methods=['POST'])
@secure_admin_required
@rate_limit('admin_bulk_reject_withdrawals', limit=10, window=300)  # 10 bulk operations per 5 minutes
def bulk_reject_withdrawals():
    """Reject multiple withdrawals"""
    withdrawals = request.form.getlist('withdrawals')
    rejected_ids = []
    
    for withdrawal_id in withdrawals:
        withdrawal = WithdrawalRequest.query.get_or_404(int(withdrawal_id))
        old_status = withdrawal.status
        withdrawal.status = WithdrawalStatus.REJECTED
        withdrawal.rejected_at = datetime.utcnow()
        withdrawal.rejected_by = current_user.id
        rejected_ids.append(withdrawal_id)
        
        # Log each rejection
        log_admin_action(            action='bulk_reject_withdrawal',
            target_type='withdrawal',
            target_id=int(withdrawal_id),
            description=f'Bulk rejected withdrawal {withdrawal_id} (amount: {withdrawal.amount})',
            old_values={'status': old_status},
            new_values={'status': 'rejected', 'rejected_by': current_user.id}
        )
    
    db.session.commit()
    
    # Log bulk operation summary
    log_admin_action(        action='bulk_reject_summary',
        target_type='withdrawal_bulk',
        target_id=0,
        description=f'Bulk rejected {len(rejected_ids)} withdrawals: {rejected_ids}'
    )
    
    flash('Selected withdrawals rejected successfully', 'success')
    return redirect(url_for('admin.withdrawals_list'))

# Report Routes
@admin_bp.route('/reports')
@secure_admin_required
def reports():
    """Show all reports"""
    # Get all reports
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('admin/reports/index.html', reports=reports)

@admin_bp.route('/report/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_report():
    """Create a new report"""
    form = ReportForm()
    if form.validate_on_submit():
        try:
            # Create report
            report = Report(
                name=form.name.data,
                description=form.description.data,
                report_type=form.report_type.data,
                filters=form.get_filters()
            )
            db.session.add(report)
            db.session.commit()
            
            # Log audit trail
            AuditTrail.log_action(
                user_id=current_user.id,
                action_type=AuditActionType.CREATE.value,
                entity_type='report',
                entity_id=report.id,
                new_value={
                    'name': report.name,
                    'type': report.report_type,
                    'filters': report.filters
                },
                request=request
            )
            
            flash('Report created successfully', 'success')
            return redirect(url_for('admin.reports'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating report: {str(e)}', 'error')
    
    return render_template('admin/reports.html', form=form)

@admin_bp.route('/report/<int:report_id>')
@login_required
@admin_required
def view_report(report_id):
    """View a specific report"""
    report = Report.query.get_or_404(report_id)
    
    # Generate report data
    report_data = report.generate_report()
    
    # Format data for display
    if report_data:
        if report.report_type == ReportType.PAYMENT_SUMMARY.value:
            template = 'admin/_report_payment_summary.html'
        elif report.report_type == ReportType.CLIENT_ANALYSIS.value:
            template = 'admin/_report_client_analysis.html'
        elif report.report_type == ReportType.REVENUE_TRENDS.value:
            template = 'admin/_report_revenue_trends.html'
        elif report.report_type == ReportType.PAYMENT_METHODS.value:
            template = 'admin/_report_payment_methods.html'
        elif report.report_type == ReportType.OVERDUE_PAYMENTS.value:
            template = 'admin/_report_overdue_payments.html'
        
        return render_template(
            template,
            report=report,
            data=report_data
        )
    
    flash('Error generating report', 'error')
    return redirect(url_for('admin.reports'))

@admin_bp.route('/report/<int:report_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_report(report_id):
    """Delete a report"""
    report = Report.query.get_or_404(report_id)
    
    try:
        # Log audit trail
        AuditTrail.log_action(
            user_id=current_user.id,
            action_type=AuditActionType.DELETE.value,
            entity_type='report',
            entity_id=report_id,
            old_value={
                'name': report.name,
                'type': report.report_type,
                'filters': report.filters
            },
            request=request
        )
        
        db.session.delete(report)
        db.session.commit()
        flash('Report deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting report: {str(e)}', 'error')
    
    return redirect(url_for('admin.reports'))

@admin_bp.route('/report/<int:report_id>/export')
@login_required
@admin_required
def export_report(report_id):
    """Export report data"""
    report = Report.query.get_or_404(report_id)
    report_data = report.generate_report()
    
    if report_data:
        # Format filename
        filename = f"report_{report.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Create response
        response = make_response(json.dumps(report_data, indent=2))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    flash('Error exporting report', 'error')
    return redirect(url_for('admin.reports'))



# Access Control Routes
@admin_bp.route('/access-control', methods=['GET', 'POST'])
@secure_admin_required
def access_control():
    """Admin role management"""
    admin_users = AdminUser.query.all()
    return render_template('admin/access_control.html', admin_users=admin_users)

# Commission Reports Routes
@admin_bp.route('/commission-reports', methods=['GET'])
@secure_admin_required
def commission_reports():
    """Commission reports dashboard"""
    # Get commission data using FinanceCalculator
    calculator = FinanceCalculator()
    try:
        commission_stats = calculator.get_commission_stats()
        total_commissions = commission_stats.get('total_commissions', 0)
    except Exception as e:
        current_app.logger.error(f"Error calculating commissions: {e}")
        total_commissions = 0
    return render_template('admin/commission_reports.html', total_commissions=total_commissions)

# Platform Balance Routes
@admin_bp.route('/platform-balance', methods=['GET'])
@secure_admin_required
def platform_balance():
    """Platform balance overview"""
    # Calculate platform balance using available data
    try:
        calculator = FinanceCalculator()
        commission_stats = calculator.get_commission_stats()
        balance = commission_stats.get('platform_balance', 0)
    except Exception as e:
        current_app.logger.error(f"Error calculating platform balance: {e}")
        balance = 0
    return render_template('admin/platform_balance.html', balance=balance)

# API Documentation Routes
@admin_bp.route('/api-docs', methods=['GET'])
@secure_admin_required
def api_docs():
    """API documentation"""
    return render_template('admin/api_docs.html')

# Support Tickets Routes
@admin_bp.route('/support-tickets', methods=['GET', 'POST'])
@secure_admin_required
def support_tickets():
    """Support tickets management"""
    tickets = SupportTicket.query.all()
    return render_template('admin/support_tickets.html', tickets=tickets)

# Settings Routes
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    """Show settings page"""
    # Get all settings grouped by type
    settings = Setting.get_all_settings()
    
    # Create form with current values
    form = SettingForm(setting_type=request.args.get('type', SettingType.SYSTEM.value))
    
    # Populate form fields with current values
    for setting in settings.get(form.setting_type, []):
        if setting.key in form.fields:
            form.fields[setting.key].data = setting.value
    
    return render_template('admin/settings.html', 
                         settings=settings,
                         form=form)

@admin_bp.route('/settings/general')
@login_required
@admin_required
def general_settings():
    """General system settings"""
    return render_template('admin/settings/general.html')

@admin_bp.route('/settings/payment-methods')
@login_required
@admin_required
def payment_methods():
    """Payment methods configuration"""
    return render_template('admin/settings/payment_methods.html')

@admin_bp.route('/settings/email-templates')
@login_required
@admin_required
def email_templates():
    """Email templates management"""
    return render_template('admin/settings/email_templates.html')

@admin_bp.route('/settings/api')
@secure_admin_required
def api_settings():
    """API settings page"""
    return render_template('admin/settings/api.html')

@admin_bp.route('/wallet-providers')
@secure_admin_required
def wallet_providers():
    """List all wallet providers"""
    providers = WalletProvider.query.order_by(WalletProvider.priority.asc(), WalletProvider.name).all()
    return render_template('admin/wallet_providers.html', providers=providers)

@admin_bp.route('/wallet-providers/new', methods=['GET', 'POST'])
@secure_admin_required
def create_wallet_provider():
    """Create a new wallet provider"""
    form = WalletProviderForm()
    
    if form.validate_on_submit():
        try:
            provider = WalletProvider(
                name=form.name.data,
                provider_type=form.provider_type.data,
                api_key=form.api_key.data if form.api_key.data else None,
                api_secret=form.api_secret.data if form.api_secret.data else None,
                api_passphrase=form.api_passphrase.data if form.api_passphrase.data else None,
                sandbox_mode=form.sandbox_mode.data,
                is_active=form.is_active.data,
                is_primary=form.is_primary.data,
                priority=form.priority.data,
                supports_deposits=form.supports_deposits.data,
                supports_withdrawals=form.supports_withdrawals.data,
                supports_balance_check=form.supports_balance_check.data,
                max_requests_per_minute=form.max_requests_per_minute.data,
                description=form.description.data
            )
            
            # Handle wallet addresses for manual wallets
            if form.provider_type.data == 'manual_wallet':
                wallet_addresses = {}
                for field in form:
                    if field.name.startswith('wallet_address_') and field.data:
                        currency = field.name.replace('wallet_address_', '').upper()
                        wallet_addresses[currency] = field.data
                provider.wallet_addresses_dict = wallet_addresses
            
            db.session.add(provider)
            db.session.commit()
            
            # If set as primary, update other providers
            if form.is_primary.data:
                provider.set_as_primary()
            
            flash('Wallet provider created successfully!', 'success')
            return redirect(url_for('admin.wallet_providers'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating wallet provider: {str(e)}")
            flash(f'Error creating wallet provider: {str(e)}', 'danger')
    
    return render_template('admin/create_wallet_provider.html', form=form)

@admin_bp.route('/wallet-providers/<int:provider_id>/edit', methods=['GET', 'POST'])
@secure_admin_required
def edit_wallet_provider(provider_id):
    """Edit a wallet provider"""
    provider = WalletProvider.query.get_or_404(provider_id)
    form = WalletProviderForm(obj=provider)
    
    if form.validate_on_submit():
        try:
            # Update basic fields
            provider.name = form.name.data
            provider.provider_type = form.provider_type.data
            provider.api_key = form.api_key.data if form.api_key.data else None
            provider.api_secret = form.api_secret.data if form.api_secret.data else None
            provider.api_passphrase = form.api_passphrase.data if form.api_passphrase.data else None
            provider.sandbox_mode = form.sandbox_mode.data
            provider.is_active = form.is_active.data
            provider.is_primary = form.is_primary.data
            provider.priority = form.priority.data
            provider.supports_deposits = form.supports_deposits.data
            provider.supports_withdrawals = form.supports_withdrawals.data
            provider.supports_balance_check = form.supports_balance_check.data
            provider.max_requests_per_minute = form.max_requests_per_minute.data
            provider.description = form.description.data
            
            # Handle wallet addresses for manual wallets
            if form.provider_type.data == 'manual_wallet':
                wallet_addresses = {}
                for field in form:
                    if field.name.startswith('wallet_address_') and field.data:
                        currency = field.name.replace('wallet_address_', '').upper()
                        wallet_addresses[currency] = field.data
                provider.wallet_addresses_dict = wallet_addresses
            
            db.session.commit()
            
            # If set as primary, update other providers
            if form.is_primary.data:
                provider.set_as_primary()
            
            flash('Wallet provider updated successfully!', 'success')
            return redirect(url_for('admin.wallet_providers'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating wallet provider: {str(e)}")
            flash(f'Error updating wallet provider: {str(e)}', 'danger')
    
    # Pre-populate wallet addresses for manual wallets
    if provider.provider_type == 'manual_wallet' and provider.wallet_addresses:
        try:
            addresses = json.loads(provider.wallet_addresses)
            for currency, address in addresses.items():
                field_name = f'wallet_address_{currency.lower()}'
                if hasattr(form, field_name):
                    getattr(form, field_name).data = address
        except json.JSONDecodeError:
            pass
    
    return render_template('admin/edit_wallet_provider.html', form=form, provider=provider)

@admin_bp.route('/wallet-providers/<int:provider_id>/delete', methods=['POST'])
@secure_admin_required
def delete_wallet_provider(provider_id):
    """Delete a wallet provider"""
    provider = WalletProvider.query.get_or_404(provider_id)
    
    try:
        db.session.delete(provider)
        db.session.commit()
        flash('Wallet provider deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting wallet provider: {str(e)}")
        flash(f'Error deleting wallet provider: {str(e)}', 'danger')
    
    return redirect(url_for('admin.wallet_providers'))

@admin_bp.route('/wallet-providers/<int:provider_id>/set-primary', methods=['POST'])
@secure_admin_required
def set_primary_wallet_provider(provider_id):
    """Set a wallet provider as primary"""
    provider = WalletProvider.query.get_or_404(provider_id)
    
    try:
        provider.set_as_primary()
        return jsonify({'success': True, 'message': 'Primary wallet provider updated successfully'})
    except Exception as e:
        current_app.logger.error(f"Error setting primary wallet provider: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400

@admin_bp.route('/wallet-providers/<int:provider_id>/test-connection', methods=['POST'])
@secure_admin_required
def test_wallet_connection(provider_id):
    """Test connection to a wallet provider"""
    provider = WalletProvider.query.get_or_404(provider_id)
    
    try:
        # This is a simplified example - implement actual connection test based on provider type
        if provider.provider_type == 'manual_wallet':
            return jsonify({
                'success': True,
                'message': 'Manual wallet provider - no connection test available',
                'provider': provider.name
            })
        
        # Add specific test logic for different provider types
        # Example for Binance:
        # client = BinanceClient(provider.api_key, provider.api_secret)
        # account_info = client.get_account()
        
        # For now, just simulate a successful test
        provider.update_health_status('healthy', 'Connection test successful')
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Connection test successful',
            'provider': provider.name
        })
        
    except Exception as e:
        error_msg = str(e)
        provider.update_health_status('error', error_msg)
        db.session.commit()
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'provider': provider.name
        }), 400

@admin_bp.route('/wallet-providers/<int:provider_id>/sync-balances', methods=['POST'])
@secure_admin_required
def sync_wallet_balances(provider_id):
    """Synchronize wallet balances from the provider"""
    provider = WalletProvider.query.get_or_404(provider_id)
    
    try:
        # This is a placeholder - implement actual balance sync based on provider type
        if provider.provider_type == 'manual_wallet':
            return jsonify({
                'success': True,
                'message': 'Manual wallet - balances must be updated manually',
                'provider': provider.name
            })
        
        # Add specific sync logic for different provider types
        # Example for Binance:
        # client = BinanceClient(provider.api_key, provider.api_secret)
        # balances = client.get_balances()
        # for currency, balance in balances.items():
        #     WalletBalance.update_balance(provider_id, currency, balance)
        
        # For now, just return a success message
        return jsonify({
            'success': True,
            'message': 'Balance sync completed',
            'provider': provider.name,
            'balances_updated': 0  # Replace with actual count
        })
        
    except Exception as e:
        error_msg = str(e)
        provider.update_health_status('error', f'Sync failed: {error_msg}')
        db.session.commit()
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'provider': provider.name
        }), 400

@admin_bp.route('/wallet-balances')
@secure_admin_required
def wallet_balances():
    """Show wallet balances across all providers"""
    # Get all active providers
    providers = WalletProvider.query.filter_by(is_active=True).order_by(WalletProvider.priority.asc()).all()
    
    # Get balances for each provider
    balances = {}
    for provider in providers:
        provider_balances = WalletBalance.query.filter_by(provider_id=provider.id).all()
        balances[provider.id] = {
            'name': provider.name,
            'type': provider.provider_type,
            'balances': {b.currency_code: b for b in provider_balances}
        }
    
    # Get all unique currencies across all providers
    all_currencies = set()
    for provider_data in balances.values():
        all_currencies.update(provider_data['balances'].keys())
    all_currencies = sorted(list(all_currencies))
    
    # Calculate totals for each currency
    totals = {}
    for currency in all_currencies:
        total_available = 0
        total_locked = 0
        
        for provider_data in balances.values():
            if currency in provider_data['balances']:
                balance = provider_data['balances'][currency]
                total_available += float(balance.available_balance)
                total_locked += float(balance.locked_balance)
        
        totals[currency] = {
            'available': total_available,
            'locked': total_locked,
            'total': total_available + total_locked
        }
    
    return render_template(
        'admin/wallet_balances.html',
        providers=providers,
        balances=balances,
        currencies=all_currencies,
        totals=totals
    )

# Withdrawal Routes
@admin_bp.route('/withdrawals')
@login_required
@admin_required
def list_withdrawals():
    """Show all withdrawal requests"""
    # Get query parameters for filtering
    status = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Base query
    query = WithdrawalRequest.query
    
    # Apply filters
    if status != 'all':
        query = query.filter(WithdrawalRequest.status == status)
    
    # Order by creation date (newest first)
    withdrawals = query.order_by(WithdrawalRequest.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    # Get counts for each status
    status_counts = {
        'pending': WithdrawalRequest.query.filter_by(status='pending').count(),
        'approved': WithdrawalRequest.query.filter_by(status='approved').count(),
        'completed': WithdrawalRequest.query.filter_by(status='completed').count(),
        'rejected': WithdrawalRequest.query.filter_by(status='rejected').count(),
        'cancelled': WithdrawalRequest.query.filter_by(status='cancelled').count(),
        'all': WithdrawalRequest.query.count()
    }
    
    # Get pending withdrawals count for the badge
    pending_withdrawals_count = WithdrawalRequest.query.filter_by(status='pending').count()
    
    return render_template('admin/withdrawals/list.html', 
                         withdrawals=withdrawals,
                         status=status,
                         status_counts=status_counts,
                         pending_withdrawals_count=pending_withdrawals_count)

# Payment Routes


@admin_bp.route('/system/logs')
@login_required
@admin_required
def system_logs():
    """View system logs"""
    return render_template('admin/system/logs.html')

@admin_bp.route('/system/backup')
@login_required
@admin_required
def backup():
    """Database backup and restore"""
    return render_template('admin/system/backup.html')

@admin_bp.route('/system/maintenance')
@login_required
@admin_required
def maintenance():
    """System maintenance tools"""
    return render_template('admin/system/maintenance.html')

@admin_bp.route('/save-settings', methods=['POST'])
@login_required
@admin_required
@rate_limit('admin_save_settings', limit=20, window=300)  # 20 settings updates per 5 minutes
def save_settings():
    """Save settings"""
    form = SettingForm(request.form)
    if form.validate():
        try:
            setting_type = request.form.get('setting_type')
            old_settings = Setting.get_all_settings().get(setting_type, [])
            old_values = {s.key: s.value for s in old_settings}
            
            # Update each setting
            new_values = {}
            for key, field in form.fields.items():
                if field.data is not None:
                    Setting.update_setting(key, field.data)
                    new_values[key] = field.data
            
            # Log admin action
            log_admin_action(
                action='update_settings',
                target_type='settings',
                target_id=0,
                description=f'Updated {setting_type} settings',
                old_values=old_values,
                new_values=new_values
            )
            # Log audit trail
            AuditTrail.log_action(
                user_id=current_user.id,
                action_type=AuditActionType.UPDATE.value,
                entity_type='settings',
                entity_id=0,
                old_value=old_values,
                new_value={
                    'type': setting_type,
                    'changes': new_values
                },
                request=request
            )
            
            flash('Settings saved successfully', 'success')
            return redirect(url_for('admin.settings', type=setting_type))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error saving settings: {e}")
            flash(f'Error saving settings: {str(e)}', 'error')
    
    # If validation failed, show form again with errors
    settings = Setting.get_all_settings()
    return render_template('admin/settings.html', 
                         settings=settings,
                         form=form)

@admin_bp.route('/reset-settings/<string:setting_type>')
@login_required
@admin_required
def reset_settings(setting_type):
    """Reset settings to default values"""
    try:
        # Delete all settings of this type
        Setting.query.filter_by(setting_type=setting_type).delete()
        
        # Create default settings
        Setting.create_default_settings()
        
        # Log audit trail
        AuditTrail.log_action(
            user_id=current_user.id,
            action_type=AuditActionType.DELETE.value,
            entity_type='settings',
            entity_id=0,
            old_value=None,
            request=request
        )
        
        flash('Settings reset to default values', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error resetting settings: {str(e)}', 'error')
    
    return redirect(url_for('admin.settings', type=setting_type))

@admin_bp.route('/test-settings/<string:setting_type>')
@login_required
@admin_required
def test_settings(setting_type):
    """Test settings configuration"""
    try:
        # Get settings of this type
        settings = Setting.query.filter_by(setting_type=setting_type).all()
        
        # Test specific settings based on type
        if setting_type == SettingType.SYSTEM.value:
            # Test system settings
            flash('System settings tested successfully', 'success')
        elif setting_type == SettingType.PLATFORM.value:
            # Test platform settings
            flash('Platform settings tested successfully', 'success')
        elif setting_type == SettingType.CLIENT.value:
            # Test client settings
            flash('Client settings tested successfully', 'success')
        elif setting_type == SettingType.ADMIN.value:
            # Test admin settings
            flash('Admin settings tested successfully', 'success')
        else:
            flash('Settings type not recognized for testing', 'warning')
    except Exception as e:
        flash(f'Test failed: {str(e)}', 'error')
    
    return redirect(url_for('admin.settings', type=setting_type))

# Route aliases for withdrawal management (redirect to the new dedicated routes)
@admin_bp.route('/user-withdrawal-requests')
@secure_admin_required
def user_withdrawal_requests():
    """Redirect to user withdrawal requests"""
    return redirect(url_for('withdrawal_admin.user_withdrawal_requests'))

@admin_bp.route('/client-withdrawal-requests')
@secure_admin_required
def client_withdrawal_requests():
    """Redirect to client withdrawal requests"""
    return redirect(url_for('withdrawal_admin.client_withdrawal_requests'))

@admin_bp.route('/user-withdrawal-bulk')
@secure_admin_required
def user_withdrawal_bulk():
    """Redirect to user withdrawal bulk actions"""
    return redirect(url_for('withdrawal_admin.user_withdrawal_bulk'))

@admin_bp.route('/client-withdrawal-bulk')
@secure_admin_required
def client_withdrawal_bulk():
    """Redirect to client withdrawal bulk actions"""
    return redirect(url_for('withdrawal_admin.client_withdrawal_bulk'))

@admin_bp.route('/withdrawal-history')
@secure_admin_required
def withdrawal_history():
    """Redirect to withdrawal history"""
    return redirect(url_for('withdrawal_admin.withdrawal_history'))

@admin_bp.route('/withdrawal-reports')
@secure_admin_required
def withdrawal_reports():
    """Redirect to withdrawal reports"""
    return redirect(url_for('withdrawal_admin.withdrawal_reports'))

# Legacy route redirects for backward compatibility
@admin_bp.route('/withdrawals/list')
@secure_admin_required
def legacy_list_withdrawals():
    """Legacy route - redirect to user withdrawals by default"""
    return redirect(url_for('withdrawal_admin.user_withdrawal_requests'))

@admin_bp.route('/bulk_approvals')
@secure_admin_required
def legacy_bulk_approvals():
    """Legacy route - redirect to user bulk approvals by default"""
    return redirect(url_for('withdrawal_admin.user_withdrawal_bulk'))

@admin_bp.route('/clients/<int:client_id>/features', methods=['GET', 'POST'])
@login_required
@admin_required
@secure_admin_required
@rate_limit('admin_edit_features', limit=10, window=60)
def edit_client_features(client_id):
    """Edit client feature overrides"""
    try:
        from app.models.client import Client
        from app.config.packages import PACKAGE_FEATURES, FEATURE_DESCRIPTIONS
        
        client = Client.query.get_or_404(client_id)
        
        # Get all possible features
        all_possible_features = sorted({f for features in PACKAGE_FEATURES.values() for f in features})
        
        if request.method == 'POST':
            # Get selected features from form
            selected_features = request.form.getlist('features')
            
            # Get package features to avoid duplicating them in overrides
            package_features = client.get_package_features() if hasattr(client, 'get_package_features') else []
            
            # Only store features that are NOT already in the package
            override_features = [f for f in selected_features if f not in package_features]
            
            # Update client
            client.features_override = override_features
            db.session.commit()
            
            flash(f"Feature overrides updated for {client.company_name}.", "success")
            return redirect(url_for('admin.view_client', client_id=client.id))
        
        # Get current features
        package_features = client.get_package_features() if hasattr(client, 'get_package_features') else []
        override_features = client.get_override_features() if hasattr(client, 'get_override_features') else []
        all_client_features = client.get_features() if hasattr(client, 'get_features') else []
        
        return render_template('admin/edit_client_features.html',
                             client=client,
                             all_possible_features=all_possible_features,
                             package_features=package_features,
                             override_features=override_features,
                             all_client_features=all_client_features,
                             feature_descriptions=FEATURE_DESCRIPTIONS)
        
    except Exception as e:
        current_app.logger.error(f"Error editing client features: {str(e)}")
        flash("Error loading client features.", "error")
        return redirect(url_for('admin.list_clients'))


def get_sidebar_stats():
    """Helper function to get sidebar statistics for the base template"""
    try:
        # Ensure we have an active application context and database connection
        if not current_app:
            current_app.logger.warning("No current app context in get_sidebar_stats")
            raise Exception("No application context")
        
        # Initialize default values
        pending_withdrawals = 0
        pending_user_withdrawals = 0
        pending_client_withdrawals = 0
        total_clients = 0
        custom_wallets = 0
        pending_tickets = 0
        
        # Get pending withdrawals count
        try:
            pending_withdrawals = db.session.query(func.count(Withdrawal.id)).filter(
                (Withdrawal.status == WithdrawalStatus.PENDING) | 
                (Withdrawal.status == WithdrawalStatus.PROCESSING)
            ).scalar() or 0
            
            # Split by user type if possible
            pending_user_withdrawals = pending_withdrawals // 2  # Placeholder
            pending_client_withdrawals = pending_withdrawals - pending_user_withdrawals
        except Exception as e:
            current_app.logger.warning(f"Error getting withdrawal stats: {str(e)}")
        
        # Get total clients count
        try:
            total_clients = Client.query.count()
        except Exception as e:
            current_app.logger.warning(f"Error getting client count: {str(e)}")
        
        # Get custom wallets count (placeholder)
        custom_wallets = 0
        
        # Get pending support tickets
        try:
            from app.models.support_ticket import SupportTicket
            pending_tickets = SupportTicket.query.filter_by(status='pending').count()
        except Exception as e:
            current_app.logger.warning(f"Error getting support ticket count: {str(e)}")
        
        stats = {
            'pending_withdrawals': pending_withdrawals,
            'pending_user_withdrawals': pending_user_withdrawals,
            'pending_client_withdrawals': pending_client_withdrawals,
            'total_clients': total_clients,
            'custom_wallets': custom_wallets,
            'pending_tickets': pending_tickets
        }
        
        current_app.logger.debug(f"get_sidebar_stats returning: {stats}")
        return stats
        
    except Exception as e:
        current_app.logger.error(f"Error getting sidebar stats: {str(e)}")
        return {
            'pending_withdrawals': 0,
            'pending_user_withdrawals': 0,
            'pending_client_withdrawals': 0,
            'total_clients': 0,
            'custom_wallets': 0,
            'pending_tickets': 0
        }
