"""
Test script for package management functionality.
Run with: python test_package_management.py
"""
from app import create_app
from app.extensions import db
from app.models.client_package import ClientPackage, ClientType, PackageStatus, PackageFeature
from app.models.feature import Feature
from app.services.package_service import PackageService

def test_package_management():
    # Create a test app
    app = create_app()
    
    with app.app_context():
        # Initialize the database
        db.create_all()
        
        # Test 1: Initialize default packages
        print("\n=== Testing Package Initialization ===")
        success = PackageService.initialize_default_packages()
        print(f"Package initialization {'succeeded' if success else 'failed'}")
        
        # Test 2: List packages
        print("\n=== Listing Packages ===")
        packages = db.session.query(ClientPackage).order_by(ClientPackage.sort_order).all()
        print(f"Found {len(packages)} packages:")
        
        for pkg in packages:
            print(f"\n{pkg.name} ({pkg.client_type.value}): {pkg.description}")
            print(f"  Status: {pkg.status.value}")
            print(f"  Popular: {'Yes' if pkg.is_popular else 'No'}")
            
            if pkg.client_type == ClientType.FLAT_RATE:
                print(f"  Monthly Price: ${pkg.monthly_price}")
                print(f"  Annual Price: ${pkg.annual_price} (10% discount)")
            else:
                print(f"  Commission Rate: {float(pkg.commission_rate)*100}%")
                
            print(f"  Max Transactions/Month: {pkg.max_transactions_per_month or 'Unlimited'}")
            print(f"  Max API Calls/Month: {pkg.max_api_calls_per_month or 'Unlimited'}")
            
            # Get package features
            features = PackageService.get_package_features(pkg.id)
            print(f"  Features ({len(features)}):")
            for assignment, feature in features:
                limit_str = f" (limit: {assignment.limit_value})" if assignment.limit_value else ""
                print(f"    - {feature.name} ({feature.feature_key}){limit_str}")
        
        # Test 3: Create a new package
        print("\n=== Testing Package Creation ===")
        new_package = PackageService.create_package(
            name="Test Package",
            description="A test package",
            client_type=ClientType.FLAT_RATE,
            monthly_price=49.99,
            is_popular=False,
            max_transactions_per_month=500,
            max_api_calls_per_month=5000
        )
        
        if new_package:
            db.session.add(new_package)
            db.session.commit()
            print(f"Created package: {new_package.name} (ID: {new_package.id})")
            
            # Test 4: Add a feature to the package
            print("\n=== Testing Feature Assignment ===")
            assignment = PackageService.assign_feature_to_package(
                package_id=new_package.id,
                feature_key='api_basic',
                is_included=True,
                limit_value=1000
            )
            
            if assignment:
                db.session.add(assignment)
                db.session.commit()
                print(f"Assigned feature 'api_basic' to package '{new_package.name}'")
            else:
                print("Failed to assign feature to package")
        else:
            print("Failed to create test package")
        
        # Clean up
        print("\n=== Cleaning Up ===")
        if 'new_package' in locals() and new_package:
            db.session.delete(new_package)
            db.session.commit()
            print("Cleaned up test package")
        
        print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_package_management()
