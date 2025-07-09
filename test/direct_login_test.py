"""
Direct Client Login Test

This script bypasses the form and directly logs in the client using the Flask-Login library.
"""

from flask import Flask, session
from flask_login import login_user, current_user
from app import create_app
from app.models import Client, User
from app.extensions import db, login_manager
import sys

def test_client_login():
    # Get test client
    client = Client.query.filter_by(email="testclient@example.com").first()
    if not client:
        print("Error: Test client not found!")
        return False
        
    print(f"Found client: {client.company_name} (ID: {client.id})")
    
    # Get or create user
    user = None
    if client.user_id:
        user = User.query.get(client.user_id)
        print(f"Found existing user: {user.username} (ID: {user.id})")
    
    if not user:
        # Create user
        user = User(
            username=client.email,
            email=client.email
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.flush()
        
        # Link user to client
        client.user_id = user.id
        db.session.commit()
        print(f"Created new user: {user.username} (ID: {user.id})")
    
    # Direct login via login_user
    print(f"Attempting login for user {user.id}...")
    result = login_user(user, remember=True)
    print(f"Login result: {result}")
    
    # Verify authentication
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        print(f"Current user authenticated: {current_user.username}")
        return True
    else:
        print("Authentication failed!")
        return False

# Create app and run in context
if __name__ == "__main__":
    app = create_app()
    with app.test_request_context():
        if test_client_login():
            print("✅ Direct login successful!")
            print(f"Session contains: {session.keys()}")
            sys.exit(0)
        else:
            print("❌ Direct login failed!")
            sys.exit(1)
