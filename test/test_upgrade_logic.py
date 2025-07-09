#!/usr/bin/env python3
"""
Test the new upgrade logic for commission-based clients
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.extensions.extensions import db
from app.models import Client, ClientPackage
from app.config.packages import PACKAGE_FEATURES, PACKAGE_DISPLAY_NAMES

def test_upgrade_logic():
    """Test upgrade logic for different client types"""
    
    app = create_app()
    
    with app.app_context():
        print("=== TESTING UPGRADE LOGIC ===\n")
        
        # Get all clients
        clients = Client.query.filter(Client.username.isnot(None)).limit(5).all()
        
        for client in clients:
            print(f"👤 Client: {client.username}")
            
            if client.package:
                package = client.package
                package_slug = package.slug
                is_commission = client.is_commission_based()
                is_flat_rate = client.is_flat_rate()
                
                print(f"   Package: {package.name} ({package_slug})")
                print(f"   Type: {'Commission' if is_commission else 'Flat Rate' if is_flat_rate else 'Unknown'}")
                
                # Apply upgrade logic
                if is_commission:
                    upgrade_package = 'professional_flat_rate'
                    upgrade_name = 'Flat-Rate Enterprise'
                    upgrade_reason = 'Switch to flat-rate pricing and unlock all enterprise features'
                    show_upgrade = True
                elif is_flat_rate:
                    if package_slug == 'basic_flat_rate':
                        upgrade_package = 'premium_flat_rate'
                        upgrade_name = 'Premium Flat Rate'
                        upgrade_reason = 'Unlock advanced analytics and priority support'
                        show_upgrade = True
                    elif package_slug == 'premium_flat_rate':
                        upgrade_package = 'professional_flat_rate'
                        upgrade_name = 'Professional Flat Rate'
                        upgrade_reason = 'Get real-time dashboard and all enterprise features'
                        show_upgrade = True
                    else:
                        show_upgrade = False
                        upgrade_name = "Already at highest tier"
                        upgrade_reason = "No upgrade available"
                else:
                    upgrade_package = 'premium_flat_rate'
                    upgrade_name = 'Premium Plan'
                    upgrade_reason = 'Get started with advanced features'
                    show_upgrade = True
                
                print(f"   Upgrade Recommendation: {upgrade_name}")
                print(f"   Show Upgrade: {'✅ Yes' if show_upgrade else '❌ No'}")
                print(f"   Reason: {upgrade_reason}")
                
            else:
                print(f"   Package: No package assigned")
                print(f"   Upgrade Recommendation: Premium Plan")
                print(f"   Show Upgrade: ✅ Yes")
            
            print()

if __name__ == "__main__":
    test_upgrade_logic()
