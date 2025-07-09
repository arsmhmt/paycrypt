import requests
import sys

def test_refresh(cookies=None):
    """Test JWT token refresh endpoint"""
    print("\n=== Testing JWT Refresh ===")
    
    # Test refresh endpoint without refresh token
    print("\n1. Testing refresh without token")
    response = requests.post(
        'http://localhost:5000/auth/refresh',
        allow_redirects=False
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 401:
        print("✅ Correctly rejected refresh without token")
    else:
        print("❌ Unexpected response without refresh token")
    
    # Test refresh with valid refresh token
    if cookies and 'refresh_token_cookie' in cookies:
        print("\n2. Testing refresh with valid token")
        response = requests.post(
            'http://localhost:5000/auth/refresh',
            cookies={'refresh_token_cookie': cookies['refresh_token_cookie']},
            allow_redirects=False
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"New Access Token Cookie: 'access_token_cookie' in response.cookies")
        
        if response.status_code == 200 and 'access_token_cookie' in response.cookies:
            print("✅ Successfully refreshed access token")
            return response.cookies
        else:
            print("❌ Failed to refresh access token")
    else:
        print("\nSkipping refresh test - no refresh token provided")
    
    return None

if __name__ == "__main__":
    print("Starting refresh token test...")
    try:
        # First, get a refresh token by logging in
        login_response = requests.post(
            'http://localhost:5000/auth/login',
            data={'username': 'testadmin', 'password': 'testpass123'},
            allow_redirects=True
        )
        
        if 'refresh_token_cookie' not in login_response.cookies:
            print("❌ Could not get refresh token. Login failed.")
            sys.exit(1)
            
        # Test refresh with the obtained token
        new_cookies = test_refresh(login_response.cookies)
        
        if new_cookies and 'access_token_cookie' in new_cookies:
            print("\n✅ Refresh test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Refresh test failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
