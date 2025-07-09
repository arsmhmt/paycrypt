#!/usr/bin/env python3
"""
Test script to create sample withdrawal requests for testing the admin interface
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.client import Client
from app.models.client_package import ClientPackage, ClientType
from app.models.withdrawal import WithdrawalRequest, WithdrawalType, WithdrawalStatus
from app.models.user import User
from datetime import datetime

def create_sample_withdrawals():
    """Create sample withdrawal requests for testing"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Creating sample withdrawal requests...")
            
            # Get or create a test client
            client = Client.query.filter_by(email='admin@paycrypt.online').first()
            if not client:
                print("No test client found. Please create a client first.")
                return
            
            # Get or create a test user
            user = User.query.first()
            if not user:
                # Create a test user
                user = User(
                    username='testuser',
                    email='testuser@example.com',
                    password_hash='hashed_password'
                )
                db.session.add(user)
                db.session.flush()
            
            # Create user withdrawal requests (B2C)
            for i in range(3):
                withdrawal = WithdrawalRequest(
                    client_id=client.id,
                    user_id=user.id,
                    withdrawal_type=WithdrawalType.USER_REQUEST,
                    amount=100.00 + (i * 50),
                    currency='USD',
                    crypto_address='1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',  # Bitcoin address
                    status=WithdrawalStatus.PENDING,
                    created_at=datetime.utcnow()
                )
                db.session.add(withdrawal)
            
            # Create client withdrawal requests (B2B)
            for i in range(2):
                withdrawal = WithdrawalRequest(
                    client_id=client.id,
                    withdrawal_type=WithdrawalType.CLIENT_BALANCE,
                    amount=500.00 + (i * 250),
                    net_amount=475.00 + (i * 237.5),  # After fees
                    fee=25.00 + (i * 12.5),
                    currency='USD',
                    crypto_address='1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',  # Bitcoin address
                    status=WithdrawalStatus.PENDING,
                    created_at=datetime.utcnow()
                )
                db.session.add(withdrawal)
            
            # Create some approved/rejected ones for statistics
            # Approved user withdrawal
            withdrawal = WithdrawalRequest(
                client_id=client.id,
                user_id=user.id,
                withdrawal_type=WithdrawalType.USER_REQUEST,
                amount=75.00,
                currency='USD',
                crypto_address='1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
                status=WithdrawalStatus.APPROVED,
                approved_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            db.session.add(withdrawal)
            
            # Rejected client withdrawal
            withdrawal = WithdrawalRequest(
                client_id=client.id,
                withdrawal_type=WithdrawalType.CLIENT_BALANCE,
                amount=1000.00,
                currency='USD',
                crypto_address='1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
                status=WithdrawalStatus.REJECTED,
                rejection_reason='Insufficient balance',
                rejected_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            db.session.add(withdrawal)
            
            db.session.commit()
            print("✅ Sample withdrawal requests created successfully!")
            print("- 3 pending user withdrawal requests")
            print("- 2 pending client withdrawal requests")
            print("- 1 approved user withdrawal")
            print("- 1 rejected client withdrawal")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating sample data: {e}")
            return False
    
    return True

if __name__ == '__main__':
    create_sample_withdrawals()
