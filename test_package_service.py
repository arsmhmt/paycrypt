from app import create_app
from app.extensions import db
from app.models.client_package import ClientPackage, ClientType, PackageStatus
from app.models.feature import Feature, PackageFeature
from app.services.package_service import PackageService

def test_package_service():
    # Create app and context
    app = create_app()
    app_context = app.app_context()
    app_context.push()
    
    try:
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
        
        print("\n=== Test completed successfully ===")
        
    except Exception as e:
        print(f"\n!!! Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        app_context.pop()

if __name__ == "__main__":
    test_package_service()
