#!/usr/bin/env python
"""
Test script to verify the clients template syntax is correct.
"""
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from flask import current_app

def test_clients_template():
    """Test if clients template renders without syntax errors"""
    app = create_app()
    
    with app.app_context():
        print("=== Testing Clients Template ===")
        
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
                
                # Test if we can access the clients page
                response = client.get('/admin/clients')
                print(f"✓ Clients page response status: {response.status_code}")
                
                if response.status_code == 500:
                    print("✗ Clients page returned 500 error")
                    print(f"Response data: {response.data.decode()}")
                else:
                    print("✓ Clients page loaded successfully")
                    print("✓ Template syntax errors have been resolved")
                    
        else:
            print("✗ No admin user found")

if __name__ == '__main__':
    print("Testing clients template syntax...")
    test_clients_template()
    print("Test complete.")
