#!/bin/bash

# Exit on error
set -e

# Configuration
PROJECT_ID="your-project-id"  # Replace with your GCP project ID
SERVICE_NAME="cpgateway-service"
REGION="us-central1"

# Authenticate with Google Cloud
echo "🔐 Authenticating with Google Cloud..."
gcloud auth login

echo "🚀 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Build and push the Docker image
echo "🐳 Building and pushing Docker image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME .

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --update-env-vars FLASK_ENV=production,SECRET_KEY=your-secret-key-here,SQLALCHEMY_DATABASE_URI=your-db-uri-here

echo "✅ Deployment complete!"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')
echo "🌐 Service URL: $SERVICE_URL"
