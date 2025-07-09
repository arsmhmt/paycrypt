#!/bin/bash
# Google Cloud SSL Configuration for PayCrypt Gateway

echo "☁️ Setting up SSL on Google Cloud..."

# Create SSL certificate
gcloud compute ssl-certificates create paycrypt-ssl-cert \
    --domains=paycrypt.online,www.paycrypt.online \
    --global

# Create backend service
gcloud compute backend-services create paycrypt-backend \
    --protocol=HTTP \
    --port-name=http \
    --health-checks=paycrypt-health-check \
    --global

# Add instance group to backend service
gcloud compute backend-services add-backend paycrypt-backend \
    --instance-group=paycrypt-ig \
    --instance-group-zone=us-central1-a \
    --global

# Create URL map
gcloud compute url-maps create paycrypt-map \
    --default-service=paycrypt-backend

# Create HTTPS proxy
gcloud compute target-https-proxies create paycrypt-https-proxy \
    --url-map=paycrypt-map \
    --ssl-certificates=paycrypt-ssl-cert

# Create forwarding rule
gcloud compute forwarding-rules create paycrypt-https-rule \
    --address=paycrypt-ip \
    --global \
    --target-https-proxy=paycrypt-https-proxy \
    --ports=443

# Create HTTP to HTTPS redirect
gcloud compute url-maps create paycrypt-redirect \
    --default-url-redirect-response-code=301 \
    --default-url-redirect-https-redirect

gcloud compute target-http-proxies create paycrypt-http-proxy \
    --url-map=paycrypt-redirect

gcloud compute forwarding-rules create paycrypt-http-rule \
    --address=paycrypt-ip \
    --global \
    --target-http-proxy=paycrypt-http-proxy \
    --ports=80

echo "✅ Google Cloud SSL configured!"
echo "🌐 Your site will be available at: https://paycrypt.online"
echo "⏳ SSL certificate may take 10-60 minutes to provision"
