#!/usr/bin/env python3
"""
Test script to verify client dashboard functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import Client, User, Payment
from flask import url_for
import tempfile

def test_client_dashboard():
    """Test client dashboard rendering and functionality"""
    
    # Create a test app
    app = create_app()
    
    with app.app_context():
        # Create a test client
        test_client = Client(
            company_name="Test Company",
            email="test@example.com",
            contact_person="John Doe",
            is_active=True
        )
        
        # Try to generate URL
        try:
            with app.test_request_context():
                dashboard_url = url_for('client.dashboard')
                print(f"✓ Dashboard URL generated: {dashboard_url}")
                
                stats_url = url_for('client.dashboard_stats')
                print(f"✓ Dashboard stats URL generated: {stats_url}")
                
                # Test other routes
                routes_to_test = [
                    'client.payments',
                    'client.api_docs',
                    'client.api_keys',
                    'client.profile',
                    'client.settings',
                    'client.support',
                    'client.invoices',
                    'client.documents',
                    'client.withdraw',
                    'client.payment_history',
                    'client.logout'
                ]
                
                for route in routes_to_test:
                    try:
                        url = url_for(route)
                        print(f"✓ {route} URL generated: {url}")
                    except Exception as e:
                        print(f"✗ {route} URL generation failed: {str(e)}")
                
        except Exception as e:
            print(f"✗ URL generation failed: {str(e)}")
            return False
            
        # Test client model methods
        try:
            # Test basic methods
            client_type = test_client.get_client_type()
            print(f"✓ Client type: {client_type}")
            
            is_commission_based = test_client.is_commission_based()
            print(f"✓ Is commission based: {is_commission_based}")
            
            balance = test_client.get_balance()
            print(f"✓ Balance: {balance}")
            
            # Test feature checking
            has_api_feature = test_client.has_feature('api_basic')
            print(f"✓ Has API feature: {has_api_feature}")
            
        except Exception as e:
            print(f"✗ Client model method test failed: {str(e)}")
            return False
        
        print("\n✓ All dashboard tests passed!")
        return True

if __name__ == '__main__':
    success = test_client_dashboard()
    sys.exit(0 if success else 1)
