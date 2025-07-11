import os
import sys
from dotenv import load_dotenv
from flask_migrate import Migrate

# Load environment variables from .env file
load_dotenv()

# Add the app directory to the Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(app_dir)

# Import create_app after path is set
from app import create_app, db

# Create the application instance
app = create_app()

# Initialize Flask-Migrate
migrate = Migrate(app, db)

@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    with app.app_context():
        # Create tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Run migrations
        from flask_migrate import upgrade
        upgrade()
        print("Database migrations applied successfully!")

if __name__ == '__main__':
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", "5000"))
    
    # Initialize database if running directly
    if debug:
        with app.app_context():
            print("\nInitializing database...")
            try:
                # Create tables if they don't exist
                db.create_all()
                print("Database tables created successfully!")
                
                # Apply any pending migrations
                from flask_migrate import upgrade
                upgrade()
                print("Database migrations applied successfully!")
            except Exception as e:
                print(f"Error initializing database: {e}")
                raise
    
    # Run the application
    app.run(host='0.0.0.0', port=port, debug=debug)
