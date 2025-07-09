#!/usr/bin/env python
"""
Create test clients for different package types (B2B and B2C)
"""

import sys
import logging
from datetime import datetime
from flask import Flask
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models.client import Client
from app.models.user import User
from app.models.client_package import ClientPackage, ClientType

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger('create_clients')

def create_test_clients():
    """Create test clients for each package type"""
    
    # Create app with development config
    app = create_app()
    app.app_context().push()
    
    logger.info("Finding available packages...")
    
    # Get packages
    b2c_package = ClientPackage.query.filter_by(name='B2C Commission').first()
    b2b_package = ClientPackage.query.filter_by(name='B2B Flat Rate').first()
    
    if not b2c_package or not b2b_package:
        logger.error("Required packages not found! Run create_client_packages.py first")
        return False
    
    logger.info(f"Found packages: B2C ({b2c_package.id}) and B2B ({b2b_package.id})")
    
    # Create test clients
    test_clients = [
        {
            'email': 'b2c@example.com',
            'username': 'b2c_client',
            'company_name': 'B2C Test Company',
            'password': 'testpassword',
            'package_id': b2c_package.id,
            'type': 'B2C (Commission)'
        },
        {
            'email': 'b2b@example.com',
            'username': 'b2b_client',
            'company_name': 'B2B Test Company',
            'password': 'testpassword',
            'package_id': b2b_package.id,
            'type': 'B2B (Flat Rate)'
        }
    ]
    
    for client_data in test_clients:
        client_type = client_data.pop('type')
        password = client_data.pop('password')
        
        # Check if client already exists
        existing = Client.query.filter_by(email=client_data['email']).first()
        if existing:
            logger.info(f"{client_type} client already exists: {existing.email} (ID: {existing.id})")
            continue
            
        # Create a new client
        client = Client(**client_data)
        client.password_hash = generate_password_hash(password)
        client.is_active = True
        client.is_verified = True
        
        db.session.add(client)
        db.session.flush()  # Get ID without committing
        
        # Create a user for this client
        user = User(
            username=client_data['username'],
            email=client_data['email']
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.flush()  # Get user ID without committing
        
        # Link the user to the client
        client.user_id = user.id
        
        db.session.commit()
        logger.info(f"Created {client_type} client: {client.email} (ID: {client.id}, User ID: {user.id})")
    
    logger.info("All test clients created successfully!")
    return True

def main():
    try:
        success = create_test_clients()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Error creating test clients: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
