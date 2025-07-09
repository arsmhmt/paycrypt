from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort, current_app
from flask_login import current_user
from app.models import Client, db, ClientDocument, ClientNotificationPreference, Payment, WithdrawalRequest, AuditTrail, User, AdminUser
from app.models.client_package import ClientPackage, PackageStatus
from app.models.withdrawal import WithdrawalStatus
from app.forms import ClientForm
from app.decorators import admin_required, admin_login_required
from app.utils.finance import FinanceCalculator, calculator
from app.utils.security import rate_limit, AbuseProtection
from app.utils.audit import log_admin_action, log_security_event, log_client_setting_change
from datetime import datetime, timedelta
import secrets
import string
import json
import os

# Create client blueprint with admin prefix
client_bp = Blueprint('client', __name__, url_prefix='/admin/clients')

# Set the template folder to the admin templates
client_bp.template_folder = 'templates/admin'

# Initialize abuse protection
abuse_protection = AbuseProtection()



def generate_api_key(length=32):
    """Generate a secure random API key"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@client_bp.route('', methods=['GET'], endpoint='list')
@admin_login_required
def list_clients():
    """List all clients with pagination and search"""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '').strip()
    status = request.args.get('status', 'all')
    
    # Build base query
    query = Client.query
    
    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Client.company_name.ilike(search_term)) |
            (Client.email.ilike(search_term)) |
            (Client.contact_person.ilike(search_term)) |
            (Client.contact_email.ilike(search_term))
        )
    
    # Apply status filter
    if status == 'active':
        query = query.filter(Client.is_active == True)
    elif status == 'inactive':
        query = query.filter(Client.is_active == False)
    
    # Order and paginate results
    clients = query.order_by(Client.company_name.asc())\
                  .paginate(page=page, per_page=per_page, error_out=False)
    
    # Calculate commission stats
    total_30d = sum(c.get_30d_commission() if hasattr(c, 'get_30d_commission') else 0 for c in clients.items)
    total_volume_30d = sum(c.get_30d_volume() if hasattr(c, 'get_30d_volume') else 0 for c in clients.items)
    avg_rate = sum((c.deposit_commission_rate or 0) + (c.withdrawal_commission_rate or 0) for c in clients.items) / (len(clients.items) * 2) if clients.items else 0
    
    # Get API usage stats (placeholder - implement actual API tracking)
    api_usage = {
        'today': 0,
        'month': 0
    }
    
    # Add calculator to context
    return render_template('admin/clients.html',
                         clients=clients,
                         search=search,
                         status=status,
                         active_page='clients',
                         total_30d=total_30d,
                         total_volume_30d=total_volume_30d,
                         avg_commission_rate=avg_rate,
                         api_usage=api_usage,
                         calculator=calculator)

@client_bp.route('/commission-settings', methods=['GET'], endpoint='commission_settings')
@admin_login_required
def commission_settings():
    """Manage global commission settings"""
    # Query all clients to show current commission rates
    clients = Client.query.all()
    
    # Calculate average commission rates
    total_deposit_rate = sum(c.deposit_commission_rate or 0 for c in clients)
    total_withdrawal_rate = sum(c.withdrawal_commission_rate or 0 for c in clients)
    avg_deposit_rate = total_deposit_rate / len(clients) if clients else 0
    avg_withdrawal_rate = total_withdrawal_rate / len(clients) if clients else 0
    
    return render_template('admin/commission_settings.html',
                         clients=clients,
                         avg_deposit_rate=avg_deposit_rate,
                         avg_withdrawal_rate=avg_withdrawal_rate,
                         calculator=calculator)

@client_bp.route('/branding', methods=['GET', 'POST'], endpoint='branding')
@admin_login_required
def branding():
    """Manage client branding settings"""
    if request.method == 'POST':
        # Handle branding updates
        logo = request.files.get('logo')
        favicon = request.files.get('favicon')
        primary_color = request.form.get('primary_color', '#007bff')
        secondary_color = request.form.get('secondary_color', '#6c757d')
        font_family = request.form.get('font_family', 'Arial')
        
        # Save files if provided
        if logo:
            logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'logo.png')
            logo.save(logo_path)
        if favicon:
            favicon_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'favicon.ico')
            favicon.save(favicon_path)
            
        # Update branding settings in config
        current_app.config['BRANDING'] = {
            'primary_color': primary_color,
            'secondary_color': secondary_color,
            'font_family': font_family
        }
        
        flash('Branding settings updated successfully!', 'success')
        return redirect(url_for('client.branding'))
    
    # Get current branding settings
    branding = current_app.config.get('BRANDING', {
        'primary_color': '#007bff',
        'secondary_color': '#6c757d',
        'font_family': 'Arial'
    })
    
    return render_template('admin/branding.html',
                         branding=branding,
                         calculator=calculator)

@client_bp.route('/rate-limits', methods=['GET', 'POST'], endpoint='rate_limits')
@admin_login_required
def rate_limits():
    """Manage client rate limits"""
    if request.method == 'POST':
        # Handle rate limit updates
        default_rate_limit = request.form.get('default_rate_limit', type=int)
        max_rate_limit = request.form.get('max_rate_limit', type=int)
        
        # Update rate limits in config
        current_app.config['RATE_LIMITS'] = {
            'default': default_rate_limit,
            'max': max_rate_limit
        }
        
        flash('Rate limits updated successfully!', 'success')
        return redirect(url_for('client.rate_limits'))
    
    # Get current rate limit settings
    rate_limits = current_app.config.get('RATE_LIMITS', {
        'default': 1000,
        'max': 5000
    })
    
    return render_template('admin/rate_limits.html',
                         rate_limits=rate_limits,
                         calculator=calculator)

@client_bp.route('/api-keys', methods=['GET'], endpoint='api_keys')
@admin_login_required
def api_keys():
    """Manage API keys"""
    # Query all clients with their API keys
    clients = Client.query.all()
    
    return render_template('admin/api_keys.html',
                         clients=clients,
                         calculator=calculator)

@client_bp.route('/audit-logs', methods=['GET'], endpoint='audit_logs')
@admin_login_required
def audit_logs():
    """View client audit logs"""
    # Get filter parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    action_type = request.args.get('action_type')
    entity_type = request.args.get('entity_type')
    user_id = request.args.get('user_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query
    query = AuditTrail.query
    
    if action_type:
        query = query.filter(AuditTrail.action_type == action_type)
    if entity_type:
        query = query.filter(AuditTrail.entity_type == entity_type)
    if user_id:
        query = query.filter(AuditTrail.user_id == user_id)
    if start_date:
        query = query.filter(AuditTrail.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(AuditTrail.created_at <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    # Get users for filter dropdown
    users = User.query.all()
    
    # Get audit logs with pagination
    audit_logs = query.order_by(AuditTrail.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/audit_trail.html',
                         audit_logs=audit_logs,
                         users=users,
                         calculator=calculator)
    """Manage client branding settings"""
    if request.method == 'POST':
        # Handle branding updates
        logo = request.files.get('logo')
        favicon = request.files.get('favicon')
        primary_color = request.form.get('primary_color', '#007bff')
        secondary_color = request.form.get('secondary_color', '#6c757d')
        font_family = request.form.get('font_family', 'Arial')
        
        # Save files if provided
        if logo:
            logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'logo.png')
            logo.save(logo_path)
        if favicon:
            favicon_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'favicon.ico')
            favicon.save(favicon_path)
            
        # Update branding settings in config
        current_app.config['BRANDING'] = {
            'primary_color': primary_color,
            'secondary_color': secondary_color,
            'font_family': font_family
        }
        
        flash('Branding settings updated successfully!', 'success')
        return redirect(url_for('client.branding'))
    
    # Get current branding settings
    branding = current_app.config.get('BRANDING', {
        'primary_color': '#007bff',
        'secondary_color': '#6c757d',
        'font_family': 'Arial'
    })
    
    return render_template('admin/branding.html',
                         branding=branding,
                         calculator=calculator)
    """Manage global commission settings"""
    # Query all clients to show current commission rates
    clients = Client.query.all()
    
    # Calculate average commission rates
    total_deposit_rate = sum(c.deposit_commission_rate or 0 for c in clients)
    total_withdrawal_rate = sum(c.withdrawal_commission_rate or 0 for c in clients)
    avg_deposit_rate = total_deposit_rate / len(clients) if clients else 0
    avg_withdrawal_rate = total_withdrawal_rate / len(clients) if clients else 0
    
    return render_template('admin/commission_settings.html',
                         clients=clients,
                         avg_deposit_rate=avg_deposit_rate,
                         avg_withdrawal_rate=avg_withdrawal_rate,
                         calculator=calculator)

@client_bp.route('/new', methods=['GET', 'POST'], endpoint='new_client')
@admin_login_required
@rate_limit(requests=10, window=300)  # 10 client creations per 5 minutes
def new_client():
    """Create a new client"""
    form = ClientForm()
    
    # Set default values for the form
    if request.method == 'GET':
        form.deposit_commission_rate.data = 3.5  # Default 3.5%
        form.withdrawal_commission_rate.data = 1.5  # Default 1.5%
        form.rate_limit.data = 1000  # Default rate limit
        form.is_active.data = True  # Default to active
    
    if form.validate_on_submit():
        try:
            # Create the client
            client = Client(
                company_name=form.company_name.data.strip(),
                email=form.email.data.lower().strip(),
                phone=form.phone.data.strip() if form.phone.data else None,
                contact_person=form.contact_person.data.strip() if form.contact_person.data else None,
                contact_email=form.contact_email.data.lower().strip() if form.contact_email.data else None,
                contact_phone=form.contact_phone.data.strip() if form.contact_phone.data else None,
                website=form.website.data.strip() if form.website.data else None,
                deposit_commission_rate=float(form.deposit_commission_rate.data) / 100,  # Convert percentage to decimal
                withdrawal_commission_rate=float(form.withdrawal_commission_rate.data) / 100,
                api_key=generate_api_key(),
                webhook_url=form.webhook_url.data.strip() if form.webhook_url.data else None,
                rate_limit=form.rate_limit.data,
                is_active=form.is_active.data,
                notes=form.notes.data.strip() if form.notes.data else None,
                created_by=current_user.id
            )
            # Save username and password if provided
            if form.username.data:
                client.username = form.username.data.strip()
            if form.password.data:
                client.set_password(form.password.data)
            db.session.add(client)
            db.session.commit()
            
            # Log admin action
            log_admin_action(
                admin_id=current_user.id,
                action='create_client',
                target_type='client',
                target_id=client.id,
                details=f'Created new client: {client.company_name}',
                new_value={
                    'company_name': client.company_name,
                    'email': client.email,
                    'deposit_commission_rate': client.deposit_commission_rate,
                    'withdrawal_commission_rate': client.withdrawal_commission_rate,
                    'is_active': client.is_active
                }
            )
            
            # Log the action (legacy audit trail)
            log_audit(
                'create', 
                'Client', 
                client.id, 
                f'Created new client: {client.company_name}',
                new_values={
                    'company_name': client.company_name,
                    'email': client.email,
                    'deposit_commission_rate': client.deposit_commission_rate,
                    'withdrawal_commission_rate': client.withdrawal_commission_rate,
                    'is_active': client.is_active
                }
            )
            
            flash(f'Client {client.company_name} created successfully!', 'success')
            return redirect(url_for('client.client_view_detail', client_id=client.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating client: {str(e)}", exc_info=True)
            flash('An error occurred while creating the client. Please try again.', 'error')
    
    # Add calculator to context
    return render_template('admin/client_form.html', 
                         form=form, 
                         title='New Client',
                         active_page='clients',
                         calculator=calculator)

@client_bp.route('/<int:client_id>', endpoint='client_view_detail')
@admin_login_required
def view_client(client_id):
    """View client details and statistics"""
    client = Client.query.get_or_404(client_id)
    
    # Get recent transactions
    recent_payments = Payment.query.filter_by(client_id=client_id)\
                                 .order_by(Payment.created_at.desc())\
                                 .limit(5).all()
    
    recent_withdrawals = WithdrawalRequest.query.filter_by(client_id=client_id)\
                                              .order_by(WithdrawalRequest.created_at.desc())\
                                              .limit(5).all()
    
    # Calculate statistics for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Payment stats
    payment_stats = db.session.query(
        db.func.count(Payment.id).label('count'),
        db.func.sum(Payment.amount).label('total'),
        db.func.sum(Payment.fee).label('fees')
    ).filter(
        Payment.client_id == client_id,
        Payment.status == 'completed',
        Payment.created_at >= thirty_days_ago
    ).first()
    
    # Withdrawal stats
    withdrawal_stats = db.session.query(
        db.func.count(WithdrawalRequest.id).label('count'),
        db.func.sum(WithdrawalRequest.amount).label('total'),
        db.func.sum(WithdrawalRequest.fee).label('fees')
    ).filter(
        WithdrawalRequest.client_id == client_id,
        WithdrawalRequest.status == 'completed',
        WithdrawalRequest.created_at >= thirty_days_ago
    ).first()
    
    # Monthly volume (last 6 months)
    monthly_volume = db.session.query(
        db.func.date_trunc('month', Payment.created_at).label('month'),
        db.func.sum(Payment.amount).label('volume')
    ).filter(
        Payment.client_id == client_id,
        Payment.status == 'completed',
        Payment.created_at >= (datetime.utcnow() - timedelta(days=180))
    ).group_by('month').order_by('month').all()
    
    # Format data for chart
    chart_labels = [(m[0].strftime('%b %Y') if m[0] else '') for m in monthly_volume]
    chart_data = [float(m[1] or 0) for m in monthly_volume]
    
    # Get audit logs for this client
    audit_logs = AuditTrail.query.filter(
        (AuditTrail.model == 'Client') & 
        (AuditTrail.model_id == str(client_id))
    ).order_by(AuditTrail.created_at.desc()).limit(10).all()
    
    # Get financial data using FinanceCalculator
    calculator = FinanceCalculator()
    balance = calculator.calculate_client_balance(client_id)
    deposit_comm, withdrawal_comm, total_comm = calculator.calculate_commission(client_id)
    
    # Get deposit and withdrawal totals
    deposits = db.session.query(db.func.sum(Payment.amount))\
        .filter(Payment.client_id == client_id, Payment.status == 'completed')\
        .scalar() or 0
        
    withdrawals = db.session.query(db.func.sum(WithdrawalRequest.amount))\
        .filter(WithdrawalRequest.client_id == client_id, WithdrawalRequest.status == 'approved')\
        .scalar() or 0
    
    # Get recent commission transactions (last 5)
    recent_commissions = []
    
    # Add recent payments with commissions
    for payment in recent_payments:
        if payment.status == 'completed':
            recent_commissions.append({
                'created_at': payment.created_at,
                'type': 'deposit',
                'amount': payment.amount,
                'commission': payment.amount * client.deposit_commission,
                'status': payment.status
            })
    
    # Add recent withdrawals with commissions
    for withdrawal in recent_withdrawals:
        if withdrawal.status == WithdrawalStatus.APPROVED:
            recent_commissions.append({
                'created_at': withdrawal.created_at,
                'type': 'withdrawal',
                'amount': withdrawal.amount,
                'commission': withdrawal.amount * client.withdrawal_commission,
                'status': withdrawal.status
            })
    
    # Sort by date descending and take top 5
    recent_commissions = sorted(recent_commissions, key=lambda x: x['created_at'], reverse=True)[:5]
    total_commissions = len(recent_commissions)  # This would be the total count in a real implementation
    
    # Calculate client net balance for withdrawals (only for commission-based clients)
    client_net_balance = 0
    total_user_deposits = 0
    total_user_withdrawals = 0 
    total_commission = deposit_comm + withdrawal_comm
    
    if client.package and client.package.client_type.name == 'COMMISSION':
        # Net balance = Total user deposits - Total user withdrawals - Our commission
        total_user_deposits = deposits  # User deposits on client's platform
        total_user_withdrawals = withdrawals  # User withdrawals from client's platform
        client_net_balance = total_user_deposits - total_user_withdrawals - total_commission
    
    # Get withdrawal requests for this client (placeholder - would use real withdrawal model)
    withdrawal_requests = []
    # TODO: Replace with actual withdrawal request query when withdrawal model is ready
    
    # Get available packages for change package modal
    available_packages = ClientPackage.query.filter_by(status=PackageStatus.ACTIVE).order_by(ClientPackage.sort_order, ClientPackage.name).all()
    
    return render_template('admin/clients/view.html', 
                         client=client, 
                         recent_payments=recent_payments, 
                         recent_withdrawals=recent_withdrawals,
                         payment_stats=payment_stats,
                         withdrawal_stats=withdrawal_stats,
                         chart_labels=json.dumps(chart_labels),
                         chart_data=json.dumps(chart_data),
                         audit_logs=audit_logs,
                         balance=balance,
                         deposits=deposits,
                         withdrawals=withdrawals,
                         deposit_comm=deposit_comm,
                         withdrawal_comm=withdrawal_comm,
                         total_comm=total_comm,
                         recent_commissions=recent_commissions,
                         total_commissions=total_commissions,
                         # New withdrawal-related variables
                         client_net_balance=client_net_balance,
                         total_user_deposits=total_user_deposits,
                         total_user_withdrawals=total_user_withdrawals,
                         total_commission=total_commission,
                         withdrawal_requests=withdrawal_requests,
                         # Package management
                         available_packages=available_packages,
                         active_page='clients')

@client_bp.route('/<int:client_id>/edit', methods=['POST'], endpoint='edit_client')
@admin_login_required
@rate_limit(requests=20, window=300)  # 20 client edits per 5 minutes
def edit_client(client_id):
    """Edit an existing client"""
    client = Client.query.get_or_404(client_id)
    form = ClientForm(obj=client)
    
    if form.validate_on_submit():
        try:
            # Store old values for audit log
            old_values = {
                'company_name': client.company_name,
                'email': client.email,
                'phone': client.phone,
                'contact_person': client.contact_person,
                'contact_email': client.contact_email,
                'contact_phone': client.contact_phone,
                'website': client.website,
                'deposit_commission_rate': client.deposit_commission_rate,
                'withdrawal_commission_rate': client.withdrawal_commission_rate,
                'webhook_url': client.webhook_url,
                'rate_limit': client.rate_limit,
                'is_active': client.is_active,
                'notes': client.notes
            }
            
            # Update client with form data
            client.company_name = form.company_name.data.strip()
            client.email = form.email.data.lower().strip()
            client.phone = form.phone.data.strip() if form.phone.data else None
            client.contact_person = form.contact_person.data.strip() if form.contact_person.data else None
            client.contact_email = form.contact_email.data.lower().strip() if form.contact_email.data else None
            client.contact_phone = form.contact_phone.data.strip() if form.contact_phone.data else None
            client.website = form.website.data.strip() if form.website.data else None
            client.deposit_commission_rate = float(form.deposit_commission_rate.data) / 100
            client.withdrawal_commission_rate = float(form.withdrawal_commission_rate.data) / 100
            client.webhook_url = form.webhook_url.data.strip() if form.webhook_url.data else None
            client.rate_limit = form.rate_limit.data
            client.is_active = form.is_active.data
            client.notes = form.notes.data.strip() if form.notes.data else None
            client.updated_at = datetime.utcnow()
            client.updated_by = current_user.id

            # Password reset logic
            import secrets, string
            if form.auto_generate_password.data:
                new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
                client.set_password(new_password)
                flash(f'New password generated: {new_password}', 'info')
            elif form.new_password.data:
                client.set_password(form.new_password.data)
                flash('Client password has been updated.', 'info')

            db.session.commit()
            
            # Log admin action
            new_values = {
                'company_name': client.company_name,
                'email': client.email,
                'phone': client.phone,
                'contact_person': client.contact_person,
                'contact_email': client.contact_email,
                'contact_phone': client.contact_phone,
                'website': client.website,
                'deposit_commission_rate': client.deposit_commission_rate,
                'withdrawal_commission_rate': client.withdrawal_commission_rate,
                'webhook_url': client.webhook_url,
                'rate_limit': client.rate_limit,
                'is_active': client.is_active,
                'notes': client.notes
            }
            
            log_admin_action(
                admin_id=current_user.id,
                action='edit_client',
                target_type='client',
                target_id=client.id,
                details=f'Updated client: {client.company_name}',
                old_value=old_values,
                new_value=new_values
            )
            
            # Log the action (legacy audit trail)
            log_audit(
                'update', 
                'Client', 
                client.id, 
                f'Updated client: {client.company_name}',
                old_values=old_values,
                new_values=new_values
            )
            
            flash('Client updated successfully!', 'success')
            return redirect(url_for('client.client_view_detail', client_id=client.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating client {client_id}: {str(e)}", exc_info=True)
            flash('An error occurred while updating the client. Please try again.', 'error')
    
    # Convert decimal rates to percentages for the form
    if request.method == 'GET':
        form.deposit_commission_rate.data = client.deposit_commission_rate * 100
        form.withdrawal_commission_rate.data = client.withdrawal_commission_rate * 100
    
    return render_template('admin/clients/form.html', 
                         form=form, 
                         client=client, 
                         title=f'Edit {client.company_name}',
                         active_page='clients')

@client_bp.route('/<int:client_id>/update-commission-rates', methods=['POST'], endpoint='update_commission_rates')
@admin_login_required
def update_commission_rates(client_id):
    """Update client's commission rates"""
    client = Client.query.get_or_404(client_id)
    
    try:
        # Get and validate commission rates
        deposit_rate = float(request.form.get('deposit_commission', 0)) / 100  # Convert from percentage to decimal
        withdrawal_rate = float(request.form.get('withdrawal_commission', 0)) / 100
        
        if not (0 <= deposit_rate <= 1 and 0 <= withdrawal_rate <= 1):
            flash('Commission rates must be between 0% and 100%', 'error')
            return redirect(url_for('client.client_view_detail', client_id=client_id))
        
        # Log old values for audit
        old_values = {
            'deposit_commission': float(client.deposit_commission) * 100,
            'withdrawal_commission': float(client.withdrawal_commission) * 100
        }
        
        # Update commission rates
        client.deposit_commission = deposit_rate
        client.withdrawal_commission = withdrawal_rate
        
        db.session.commit()
        
        # Log the change
        log_audit(
            action='update',
            model='Client',
            model_id=client.id,
            description=f'Updated commission rates for {client.company_name}',
            old_values=old_values,
            new_values={
                'deposit_commission': deposit_rate * 100,
                'withdrawal_commission': withdrawal_rate * 100
            }
        )
        
        flash('Commission rates updated successfully', 'success')
        
    except ValueError:
        db.session.rollback()
        flash('Invalid commission rate values', 'error')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error updating commission rates: {str(e)}')
        flash('An error occurred while updating commission rates', 'error')
    
    return redirect(url_for('client.client_view_detail', client_id=client_id, _anchor='finance-tab'))

@client_bp.route('/<int:client_id>/regenerate-api-key', methods=['POST'], endpoint='regenerate_api_key')
@admin_login_required
def regenerate_api_key(client_id):
    """Regenerate a client's API key"""
    client = Client.query.get_or_404(client_id)
    old_key = client.api_key
    
    try:
        # Generate new API key
        new_key = generate_api_key()
        
        # Update client
        client.api_key = new_key
        client.updated_at = datetime.utcnow()
        client.updated_by = current_user.id
        
        # Invalidate any active sessions/tokens for this client
        # This would depend on your authentication system
        
        db.session.commit()
        
        # Log the action (don't log the actual keys)
        log_audit(
            'update', 
            'Client', 
            client.id, 
            'Regenerated API key',
            old_values={'api_key': '***' + (old_key[-4:] if old_key else '')},
            new_values={'api_key': '***' + new_key[-4:]}
        )
        
        flash('API key regenerated successfully! The old key is no longer valid.', 'success')
        return jsonify({
            'success': True,
            'message': 'API key regenerated',
            'api_key': new_key  # In production, you might not want to return this
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error regenerating API key for client {client_id}: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Failed to regenerate API key. Please try again.'
        }), 500

@client_bp.route('/<int:client_id>/toggle-status', methods=['POST'], endpoint='toggle_client_status')
@admin_login_required
def toggle_client_status(client_id):
    """Toggle a client's active status"""
    client = Client.query.get_or_404(client_id)
    old_status = client.is_active
    new_status = not old_status
    
    try:
        # Update client status
        client.is_active = new_status
        client.updated_at = datetime.utcnow()
        client.updated_by = current_user.id
        
        # If deactivating, you might want to revoke active sessions/tokens
        if not new_status:
            # Add any deactivation logic here, e.g., revoke tokens
            pass
            
        db.session.commit()
        
        # Log the action
        log_audit(
            'update', 
            'Client', 
            client.id, 
            f'Changed status to {"active" if new_status else "inactive"}',
            old_values={'is_active': old_status},
            new_values={'is_active': new_status}
        )
        
        flash(f'Client {"activated" if new_status else "deactivated"} successfully!', 'success')
        return jsonify({
            'success': True,
            'message': f'Client {"activated" if new_status else "deactivated"} successfully!',
            'is_active': new_status
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error toggling status for client {client_id}: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Failed to update client status. Please try again.'
        }), 500

@client_bp.route('/<int:client_id>/delete', methods=['POST'], endpoint='delete_client')
@admin_login_required
def delete_client(client_id):
    """Delete a client"""
    client = Client.query.get_or_404(client_id)
    
    try:
        # Log the action
        log_audit(
            'delete', 
            'Client', 
            client.id, 
            f'Deleted client: {client.company_name}',
            old_values={
                'company_name': client.company_name,
                'email': client.email,
                'deposit_commission_rate': client.deposit_commission_rate,
                'withdrawal_commission_rate': client.withdrawal_commission_rate,
                'is_active': client.is_active
            }
        )
        
        db.session.delete(client)
        db.session.commit()
        
        flash(f'Client {client.company_name} deleted successfully!', 'success')
        return jsonify({
            'success': True,
            'message': 'Client deleted successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting client {client_id}: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Failed to delete client. Please try again.'
        }), 500

@client_bp.route('/<int:client_id>/reset-password', methods=['POST'], endpoint='reset_client_password')
@admin_login_required
def reset_client_password(client_id):
    """Reset client password - generates new password if none provided"""
    client = Client.query.get_or_404(client_id)
    
    try:
        new_password = request.form.get('new_password')
        
        # If no password provided, generate one
        if not new_password:
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits + "!@#$%&*"
            new_password = ''.join(secrets.choice(alphabet) for _ in range(12))
        elif len(new_password) < 8:
            message = 'Password must be at least 8 characters long'
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'message': message}), 400
            flash(message, 'error')
            return redirect(url_for('client.client_view_detail', client_id=client_id))
        
        # Set the new password
        client.set_password(new_password)
        db.session.commit()
        
        # Log the action
        log_audit(
            'update', 
            'Client', 
            client.id, 
            f'Password reset for client: {client.company_name}',
            old_values={'password': '[HIDDEN]'},
            new_values={'password': '[RESET]'}
        )
        
        message = f'Password reset successfully for {client.company_name}'
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': True, 'message': message, 'password': new_password})
        
        flash(message, 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error resetting password for client {client_id}: {str(e)}", exc_info=True)
        message = 'An error occurred while resetting the password. Please try again.'
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'message': message}), 500
        flash(message, 'error')
    
    return redirect(url_for('client.client_view_detail', client_id=client_id))

@client_bp.route('/<int:client_id>/generate-password', methods=['POST'], endpoint='generate_client_password')
@admin_login_required
def generate_client_password(client_id):
    """Generate a new random password for client"""
    client = Client.query.get_or_404(client_id)
    
    try:
        # Generate a secure random password
        import secrets
        import string
        
        # Generate 12-character password with mix of characters
        alphabet = string.ascii_letters + string.digits + "!@#$%&*"
        new_password = ''.join(secrets.choice(alphabet) for _ in range(12))
        
        # Set the new password
        client.set_password(new_password)
        db.session.commit()
        
        # Log the action
        log_audit(
            'update', 
            'Client', 
            client.id, 
            f'Password generated for client: {client.company_name}',
            old_values={'password': '[HIDDEN]'},
            new_values={'password': '[GENERATED]'}
        )
        
        message = f'New password generated for {client.company_name}'
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': True, 'message': message, 'password': new_password})
        
        flash(f'{message}: <strong>{new_password}</strong>', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error generating password for client {client_id}: {str(e)}", exc_info=True)
        message = 'An error occurred while generating the password. Please try again.'
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'message': message}), 500
        flash(message, 'error')
    
    return redirect(url_for('client.client_view_detail', client_id=client_id))

@client_bp.route('/<int:client_id>/set-username', methods=['POST'], endpoint='set_client_username')
@admin_login_required
def set_client_username(client_id):
    """Set or update client username"""
    client = Client.query.get_or_404(client_id)
    
    try:
        new_username = request.form.get('username', '').strip()
        
        if not new_username:
            flash('Username cannot be empty', 'error')
            return redirect(url_for('client.client_view_detail', client_id=client_id))
            
        if len(new_username) < 4:
            flash('Username must be at least 4 characters long', 'error')
            return redirect(url_for('client.client_view_detail', client_id=client_id))
        
        # Check if username is already taken
        existing_client = Client.query.filter(
            Client.username == new_username,
            Client.id != client_id
        ).first()
        
        if existing_client:
            flash('Username is already taken. Please choose a different one.', 'error')
            return redirect(url_for('client.client_view_detail', client_id=client_id))
        
        old_username = client.username
        client.username = new_username
        db.session.commit()
        
        # Log the action
        log_audit(
            'update', 
            'Client', 
            client.id, 
            f'Username updated for client: {client.company_name}',
            old_values={'username': old_username},
            new_values={'username': new_username}
        )
        
        flash(f'Username updated successfully for {client.company_name}', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error setting username for client {client_id}: {str(e)}", exc_info=True)
        flash('An error occurred while updating the username. Please try again.', 'error')
    
    return redirect(url_for('client.client_view_detail', client_id=client_id))

# Withdrawal Management Routes

@client_bp.route('/<int:client_id>/change-package', methods=['POST'], endpoint='change_client_package')
@admin_login_required
def change_client_package(client_id):
    """Change client package/status"""
    client = Client.query.get_or_404(client_id)
    
    try:
        package_id = request.form.get('package_id')
        reason = request.form.get('reason', '')
        
        if not package_id:
            flash('Please select a package', 'error')
            return redirect(url_for('client.client_view_detail', client_id=client_id))
        
        old_package = client.package.name if client.package else 'None'
        client.package_id = int(package_id)
        db.session.commit()
        
        # Log the action
        log_audit(
            'update', 
            'Client', 
            client.id, 
            f'Package changed from {old_package} to {client.package.name}. Reason: {reason}',
            old_values={'package': old_package},
            new_values={'package': client.package.name}
        )
        
        flash(f'Package changed successfully for {client.company_name}', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error changing package for client {client_id}: {str(e)}", exc_info=True)
        flash('An error occurred while changing the package. Please try again.', 'error')
    
    return redirect(url_for('client.client_view_detail', client_id=client_id))

@client_bp.route('/<int:client_id>/toggle-status', methods=['POST'], endpoint='toggle_client_status')
@admin_login_required
def toggle_client_status(client_id):
    """Toggle client active status"""
    client = Client.query.get_or_404(client_id)
    
    try:
        new_status = request.json.get('is_active') if request.is_json else request.form.get('is_active') == 'true'
        old_status = client.is_active
        
        client.is_active = new_status
        db.session.commit()
        
        # Log the action
        action = 'activated' if new_status else 'deactivated'
        log_audit(
            'update', 
            'Client', 
            client.id, 
            f'Client {action}',
            old_values={'is_active': old_status},
            new_values={'is_active': new_status}
        )
        
        message = f'Client {action} successfully'
        if request.is_json:
            return jsonify({'success': True, 'message': message})
        
        flash(message, 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error toggling status for client {client_id}: {str(e)}", exc_info=True)
        message = 'An error occurred while updating client status. Please try again.'
        if request.is_json:
            return jsonify({'success': False, 'message': message}), 500
        flash(message, 'error')
    
    return redirect(url_for('client.client_view_detail', client_id=client_id))

@client_bp.route('/<int:client_id>/withdrawals/user', methods=['POST'], endpoint='create_user_withdrawal')
@admin_login_required
def create_user_withdrawal(client_id):
    """Create Type A withdrawal (user withdrawal with commission)"""
    client = Client.query.get_or_404(client_id)
    
    try:
        amount = float(request.form.get('amount', 0))
        commission_rate = float(request.form.get('commission_rate', 0)) / 100
        destination_address = request.form.get('destination_address')
        notes = request.form.get('notes', '')
        
        if amount <= 0:
            flash('Invalid withdrawal amount', 'error')
            return redirect(url_for('client.client_view_detail', client_id=client_id))
        
        if not destination_address:
            flash('Destination address is required', 'error')
            return redirect(url_for('client.client_view_detail', client_id=client_id))
        
        # Calculate commission
        commission_amount = amount * commission_rate
        
        # TODO: Create withdrawal record using proper withdrawal model
        # For now, just log the action
        log_audit(
            'create', 
            'Withdrawal', 
            None, 
            f'Type A withdrawal created: ${amount:.2f} with ${commission_amount:.2f} commission for {client.company_name}',
            old_values={},
            new_values={
                'type': 'user_withdrawal',
                'amount': amount,
                'commission': commission_amount,
                'destination': destination_address,
                'notes': notes
            }
        )
        
        flash(f'User withdrawal request created: ${amount:.2f} (Commission: ${commission_amount:.2f})', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating user withdrawal for client {client_id}: {str(e)}", exc_info=True)
        flash('An error occurred while creating the withdrawal. Please try again.', 'error')
    
    return redirect(url_for('client.client_view_detail', client_id=client_id))

@client_bp.route('/<int:client_id>/withdrawals/net', methods=['POST'], endpoint='create_net_withdrawal')
@admin_login_required
def create_net_withdrawal(client_id):
    """Create Type B withdrawal (client net balance withdrawal)"""
    client = Client.query.get_or_404(client_id)
    
    try:
        amount = float(request.form.get('amount', 0))
        destination_address = request.form.get('destination_address')
        notes = request.form.get('notes', '')
        
        if amount <= 0:
            flash('Invalid withdrawal amount', 'error')
            return redirect(url_for('client.client_view_detail', client_id=client_id))
        
        # TODO: Check client net balance using finance calculator
        # For now, assume balance is sufficient
        
        if not destination_address:
            flash('Destination address is required', 'error')
            return redirect(url_for('client.client_view_detail', client_id=client_id))
        
        # TODO: Deduct amount from client net balance
        # TODO: Create withdrawal record using proper withdrawal model
        
        # For now, just log the action
        log_audit(
            'create', 
            'Withdrawal', 
            None, 
            f'Type B net withdrawal created: ${amount:.2f} for {client.company_name}',
            old_values={},
            new_values={
                'type': 'net_withdrawal',
                'amount': amount,
                'commission': 0,
                'destination': destination_address,
                'notes': notes
            }
        )
        
        flash(f'Net balance withdrawal request created: ${amount:.2f}', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating net withdrawal for client {client_id}: {str(e)}", exc_info=True)
        flash('An error occurred while creating the withdrawal. Please try again.', 'error')
    
    return redirect(url_for('client.client_view_detail', client_id=client_id))

@client_bp.route('/<int:client_id>/withdrawals/<int:withdrawal_id>/approve', methods=['POST'], endpoint='approve_withdrawal')
@admin_login_required
def approve_withdrawal(client_id, withdrawal_id):
    """Approve a withdrawal request"""
    client = Client.query.get_or_404(client_id)
    
    try:
        # TODO: Update withdrawal status using proper withdrawal model
        # For now, just log the action
        log_audit(
            'update', 
            'Withdrawal', 
            withdrawal_id, 
            f'Withdrawal approved for {client.company_name}',
            old_values={'status': 'pending'},
            new_values={'status': 'approved'}
        )
        
        message = 'Withdrawal approved successfully'
        if request.is_json:
            return jsonify({'success': True, 'message': message})
        
        flash(message, 'success')
        
    except Exception as e:
        current_app.logger.error(f"Error approving withdrawal {withdrawal_id}: {str(e)}", exc_info=True)
        message = 'An error occurred while approving the withdrawal'
        if request.is_json:
            return jsonify({'success': False, 'message': message}), 500
        flash(message, 'error')
    
    return redirect(url_for('client.client_view_detail', client_id=client_id))

@client_bp.route('/<int:client_id>/withdrawals/<int:withdrawal_id>/reject', methods=['POST'], endpoint='reject_withdrawal')
@admin_login_required
def reject_withdrawal(client_id, withdrawal_id):
    """Reject a withdrawal request"""
    client = Client.query.get_or_404(client_id)
    
    try:
        reason = request.json.get('reason') if request.is_json else request.form.get('reason', '')
        
        # TODO: Update withdrawal status using proper withdrawal model
        # For now, just log the action
        log_audit(
            'update', 
            'Withdrawal', 
            withdrawal_id, 
            f'Withdrawal rejected for {client.company_name}. Reason: {reason}',
            old_values={'status': 'pending'},
            new_values={'status': 'rejected', 'rejection_reason': reason}
        )
        
        message = 'Withdrawal rejected successfully'
        if request.is_json:
            return jsonify({'success': True, 'message': message})
        
        flash(message, 'success')
        
    except Exception as e:
        current_app.logger.error(f"Error rejecting withdrawal {withdrawal_id}: {str(e)}", exc_info=True)
        message = 'An error occurred while rejecting the withdrawal'
        if request.is_json:
            return jsonify({'success': False, 'message': message}), 500
        flash(message, 'error')
    
    return redirect(url_for('client.client_view_detail', client_id=client_id))

def log_audit(action, model, model_id, description, old_values=None, new_values=None):
    """Helper function to log audit trail"""
    current_app.logger.info(f"AUDIT: {action} {model} {model_id} - {description} - User: {current_user.id if current_user else 'System'} - IP: {request.remote_addr}")
    # TODO: Implement proper audit logging with AuditLog model when available
