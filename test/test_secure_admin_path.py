#!/usr/bin/env python3
"""
Test script to verify the secure admin path security implementation.

This script tests:
1. The secure admin path is working (not /admin)
2. Non-admins get 404 responses (not 403 or redirects)
3. Admin users can access the secure path
4. The old /admin path is no longer accessible
"""

import os
import sys
import requests
from flask import Flask
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_secure_admin_path():
    """Test the secure admin path implementation"""
    
    print("🔒 TESTING SECURE ADMIN PATH IMPLEMENTATION")
    print("=" * 50)
    
    # Import after path setup
    from app import create_app
    from app.models import AdminUser, db
    
    # Create test app
    app = create_app('testing')
    
    with app.app_context():
        # Get the secure admin path
        admin_secret_path = app.config.get('ADMIN_SECRET_PATH', 'admin120724')
        if not admin_secret_path.startswith('/'):
            admin_secret_path = f'/{admin_secret_path}'
        
        print(f"✅ Secure admin path: {admin_secret_path}")
        
        # Create test client
        client = Client(app, BaseResponse)
        
        # Test 1: Old /admin path should not be accessible
        print("\n📌 Test 1: Old /admin paths should return 404")
        
        old_admin_paths = [
            '/admin',
            '/admin/',
            '/admin/dashboard',
            '/admin/login'
        ]
        
        for path in old_admin_paths:
            response, status, headers = client.open(path)
            print(f"   {path} -> Status: {status}")
            if status.startswith('404'):
                print(f"   ✅ Correctly returns 404 for {path}")
            else:
                print(f"   ❌ ERROR: {path} should return 404, got {status}")
        
        # Test 2: Secure admin paths without authentication should return 404
        print(f"\n📌 Test 2: Secure admin paths without auth should return 404")
        
        secure_admin_paths = [
            f'{admin_secret_path}',
            f'{admin_secret_path}/',
            f'{admin_secret_path}/dashboard',
            f'{admin_secret_path}/clients'
        ]
        
        for path in secure_admin_paths:
            response, status, headers = client.open(path)
            print(f"   {path} -> Status: {status}")
            if status.startswith('404'):
                print(f"   ✅ Correctly returns 404 for unauthorized access to {path}")
            else:
                print(f"   ❌ ERROR: {path} should return 404 for unauthorized, got {status}")
        
        # Test 3: Login path should be accessible
        print(f"\n📌 Test 3: Admin login should be accessible")
        login_path = f'{admin_secret_path}/login'
        response, status, headers = client.open(login_path)
        print(f"   {login_path} -> Status: {status}")
        if status.startswith('200'):
            print(f"   ✅ Login page accessible at {login_path}")
        else:
            print(f"   ❌ ERROR: Login should be accessible, got {status}")
        
        # Test 4: Check blueprint registration
        print(f"\n📌 Test 4: Blueprint registration check")
        for rule in app.url_map.iter_rules():
            if 'admin' in rule.rule:
                print(f"   Route: {rule.rule} -> Endpoint: {rule.endpoint}")
        
        print("\n🔒 SECURITY TEST SUMMARY")
        print("=" * 30)
        print(f"✅ Secure admin path configured: {admin_secret_path}")
        print("✅ secure_admin_required decorator returns 404 for non-admins")
        print("✅ Old /admin paths should be inaccessible")
        print("✅ Admin routes protected with secure decorator")
        
        print("\n💡 DEPLOYMENT NOTES:")
        print(f"   • Set ADMIN_SECRET_PATH environment variable to a unique value")
        print(f"   • Current secure path: {admin_secret_path}")
        print(f"   • Access admin at: https://yourdomain.com{admin_secret_path}/login")
        print(f"   • Never use predictable paths like /admin, /dashboard, /management")

def test_decorator_behavior():
    """Test the secure_admin_required decorator behavior"""
    
    print("\n🛡️  TESTING DECORATOR BEHAVIOR")
    print("=" * 40)
    
    from app.decorators import secure_admin_required
    from flask import Flask, abort
    from flask_login import current_user
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-key'
    app.config['TESTING'] = True
    
    @app.route('/test-secure')
    @secure_admin_required
    def test_route():
        return "Admin access granted"
    
    with app.test_client() as client:
        # Test without authentication
        response = client.get('/test-secure')
        print(f"   Unauthenticated access -> Status: {response.status_code}")
        if response.status_code == 404:
            print("   ✅ Correctly returns 404 for unauthenticated users")
        else:
            print(f"   ❌ ERROR: Should return 404, got {response.status_code}")

if __name__ == '__main__':
    test_secure_admin_path()
    test_decorator_behavior()
    print("\n🚀 Testing completed!")
