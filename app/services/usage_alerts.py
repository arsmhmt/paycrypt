#!/usr/bin/env python3
"""
Usage Alert Email System
Sends email notifications when clients approach usage limits
"""

from datetime import datetime
from flask import current_app
import click
from app.models.client import Client
from app.models.client_package import ClientPackage
from app.models.usage_alert import UsageAlert
from app.extensions.extensions import db, mail
from flask_mail import Message
import logging

logger = logging.getLogger(__name__)

class UsageAlertService:
    """Service for monitoring client usage and sending alerts"""
    
    ALERT_THRESHOLDS = [80, 90, 95, 100]  # Percentage thresholds
    
    @staticmethod
    def check_all_clients():
        """Check all flat-rate clients for usage alerts"""
        try:
            # Get all active flat-rate clients
            flat_rate_clients = Client.query.join(ClientPackage).filter(
                ClientPackage.client_type == 'FLAT_RATE',
                Client.is_active == True,
                Client.package_id.isnot(None)
            ).all()
            
            alerts_sent = 0
            for client in flat_rate_clients:
                if UsageAlertService.check_client_usage(client):
                    alerts_sent += 1
            
            logger.info(f"Usage alerts checked for {len(flat_rate_clients)} clients, {alerts_sent} alerts sent")
            return alerts_sent
            
        except Exception as e:
            logger.error(f"Error checking client usage alerts: {str(e)}")
            return 0
    
    @staticmethod
    def check_client_usage(client):
        """Check individual client usage and send alerts if needed"""
        try:
            if not client.package or not client.package.max_volume_per_month:
                return False
            
            # Calculate usage percentage
            current_volume = float(client.current_month_volume or 0)
            max_volume = float(client.package.max_volume_per_month)
            usage_percentage = (current_volume / max_volume) * 100
            
            # Check if we should send an alert
            alert_threshold = UsageAlertService.get_alert_threshold(usage_percentage)
            if alert_threshold and not UsageAlertService.was_alert_sent(client, alert_threshold):
                return UsageAlertService.send_usage_alert(client, usage_percentage, alert_threshold)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking usage for client {client.id}: {str(e)}")
            return False
    
    @staticmethod
    def get_alert_threshold(usage_percentage):
        """Determine which alert threshold to send"""
        for threshold in sorted(UsageAlertService.ALERT_THRESHOLDS, reverse=True):
            if usage_percentage >= threshold:
                return threshold
        return None
    
    @staticmethod
    def was_alert_sent(client, threshold):
        """Check if alert was already sent for this threshold this month"""
        return UsageAlert.was_alert_sent(client.id, threshold)
    
    @staticmethod
    def send_usage_alert(client, usage_percentage, threshold):
        """Send usage alert email to client"""
        try:
            # Determine alert type and styling
            if threshold >= 100:
                alert_type = "LIMIT_EXCEEDED"
                alert_color = "#dc3545"  # Red
                alert_icon = "⚠️"
                subject = f"Usage Limit Exceeded - {client.company_name or client.name}"
            elif threshold >= 95:
                alert_type = "CRITICAL"
                alert_color = "#fd7e14"  # Orange
                alert_icon = "🚨"
                subject = f"Critical Usage Alert ({threshold}%) - {client.company_name or client.name}"
            elif threshold >= 90:
                alert_type = "WARNING"
                alert_color = "#ffc107"  # Yellow
                alert_icon = "⚡"
                subject = f"High Usage Warning ({threshold}%) - {client.company_name or client.name}"
            else:
                alert_type = "NOTICE"
                alert_color = "#17a2b8"  # Info blue
                alert_icon = "📊"
                subject = f"Usage Notice ({threshold}%) - {client.company_name or client.name}"
            
            # Calculate remaining volume
            current_volume = float(client.current_month_volume or 0)
            max_volume = float(client.package.max_volume_per_month)
            remaining_volume = max_volume - current_volume
            
            # Generate email content
            html_content = UsageAlertService.generate_email_html(
                client, usage_percentage, threshold, alert_type, 
                alert_color, alert_icon, current_volume, max_volume, remaining_volume
            )
            
            # Send email
            msg = Message(
                subject=subject,
                recipients=[client.email],
                html=html_content,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@paycrypt.online')
            )
            
            if current_app.config.get('MAIL_ENABLED', True):
                mail.send(msg)
                logger.info(f"Usage alert sent to client {client.id} ({client.email}) - {threshold}% threshold")
                
                # Create alert record for tracking
                UsageAlert.create_alert_record(
                    client, threshold, alert_type, usage_percentage, 
                    current_volume, max_volume
                )
                return True
            else:
                logger.info(f"Email disabled - would send usage alert to {client.email}")
                # Still create record even if email is disabled
                UsageAlert.create_alert_record(
                    client, threshold, alert_type, usage_percentage, 
                    current_volume, max_volume
                )
                return True
                
        except Exception as e:
            logger.error(f"Error sending usage alert to client {client.id}: {str(e)}")
            return False
    
    @staticmethod
    def generate_email_html(client, usage_percentage, threshold, alert_type, 
                          alert_color, alert_icon, current_volume, max_volume, remaining_volume):
        """Generate HTML email content for usage alerts"""
        
        # Get upgrade suggestion
        upgrade_suggestion = ""
        if client.package.slug == 'starter_flat_rate':
            upgrade_suggestion = "Consider upgrading to Business ($999/month) for $70,000 monthly volume."
        elif client.package.slug == 'business_flat_rate':
            upgrade_suggestion = "Consider upgrading to Enterprise ($2,000/month) for unlimited volume."
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PayCrypt Usage Alert</title>
    <style>
        body {{ font-family: 'Inter', Arial, sans-serif; margin: 0; padding: 0; background-color: #f8f9fa; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
        .header {{ background: linear-gradient(135deg, #212529 0%, #495057 100%); color: white; padding: 2rem; text-align: center; }}
        .logo {{ max-height: 40px; margin-bottom: 1rem; }}
        .alert-section {{ padding: 2rem; border-left: 5px solid {alert_color}; background: rgba({alert_color.replace('#', '')}, 0.05); }}
        .alert-header {{ color: {alert_color}; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem; }}
        .usage-stats {{ background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0; }}
        .stat-row {{ display: flex; justify-content: space-between; margin: 0.5rem 0; }}
        .progress-bar {{ background: #e9ecef; height: 20px; border-radius: 10px; overflow: hidden; margin: 1rem 0; }}
        .progress-fill {{ background: {alert_color}; height: 100%; transition: width 0.3s ease; }}
        .action-section {{ padding: 2rem; background: #f8f9fa; }}
        .btn {{ display: inline-block; padding: 0.75rem 2rem; background: #FF6B35; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; }}
        .footer {{ padding: 1rem; text-align: center; color: #6c757d; font-size: 0.875rem; }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>{alert_icon} PayCrypt Usage Alert</h1>
            <p>Monitoring your crypto payment gateway usage</p>
        </div>
        
        <!-- Alert Section -->
        <div class="alert-section">
            <div class="alert-header">
                {alert_type.replace('_', ' ').title()}: {usage_percentage:.1f}% of monthly volume used
            </div>
            <p>Hello <strong>{client.company_name or client.name}</strong>,</p>
            <p>Your current usage has reached <strong>{usage_percentage:.1f}%</strong> of your monthly volume limit.</p>
        </div>
        
        <!-- Usage Statistics -->
        <div class="usage-stats">
            <h3>Current Usage Statistics</h3>
            <div class="stat-row">
                <span>Package:</span>
                <strong>{client.package.name}</strong>
            </div>
            <div class="stat-row">
                <span>Current Volume:</span>
                <strong>${current_volume:,.2f}</strong>
            </div>
            <div class="stat-row">
                <span>Monthly Limit:</span>
                <strong>${max_volume:,.2f}</strong>
            </div>
            <div class="stat-row">
                <span>Remaining:</span>
                <strong>${remaining_volume:,.2f}</strong>
            </div>
            
            <div class="progress-bar">
                <div class="progress-fill" style="width: {min(usage_percentage, 100)}%"></div>
            </div>
        </div>
        
        <!-- Action Section -->
        <div class="action-section">
            <h3>Recommended Actions</h3>
            <ul>
                <li>Monitor your transaction volume closely</li>
                <li>Review your usage patterns in the dashboard</li>
                {"<li>" + upgrade_suggestion + "</li>" if upgrade_suggestion else ""}
                <li>Contact support if you need assistance</li>
            </ul>
            
            <p style="text-align: center; margin-top: 2rem;">
                <a href="https://dashboard.paycrypt.online/client/dashboard" class="btn">View Dashboard</a>
            </p>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p>This is an automated notification from PayCrypt.</p>
            <p>© 2025 PayCrypt - Crypto Payment Gateway</p>
        </div>
    </div>
</body>
</html>
"""


# CLI Command for manual usage check
def create_usage_alert_commands(app):
    """Create CLI commands for usage alerts"""
    
    @app.cli.command('check-usage-alerts')
    def check_usage_alerts():
        """Check all clients for usage alerts and send notifications"""
        print("🔍 Checking client usage alerts...")
        alerts_sent = UsageAlertService.check_all_clients()
        print(f"✅ Usage check complete. {alerts_sent} alerts sent.")
    
    @app.cli.command('test-usage-alert')
    @click.option('--client-id', type=int, required=True, help='Client ID to test')
    @click.option('--threshold', type=int, default=80, help='Test threshold percentage')
    def test_usage_alert(client_id, threshold):
        """Test usage alert for a specific client"""
        from app.models.client import Client
        
        client = Client.query.get(client_id)
        if not client:
            print(f"❌ Client {client_id} not found")
            return
        
        if not client.package:
            print(f"❌ Client {client_id} has no package assigned")
            return
        
        print(f"📧 Sending test usage alert to {client.email} ({threshold}% threshold)")
        success = UsageAlertService.send_usage_alert(client, threshold, threshold)
        if success:
            print("✅ Test alert sent successfully")
        else:
            print("❌ Failed to send test alert")
