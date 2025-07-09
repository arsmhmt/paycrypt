#!/bin/bash
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
