import os
import sys
import logging
from datetime import datetime

# Add the root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set the FLASK_APP environment variable
os.environ['FLASK_APP'] = 'wsgi.py'

# Set up Flask environment
os.environ['FLASK_ENV'] = os.getenv('FLASK_ENV', 'development')

# Make sure we're importing from the correct directory
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
log_level = logging.INFO if os.getenv('FLASK_ENV') == 'production' else logging.DEBUG
logging.basicConfig(
    level=log_level,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Initialize the application
from app import create_app, db
from flask_migrate import Migrate

# Create the application instance
application = create_app()

# Initialize Flask-Migrate
migrate = Migrate(application, db)

# Log successful startup
application.logger.info("Application started successfully")

# For local development
if __name__ == "__main__":
    try:
        port = int(os.getenv("PORT", 5000))
        application.logger.info(f"Starting development server on http://0.0.0.0:{port}")
        application.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        application.logger.error(f"Error starting server: {str(e)}")
        raise
