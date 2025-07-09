import os
import sys
from app import create_app
from app.extensions.extensions import db

def reset_database():
    # Set the FLASK_ENV to development if not set
    if 'FLASK_ENV' not in os.environ:
        os.environ['FLASK_ENV'] = 'development'
    
    # Create the Flask app
    app = create_app()
    
    with app.app_context():
        try:
            # Drop all tables
            print("Dropping all tables...")
            db.drop_all()
            print("All tables dropped.")
            
            # Create all tables
            print("\nCreating database tables...")
            db.create_all()
            print("Database tables created successfully!")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print("\nTables in the database:")
            for table in tables:
                print(f"- {table}")
            
            return 0
            
        except Exception as e:
            print(f"\nError resetting database: {e}")
            import traceback
            traceback.print_exc()
            return 1

if __name__ == "__main__":
    sys.exit(reset_database())
