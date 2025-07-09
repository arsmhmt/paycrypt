#!/usr/bin/env python3
"""Test client authentication session persistence."""

import requests
import traceback

def test_authentication_flow():
    """Test the complete authentication flow with session debugging."""
    
    base_url = "http://localhost:8080"
    session = requests.Session()
    
    try:
        print("=== AUTHENTICATION FLOW TEST ===")
        
        # 1. Get login page
        print("\n1. Getting login page...")
        login_url = f"{base_url}/client/login"
        response = session.get(login_url)
        print(f"   Status: {response.status_code}")
        print(f"   Cookies received: {dict(response.cookies)}")
        
        if response.status_code != 200:
            print(f"   ERROR: Failed to get login page")
            return False
            
        # Extract CSRF token
        csrf_token = None
        lines = response.text.split('\n')
        for line in lines:
            if 'csrf_token' in line and 'value=' in line:
                start = line.find('value="') + 7
                end = line.find('"', start)
                csrf_token = line[start:end]
                break
                
        if not csrf_token:
            print("   ERROR: Could not extract CSRF token")
            return False
            
        print(f"   ✅ Got CSRF token: {csrf_token[:10]}...")
        
        # 2. Submit login credentials
        print("\n2. Submitting login credentials...")
        login_data = {
            'username': 'testclient_79939860@example.com',
            'password': 'testpassword',
            'csrf_token': csrf_token
        }
        
        response = session.post(login_url, data=login_data, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Cookies after login: {dict(session.cookies)}")
        
        if response.status_code not in [302, 303]:
            print(f"   ERROR: Login failed with status {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
        # Check redirect location
        redirect_location = response.headers.get('Location', '')
        print(f"   ✅ Login successful, redirecting to: {redirect_location}")
        
        # 3. Follow the redirect manually to see what happens
        print("\n3. Following redirect manually...")
        
        if redirect_location.startswith('/'):
            redirect_url = f"{base_url}{redirect_location}"
        else:
            redirect_url = redirect_location
            
        print(f"   Accessing: {redirect_url}")
        print(f"   Current cookies: {dict(session.cookies)}")
        
        response = session.get(redirect_url, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            # Another redirect
            redirect_location2 = response.headers.get('Location', '')
            print(f"   Another redirect to: {redirect_location2}")
            
            # If it redirects to login again, that's the problem
            if 'login' in redirect_location2:
                print("   ❌ ERROR: Redirected back to login - authentication not persisting!")
                return False
        elif response.status_code == 200:
            print("   ✅ Successfully reached target page")
            # Check if it's the dashboard
            if 'dashboard' in response.text.lower():
                print("   ✅ Dashboard content detected")
                return True
            else:
                print("   ⚠️ Not dashboard content")
                print(f"   Content length: {len(response.text)}")
                return False
        else:
            print(f"   ERROR: Unexpected status {response.status_code}")
            return False
            
        # 4. Try to access dashboard directly
        print("\n4. Trying to access dashboard directly...")
        dashboard_url = f"{base_url}/client/dashboard"
        response = session.get(dashboard_url, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("   ✅ Dashboard accessible")
            return True
        elif response.status_code == 302:
            redirect_location = response.headers.get('Location', '')
            print(f"   Redirected to: {redirect_location}")
            if 'login' in redirect_location:
                print("   ❌ ERROR: Dashboard access redirected to login!")
                return False
        else:
            print(f"   ERROR: Unexpected dashboard status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_authentication_flow()
    print("\n" + "="*50)
    if success:
        print("Test result: ✅ SUCCESS")
    else:
        print("Test result: ❌ FAILED")
    print("="*50)
