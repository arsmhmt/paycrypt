from app import create_app, db
from app.models import Client, User
from werkzeug.security import generate_password_hash
import decimal
import os

# Create application context
app = create_app()

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
    
    # Verify the schema
    print("\nVerifying database schema...")
    result = db.engine.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'").fetchone()
    if result:
        print("Clients table exists. Checking columns...")
        columns = db.engine.execute("PRAGMA table_info(clients)").fetchall()
        column_names = [col[1] for col in columns]
        print("Columns in clients table:", column_names)
    else:
        print("Clients table does not exist!")
