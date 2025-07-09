from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required
from app.models import Client, Payment, AuditTrail, WebhookLog
from app.extensions import db
from app.decorators import admin_required
import sentry_sdk

admin_tools_bp = Blueprint('admin_tools', __name__, url_prefix='/admin/tools')

@admin_tools_bp.route('/clients')
@login_required
@admin_required
def manage_clients():
    """Manage client accounts"""
    clients = Client.query.all()
    return render_template('admin/tools/clients.html', clients=clients)

@admin_tools_bp.route('/clients/<int:client_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_client(client_id):
    """Toggle client active status"""
    client = Client.query.get_or_404(client_id)
    client.is_active = not client.is_active
    db.session.commit()
    
    flash(f'Client {client.company_name} status updated to {"active" if client.is_active else "inactive"}', 'success')
    return redirect(url_for('admin_tools.manage_clients'))

@admin_tools_bp.route('/webhook-logs')
@login_required
@admin_required
def webhook_logs():
    """View webhook logs"""
    logs = WebhookLog.query.order_by(WebhookLog.created_at.desc()).limit(100).all()
    return render_template('admin/tools/webhook_logs.html', logs=logs)

@admin_tools_bp.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    """View audit logs"""
    logs = AuditTrail.query.order_by(AuditTrail.created_at.desc()).limit(100).all()
    return render_template('admin/tools/audit_logs.html', logs=logs)

@admin_tools_bp.route('/error-monitoring')
@login_required
@admin_required
def error_monitoring():
    """View error monitoring dashboard"""
    # Get recent errors from Sentry
    errors = sentry_sdk.capture_message("Checking error monitoring")
    return render_template('admin/tools/error_monitoring.html', errors=errors)

@admin_tools_bp.route('/payment-gateway')
@login_required
@admin_required
def payment_gateway():
    """Manage payment gateway settings"""
    # Get current gateway settings
    return render_template('admin/tools/payment_gateway.html')
