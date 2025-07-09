#!/usr/bin/env python3
"""
Simple login test for both admin and client users
"""

import requests
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Base URL for the application
BASE_URL = 'http://127.0.0.1:5000'

def test_admin_login():
    """Test admin login with testadmin credentials"""
    print("=== TESTING ADMIN LOGIN ===")
    
    session = requests.Session()
    
    # Step 1: Get login page
    login_url = f"{BASE_URL}/admin/login"
    response = session.get(login_url)
    print(f"GET login page status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Failed to get login page")
        return False
    
    # Step 2: Extract CSRF token
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    csrf_token = csrf_input['value'] if csrf_input else None
    print(f"CSRF token: {csrf_token[:20]}..." if csrf_token else "No CSRF token found")
    
    # Step 3: Prepare login data
    login_data = {
        'username': 'testadmin',
        'password': 'testpassword',  # Try this password
        'csrf_token': csrf_token
    }
    
    # Step 4: Submit login
    response = session.post(login_url, data=login_data, allow_redirects=False)
    print(f"POST login status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    if response.status_code == 302:
        print(f"✅ Admin login successful! Redirected to: {response.headers.get('Location')}")
        return True
    else:
        print("❌ Admin login failed")
        print(f"Response text snippet: {response.text[:500]}...")
        return False

def test_client_login():
    """Test client login with email credentials"""
    print("\n=== TESTING CLIENT LOGIN ===")
    
    session = requests.Session()
    
    # Step 1: Get login page
    login_url = f"{BASE_URL}/client/login"
    response = session.get(login_url)
    print(f"GET login page status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Failed to get login page")
        return False
    
    # Step 2: Extract CSRF token
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    csrf_token = csrf_input['value'] if csrf_input else None
    print(f"CSRF token: {csrf_token[:20]}..." if csrf_token else "No CSRF token found")
    
    # Step 3: Try different client accounts
    client_credentials = [
        {'username': 'testclient@example.com', 'password': 'testpassword'},
        {'username': 'admin@paycrypt.online', 'password': 'testpassword'},  # This client exists
        {'username': 'betagent@protonmail.com', 'password': 'testpassword'},  # smartbetslip client
    ]
    
    for creds in client_credentials:
        print(f"\nTrying credentials: {creds['username']}")
        
        # Prepare login data
        login_data = {
            'username': creds['username'],
            'password': creds['password'],
            'csrf_token': csrf_token
        }
        
        # Submit login
        response = session.post(login_url, data=login_data, allow_redirects=False)
        print(f"POST login status: {response.status_code}")
        
        if response.status_code == 302:
            print(f"✅ Client login successful! Redirected to: {response.headers.get('Location')}")
            return True
        elif response.status_code == 401:
            print("❌ Invalid credentials (401)")
        elif response.status_code == 400:
            print("❌ Bad request (400)")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response text snippet: {response.text[:300]}...")
    
    return False

def main():
    """Run login tests"""
    print("Starting login tests...")
    
    admin_success = test_admin_login()
    client_success = test_client_login()
    
    print(f"\n=== RESULTS ===")
    print(f"Admin login: {'✅ SUCCESS' if admin_success else '❌ FAILED'}")
    print(f"Client login: {'✅ SUCCESS' if client_success else '❌ FAILED'}")

if __name__ == '__main__':
    main()
