#!/usr/bin/env python3
"""
Quick test script to check if client routes are working properly
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

try:
    from flask import url_for
    from app import create_app
    
    print("✅ Creating Flask app...")
    app = create_app()
    
    with app.test_request_context():
        print("✅ Test request context created successfully")
        
        # Test client routes
        client_routes = [
            'client.dashboard',
            'client.payments', 
            'client.withdraw',
            'client.withdrawal_history',
            'client.profile',
            'client.api_docs',
            'client.api_keys'
        ]
        
        print("\n🔍 Testing client routes:")
        for route in client_routes:
            try:
                url = url_for(route)
                print(f"  ✅ {route}: {url}")
            except Exception as e:
                print(f"  ❌ {route}: {e}")
        
        print("\n🔍 Testing admin routes:")
        admin_routes = [
            'admin.admin_dashboard',
            'admin.payments_list',
            'admin.withdrawals_list'
        ]
        
        for route in admin_routes:
            try:
                url = url_for(route)
                print(f"  ✅ {route}: {url}")
            except Exception as e:
                print(f"  ❌ {route}: {e}")
                
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
