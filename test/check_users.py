#!/usr/bin/env python3
"""
Check existing users in the database
"""
from app import create_app
from app.models.admin import AdminUser
from app.models.client import Client

app = create_app()
with app.app_context():
    print("=== ADMIN USERS ===")
    admins = AdminUser.query.all()
    if admins:
        for admin in admins:
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Active: {admin.is_active}")
            print(f"Superuser: {admin.is_superuser}")
            print("---")
    else:
        print("No admin users found")
    
    print("\n=== CLIENT USERS ===")
    clients = Client.query.all()
    if clients:
        for client in clients:
            print(f"Username: {getattr(client, 'username', 'N/A')}")
            print(f"Email: {client.email}")
            print(f"Company: {client.company_name}")
            print(f"Active: {client.is_active}")
            print(f"Verified: {client.is_verified}")
            print("---")
    else:
        print("No client users found")
