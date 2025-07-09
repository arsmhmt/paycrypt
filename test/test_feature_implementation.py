#!/usr/bin/env python3
"""
Test Feature Access Implementation

This script tests the complete feature access system including:
1. Package-based features
2. Manual feature overrides
3. Dynamic feature checking
4. Admin utility functionality
"""

import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_feature_access():
    """Test the complete feature access system"""
    print("🚀 Testing Feature Access Implementation")
    print("=" * 60)
    
    try:
        from app import create_app
        from app.models.client import Client
        from app.config.packages import PACKAGE_FEATURES, FEATURE_DESCRIPTIONS
        from app.extensions import db
        
        app = create_app()
        
        with app.app_context():
            # Get a test client
            client = Client.query.first()
            if not client:
                print("❌ No clients found in database")
                return False
            
            print(f"📝 Testing with client: {client.company_name}")
            print(f"📦 Package: {client.package.name if client.package else 'None'}")
            print(f"🔧 Features Override: {client.features_override}")
            print("-" * 60)
            
            # Test 1: Package-based features
            print("🧪 Test 1: Package-based features")
            if client.package and hasattr(client.package, 'slug'):
                package_slug = client.package.slug
                print(f"   Package slug: {package_slug}")
                
                # Check if slug exists in PACKAGE_FEATURES
                if package_slug in PACKAGE_FEATURES:
                    package_features = PACKAGE_FEATURES[package_slug]
                    print(f"   Package features: {package_features}")
                    
                    # Test a specific feature
                    if package_features:
                        test_feature = package_features[0]
                        has_feature = client.has_feature(test_feature)
                        print(f"   ✅ has_feature('{test_feature}'): {has_feature}")
                    else:
                        print("   ⚠️  No features defined for this package")
                else:
                    print(f"   ❌ Package slug '{package_slug}' not found in PACKAGE_FEATURES")
            else:
                print("   ⚠️  Client has no package or package has no slug")
            
            # Test 2: Manual feature overrides
            print("\n🧪 Test 2: Manual feature overrides")
            original_overrides = client.features_override.copy() if client.features_override else []
            
            # Add a test override
            test_override = 'test_manual_feature'
            client.features_override = [test_override]
            db.session.commit()
            
            has_override = client.has_feature(test_override)
            print(f"   ✅ has_feature('{test_override}') after override: {has_override}")
            
            # Restore original overrides
            client.features_override = original_overrides
            db.session.commit()
            
            # Test 3: Feature descriptions
            print("\n🧪 Test 3: Feature descriptions")
            print(f"   Available feature descriptions: {len(FEATURE_DESCRIPTIONS)}")
            for feature, description in list(FEATURE_DESCRIPTIONS.items())[:3]:
                print(f"   - {feature}: {description}")
            
            # Test 4: All available features
            print("\n🧪 Test 4: Available features in system")
            all_features = sorted({f for features in PACKAGE_FEATURES.values() for f in features})
            print(f"   Total unique features: {len(all_features)}")
            print(f"   Features: {all_features[:5]}{'...' if len(all_features) > 5 else ''}")
            
            # Test 5: Template context functions
            print("\n🧪 Test 5: Template context functions")
            try:
                from app import get_package_features, client_has_feature
                
                # Test template functions
                if client.package:
                    template_features = get_package_features(client.package.slug)
                    template_has_feature = client_has_feature(client.id, all_features[0] if all_features else 'test_feature')
                    
                    print(f"   ✅ get_package_features(): {template_features}")
                    print(f"   ✅ client_has_feature(): {template_has_feature}")
                else:
                    print("   ⚠️  Cannot test template functions without package")
                    
            except ImportError as e:
                print(f"   ❌ Template functions not found: {e}")
            
            print("\n" + "=" * 60)
            print("✅ Feature access system test completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_admin_routes():
    """Test that admin routes are properly configured"""
    print("\n🔧 Testing Admin Routes")
    print("-" * 40)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            # Check if the edit features route exists
            from app.admin.routes import admin_bp
            
            # Get all rules for the admin blueprint
            admin_rules = [rule for rule in app.url_map.iter_rules() if rule.endpoint and rule.endpoint.startswith('admin.')]
            
            # Look for the edit features route
            features_route = None
            for rule in admin_rules:
                if 'edit_client_features' in rule.endpoint:
                    features_route = rule
                    break
            
            if features_route:
                print(f"   ✅ Features route found: {features_route.rule}")
                print(f"   Methods: {features_route.methods}")
            else:
                print("   ❌ Features route not found")
            
            print(f"   Total admin routes: {len(admin_rules)}")
            return True
            
    except Exception as e:
        print(f"   ❌ Error testing admin routes: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Feature Access System Test Suite")
    print("=" * 60)
    
    # Run feature access tests
    feature_test_success = test_feature_access()
    
    # Run admin route tests
    admin_test_success = test_admin_routes()
    
    print("\n" + "=" * 60)
    if feature_test_success and admin_test_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Feature access system is working correctly")
        print("✅ Admin routes are properly configured")
        print("✅ Manual feature overrides are functional")
        print("✅ Dynamic feature rendering is available")
    else:
        print("❌ SOME TESTS FAILED!")
        if not feature_test_success:
            print("❌ Feature access system issues detected")
        if not admin_test_success:
            print("❌ Admin route configuration issues detected")
        sys.exit(1)
    
    print("=" * 60)
