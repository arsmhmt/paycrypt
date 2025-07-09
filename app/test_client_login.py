"""
Test Client Login Script

This script provides a simplified way to test client login functionality.
It creates a test client if one doesn't exist and attempts to log in.
"""

from app import create_app
from app.models import Client, User
from app.extensions import db
from flask_login import login_user
from werkzeug.security import generate_password_hash
from flask import session
import os
import sys

def create_test_client_if_not_exists():
    """Create a test client if one doesn't exist"""
    # Email for test client
    email = "testclient@example.com"
    
    # Check if client already exists
    client = Client.query.filter_by(email=email).first()
    if client:
        print(f"Test client already exists with ID: {client.id}")
        return client
        
    # Create new test client
    client = Client(
        company_name="Test Company",
        email=email,
        username="testclient",
        contact_person="Test Person",
        is_active=True,
        is_verified=True,
        deposit_commission_rate=0.035,
        withdrawal_commission_rate=0.015,
    )
    client.set_password("password123")
    
    # Create user for test client
    user = User(
        username=email,
        email=email
    )
    user.set_password("password123")
    db.session.add(user)
    db.session.flush()
    
    # Link user to client
    client.user_id = user.id
    db.session.add(client)
    db.session.commit()
    
    print(f"Created test client with ID: {client.id}")
    return client

def login_test_client():
    """Log in as test client and print session info"""
    # Ensure test client exists
    client = create_test_client_if_not_exists()
    
    # Get associated user
    user = User.query.get(client.user_id)
    if not user:
        print("Error: No user associated with test client!")
        return False
    
    # Log in with Flask-Login
    result = login_user(user)
    print(f"Login result: {result}")
    
    # Print session info
    print(f"Session keys: {list(session.keys())}")
    print(f"User ID in session: {session.get('_user_id')}")
    
    return result

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        if login_test_client():
            print("✅ Test client logged in successfully!")
        else:
            print("❌ Test client login failed!")
            sys.exit(1)
