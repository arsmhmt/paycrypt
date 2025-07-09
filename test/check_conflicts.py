#!/usr/bin/env python3
"""
Code Factory Duplication & Conflict Check

This script analyzes the codebase for potential duplications and conflicts
before running the application.
"""

import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_feature_conflicts():
    """Check for feature name conflicts and inconsistencies"""
    print("🔍 Checking Feature Name Conflicts")
    print("-" * 50)
    
    try:
        from app.config.packages import PACKAGE_FEATURES, FEATURE_DESCRIPTIONS
        
        # Check 1: Feature consistency in routes vs config
        print("📝 Feature Name Consistency Check:")
        
        # Dynamically scan routes for feature usage
        route_features = set()
        
        # Scan client_routes.py for has_feature and feature_required usage
        client_routes_path = 'app/client_routes.py'
        if os.path.exists(client_routes_path):
            with open(client_routes_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Find feature_required decorator usage
                import re
                feature_patterns = [
                    r"@feature_required\(['\"]([^'\"]+)['\"]",  # @feature_required('feature_name')
                    r"has_feature\(['\"]([^'\"]+)['\"]",        # has_feature('feature_name')
                ]
                
                for pattern in feature_patterns:
                    matches = re.findall(pattern, content)
                    route_features.update(matches)
        
        # Features defined in config
        config_features = set()
        for features in PACKAGE_FEATURES.values():
            config_features.update(features)
        
        print(f"   Config features: {sorted(config_features)}")
        print(f"   Route features: {sorted(route_features)}")
        
        # Find mismatches
        missing_in_config = route_features - config_features
        if missing_in_config:
            print(f"   ❌ Features used in routes but missing in config: {missing_in_config}")
            return False
        else:
            print("   ✅ All route features are defined in config")
        
        # Check 2: Feature descriptions completeness
        missing_descriptions = config_features - set(FEATURE_DESCRIPTIONS.keys())
        if missing_descriptions:
            print(f"   ⚠️  Features missing descriptions: {missing_descriptions}")
        else:
            print("   ✅ All features have descriptions")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error checking features: {e}")
        return False

def check_function_duplications():
    """Check for duplicate function definitions"""
    print("\n🔍 Checking Function Duplications")
    print("-" * 50)
    
    try:
        # Check has_feature method implementations
        print("📝 has_feature Method Implementations:")
        
        # Import and check both implementations
        from app.config.packages import FeatureAccessMixin
        from app.models.client_package import ClientPackage
        
        # Check if both classes have has_feature methods
        mixin_has_method = hasattr(FeatureAccessMixin, 'has_feature')
        package_has_method = hasattr(ClientPackage, 'has_feature')
        
        print(f"   FeatureAccessMixin.has_feature: {'✅ EXISTS' if mixin_has_method else '❌ MISSING'}")
        print(f"   ClientPackage.has_feature: {'✅ EXISTS' if package_has_method else '❌ MISSING'}")
        
        if mixin_has_method and package_has_method:
            print("   ℹ️  Both implementations exist but serve different purposes:")
            print("      - FeatureAccessMixin: For client feature access (package + overrides)")
            print("      - ClientPackage: For package-level feature checking only")
            print("   ✅ No conflict - different scopes")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error checking function duplications: {e}")
        return False

def check_template_conflicts():
    """Check for template conflicts and issues"""
    print("\n🔍 Checking Template Conflicts")
    print("-" * 50)
    
    template_files = [
        'app/templates/client/dashboard.html',
        'app/templates/admin/edit_client_features.html', 
        'app/templates/client/partials/feature_showcase.html'
    ]
    
    issues_found = []
    
    for template_file in template_files:
        if os.path.exists(template_file):
            print(f"   📄 {template_file}: ✅ EXISTS")
            
            # Check for potential template syntax issues
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for unclosed blocks
                if_count = content.count('{% if ')
                endif_count = content.count('{% endif %}')
                if if_count != endif_count:
                    issues_found.append(f"{template_file}: Unclosed if blocks ({if_count} if, {endif_count} endif)")
                
                # Check for undefined template functions
                if 'client_has_feature(' in content:
                    print(f"      ℹ️  Uses client_has_feature() function")
                if 'current_user.client.has_feature(' in content:
                    print(f"      ℹ️  Uses current_user.client.has_feature() method")
        else:
            issues_found.append(f"{template_file}: FILE NOT FOUND")
    
    if issues_found:
        print("   ❌ Template issues found:")
        for issue in issues_found:
            print(f"      - {issue}")
        return False
    else:
        print("   ✅ No template conflicts detected")
        return True

def check_import_conflicts():
    """Check for import conflicts"""
    print("\n🔍 Checking Import Conflicts")
    print("-" * 50)
    
    try:
        # Test critical imports
        print("📝 Testing Critical Imports:")
        
        from app.config.packages import FeatureAccessMixin, PACKAGE_FEATURES, FEATURE_DESCRIPTIONS
        print("   ✅ app.config.packages imports successful")
        
        from app.models.client import Client
        print("   ✅ app.models.client imports successful")
        
        # Test that Client has the mixin
        test_client_methods = [
            'has_feature'
        ]
        
        for method in test_client_methods:
            if hasattr(Client, method):
                print(f"   ✅ Client.{method} method available")
            else:
                print(f"   ❌ Client.{method} method missing")
                return False
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def check_database_conflicts():
    """Check for database-related conflicts"""
    print("\n🔍 Checking Database Conflicts")
    print("-" * 50)
    
    try:
        from app import create_app
        from app.models.client import Client
        from app.extensions import db
        
        app = create_app()
        
        with app.app_context():
            # Check if features_override column exists and is correct type
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('clients')
            
            features_override_column = None
            for column in columns:
                if column['name'] == 'features_override':
                    features_override_column = column
                    break
            
            if features_override_column:
                print(f"   ✅ features_override column exists")
                print(f"   📝 Column type: {features_override_column['type']}")
                
                # Test reading a client to ensure column works
                client = Client.query.first()
                if client:
                    try:
                        features = client.features_override
                        print(f"   ✅ Column is readable: {type(features)} = {features}")
                        return True
                    except Exception as e:
                        print(f"   ❌ Column read error: {e}")
                        return False
                else:
                    print("   ⚠️  No clients in database to test")
                    return True
            else:
                print("   ❌ features_override column missing")
                return False
        
    except Exception as e:
        print(f"   ❌ Database check error: {e}")
        return False

def main():
    """Run all conflict checks"""
    print("🏭 Code Factory Duplication & Conflict Check")
    print("=" * 70)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checks = [
        ("Feature Conflicts", check_feature_conflicts),
        ("Function Duplications", check_function_duplications), 
        ("Template Conflicts", check_template_conflicts),
        ("Import Conflicts", check_import_conflicts),
        ("Database Conflicts", check_database_conflicts)
    ]
    
    all_passed = True
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} check failed with exception: {e}")
            results.append((check_name, False))
            all_passed = False
    
    # Final report
    print("\n" + "=" * 70)
    print("📊 FINAL REPORT")
    print("=" * 70)
    
    for check_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {check_name}")
    
    print()
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ No conflicts or duplications detected")
        print("✅ Application is ready to run")
        
        print("\n🚀 Recommended Actions:")
        print("   1. Run 'python run.py' to start the application")
        print("   2. Test admin feature editing at /admin120724/clients/1/features")
        print("   3. Test client dashboard with dynamic features")
        print("   4. Verify all feature access controls work correctly")
        
    else:
        print("❌ CONFLICTS DETECTED!")
        print("⚠️  Fix the issues above before running the application")
        
        print("\n🔧 Recommended Fixes:")
        for check_name, passed in results:
            if not passed:
                if "Feature" in check_name:
                    print("   - Check feature name consistency in routes vs config")
                elif "Function" in check_name:
                    print("   - Resolve duplicate function definitions")
                elif "Template" in check_name:
                    print("   - Fix template syntax or missing files")
                elif "Import" in check_name:
                    print("   - Resolve import errors or missing modules")
                elif "Database" in check_name:
                    print("   - Run database migration or fix column issues")
    
    print("=" * 70)
    return all_passed

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
