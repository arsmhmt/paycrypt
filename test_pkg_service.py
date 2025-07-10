"""
Test script for package service functionality.
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

def test_package_service():
    print("Testing Package Service...")
    
    try:
        # Import required modules
        from app import create_app
        from app.extensions import db
        from app.models.client_package import ClientPackage, ClientType, PackageStatus
        from app.models.feature import Feature, PackageFeature
        from app.services.package_service import PackageService
        
        # Create app and context
        app = create_app()
        app_context = app.app_context()
        app_context.push()
        
        # Create database tables
        print("Creating database tables...")
        db.create_all()
        
        # Test 1: Initialize default packages
        print("\n=== Testing Package Initialization ===")
        success = PackageService.initialize_default_packages()
        print(f"Package initialization {'succeeded' if success else 'failed'}")
        
        # Test 2: List packages
        print("\n=== Listing Packages ===")
        packages = ClientPackage.query.order_by(ClientPackage.sort_order).all()
        print(f"Found {len(packages)} packages:")
        
        for pkg in packages:
            print(f"\nPackage: {pkg.name} ({pkg.client_type.value})")
            print(f"Description: {pkg.description}")
            print(f"Status: {pkg.status.value}")
            
            if pkg.client_type == ClientType.FLAT_RATE:
                print(f"Monthly Price: ${pkg.monthly_price}")
                print(f"Annual Price: ${pkg.annual_price}")
            else:
                print(f"Commission Rate: {float(pkg.commission_rate)*100}%")
            
            # Get package features
            features = PackageService.get_package_features(pkg.id)
            print(f"Features ({len(features)}):")
            for assignment, feature in features:
                limit_str = f" (limit: {assignment.limit_value}" if assignment.limit_value else ""
                print(f"  - {feature.name} ({feature.feature_key}){limit_str}")
        
        print("\n=== Test completed successfully! ===")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'app_context' in locals():
            app_context.pop()

if __name__ == "__main__":
    test_package_service()
