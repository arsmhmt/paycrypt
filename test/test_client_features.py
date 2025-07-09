#!/usr/bin/env python3
"""
Test client features
"""
from app import create_app
from app.models.client import Client

app = create_app()
with app.app_context():
    # Test premium client
    client = Client.query.filter_by(company_name='SMARTBETSLİP').first()
    print(f"=== Premium Client Test ===")
    print(f"Client: {client.company_name}")
    
    pkg = client.get_current_package()
    print(f"Package: {pkg.name if pkg else 'None'}")
    
    print(f"Has API Basic: {client.has_feature('api_basic')}")
    print(f"Has Analytics: {client.has_feature('dashboard_analytics')}")
    print(f"Has Advanced API: {client.has_feature('api_advanced')}")
    print(f"Has Wallet Management: {client.has_feature('wallet_management')}")
    print(f"Has Priority Support: {client.has_feature('support_priority')}")
    
    # Test basic client
    client2 = Client.query.filter_by(company_name='PAYCRYPT').first()
    print(f"\n=== Basic Client Test ===")
    print(f"Client: {client2.company_name}")
    
    pkg2 = client2.get_current_package()
    print(f"Package: {pkg2.name if pkg2 else 'None'}")
    
    print(f"Has API Basic: {client2.has_feature('api_basic')}")
    print(f"Has Analytics: {client2.has_feature('dashboard_analytics')}")
    print(f"Has Advanced API: {client2.has_feature('api_advanced')}")
    print(f"Has Wallet Management: {client2.has_feature('wallet_management')}")
    print(f"Has Priority Support: {client2.has_feature('support_priority')}")
