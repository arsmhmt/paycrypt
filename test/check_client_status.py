#!/usr/bin/env python3
"""
Check client status and package features
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

try:
    from app import create_app
    from app.models import Client
    from app.models.client_package import ClientPackage
    from app.config.packages import PACKAGE_FEATURES, FEATURE_DESCRIPTIONS
    
    print("✅ Creating Flask app...")
    app = create_app()
    
    with app.app_context():
        print("✅ App context created successfully")
        
        # Get all packages
        packages = ClientPackage.query.all()
        print(f'\n📦 All Available Packages:')
        for package in packages:
            features = PACKAGE_FEATURES.get(package.slug, [])
            has_features = "✅" if features else "❌"
            print(f'  {has_features} {package.name} (slug: "{package.slug}") - Features: {features}')
        
        print(f'\n🔧 Package Features Configuration:')
        for slug, features in PACKAGE_FEATURES.items():
            print(f'  "{slug}": {features}')
        
        # Get a client (smartbetslip)
        client = Client.query.filter_by(username='smartbetslip').first()
        if client:
            print(f'\n📊 Client Analysis: {client.company_name} ({client.username})')
            print(f'Package: {client.package.name if client.package else "No package"}')
            print(f'Package Slug: {client.package.slug if client.package else "No package"}')
            print(f'Status: {getattr(client, "status", "No status field")}')
            print(f'Features Override: {getattr(client, "features_override", [])}')
            
            if client.package:
                package_features = PACKAGE_FEATURES.get(client.package.slug, [])
                print(f'Package Features: {package_features}')
                
                if hasattr(client, 'get_features'):
                    print(f'Client Features (combined): {client.get_features()}')
                else:
                    print('Client Features: Method not available')
            
            # Test specific features mentioned in templates
            test_features = ['api_basic', 'api_advanced', 'dashboard_analytics', 'dashboard_realtime', 'wallet_management', 'support_priority']
            print(f'\n🔍 Feature Access Check:')
            for feature in test_features:
                if hasattr(client, 'has_feature'):
                    has_access = client.has_feature(feature)
                    status_icon = "✅" if has_access else "❌"
                    print(f'  {status_icon} {feature}: {has_access}')
                else:
                    print(f'  ❓ {feature}: Method not available')
        else:
            print('❌ Client "smartbetslip" not found')
            
        # List all clients
        print(f'\n📋 All clients:')
        clients = Client.query.all()
        for c in clients:
            package_name = c.package.name if c.package else "None"
            print(f'  - {c.username}: {c.company_name} (Package: {package_name})')
                
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
