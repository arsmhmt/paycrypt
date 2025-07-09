from app import create_app, db
from app.models import Client, User
from werkzeug.security import generate_password_hash
import os
import decimal

# Create application context
app = create_app()

# Create database file if it doesn't exist
if not os.path.exists('app.db'):
    print("Creating database file...")
    with open('app.db', 'w') as f:
        pass

with app.app_context():
    # Drop all tables
    print("Dropping all tables...")
    db.drop_all()
    
    # Create all tables
    print("Creating tables...")
    db.create_all()
    
    # Create admin user
    print("Creating admin user...")
    admin = User(
        email='admin@paycrypt.online',
        password_hash=generate_password_hash('admin123'),
        is_admin=True,
        is_active=True
    )
    db.session.add(admin)
    
    # Create test client with commission fields
    print("Creating test client...")
    test_client = Client(
        company_name='Test Client',
        email='test@client.com',
        contact_person='Test User',
        contact_email='test@client.com',
        deposit_commission_rate=0.035,
        withdrawal_commission_rate=0.015,
        deposit_commission=decimal.Decimal('0.035'),
        withdrawal_commission=decimal.Decimal('0.015'),
        balance=decimal.Decimal('0.0'),
        is_active=True
    )
    db.session.add(test_client)
    
    # Commit changes
    print("Committing changes...")
    db.session.commit()
    
    print("Database initialized successfully!")
