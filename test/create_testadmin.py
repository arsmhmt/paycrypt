#!/usr/bin/env python3
"""
Create a test admin with known password
"""
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app import create_app
from app.extensions import db
from app.models import AdminUser

def create_test_admin():
    """Create test admin with known password"""
    app = create_app()
    
    with app.app_context():
        # Check if testadmin already exists
        admin = AdminUser.query.filter_by(username='testadmin').first()
        
        if admin:
            print("Found existing testadmin, updating password...")
            admin.set_password('testpassword')
            db.session.commit()
            print("✅ testadmin password updated to 'testpassword'")
        else:
            print("Creating new testadmin...")
            admin = AdminUser(
                username='testadmin',
                email='testadmin@example.com',
                first_name='Test',
                last_name='Admin',
                is_active=True,
                is_superuser=True
            )
            admin.set_password('testpassword')
            db.session.add(admin)
            db.session.commit()
            print("✅ testadmin created with password 'testpassword'")
        
        # Verify the password works
        if admin.check_password('testpassword'):
            print("✅ Password verification successful")
        else:
            print("❌ Password verification failed")

if __name__ == '__main__':
    create_test_admin()
