import os
from app import create_app
from app.extensions.extensions import db
from app.models.user import User
from app.models.client import Client
from werkzeug.security import generate_password_hash

def setup_database():
    app = create_app()
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Create a test user if it doesn't exist
        if not User.query.filter_by(username='testuser').first():
            print("Creating test user...")
            user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('Test123!')
            )
            db.session.add(user)
            db.session.flush()
            
            client = Client(
                user_id=user.id,
                company_name='Test Company',
                email='test@example.com',  # Required field
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
        else:
            print("Test user already exists.")
        
        # Print database path
        print(f"\nDatabase path: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # List all tables
        print("\nTables in the database:")
        inspector = db.inspect(db.engine)
        for table_name in inspector.get_table_names():
            print(f"- {table_name}")

if __name__ == '__main__':
    setup_database()
