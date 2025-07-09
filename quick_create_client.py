#!/usr/bin/env python
"""
Create a test client directly using SQL
"""

import sqlite3
import hashlib
import os
from werkzeug.security import generate_password_hash
import uuid

# Configuration
DB_PATH = 'instance/app.db'  # Path to the SQLite database file
PASSWORD = 'testpassword'    # Password for the test client

def create_test_client():
    """Create a test client and user in the database"""
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return False
    
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Create a user
        username = f"testclient_{uuid.uuid4().hex[:8]}"
        email = f"{username}@example.com"
        password_hash = generate_password_hash(PASSWORD)
        
        # Insert user
        cursor.execute("""
        INSERT INTO users (username, email, password_hash, created_at, updated_at)
        VALUES (?, ?, ?, datetime('now'), datetime('now'))
        """, (username, email, password_hash))
        
        # Get the user ID
        user_id = cursor.lastrowid
        
        # 2. Find a package for the client (assuming packages exist)
        cursor.execute("SELECT id FROM client_packages LIMIT 1")
        package_result = cursor.fetchone()
        package_id = package_result[0] if package_result else None
        
        # 3. Create a client linked to the user
        client_password_hash = password_hash  # Use the same hash as the user
        cursor.execute("""
        INSERT INTO clients (user_id, package_id, username, company_name, email, is_active, is_verified, created_at, updated_at, password_hash)
        VALUES (?, ?, ?, ?, ?, 1, 1, datetime('now'), datetime('now'), ?)
        """, (user_id, package_id, username, f"Test Company {username}", email, client_password_hash))
        
        client_id = cursor.lastrowid
        
        # Commit the transaction
        conn.commit()
        
        print(f"\nCreated test client:")
        print(f"Username/Email: {email}")
        print(f"Password: {PASSWORD}")
        print(f"User ID: {user_id}")
        print(f"Client ID: {client_id}")
        print(f"Package ID: {package_id}")
        
        return True
        
    except Exception as e:
        print(f"Error creating test client: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_client()
