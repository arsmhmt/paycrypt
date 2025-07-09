#!/usr/bin/env python3
"""
Test actual login with correct credentials
"""
import requests
from bs4 import BeautifulSoup
import re

def test_admin_login():
    """Test admin login with testadmin/testpassword"""
    print("=== TESTING ADMIN LOGIN ===")
    
    # Start session
    session = requests.Session()
    
    # Get login page
    login_url = "http://localhost:8080/admin/login"
    response = session.get(login_url)
    print(f"GET login page status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Could not access admin login page")
        return False
    
    # Parse CSRF token
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if not csrf_input:
        print("❌ Could not find CSRF token")
        return False
    
    csrf_token = csrf_input.get('value')
    print(f"Using CSRF token: {csrf_token[:20]}...")
    
    # Attempt login
    login_data = {
        'username': 'testadmin',
        'password': 'testpassword',
        'csrf_token': csrf_token
    }
    
    response = session.post(login_url, data=login_data, allow_redirects=False)
    print(f"POST login status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    if response.status_code == 302:
        print(f"✅ Admin login successful! Redirected to: {response.headers.get('Location')}")
        return True
    else:
        print("❌ Admin login failed")
        print(f"Response text: {response.text[:500]}...")
        return False

def test_client_login():
    """Test client login with smartbetslip/Mahmut*1905"""
    print("\n=== TESTING CLIENT LOGIN ===")
    
    # Start session
    session = requests.Session()
    
    # Get login page
    login_url = "http://localhost:8080/client/login"
    response = session.get(login_url)
    print(f"GET login page status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Could not access client login page")
        return False
    
    # Parse CSRF token
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if not csrf_input:
        print("❌ Could not find CSRF token")
        return False
    
    csrf_token = csrf_input.get('value')
    print(f"Using CSRF token: {csrf_token[:20]}...")
    
    # Attempt login
    login_data = {
        'username': 'smartbetslip',
        'password': 'Mahmut*1905',
        'csrf_token': csrf_token
    }
    
    response = session.post(login_url, data=login_data, allow_redirects=False)
    print(f"POST login status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    if response.status_code == 302:
        print(f"✅ Client login successful! Redirected to: {response.headers.get('Location')}")
        return True
    else:
        print("❌ Client login failed")
        print(f"Response text: {response.text[:500]}...")
        return False

if __name__ == "__main__":
    # Test both logins
    admin_success = test_admin_login()
    client_success = test_client_login()
    
    print(f"\n=== SUMMARY ===")
    print(f"Admin login: {'✅ SUCCESS' if admin_success else '❌ FAILED'}")
    print(f"Client login: {'✅ SUCCESS' if client_success else '❌ FAILED'}")
