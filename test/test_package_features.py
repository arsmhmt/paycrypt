#!/usr/bin/env python3
"""
Package Feature Access Test Script

This script tests the new centralized package-to-feature mapping system
and client status synchronization functionality.
"""

import os
import sys
import traceback
from decimal import Decimal

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_package_feature_mapping():
    """Test the centralized package-to-feature mapping"""
    print("=" * 60)
    print("🧪 TESTING PACKAGE-TO-FEATURE MAPPING")
    print("=" * 60)
    
    try:
        # Import the configuration
        from app.config.packages import (
            PACKAGE_FEATURES, 
            get_client_features, 
            client_has_feature,
            get_package_display_name,
            sync_client_status_with_package,
            template_helpers
        )
        
        # Test package features
        print("\n1. Package Feature Mappings:")
        for package, features in PACKAGE_FEATURES.items():
            print(f"   📦 {package}: {features}")
        
        # Test feature access functions
        print("\n2. Testing Feature Access Functions:")
        
        # Mock client object for testing
        class MockPackage:
            def __init__(self, slug):
                self.slug = slug
        
        class MockClient:
            def __init__(self, package_slug):
                self.package = MockPackage(package_slug) if package_slug else None
                self.status = None
        
        test_clients = [
            MockClient('starter_commission'),
            MockClient('basic'),
            MockClient('premium'),
            MockClient('professional'),
            MockClient(None)  # No package
        ]
        
        test_features = ['api_basic', 'api_advanced', 'dashboard_analytics', 'wallet_management']
        
        for client in test_clients:
            package_name = client.package.slug if client.package else 'No Package'
            print(f"\n   👤 Client with {package_name}:")
            
            for feature in test_features:
                has_access = client_has_feature(client, feature)
                status = "✅ HAS" if has_access else "❌ NO"
                print(f"      {status} access to {feature}")
        
        # Test template helpers
        print("\n3. Testing Template Helpers:")
        helpers = template_helpers()
        print(f"   Available helpers: {list(helpers.keys())}")
        
        # Test display names
        print("\n4. Testing Display Names:")
        for package_slug in PACKAGE_FEATURES.keys():
            display_name = get_package_display_name(package_slug)
            print(f"   📦 {package_slug} → {display_name}")
        
        print("\n✅ Package feature mapping tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Package feature mapping test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_client_model_integration():
    """Test Client model integration with feature access"""
    print("\n" + "=" * 60)
    print("🧪 TESTING CLIENT MODEL INTEGRATION")
    print("=" * 60)
    
    try:
        from app import create_app
        from app.models.client import Client
        from app.models.client_package import ClientPackage
        from app.extensions import db
        
        app = create_app()
        
        with app.app_context():
            # Test existing clients
            print("\n1. Testing Existing Clients:")
            clients = Client.query.limit(3).all()
            
            for client in clients:
                print(f"\n   👤 Client: {client.company_name} (ID: {client.id})")
                print(f"      Package: {client.package.slug if client.package else 'None'}")
                
                # Test feature access via mixin
                test_features = ['api_basic', 'dashboard_analytics', 'wallet_management']
                for feature in test_features:
                    has_access = client.has_feature(feature)
                    status = "✅" if has_access else "❌"
                    print(f"      {status} {feature}")
                
                # Test getting all features
                all_features = client.get_features()
                print(f"      All features: {all_features}")
                
                # Test status display
                status_display = client.get_status_display()
                print(f"      Status display: {status_display}")
        
        print("\n2. Testing Status Synchronization:")
        with app.app_context():
            # Find a client with a package
            client = Client.query.filter(Client.package_id.isnot(None)).first()
            if client:
                print(f"   👤 Testing with client: {client.company_name}")
                old_status = client.status
                print(f"      Current status: {old_status}")
                
                # Sync status
                new_status = client.sync_status()
                print(f"      Synced status: {new_status}")
                
                if client.package:
                    expected_status = client.package.slug
                    print(f"      Expected status: {expected_status}")
                    
                    if new_status == expected_status:
                        print("      ✅ Status sync working correctly!")
                    else:
                        print("      ⚠️ Status sync mismatch")
            else:
                print("   ⚠️ No clients with packages found for testing")
        
        print("\n✅ Client model integration tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Client model integration test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_template_context():
    """Test that template helpers are available in app context"""
    print("\n" + "=" * 60)
    print("🧪 TESTING TEMPLATE CONTEXT")
    print("=" * 60)
    
    try:
        from app import create_app
        from flask import render_template_string
        
        app = create_app()
        
        with app.app_context():
            # Test template context
            test_template = """
            Package Features Available: {{ PACKAGE_FEATURES is defined }}
            Feature Descriptions Available: {{ FEATURE_DESCRIPTIONS is defined }}
            Client Has Feature Function: {{ client_has_feature is defined }}
            Get Client Features Function: {{ get_client_features is defined }}
            Package Display Names: {{ PACKAGE_DISPLAY_NAMES is defined }}
            """
            
            with app.test_request_context():
                rendered = render_template_string(test_template)
                print("\n   Template Context Test Results:")
                for line in rendered.strip().split('\n'):
                    if line.strip():
                        parts = line.strip().split(': ')
                        if len(parts) == 2:
                            name, available = parts
                            status = "✅" if available == "True" else "❌"
                            print(f"      {status} {name}")
        
        print("\n✅ Template context tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Template context test failed: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run all package feature tests"""
    print("🚀 Starting Package Feature Access Tests...")
    
    results = []
    
    # Run all tests
    results.append(test_package_feature_mapping())
    results.append(test_client_model_integration())
    results.append(test_template_context())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    
    if all(results):
        print("\n🎉 All package feature tests passed!")
        return True
    else:
        print("\n⚠️ Some package feature tests failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
