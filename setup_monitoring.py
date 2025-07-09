#!/usr/bin/env python3
"""
Production Monitoring and Uptime Setup
Sets up monitoring tools and health checks for production deployment
"""

import os
import sys
import requests
import json
from datetime import datetime

def setup_health_check_endpoint():
    """Create a health check endpoint for monitoring"""
    
    health_check_code = """
from flask import Blueprint, jsonify
from datetime import datetime
from app.extensions.extensions import db
from app.models.client import Client

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    \"\"\"Health check endpoint for monitoring\"\"\"
    try:
        # Check database connectivity
        client_count = Client.query.count()
        
        # Check critical services
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'client_count': client_count,
            'version': '1.0.0',
            'environment': os.getenv('FLASK_ENV', 'production')
        }
        
        return jsonify(health_data), 200
        
    except Exception as e:
        error_data = {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e),
            'database': 'disconnected'
        }
        return jsonify(error_data), 503

@health_bp.route('/health/detailed')
def detailed_health_check():
    \"\"\"Detailed health check with more metrics\"\"\"
    try:
        from app.models.client_package import ClientPackage
        from app.services.usage_alerts import UsageAlertService
        
        # Gather detailed metrics
        total_clients = Client.query.count()
        active_clients = Client.query.filter_by(is_active=True).count()
        packages_count = ClientPackage.query.count()
        
        # Check recent activity (if you have transaction logs)
        # recent_transactions = Transaction.query.filter(
        #     Transaction.created_at >= datetime.utcnow() - timedelta(hours=24)
        # ).count()
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': {
                'total_clients': total_clients,
                'active_clients': active_clients,
                'packages_available': packages_count,
                'database_status': 'connected',
                'uptime_check': True
            },
            'environment': os.getenv('FLASK_ENV', 'production'),
            'version': '1.0.0'
        }
        
        return jsonify(health_data), 200
        
    except Exception as e:
        error_data = {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }
        return jsonify(error_data), 503
"""
    
    # Write health check blueprint
    health_dir = "app/blueprints"
    os.makedirs(health_dir, exist_ok=True)
    
    with open(f"{health_dir}/health.py", "w") as f:
        f.write(health_check_code)
    
    print("✅ Health check endpoint created at /health and /health/detailed")
    return True

def create_monitoring_config():
    """Create monitoring configuration files"""
    
    # UptimeRobot configuration (JSON format for API setup)
    uptimerobot_config = {
        "monitors": [
            {
                "friendly_name": "PayCrypt Main Site",
                "url": "https://paycrypt.online/health",
                "type": 1,  # HTTP(s)
                "interval": 300,  # 5 minutes
                "timeout": 30,
                "keyword_type": 1,  # keyword exists
                "keyword_value": "healthy"
            },
            {
                "friendly_name": "PayCrypt Dashboard",
                "url": "https://dashboard.paycrypt.online/health",
                "type": 1,
                "interval": 300,
                "timeout": 30,
                "keyword_type": 1,
                "keyword_value": "healthy"
            }
        ],
        "alert_contacts": [
            {
                "type": 2,  # Email
                "value": "admin@paycrypt.online",
                "friendly_name": "Admin Email"
            }
        ]
    }
    
    # Pingdom configuration
    pingdom_config = {
        "checks": [
            {
                "name": "PayCrypt Health Check",
                "host": "paycrypt.online",
                "type": "http",
                "url": "/health",
                "encryption": True,
                "port": 443,
                "shouldcontain": "healthy",
                "sendnotificationwhendown": 2,
                "notifyagainevery": 5,
                "notifywhenbackup": True
            }
        ]
    }
    
    # Create monitoring directory
    os.makedirs("monitoring", exist_ok=True)
    
    # Write configuration files
    with open("monitoring/uptimerobot_config.json", "w") as f:
        json.dump(uptimerobot_config, f, indent=2)
    
    with open("monitoring/pingdom_config.json", "w") as f:
        json.dump(pingdom_config, f, indent=2)
    
    print("✅ Monitoring configuration files created in monitoring/ directory")
    return True

def create_monitoring_dashboard():
    """Create a simple monitoring dashboard HTML"""
    
    dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PayCrypt System Monitor</title>
    <style>
        body { font-family: 'Inter', Arial, sans-serif; margin: 0; padding: 2rem; background: #f8f9fa; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 2rem; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }
        .status-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .status-healthy { border-left: 5px solid #28a745; }
        .status-warning { border-left: 5px solid #ffc107; }
        .status-error { border-left: 5px solid #dc3545; }
        .metric { display: flex; justify-content: space-between; margin: 0.5rem 0; }
        .refresh-btn { background: #FF6B35; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 5px; cursor: pointer; }
        .timestamp { color: #6c757d; font-size: 0.875rem; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 PayCrypt System Monitor</h1>
            <button class="refresh-btn" onclick="refreshStatus()">Refresh Status</button>
            <p class="timestamp">Last updated: <span id="lastUpdate">Never</span></p>
        </div>
        
        <div class="status-grid">
            <div class="status-card" id="main-health">
                <h3>🌐 Main Application</h3>
                <div class="metric">
                    <span>Status:</span>
                    <span id="main-status">Checking...</span>
                </div>
                <div class="metric">
                    <span>Response Time:</span>
                    <span id="main-response">-</span>
                </div>
                <div class="metric">
                    <span>Database:</span>
                    <span id="main-db">-</span>
                </div>
            </div>
            
            <div class="status-card" id="client-metrics">
                <h3>👥 Client Metrics</h3>
                <div class="metric">
                    <span>Total Clients:</span>
                    <span id="total-clients">-</span>
                </div>
                <div class="metric">
                    <span>Active Clients:</span>
                    <span id="active-clients">-</span>
                </div>
                <div class="metric">
                    <span>Packages:</span>
                    <span id="packages">-</span>
                </div>
            </div>
            
            <div class="status-card" id="usage-alerts">
                <h3>📊 Usage Monitoring</h3>
                <div class="metric">
                    <span>Alerts Today:</span>
                    <span id="alerts-today">-</span>
                </div>
                <div class="metric">
                    <span>High Usage Clients:</span>
                    <span id="high-usage">-</span>
                </div>
                <div class="metric">
                    <span>Last Alert Check:</span>
                    <span id="last-check">-</span>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        async function refreshStatus() {
            document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
            
            try {
                // Check main health
                const response = await fetch('/health/detailed');
                const data = await response.json();
                
                document.getElementById('main-status').textContent = data.status;
                document.getElementById('main-db').textContent = data.metrics?.database_status || 'Unknown';
                document.getElementById('total-clients').textContent = data.metrics?.total_clients || '-';
                document.getElementById('active-clients').textContent = data.metrics?.active_clients || '-';
                document.getElementById('packages').textContent = data.metrics?.packages_available || '-';
                
                // Update card styling
                const mainCard = document.getElementById('main-health');
                mainCard.className = 'status-card ' + (data.status === 'healthy' ? 'status-healthy' : 'status-error');
                
            } catch (error) {
                console.error('Failed to fetch status:', error);
                document.getElementById('main-status').textContent = 'Error';
            }
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshStatus, 30000);
        
        // Initial load
        refreshStatus();
    </script>
</body>
</html>
"""
    
    # Create monitoring directory and dashboard
    os.makedirs("app/templates/monitoring", exist_ok=True)
    
    with open("app/templates/monitoring/dashboard.html", "w") as f:
        f.write(dashboard_html)
    
    print("✅ Monitoring dashboard created at /monitoring/dashboard")
    return True

def create_log_monitoring_script():
    """Create log monitoring and analysis script"""
    
    log_monitor_code = """#!/usr/bin/env python3
\"\"\"
Log Monitoring and Analysis
Monitors application logs for errors and performance issues
\"\"\"

import os
import re
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter

class LogMonitor:
    def __init__(self, log_file="app.log"):
        self.log_file = log_file
        self.error_patterns = [
            r'ERROR',
            r'CRITICAL',
            r'Exception',
            r'500 Internal Server Error',
            r'Database connection failed',
            r'Authentication failed'
        ]
    
    def analyze_logs(self, hours=24):
        \"\"\"Analyze logs from the last N hours\"\"\"
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        analysis = {
            'period_hours': hours,
            'total_lines': 0,
            'errors': [],
            'error_count': 0,
            'warning_count': 0,
            'top_errors': Counter(),
            'status_codes': Counter(),
            'performance_issues': []
        }
        
        if not os.path.exists(self.log_file):
            print(f"Log file {self.log_file} not found")
            return analysis
        
        with open(self.log_file, 'r') as f:
            for line in f:
                analysis['total_lines'] += 1
                
                # Extract timestamp
                timestamp_match = re.search(r'\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}', line)
                if timestamp_match:
                    try:
                        log_time = datetime.strptime(timestamp_match.group(), '%Y-%m-%d %H:%M:%S')
                        if log_time < cutoff_time:
                            continue
                    except ValueError:
                        pass
                
                # Check for errors
                for pattern in self.error_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        analysis['errors'].append(line.strip())
                        analysis['error_count'] += 1
                        analysis['top_errors'][pattern] += 1
                        break
                
                # Check for warnings
                if re.search(r'WARNING', line, re.IGNORECASE):
                    analysis['warning_count'] += 1
                
                # Extract HTTP status codes
                status_match = re.search(r'HTTP/(\\d\\.\\d)" (\\d{3})', line)
                if status_match:
                    status_code = status_match.group(2)
                    analysis['status_codes'][status_code] += 1
                
                # Check for slow requests (>5 seconds)
                time_match = re.search(r'(\\d+\\.\\d+)ms', line)
                if time_match:
                    response_time = float(time_match.group(1))
                    if response_time > 5000:  # 5 seconds
                        analysis['performance_issues'].append({
                            'time': response_time,
                            'line': line.strip()
                        })
        
        return analysis
    
    def generate_report(self, analysis):
        \"\"\"Generate a readable report from analysis\"\"\"
        report = []
        report.append(f"📊 Log Analysis Report - Last {analysis['period_hours']} hours")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        
        # Summary
        report.append(f"📈 Summary:")
        report.append(f"   Total log lines: {analysis['total_lines']:,}")
        report.append(f"   Errors: {analysis['error_count']}")
        report.append(f"   Warnings: {analysis['warning_count']}")
        report.append(f"   Performance issues: {len(analysis['performance_issues'])}")
        report.append("")
        
        # Top errors
        if analysis['top_errors']:
            report.append("🚨 Top Error Types:")
            for error_type, count in analysis['top_errors'].most_common(5):
                report.append(f"   {error_type}: {count}")
            report.append("")
        
        # HTTP status codes
        if analysis['status_codes']:
            report.append("🌐 HTTP Status Codes:")
            for code, count in sorted(analysis['status_codes'].items()):
                report.append(f"   {code}: {count}")
            report.append("")
        
        # Recent errors
        if analysis['errors']:
            report.append("⚠️  Recent Errors (last 10):")
            for error in analysis['errors'][-10:]:
                report.append(f"   {error}")
            report.append("")
        
        # Performance issues
        if analysis['performance_issues']:
            report.append("🐌 Performance Issues (slow requests):")
            for issue in analysis['performance_issues'][-5:]:
                report.append(f"   {issue['time']:.2f}ms: {issue['line'][:100]}...")
            report.append("")
        
        return "\\n".join(report)

def main():
    monitor = LogMonitor()
    analysis = monitor.analyze_logs(24)  # Last 24 hours
    report = monitor.generate_report(analysis)
    
    print(report)
    
    # Save report to file
    with open(f"log_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w") as f:
        f.write(report)
    
    # Alert if too many errors
    if analysis['error_count'] > 50:
        print("🚨 HIGH ERROR COUNT DETECTED! Consider immediate investigation.")
    
    if len(analysis['performance_issues']) > 10:
        print("🐌 PERFORMANCE ISSUES DETECTED! Check for slow queries or bottlenecks.")

if __name__ == '__main__':
    main()
"""
    
    with open("monitoring/log_monitor.py", "w") as f:
        f.write(log_monitor_code)
    
    os.chmod("monitoring/log_monitor.py", 0o755)
    print("✅ Log monitoring script created at monitoring/log_monitor.py")
    return True

def create_cron_monitoring_jobs():
    """Create cron job configurations for monitoring"""
    
    cron_config = """
# PayCrypt Production Monitoring Cron Jobs
# Add these to your crontab with: crontab -e

# Check usage alerts every hour
0 * * * * cd /path/to/cpgateway && /usr/bin/python3 -m flask check-usage-alerts >> /var/log/paycrypt/usage_alerts.log 2>&1

# Generate log analysis report daily at 6 AM
0 6 * * * cd /path/to/cpgateway && /usr/bin/python3 monitoring/log_monitor.py >> /var/log/paycrypt/monitoring.log 2>&1

# Check health endpoint every 5 minutes (basic monitoring)
*/5 * * * * curl -f https://paycrypt.online/health > /dev/null 2>&1 || echo "Health check failed at $(date)" >> /var/log/paycrypt/health_failures.log

# Reset monthly usage (first day of month at 1 AM)
0 1 1 * * cd /path/to/cpgateway && /usr/bin/python3 -m flask reset-monthly-usage >> /var/log/paycrypt/monthly_reset.log 2>&1

# Weekly usage summary report (Mondays at 9 AM)
0 9 * * 1 cd /path/to/cpgateway && /usr/bin/python3 -m flask generate-usage-report >> /var/log/paycrypt/weekly_reports.log 2>&1

# Cleanup old log files (monthly, first Sunday at 2 AM)
0 2 * * 0 [ $(date +\\%d) -le 7 ] && find /var/log/paycrypt/ -name "*.log" -mtime +30 -delete
"""
    
    with open("monitoring/cron_monitoring.txt", "w") as f:
        f.write(cron_config)
    
    print("✅ Cron monitoring jobs configuration created")
    print("   Add to crontab with: crontab -e")
    return True

def main():
    """Set up all monitoring components"""
    print("🔧 Setting up production monitoring and uptime tools...")
    print()
    
    success_count = 0
    
    # Setup components
    components = [
        ("Health Check Endpoints", setup_health_check_endpoint),
        ("Monitoring Config Files", create_monitoring_config),
        ("Monitoring Dashboard", create_monitoring_dashboard),
        ("Log Monitoring Script", create_log_monitoring_script),
        ("Cron Monitoring Jobs", create_cron_monitoring_jobs)
    ]
    
    for name, func in components:
        try:
            print(f"Setting up {name}...")
            if func():
                success_count += 1
                print(f"✅ {name} setup complete")
            else:
                print(f"❌ {name} setup failed")
        except Exception as e:
            print(f"❌ Error setting up {name}: {e}")
        print()
    
    # Summary
    print("=" * 60)
    print(f"📊 Setup Summary: {success_count}/{len(components)} components successful")
    print()
    
    if success_count == len(components):
        print("🎉 All monitoring components set up successfully!")
        print()
        print("Next steps:")
        print("1. Register health endpoint in your Flask app")
        print("2. Set up UptimeRobot or Pingdom using the config files")
        print("3. Add cron jobs to your production server")
        print("4. Configure log rotation for monitoring logs")
        print("5. Test the monitoring dashboard at /monitoring/dashboard")
    else:
        print("⚠️  Some components failed to set up. Check the errors above.")

if __name__ == '__main__':
    main()
