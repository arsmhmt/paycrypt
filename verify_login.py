import os
import sys
import requests
from flask import Flask, request, jsonify

# Configuration
BASE_URL = 'http://localhost:5000'
LOGIN_URL = f"{BASE_URL}/auth/login"
DASHBOARD_URL = f"{BASE_URL}/admin/dashboard"

def print_http_exchange(method, url, **kwargs):
    """Print details of an HTTP request/response"""
    print(f"\n{'='*80}")
    print(f"REQUEST: {method} {url}")
    if 'json' in kwargs:
        print("BODY (JSON):", kwargs['json'])
    elif 'data' in kwargs:
        print("BODY (FORM):", kwargs['data'])
    if 'headers' in kwargs:
        print("HEADERS:", {k: v for k, v in kwargs['headers'].items() 
                          if k.lower() not in ['authorization', 'cookie']})
    
    response = requests.request(method, url, **kwargs, allow_redirects=False)
    
    print(f"\nRESPONSE: {response.status_code} {response.reason}")
    print("HEADERS:", dict(response.headers))
    print("COOKIES:", response.cookies.get_dict())
    
    try:
        print("JSON:", response.json())
    except:
        print("TEXT:", response.text[:500] + ('...' if len(response.text) > 500 else ''))
    
    print("="*80)
    return response

def test_login(username, password):
    """Test the login flow"""
    # 1. Get login page (should return 200 with login form)
    print("\n1. Getting login page...")
    response = print_http_exchange('GET', LOGIN_URL)
    
    if response.status_code != 200:
        print("❌ Failed to get login page")
        return False
    
    # 2. Submit login form (should redirect to dashboard)
    print("\n2. Submitting login form...")
    response = print_http_exchange(
        'POST', 
        LOGIN_URL,
        data={'username': username, 'password': password},
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        allow_redirects=True
    )
    
    # Check for successful login (should redirect to dashboard)
    if response.status_code != 200 or 'dashboard' not in response.url:
        print("❌ Login failed or unexpected redirect")
        return False
    
    # Check for JWT cookies
    cookies = response.cookies.get_dict()
    if 'access_token_cookie' not in cookies:
        print("❌ No access token cookie found after login")
        return False
    
    print("✅ Login successful")
    return cookies

def test_dashboard_access(cookies):
    """Test accessing the dashboard with the obtained cookies"""
    print("\n3. Testing dashboard access...")
    
    # Access dashboard with cookies
    response = print_http_exchange(
        'GET',
        DASHBOARD_URL,
        cookies=cookies,
        allow_redirects=True
    )
    
    if response.status_code == 200 and 'Dashboard' in response.text:
        print("✅ Successfully accessed dashboard")
        return True
    else:
        print("❌ Failed to access dashboard")
        return False

def main():
    # Get credentials from environment or use defaults
    username = os.getenv('ADMIN_USERNAME', 'testadmin')
    password = os.getenv('ADMIN_PASSWORD', 'testpass123')
    
    print(f"Testing login with username: {username}")
    
    # Test login
    cookies = test_login(username, password)
    if not cookies:
        print("\n❌ Login test failed")
        sys.exit(1)
    
    # Test dashboard access
    if not test_dashboard_access(cookies):
        print("\n❌ Dashboard access test failed")
        sys.exit(1)
    
    print("\n✅ All tests passed!")
    sys.exit(0)

if __name__ == "__main__":
    main()
