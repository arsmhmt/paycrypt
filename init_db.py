from app import create_app
from app.extensions import db
from app.models import User, AdminUser, Client, Payment, Withdrawal, Document, Platform, PlatformSetting

app = create_app()

with app.app_context():
    # Drop all tables first (be careful with this in production!)
    print("Dropping all tables...")
    db.drop_all()
    
    # Create all tables
    print("Creating tables...")
    db.create_all()
    
    # Verify tables were created
    print("\nAvailable tables:")
    for table in db.metadata.tables:
        print(f"- {table}")
    
    print("\nDatabase initialized successfully!")
