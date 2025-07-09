import os
import sys
from app import create_app
from app.extensions.extensions import db
from app.models.user import User
from app.models.client import Client
from werkzeug.security import generate_password_hash

def init_new_database():
    # Set the FLASK_ENV to development if not set
    if 'FLASK_ENV' not in os.environ:
        os.environ['FLASK_ENV'] = 'development'
    
    # Remove existing database files if they exist
    db_files = [
        os.path.join('instance', 'app.db'),
        os.path.join('instance', 'cpgateway.db')
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                print(f"Removed existing database file: {db_file}")
            except Exception as e:
                print(f"Error removing {db_file}: {e}")
    
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
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            print(f"\nDatabase created at: {db_path}")
            print(f"File size: {os.path.getsize(db_path) / 1024:.2f} KB")
            
        except Exception as e:
            print(f"\nError initializing database: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(init_new_database())
