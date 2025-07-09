#!/usr/bin/env python3
"""Direct dashboard test with detailed error logging."""

import requests
import traceback
from flask import Flask
from app import create_app
from app.models.client import Client
from app.extensions.extensions import db

def test_dashboard_direct():
    """Test dashboard access directly with proper error handling."""
    try:
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            # Find test client
            client = Client.query.filter_by(email='testclient_85120b7e@example.com').first()
            if not client:
                print("❌ Test client not found")
                return False
                
            print(f"✅ Found test client: {client.email} (ID: {client.id})")
            print(f"   Package ID: {client.package_id}")
            print(f"   Client Type: {client.type}")
            print(f"   Is Active: {client.is_active}")
            
            # Test HTTP request
            base_url = "http://localhost:8080"
            session = requests.Session()
            
            # 1. Get login page
            login_url = f"{base_url}/auth/login"
            response = session.get(login_url)
            if response.status_code != 200:
                print(f"❌ Failed to get login page: {response.status_code}")
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
                print("❌ Could not extract CSRF token")
                return False
                
            print(f"✅ Got CSRF token: {csrf_token[:10]}...")
            
            # 2. Login
            login_data = {
                'email': 'testclient_85120b7e@example.com',
                'password': 'password123',
                'csrf_token': csrf_token
            }
            
            response = session.post(login_url, data=login_data, allow_redirects=False)
            if response.status_code not in [302, 303]:
                print(f"❌ Login failed: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False
                
            print("✅ Login successful")
            
            # 3. Access dashboard
            dashboard_url = f"{base_url}/client/dashboard"
            response = session.get(dashboard_url)
            
            print(f"Dashboard response status: {response.status_code}")
            if response.status_code == 500:
                print("❌ Dashboard returned 500 error")
                print(f"Response content: {response.text[:1000]}")
                
                # Try to get more details from the error
                if response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        error_data = response.json()
                        print(f"Error JSON: {error_data}")
                    except:
                        pass
                        
                return False
            elif response.status_code == 200:
                print("✅ Dashboard loaded successfully")
                print(f"Response length: {len(response.text)} characters")
                # Check if it contains expected content
                if 'dashboard' in response.text.lower():
                    print("✅ Dashboard content detected")
                    return True
                else:
                    print("⚠️ Dashboard loaded but no dashboard content found")
                    return False
            else:
                print(f"❌ Unexpected dashboard status: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dashboard_direct()
    print("\n" + "="*50)
    if success:
        print("Test result: ✅ SUCCESS")
    else:
        print("Test result: ❌ FAILED")
    print("="*50)
