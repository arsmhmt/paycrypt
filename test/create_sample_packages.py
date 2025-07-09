#!/usr/bin/env python3
"""
Create sample client packages for testing
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.client_package import ClientPackage, ClientType, PackageStatus
from decimal import Decimal

def create_sample_packages():
    """Create sample client packages"""
    app = create_app()
    
    with app.app_context():
        # Check if packages already exist
        existing_packages = ClientPackage.query.count()
        if existing_packages > 0:
            print(f"Found {existing_packages} existing packages. Skipping creation.")
            return
            
        # Commission-based packages
        starter_commission = ClientPackage(
            name="Starter Commission",
            description="Perfect for small businesses starting with crypto payments",
            client_type=ClientType.COMMISSION,
            commission_rate=Decimal('0.035'),  # 3.5%
            setup_fee=Decimal('500.00'),
            max_transactions_per_month=1000,
            max_api_calls_per_month=10000,
            max_wallets=1,
            sort_order=1,
            status=PackageStatus.ACTIVE
        )
        
        business_commission = ClientPackage(
            name="Business Commission",
            description="Ideal for growing businesses with higher transaction volumes",
            client_type=ClientType.COMMISSION,
            commission_rate=Decimal('0.025'),  # 2.5%
            setup_fee=Decimal('1000.00'),
            max_transactions_per_month=5000,
            max_api_calls_per_month=50000,
            max_wallets=3,
            sort_order=2,
            status=PackageStatus.ACTIVE,
            is_popular=True
        )
        
        enterprise_commission = ClientPackage(
            name="Enterprise Commission",
            description="For large enterprises with unlimited transactions",
            client_type=ClientType.COMMISSION,
            commission_rate=Decimal('0.015'),  # 1.5%
            setup_fee=Decimal('2000.00'),
            max_transactions_per_month=None,  # Unlimited
            max_api_calls_per_month=None,     # Unlimited
            max_wallets=10,
            sort_order=3,
            status=PackageStatus.ACTIVE
        )
        
        # Flat-rate packages
        basic_flat = ClientPackage(
            name="Basic Flat Rate",
            description="Flat monthly fee for small to medium businesses",
            client_type=ClientType.FLAT_RATE,
            monthly_price=Decimal('299.00'),
            annual_price=Decimal('2990.00'),  # 2 months free
            max_transactions_per_month=2000,
            max_api_calls_per_month=25000,
            max_wallets=2,
            sort_order=4,
            status=PackageStatus.ACTIVE
        )
        
        premium_flat = ClientPackage(
            name="Premium Flat Rate",
            description="Premium flat rate with enhanced features",
            client_type=ClientType.FLAT_RATE,
            monthly_price=Decimal('799.00'),
            annual_price=Decimal('7990.00'),  # 2 months free
            max_transactions_per_month=10000,
            max_api_calls_per_month=100000,
            max_wallets=5,
            sort_order=5,
            status=PackageStatus.ACTIVE
        )
        
        professional_flat = ClientPackage(
            name="Professional Flat Rate",
            description="Professional package for high-volume businesses",
            client_type=ClientType.FLAT_RATE,
            monthly_price=Decimal('1499.00'),
            annual_price=Decimal('14990.00'),  # 2 months free
            max_transactions_per_month=None,  # Unlimited
            max_api_calls_per_month=None,     # Unlimited
            max_wallets=20,
            sort_order=6,
            status=PackageStatus.ACTIVE
        )
        
        # Add all packages
        packages = [
            starter_commission, business_commission, enterprise_commission,
            basic_flat, premium_flat, professional_flat
        ]
        
        for package in packages:
            db.session.add(package)
            
        db.session.commit()
        print(f"Successfully created {len(packages)} sample packages!")
        
        # Print summary
        print("\nCreated packages:")
        for package in packages:
            print(f"- {package.name} ({package.client_type.value}): {package.price_display}")

if __name__ == '__main__':
    create_sample_packages()
