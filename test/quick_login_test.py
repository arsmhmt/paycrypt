#!/usr/bin/env python
"""
Simple test script for client login and dashboard access
"""

import requests
import sys
import re

# Configuration
BASE_URL = 'http://localhost:8080'
CLIENT_EMAIL = 'testclient_85120b7e@example.com'  # Update with the email from quick_create_client.py
PASSWORD = 'testpassword'

def test_client_login():
    """Test client login and dashboard access"""
    print(f"\nTesting login for client: {CLIENT_EMAIL}\n")
    
    session = requests.Session()
    
    try:
        # 1. Access login page
        print("1. Getting login page...")
        response = session.get(f"{BASE_URL}/client/login")
        
        if response.status_code != 200:
            print(f"❌ Failed to access login page: Status {response.status_code}")
            return False
            
        print(f"✅ Got login page: Status {response.status_code}")
        
        # 2. Extract CSRF token from the login page
        csrf_token = None
        csrf_match = re.search(r'<input[^>]*name="csrf_token"[^>]*value="([^"]*)"', response.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"   Found CSRF token: {csrf_token[:10]}...")
        else:
            print("   No CSRF token found")
        
        # 3. Submit login credentials
        print("\n3. Submitting login credentials...")
        login_data = {
            'username': CLIENT_EMAIL,
            'password': PASSWORD,
            'remember_me': 'on'
        }
        
        if csrf_token:
            login_data['csrf_token'] = csrf_token
        
        response = session.post(
            f"{BASE_URL}/client/login", 
            data=login_data,
            allow_redirects=False
        )
        
        # Check if we got a redirect (success) or error message
        if 300 <= response.status_code < 400:
            redirect_url = response.headers.get('Location')
            print(f"✅ Login successful: Redirected to {redirect_url}")
        else:
            print(f"❌ Login failed: Status {response.status_code}")
            print(f"Response content: {response.text[:500]}...")
            return False
        
        # 4. Access the dashboard with the session cookies
        print("\n4. Accessing dashboard...")
        response = session.get(f"{BASE_URL}/client/dashboard", allow_redirects=False)
        
        if response.status_code == 200:
            print(f"✅ Dashboard accessed successfully: Status {response.status_code}")
            
            # Check for expected content in the dashboard
            if "Welcome back" in response.text and "Dashboard" in response.text:
                print("✅ Dashboard content looks correct")
            else:
                print("⚠️ Dashboard accessed but content may be incorrect")
                
            return True
        elif 300 <= response.status_code < 400:
            redirect_url = response.headers.get('Location')
            print(f"⚠️ Dashboard redirected to: {redirect_url}")
            
            # Follow the redirect
            print("Following redirect...")
            response = session.get(redirect_url)
            print(f"Final status: {response.status_code}")
            return response.status_code == 200
        else:
            print(f"❌ Failed to access dashboard: Status {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            return False
    
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_client_login()
    print("\n" + "="*50)
    print(f"Test result: {'✅ PASSED' if success else '❌ FAILED'}")
    print("="*50)
    sys.exit(0 if success else 1)
