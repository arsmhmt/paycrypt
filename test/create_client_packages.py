#!/usr/bin/env python
"""
Create sample client packages for testing
"""

import sys
import logging
from datetime import datetime
from flask import Flask
from app import create_app, db
from app.models.client_package import ClientPackage, Feature, PackageFeature, ClientType

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger('create_packages')

def create_packages():
    """Create standard client packages and features for testing"""
    
    # Create app with development config
    app = create_app()
    app.app_context().push()
    
    logger.info("Creating features...")
    
    # Create basic features
    features = {
        # Dashboard features
        'dashboard': Feature(
            name='Basic Dashboard',
            feature_key='dashboard',
            description='Access to basic dashboard functionality',
            category='dashboard'
        ),
        'analytics': Feature(
            name='Advanced Analytics',
            feature_key='analytics',
            description='Advanced analytics and reporting',
            category='dashboard',
            is_premium=True
        ),
        
        # API features
        'api_access': Feature(
            name='API Access',
            feature_key='api_access',
            description='Access to payment gateway API',
            category='api'
        ),
        'webhooks': Feature(
            name='Webhooks',
            feature_key='webhooks',
            description='Webhook notifications for transactions',
            category='api'
        ),
        
        # Payment features
        'deposit': Feature(
            name='Deposits',
            feature_key='deposit',
            description='Accept cryptocurrency deposits',
            category='payment'
        ),
        'withdrawals': Feature(
            name='Withdrawals',
            feature_key='withdrawals',
            description='Process cryptocurrency withdrawals',
            category='payment'
        ),
        'auto_exchange': Feature(
            name='Auto Exchange',
            feature_key='auto_exchange',
            description='Automatic exchange to fiat',
            category='payment',
            is_premium=True
        ),
        
        # Support features
        'email_support': Feature(
            name='Email Support',
            feature_key='email_support',
            description='Email support during business hours',
            category='support'
        ),
        'priority_support': Feature(
            name='Priority Support',
            feature_key='priority_support',
            description='24/7 priority support',
            category='support',
            is_premium=True
        ),
    }
    
    # Save features first
    for key, feature in features.items():
        # Check if feature already exists
        existing = Feature.query.filter_by(feature_key=feature.feature_key).first()
        if existing:
            features[key] = existing  # Use existing feature
            logger.info(f"Feature already exists: {feature.feature_key}")
        else:
            db.session.add(feature)
            logger.info(f"Added new feature: {feature.feature_key}")
    
    db.session.commit()  # Commit to get feature IDs
    
    logger.info("Creating packages...")
    
    # COMMISSION package (B2C)
    b2c_commission = ClientPackage.query.filter_by(name='B2C Commission').first()
    if not b2c_commission:
        b2c_commission = ClientPackage(
            name='B2C Commission',
            description='Commission-based package for B2C clients',
            client_type=ClientType.COMMISSION,
            commission_rate=0.035,  # 3.5%
            setup_fee=1000.00,
            max_transactions_per_month=500,
            max_api_calls_per_month=10000,
            status='active',
            is_popular=True
        )
        db.session.add(b2c_commission)
        db.session.flush()  # Get ID without committing
        
        # Add basic features
        commission_features = [
            'dashboard', 'deposit', 'withdrawals', 'email_support'
        ]
        
        # Add features to commission package
        for feature_key in commission_features:
            feature = features.get(feature_key)
            if feature:
                pf = PackageFeature(
                    package_id=b2c_commission.id, 
                    feature_id=feature.id, 
                    is_included=True
                )
                db.session.add(pf)
                logger.info(f"Added feature {feature.name} to B2C Commission package")
        
        logger.info("Created B2C Commission package")
    else:
        logger.info("B2C Commission package already exists")
    
    # FLAT_RATE package (B2B)
    b2b_flat_rate = ClientPackage.query.filter_by(name='B2B Flat Rate').first()
    if not b2b_flat_rate:
        b2b_flat_rate = ClientPackage(
            name='B2B Flat Rate',
            description='Flat-rate package for B2B clients',
            client_type=ClientType.FLAT_RATE,
            monthly_price=299.99,
            annual_price=2999.99,
            max_transactions_per_month=None,  # Unlimited
            max_api_calls_per_month=50000,
            status='active',
            is_popular=True
        )
        db.session.add(b2b_flat_rate)
        db.session.flush()  # Get ID without committing
        
        # Add all features
        for feature in features.values():
            pf = PackageFeature(
                package_id=b2b_flat_rate.id, 
                feature_id=feature.id, 
                is_included=True
            )
            db.session.add(pf)
            logger.info(f"Added feature {feature.name} to B2B Flat Rate package")
        
        logger.info("Created B2B Flat Rate package")
    else:
        logger.info("B2B Flat Rate package already exists")
    
    # Premium FLAT_RATE package (B2B Enterprise)
    b2b_enterprise = ClientPackage.query.filter_by(name='B2B Enterprise').first()
    if not b2b_enterprise:
        b2b_enterprise = ClientPackage(
            name='B2B Enterprise',
            description='Enterprise flat-rate package for B2B clients',
            client_type=ClientType.FLAT_RATE,
            monthly_price=999.99,
            annual_price=9999.99,
            max_transactions_per_month=None,  # Unlimited
            max_api_calls_per_month=None,     # Unlimited
            status='active'
        )
        db.session.add(b2b_enterprise)
        db.session.flush()  # Get ID without committing
        
        # Add all features
        for feature in features.values():
            pf = PackageFeature(
                package_id=b2b_enterprise.id, 
                feature_id=feature.id, 
                is_included=True
            )
            db.session.add(pf)
            logger.info(f"Added feature {feature.name} to B2B Enterprise package")
        
        logger.info("Created B2B Enterprise package")
    else:
        logger.info("B2B Enterprise package already exists")
    
    db.session.commit()
    logger.info("All packages created successfully!")

def main():
    try:
        create_packages()
        return 0
    except Exception as e:
        logger.error(f"Error creating packages: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
