#!/usr/bin/env python3
"""
Test script to verify admin client management functionality
"""
import requests
import sys

BASE_URL = "http://127.0.0.1:8080"

def test_admin_login():
    """Test admin login and get session"""
    session = requests.Session()
    
    # Get login page to get CSRF token
    response = session.get(f"{BASE_URL}/admin/login")
    if response.status_code != 200:
        print(f"❌ Failed to get admin login page: {response.status_code}")
        return None
    
    # Login with admin credentials
    login_data = {
        'username': 'paycrypt',
        'password': 'admin123'
    }
    
    response = session.post(f"{BASE_URL}/admin/login", data=login_data)
    if "dashboard" in response.url or response.status_code == 200:
        print("✅ Admin login successful")
        return session
    else:
        print(f"❌ Admin login failed: {response.status_code}")
        return None

def test_client_routes(session):
    """Test all client management routes"""
    test_routes = [
        ("/admin/clients", "Clients list"),
        ("/admin/clients/new", "New client form"),
    ]
    
    # Test basic routes
    for route, description in test_routes:
        try:
            response = session.get(f"{BASE_URL}{route}")
            if response.status_code == 200:
                print(f"✅ {description}: OK")
            else:
                print(f"❌ {description}: {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
    
    # Get a client ID to test subpages
    try:
        response = session.get(f"{BASE_URL}/admin/clients")
        if response.status_code == 200:
            # Try to find a client ID in the response (basic parsing)
            if "clients/1/view" in response.text or "clients/1/" in response.text:
                client_id = 1
                print(f"Found client ID: {client_id}")
                
                # Test client subpages
                subpages = [
                    (f"/admin/clients/{client_id}/view", "Client view"),
                    (f"/admin/clients/{client_id}/commission", "Client commission"),
                    (f"/admin/clients/{client_id}/branding", "Client branding"),
                    (f"/admin/clients/{client_id}/rate-limits", "Client rate limits"),
                    (f"/admin/clients/{client_id}/api-keys", "Client API keys"),
                    (f"/admin/clients/{client_id}/audit-logs", "Client audit logs"),
                ]
                
                for route, description in subpages:
                    try:
                        response = session.get(f"{BASE_URL}{route}")
                        if response.status_code == 200:
                            print(f"✅ {description}: OK")
                        else:
                            print(f"❌ {description}: {response.status_code}")
                    except Exception as e:
                        print(f"❌ {description}: Error - {e}")
            else:
                print("⚠️  No existing clients found to test subpages")
                
    except Exception as e:
        print(f"❌ Error testing client routes: {e}")

def main():
    print("🧪 Testing admin client management functionality...")
    print("=" * 50)
    
    # Test admin login
    session = test_admin_login()
    if not session:
        print("❌ Cannot proceed without admin session")
        sys.exit(1)
    
    # Test client routes
    test_client_routes(session)
    
    print("=" * 50)
    print("🏁 Test completed")

if __name__ == '__main__':
    main()
