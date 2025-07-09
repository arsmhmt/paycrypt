"""
Cleanup script to keep only 'starter', 'business', and 'enterprise' flat-rate packages.
Deletes all other flat-rate packages and reassigns any related payments/subscriptions if needed.
"""

from app import create_app
from app.extensions import db
from app.models.client_package import ClientPackage, ClientType

app = create_app()

with app.app_context():
    # Define the slugs to keep
    keep_slugs = {'starter', 'business', 'enterprise'}
    # Map DB slugs to simplified slugs
    slug_map = {
        'starter_flat_rate': 'starter',
        'business_flat_rate': 'business',
        'enterprise_flat_rate': 'enterprise',
    }
    # Find packages to keep and delete
    flat_packages = ClientPackage.query.filter_by(client_type=ClientType.FLAT_RATE).all()
    keep_packages = {slug: None for slug in keep_slugs}
    for pkg in flat_packages:
        mapped_slug = slug_map.get(pkg.slug, pkg.slug)
        if mapped_slug in keep_slugs and keep_packages[mapped_slug] is None:
            keep_packages[mapped_slug] = pkg
    # Delete all other flat-rate packages
    for pkg in flat_packages:
        mapped_slug = slug_map.get(pkg.slug, pkg.slug)
        if mapped_slug not in keep_slugs or list(keep_packages.values()).count(pkg) > 1:
            print(f"Deleting flat-rate package: {pkg.id} ({pkg.name}) [{pkg.slug}]")
            db.session.delete(pkg)
    db.session.commit()
    print("Flat-rate package cleanup complete. Remaining packages:")
    for slug, pkg in keep_packages.items():
        if pkg:
            print(f"  {slug}: {pkg.id} ({pkg.name}) [{pkg.slug}]")
        else:
            print(f"  {slug}: MISSING!")
