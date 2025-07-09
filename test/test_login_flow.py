#!/usr/bin/env python3
"""
Test login functionality for admin and client
"""
import requests
import json
from bs4 import BeautifulSoup

# Test admin login
def test_admin_login():
    print("=== TESTING ADMIN LOGIN ===")
    
    login_url = "http://127.0.0.1:8080/admin/login"
    
    # First get the login page to get CSRF token
    session = requests.Session()
    response = session.get(login_url)
    print(f"GET login page status: {response.status_code}")
    
    # Extract CSRF token from page
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = None
    csrf_meta = soup.find('meta', {'name': 'csrf-token'})
    if csrf_meta:
        csrf_token = csrf_meta.get('content')
    
    # Try login
    login_data = {
        'username': 'testadmin',
        'password': 'testpass123',  # Correct test password
    }
    
    if csrf_token:
        login_data['csrf_token'] = csrf_token
        print(f"Using CSRF token: {csrf_token[:20]}...")
    
    response = session.post(login_url, data=login_data, allow_redirects=False)
    print(f"POST login status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    if response.status_code == 302:
        print(f"Redirect location: {response.headers.get('Location')}")
        print("✅ Admin login successful - redirected")
    else:
        print("❌ Admin login failed")
        print(f"Response text: {response.text[:500]}...")

def test_client_login():
    print("\n=== TESTING CLIENT LOGIN ===")
    
    login_url = "http://127.0.0.1:8080/client/login"
    
    # First get the login page
    session = requests.Session()
    response = session.get(login_url)
    print(f"GET login page status: {response.status_code}")
    
    # Extract CSRF token from page
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = None
    csrf_meta = soup.find('meta', {'name': 'csrf-token'})
    if csrf_meta:
        csrf_token = csrf_meta.get('content')
    
    # Try login with email
    login_data = {
        'username': 'testclient@example.com',
        'password': 'testpassword',  # Correct client password
    }
    
    if csrf_token:
        login_data['csrf_token'] = csrf_token
        print(f"Using CSRF token: {csrf_token[:20]}...")
    
    response = session.post(login_url, data=login_data, allow_redirects=False)
    print(f"POST login status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    if response.status_code == 302:
        print(f"Redirect location: {response.headers.get('Location')}")
        print("✅ Client login successful - redirected")
    else:
        print("❌ Client login failed")
        print(f"Response text: {response.text[:500]}...")

if __name__ == "__main__":
    test_admin_login()
    test_client_login()
