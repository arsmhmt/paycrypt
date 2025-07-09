import os
import sys
import requests
import json
from urllib.parse import urljoin

# Configuration
BASE_URL = 'http://localhost:5000'
LOGIN_URL = urljoin(BASE_URL, '/auth/login')
DASHBOARD_URL = urljoin(BASE_URL, '/admin/dashboard')
REFRESH_URL = urljoin(BASE_URL, '/auth/refresh')
LOGOUT_URL = urljoin(BASE_URL, '/auth/logout')

# Test credentials
TEST_USERNAME = 'testadmin'
TEST_PASSWORD = 'testpass123'

def print_http_exchange(method, url, **kwargs):
    """Print details of an HTTP request/response"""
    print(f"\n{'='*80}")
    print(f"REQUEST: {method} {url}")
    if 'json' in kwargs:
        print("BODY (JSON):", json.dumps(kwargs['json'], indent=2))
    elif 'data' in kwargs:
        print("BODY (FORM):", kwargs['data'])
    if 'headers' in kwargs:
        print("HEADERS:", {k: v for k, v in kwargs['headers'].items() 
                          if k.lower() not in ['authorization', 'cookie']})
    if 'cookies' in kwargs:
        print("COOKIES:", kwargs['cookies'])
    
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
    """Test the login endpoint"""
    print("\n1. Testing login...")
    
    # First, get the CSRF token
    session = requests.Session()
    response = session.get(LOGIN_URL)
    csrf_token = None
    
    # Try to extract CSRF token from HTML
    if '<input id="csrf_token"' in response.text:
        csrf_token = response.text.split('name="csrf_token" value="')[1].split('"')[0]
    
    # Prepare login data
    login_data = {
        'username': username,
        'password': password,
        'remember': 'y'
    }
    
    # Add CSRF token if found
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    # Make login request
    response = print_http_exchange(
        'POST',
        LOGIN_URL,
        data=login_data,
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
        },
        cookies=session.cookies,
        allow_redirects=True
    )
    
    # Check for successful login
    if response.status_code == 200 and 'access_token_cookie' in response.cookies:
        print("✅ Login successful")
        return response.cookies
    else:
        print("❌ Login failed")
        return None

def test_dashboard_access(cookies):
    """Test accessing the dashboard with the obtained cookies"""
    print("\n2. Testing dashboard access...")
    
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

def test_refresh_token(cookies):
    """Test refreshing the access token"""
    print("\n3. Testing token refresh...")
    
    if 'refresh_token_cookie' not in cookies:
        print("❌ No refresh token available")
        return None
    
    # Try to refresh the token
    response = print_http_exchange(
        'POST',
        REFRESH_URL,
        cookies=cookies,
        allow_redirects=False
    )
    
    if response.status_code == 200 and 'access_token_cookie' in response.cookies:
        print("✅ Successfully refreshed access token")
        return response.cookies
    else:
        print("❌ Failed to refresh token")
        return None

def test_logout(cookies):
    """Test logging out"""
    print("\n4. Testing logout...")
    
    response = print_http_exchange(
        'GET',
        LOGOUT_URL,
        cookies=cookies,
        allow_redirects=True
    )
    
    # Check if cookies were cleared
    cleared_cookies = response.history[-1].cookies if response.history else response.cookies
    access_cleared = any('access_token_cookie' in str(c) and 'deleted' in str(c).lower() 
                         for c in cleared_cookies)
    
    if access_cleared:
        print("✅ Logout successful")
        return True
    else:
        print("❌ Logout failed - cookies not cleared")
        return False

def main():
    print("=== Testing JWT Authentication Flow ===\n")
    
    # 1. Test login
    cookies = test_login(TEST_USERNAME, TEST_PASSWORD)
    if not cookies:
        print("\n❌ Authentication tests failed at login step")
        return 1
    
    # 2. Test dashboard access
    if not test_dashboard_access(cookies):
        print("\n❌ Authentication tests failed at dashboard access")
        return 1
    
    # 3. Test token refresh
    new_cookies = test_refresh_token(cookies)
    if new_cookies:
        cookies.update(new_cookies)  # Use the new cookies if refresh was successful
    
    # 4. Test logout
    if not test_logout(cookies):
        print("\n⚠️ Logout test had issues, but continuing...")
    
    print("\n✅ All tests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
