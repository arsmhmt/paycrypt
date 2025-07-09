import requests
import sys

def test_login():
    # Test login endpoint
    url = 'http://localhost:5000/auth/login'
    
    # Test GET request
    print("\n1. Testing GET /auth/login")
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Content Type: {response.headers.get('content-type')}")
    print(f"Response Length: {len(response.text)} bytes")
    
    # Test POST with incorrect credentials
    print("\n2. Testing POST /auth/login with incorrect credentials")
    response = requests.post(url, data={
        'username': 'wronguser',
        'password': 'wrongpass'
    }, allow_redirects=False)
    
    print(f"Status Code: {response.status_code}")
    print(f"Location: {response.headers.get('Location')}")
    print(f"Cookies: {response.cookies}")
    
    # Test POST with correct credentials
    print("\n3. Testing POST /auth/login with correct credentials")
    response = requests.post(url, data={
        'username': 'testadmin',
        'password': 'testpass123'
    }, allow_redirects=True)
    
    print(f"Status Code: {response.status_code}")
    print(f"Final URL: {response.url}")
    print(f"Cookies: {response.cookies}")
    print(f"Response Length: {len(response.text)} bytes")
    
    # Check for JWT cookies
    cookies = response.cookies
    if 'access_token_cookie' in cookies:
        print("✅ Access token cookie found")
    else:
        print("❌ Access token cookie not found")
    
    if 'refresh_token_cookie' in cookies:
        print("✅ Refresh token cookie found")
    else:
        print("❌ Refresh token cookie not found")
    
    return response.cookies

if __name__ == "__main__":
    print("Starting login test...")
    try:
        cookies = test_login()
        if 'access_token_cookie' in cookies:
            print("\n✅ Login test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Login test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
