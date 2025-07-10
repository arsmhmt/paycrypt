import sys
import os

print("Testing Package Service...")

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

try:
    print("Creating Flask app...")
    from app import create_app
    app = create_app()
    
    print("\nCreating database tables...")
    from app.extensions import db
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")
        
        # Test package service
        print("\nTesting PackageService...")
        from app.services.package_service import PackageService
        
        # Initialize default packages
        print("Initializing default packages...")
        success = PackageService.initialize_default_packages()
        print(f"Package initialization {'succeeded' if success else 'failed'}")
        
        # List packages
        print("\nListing packages...")
        from app.models.client_package import ClientPackage
        packages = ClientPackage.query.all()
        print(f"Found {len(packages)} packages")
        
        for pkg in packages:
            print(f"\nPackage: {pkg.name} ({pkg.client_type.value})")
            print(f"Description: {pkg.description}")
            
            # Get package features
            features = PackageService.get_package_features(pkg.id)
            print(f"Features ({len(features)}):")
            for assignment, feature in features:
                print(f"  - {feature.name} ({feature.feature_key})")

        print("\nTest completed successfully!")
        
except Exception as e:
    print(f"\nError: {str(e)}")
    import traceback
    traceback.print_exc()
