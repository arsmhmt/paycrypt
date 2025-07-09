#!/usr/bin/env python3
"""Check current packages in the database"""

from app import create_app
from app.models.client_package import ClientPackage

app = create_app()
with app.app_context():
    packages = ClientPackage.query.all()
    print("Current packages:")
    for p in packages:
        print(f"- {p.name} ({p.slug})")
        print(f"  Type: {p.client_type.value if hasattr(p.client_type, 'value') else p.client_type}")
        print(f"  Price: ${p.monthly_price if p.monthly_price else 'commission'}")
        print(f"  Volume: {p.max_volume_per_month if p.max_volume_per_month else 'unlimited'}")
        print(f"  Status: {p.status.value if hasattr(p.status, 'value') else p.status}")
        print()
