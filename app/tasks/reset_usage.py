"""
Celery Tasks for Monthly Usage Reset
Automated tasks for resetting client monthly usage counters.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from celery import Celery
from app.extensions import db
from app.models.client import Client
from app.models.client_package import ClientType
from app.utils.notifications import send_admin_notification, send_client_notification


def create_celery_app(app=None):
    """Create Celery app with Flask app context"""
    celery = Celery(
        app.import_name if app else __name__,
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    )
    
    if app:
        celery.conf.update(app.config)
        
        class ContextTask(celery.Task):
            """Make celery tasks work with Flask app context."""
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        
        celery.Task = ContextTask
    
    return celery


# Initialize Celery (will be properly configured in main app)
celery = create_celery_app()


@celery.task(bind=True)
def reset_monthly_usage_task(self, client_id=None, force=False):
    """
    Celery task to reset monthly usage for flat-rate clients.
    
    Args:
        client_id (int, optional): Reset specific client only
        force (bool): Force reset even if already reset this month
    
    Returns:
        dict: Summary of reset operation
    """
    
    try:
        # Build query for flat-rate clients
        query = db.session.query(Client).join(Client.package).filter(
            Client.package.has(client_type=ClientType.FLAT_RATE),
            Client.is_active == True
        )
        
        # Filter by specific client if requested
        if client_id:
            query = query.filter(Client.id == client_id)
        
        # Filter by reset eligibility (unless forced)
        if not force:
            current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(
                db.or_(
                    Client.last_usage_reset.is_(None),
                    Client.last_usage_reset < current_month_start
                )
            )
        
        clients = query.all()
        
        reset_count = 0
        total_volume_reset = Decimal('0.00')
        total_transactions_reset = 0
        errors = []
        
        for client in clients:
            try:
                # Record pre-reset values
                old_volume = client.current_month_volume or Decimal('0.00')
                old_transactions = client.current_month_transactions or 0
                
                # Perform reset
                client.reset_monthly_usage()
                
                reset_count += 1
                total_volume_reset += old_volume
                total_transactions_reset += old_transactions
                
                # Send notification to client if they had significant usage
                if old_volume > 1000 or old_transactions > 100:
                    send_client_usage_reset_notification.delay(client.id, float(old_volume), old_transactions)
                
            except Exception as e:
                error_msg = f"Failed to reset client {client.id} ({client.company_name}): {str(e)}"
                errors.append(error_msg)
                self.retry(countdown=60, max_retries=3)
        
        # Prepare summary
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'clients_processed': len(clients),
            'clients_reset': reset_count,
            'total_volume_reset': float(total_volume_reset),
            'total_transactions_reset': total_transactions_reset,
            'errors': errors,
            'task_id': self.request.id
        }
        
        # Send admin notification with summary
        if reset_count > 0 or errors:
            send_admin_reset_summary.delay(summary)
        
        return summary
        
    except Exception as e:
        # Log the error and retry
        error_msg = f"Monthly usage reset task failed: {str(e)}"
        self.retry(countdown=300, max_retries=3, exc=e)


@celery.task
def send_client_usage_reset_notification(client_id, volume_reset, transactions_reset):
    """
    Send usage reset notification to client.
    
    Args:
        client_id (int): Client ID
        volume_reset (float): Volume amount that was reset
        transactions_reset (int): Transaction count that was reset
    """
    
    try:
        client = Client.query.get(client_id)
        if not client:
            return {'error': f'Client {client_id} not found'}
        
        # Send email notification
        subject = "Monthly Usage Reset - CPGateway"
        message = f"""
        Dear {client.company_name},
        
        Your monthly usage counters have been reset for the new billing period.
        
        Previous Month Summary:
        - Volume Processed: ${volume_reset:,.2f}
        - Transactions: {transactions_reset:,}
        
        Your new month limits are now available:
        - Volume Limit: ${float(client.package.max_volume_per_month or 0):,.2f}
        - Transaction Limit: {client.package.max_transactions_per_month or 'Unlimited'}
        
        View your dashboard: {client.get_dashboard_url()}
        
        Best regards,
        CPGateway Team
        """
        
        send_client_notification(
            client_id=client_id,
            subject=subject,
            message=message,
            notification_type='usage_reset'
        )
        
        return {'success': True, 'client_id': client_id}
        
    except Exception as e:
        return {'error': f'Failed to send notification to client {client_id}: {str(e)}'}


@celery.task
def send_admin_reset_summary(summary):
    """
    Send monthly reset summary to administrators.
    
    Args:
        summary (dict): Reset operation summary
    """
    
    try:
        subject = f"Monthly Usage Reset Summary - {summary['clients_reset']} clients reset"
        
        message = f"""
        Monthly Usage Reset Summary
        ===========================
        
        Timestamp: {summary['timestamp']}
        Task ID: {summary['task_id']}
        
        Results:
        - Clients Processed: {summary['clients_processed']}
        - Clients Reset: {summary['clients_reset']}
        - Total Volume Reset: ${summary['total_volume_reset']:,.2f}
        - Total Transactions Reset: {summary['total_transactions_reset']:,}
        
        """
        
        if summary['errors']:
            message += f"""
        Errors ({len(summary['errors'])}):
        {chr(10).join(f'- {error}' for error in summary['errors'])}
        """
        else:
            message += "✅ No errors occurred during the reset process."
        
        send_admin_notification(
            subject=subject,
            message=message,
            notification_type='system_task',
            priority='normal' if not summary['errors'] else 'high'
        )
        
        return {'success': True}
        
    except Exception as e:
        return {'error': f'Failed to send admin summary: {str(e)}'}


@celery.task
def check_margin_violations():
    """
    Check for clients whose current usage would violate minimum margin requirements.
    Run daily to identify clients approaching dangerous margin levels.
    """
    
    try:
        # Get all active flat-rate clients
        clients = db.session.query(Client).join(Client.package).filter(
            Client.package.has(client_type=ClientType.FLAT_RATE),
            Client.is_active == True,
            Client.package.has(db.and_(
                Client.package.has(min_margin_percent__isnot=None),
                Client.package.has(monthly_price__isnot=None)
            ))
        ).all()
        
        violations = []
        warnings = []
        
        for client in clients:
            margin_status = client.get_margin_status()
            if not margin_status:
                continue
            
            current_margin = margin_status['current_margin']
            min_margin = margin_status['min_margin']
            
            # Critical: Below minimum margin
            if current_margin < min_margin:
                violations.append({
                    'client_id': client.id,
                    'company_name': client.company_name,
                    'current_margin': current_margin,
                    'min_margin': min_margin,
                    'volume_used': margin_status['volume_used'],
                    'volume_limit': margin_status['volume_limit']
                })
            
            # Warning: Within 0.5% of minimum margin
            elif current_margin < (min_margin + 0.5):
                warnings.append({
                    'client_id': client.id,
                    'company_name': client.company_name,
                    'current_margin': current_margin,
                    'min_margin': min_margin,
                    'volume_used': margin_status['volume_used'],
                    'volume_limit': margin_status['volume_limit']
                })
        
        # Send notifications if violations or warnings found
        if violations or warnings:
            send_margin_alert.delay(violations, warnings)
        
        return {
            'violations': len(violations),
            'warnings': len(warnings),
            'total_checked': len(clients)
        }
        
    except Exception as e:
        return {'error': f'Margin check failed: {str(e)}'}


@celery.task
def send_margin_alert(violations, warnings):
    """
    Send margin violation alerts to administrators.
    
    Args:
        violations (list): Clients with margin violations
        warnings (list): Clients with margin warnings
    """
    
    try:
        if violations:
            # Critical alert for violations
            subject = f"🔴 CRITICAL: {len(violations)} Margin Violation(s) Detected"
            
            message = f"""
            CRITICAL MARGIN VIOLATIONS
            ==========================
            
            The following clients have exceeded minimum margin requirements:
            
            """
            
            for v in violations:
                message += f"""
            🔴 {v['company_name']} (ID: {v['client_id']})
               Current Margin: {v['current_margin']:.2f}%
               Minimum Required: {v['min_margin']:.2f}%
               Volume Used: ${v['volume_used']:,.2f} / ${v['volume_limit']:,.2f}
            """
            
            send_admin_notification(
                subject=subject,
                message=message,
                notification_type='margin_violation',
                priority='critical'
            )
        
        if warnings:
            # Warning alert
            subject = f"⚠️  {len(warnings)} Margin Warning(s) - Near Violation"
            
            message = f"""
            MARGIN WARNINGS
            ===============
            
            The following clients are approaching minimum margin limits:
            
            """
            
            for w in warnings:
                message += f"""
            ⚠️  {w['company_name']} (ID: {w['client_id']})
               Current Margin: {w['current_margin']:.2f}%
               Minimum Required: {w['min_margin']:.2f}%
               Volume Used: ${w['volume_used']:,.2f} / ${w['volume_limit']:,.2f}
            """
            
            send_admin_notification(
                subject=subject,
                message=message,
                notification_type='margin_warning',
                priority='high'
            )
        
        return {'success': True}
        
    except Exception as e:
        return {'error': f'Failed to send margin alerts: {str(e)}'}


# Periodic task configuration (add to celery beat schedule)
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Configure periodic tasks for monthly resets and monitoring.
    """
    
    # Monthly usage reset - Run on 1st of each month at 2 AM UTC
    sender.add_periodic_task(
        crontab(minute=0, hour=2, day_of_month=1),
        reset_monthly_usage_task.s(),
        name='monthly-usage-reset'
    )
    
    # Daily margin check - Run every day at 8 AM UTC
    sender.add_periodic_task(
        crontab(minute=0, hour=8),
        check_margin_violations.s(),
        name='daily-margin-check'
    )
    
    # Weekly usage summary - Run every Monday at 9 AM UTC
    sender.add_periodic_task(
        crontab(minute=0, hour=9, day_of_week=1),
        generate_weekly_usage_report.s(),
        name='weekly-usage-report'
    )


@celery.task
def generate_weekly_usage_report():
    """Generate weekly usage report for all flat-rate clients"""
    
    try:
        clients = db.session.query(Client).join(Client.package).filter(
            Client.package.has(client_type=ClientType.FLAT_RATE),
            Client.is_active == True
        ).all()
        
        report_data = []
        for client in clients:
            volume_percent = client.get_volume_utilization_percent()
            tx_percent = client.get_transaction_utilization_percent()
            margin_status = client.get_margin_status()
            
            report_data.append({
                'client_id': client.id,
                'company_name': client.company_name,
                'package_name': client.package.name,
                'volume_used': float(client.current_month_volume or 0),
                'volume_percent': volume_percent,
                'transactions_used': client.current_month_transactions or 0,
                'transaction_percent': tx_percent,
                'margin_status': margin_status
            })
        
        # Send report to administrators
        send_weekly_usage_report.delay(report_data)
        
        return {'clients_reported': len(report_data)}
        
    except Exception as e:
        return {'error': f'Weekly report generation failed: {str(e)}'}


@celery.task  
def send_weekly_usage_report(report_data):
    """Send weekly usage report to administrators"""
    
    try:
        subject = f"Weekly Usage Report - {len(report_data)} Flat-Rate Clients"
        
        message = """
        Weekly Flat-Rate Client Usage Report
        ===================================
        
        """
        
        # Sort by volume utilization percentage (highest first)
        sorted_data = sorted(report_data, key=lambda x: x['volume_percent'], reverse=True)
        
        for client in sorted_data:
            volume_status = "🔴" if client['volume_percent'] > 90 else "⚠️" if client['volume_percent'] > 75 else "✅"
            margin_ok = "✅" if client['margin_status'] and client['margin_status']['is_acceptable'] else "🔴"
            
            message += f"""
        {volume_status} {client['company_name']} ({client['package_name']})
           Volume: ${client['volume_used']:,.2f} ({client['volume_percent']:.1f}%)
           Transactions: {client['transactions_used']:,} ({client['transaction_percent']:.1f}%)
           Margin: {margin_ok} {client['margin_status']['current_margin']:.2f}% if client['margin_status'] else 'N/A'}
        """
        
        send_admin_notification(
            subject=subject,
            message=message,
            notification_type='weekly_report',
            priority='normal'
        )
        
        return {'success': True}
        
    except Exception as e:
        return {'error': f'Failed to send weekly report: {str(e)}'}


# Additional utility tasks
@celery.task
def manual_client_reset(client_id, admin_user_id, reason="Manual reset by admin"):
    """
    Manually reset a specific client's usage (for admin use).
    
    Args:
        client_id (int): Client to reset
        admin_user_id (int): Admin user performing the reset
        reason (str): Reason for manual reset
    """
    
    try:
        client = Client.query.get(client_id)
        if not client:
            return {'error': f'Client {client_id} not found'}
        
        # Record pre-reset values
        old_volume = float(client.current_month_volume or 0)
        old_transactions = client.current_month_transactions or 0
        
        # Perform reset
        client.reset_monthly_usage()
        
        # Log the manual reset action
        from app.models.audit import AuditTrail, AuditActionType
        AuditTrail.log_action(
            user_id=admin_user_id,
            action_type=AuditActionType.UPDATE.value,
            entity_type='client_usage',
            entity_id=client_id,
            old_value={'volume': old_volume, 'transactions': old_transactions},
            new_value={'volume': 0, 'transactions': 0},
            notes=f"Manual usage reset: {reason}"
        )
        
        return {
            'success': True,
            'client_id': client_id,
            'old_volume': old_volume,
            'old_transactions': old_transactions,
            'reset_timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {'error': f'Manual reset failed: {str(e)}'}
