#!/usr/bin/env python3
"""
Test Client API Key Management Implementation

This script tests the client-side API key management functionality
that was implemented to complete the admin panel client management system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all necessary imports work correctly"""
    print("Testing imports...")
    
    try:
        from app.models.api_key import ClientApiKey, ApiKeyUsageLog
        print("✓ API key models imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import API key models: {e}")
        return False
    
    try:
        from app.forms.client_forms import ClientApiKeyForm, ClientApiKeyEditForm, ClientApiKeyRevokeForm
        print("✓ Client API key forms imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import client API key forms: {e}")
        return False
    
    try:
        from app.models.audit import AuditActionType
        print("✓ Audit action types imported successfully")
        
        # Test that our new audit action types exist
        audit_types = [
            AuditActionType.API_KEY_CREATED,
            AuditActionType.API_KEY_UPDATED,
            AuditActionType.API_KEY_REVOKED,
            AuditActionType.API_KEY_REGENERATED
        ]
        print("✓ All API key audit action types are available")
    except (ImportError, AttributeError) as e:
        print(f"✗ Failed to import audit action types: {e}")
        return False
    
    return True

def test_api_key_model():
    """Test ClientApiKey model functionality"""
    print("\nTesting ClientApiKey model...")
    
    try:
        from app.models.api_key import ClientApiKey
        
        # Test key generation
        key = ClientApiKey.generate_key()
        assert len(key) == 64, f"Generated key should be 64 characters, got {len(key)}"
        print("✓ API key generation works")
        
        # Test key hashing
        key_hash = ClientApiKey.hash_key(key)
        assert key_hash != key, "Hashed key should be different from original"
        print("✓ API key hashing works")
        
        # Test create_for_client method exists
        assert hasattr(ClientApiKey, 'create_for_client'), "create_for_client method should exist"
        print("✓ create_for_client method exists")
        
    except Exception as e:
        print(f"✗ API key model test failed: {e}")
        return False
    
    return True

def test_routes_structure():
    """Test that the route structure looks correct"""
    print("\nTesting route structure...")
    
    # This is a basic test to check if the routes file has the expected structure
    try:
        with open('app/client_routes.py', 'r') as f:
            content = f.read()
        
        required_routes = [
            '@client_bp.route(\'/api-keys\'',
            '@client_bp.route(\'/api-keys/create\'',
            '@client_bp.route(\'/api-keys/<int:key_id>\'',
            '@client_bp.route(\'/api-keys/<int:key_id>/edit\'',
            '@client_bp.route(\'/api-keys/<int:key_id>/revoke\'',
            '@client_bp.route(\'/api-keys/<int:key_id>/regenerate\''
        ]
        
        for route in required_routes:
            if route not in content:
                print(f"✗ Missing route: {route}")
                return False
        
        print("✓ All expected API key routes are present")
        
    except Exception as e:
        print(f"✗ Route structure test failed: {e}")
        return False
    
    return True

def test_template_files():
    """Test that all template files were created"""
    print("\nTesting template files...")
    
    required_templates = [
        'app/templates/client/api_keys.html',
        'app/templates/client/create_api_key.html',
        'app/templates/client/api_key_details.html',
        'app/templates/client/edit_api_key.html'
    ]
    
    for template in required_templates:
        if not os.path.exists(template):
            print(f"✗ Missing template: {template}")
            return False
        else:
            # Check if template has basic structure
            try:
                with open(template, 'r') as f:
                    content = f.read()
                if '{% extends "client/base.html" %}' not in content:
                    print(f"✗ Template {template} doesn't extend base template")
                    return False
            except Exception as e:
                print(f"✗ Error reading template {template}: {e}")
                return False
    
    print("✓ All required templates exist and have basic structure")
    return True

def test_dashboard_integration():
    """Test that dashboard integration was added"""
    print("\nTesting dashboard integration...")
    
    try:
        with open('app/templates/client/dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'url_for(\'client.api_keys\')' not in content:
            print("✗ API keys link not found in dashboard")
            return False
        
        if 'has_feature(\'api_basic\')' not in content:
            print("✗ Feature check for api_basic not found in dashboard")
            return False
        
        print("✓ Dashboard integration looks correct")
        
    except Exception as e:
        print(f"✗ Dashboard integration test failed: {e}")
        return False
    
    return True

def test_navigation_integration():
    """Test that navigation integration was added"""
    print("\nTesting navigation integration...")
    
    try:
        with open('app/templates/client/base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'client.api_keys' not in content:
            print("✗ API keys navigation not found in base template")
            return False
        
        if 'fas fa-key' not in content:
            print("✗ API key icon not found in navigation")
            return False
        
        print("✓ Navigation integration looks correct")
        
    except Exception as e:
        print(f"✗ Navigation integration test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("TESTING CLIENT API KEY MANAGEMENT IMPLEMENTATION")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("API Key Model Tests", test_api_key_model),
        ("Route Structure Tests", test_routes_structure),
        ("Template File Tests", test_template_files),
        ("Dashboard Integration Tests", test_dashboard_integration),
        ("Navigation Integration Tests", test_navigation_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Client API key management implementation is complete.")
        print("\nNext steps:")
        print("1. Test the functionality in a browser")
        print("2. Create some test API keys")
        print("3. Verify the admin panel can also manage client API keys")
        print("4. Test the API endpoints with generated keys")
    else:
        print("❌ Some tests failed. Please review the implementation.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
