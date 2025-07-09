import requests
import sys

def test_logout(cookies=None):
    """Test logout functionality"""
    print("\n=== Testing Logout ===")
    
    # Test logout without being logged in
    print("\n1. Testing logout without being logged in")
    response = requests.get(
        'http://localhost:5000/auth/logout',
        allow_redirects=True
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Redirected to: {response.url}")
    
    # Test logout with valid session
    if cookies and 'access_token_cookie' in cookies:
        print("\n2. Testing logout with valid session")
        response = requests.get(
            'http://localhost:5000/auth/logout',
            cookies=cookies,
            allow_redirects=True
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Redirected to: {response.url}")
        
        # Check if cookies are cleared
        response_cookies = response.history[-1].cookies if response.history else response.cookies
        access_cleared = any('access_token_cookie="";' in str(c) for c in response_cookies)
        refresh_cleared = any('refresh_token_cookie="";' in str(c) for c in response_cookies)
        
        print(f"Access Token Cleared: {'✅ Yes' if access_cleared else '❌ No'}")
        print(f"Refresh Token Cleared: {'✅ Yes' if refresh_cleared else '❌ No'}")
        
        if access_cleared and refresh_cleared:
            print("✅ Logout successful")
            return True
        else:
            print("❌ Logout failed - cookies not cleared")
            return False
    else:
        print("\nSkipping authenticated logout test - no session cookies provided")
        return False

if __name__ == "__main__":
    print("Starting logout test...")
    try:
        # First, log in to get a session
        login_response = requests.post(
            'http://localhost:5000/auth/login',
            data={'username': 'testadmin', 'password': 'testpass123'},
            allow_redirects=True
        )
        
        if 'access_token_cookie' not in login_response.cookies:
            print("❌ Could not log in. Cannot test logout.")
            sys.exit(1)
            
        # Test logout
        success = test_logout(login_response.cookies)
        
        if success:
            print("\n✅ Logout test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Logout test failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
