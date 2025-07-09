#!/usr/bin/env python3
"""
Simple test to isolate admin login issue
"""
import requests
from bs4 import BeautifulSoup
import json

def test_admin_login_detailed():
    """Test admin login with detailed error reporting"""
    print("=== DETAILED ADMIN LOGIN TEST ===")
    
    session = requests.Session()
    
    try:
        # Get login page
        login_url = "http://localhost:8080/admin/login"
        print(f"1. Getting login page: {login_url}")
        response = session.get(login_url)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Failed to get login page: {response.status_code}")
            return False
        
        # Parse CSRF token
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        if not csrf_input:
            print("❌ No CSRF token found")
            return False
        
        csrf_token = csrf_input.get('value')
        print(f"2. CSRF token extracted: {csrf_token[:20]}...")
        
        # Prepare login data
        login_data = {
            'username': 'testadmin',
            'password': 'testpassword',
            'csrf_token': csrf_token
        }
        
        print("3. Attempting POST login...")
        print(f"   Data: {json.dumps({k: v if k != 'password' else '***' for k, v in login_data.items()}, indent=2)}")
        
        # Attempt login
        response = session.post(login_url, data=login_data, allow_redirects=False)
        print(f"   POST Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print(f"✅ Success! Redirected to: {response.headers.get('Location')}")
            return True
        elif response.status_code == 500:
            print("❌ 500 Server Error - checking response content...")
            print(f"   Content length: {len(response.text)}")
            # Look for error details in response
            if "Traceback" in response.text or "Error" in response.text:
                lines = response.text.split('\n')
                for i, line in enumerate(lines):
                    if "Traceback" in line or "Error:" in line:
                        print(f"   Error found at line {i}: {line}")
                        # Print next few lines for context
                        for j in range(i, min(i+10, len(lines))):
                            if lines[j].strip():
                                print(f"   {j}: {lines[j]}")
                        break
            return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"   Response preview: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False

if __name__ == "__main__":
    test_admin_login_detailed()
