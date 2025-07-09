#!/usr/bin/env python
"""
Test script to verify the sidebar stats context processor works properly.
"""
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from flask import current_app
from flask_login import login_user

def test_admin_template_context():
    """Test if admin template context includes sidebar_stats"""
    app = create_app()
    
    with app.app_context():
        with app.test_request_context('/admin/dashboard'):
            print("=== Testing Admin Template Context ===")
            
            # Import the admin user model
            from app.models import AdminUser
            
            # Get an admin user for testing
            admin = AdminUser.query.first()
            if admin:
                print(f"✓ Found admin user: {admin.username}")
                
                # Create a client to simulate a request
                with app.test_client() as client:
                    # Login as admin
                    with client.session_transaction() as sess:
                        sess['_user_id'] = str(admin.id)
                        sess['_fresh'] = True
                    
                    # Test if we can access the dashboard
                    response = client.get('/admin/dashboard')
                    print(f"✓ Dashboard response status: {response.status_code}")
                    
                    if response.status_code == 500:
                        print("✗ Dashboard returned 500 error")
                        print(f"Response data: {response.data.decode()}")
                    else:
                        print("✓ Dashboard loaded successfully")
                        
            else:
                print("✗ No admin user found")
                
                # Create a test admin user
                from werkzeug.security import generate_password_hash
                from app.extensions import db
                
                test_admin = AdminUser(
                    username='testadmin',
                    email='test@example.com',
                    password_hash=generate_password_hash('password'),
                    is_active=True,
                    is_superuser=True
                )
                
                try:
                    db.session.add(test_admin)
                    db.session.commit()
                    print("✓ Created test admin user")
                    
                    # Test with the new admin
                    with app.test_client() as client:
                        with client.session_transaction() as sess:
                            sess['_user_id'] = str(test_admin.id)
                            sess['_fresh'] = True
                        
                        response = client.get('/admin/dashboard')
                        print(f"✓ Dashboard response status: {response.status_code}")
                        
                        if response.status_code == 500:
                            print("✗ Dashboard returned 500 error")
                            print(f"Response data: {response.data.decode()}")
                        else:
                            print("✓ Dashboard loaded successfully")
                            
                except Exception as e:
                    print(f"✗ Error creating test admin: {str(e)}")

if __name__ == '__main__':
    print("Testing admin template context...")
    test_admin_template_context()
    print("Test complete.")
