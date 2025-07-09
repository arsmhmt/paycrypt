#!/usr/bin/env python3
"""
Setup script for single commission-based package model and Paycrypt as first client
"""

import os
import sys
from decimal import Decimal
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models import (
    Client, ClientPackage, Feature, PackageFeature, 
    PackageActivationPayment, PaymentStatus, ClientType, 
    PackageStatus, User
)
from werkzeug.security import generate_password_hash

def create_single_package():
    """Create the single commission-based professional package"""
    
    # Check if package already exists
    existing_package = ClientPackage.query.filter_by(name='Professional').first()
    if existing_package:
        print("✅ Professional package already exists")
        return existing_package
    
    # Create the single professional package
    package = ClientPackage(
        name='Professional',
        description='Complete crypto payment solution with personalized commission rates based on your business volume and requirements.',
        client_type=ClientType.COMMISSION,
        commission_rate=Decimal('2.5'),  # Default rate, customizable per client
        monthly_fee=None,  # No monthly fee for commission-based
        setup_fee=Decimal('1000.00'),  # $1000 setup fee
        max_transactions_per_month=None,  # Unlimited
        max_transaction_amount=None,  # Unlimited
        is_popular=True,
        is_custom=False,
        status=PackageStatus.ACTIVE
    )
    
    db.session.add(package)
    db.session.flush()  # Get the ID
    
    print(f"✅ Created Professional package (ID: {package.id})")
    return package

def create_package_features(package):
    """Create and assign features to the package"""
    
    features_data = [
        {
            'name': 'custom_commission_rates',
            'display_name': 'Custom Commission Rates',
            'description': 'Personalized commission rates based on business volume',
            'is_core': True
        },
        {
            'name': 'all_cryptocurrencies',
            'display_name': 'All Cryptocurrency Support',
            'description': 'Accept Bitcoin, Ethereum, and 150+ cryptocurrencies',
            'is_core': True
        },
        {
            'name': 'advanced_dashboard',
            'display_name': 'Advanced Dashboard & Analytics',
            'description': 'Real-time analytics and business intelligence tools',
            'is_core': True
        },
        {
            'name': 'custom_wallet_integration',
            'display_name': 'Custom Wallet Integration',
            'description': 'Integrate your own wallet infrastructure',
            'is_core': True
        },
        {
            'name': 'api_access',
            'display_name': 'API Access & Webhooks',
            'description': 'Full API access with webhooks and SDKs',
            'is_core': True
        },
        {
            'name': 'priority_support',
            'display_name': '24/7 Priority Support',
            'description': 'Round-the-clock priority support with dedicated account manager',
            'is_core': True
        },
        {
            'name': 'white_label',
            'display_name': 'White-label Options',
            'description': 'Brand the platform with your company identity',
            'is_core': False
        },
        {
            'name': 'multi_signature_wallets',
            'display_name': 'Multi-Signature Wallets',
            'description': 'Enhanced security with multi-signature wallet support',
            'is_core': True
        },
        {
            'name': 'instant_settlements',
            'display_name': 'Instant Settlements',
            'description': 'Real-time settlements with automatic processing',
            'is_core': True
        },
        {
            'name': 'compliance_tools',
            'display_name': 'Compliance & Reporting Tools',
            'description': 'Built-in AML/KYC compliance and reporting features',
            'is_core': True
        }
    ]
    
    created_features = []
    
    for feature_data in features_data:
        # Check if feature already exists
        feature = Feature.query.filter_by(name=feature_data['name']).first()
        
        if not feature:
            feature = Feature(
                name=feature_data['name'],
                display_name=feature_data['display_name'],
                description=feature_data['description'],
                is_core=feature_data['is_core']
            )
            db.session.add(feature)
            db.session.flush()
            print(f"✅ Created feature: {feature.display_name}")
        else:
            print(f"ℹ️  Feature already exists: {feature.display_name}")
        
        # Check if package-feature relationship exists
        package_feature = PackageFeature.query.filter_by(
            package_id=package.id,
            feature_id=feature.id
        ).first()
        
        if not package_feature:
            package_feature = PackageFeature(
                package_id=package.id,
                feature_id=feature.id,
                is_included=True,
                limit_value=None  # No limits for professional package
            )
            db.session.add(package_feature)
            print(f"✅ Assigned feature to package: {feature.display_name}")
        
        created_features.append(feature)
    
    return created_features

def create_paycrypt_client(package):
    """Create Paycrypt as the first client"""
    
    # Check if Paycrypt client already exists
    existing_client = Client.query.filter_by(email='admin@paycrypt.com').first()
    if existing_client:
        print("✅ Paycrypt client already exists")
        return existing_client
    
    # Create Paycrypt as a client
    paycrypt_client = Client(
        company_name='Paycrypt Technologies',
        email='admin@paycrypt.com',
        phone='+1-555-PAYCRYPT',
        address='123 Crypto Street',
        city='San Francisco',
        country='United States',
        postal_code='94105',
        website='https://paycrypt.com',
        contact_person='Paycrypt Team',
        contact_email='admin@paycrypt.com',
        contact_phone='+1-555-PAYCRYPT',
        type=ClientType.COMMISSION,
        package_id=package.id,
        is_active=True,
        is_verified=True,
        verified_at=datetime.utcnow(),
        password_hash=generate_password_hash('PaycryptDemo2025!'),
        # Custom commission rates for Paycrypt (lower rates as we're the platform)
        deposit_commission_rate=Decimal('1.0'),  # 1% for deposits
        withdrawal_commission_rate=Decimal('0.5'),  # 0.5% for withdrawals
        notes='Paycrypt platform owner - demo client account'
    )
    
    db.session.add(paycrypt_client)
    db.session.flush()
    
    print(f"✅ Created Paycrypt client (ID: {paycrypt_client.id})")
    
    # Create a completed activation payment for Paycrypt (waived setup fee)
    activation_payment = PackageActivationPayment(
        client_id=paycrypt_client.id,
        package_id=package.id,
        setup_fee_amount=Decimal('0.00'),  # Waived for platform owner
        setup_fee_currency='USD',
        crypto_amount=Decimal('0.00'),
        crypto_currency='BTC',
        crypto_address='platform_owner_waived',
        status=PaymentStatus.COMPLETED,
        is_activated=True,
        activated_at=datetime.utcnow(),
        transaction_hash='platform_owner_setup',
        confirmations=1,
        notes='Setup fee waived for platform owner'
    )
    
    db.session.add(activation_payment)
    
    print("✅ Created completed activation payment for Paycrypt (fee waived)")
    
    return paycrypt_client

def update_existing_clients(package):
    """Update any existing clients to use the new package structure"""
    
    # Find clients without a package assigned
    unassigned_clients = Client.query.filter_by(package_id=None).all()
    
    for client in unassigned_clients:
        if client.email != 'admin@paycrypt.com':  # Skip our main client
            client.package_id = package.id
            print(f"✅ Assigned package to existing client: {client.email}")
    
    if unassigned_clients:
        print(f"✅ Updated {len(unassigned_clients)} existing clients")

def main():
    """Main setup function"""
    print("🚀 Setting up single commission-based package model...")
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        try:
            # Create the professional package
            package = create_single_package()
            
            # Create and assign features
            features = create_package_features(package)
            
            # Create Paycrypt as first client
            paycrypt_client = create_paycrypt_client(package)
            
            # Update existing clients
            update_existing_clients(package)
            
            # Commit all changes
            db.session.commit()
            
            print("\n🎉 Setup completed successfully!")
            print(f"📦 Package: {package.name} (ID: {package.id})")
            print(f"🏢 Features: {len(features)} features assigned")
            print(f"👤 Client: {paycrypt_client.company_name} (ID: {paycrypt_client.id})")
            print(f"💰 Commission Rates: {paycrypt_client.deposit_commission_rate}% deposit, {paycrypt_client.withdrawal_commission_rate}% withdrawal")
            
            print("\n📋 Next Steps:")
            print("1. ✅ Single package model is now active")
            print("2. ✅ Paycrypt is set up as the first client")
            print("3. 🔄 New registrations will use the activation payment flow")
            print("4. ⚙️  Commission rates can be customized per client in admin dashboard")
            print("5. 🌐 Landing page will show the single package option")
            
        except Exception as e:
            print(f"❌ Error during setup: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    main()
