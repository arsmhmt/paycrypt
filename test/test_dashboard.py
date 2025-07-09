import requests
import sys

def test_dashboard(cookies=None):
    # Test dashboard endpoint
    url = 'http://localhost:5000/admin/dashboard'
    
    # Test without authentication
    print("\n1. Testing GET /admin/dashboard without authentication")
    response = requests.get(url, allow_redirects=False)
    
    print(f"Status Code: {response.status_code}")
    print(f"Location: {response.headers.get('Location')}")
    
    if response.status_code == 302 and 'login' in response.headers.get('Location', ''):
        print("✅ Correctly redirected to login page")
    else:
        print("❌ Unexpected response without authentication")
    
    # Test with authentication
    if cookies:
        print("\n2. Testing GET /admin/dashboard with authentication")
        response = requests.get(url, cookies=cookies, allow_redirects=True)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type')}")
        print(f"Response Length: {len(response.text)} bytes")
        
        if 'Admin Dashboard' in response.text:
            print("✅ Successfully accessed dashboard")
        else:
            print("❌ Failed to access dashboard")
            print("Response sample:", response.text[:200])
    else:
        print("\nSkipping authenticated test - no cookies provided")

if __name__ == "__main__":
    print("Starting dashboard test...")
    try:
        # You can pass cookies from login test if needed
        cookies = {}
        test_dashboard(cookies)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
