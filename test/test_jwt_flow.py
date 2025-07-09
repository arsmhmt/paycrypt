import requests
import json

# Configuration
BASE_URL = 'http://localhost:5000'
LOGIN_URL = f"{BASE_URL}/auth/login"
DASHBOARD_URL = f"{BASE_URL}/admin/dashboard"

# Test credentials
CREDENTIALS = {
    'username': 'testadmin',
    'password': 'testpass123'
}

def test_login():
    """Test login and get JWT token"""
    print("\n=== Testing Login ===")
    
    # Make login request
    response = requests.post(
        LOGIN_URL,
        data=CREDENTIALS,
        allow_redirects=True
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response URL: {response.url}")
    print("Headers:", json.dumps(dict(response.headers), indent=2))
    
    # Check for redirect to dashboard on successful login
    if response.status_code == 200 and 'dashboard' in response.url:
        print("✅ Login successful - Redirected to dashboard")
        return True, response.cookies
    
    # If JSON response (API call)
    try:
        data = response.json()
        print("Response JSON:", json.dumps(data, indent=2))
        if data.get('success'):
            print("✅ Login successful - Token received")
            return True, response.cookies
    except:
        pass
    
    print("❌ Login failed")
    return False, None

def test_dashboard_access(cookies=None):
    """Test accessing dashboard with JWT"""
    print("\n=== Testing Dashboard Access ===")
    
    headers = {
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # Make request to dashboard
    response = requests.get(
        DASHBOARD_URL,
        cookies=cookies,
        headers=headers,
        allow_redirects=False
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Successfully accessed dashboard")
        print("Page content sample:", response.text[:200] + '...')
        return True
    elif response.status_code == 302:
        print(f"❌ Redirected to: {response.headers.get('Location', 'Unknown')}")
        print("This usually means the JWT token is missing or invalid")
    else:
        print("❌ Failed to access dashboard")
        print("Response:", response.text)
    
    return False

if __name__ == "__main__":
    # Test login
    success, cookies = test_login()
    
    # If login was successful, test dashboard access
    if success and cookies:
        test_dashboard_access(cookies)
    else:
        print("\n⚠️  Cannot test dashboard access without successful login")
