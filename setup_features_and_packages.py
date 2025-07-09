#!/usr/bin/env python3
"""
Setup basic features and package assignments for clients
"""
from app import create_app
from app.models.client import Client
from app.models.client_package import Feature, ClientPackage, PackageFeature
from app.extensions import db

app = create_app()
with app.app_context():
    print("=== SETTING UP FEATURES ===")
    
    # Create basic features if they don't exist
    features_to_create = [
        {'name': 'Basic API Access', 'feature_key': 'api_basic', 'description': 'Basic API endpoints', 'category': 'api'},
        {'name': 'Advanced API Access', 'feature_key': 'api_advanced', 'description': 'Advanced API endpoints and features', 'category': 'api', 'is_premium': True},
        {'name': 'Dashboard Analytics', 'feature_key': 'dashboard_analytics', 'description': 'Advanced analytics and reporting', 'category': 'dashboard', 'is_premium': True},
        {'name': 'Real-time Dashboard', 'feature_key': 'dashboard_realtime', 'description': 'Real-time updates and live data', 'category': 'dashboard', 'is_premium': True},
        {'name': 'Wallet Management', 'feature_key': 'wallet_management', 'description': 'Multi-wallet support and management', 'category': 'wallet', 'is_premium': True},
        {'name': 'Priority Support', 'feature_key': 'support_priority', 'description': 'Priority customer support', 'category': 'support', 'is_premium': True},
    ]
    
    created_features = {}
    for feature_data in features_to_create:
        existing = Feature.query.filter_by(feature_key=feature_data['feature_key']).first()
        if not existing:
            feature = Feature(**feature_data)
            db.session.add(feature)
            created_features[feature_data['feature_key']] = feature
            print(f"Created feature: {feature_data['name']}")
        else:
            created_features[feature_data['feature_key']] = existing
            print(f"Feature already exists: {feature_data['name']}")
    
    db.session.commit()
    
    print("\n=== ASSIGNING FEATURES TO PACKAGES ===")
    
    # Get all packages
    packages = ClientPackage.query.all()
    
    # Define feature assignments for each package type
    package_features = {
        'Starter Commission': ['api_basic'],
        'Business Commission': ['api_basic', 'dashboard_analytics'],
        'Enterprise Commission': ['api_basic', 'api_advanced', 'dashboard_analytics', 'dashboard_realtime', 'support_priority'],
        'Basic Flat Rate': ['api_basic'],
        'Premium Flat Rate': ['api_basic', 'dashboard_analytics', 'wallet_management'],
        'Professional Flat Rate': ['api_basic', 'api_advanced', 'dashboard_analytics', 'dashboard_realtime', 'wallet_management', 'support_priority'],
    }
    
    for package in packages:
        package_name = package.name
        if package_name in package_features:
            for feature_key in package_features[package_name]:
                feature = created_features.get(feature_key)
                if feature:
                    # Check if the package feature relationship already exists
                    existing_pf = PackageFeature.query.filter_by(
                        package_id=package.id, 
                        feature_id=feature.id
                    ).first()
                    
                    if not existing_pf:
                        package_feature = PackageFeature(
                            package_id=package.id,
                            feature_id=feature.id,
                            is_included=True
                        )
                        db.session.add(package_feature)
                        print(f"Assigned {feature_key} to {package_name}")
                    else:
                        print(f"Feature {feature_key} already assigned to {package_name}")
    
    db.session.commit()
    
    print("\n=== ASSIGNING PACKAGES TO CLIENTS ===")
    
    # Assign default packages to clients that have None
    clients_without_packages = Client.query.filter_by(package_id=None).all()
    default_package = ClientPackage.query.filter_by(name='Starter Commission').first()
    
    if default_package:
        for client in clients_without_packages:
            client.package_id = default_package.id
            print(f"Assigned {default_package.name} to {client.company_name}")
        
        db.session.commit()
        print(f"Assigned default package to {len(clients_without_packages)} clients")
    else:
        print("No default package found")
    
    print("\n=== VERIFICATION ===")
    
    # Verify the setup
    clients = Client.query.all()
    for client in clients:
        print(f"Client {client.company_name}:")
        print(f"  Package: {client.get_current_package().name if client.get_current_package() else 'None'}")
        print(f"  Has API Basic: {client.has_feature('api_basic')}")
        print(f"  Has Analytics: {client.has_feature('dashboard_analytics')}")
        print("---")
