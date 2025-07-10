print("Testing Python environment...")

# Test basic imports
try:
    import flask
    print("Flask is installed")
except ImportError:
    print("Flask is NOT installed")

# Test database connection
try:
    from app.extensions import db
    print("Database extension imported successfully")
except Exception as e:
    print(f"Error importing database: {str(e)}")

# Test package service
try:
    from app.services.package_service import PackageService
    print("PackageService imported successfully")
except Exception as e:
    print(f"Error importing PackageService: {str(e)}")

print("Test completed")
