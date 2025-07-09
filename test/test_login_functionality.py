#!/usr/bin/env python3
"""
Quick test script to verify admin login functionality
"""

import requests
import json

def test_admin_login():
    """Test admin login functionality"""
    base_url = "http://127.0.0.1:8080"
    login_url = f"{base_url}/admin120724/login"
    
    # Test credentials
    test_credentials = {
        'username': 'paycrypt',  # Default admin user
        'password': 'test123',   # Default password
    }
    
    print("🔍 Testing Admin Login...")
    print(f"URL: {login_url}")
    print(f"Username: {test_credentials['username']}")
    
    try:
        # First, get the login page to get CSRF token
        session = requests.Session()
        
        print("\n1. Getting login page...")
        get_response = session.get(login_url)
        print(f"   Status: {get_response.status_code}")
        
        if get_response.status_code != 200:
            print(f"❌ Failed to get login page: {get_response.status_code}")
            return False
            
        # Try to extract CSRF token (basic approach)
        content = get_response.text
        if 'csrf_token' in content:
            print("   ✅ CSRF token found in page")
        else:
            print("   ⚠️  CSRF token not found in page")
        
        # Test login
        print("\n2. Testing login...")
        login_data = test_credentials.copy()
        
        # Try to extract CSRF token using regex
        import re
        csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', content)
        if csrf_match:
            login_data['csrf_token'] = csrf_match.group(1)
            print(f"   ✅ CSRF token extracted: {login_data['csrf_token'][:10]}...")
        else:
            print("   ⚠️  Could not extract CSRF token from form")
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        response = session.post(login_url, data=login_data, headers=headers, allow_redirects=False)
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"   ✅ Redirected to: {location}")
            if 'dashboard' in location:
                print("   ✅ Login successful - redirected to dashboard")
                return True
            else:
                print("   ⚠️  Redirected but not to dashboard")
                return False
        elif response.status_code == 200:
            if 'Invalid username or password' in response.text:
                print("   ❌ Login failed - invalid credentials")
            elif 'dashboard' in response.text:
                print("   ✅ Login successful - dashboard content")
                return True
            else:
                print("   ⚠️  Unexpected response content")
                print(f"   Content preview: {response.text[:200]}...")
            return False
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the application. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error during login test: {e}")
        return False

def test_client_login():
    """Test client login functionality"""
    base_url = "http://127.0.0.1:8080"
    # Client login is at /client/login, auth login is at /auth/login
    client_login_url = f"{base_url}/client/login"
    auth_login_url = f"{base_url}/auth/login"
    
    print("\n\n🔍 Testing Client Login Routes...")
    
    try:
        session = requests.Session()
        
        # Test client login route
        print(f"\n1. Testing client login at: {client_login_url}")
        get_response = session.get(client_login_url)
        print(f"   Status: {get_response.status_code}")
        
        if get_response.status_code == 200:
            print("   ✅ Client login page loads successfully")
            client_result = True
        else:
            print(f"   ❌ Failed to get client login page: {get_response.status_code}")
            client_result = False
        
        # Test auth login route
        print(f"\n2. Testing auth login at: {auth_login_url}")
        get_response2 = session.get(auth_login_url)
        print(f"   Status: {get_response2.status_code}")
        
        if get_response2.status_code == 200:
            print("   ✅ Auth login page loads successfully")
            auth_result = True
        else:
            print(f"   ❌ Failed to get auth login page: {get_response2.status_code}")
            auth_result = False
            
        return client_result or auth_result  # Either one working is good
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the application. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error during client login test: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 CPGATEWAY LOGIN TESTS")
    print("=" * 60)
    
    admin_result = test_admin_login()
    client_result = test_client_login()
    
    print("\n" + "=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60)
    print(f"Admin Login:  {'✅ PASS' if admin_result else '❌ FAIL'}")
    print(f"Client Login: {'✅ PASS' if client_result else '❌ FAIL'}")
    
    overall_result = admin_result and client_result
    print(f"\nOverall:      {'✅ ALL TESTS PASSED' if overall_result else '❌ SOME TESTS FAILED'}")
    
    if not overall_result:
        print("\n💡 Next steps:")
        if not admin_result:
            print("   - Check admin credentials (paycrypt/test123)")
            print("   - Verify admin user exists in database")
            print("   - Check admin route configuration")
        if not client_result:
            print("   - Check client login route")
            print("   - Verify client login template")
