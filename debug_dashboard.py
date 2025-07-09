#!/usr/bin/env python
"""
Debug dashboard access to identify the error
"""

from app import create_app
from app.models import Client, User
from app.extensions.extensions import db
from flask_login import login_user
import traceback

def debug_dashboard():
    """Debug dashboard access"""
    app = create_app()
    
    with app.app_context():
        # Get our test client
        client = Client.query.filter_by(email='testclient_85120b7e@example.com').first()
        if not client:
            print("❌ Test client not found")
            return False
            
        print(f"✅ Found client: {client.company_name} (ID: {client.id})")
        
        # Get the user associated with this client
        user = User.query.filter_by(id=client.user_id).first()
        if not user:
            print("❌ No user found for this client")
            return False
            
        print(f"✅ Found user: {user.username} (ID: {user.id})")
        
        # Simulate logged in state
        with app.test_request_context('/client/dashboard'):
            try:
                # Login the user for the session
                login_user(user)
                
                # Now test the dashboard function directly
                from app.client_routes import dashboard
                
                print("🔍 Testing dashboard function...")
                result = dashboard(client=client)
                print("✅ Dashboard function executed successfully")
                print(f"   Result type: {type(result)}")
                return True
                
            except Exception as e:
                print(f"❌ Error in dashboard function: {str(e)}")
                print("Full traceback:")
                traceback.print_exc()
                return False

if __name__ == "__main__":
    success = debug_dashboard()
    print(f"\nResult: {'✅ SUCCESS' if success else '❌ FAILED'}")
