#!/usr/bin/env python
"""
Fix the test client's password hash
"""

import sqlite3
from werkzeug.security import generate_password_hash

# Configuration
DB_PATH = 'instance/app.db'
CLIENT_EMAIL = 'testclient_85120b7e@example.com'
PASSWORD = 'testpassword'

def fix_client_password():
    """Fix the client's password hash"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Generate proper password hash
        password_hash = generate_password_hash(PASSWORD)
        
        # Update the client's password
        cursor.execute("""
        UPDATE clients SET password_hash = ? WHERE email = ?
        """, (password_hash, CLIENT_EMAIL))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ Updated password hash for client: {CLIENT_EMAIL}")
        else:
            print(f"❌ No client found with email: {CLIENT_EMAIL}")
            
    except Exception as e:
        print(f"❌ Error updating password: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_client_password()
