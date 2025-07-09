"""
Script to create default flat-rate packages in the database.
Run this to initialize or reset the package data.
"""
from app import create_app
from app.models.client_package import create_default_flat_rate_packages

def main():
    app = create_app()
    with app.app_context():
        print("Creating default flat-rate packages...")
        result = create_default_flat_rate_packages()
        if result.get('success'):
            print("Successfully created/updated packages:")
            for pkg in result.get('packages', []):
                print(f"- {pkg}")
        else:
            print("Error creating packages:", result.get('error', 'Unknown error'))

if __name__ == "__main__":
    main()
