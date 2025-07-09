#!/usr/bin/env python3
"""
Check client package details for upgrade logic
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.extensions.extensions import db
from app.models import Client, ClientPackage
from app.config.packages import PACKAGE_DISPLAY_NAMES

def check_client_package():
    """Check smartbetslip client package details"""
    
    app = create_app()
    
    with app.app_context():
        # Find smartbetslip client
        client = Client.query.filter_by(client_id='smartbetslip').first()
        
        if not client:
            print("❌ Client 'smartbetslip' not found")
            return
        
        print(f"🔍 Client: {client.client_id}")
        print(f"   Status: {client.status}")
        print(f"   Account Type: {client.account_type}")
        
        # Get client packages
        packages = ClientPackage.query.filter_by(client_id=client.id).all()
        print(f"   Packages: {len(packages)}")
        
        for pkg in packages:
            display_name = PACKAGE_DISPLAY_NAMES.get(pkg.package_slug, pkg.package_slug)
            print(f"     • Package Slug: {pkg.package_slug}")
            print(f"     • Display Name: {display_name}")
            print(f"     • Status: {pkg.status}")
            print(f"     • Created: {pkg.created_at}")
        
        # Check if client has a package attribute (from relationships)
        if hasattr(client, 'package') and client.package:
            print(f"   Package Relationship: {client.package}")
            if hasattr(client.package, 'name'):
                print(f"   Package Name: {client.package.name}")
        
        # Show all available packages for upgrade logic
        print(f"\n📦 All Available Packages:")
        for slug, name in PACKAGE_DISPLAY_NAMES.items():
            print(f"   • {slug} → {name}")

if __name__ == "__main__":
    check_client_package()
