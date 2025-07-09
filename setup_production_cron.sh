#!/bin/bash

# Production Cron Setup for Monthly Usage Reset
# This script sets up the necessary cron jobs for automatic monthly usage reset
# and monitoring for flat-rate clients.

set -e

# Configuration
FLASK_APP_DIR="/path/to/your/cpgateway"  # Update this path
FLASK_ENV="production"
PYTHON_PATH="/path/to/your/venv/bin/python"  # Update this path
LOG_DIR="/var/log/cpgateway"
USER="cpgateway"  # Update this user

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔧 Setting up CPGateway Production Cron Jobs${NC}"
echo "=============================================="

# Create log directory
echo "📁 Creating log directory..."
sudo mkdir -p $LOG_DIR
sudo chown $USER:$USER $LOG_DIR
sudo chmod 755 $LOG_DIR

# Create cron jobs file
CRON_FILE="/tmp/cpgateway_cron"

cat > $CRON_FILE << 'EOF'
# CPGateway Production Cron Jobs
# Monthly usage reset and monitoring for flat-rate clients

# Monthly Usage Reset - Run on 1st of each month at 2:00 AM
0 2 1 * * cd /path/to/your/cpgateway && /path/to/your/venv/bin/python -m flask reset-monthly-usage >> /var/log/cpgateway/monthly_reset.log 2>&1

# Daily Margin Check - Run every day at 8:00 AM
0 8 * * * cd /path/to/your/cpgateway && /path/to/your/venv/bin/python -c "
import sys, os
sys.path.append('.')
from app import create_app
from app.tasks.reset_usage import check_margin_violations
app = create_app()
with app.app_context():
    result = check_margin_violations.delay()
    print(f'Margin check queued: {result.id}')
" >> /var/log/cpgateway/margin_check.log 2>&1

# Weekly Usage Report - Run every Monday at 9:00 AM  
0 9 * * 1 cd /path/to/your/cpgateway && /path/to/your/venv/bin/python -c "
import sys, os
sys.path.append('.')
from app import create_app
from app.tasks.reset_usage import generate_weekly_usage_report
app = create_app()
with app.app_context():
    result = generate_weekly_usage_report.delay()
    print(f'Weekly report queued: {result.id}')
" >> /var/log/cpgateway/weekly_report.log 2>&1

# Database Backup - Run every day at 3:00 AM
0 3 * * * cd /path/to/your/cpgateway && /path/to/your/venv/bin/python -c "
import subprocess, datetime
backup_name = f'cpgateway_backup_{datetime.datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.sql'
subprocess.run(['pg_dump', 'cpgateway_production', '-f', f'/var/backups/{backup_name}'])
print(f'Backup created: {backup_name}')
" >> /var/log/cpgateway/backup.log 2>&1

# Log Rotation - Run daily at 4:00 AM
0 4 * * * find /var/log/cpgateway -name "*.log" -size +100M -exec logrotate -f {} \; >> /var/log/cpgateway/logrotate.log 2>&1

EOF

# Replace placeholders in cron file
sed -i "s|/path/to/your/cpgateway|$FLASK_APP_DIR|g" $CRON_FILE
sed -i "s|/path/to/your/venv/bin/python|$PYTHON_PATH|g" $CRON_FILE

echo "📅 Installing cron jobs for user: $USER"
sudo -u $USER crontab $CRON_FILE

# Clean up
rm $CRON_FILE

echo -e "${GREEN}✅ Cron jobs installed successfully!${NC}"
echo ""
echo "📋 Installed jobs:"
echo "  • Monthly usage reset: 1st of each month at 2:00 AM"
echo "  • Daily margin check: Every day at 8:00 AM"
echo "  • Weekly usage report: Every Monday at 9:00 AM"
echo "  • Database backup: Every day at 3:00 AM"
echo "  • Log rotation: Every day at 4:00 AM"
echo ""
echo "📁 Log files location: $LOG_DIR"
echo ""

# Create logrotate configuration
echo "📄 Creating logrotate configuration..."
sudo tee /etc/logrotate.d/cpgateway > /dev/null << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    su $USER $USER
}
EOF

echo -e "${GREEN}✅ Logrotate configuration created${NC}"

# Create systemd service for Celery worker (if using Celery)
echo "🔧 Creating Celery worker service..."
sudo tee /etc/systemd/system/cpgateway-celery.service > /dev/null << EOF
[Unit]
Description=CPGateway Celery Worker
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$FLASK_APP_DIR
Environment=FLASK_ENV=$FLASK_ENV
ExecStart=$PYTHON_PATH -m celery -A app.tasks.reset_usage worker --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for Celery beat (scheduler)
echo "⏰ Creating Celery beat service..."
sudo tee /etc/systemd/system/cpgateway-celery-beat.service > /dev/null << EOF
[Unit]
Description=CPGateway Celery Beat
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$FLASK_APP_DIR
Environment=FLASK_ENV=$FLASK_ENV
ExecStart=$PYTHON_PATH -m celery -A app.tasks.reset_usage beat --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable services
echo "🔄 Enabling Celery services..."
sudo systemctl daemon-reload
sudo systemctl enable cpgateway-celery.service
sudo systemctl enable cpgateway-celery-beat.service

echo -e "${YELLOW}⚠️  Manual steps required:${NC}"
echo "1. Update paths in this script:"
echo "   - FLASK_APP_DIR: $FLASK_APP_DIR"
echo "   - PYTHON_PATH: $PYTHON_PATH"
echo "   - USER: $USER"
echo ""
echo "2. Start Celery services:"
echo "   sudo systemctl start cpgateway-celery"
echo "   sudo systemctl start cpgateway-celery-beat"
echo ""
echo "3. Test the cron jobs:"
echo "   sudo -u $USER crontab -l"
echo ""
echo "4. Test manual usage reset:"
echo "   cd $FLASK_APP_DIR"
echo "   $PYTHON_PATH -m flask reset-monthly-usage --dry-run"
echo ""
echo "5. Monitor log files:"
echo "   tail -f $LOG_DIR/monthly_reset.log"
echo "   tail -f $LOG_DIR/margin_check.log"
echo ""

# Create monitoring script
echo "📊 Creating monitoring script..."
cat > /usr/local/bin/cpgateway-monitor << 'EOF'
#!/bin/bash

# CPGateway Monitoring Script
# Quick status check for cron jobs and services

LOG_DIR="/var/log/cpgateway"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔍 CPGateway System Status${NC}"
echo "=========================="

# Check cron jobs
echo "📅 Cron Jobs:"
if crontab -l | grep -q "cpgateway"; then
    echo -e "  ✅ Cron jobs installed"
    cron_count=$(crontab -l | grep "cpgateway" | wc -l)
    echo -e "  📊 Active jobs: $cron_count"
else
    echo -e "  ❌ No cron jobs found"
fi

# Check Celery services
echo ""
echo "🔧 Celery Services:"
for service in cpgateway-celery cpgateway-celery-beat; do
    if systemctl is-active --quiet $service; then
        echo -e "  ✅ $service: running"
    else
        echo -e "  ❌ $service: stopped"
    fi
done

# Check recent logs
echo ""
echo "📋 Recent Activity:"
if [ -f "$LOG_DIR/monthly_reset.log" ]; then
    last_reset=$(tail -n 1 "$LOG_DIR/monthly_reset.log" 2>/dev/null | head -c 50)
    echo -e "  🔄 Last reset: $last_reset..."
fi

if [ -f "$LOG_DIR/margin_check.log" ]; then
    last_check=$(tail -n 1 "$LOG_DIR/margin_check.log" 2>/dev/null | head -c 50)
    echo -e "  💹 Last margin check: $last_check..."
fi

# Check disk space
echo ""
echo "💾 Disk Usage:"
df -h $LOG_DIR | tail -n 1 | awk '{print "  📁 Logs: " $3 " used, " $4 " available (" $5 " full)"}'

echo ""
echo -e "${GREEN}✅ Status check complete${NC}"
EOF

sudo chmod +x /usr/local/bin/cpgateway-monitor

echo -e "${GREEN}📊 Monitoring script created: /usr/local/bin/cpgateway-monitor${NC}"
echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "Run 'cpgateway-monitor' anytime to check system status."
