"""
Cleanup script to keep only 'starter', 'business', and 'enterprise' flat-rate packages in the client_packages table.
Deletes all other flat-rate packages and prints the result.
"""

from app import create_app, db
from app.models.client_package import ClientPackage, ClientType

# Slugs to keep (as mapped by the model's slug property)
KEEP_SLUGS = {'starter', 'business', 'enterprise'}

app = create_app()

with app.app_context():
    # Find all flat-rate packages
    flat_packages = ClientPackage.query.filter_by(client_type=ClientType.FLAT_RATE).all()
    keep_packages = []
    delete_packages = []
    for pkg in flat_packages:
        slug = pkg.slug
        if slug in KEEP_SLUGS and not any(p.slug == slug for p in keep_packages):
            keep_packages.append(pkg)
        else:
            delete_packages.append(pkg)
    for pkg in delete_packages:
        print(f"Deleting flat-rate package: {pkg.id} ({pkg.name}) [{pkg.slug}]")
        db.session.delete(pkg)
    db.session.commit()
    print("Flat-rate package cleanup complete. Remaining packages:")
    for pkg in keep_packages:
        print(f"  {pkg.id}: {pkg.name} [{pkg.slug}]")
    if not keep_packages:
        print("  No flat-rate packages remain!")
