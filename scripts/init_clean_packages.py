#!/usr/bin/env python3
"""
Initialize clean package structure for Paycrypt
Creates the 4 core packages: 1 commission-based + 3 flat-rate packages
"""

import os
import sys
from decimal import Decimal
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.client_package import ClientPackage, ClientType, PackageStatus, Feature, PackageFeature

def init_clean_packages():
    """Initialize the clean package structure"""
    app = create_app()
    with app.app_context():
        print("Initializing clean package structure...")
        
        # Clear existing packages (optional - comment out if you want to keep existing)
        # ClientPackage.query.delete()
        # Feature.query.delete()
        # PackageFeature.query.delete()
        
        # Create core features
        features = {
            'basic_dashboard': Feature(
                name='Basic Dashboard',
                description='Essential payment tracking and analytics',
                feature_key='basic_dashboard',
                category='dashboard'
            ),
            'advanced_dashboard': Feature(
                name='Advanced Dashboard',
                description='Comprehensive analytics and reporting',
                feature_key='advanced_dashboard',
                category='dashboard',
                is_premium=True
            ),
            'custom_dashboard': Feature(
                name='Custom Dashboard',
                description='Fully customizable dashboard and white-labeling',
                feature_key='custom_dashboard',
                category='dashboard',
                is_premium=True
            ),
            'api_access': Feature(
                name='API Access',
                description='RESTful API for integration',
                feature_key='api_access',
                category='api'
            ),
            'webhooks': Feature(
                name='Webhooks',
                description='Real-time payment notifications',
                feature_key='webhooks',
                category='api',
                is_premium=True
            ),
            'email_support': Feature(
                name='Email Support',
                description='Standard email support during business hours',
                feature_key='email_support',
                category='support'
            ),
            'priority_support': Feature(
                name='Priority Support',
                description='Priority email and chat support',
                feature_key='priority_support',
                category='support',
                is_premium=True
            ),
            'phone_support': Feature(
                name='24/7 Phone Support',
                description='Round-the-clock phone support',
                feature_key='phone_support',
                category='support',
                is_premium=True
            ),
            'white_label': Feature(
                name='White-label Options',
                description='Custom branding and white-label deployment',
                feature_key='white_label',
                category='premium',
                is_premium=True
            ),
            'custom_wallet': Feature(
                name='Custom Wallet Integration',
                description='Connect your own crypto wallets',
                feature_key='custom_wallet',
                category='premium',
                is_premium=True
            )
        }
        
        # Add features to database
        for feature in features.values():
            existing = Feature.query.filter_by(feature_key=feature.feature_key).first()
            if not existing:
                db.session.add(feature)
        
        db.session.commit()
        print(f"Created {len(features)} features")
        
        # Create packages
        packages = []
        
        # 1. Commission-Based Professional Package
        professional = ClientPackage(
            name='Professional',
            description='Flexible commission-based plan for high-volume businesses. Pay $1,000 setup fee, then only commission on transactions.',
            client_type=ClientType.COMMISSION,
            setup_fee=Decimal('1000.00'),
            commission_rate=Decimal('0.025'),  # 2.5% - this will be negotiated per client
            max_transactions_per_month=None,  # Unlimited
            max_api_calls_per_month=None,     # Unlimited
            max_wallets=10,
            is_popular=True,
            sort_order=1,
            status=PackageStatus.ACTIVE
        )
        
        # 2. Starter Flat-Rate Package
        starter = ClientPackage(
            name='Starter',
            description='Perfect for small businesses getting started with crypto payments.',
            client_type=ClientType.FLAT_RATE,
            monthly_price=Decimal('99.00'),
            annual_price=Decimal('1069.20'),  # 99 * 12 * 0.9 = 10% discount
            supports_monthly=True,
            supports_annual=True,
            annual_discount_percent=Decimal('10.0'),
            max_transactions_per_month=1000,
            max_api_calls_per_month=10000,
            max_wallets=1,
            sort_order=2,
            status=PackageStatus.ACTIVE
        )
        
        # 3. Business Flat-Rate Package
        business = ClientPackage(
            name='Business',
            description='Ideal for growing businesses with moderate transaction volumes.',
            client_type=ClientType.FLAT_RATE,
            monthly_price=Decimal('299.00'),
            annual_price=Decimal('3230.40'),  # 299 * 12 * 0.9 = 10% discount
            supports_monthly=True,
            supports_annual=True,
            annual_discount_percent=Decimal('10.0'),
            max_transactions_per_month=10000,
            max_api_calls_per_month=50000,
            max_wallets=3,
            is_popular=True,
            sort_order=3,
            status=PackageStatus.ACTIVE
        )
        
        # 4. Enterprise Flat-Rate Package
        enterprise = ClientPackage(
            name='Enterprise',
            description='Comprehensive solution for large businesses with high transaction volumes.',
            client_type=ClientType.FLAT_RATE,
            monthly_price=Decimal('999.00'),
            annual_price=Decimal('10790.40'),  # 999 * 12 * 0.9 = 10% discount
            supports_monthly=True,
            supports_annual=True,
            annual_discount_percent=Decimal('10.0'),
            max_transactions_per_month=None,  # Unlimited
            max_api_calls_per_month=None,     # Unlimited
            max_wallets=10,
            sort_order=4,
            status=PackageStatus.ACTIVE
        )
        
        packages = [professional, starter, business, enterprise]
        
        # Add packages to database (check if they exist first)
        for package in packages:
            existing = ClientPackage.query.filter_by(name=package.name, client_type=package.client_type).first()
            if not existing:
                db.session.add(package)
                packages.append(package)
            else:
                print(f"Package {package.name} ({package.client_type.value}) already exists, updating...")
                # Update existing package
                existing.description = package.description
                existing.monthly_price = package.monthly_price
                existing.annual_price = package.annual_price
                existing.setup_fee = package.setup_fee
                existing.commission_rate = package.commission_rate
                existing.max_transactions_per_month = package.max_transactions_per_month
                existing.max_api_calls_per_month = package.max_api_calls_per_month
                existing.max_wallets = package.max_wallets
                existing.is_popular = package.is_popular
                existing.sort_order = package.sort_order
                existing.updated_at = datetime.utcnow()
        
        db.session.commit()
        print(f"Created/updated packages")
        
        # Assign features to packages
        package_features = {
            'Professional': [
                'advanced_dashboard', 'custom_dashboard', 'api_access', 'webhooks',
                'priority_support', 'phone_support', 'white_label', 'custom_wallet'
            ],
            'Starter': [
                'basic_dashboard', 'api_access', 'email_support'
            ],
            'Business': [
                'advanced_dashboard', 'api_access', 'webhooks', 'priority_support'
            ],
            'Enterprise': [
                'advanced_dashboard', 'custom_dashboard', 'api_access', 'webhooks',
                'priority_support', 'phone_support', 'white_label'
            ]
        }
        
        for package_name, feature_keys in package_features.items():
            package = ClientPackage.query.filter_by(name=package_name).first()
            if package:
                # Clear existing features for this package
                PackageFeature.query.filter_by(package_id=package.id).delete()
                
                for feature_key in feature_keys:
                    feature = Feature.query.filter_by(feature_key=feature_key).first()
                    if feature:
                        pf = PackageFeature(
                            package_id=package.id,
                            feature_id=feature.id,
                            is_included=True
                        )
                        db.session.add(pf)
        
        db.session.commit()
        print("Assigned features to packages")
        
        # Print summary
        print("\n=== PACKAGE SUMMARY ===")
        for package in ClientPackage.query.order_by(ClientPackage.sort_order).all():
            print(f"\n{package.name} ({package.client_type.value})")
            print(f"  Description: {package.description}")
            if package.client_type == ClientType.COMMISSION:
                print(f"  Setup Fee: ${package.setup_fee}")
                print(f"  Commission Rate: {float(package.commission_rate * 100):.1f}%")
            else:
                print(f"  Monthly: ${package.monthly_price}")
                print(f"  Annual: ${package.annual_price} (Save {package.annual_discount_percent}%)")
            print(f"  Max Transactions: {package.max_transactions_per_month or 'Unlimited'}")
            print(f"  Features: {len(package.features)}")
            for feature in package.features:
                print(f"    - {feature.name}")

if __name__ == '__main__':
    init_clean_packages()
