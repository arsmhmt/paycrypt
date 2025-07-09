
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
