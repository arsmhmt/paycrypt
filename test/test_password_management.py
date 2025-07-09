#!/usr/bin/env python3
"""
Test script for password management functionality
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_admin_login():
    """Test admin login"""
    login_url = f"{BASE_URL}/admin/login"
    
    # Get login page first to get any CSRF token
    session = requests.Session()
    response = session.get(login_url)
    print(f"Login page status: {response.status_code}")
    
    # Attempt login
    login_data = {
        'username': 'paycrypt',
        'password': 'admin123'
    }
    
    response = session.post(login_url, data=login_data)
    print(f"Login attempt status: {response.status_code}")
    print(f"Login response URL: {response.url}")
    
    if response.status_code == 200 and "dashboard" in response.url.lower():
        print("✅ Login successful")
        return session
    else:
        print("❌ Login failed")
        return None

def test_client_view(session):
    """Test client view page"""
    clients_url = f"{BASE_URL}/admin/clients"
    response = session.get(clients_url)
    print(f"Clients page status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Clients page accessible")
        # Try to get first client ID from the page (simple approach)
        # In real scenario, we'd parse the HTML properly
        return 1  # Assume client ID 1 exists
    else:
        print("❌ Clients page not accessible")
        return None

def test_password_generation(session, client_id):
    """Test password generation endpoint"""
    generate_url = f"{BASE_URL}/admin/clients/{client_id}/generate-password"
    
    # Test JSON request
    response = session.post(generate_url, 
                          headers={'Content-Type': 'application/json'},
                          json={})
    
    print(f"Password generation status: {response.status_code}")
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Password generation response: {data}")
            if data.get('success'):
                print("✅ Password generation successful")
                print(f"Generated password: {data.get('password', 'N/A')}")
            else:
                print(f"❌ Password generation failed: {data.get('message')}")
        except:
            print("❌ Invalid JSON response")
    else:
        print("❌ Password generation endpoint error")

def main():
    print("🧪 Testing Password Management Functionality")
    print("=" * 50)
    
    # Test admin login
    session = test_admin_login()
    if not session:
        print("Cannot proceed without admin login")
        return
    
    # Test client view
    client_id = test_client_view(session)
    if not client_id:
        print("Cannot get client ID")
        return
    
    # Test password generation
    test_password_generation(session, client_id)
    
    print("\n✅ Testing completed")

if __name__ == "__main__":
    main()
