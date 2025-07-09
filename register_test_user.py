from app import create_app
from app.extensions.extensions import db
from app.models.user import User
from app.models.client import Client
from werkzeug.security import generate_password_hash

def register_test_user():
    app = create_app()
    
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            print("Test user already exists!")
            return
        
        # Create a new user
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('Test123!'),
            is_active=True,
            is_verified=True
        )
        
        # Add user to the database
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
        
        print("Test user created successfully!")
        print(f"Username: testuser")
        print(f"Password: Test123!")

if __name__ == '__main__':
    register_test_user()
