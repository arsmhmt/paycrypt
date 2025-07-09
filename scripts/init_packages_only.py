#!/usr/bin/env python3
"""
Initialize just the packages (skip features for now)
"""

import os
import sys
from decimal import Decimal
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.client_package import ClientPackage, ClientType, PackageStatus

def init_packages_only():
    """Initialize just the packages"""
    app = create_app()
    with app.app_context():
        print("Initializing packages...")
        
        # Create packages
        packages_data = [
            {
                'name': 'Professional',
                'description': 'Flexible commission-based plan for high-volume businesses. Pay $1,000 setup fee, then only commission on transactions.',
                'client_type': ClientType.COMMISSION,
                'setup_fee': Decimal('1000.00'),
                'commission_rate': Decimal('0.025'),  # 2.5% - this will be negotiated per client
                'max_transactions_per_month': None,  # Unlimited
                'max_api_calls_per_month': None,     # Unlimited
                'max_wallets': 10,
                'is_popular': True,
                'sort_order': 1,
                'status': PackageStatus.ACTIVE
            },
            {
                'name': 'Starter',
                'description': 'Perfect for small businesses getting started with crypto payments.',
                'client_type': ClientType.FLAT_RATE,
                'monthly_price': Decimal('99.00'),
                'annual_price': Decimal('1069.20'),  # 99 * 12 * 0.9 = 10% discount
                'supports_monthly': True,
                'supports_annual': True,
                'annual_discount_percent': Decimal('10.0'),
                'max_transactions_per_month': 1000,
                'max_api_calls_per_month': 10000,
                'max_wallets': 1,
                'sort_order': 2,
                'status': PackageStatus.ACTIVE
            },
            {
                'name': 'Business',
                'description': 'Ideal for growing businesses with moderate transaction volumes.',
                'client_type': ClientType.FLAT_RATE,
                'monthly_price': Decimal('299.00'),
                'annual_price': Decimal('3230.40'),  # 299 * 12 * 0.9 = 10% discount
                'supports_monthly': True,
                'supports_annual': True,
                'annual_discount_percent': Decimal('10.0'),
                'max_transactions_per_month': 10000,
                'max_api_calls_per_month': 50000,
                'max_wallets': 3,
                'is_popular': True,
                'sort_order': 3,
                'status': PackageStatus.ACTIVE
            },
            {
                'name': 'Enterprise',
                'description': 'Comprehensive solution for large businesses with high transaction volumes.',
                'client_type': ClientType.FLAT_RATE,
                'monthly_price': Decimal('999.00'),
                'annual_price': Decimal('10790.40'),  # 999 * 12 * 0.9 = 10% discount
                'supports_monthly': True,
                'supports_annual': True,
                'annual_discount_percent': Decimal('10.0'),
                'max_transactions_per_month': None,  # Unlimited
                'max_api_calls_per_month': None,     # Unlimited
                'max_wallets': 10,
                'sort_order': 4,
                'status': PackageStatus.ACTIVE
            }
        ]
        
        # Add packages to database
        for package_data in packages_data:
            existing = ClientPackage.query.filter_by(name=package_data['name']).first()
            if not existing:
                package = ClientPackage(**package_data)
                db.session.add(package)
                print(f"  Added package: {package_data['name']}")
            else:
                print(f"  Package {package_data['name']} already exists - updating...")
                # Update existing package
                for key, value in package_data.items():
                    if key != 'name':  # Don't update the name
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
        
        db.session.commit()
        print("Done!")
        
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

if __name__ == '__main__':
    init_packages_only()
