
# UptimeRobot Monitoring Configuration for PayCrypt Gateway

## Monitors to Create

### 1. Main Website Health Check
- **Name:** PayCrypt Gateway - Health Check
- **URL:** https://paycrypt.online/health  
- **Type:** HTTP(s)
- **Monitoring Interval:** 5 minutes
- **Timeout:** 30 seconds
- **Expected Status Code:** 200
- **Keyword Monitoring:** "healthy"

### 2. API Endpoint Monitoring
- **Name:** PayCrypt Gateway - API Status
- **URL:** https://paycrypt.online/api/v1/status
- **Type:** HTTP(s)  
- **Monitoring Interval:** 5 minutes
- **Timeout:** 30 seconds
- **Expected Status Code:** 200

### 3. Admin Dashboard Monitoring
- **Name:** PayCrypt Gateway - Admin Access
- **URL:** https://paycrypt.online/your-secret-admin-path
- **Type:** HTTP(s)
- **Monitoring Interval:** 15 minutes
- **Timeout:** 30 seconds
- **Expected Status Code:** 200 or 302

### 4. Database Connectivity Check
- **Name:** PayCrypt Gateway - Database Health
- **URL:** https://paycrypt.online/health/detailed
- **Type:** HTTP(s)
- **Monitoring Interval:** 10 minutes
- **Keyword Monitoring:** "database"

## Alert Contacts
Configure these notification methods:

### Email Alerts
- **Primary:** admin@paycrypt.online
- **Secondary:** alerts@paycrypt.online

### SMS Alerts (for critical issues)
- Phone number for immediate alerts

### Slack Integration
- Webhook URL: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
- Channel: #paycrypt-alerts

### Discord Integration (optional)
- Webhook URL for Discord notifications

## Escalation Rules
1. **First Alert:** Email notification immediately
2. **After 5 minutes down:** SMS + Email
3. **After 15 minutes down:** Call primary contact
4. **After 30 minutes down:** Escalate to entire team

## Maintenance Windows
Configure maintenance windows for:
- Weekly maintenance: Sundays 2:00 AM - 4:00 AM UTC
- Monthly updates: First Saturday 1:00 AM - 3:00 AM UTC

## Custom Status Page
Create a public status page at: https://status.paycrypt.online
- Include all major components
- Historical uptime data
- Incident history
- Subscribe to updates feature

## API Integration Script
Use this script to automate monitor creation:

```bash
curl -X POST "https://api.uptimerobot.com/v2/newMonitor" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "api_key=YOUR_API_KEY" \
  -d "format=json" \
  -d "type=1" \
  -d "url=https://paycrypt.online/health" \
  -d "friendly_name=PayCrypt Gateway Health" \
  -d "interval=300"
```
