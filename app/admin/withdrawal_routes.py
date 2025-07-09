"""
Admin Withdrawal Management Routes
Handles both User Withdrawal Requests (B2C) and Client Withdrawal Requests (B2B)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app.models import db, WithdrawalRequest, Client, User
from app.models.withdrawal import WithdrawalStatus, WithdrawalType
from app.decorators import admin_login_required, secure_admin_required
from app.utils.audit import log_audit, log_admin_action, log_security_event
from app.utils.security import rate_limit, AbuseProtection
from app.utils.fraud_detection import analyze_withdrawal_fraud, FraudRiskLevel
from datetime import datetime, timedelta
from sqlalchemy import or_, and_
import logging

logger = logging.getLogger(__name__)

# Get secure admin path from environment or use secure default
import os
ADMIN_SECRET_PATH = os.environ.get('ADMIN_SECRET_PATH', 'admin120724')

# Ensure path starts with /
if not ADMIN_SECRET_PATH.startswith('/'):
    ADMIN_SECRET_PATH = f'/{ADMIN_SECRET_PATH}'

# Create withdrawal blueprint with secure admin path
withdrawal_bp = Blueprint('withdrawal_admin', __name__, url_prefix=f'{ADMIN_SECRET_PATH}/withdrawals')

# User Withdrawal Routes (B2C - end users withdrawing from client platforms)
@withdrawal_bp.route('/users', methods=['GET'])
@secure_admin_required
@rate_limit('admin_withdrawal_list', limit=100, window=3600)  # 100 requests per hour
def user_withdrawal_requests():
    """List all user withdrawal requests (B2C)"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    client_filter = request.args.get('client', '', type=int)
    
    query = WithdrawalRequest.query.filter_by(withdrawal_type=WithdrawalType.USER_REQUEST)
    
    # Apply filters
    if status_filter:
        query = query.filter_by(status=status_filter)
    if client_filter:
        query = query.filter_by(client_id=client_filter)
    
    withdrawals = query.order_by(WithdrawalRequest.created_at.desc())\
                      .paginate(page=page, per_page=20, error_out=False)
    
    # Get clients for filter dropdown
    clients = Client.query.filter_by(is_active=True).all()
    
    # Get statistics
    stats = {
        'total': WithdrawalRequest.query.filter_by(withdrawal_type=WithdrawalType.USER_REQUEST).count(),
        'pending': WithdrawalRequest.query.filter_by(
            withdrawal_type=WithdrawalType.USER_REQUEST, 
            status=WithdrawalStatus.PENDING
        ).count(),
        'approved': WithdrawalRequest.query.filter_by(
            withdrawal_type=WithdrawalType.USER_REQUEST, 
            status=WithdrawalStatus.APPROVED
        ).count(),
        'rejected': WithdrawalRequest.query.filter_by(
            withdrawal_type=WithdrawalType.USER_REQUEST, 
            status=WithdrawalStatus.REJECTED
        ).count(),
    }
    
    return render_template('admin/withdrawals/user_requests.html', 
                         withdrawals=withdrawals,
                         clients=clients,
                         stats=stats,
                         status_filter=status_filter,
                         client_filter=client_filter)

@withdrawal_bp.route('/users/bulk', methods=['GET', 'POST'])
@secure_admin_required
def user_withdrawal_bulk():
    """Bulk approve/reject user withdrawal requests"""
    if request.method == 'POST':
        withdrawal_ids = request.form.getlist('withdrawal_ids')
        action = request.form.get('action')
        
        if not withdrawal_ids or not action:
            flash('Please select withdrawals and an action', 'error')
            return redirect(url_for('withdrawal_admin.user_withdrawal_bulk'))
        
        try:
            withdrawals = WithdrawalRequest.query.filter(
                WithdrawalRequest.id.in_(withdrawal_ids),
                WithdrawalRequest.withdrawal_type == WithdrawalType.USER_REQUEST,
                WithdrawalRequest.status == WithdrawalStatus.PENDING
            ).all()
            
            if action == 'approve':
                for withdrawal in withdrawals:
                    withdrawal.status = WithdrawalStatus.APPROVED
                    withdrawal.approved_at = datetime.utcnow()
                    withdrawal.approved_by = current_user.id
                    
                    # Log the action
                    log_audit('approve', 'WithdrawalRequest', withdrawal.id, 
                             f'User withdrawal approved in bulk by {current_user.username}')
                
                flash(f'Approved {len(withdrawals)} user withdrawal requests', 'success')
                
            elif action == 'reject':
                reason = request.form.get('reason', 'Bulk rejection')
                for withdrawal in withdrawals:
                    withdrawal.status = WithdrawalStatus.REJECTED
                    withdrawal.rejected_at = datetime.utcnow()
                    withdrawal.rejected_by = current_user.id
                    withdrawal.rejection_reason = reason
                    
                    # Log the action
                    log_audit('reject', 'WithdrawalRequest', withdrawal.id, 
                             f'User withdrawal rejected in bulk: {reason}')
                
                flash(f'Rejected {len(withdrawals)} user withdrawal requests', 'success')
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing bulk action: {str(e)}', 'error')
        
        return redirect(url_for('withdrawal_admin.user_withdrawal_requests'))
    
    # GET request - show bulk approval page
    pending_withdrawals = WithdrawalRequest.query.filter_by(
        withdrawal_type=WithdrawalType.USER_REQUEST,
        status=WithdrawalStatus.PENDING
    ).order_by(WithdrawalRequest.created_at.desc()).all()
    
    return render_template('admin/withdrawals/user_bulk.html', 
                         pending_withdrawals=pending_withdrawals)

# Client Withdrawal Routes (B2B - clients withdrawing their balances)
@withdrawal_bp.route('/clients', methods=['GET'])
@secure_admin_required
def client_withdrawal_requests():
    """List all client withdrawal requests (B2B)"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    client_filter = request.args.get('client', '', type=int)
    
    query = WithdrawalRequest.query.filter_by(withdrawal_type=WithdrawalType.CLIENT_BALANCE)
    
    # Apply filters
    if status_filter:
        query = query.filter_by(status=status_filter)
    if client_filter:
        query = query.filter_by(client_id=client_filter)
    
    withdrawals = query.order_by(WithdrawalRequest.created_at.desc())\
                      .paginate(page=page, per_page=20, error_out=False)
    
    # Get clients for filter dropdown
    clients = Client.query.filter_by(is_active=True).all()
    
    # Get statistics
    stats = {
        'total': WithdrawalRequest.query.filter_by(withdrawal_type=WithdrawalType.CLIENT_BALANCE).count(),
        'pending': WithdrawalRequest.query.filter_by(
            withdrawal_type=WithdrawalType.CLIENT_BALANCE, 
            status=WithdrawalStatus.PENDING
        ).count(),
        'approved': WithdrawalRequest.query.filter_by(
            withdrawal_type=WithdrawalType.CLIENT_BALANCE, 
            status=WithdrawalStatus.APPROVED
        ).count(),
        'rejected': WithdrawalRequest.query.filter_by(
            withdrawal_type=WithdrawalType.CLIENT_BALANCE, 
            status=WithdrawalStatus.REJECTED
        ).count(),
    }
    
    return render_template('admin/withdrawals/client_requests.html', 
                         withdrawals=withdrawals,
                         clients=clients,
                         stats=stats,
                         status_filter=status_filter,
                         client_filter=client_filter)

@withdrawal_bp.route('/clients/bulk', methods=['GET', 'POST'])
@secure_admin_required
def client_withdrawal_bulk():
    """Bulk approve/reject client withdrawal requests"""
    if request.method == 'POST':
        withdrawal_ids = request.form.getlist('withdrawal_ids')
        action = request.form.get('action')
        
        if not withdrawal_ids or not action:
            flash('Please select withdrawals and an action', 'error')
            return redirect(url_for('withdrawal_admin.client_withdrawal_bulk'))
        
        try:
            withdrawals = WithdrawalRequest.query.filter(
                WithdrawalRequest.id.in_(withdrawal_ids),
                WithdrawalRequest.withdrawal_type == WithdrawalType.CLIENT_BALANCE,
                WithdrawalRequest.status == WithdrawalStatus.PENDING
            ).all()
            
            if action == 'approve':
                for withdrawal in withdrawals:
                    withdrawal.status = WithdrawalStatus.APPROVED
                    withdrawal.approved_at = datetime.utcnow()
                    withdrawal.approved_by = current_user.id
                    
                    # Log the action
                    log_audit('approve', 'WithdrawalRequest', withdrawal.id, 
                             f'Client withdrawal approved in bulk by {current_user.username}')
                
                flash(f'Approved {len(withdrawals)} client withdrawal requests', 'success')
                
            elif action == 'reject':
                reason = request.form.get('reason', 'Bulk rejection')
                for withdrawal in withdrawals:
                    withdrawal.status = WithdrawalStatus.REJECTED
                    withdrawal.rejected_at = datetime.utcnow()
                    withdrawal.rejected_by = current_user.id
                    withdrawal.rejection_reason = reason
                    
                    # Log the action
                    log_audit('reject', 'WithdrawalRequest', withdrawal.id, 
                             f'Client withdrawal rejected in bulk: {reason}')
                
                flash(f'Rejected {len(withdrawals)} client withdrawal requests', 'success')
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing bulk action: {str(e)}', 'error')
        
        return redirect(url_for('withdrawal_admin.client_withdrawal_requests'))
    
    # GET request - show bulk approval page
    pending_withdrawals = WithdrawalRequest.query.filter_by(
        withdrawal_type=WithdrawalType.CLIENT_BALANCE,
        status=WithdrawalStatus.PENDING
    ).order_by(WithdrawalRequest.created_at.desc()).all()
    
    return render_template('admin/withdrawals/client_bulk.html', 
                         pending_withdrawals=pending_withdrawals)

# Individual Withdrawal Actions
@withdrawal_bp.route('/<int:withdrawal_id>/approve', methods=['POST'])
@secure_admin_required
@rate_limit('admin_withdrawal_approve', limit=50, window=3600)  # 50 approvals per hour
def approve_withdrawal(withdrawal_id):
    """Approve a single withdrawal request with fraud detection"""
    withdrawal = WithdrawalRequest.query.get_or_404(withdrawal_id)
    
    if withdrawal.status != WithdrawalStatus.PENDING:
        flash('This withdrawal has already been processed', 'warning')
        return redirect(request.referrer or url_for('withdrawal_admin.user_withdrawal_requests'))
    
    try:
        # Perform fraud detection analysis
        fraud_alert = analyze_withdrawal_fraud(withdrawal)
        
        # Log fraud analysis results
        log_security_event(
            event_type='withdrawal_approval_attempt',
            details={
                'withdrawal_id': withdrawal_id,
                'admin_id': current_user.id,
                'fraud_risk_level': fraud_alert.risk_level.value,
                'fraud_risk_score': fraud_alert.risk_score,
                'risk_factors': fraud_alert.factors
            },
            severity='medium' if fraud_alert.risk_level in [FraudRiskLevel.HIGH, FraudRiskLevel.CRITICAL] else 'low'
        )
        
        # Check if manual review is required for high-risk withdrawals
        if fraud_alert.risk_level == FraudRiskLevel.CRITICAL:
            flash(f'⚠️ CRITICAL RISK: {fraud_alert.recommended_action}. Manual review required before approval.', 'error')
            return redirect(request.referrer or url_for('withdrawal_admin.user_withdrawal_requests'))
        elif fraud_alert.risk_level == FraudRiskLevel.HIGH:
            flash(f'⚠️ HIGH RISK: {fraud_alert.recommended_action}. Consider additional verification.', 'warning')
        
        withdrawal.status = WithdrawalStatus.APPROVED
        withdrawal.approved_at = datetime.utcnow()
        withdrawal.approved_by = current_user.id
        
        # Enhanced audit logging
        withdrawal_type_name = "user" if withdrawal.withdrawal_type == WithdrawalType.USER_REQUEST else "client"
        log_admin_action(
            action='approve',
            target_type='withdrawal',
            target_id=withdrawal.id,
            description=f'{withdrawal_type_name.title()} withdrawal approved by {current_user.username}',
            new_values={
                'status': 'approved',
                'amount': withdrawal.amount,
                'fraud_risk_level': fraud_alert.risk_level.value,
                'fraud_risk_score': fraud_alert.risk_score
            },
            admin_user=current_user
        )
        
        db.session.commit()
        
        risk_msg = f" (Risk: {fraud_alert.risk_level.value})" if fraud_alert.risk_level != FraudRiskLevel.LOW else ""
        flash(f'Withdrawal approved successfully{risk_msg}', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error approving withdrawal {withdrawal_id}: {e}")
        flash(f'Error approving withdrawal: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('withdrawal_admin.user_withdrawal_requests'))

@withdrawal_bp.route('/<int:withdrawal_id>/reject', methods=['POST'])
@secure_admin_required
@rate_limit('admin_withdrawal_reject', limit=50, window=3600)  # 50 rejections per hour
def reject_withdrawal(withdrawal_id):
    """Reject a single withdrawal request"""
    withdrawal = WithdrawalRequest.query.get_or_404(withdrawal_id)
    
    if withdrawal.status != WithdrawalStatus.PENDING:
        flash('This withdrawal has already been processed', 'warning')
        return redirect(request.referrer or url_for('withdrawal_admin.user_withdrawal_requests'))
    
    try:
        reason = request.form.get('reason', 'No reason provided')
        withdrawal.status = WithdrawalStatus.REJECTED
        withdrawal.rejected_at = datetime.utcnow()
        withdrawal.rejected_by = current_user.id
        withdrawal.rejection_reason = reason
        
        # Log the action
        withdrawal_type_name = "user" if withdrawal.withdrawal_type == WithdrawalType.USER_REQUEST else "client"
        log_audit('reject', 'WithdrawalRequest', withdrawal.id, 
                 f'{withdrawal_type_name.title()} withdrawal rejected: {reason}')
        
        db.session.commit()
        flash('Withdrawal rejected successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error rejecting withdrawal: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('withdrawal_admin.user_withdrawal_requests'))

# History and Reports
@withdrawal_bp.route('/history', methods=['GET'])
@secure_admin_required
def withdrawal_history():
    """Show complete withdrawal history"""
    page = request.args.get('page', 1, type=int)
    withdrawal_type_filter = request.args.get('type', '')
    status_filter = request.args.get('status', '')
    date_range = request.args.get('range', '30')  # days
    
    query = WithdrawalRequest.query
    
    # Apply filters
    if withdrawal_type_filter:
        query = query.filter_by(withdrawal_type=withdrawal_type_filter)
    if status_filter:
        query = query.filter_by(status=status_filter)
    if date_range != 'all':
        days_ago = datetime.utcnow() - timedelta(days=int(date_range))
        query = query.filter(WithdrawalRequest.created_at >= days_ago)
    
    withdrawals = query.order_by(WithdrawalRequest.created_at.desc())\
                      .paginate(page=page, per_page=50, error_out=False)
    
    return render_template('admin/withdrawals/history.html', 
                         withdrawals=withdrawals,
                         withdrawal_type_filter=withdrawal_type_filter,
                         status_filter=status_filter,
                         date_range=date_range)

@withdrawal_bp.route('/reports', methods=['GET'])
@secure_admin_required
def withdrawal_reports():
    """Show withdrawal reports and analytics"""
    # Get date range from query params
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # User withdrawal stats
    user_stats = {
        'total': WithdrawalRequest.query.filter(
            WithdrawalRequest.withdrawal_type == WithdrawalType.USER_REQUEST,
            WithdrawalRequest.created_at >= start_date
        ).count(),
        'approved': WithdrawalRequest.query.filter(
            WithdrawalRequest.withdrawal_type == WithdrawalType.USER_REQUEST,
            WithdrawalRequest.status == WithdrawalStatus.APPROVED,
            WithdrawalRequest.created_at >= start_date
        ).count(),
        'pending': WithdrawalRequest.query.filter(
            WithdrawalRequest.withdrawal_type == WithdrawalType.USER_REQUEST,
            WithdrawalRequest.status == WithdrawalStatus.PENDING,
            WithdrawalRequest.created_at >= start_date
        ).count(),
        'rejected': WithdrawalRequest.query.filter(
            WithdrawalRequest.withdrawal_type == WithdrawalType.USER_REQUEST,
            WithdrawalRequest.status == WithdrawalStatus.REJECTED,
            WithdrawalRequest.created_at >= start_date
        ).count(),
    }
    
    # Client withdrawal stats
    client_stats = {
        'total': WithdrawalRequest.query.filter(
            WithdrawalRequest.withdrawal_type == WithdrawalType.CLIENT_BALANCE,
            WithdrawalRequest.created_at >= start_date
        ).count(),
        'approved': WithdrawalRequest.query.filter(
            WithdrawalRequest.withdrawal_type == WithdrawalType.CLIENT_BALANCE,
            WithdrawalRequest.status == WithdrawalStatus.APPROVED,
            WithdrawalRequest.created_at >= start_date
        ).count(),
        'pending': WithdrawalRequest.query.filter(
            WithdrawalRequest.withdrawal_type == WithdrawalType.CLIENT_BALANCE,
            WithdrawalRequest.status == WithdrawalStatus.PENDING,
            WithdrawalRequest.created_at >= start_date
        ).count(),
        'rejected': WithdrawalRequest.query.filter(
            WithdrawalRequest.withdrawal_type == WithdrawalType.CLIENT_BALANCE,
            WithdrawalRequest.status == WithdrawalStatus.REJECTED,
            WithdrawalRequest.created_at >= start_date
        ).count(),
    }
    
    return render_template('admin/withdrawals/reports.html',
                         user_stats=user_stats,
                         client_stats=client_stats,
                         days=days,
                         start_date=start_date)
