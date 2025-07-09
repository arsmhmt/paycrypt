# Script to insert default flat-rate packages into the database
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.client_package import ClientPackage, ClientType

# Define default flat-rate packages (removed 'slug' field)
flat_rate_packages = [
    dict(
        name='Starter Flat Rate',
        description='Perfect for small businesses getting started with crypto payments',
        client_type=ClientType.FLAT_RATE,
        monthly_price=499.00,
        annual_price=499.00 * 12 * 0.9,  # 10% discount
        max_transactions_per_month=500,
        max_api_calls_per_month=10000,
        max_wallets=1,
        max_volume_per_month=35000.00,
        min_margin_percent=1.43,
        is_popular=False,
        status='ACTIVE',
        sort_order=1,
        setup_fee=1000.00,
        supports_monthly=True,
        supports_annual=True,
        annual_discount_percent=10.0
    ),
    dict(
        name='Business Flat Rate',
        description='Ideal for growing businesses with moderate transaction volumes',
        client_type=ClientType.FLAT_RATE,
        monthly_price=999.00,
        annual_price=999.00 * 12 * 0.9,
        max_transactions_per_month=2000,
        max_api_calls_per_month=50000,
        max_wallets=3,
        max_volume_per_month=70000.00,
        min_margin_percent=1.42,
        is_popular=True,
        status='ACTIVE',
        sort_order=2,
        setup_fee=1000.00,
        supports_monthly=True,
        supports_annual=True,
        annual_discount_percent=10.0
    ),
    dict(
        name='Enterprise Flat Rate',
        description='Full-featured enterprise solution with unlimited scaling',
        client_type=ClientType.FLAT_RATE,
        monthly_price=2000.00,
        annual_price=2000.00 * 12 * 0.9,
        max_transactions_per_month=None,
        max_api_calls_per_month=None,
        max_wallets=None,
        max_volume_per_month=None,
        min_margin_percent=1.20,
        is_popular=False,
        status='ACTIVE',
        sort_order=3,
        setup_fee=1000.00,
        supports_monthly=True,
        supports_annual=True,
        annual_discount_percent=10.0
    ),
]

def insert_packages():
    app = create_app()
    with app.app_context():
        for pkg in flat_rate_packages:
            # Use name to check existence since slug is not a column
            exists = ClientPackage.query.filter_by(name=pkg['name']).first()
            if not exists:
                cp = ClientPackage(**pkg)
                db.session.add(cp)
        db.session.commit()
        print('Flat-rate packages inserted.')

if __name__ == '__main__':
    insert_packages()
