import os
import sys

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import Client, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Drop all tables
    db.drop_all()
    
    # Create all tables with the correct schema
    db.create_all()
    
    # Create admin user
    admin = User(
        email='admin@paycrypt.online',
        password_hash=generate_password_hash('admin123'),
        is_admin=True,
        is_active=True
    )
    db.session.add(admin)
    
    # Create a test client with commission rates
    test_client = Client(
        company_name='Test Client',
        email='test@client.com',
        contact_person='Test User',
        contact_email='test@client.com',
        deposit_commission_rate=0.035,
        withdrawal_commission_rate=0.015,
        deposit_commission=Decimal('0.035'),
        withdrawal_commission=Decimal('0.015'),
        balance=Decimal('0.0'),
        is_active=True
    )
    db.session.add(test_client)
    
    db.session.commit()
    print("Database reset and initial data created.")

    # Insert the default flat-rate packages
    from scripts.insert_flatrate_packages import insert_packages
    insert_packages()

    print("Database reset and initialization complete.")
