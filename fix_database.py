import os
import shutil
from app import create_app

def fix_database():
    # Set the FLASK_ENV to development if not set
    if 'FLASK_ENV' not in os.environ:
        os.environ['FLASK_ENV'] = 'development'
    
    # Create the Flask app
    app = create_app()
    
    # Get the current database path from config
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"Current database URI: {db_uri}")
    
    # Check if the database file exists
    db_path = db_uri.replace('sqlite:///', '')
    print(f"Database file path: {db_path}")
    print(f"Database file exists: {os.path.exists(db_path)}")
    
    # Check for the cpgateway.db file
    cpgateway_db = os.path.join(os.path.dirname(db_path), 'cpgateway.db')
    print(f"\nChecking for cpgateway.db at: {cpgateway_db}")
    print(f"cpgateway.db exists: {os.path.exists(cpgateway_db)}")
    
    if os.path.exists(cpgateway_db):
        print("\nFound cpgateway.db. Copying to app.db...")
        try:
            shutil.copy2(cpgateway_db, db_path)
            print(f"Successfully copied {cpgateway_db} to {db_path}")
        except Exception as e:
            print(f"Error copying database file: {e}")
    else:
        print("\ncpgateway.db not found. Creating a new database...")
        try:
            # Create a new database
            from app.extensions.extensions import db
            with app.app_context():
                db.create_all()
                print("Created new database with all tables.")
        except Exception as e:
            print(f"Error creating new database: {e}")

if __name__ == '__main__':
    fix_database()
