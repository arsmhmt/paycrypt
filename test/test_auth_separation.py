#!/usr/bin/env python3
"""
Test script to verify authentication separation between client and admin systems.
This will test that logging in as a client does NOT grant admin access.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models import AdminUser
from app.models.client import Client
from flask import url_for
import requests

def test_auth_separation():
    """Test that client and admin authentication are properly separated"""
    app = create_app()
    
    with app.app_context():
        print("=== AUTHENTICATION SEPARATION TEST ===\n")
        
        # Import models within app context
        from app.models.user import User
        from app.models import AdminUser
        from app.models.client import Client
        
        # Check if betagent@protonmail.com exists as both client and admin
        client_user = User.query.filter_by(email='betagent@protonmail.com').first()
        admin_user = AdminUser.query.filter_by(email='betagent@protonmail.com').first()
        
        print(f"Client user (betagent@protonmail.com): {'EXISTS' if client_user else 'NOT FOUND'}")
        print(f"Admin user (betagent@protonmail.com): {'EXISTS' if admin_user else 'NOT FOUND'}")
        
        if client_user:
            print(f"  Client ID: {client_user.id}")
            print(f"  Client Username: {client_user.username}")
            # Check if this user has a client relationship
            client_record = Client.query.filter_by(user_id=client_user.id).first()
            print(f"  Has Client Record: {'YES' if client_record else 'NO'}")
            if client_record:
                print(f"  Client Company: {client_record.company_name}")
        
        if admin_user:
            print(f"  Admin ID: {admin_user.id}")
            print(f"  Admin Username: {admin_user.username}")
        
        print("\n=== USER LOADER TEST ===")
        
        # Test user_loader with client ID
        if client_user:
            # Test by directly calling the user_loader logic
            print(f"Testing user loading for client user ID {client_user.id}:")
            
            # Try to load user using the same logic as the user_loader
            try:
                from app.models.user import User
                from app.models import AdminUser
                
                # Try User model first
                loaded_user = User.query.get(client_user.id)
                if loaded_user:
                    print(f"  Loaded as User: {loaded_user}")
                    print(f"  User type: {type(loaded_user).__name__}")
                    if hasattr(loaded_user, 'is_client'):
                        print(f"  is_client(): {loaded_user.is_client()}")
                
                # Try AdminUser model
                loaded_admin = AdminUser.query.get(client_user.id)
                if loaded_admin:
                    print(f"  ⚠️  ALSO loaded as AdminUser: {loaded_admin}")
                else:
                    print(f"  ✅ NOT loaded as AdminUser (good)")
                    
            except Exception as e:
                print(f"  Error testing user loading: {e}")
        
        # Test user_loader with admin user if exists
        admin_test_id = 1  # Assuming admin user has ID 1
        print(f"\nTesting user loading for admin user ID {admin_test_id}:")
        try:
            from app.models.user import User
            from app.models import AdminUser
            
            # Try User model first
            loaded_user = User.query.get(admin_test_id)
            if loaded_user:
                print(f"  ⚠️  ALSO loaded as User: {loaded_user}")
            else:
                print(f"  ✅ NOT loaded as User (good)")
            
            # Try AdminUser model
            loaded_admin = AdminUser.query.get(admin_test_id)
            if loaded_admin:
                print(f"  Loaded as AdminUser: {loaded_admin}")
                print(f"  Admin type: {type(loaded_admin).__name__}")
                    
        except Exception as e:
            print(f"  Error testing admin loading: {e}")
        
        print("\n=== ROUTE PROTECTION TEST ===")
        
        # Test client and admin route access
        with app.test_client() as client:
            print("Testing route access without authentication:")
            
            # Test admin routes
            admin_routes = ['/admin/', '/admin/dashboard', '/admin/clients']
            for route in admin_routes:
                try:
                    response = client.get(route, follow_redirects=False)
                    print(f"  {route}: {response.status_code} {'(redirected)' if response.status_code in [301, 302] else ''}")
                except Exception as e:
                    print(f"  {route}: ERROR - {str(e)}")
            
            # Test client routes
            client_routes = ['/client/', '/client/dashboard']
            for route in client_routes:
                try:
                    response = client.get(route, follow_redirects=False)
                    print(f"  {route}: {response.status_code} {'(redirected)' if response.status_code in [301, 302] else ''}")
                except Exception as e:
                    print(f"  {route}: ERROR - {str(e)}")
        
        print("\n=== SECURITY ANALYSIS ===")
        
        # Check for potential security issues
        issues = []
        
        if client_user and admin_user and client_user.email == admin_user.email:
            issues.append("CRITICAL: Same email exists in both client and admin tables!")
        
        if client_user and admin_user and client_user.id == admin_user.id:
            issues.append("CRITICAL: Same ID exists in both client and admin tables!")
        
        # Check user_loader count
        from app.extensions import login_manager
        print(f"Login manager user_loader: {hasattr(login_manager, 'user_loader')}")
        
        if issues:
            print("SECURITY ISSUES FOUND:")
            for issue in issues:
                print(f"  ❌ {issue}")
        else:
            print("✅ No obvious security issues found")
        
        print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_auth_separation()
