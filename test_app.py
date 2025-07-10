from app import create_app
from app.extensions import db
from app.models.client_package import ClientPackage, ClientType, PackageStatus
from app.models.feature import Feature, PackageFeature

app = create_app()

@app.route('/test-package')
def test_package():
    with app.app_context():
        try:
            # Create a test feature
            feature = Feature(
                name="Web Test Feature",
                feature_key="web_test_feature",
                category="test",
                description="A test feature created via web"
            )
            db.session.add(feature)
            
            # Create a test package
            package = ClientPackage(
                name="Web Test Package",
                description="A test package created via web",
                client_type=ClientType.FLAT_RATE,
                monthly_price=99.99,
                status=PackageStatus.ACTIVE,
                is_popular=True,
                sort_order=100
            )
            db.session.add(package)
            db.session.flush()  # Get the package ID
            
            # Assign feature to package
            assignment = PackageFeature(
                package_id=package.id,
                feature_id=feature.id,
                is_included=True
            )
            db.session.add(assignment)
            
            # Commit all changes
            db.session.commit()
            
            # Return success message
            return f"Successfully created package '{package.name}' with feature '{feature.name}'"
            
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}", 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
