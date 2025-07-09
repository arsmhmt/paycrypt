import os
import sys
from app import create_app
from app.extensions.extensions import db
from app.models.user import User
from app.models.client import Client
from werkzeug.security import generate_password_hash

def create_test_user():
    # Set the FLASK_ENV to development if not set
    if 'FLASK_ENV' not in os.environ:
        os.environ['FLASK_ENV'] = 'development'
    
    # Create the Flask app
    app = create_app()
    
    with app.app_context():
        try:
            # Check if test user already exists
            if User.query.filter_by(username='testuser').first():
                print("Test user already exists!")
                return 0
            
            # Create a test user
            print("Creating test user...")
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
            
            return 0
            
        except Exception as e:
            print(f"\nError creating test user: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return 1

if __name__ == "__main__":
    sys.exit(create_test_user())
