import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the app directory to the Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(app_dir)

# Import create_app after path is set
from app import create_app

# Create the application instance
app = create_app()

# Register Flask-Migrate commands
@app.cli.command("db")
def db_command():
    """Run database management commands."""
    pass

@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    from app.extensions.extensions import db
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database initialized successfully!")

if __name__ == '__main__':
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", "5000"))
    
    # Initialize database if running directly
    if debug:
        with app.app_context():
            print("\nInitializing database...")
            from app.extensions.extensions import db
            try:
                db.drop_all()
                db.create_all()
                print("Database initialized successfully!")
            except Exception as e:
                print(f"Error initializing database: {e}")
                raise
    
    # Run the application
    app.run(host='0.0.0.0', port=port, debug=debug)
