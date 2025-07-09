#!/usr/bin/env python3
"""
Create a test client for testing admin client management functionality
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.client import Client, ClientType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_client():
    """Create a test client for admin management testing"""
    app = create_app()
    with app.app_context():
        try:
            # Check if test client already exists
            existing_client = Client.query.filter_by(email='testclient@example.com').first()
            if existing_client:
                logger.info(f"Test client already exists with ID: {existing_client.id}")
                return existing_client.id
            
            # Create new test client
            test_client = Client(
                name='Test Client',
                company_name='Test Company Ltd',
                email='testclient@example.com',
                phone='+1234567890',
                address='123 Test Street',
                city='Test City',
                country='Test Country',
                postal_code='12345',
                is_active=True,
                is_verified=True,
                type=ClientType.INDIVIDUAL,
                api_key='test_api_key_123',
                rate_limit=1000,
                theme_color='#007bff',
                deposit_commission_rate=0.025,
                withdrawal_commission_rate=0.025,
                balance=100.50
            )
            test_client.set_password('testpass123')
            
            db.session.add(test_client)
            db.session.commit()
            
            logger.info(f"✅ Test client created successfully with ID: {test_client.id}")
            logger.info(f"Email: {test_client.email}")
            logger.info(f"Company: {test_client.company_name}")
            
            return test_client.id
            
        except Exception as e:
            logger.error(f"❌ Failed to create test client: {e}")
            db.session.rollback()
            return None

if __name__ == '__main__':
    client_id = create_test_client()
    if client_id:
        print(f"\n🎉 Test client created! Use client ID {client_id} for testing.")
        print(f"Admin URL: http://127.0.0.1:8080/admin/clients/{client_id}/view")
    else:
        print("❌ Failed to create test client")
