# CPGateway

A Flask-based payment gateway application.

## Prerequisites

- Python 3.10+
- Google Cloud SDK
- Docker (for local development)
- A Google Cloud Platform account with billing enabled

## Local Development

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run the development server:
   ```bash
   python run.py
   ```

## Deployment to Google Cloud Run

### Prerequisites

1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Authenticate with Google Cloud:
   ```bash
   gcloud auth login
   ```
3. Set your project:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```
4. Enable required services:
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

### Using the deployment script

1. Make the script executable:
   ```bash
   chmod +x deploy.sh
   ```
2. Edit the `deploy.sh` script and replace `your-project-id` with your GCP project ID.
3. Run the deployment script:
   ```bash
   ./deploy.sh
   ```

### Manual Deployment

1. Build and push the container image:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/cpgateway-service .
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy cpgateway-service \
     --image gcr.io/YOUR_PROJECT_ID/cpgateway-service \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --update-env-vars FLASK_ENV=production,SECRET_KEY=your-secret-key-here,SQLALCHEMY_DATABASE_URI=your-db-uri-here
   ```

## Environment Variables

Create a `.env` file based on `.env.example` with the following variables:

```
FLASK_APP=wsgi.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
SQLALCHEMY_DATABASE_URI=sqlite:///app.db
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

## Database

For production, it's recommended to use Cloud SQL. Update the `SQLALCHEMY_DATABASE_URI` to point to your Cloud SQL instance.

## License

This project is licensed under the MIT License.