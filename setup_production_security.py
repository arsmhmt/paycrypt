#!/usr/bin/env python3
"""
HTTPS and Security Configuration for PayCrypt Gateway
Provides multiple options for enabling HTTPS and security headers
"""

import os
import sys
import subprocess

def create_nginx_ssl_config():
    """Generate Nginx SSL configuration"""
    config = """
# PayCrypt Gateway Nginx Configuration with SSL
server {
    listen 80;
    server_name paycrypt.online www.paycrypt.online;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name paycrypt.online www.paycrypt.online;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/paycrypt.online/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/paycrypt.online/privkey.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    
    # HSTS (HTTP Strict Transport Security)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Content Security Policy (adjust based on your needs)
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.coingecko.com wss: https:;" always;
    
    # Application proxy
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint (bypass authentication)
    location /health {
        proxy_pass http://127.0.0.1:8080/health;
        access_log off;
    }
    
    # Static files optimization
    location /static/ {
        proxy_pass http://127.0.0.1:8080/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:8080/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Rate limiting zones
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
}
"""
    
    with open('nginx_ssl_config.conf', 'w') as f:
        f.write(config)
    
    print("✅ Nginx SSL configuration created: nginx_ssl_config.conf")

def create_letsencrypt_script():
    """Generate Let's Encrypt SSL setup script"""
    script = """#!/bin/bash
# Let's Encrypt SSL Certificate Setup for PayCrypt Gateway

echo "🔐 Setting up Let's Encrypt SSL for PayCrypt Gateway..."

# Update system
sudo apt update

# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Stop nginx temporarily
sudo systemctl stop nginx

# Generate SSL certificate
sudo certbot certonly --standalone -d paycrypt.online -d www.paycrypt.online

# Install the nginx configuration
sudo cp nginx_ssl_config.conf /etc/nginx/sites-available/paycrypt
sudo ln -sf /etc/nginx/sites-available/paycrypt /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Setup auto-renewal
sudo crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx"; } | sudo crontab -

echo "✅ SSL certificate installed successfully!"
echo "🔄 Auto-renewal configured"
echo "🌐 Your site is now available at: https://paycrypt.online"

# Test SSL
echo "🧪 Testing SSL configuration..."
curl -I https://paycrypt.online/health
"""
    
    with open('setup_ssl.sh', 'w', encoding='utf-8') as f:
        f.write(script)
    
    os.chmod('setup_ssl.sh', 0o755)
    print("✅ Let's Encrypt setup script created: setup_ssl.sh")

def create_cloudflare_config():
    """Generate Cloudflare configuration guide"""
    config = """
# Cloudflare Configuration for PayCrypt Gateway

## DNS Settings
1. Set A record: paycrypt.online -> YOUR_SERVER_IP
2. Set CNAME record: www.paycrypt.online -> paycrypt.online
3. Enable "Proxied" (orange cloud) for both records

## SSL/TLS Settings
1. Go to SSL/TLS > Overview
2. Set encryption mode to "Full (Strict)"
3. Enable "Always Use HTTPS"
4. Enable "HSTS" with:
   - Max Age: 12 months
   - Include subdomains: Yes
   - Preload: Yes

## Security Settings
1. Go to Security > Settings
2. Set Security Level to "Medium" or "High"
3. Enable "Bot Fight Mode"
4. Configure rate limiting rules:
   - API endpoints: 1000 requests per hour per IP
   - Login endpoints: 10 requests per minute per IP

## Page Rules (in order)
1. paycrypt.online/api/*
   - Security Level: High
   - Cache Level: Bypass

2. paycrypt.online/static/*
   - Cache Level: Cache Everything
   - Edge Cache TTL: 1 year

3. paycrypt.online/*
   - Security Level: Medium
   - SSL: Full

## Firewall Rules
Create rules to:
1. Block known bad IPs
2. Challenge suspicious traffic
3. Allow API access from whitelisted IPs (if needed)

## Origin Rules
Set origin server to use HTTP (since Cloudflare handles SSL):
- Origin IP: YOUR_SERVER_IP
- Origin Port: 8080 (or your app port)

## Additional Security
1. Enable "Browser Integrity Check"
2. Enable "Hotlink Protection"
3. Configure "IP Geolocation" if geographic restrictions needed
4. Set up "Access" rules for admin endpoints if needed

## Environment Variables for Application
Set these in your .env file when using Cloudflare:
FORCE_HTTPS=true
TRUST_PROXY_HEADERS=true
CLOUDFLARE_PROXY=true
"""
    
    with open('cloudflare_setup_guide.md', 'w', encoding='utf-8') as f:
        f.write(config)
    
    print("✅ Cloudflare setup guide created: cloudflare_setup_guide.md")

def create_gcloud_ssl_config():
    """Generate Google Cloud SSL configuration"""
    config = """#!/bin/bash
# Google Cloud SSL Configuration for PayCrypt Gateway

echo "☁️ Setting up SSL on Google Cloud..."

# Create SSL certificate
gcloud compute ssl-certificates create paycrypt-ssl-cert \\
    --domains=paycrypt.online,www.paycrypt.online \\
    --global

# Create backend service
gcloud compute backend-services create paycrypt-backend \\
    --protocol=HTTP \\
    --port-name=http \\
    --health-checks=paycrypt-health-check \\
    --global

# Add instance group to backend service
gcloud compute backend-services add-backend paycrypt-backend \\
    --instance-group=paycrypt-ig \\
    --instance-group-zone=us-central1-a \\
    --global

# Create URL map
gcloud compute url-maps create paycrypt-map \\
    --default-service=paycrypt-backend

# Create HTTPS proxy
gcloud compute target-https-proxies create paycrypt-https-proxy \\
    --url-map=paycrypt-map \\
    --ssl-certificates=paycrypt-ssl-cert

# Create forwarding rule
gcloud compute forwarding-rules create paycrypt-https-rule \\
    --address=paycrypt-ip \\
    --global \\
    --target-https-proxy=paycrypt-https-proxy \\
    --ports=443

# Create HTTP to HTTPS redirect
gcloud compute url-maps create paycrypt-redirect \\
    --default-url-redirect-response-code=301 \\
    --default-url-redirect-https-redirect

gcloud compute target-http-proxies create paycrypt-http-proxy \\
    --url-map=paycrypt-redirect

gcloud compute forwarding-rules create paycrypt-http-rule \\
    --address=paycrypt-ip \\
    --global \\
    --target-http-proxy=paycrypt-http-proxy \\
    --ports=80

echo "✅ Google Cloud SSL configured!"
echo "🌐 Your site will be available at: https://paycrypt.online"
echo "⏳ SSL certificate may take 10-60 minutes to provision"
"""
    
    with open('gcloud_ssl_setup.sh', 'w', encoding='utf-8') as f:
        f.write(config)
    
    os.chmod('gcloud_ssl_setup.sh', 0o755)
    print("✅ Google Cloud SSL script created: gcloud_ssl_setup.sh")

def create_production_env():
    """Create production .env template"""
    env_template = """# PayCrypt Gateway Production Environment
# Copy this to .env and fill in your values

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your-super-secure-secret-key-here-change-this

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/paycrypt_prod
SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost:5432/paycrypt_prod

# Security
JWT_SECRET_KEY=your-jwt-secret-key-change-this
CSRF_SECRET_KEY=your-csrf-secret-key-change-this
HMAC_SECRET_KEY=your-hmac-secret-key-change-this

# SSL/HTTPS
FORCE_HTTPS=true
TRUST_PROXY_HEADERS=true
HSTS_MAX_AGE=31536000

# API Configuration
API_RATE_LIMIT=1000
API_BURST_LIMIT=100

# Email (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# External Services
COINGECKO_API_KEY=your-coingecko-api-key
WEBHOOK_TIMEOUT=30

# Monitoring
SENTRY_DSN=your-sentry-dsn-for-error-tracking
LOG_LEVEL=INFO

# Admin Configuration  
ADMIN_OBFUSCATED_PATH=your-secret-admin-path-change-this
ADMIN_EMAIL=admin@paycrypt.online

# Crypto Wallets (Production addresses)
BTC_WALLET_ADDRESS=your-production-btc-address
ETH_WALLET_ADDRESS=your-production-eth-address
USDT_WALLET_ADDRESS=your-production-usdt-address

# API Keys for external services
BLOCKCHAIN_INFO_API_KEY=your-blockchain-api-key
ETHERSCAN_API_KEY=your-etherscan-api-key

# Redis (for caching and rate limiting)
REDIS_URL=redis://localhost:6379/0

# Session Configuration
SESSION_TIMEOUT=3600
REMEMBER_COOKIE_DURATION=2592000

# File Upload
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=/var/uploads/paycrypt

# Backup Configuration
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30

# Compliance
ENABLE_AUDIT_LOGGING=true
ENABLE_USER_TRACKING=true
DATA_RETENTION_DAYS=2555  # 7 years for financial data
"""
    
    with open('.env.production', 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    print("✅ Production .env template created: .env.production")
    print("⚠️  IMPORTANT: Update all values before deploying!")

def create_uptime_monitoring_config():
    """Create UptimeRobot configuration"""
    config = """
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
curl -X POST "https://api.uptimerobot.com/v2/newMonitor" \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "api_key=YOUR_API_KEY" \\
  -d "format=json" \\
  -d "type=1" \\
  -d "url=https://paycrypt.online/health" \\
  -d "friendly_name=PayCrypt Gateway Health" \\
  -d "interval=300"
```
"""
    
    with open('uptime_monitoring_setup.md', 'w', encoding='utf-8') as f:
        f.write(config)
    
    print("✅ UptimeRobot monitoring config created: uptime_monitoring_setup.md")

def main():
    """Generate all HTTPS and security configuration files"""
    print("🔐 Generating HTTPS and Security Configuration Files...")
    print("=" * 60)
    
    try:
        create_nginx_ssl_config()
        create_letsencrypt_script()
        create_cloudflare_config()
        create_gcloud_ssl_config()
        create_production_env()
        create_uptime_monitoring_config()
        
        print("\n" + "=" * 60)
        print("✅ ALL CONFIGURATION FILES GENERATED!")
        print("=" * 60)
        
        print("\n📋 Next Steps:")
        print("1. Choose your SSL method:")
        print("   • Let's Encrypt: Run ./setup_ssl.sh")
        print("   • Cloudflare: Follow cloudflare_setup_guide.md")
        print("   • Google Cloud: Run ./gcloud_ssl_setup.sh")
        
        print("\n2. Configure production environment:")
        print("   • Copy .env.production to .env")
        print("   • Update all values with your secrets")
        
        print("\n3. Set up monitoring:")
        print("   • Follow uptime_monitoring_setup.md")
        print("   • Configure alerts and status page")
        
        print("\n4. Test your setup:")
        print("   • Run final_qa_test.py against your domain")
        print("   • Check SSL rating at: https://www.ssllabs.com/ssltest/")
        
        print("\n🚀 Ready for production deployment!")
        
    except Exception as e:
        print(f"❌ Error generating configuration files: {str(e)}")
        return False
        
    return True

if __name__ == '__main__':
    main()
