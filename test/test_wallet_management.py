#!/usr/bin/env python3
"""
Test wallet management implementation for flat-rate clients
"""

from app import create_app
from app.models.client import Client
from app.models.client_wallet import ClientWallet, WalletType, WalletStatus

app = create_app()
with app.app_context():
    # Check if we have any flat-rate clients
    clients = Client.query.all()
    print('=== CLIENT WALLET MANAGEMENT STATUS ===')
    print(f'Total clients: {len(clients)}')
    
    for client in clients:
        print(f'\nClient: {client.name} ({client.email})')
        pkg_name = client.package.name if client.package else 'None'
        print(f'  - Package: {pkg_name}')
        client_type = client.get_client_type().name if client.get_client_type() else 'None'
        print(f'  - Client Type: {client_type}')
        print(f'  - Is Flat-Rate: {client.is_flat_rate()}')
        has_wallet_mgmt = client.has_feature('wallet_management')
        print(f'  - Has Wallet Management: {has_wallet_mgmt}')
        print(f'  - Configured Wallets: {len(client.wallets)}')
        
        # Show wallet details
        for wallet in client.wallets:
            print(f'    * {wallet.wallet_name} ({wallet.wallet_type.value}) - {wallet.status.value}')
    
    print('\n=== WALLET MANAGEMENT SUMMARY ===')
    flat_rate_clients = [c for c in clients if c.is_flat_rate()]
    print(f'Flat-rate clients: {len(flat_rate_clients)}')
    
    clients_with_wallet_mgmt = [c for c in clients if c.has_feature('wallet_management')]
    print(f'Clients with wallet management: {len(clients_with_wallet_mgmt)}')
    
    clients_need_wallets = [c for c in flat_rate_clients if len(c.wallets) == 0]
    print(f'Flat-rate clients without wallets: {len(clients_need_wallets)}')
    
    if clients_need_wallets:
        print('\nCLIENTS NEEDING WALLET CONFIGURATION:')
        for client in clients_need_wallets:
            print(f'  - {client.name} ({client.email})')
