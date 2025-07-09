import os
import sys
from app import create_app
from app.extensions.extensions import db
from app.models.user import User
from app.models.client import Client
from werkzeug.security import generate_password_hash

def init_database():
    # Set the FLASK_ENV to development if not set
    if 'FLASK_ENV' not in os.environ:
        os.environ['FLASK_ENV'] = 'development'
    
    # Create the Flask app
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            
            # Create a test user if it doesn't exist
            if not User.query.filter_by(username='testuser').first():
                print("Creating test user...")
                user = User(
                    username='testuser',
                    email='test@example.com',
                    password_hash=generate_password_hash('Test123!'),
                    is_active=True,
                    is_verified=True
                )
                db.session.add(user)
                db.session.flush()
                
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
            else:
                print("Test user already exists.")
            
            # Print database path
            print(f"\nDatabase path: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # List all tables
            print("\nTables in the database:")
            inspector = db.inspect(db.engine)
            for table_name in inspector.get_table_names():
                print(f"- {table_name}")
                
        except Exception as e:
            print(f"Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return 1
        
    return 0

if __name__ == '__main__':
    sys.exit(init_database())
