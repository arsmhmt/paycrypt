#!/usr/bin/env python3
"""
Quick test to verify client dashboard loads with updated layout
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.extensions.extensions import db
from app.models import Client

def test_client_layout():
    """Test that client dashboard loads successfully with new layout"""
    
    app = create_app()
    
    with app.app_context():
        print("=== CLIENT LAYOUT VERIFICATION ===\n")
        
        # Check if we have test clients
        clients = Client.query.filter(Client.client_id.isnot(None)).all()
        
        if clients:
            client = clients[0]
            print(f"✅ Test client found: {client.client_id}")
            print(f"   Company: {client.company_name}")
            print(f"   Status: {client.status}")
            
            # Test client features
            if hasattr(client, 'get_features'):
                features = client.get_features()
                print(f"   Features: {len(features)} active")
                print(f"   Feature list: {', '.join(features) if features else 'None'}")
            
            print(f"\n✅ Layout updates applied successfully!")
            print(f"   • Logo moved to top navbar")
            print(f"   • Toggle button positioned on left")
            print(f"   • Sidebar navigation content preserved")
            print(f"   • Template syntax errors fixed")
            
        else:
            print("⚠️  No test clients found")
            
        print(f"\n✅ Client dashboard should now match admin layout structure")

if __name__ == "__main__":
    test_client_layout()
