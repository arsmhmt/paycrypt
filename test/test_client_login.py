#!/usr/bin/env python3
"""
Quick test to verify client login and dashboard access
"""
import requests
import sys
from werkzeug.security import check_password_hash

def test_client_login():
    """Test client login with the provided credentials"""
    base_url = "http://127.0.0.1:8080"
    
    # Test client credentials
    username = "smartbetslip"
    password = "Mahmut*1905"
    
    print(f"🔍 Testing client login for: {username}")
    print(f"📍 Server URL: {base_url}")
    print("-" * 50)
    
    try:
        # First, get the login page to get any CSRF tokens
        session = requests.Session()
        login_page = session.get(f"{base_url}/client/login")
        
        if login_page.status_code == 200:
            print("✅ Client login page accessible")
        else:
            print(f"❌ Login page error: {login_page.status_code}")
            return
        
        # Test login
        login_data = {
            'username': username,
            'password': password
        }
        
        response = session.post(f"{base_url}/client/login", data=login_data, allow_redirects=False)
        
        if response.status_code == 302:  # Redirect after successful login
            print("✅ Login successful - redirecting")
            redirect_location = response.headers.get('Location', '')
            print(f"📍 Redirect to: {redirect_location}")
            
            # Follow redirect to dashboard
            dashboard_response = session.get(f"{base_url}/client/dashboard")
            if dashboard_response.status_code == 200:
                print("✅ Dashboard accessible")
                print("🎨 Modern dashboard should be visible with:")
                print("   • Glass-card design")
                print("   • Balance, Transactions, Volume, Commission widgets")
                print("   • Recent transactions table")
                print("   • Quick actions sidebar")
                print("   • Live system status")
                print("   • Dark mode toggle")
            else:
                print(f"❌ Dashboard access error: {dashboard_response.status_code}")
        
        elif response.status_code == 200:
            # Still on login page - check for errors
            if "invalid" in response.text.lower() or "error" in response.text.lower():
                print("❌ Login failed - invalid credentials")
            else:
                print("⚠️  Still on login page - check credentials")
        
        else:
            print(f"❌ Login error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Flask is running on port 8080")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_client_login()
