import os
import shutil
from datetime import datetime
from app import create_app
from app.extensions.extensions import db
from app.models.user import User
from app.models.client import Client
from werkzeug.security import generate_password_hash

def reset_database():
    # Set the FLASK_ENV to development if not set
    if 'FLASK_ENV' not in os.environ:
        os.environ['FLASK_ENV'] = 'development'
    
    # Backup existing database if it exists
    db_path = os.path.join('instance', 'app.db')
    backup_path = os.path.join('instance', f'app.db.bak.{datetime.now().strftime("%Y%m%d%H%M%S")}')
    
    if os.path.exists(db_path):
        try:
            shutil.copy2(db_path, backup_path)
            print(f"Created backup of existing database at: {backup_path}")
            os.remove(db_path)
            print(f"Removed existing database file: {db_path}")
        except Exception as e:
            print(f"Error backing up/removing existing database: {e}")
            return 1
    
    # Create the Flask app
    app = create_app()
    
    with app.app_context():
        try:
            print("\nCreating database tables...")
            db.create_all()
            print("Database tables created successfully!")
            
            # Create a test user
            print("\nCreating test user...")
            user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('Test123!'),
                is_active=True,
                is_verified=True
            )
            db.session.add(user)
            db.session.flush()  # To get the user ID
            
            # Create a client for the user
            client = Client(
                user_id=user.id,
                company_name='Test Company',
                contact_person='Test User',
                contact_email='test@example.com',
                contact_phone='+1234567890',
                address='123 Test St',
                city='Test City',
                country='Test Country',
                is_active=True
            )
            db.session.add(client)
            db.session.commit()
            
            print("\nTest user created successfully!")
            print(f"Username: testuser")
            print(f"Password: Test123!")
            
            # Verify the database was created
            print(f"\nDatabase created at: {os.path.abspath(db_path)}")
            print(f"File size: {os.path.getsize(db_path) / 1024:.2f} KB")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print("\nTables in the database:")
            for table in tables:
                print(f"- {table}")
            
            return 0
            
        except Exception as e:
            print(f"\nError initializing database: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return 1

if __name__ == "__main__":
    import sys
    sys.exit(reset_database())
