import logging
import traceback
from datetime import datetime, timedelta
from functools import wraps
import logging
import re

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import current_user, login_required, login_user
from flask_wtf.csrf import generate_csrf
from app.extensions import db, csrf
from flask_jwt_extended import (
    jwt_required, 
    get_jwt_identity, 
    verify_jwt_in_request,
    get_jwt,
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    decode_token
)
from sqlalchemy import desc, func, or_
import requests

# Import models and forms
from app.models import AdminUser, Client, Payment, AuditTrail, RecurringPayment, Platform, Transaction, Withdrawal, User, ApiUsage, PaymentStatus, SupportTicket
from app.models.withdrawal import WithdrawalStatus
from app.models.setting import Setting
from app.decorators import admin_login_required
from app.utils.helpers import generate_api_key
from app.forms import AdminUserForm, PaymentFilterForm, ClientForm, AdminWithdrawalActionForm, PaymentForm
from app.models.client_package import ClientPackage, Feature, PackageFeature, ClientType, PackageStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get secure admin path from environment or use secure default
import os
ADMIN_SECRET_PATH = os.environ.get('ADMIN_SECRET_PATH', 'admin120724')

# Ensure path starts with /
if not ADMIN_SECRET_PATH.startswith('/'):
    ADMIN_SECRET_PATH = f'/{ADMIN_SECRET_PATH}'

# Create admin blueprint with secure, non-guessable path
admin_bp = Blueprint('admin', __name__, url_prefix=ADMIN_SECRET_PATH)

# Initialize admin routes
bp = admin_bp

@admin_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user = get_jwt_identity()
    new_token = create_access_token(
        identity=current_user,
        additional_claims={"type": "admin", "is_superuser": True},
        expires_delta=timedelta(minutes=15)
    )
    response = jsonify({"success": True})
    set_access_cookies(response, new_token)
    return response

def get_dashboard_stats():
    """Helper function to get dashboard statistics"""
    # Get current month and last month dates
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    last_24h = datetime.utcnow() - timedelta(hours=24)
    
    # Calculate success rate
    current_month_transactions = Transaction.query.filter(Transaction.created_at >= current_month_start).all()
    total_transactions_this_month = len(current_month_transactions)
    successful_transactions = len([t for t in current_month_transactions if t.status.value == 'completed'])
    success_rate = (successful_transactions / total_transactions_this_month * 100) if total_transactions_this_month > 0 else 95.5
    
    # 24h volume calculation
    volume_24h = db.session.query(func.coalesce(func.sum(Transaction.btc_value), 0)).filter(
        Transaction.created_at >= last_24h
    ).scalar() or 0
    
    # Commission calculation (assuming 1% commission)
    total_commission = (db.session.query(func.coalesce(func.sum(Transaction.btc_value), 0)).scalar() or 0) * 0.01
    
    # Pending withdrawals count
    pending_withdrawals_count = db.session.query(func.count(Withdrawal.id)).filter(
        Withdrawal.status.in_([WithdrawalStatus.PENDING, WithdrawalStatus.PROCESSING])
    ).scalar() or 0
    
    # Support tickets stats (placeholder - implement when support module is ready)
    pending_tickets = 0
    resolved_tickets = 0
    total_tickets = 0
    
    # Exchange rates (placeholder - implement with real API)
    btc_usd_rate = 45000.00
    eth_usd_rate = 3000.00
    usd_try_rate = 32.50
    btc_try_rate = btc_usd_rate * usd_try_rate
    
    # Growth calculations (month-over-month)
    last_month_transactions = Transaction.query.filter(
        Transaction.created_at >= last_month_start,
        Transaction.created_at < current_month_start
    ).count()
    last_month_clients = Client.query.filter(
        Client.created_at >= last_month_start,
        Client.created_at < current_month_start
    ).count()
    last_month_volume = db.session.query(func.coalesce(func.sum(Transaction.btc_value), 0)).filter(
        Transaction.created_at >= last_month_start,
        Transaction.created_at < current_month_start
    ).scalar() or 0
    
    # Calculate growth percentages
    revenue_growth = ((volume_24h - last_month_volume) / last_month_volume * 100) if last_month_volume > 0 else 0
    transactions_growth = ((total_transactions_this_month - last_month_transactions) / last_month_transactions * 100) if last_month_transactions > 0 else 0
    clients_growth = ((Client.query.filter(Client.created_at >= current_month_start).count() - last_month_clients) / last_month_clients * 100) if last_month_clients > 0 else 0
    commission_growth = revenue_growth * 0.8  # Assuming commission follows revenue trends
    
    # System health metrics
    system_load = 12  # Placeholder - implement actual system monitoring
    uptime_days = 99.9  # Placeholder - implement actual uptime tracking
    
    # Client balance statistics (placeholder - implement with actual balance queries)
    total_btc_balance = 12.5430
    total_eth_balance = 156.7821
    total_usdt_balance = 875430.50
    btc_active_clients = 45
    eth_active_clients = 38
    usdt_active_clients = 52
    avg_btc_balance = total_btc_balance / btc_active_clients if btc_active_clients > 0 else 0
    avg_eth_balance = total_eth_balance / eth_active_clients if eth_active_clients > 0 else 0
    avg_usdt_balance = total_usdt_balance / usdt_active_clients if usdt_active_clients > 0 else 0
    
    # Flagged activities count
    flagged_activities = 3  # Placeholder - implement actual flagged activity detection
    
    stats = {
        'total_clients': Client.query.count(),
        'total_transactions': Transaction.query.count(),
        'total_volume': db.session.query(func.coalesce(func.sum(Transaction.btc_value), 0)).scalar() or 0,
        'pending_withdrawals': pending_withdrawals_count,
        'success_rate': success_rate,
        'volume_24h': volume_24h,
        'total_commission': total_commission,
        
        # Support tickets
        'pending_tickets': pending_tickets,
        'resolved_tickets': resolved_tickets,
        'total_tickets': total_tickets,
        
        # Exchange rates
        'btc_usd_rate': btc_usd_rate,
        'eth_usd_rate': eth_usd_rate,
        'usd_try_rate': usd_try_rate,
        'btc_try_rate': btc_try_rate,
        
        # Growth metrics
        'revenue_growth': abs(revenue_growth),
        'transactions_growth': abs(transactions_growth),
        'clients_growth': abs(clients_growth),
        'commission_growth': abs(commission_growth),
        
        # System health
        'system_load': system_load,
        'uptime_days': uptime_days,
        
        # Client balances
        'total_btc_balance': total_btc_balance,
        'total_eth_balance': total_eth_balance,
        'total_usdt_balance': total_usdt_balance,
        'btc_active_clients': btc_active_clients,
        'eth_active_clients': eth_active_clients,
        'usdt_active_clients': usdt_active_clients,
        'avg_btc_balance': avg_btc_balance,
        'avg_eth_balance': avg_eth_balance,
        'avg_usdt_balance': avg_usdt_balance,
        
        # Flagged activities
        'flagged_activities': flagged_activities,
        
        # Change percentages (placeholder for now)
        'volume_change': 0,
        'transactions_change': 0,
        'active_clients_change': 0,
        'success_rate_change': 0,
        'commission_change': 0
    }
    return stats

@admin_bp.route('/login', methods=['GET', 'POST'], endpoint='admin_login')
def admin_login():
    """
    Authenticate an admin user
    """
    # Handle GET request - show login form
    if request.method == 'GET':
        # Use Flask-Login's current_user instead of JWT for redirect
        if current_user.is_authenticated:
            return redirect(url_for('admin.dashboard'))
        return render_template('admin/login.html')
    
    # Handle POST request - process login
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        
        current_app.logger.debug(f"Admin login attempt: username={username}")
        
        # Validate input
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('admin/login.html'), 400
        
        # Try to authenticate admin user
        admin = AdminUser.query.filter_by(username=username).first()
        current_app.logger.debug(f"Found admin: {admin}, admin_id={getattr(admin, 'id', None)}")
        
        if admin and admin.check_password(password):
            # Check if admin is active
            if not admin.is_active:
                flash('Account is inactive', 'error')
                return render_template('admin/login.html'), 401
            
            login_user(admin)  # Flask-Login session
            current_app.logger.info(f"Admin login successful: admin_id={admin.id}")
            
            # Create tokens
            access_token = create_access_token(
                identity=str(admin.id),
                additional_claims={"type": "admin", "is_superuser": admin.is_superuser},
                expires_delta=timedelta(minutes=15)
            )
            refresh_token = create_refresh_token(
                identity=str(admin.id),
                additional_claims={"type": "admin", "is_superuser": admin.is_superuser},
                expires_delta=timedelta(days=30)
            )
            
            # Set tokens in cookies
            response = redirect(url_for('admin.dashboard'))
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            
            # Set CSRF token
            csrf_token = generate_csrf()
            response.set_cookie('csrf_token', csrf_token, httponly=False, secure=False)
            
            return response
        
        flash('Invalid username or password', 'error')
        return render_template('admin/login.html'), 401
        
    except Exception as e:
        current_app.logger.error(f"Admin login error: {str(e)}")
        flash('Login failed. Please try again.', 'error')
        return render_template('admin/login.html'), 500

@admin_bp.route('/dashboard', endpoint='dashboard')
@login_required
def dashboard():
    print(f"[DASHBOARD DEBUG] current_user: {current_user}, is_authenticated: {current_user.is_authenticated}, id: {getattr(current_user, 'id', None)}")
    """Admin dashboard"""
    try:
        # Use Flask-Login's current_user for admin info
        logger.info(f"Dashboard accessed by admin: {current_user.username if hasattr(current_user, 'username') else current_user.id}")
        
        # Get dashboard statistics
        stats = get_dashboard_stats()
        
        # Get recent activity (recent transactions with clients)
        recent_activity = db.session.query(
            Transaction, Client
        ).join(
            Payment, Transaction.payment_id == Payment.id
        ).join(
            Client, Payment.client_id == Client.id
        ).order_by(
            desc(Transaction.created_at)
        ).limit(10).all()
        
        # Get top clients by transaction volume
        top_clients = db.session.query(
            Client,
            func.sum(Transaction.btc_value).label('total_volume'),
            func.count(Transaction.id).label('transaction_count')
        ).join(
            Payment, Client.id == Payment.client_id
        ).join(
            Transaction, Payment.id == Transaction.payment_id
        ).group_by(Client.id).order_by(
            desc('total_volume')
        ).limit(5).all()
        
        # Convert to list of dictionaries for easier template access
        top_clients_data = []
        for client, total_volume, transaction_count in top_clients:
            top_clients_data.append({
                'company_name': client.company_name,
                'email': client.email,
                'total_volume': total_volume or 0,
                'transaction_count': transaction_count or 0
            })
        
        # Get chart data for volume trends (last 7 days)
        chart_data = []
        chart_labels = []
        for i in range(6, -1, -1):  # Last 7 days
            date = datetime.utcnow() - timedelta(days=i)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            daily_volume = db.session.query(
                func.coalesce(func.sum(Transaction.btc_value), 0)
            ).filter(
                Transaction.created_at >= day_start,
                Transaction.created_at < day_end
            ).scalar() or 0
            
            chart_data.append(float(daily_volume))
            chart_labels.append(date.strftime('%b %d'))
        
        return render_template(
            'admin/dashboard.html',
            stats=stats,
            recent_activity=recent_activity,
            top_clients=top_clients_data,
            chart_data=chart_data,
            chart_labels=chart_labels,
            datetime=datetime
        )
    except Exception as e:
        logger.error(f"Error in dashboard route: {str(e)}")
        logger.error(f"Error traceback: {traceback.format_exc()}")
        flash('An error occurred while loading the dashboard', 'error')
        
        # Provide fallback data
        fallback_stats = {
            'total_clients': 0,
            'total_transactions': 0,
            'total_volume': 0,
            'pending_withdrawals': 0,
            'success_rate': 95.5,
            'volume_24h': 0,
            'total_commission': 0,
            'pending_tickets': 0,
            'resolved_tickets': 0,
            'total_tickets': 0,
            'btc_usd_rate': 45000.00,
            'eth_usd_rate': 3000.00,
            'usd_try_rate': 32.50,
            'btc_try_rate': 1500000,
            'volume_change': 0,
            'transactions_change': 0,
            'active_clients_change': 0,
            'success_rate_change': 0,
            'commission_change': 0
        }
        
        return render_template(
            'admin/dashboard.html', 
            stats=fallback_stats, 
            recent_activity=[], 
            top_clients=[], 
            chart_data=[0, 0, 0, 0, 0, 0, 0], 
            chart_labels=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datetime=datetime
        )
        
        # Get chart data (last 30 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Daily transaction volume
        daily_volume = db.session.query(
            func.date(Transaction.created_at).label('date'),
            func.sum(Transaction.btc_value).label('total')
        ).filter(
            Transaction.created_at.between(start_date, end_date)
        ).group_by(
            func.date(Transaction.created_at)
        ).all()
        
        # Format chart data
        chart_labels = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(31)]
        chart_data = [0] * 31
        
        for item in daily_volume:
            if item.date in chart_labels:
                idx = chart_labels.index(item.date)
                chart_data[idx] = float(item.total or 0)
        
        return render_template(
            'admin/dashboard.html',
            stats=stats,
            recent_activity=recent_activity,
            chart_labels=chart_labels,
            chart_data=chart_data,
            current_admin=current_user,
            current_time=datetime.utcnow(),
            pending_withdrawals_count=stats['pending_withdrawals']
        )
        
    except Exception as e:
        logger.error(f"Error in dashboard route: {str(e)}", exc_info=True)
        flash('An error occurred while loading the dashboard', 'error')
        return redirect(url_for('admin.dashboard'))

# Client Management
@admin_bp.route('/clients', methods=['GET'], endpoint='clients')
@admin_bp.route('/clients/', methods=['GET'])
@login_required
def clients():
    """List all clients with pagination and search"""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '')
    client_type = request.args.get('type', '')
    package_filter = request.args.get('package', '')
    
    # Build base query
    query = Client.query
    
    # Apply search filter
    if search:
        query = query.filter(or_(
            Client.name.ilike(f'%{search}%'),
            Client.company_name.ilike(f'%{search}%'),
            Client.email.ilike(f'%{search}%'),
            Client.contact_person.ilike(f'%{search}%'),
            Client.id.like(f'%{search}%')
        ))
    
    # Apply status filter
    if status == 'active':
        query = query.filter(Client.is_active == True)
    elif status == 'inactive':
        query = query.filter(Client.is_active == False)
    elif status == 'verified':
        query = query.filter(Client.is_verified == True)
    elif status == 'pending':
        query = query.filter(Client.is_verified == False)
    
    # Apply client type filter
    if client_type:
        from app.models.client_package import ClientType
        query = query.filter(Client.type == ClientType(client_type))
    
    # Apply package filter
    if package_filter == 'no_package':
        query = query.filter(Client.package_id.is_(None))
    elif package_filter and package_filter.isdigit():
        query = query.filter(Client.package_id == int(package_filter))

    clients = query.order_by(Client.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    commission_stats = None
    try:
        from app.utils.finance import FinanceCalculator
        commission_stats = FinanceCalculator.get_commission_stats()
    except Exception as e:
        logger.error(f"Error getting commission stats: {str(e)}")
        commission_stats = {'total_30d': 0, 'avg_rate': 0}

    total_volume_30d = 0
    try:
        from app.utils.finance import FinanceCalculator
        total_volume_30d = FinanceCalculator.get_total_volume_30d() if hasattr(FinanceCalculator, 'get_total_volume_30d') else 0
    except Exception as e:
        logger.error(f"Error getting total volume: {str(e)}")
        total_volume_30d = 0

    total_30d = commission_stats['total_30d'] if commission_stats and 'total_30d' in commission_stats else 0

    calculator = None
    try:
        from app.utils.finance import FinanceCalculator
        calculator = FinanceCalculator
    except Exception as e:
        logger.error(f"Error importing calculator: {str(e)}")
        calculator = None
    
    # Get last commission refresh time from settings
    last_refresh_time = None
    try:
        from app.models.setting import Setting
        refresh_setting = Setting.query.filter_by(key='commission_last_refresh').first()
        if refresh_setting and refresh_setting.value:
            last_refresh_time = datetime.fromisoformat(refresh_setting.value)
    except Exception as e:
        logging.error(f"Error getting commission refresh time: {str(e)}")
        last_refresh_time = None
    
    # Get available packages for filter dropdown
    available_packages = []
    try:
        from app.models.client_package import ClientPackage
        available_packages = ClientPackage.query.filter_by(status='ACTIVE').order_by(ClientPackage.name).all()
    except Exception:
        available_packages = []

    return render_template(
        'admin/clients.html',
        clients=clients,
        current_admin=current_user,
        commission_stats=commission_stats,
        last_refresh_time=last_refresh_time,
        total_volume_30d=total_volume_30d,
        total_30d=total_30d,
        calculator=calculator,
        available_packages=available_packages
    )

@admin_bp.route('/clients/new', methods=['GET', 'POST'], endpoint='new_client')
@login_required
def new_client():
    """Create a new client"""
    from decimal import Decimal
    from app.models.client_package import ClientType
    current_admin = current_user
    form = ClientForm()
    
    if form.validate_on_submit():
        try:
            client = Client(
                company_name=form.company_name.data,
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                address=form.address.data,
                city=form.city.data,
                country=form.country.data,
                postal_code=form.postal_code.data,
                type=ClientType(form.client_type.data),
                tax_id=form.tax_id.data,
                vat_number=form.vat_number.data,
                registration_number=form.registration_number.data,
                website=form.website.data,
                contact_person=form.contact_person.data,
                contact_email=form.contact_email.data,
                contact_phone=form.contact_phone.data,
                rate_limit=form.rate_limit.data or 100,
                theme_color=form.theme_color.data or '#6c63ff',
                api_key=generate_api_key(),
                is_active=form.is_active.data,
                deposit_commission_rate=Decimal(str(form.deposit_commission_rate.data)) / 100,
                withdrawal_commission_rate=Decimal(str(form.withdrawal_commission_rate.data)) / 100,
                notes=form.notes.data
            )
            db.session.add(client)
            db.session.commit()
            flash('Client created successfully!', 'success')
            return redirect(url_for('admin.clients'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating client: {str(e)}')
            flash('An error occurred while creating the client.', 'error')
    
    return render_template('admin/client_form.html', 
                         form=form, 
                         title='New Client', 
                         current_admin=current_user, 
                         client=None)

@admin_bp.route('/clients/<int:client_id>/edit', methods=['GET', 'POST'], endpoint='edit_client')
@login_required
def edit_client(client_id):
    """Edit an existing client with comprehensive features"""
    from decimal import Decimal
    from app.models.client_package import ClientType
    
    client = Client.query.get_or_404(client_id)
    form = ClientForm(obj=client)
    
    if form.validate_on_submit():
        try:
            # Update basic information
            client.company_name = form.company_name.data
            client.name = form.name.data
            client.email = form.email.data
            client.phone = form.phone.data
            client.address = form.address.data
            client.city = form.city.data
            client.country = form.country.data
            client.postal_code = form.postal_code.data
            client.type = ClientType(form.client_type.data)
            client.tax_id = form.tax_id.data
            client.vat_number = form.vat_number.data
            client.registration_number = form.registration_number.data
            client.website = form.website.data
            client.contact_person = form.contact_person.data
            client.contact_email = form.contact_email.data
            client.contact_phone = form.contact_phone.data
            client.rate_limit = form.rate_limit.data or 100
            client.theme_color = form.theme_color.data or '#6c63ff'
            client.deposit_commission_rate = float(form.deposit_commission_rate.data) / 100
            client.withdrawal_commission_rate = float(form.withdrawal_commission_rate.data) / 100
            client.notes = form.notes.data
            client.webhook_url = form.webhook_url.data
            
            # Update package assignment
            if form.package_id.data and form.package_id.data != 0:
                client.package_id = form.package_id.data
            else:
                client.package_id = None
            
            # Update status
            client.is_active = form.is_active.data
            client.is_verified = form.is_verified.data
            
            # Update balances if changed
            if form.balance.data is not None:
                client.balance = Decimal(str(form.balance.data))
            if form.commission_balance.data is not None:
                client.commission_balance = Decimal(str(form.commission_balance.data))
            
            # Handle password reset
            if form.new_password.data:
                client.set_password(form.new_password.data)
            elif form.auto_generate_password.data:
                new_password = generate_password()
                client.set_password(new_password)
                flash(f'New password generated: {new_password}', 'info')
            
            # Handle API key generation
            if form.auto_generate_api_key.data:
                client.api_key = generate_api_key()
                flash('New API key generated successfully', 'info')
            
            client.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash('Client updated successfully!', 'success')
            return redirect(url_for('admin.view_client', client_id=client.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating client: {str(e)}')
            flash('An error occurred while updating the client.', 'error')
    
    return render_template('admin/client_form.html', 
                         form=form, 
                         title=f'Edit Client: {client.company_name}', 
                         current_admin=current_user, 
                         client=client)

@admin_bp.route('/clients/<int:client_id>/view', methods=['GET'], endpoint='view_client')
@login_required
def view_client(client_id):
    """View client details with comprehensive information"""
    client = Client.query.get_or_404(client_id)
    
    # Get feature information
    from app.models.client_package import Feature
    all_features = Feature.query.order_by(Feature.category, Feature.name).all()
    client_features = {}
    for feature in all_features:
        client_features[feature.id] = client.has_feature(feature.feature_key)
    
    # Get API keys
    api_keys = []
    if hasattr(client, 'api_keys'):
        api_keys = client.api_keys
    
    # Get recent activity/statistics
    try:
        from app.utils.finance import FinanceCalculator
        stats = {
            'total_payments': 0,
            'total_withdrawals': 0,
            'commission_earned': 0,
            'api_usage_30d': 0
        }
        # Add actual stats calculation here
    except Exception as e:
        current_app.logger.error(f"Error calculating client stats: {str(e)}")
        stats = {'total_payments': 0, 'total_withdrawals': 0, 'commission_earned': 0, 'api_usage_30d': 0}
    
    return render_template('admin/client_view.html',
                         client=client,
                         all_features=all_features,
                         client_features=client_features,
                         api_keys=api_keys,
                         stats=stats,
                         current_admin=current_user)

@admin_bp.route('/clients/<int:client_id>/features', methods=['GET', 'POST'], endpoint='manage_client_features')
@login_required
def manage_client_features(client_id):
    """Manage client features independently of packages"""
    from app.forms import ClientFeatureForm
    from app.models.client_package import Feature
    
    client = Client.query.get_or_404(client_id)
    form = ClientFeatureForm(client=client)
    
    if form.validate_on_submit():
        try:
            # Get all features
            all_features = Feature.query.all()
            
            # Update client features override
            new_features = []
            for feature in all_features:
                field_name = f'feature_{feature.id}'
                if hasattr(form, field_name):
                    field_value = getattr(form, field_name).data
                    if field_value:
                        new_features.append(feature.feature_key)
            
            # Update client features override
            client.features_override = new_features
            client.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash('Client features updated successfully!', 'success')
            return redirect(url_for('admin.view_client', client_id=client.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating client features: {str(e)}')
            flash('An error occurred while updating features.', 'error')
    
    # Get all features organized by category
    all_features = Feature.query.order_by(Feature.category, Feature.name).all()
    features_by_category = {}
    for feature in all_features:
        if feature.category not in features_by_category:
            features_by_category[feature.category] = []
        features_by_category[feature.category].append(feature)
    
    return render_template('admin/client_features.html',
                         client=client,
                         form=form,
                         features_by_category=features_by_category,
                         current_admin=current_user)

@admin_bp.route('/clients/<int:client_id>/api-keys/manage', methods=['GET', 'POST'], endpoint='manage_api_keys')
@login_required
def manage_api_keys(client_id):
    """Manage client API keys"""
    from app.forms import ApiKeyManagementForm
    from app.models.api_key import ClientApiKey
    
    client = Client.query.get_or_404(client_id)
    form = ApiKeyManagementForm()
    form.client_id.data = client_id
    
    new_api_key = None
    
    if form.validate_on_submit():
        try:
            # Create new API key
            api_key_obj, api_key = ClientApiKey.create_key(
                client_id=client_id,
                name=form.key_name.data,
                permissions=form.permissions.data,
                rate_limit=form.rate_limit.data,
                expires_days=None,  # Calculate from expires_at if provided
                created_by_admin_id=current_user.id
            )
            
            new_api_key = api_key  # Store for one-time display
            flash('API key created successfully! Make sure to copy it now as it won\'t be shown again.', 'success')
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating API key: {str(e)}')
            flash('An error occurred while creating the API key.', 'error')
    
    # Get existing API keys
    api_keys = ClientApiKey.query.filter_by(client_id=client_id).order_by(ClientApiKey.created_at.desc()).all()
    
    return render_template('admin/client_api_keys.html',
                         client=client,
                         form=form,
                         api_keys=api_keys,
                         new_api_key=new_api_key,
                         current_admin=current_user)

@admin_bp.route('/clients/<int:client_id>/api-keys/<int:key_id>/revoke', methods=['POST'], endpoint='revoke_api_key')
@login_required
def revoke_api_key(client_id, key_id):
    """Revoke a client API key"""
    from app.models.api_key import ClientApiKey
    
    api_key = ClientApiKey.query.filter_by(id=key_id, client_id=client_id).first_or_404()
    
    try:
        api_key.revoke()
        flash(f'API key "{api_key.name}" has been revoked.', 'success')
    except Exception as e:
        current_app.logger.error(f'Error revoking API key: {str(e)}')
        flash('An error occurred while revoking the API key.', 'error')
    
    return redirect(url_for('admin.manage_api_keys', client_id=client_id))

@admin_bp.route('/analytics', methods=['GET'], endpoint='analytics')
@admin_login_required
def analytics():
    """Admin analytics dashboard page"""
    return render_template('admin/analytics.html')

def generate_password(length=12):
    """Generate a secure random password"""
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_api_key():
    """Generate a secure API key"""
    import secrets
    return secrets.token_urlsafe(32)
