"""
Initialize client packages and features
This script sets up the default package structure for the platform
"""

from app.extensions import db
from app.models.client_package import Feature, ClientPackage, PackageFeature, ClientType, PackageStatus


def init_features(session):
    """Initialize core features"""
    from app.models.feature import Feature
    
    features = [
        # Dashboard Features
        {'name': 'Basic Dashboard', 'feature_key': 'dashboard_basic', 'category': 'dashboard', 'description': 'Basic payment tracking and statistics'},
        {'name': 'Advanced Analytics', 'feature_key': 'dashboard_analytics', 'category': 'dashboard', 'description': 'Detailed analytics and reporting', 'is_premium': True},
        {'name': 'Real-time Monitoring', 'feature_key': 'dashboard_realtime', 'category': 'dashboard', 'description': 'Real-time payment monitoring', 'is_premium': True},
        
        # API Features
        {'name': 'Basic API Access', 'feature_key': 'api_basic', 'category': 'api', 'description': 'Basic API endpoints for payment processing'},
        {'name': 'Advanced API', 'feature_key': 'api_advanced', 'category': 'api', 'description': 'Full API access with webhooks', 'is_premium': True},
        {'name': 'Webhook Support', 'feature_key': 'api_webhooks', 'category': 'api', 'description': 'Real-time webhook notifications', 'is_premium': True},
        
        # Wallet Features
        {'name': 'Platform Wallet', 'feature_key': 'wallet_platform', 'category': 'wallet', 'description': 'Use platform-managed wallets'},
        {'name': 'Custom Wallet Integration', 'feature_key': 'wallet_custom', 'category': 'wallet', 'description': 'Integrate your own wallets', 'is_premium': True},
        {'name': 'Multi-Wallet Support', 'feature_key': 'wallet_multi', 'category': 'wallet', 'description': 'Support for multiple wallets', 'is_premium': True},
        
        # Support Features
        {'name': 'Email Support', 'feature_key': 'support_email', 'category': 'support', 'description': 'Email-based customer support'},
        {'name': 'Priority Support', 'feature_key': 'support_priority', 'category': 'support', 'description': 'Priority customer support', 'is_premium': True},
        {'name': 'Dedicated Support', 'feature_key': 'support_dedicated', 'category': 'support', 'description': 'Dedicated account manager', 'is_premium': True},
        
        # Branding Features
        {'name': 'Standard Branding', 'feature_key': 'branding_standard', 'category': 'branding', 'description': 'Platform branding'},
        {'name': 'Custom Branding', 'feature_key': 'branding_custom', 'category': 'branding', 'description': 'Custom logo and colors', 'is_premium': True},
        {'name': 'White Label', 'feature_key': 'branding_whitelabel', 'category': 'branding', 'description': 'Complete white-label solution', 'is_premium': True},
        
        # Additional Features
        {'name': 'Transaction Limits', 'feature_key': 'limits_basic', 'category': 'limits', 'description': 'Basic transaction limits'},
        {'name': 'Custom Limits', 'feature_key': 'limits_custom', 'category': 'limits', 'description': 'Customizable transaction limits', 'is_premium': True},
        {'name': 'Compliance Tools', 'feature_key': 'compliance_tools', 'category': 'compliance', 'description': 'KYC/AML compliance tools', 'is_premium': True},
    ]
    
    created_count = 0
    for feature_data in features:
        feature = session.query(Feature).filter_by(feature_key=feature_data['feature_key']).first()
        if not feature:
            feature = Feature(**feature_data)
            session.add(feature)
            created_count += 1
    
    print(f"✓ Initialized {created_count} features")
    return created_count


def init_packages(session):
    """Initialize default packages"""
    from app.models.client_package import ClientPackage, PackageFeature, ClientType
    from app.models.feature import Feature
    
    # Commission-based packages (Type 1 - Uses platform wallet)
    commission_packages = [
        {
            'name': 'Starter',
            'description': 'Perfect for small businesses getting started with crypto payments',
            'client_type': ClientType.COMMISSION,
            'commission_rate': 0.025,  # 2.5%
            'max_transactions_per_month': 100,
            'max_api_calls_per_month': 1000,
            'max_wallets': 1,
            'is_popular': False,
            'sort_order': 1,
            'features': [
                'dashboard_basic', 'api_basic', 'wallet_platform', 
                'support_email', 'branding_standard', 'limits_basic'
            ]
        },
        {
            'name': 'Professional',
            'description': 'Advanced features for growing businesses',
            'client_type': ClientType.COMMISSION,
            'commission_rate': 0.020,  # 2.0%
            'max_transactions_per_month': 1000,
            'max_api_calls_per_month': 10000,
            'max_wallets': 3,
            'is_popular': True,
            'sort_order': 2,
            'features': [
                'dashboard_basic', 'dashboard_analytics', 'api_basic', 'api_webhooks',
                'wallet_platform', 'support_priority', 'branding_custom', 'limits_custom'
            ]
        },
        {
            'name': 'Enterprise',
            'description': 'Full-featured solution for large enterprises',
            'client_type': ClientType.COMMISSION,
            'commission_rate': 0.015,  # 1.5%
            'max_transactions_per_month': None,  # Unlimited
            'max_api_calls_per_month': None,  # Unlimited
            'max_wallets': None,  # Unlimited
            'is_popular': False,
            'sort_order': 3,
            'features': [
                'dashboard_basic', 'dashboard_analytics', 'dashboard_realtime',
                'api_basic', 'api_advanced', 'api_webhooks', 'wallet_platform',
                'wallet_multi', 'support_dedicated', 'branding_whitelabel',
                'limits_custom', 'compliance_tools'
            ]
        }
    ]
    
    # Flat-rate packages (Type 2 - Own wallet)
    flat_rate_packages = [
        {
            'name': 'Basic',
            'description': 'Use your own wallet with basic platform features',
            'client_type': ClientType.FLAT_RATE,
            'monthly_price': 99.00,
            'max_transactions_per_month': 500,
            'max_api_calls_per_month': 5000,
            'max_wallets': 1,
            'is_popular': False,
            'sort_order': 4,
            'features': [
                'dashboard_basic', 'api_basic', 'wallet_custom',
                'support_email', 'branding_standard', 'limits_basic'
            ]
        },
        {
            'name': 'Advanced',
            'description': 'Multiple wallets with advanced features',
            'client_type': ClientType.FLAT_RATE,
            'monthly_price': 299.00,
            'max_transactions_per_month': 2000,
            'max_api_calls_per_month': 20000,
            'max_wallets': 5,
            'is_popular': True,
            'sort_order': 5,
            'features': [
                'dashboard_basic', 'dashboard_analytics', 'api_basic', 'api_webhooks',
                'wallet_custom', 'wallet_multi', 'support_priority',
                'branding_custom', 'limits_custom'
            ]
        },
        {
            'name': 'Premium',
            'description': 'Enterprise-grade solution with your own infrastructure',
            'client_type': ClientType.FLAT_RATE,
            'monthly_price': 599.00,
            'max_transactions_per_month': None,  # Unlimited
            'max_api_calls_per_month': None,  # Unlimited
            'max_wallets': None,  # Unlimited
            'is_popular': False,
            'sort_order': 6,
            'features': [
                'dashboard_basic', 'dashboard_analytics', 'dashboard_realtime',
                'api_basic', 'api_advanced', 'api_webhooks', 'wallet_custom',
                'wallet_multi', 'support_dedicated', 'branding_whitelabel',
                'limits_custom', 'compliance_tools'
            ]
        }
    ]
    
    all_packages = commission_packages + flat_rate_packages
    created_count = 0
    
    for package_data in all_packages:
        package = session.query(ClientPackage).filter_by(name=package_data['name']).first()
        if not package:
            # Extract features list
            feature_keys = package_data.pop('features')
            
            # Calculate annual price with 10% discount for flat-rate packages
            if package_data.get('monthly_price'):
                package_data['annual_price'] = package_data['monthly_price'] * 12 * 0.9
            
            # Create package
            package = ClientPackage(**package_data)
            session.add(package)
            session.flush()  # Get the package ID
            
            # Add features to package
            for feature_key in feature_keys:
                feature = session.query(Feature).filter_by(feature_key=feature_key).first()
                if feature:
                    package_feature = PackageFeature(
                        package_id=package.id,
                        feature_id=feature.id,
                        is_included=True
                    )
                    session.add(package_feature)
            
            created_count += 1
    
    print(f"✓ Initialized {created_count} packages")
    return created_count


def init_client_packages():
    """Initialize the complete package system"""
    from app.extensions import db
    
    print("Initializing client packages...")
    
    try:
        with db.session() as session:
            features_created = init_features(session)
            packages_created = init_packages(session)
            session.commit()
            print(f"✓ Client package system initialized successfully! ({features_created} features, {packages_created} packages)")
            return True
    except Exception as e:
        print(f"✗ Error initializing packages: {e}")
        if 'session' in locals():
            session.rollback()
        return False


if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    with app.app_context():
        init_client_packages()
