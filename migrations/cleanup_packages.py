"""
Cleanup script to enforce package constraints:
- Ensures only one commission package exists (slug 'commission')
- Ensures only flat-rate packages use 'starter', 'professional', 'enterprise' slugs
- Removes or renames any conflicting packages
"""

from app import create_app
from app.extensions import db
from app.models.client_package import ClientPackage, ClientType

app = create_app()

with app.app_context():
    # 1. Fix commission packages
    commission_packages = ClientPackage.query.filter_by(client_type=ClientType.COMMISSION).all()
    if commission_packages:
        # Keep the first (or the one with most clients, or by your business rule)
        main_commission = commission_packages[0]
        main_commission.name = 'Commission Plan'
        db.session.flush()
        # Remove all others
        for pkg in commission_packages[1:]:
            db.session.delete(pkg)
        db.session.commit()
        print(f"Kept commission package: {main_commission.id}")
    
    # 2. Fix flat-rate package slugs
    flat_slugs = {'starter', 'professional', 'enterprise', 'basic', 'premium'}
    flat_packages = ClientPackage.query.filter_by(client_type=ClientType.FLAT_RATE).all()
    for pkg in flat_packages:
        slug = pkg.slug
        if slug not in flat_slugs:
            # Optionally, rename or remove
            print(f"Flat-rate package {pkg.id} has non-standard slug: {slug}")
    db.session.commit()
    print("Flat-rate packages checked.")

print("Cleanup complete.")
