#!/usr/bin/env python3
"""
Check smartbetslip client package details
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.extensions.extensions import db
from app.models import Client, ClientPackage
from app.config.packages import PACKAGE_FEATURES, PACKAGE_DISPLAY_NAMES

def check_smartbetslip():
    """Check smartbetslip client package details"""
    
    app = create_app()
    
    with app.app_context():
        # Find smartbetslip client
        client = Client.query.filter_by(client_id='smartbetslip').first()
        
        if not client:
            print("❌ Client 'smartbetslip' not found")
            return
        
        print(f"👤 Client: {client.client_id}")
        print(f"   Company: {client.company_name}")
        print(f"   Status: {client.status}")
        print(f"   Account Type: {client.account_type}")
        
        # Get client packages
        packages = ClientPackage.query.filter_by(client_id=client.id).all()
        print(f"   Packages: {len(packages)}")
        
        for pkg in packages:
            display_name = PACKAGE_DISPLAY_NAMES.get(pkg.package_slug, pkg.package_slug)
            features = PACKAGE_FEATURES.get(pkg.package_slug, [])
            print(f"     • {display_name} ({pkg.package_slug})")
            print(f"       Features: {', '.join(features) if features else 'None'}")
            
            # Determine package type
            if 'commission' in pkg.package_slug:
                package_type = 'commission'
            elif 'flat_rate' in pkg.package_slug:
                package_type = 'flat_rate'
            else:
                package_type = 'unknown'
            
            print(f"       Type: {package_type}")
            
            # Determine upgrade recommendation
            if package_type == 'commission':
                recommended_upgrade = 'professional_flat_rate'  # Flat-rate enterprise
            elif package_type == 'flat_rate':
                if pkg.package_slug == 'basic_flat_rate':
                    recommended_upgrade = 'premium_flat_rate'
                elif pkg.package_slug == 'premium_flat_rate':
                    recommended_upgrade = 'professional_flat_rate'
                else:
                    recommended_upgrade = None  # Already at highest
            else:
                recommended_upgrade = 'premium_flat_rate'
            
            print(f"       Recommended Upgrade: {recommended_upgrade}")
            if recommended_upgrade:
                upgrade_display = PACKAGE_DISPLAY_NAMES.get(recommended_upgrade, recommended_upgrade)
                print(f"       Upgrade Display Name: {upgrade_display}")

if __name__ == "__main__":
    check_smartbetslip()
