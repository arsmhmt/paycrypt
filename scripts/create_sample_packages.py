"""
Migration script to add sample client packages
Run this after creating the database tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.client_package import Feature, ClientPackage, PackageFeature, ClientType, PackageStatus

def create_sample_packages():
    """Create sample packages for the platform"""
    
    app = create_app()
    with app.app_context():
        try:
            # Clear existing packages (for development)
            PackageFeature.query.delete()
            ClientPackage.query.delete()
            Feature.query.delete()
            db.session.commit()
            
            # Create core features
            features = [
                Feature(name='Basic Dashboard', feature_key='dashboard_basic', category='dashboard', 
                       description='Basic payment tracking and statistics'),
                Feature(name='Advanced Analytics', feature_key='dashboard_analytics', category='dashboard', 
                       description='Detailed analytics and reporting', is_premium=True),
                Feature(name='Real-time Monitoring', feature_key='dashboard_realtime', category='dashboard', 
                       description='Real-time payment monitoring', is_premium=True),
                Feature(name='Basic API Access', feature_key='api_basic', category='api', 
                       description='Basic API endpoints for payment processing'),
                Feature(name='Advanced API', feature_key='api_advanced', category='api', 
                       description='Full API access with webhooks', is_premium=True),
                Feature(name='Webhook Support', feature_key='api_webhooks', category='api', 
                       description='Real-time webhook notifications', is_premium=True),
                Feature(name='Platform Wallet', feature_key='wallet_platform', category='wallet', 
                       description='Use platform-managed wallets'),
                Feature(name='Custom Wallet Integration', feature_key='wallet_custom', category='wallet', 
                       description='Integrate your own wallets', is_premium=True),
                Feature(name='Multi-Wallet Support', feature_key='wallet_multi', category='wallet', 
                       description='Support for multiple wallets', is_premium=True),
                Feature(name='Email Support', feature_key='support_email', category='support', 
                       description='Email-based customer support'),
                Feature(name='Priority Support', feature_key='support_priority', category='support', 
                       description='Priority customer support', is_premium=True),
                Feature(name='Dedicated Support', feature_key='support_dedicated', category='support', 
                       description='Dedicated account manager', is_premium=True),
                Feature(name='Standard Branding', feature_key='branding_standard', category='branding', 
                       description='Platform branding'),
                Feature(name='Custom Branding', feature_key='branding_custom', category='branding', 
                       description='Custom logo and colors', is_premium=True),
                Feature(name='White Label', feature_key='branding_whitelabel', category='branding', 
                       description='Complete white-label solution', is_premium=True),
            ]
            
            for feature in features:
                db.session.add(feature)
            
            db.session.commit()
            print("✓ Features created")
            
            # Create Commission-based packages (Type 1)
            starter_package = ClientPackage(
                name='Starter',
                description='Perfect for small businesses getting started with crypto payments',
                client_type=ClientType.COMMISSION,
                commission_rate=0.025,  # 2.5%
                max_transactions_per_month=100,
                max_api_calls_per_month=1000,
                max_wallets=1,
                sort_order=1,
                status=PackageStatus.ACTIVE
            )
            db.session.add(starter_package)
            
            professional_package = ClientPackage(
                name='Professional',
                description='Advanced features for growing businesses',
                client_type=ClientType.COMMISSION,
                commission_rate=0.020,  # 2.0%
                max_transactions_per_month=1000,
                max_api_calls_per_month=10000,
                max_wallets=3,
                is_popular=True,
                sort_order=2,
                status=PackageStatus.ACTIVE
            )
            db.session.add(professional_package)
            
            enterprise_package = ClientPackage(
                name='Enterprise',
                description='Full-featured solution for large enterprises',
                client_type=ClientType.COMMISSION,
                commission_rate=0.015,  # 1.5%
                max_transactions_per_month=None,  # Unlimited
                max_api_calls_per_month=None,  # Unlimited
                max_wallets=None,  # Unlimited
                sort_order=3,
                status=PackageStatus.ACTIVE
            )
            db.session.add(enterprise_package)
            
            # Create Flat-rate packages (Type 2)
            basic_package = ClientPackage(
                name='Basic',
                description='Use your own wallet with basic platform features',
                client_type=ClientType.FLAT_RATE,
                monthly_price=99.00,
                max_transactions_per_month=500,
                max_api_calls_per_month=5000,
                max_wallets=1,
                sort_order=4,
                status=PackageStatus.ACTIVE
            )
            db.session.add(basic_package)
            
            advanced_package = ClientPackage(
                name='Advanced',
                description='Multiple wallets with advanced features',
                client_type=ClientType.FLAT_RATE,
                monthly_price=299.00,
                max_transactions_per_month=2000,
                max_api_calls_per_month=20000,
                max_wallets=5,
                is_popular=True,
                sort_order=5,
                status=PackageStatus.ACTIVE
            )
            db.session.add(advanced_package)
            
            premium_package = ClientPackage(
                name='Premium',
                description='Enterprise-grade solution with your own infrastructure',
                client_type=ClientType.FLAT_RATE,
                monthly_price=599.00,
                max_transactions_per_month=None,  # Unlimited
                max_api_calls_per_month=None,  # Unlimited
                max_wallets=None,  # Unlimited
                sort_order=6,
                status=PackageStatus.ACTIVE
            )
            db.session.add(premium_package)
            
            db.session.commit()
            print("✓ Sample packages created")
            
            # Add features to packages
            package_feature_mapping = {
                'Starter': ['dashboard_basic', 'api_basic', 'wallet_platform', 'support_email', 'branding_standard'],
                'Professional': ['dashboard_basic', 'dashboard_analytics', 'api_basic', 'api_webhooks', 'wallet_platform', 'support_priority', 'branding_custom'],
                'Enterprise': ['dashboard_basic', 'dashboard_analytics', 'dashboard_realtime', 'api_basic', 'api_advanced', 'api_webhooks', 'wallet_platform', 'wallet_multi', 'support_dedicated', 'branding_whitelabel'],
                'Basic': ['dashboard_basic', 'api_basic', 'wallet_custom', 'support_email', 'branding_standard'],
                'Advanced': ['dashboard_basic', 'dashboard_analytics', 'api_basic', 'api_webhooks', 'wallet_custom', 'wallet_multi', 'support_priority', 'branding_custom'],
                'Premium': ['dashboard_basic', 'dashboard_analytics', 'dashboard_realtime', 'api_basic', 'api_advanced', 'api_webhooks', 'wallet_custom', 'wallet_multi', 'support_dedicated', 'branding_whitelabel']
            }
            
            for package_name, feature_keys in package_feature_mapping.items():
                package = ClientPackage.query.filter_by(name=package_name).first()
                if package:
                    for feature_key in feature_keys:
                        feature = Feature.query.filter_by(feature_key=feature_key).first()
                        if feature:
                            package_feature = PackageFeature(
                                package_id=package.id,
                                feature_id=feature.id,
                                is_included=True
                            )
                            db.session.add(package_feature)
            
            db.session.commit()
            print("✓ Package features assigned")
            
            # Print summary
            packages = ClientPackage.query.all()
            print(f"\n📦 Created {len(packages)} packages:")
            for package in packages:
                print(f"   • {package.name} ({package.client_type.value}) - {package.price_display}")
                
            features = Feature.query.all()
            print(f"\n🔧 Created {len(features)} features:")
            for feature in features:
                print(f"   • {feature.name} ({feature.category})")
                
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error creating packages: {e}")
            return False

if __name__ == '__main__':
    create_sample_packages()
