"""
Simple test script for package management functionality.
"""
from app import create_app
from app.extensions import db
from app.models.client_package import ClientPackage, ClientType, PackageStatus
from app.models.feature import Feature, PackageFeature

def test_package_system():
    # Create app and context
    app = create_app()
    app_context = app.app_context()
    app_context.push()
    
    try:
        # Create database tables
        db.create_all()
        
        # Test 1: Create a feature
        print("\n=== Testing Feature Creation ===")
        feature = Feature(
            name="Test Feature",
            feature_key="test_feature",
            category="test",
            description="A test feature"
        )
        db.session.add(feature)
        db.session.commit()
        print(f"Created feature: {feature.name} (ID: {feature.id})")
        
        # Test 2: Create a package
        print("\n=== Testing Package Creation ===")
        package = ClientPackage(
            name="Test Package",
            description="A test package",
            client_type=ClientType.FLAT_RATE,
            monthly_price=49.99,
            status=PackageStatus.ACTIVE,
            is_popular=False,
            sort_order=99,
            max_transactions_per_month=500,
            max_api_calls_per_month=5000
        )
        db.session.add(package)
        db.session.commit()
        print(f"Created package: {package.name} (ID: {package.id})")
        
        # Test 3: Assign feature to package
        print("\n=== Testing Feature Assignment ===")
        assignment = PackageFeature(
            package_id=package.id,
            feature_id=feature.id,
            is_included=True,
            limit_value=1000
        )
        db.session.add(assignment)
        db.session.commit()
        print(f"Assigned feature '{feature.name}' to package '{package.name}'")
        
        # Test 4: Query the data
        print("\n=== Verifying Data ===")
        pkg = ClientPackage.query.get(package.id)
        print(f"Package: {pkg.name} (Type: {pkg.client_type.value})")
        print(f"Features ({len(pkg.features)}):")
        for feat in pkg.features:
            print(f"  - {feat.feature.name} (Included: {feat.is_included}, Limit: {feat.limit_value or 'None'})")
        
        # Clean up
        print("\n=== Cleaning Up ===")
        db.session.delete(assignment)
        db.session.delete(package)
        db.session.delete(feature)
        db.session.commit()
        print("Test data cleaned up")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        db.session.rollback()
    finally:
        app_context.pop()

if __name__ == "__main__":
    test_package_system()
