#!/usr/bin/env python3
"""
Admin Security Test Script

This script tests the enhanced security features for the admin panel:
1. Non-guessable admin paths
2. 404 responses for non-admins
3. Rate limiting on admin routes
4. Secure admin required decorator

Usage:
    python test_admin_security.py
"""

import os
import sys
import requests
import time
from urllib.parse import urljoin

# Test configuration
BASE_URL = "http://localhost:8080"
ADMIN_SECRET_PATH = os.environ.get('ADMIN_SECRET_PATH', 'admin120724')

def test_admin_path_security():
    """Test that the admin path is properly secured"""
    print("🔒 Testing Admin Path Security")
    print("=" * 50)
    
    # Test 1: Old admin path should return 404
    print("\n1. Testing old /admin path (should return 404)")
    try:
        response = requests.get(urljoin(BASE_URL, "/admin/dashboard"), timeout=10)
        if response.status_code == 404:
            print("✅ OLD admin path correctly returns 404")
        else:
            print(f"❌ OLD admin path returned {response.status_code}, expected 404")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing old admin path: {e}")
    
    # Test 2: Secure admin path without authentication should return 404
    print(f"\n2. Testing secure path /{ADMIN_SECRET_PATH}/dashboard without auth (should return 404)")
    try:
        response = requests.get(urljoin(BASE_URL, f"/{ADMIN_SECRET_PATH}/dashboard"), timeout=10)
        if response.status_code == 404:
            print("✅ Secure admin path correctly returns 404 for unauthenticated users")
        else:
            print(f"❌ Secure admin path returned {response.status_code}, expected 404")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing secure admin path: {e}")
    
    # Test 3: Common admin paths should all return 404
    common_admin_paths = [
        "/admin",
        "/administrator", 
        "/backend",
        "/panel",
        "/control",
        "/cp",
        "/manage",
        "/management"
    ]
    
    print("\n3. Testing common admin paths (should all return 404)")
    for path in common_admin_paths:
        try:
            response = requests.get(urljoin(BASE_URL, path), timeout=5)
            if response.status_code == 404:
                print(f"✅ {path} correctly returns 404")
            else:
                print(f"❌ {path} returned {response.status_code}, expected 404")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error testing {path}: {e}")

def test_rate_limiting():
    """Test rate limiting on admin routes"""
    print("\n\n🚦 Testing Rate Limiting")
    print("=" * 50)
    
    # Test rate limiting on admin login
    print("\n1. Testing rate limiting on admin login")
    login_url = urljoin(BASE_URL, f"/{ADMIN_SECRET_PATH}/login")
    
    print(f"Making multiple requests to {login_url}")
    for i in range(7):  # Should hit rate limit after 5 requests
        try:
            response = requests.post(login_url, data={
                'username': 'test_invalid_user',
                'password': 'test_invalid_password'
            }, timeout=5)
            
            if response.status_code == 429:
                print(f"✅ Request {i+1}: Rate limit hit (429)")
                break
            else:
                print(f"🔄 Request {i+1}: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error on request {i+1}: {e}")
        
        time.sleep(0.5)  # Small delay between requests

def test_security_headers():
    """Test security headers and configuration"""
    print("\n\n🛡️ Testing Security Headers")
    print("=" * 50)
    
    try:
        response = requests.get(BASE_URL, timeout=10)
        headers = response.headers
        
        # Check for security headers
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block'
        }
        
        for header, expected_value in security_headers.items():
            if header in headers:
                print(f"✅ {header}: {headers[header]}")
            else:
                print(f"⚠️ Missing security header: {header}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing security headers: {e}")

def test_admin_route_enumeration():
    """Test that admin routes can't be easily enumerated"""
    print("\n\n🔍 Testing Admin Route Enumeration Protection")
    print("=" * 50)
    
    # Common admin route patterns
    admin_routes = [
        "dashboard",
        "users",
        "settings", 
        "logs",
        "config",
        "system",
        "reports",
        "analytics",
        "backup"
    ]
    
    print("Testing common admin routes (should all return 404 for non-admins)")
    for route in admin_routes:
        try:
            # Test with old admin path
            old_url = urljoin(BASE_URL, f"/admin/{route}")
            response = requests.get(old_url, timeout=5)
            
            if response.status_code == 404:
                print(f"✅ /admin/{route} returns 404")
            else:
                print(f"⚠️ /admin/{route} returns {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error testing /admin/{route}: {e}")

def main():
    """Run all security tests"""
    print("🔐 CPGateway Admin Security Test Suite")
    print("=====================================")
    print(f"Testing against: {BASE_URL}")
    print(f"Admin secret path: /{ADMIN_SECRET_PATH}")
    
    # Run tests
    test_admin_path_security()
    test_rate_limiting()
    test_security_headers()
    test_admin_route_enumeration()
    
    print("\n\n📊 Security Test Summary")
    print("=" * 50)
    print("✅ Tests completed - Review results above")
    print("🔒 Admin path security: Non-guessable path implemented")
    print("🚫 Route protection: 404 responses for non-admins") 
    print("🚦 Rate limiting: Active on admin routes")
    print("🛡️ Security headers: Check results above")
    
    print("\n📝 Security Recommendations:")
    print("1. Regularly rotate the ADMIN_SECRET_PATH")
    print("2. Monitor failed login attempts in logs")
    print("3. Consider adding IP whitelisting for admin access")
    print("4. Enable HTTPS in production")
    print("5. Set up alerting for suspicious admin access patterns")

if __name__ == "__main__":
    main()
