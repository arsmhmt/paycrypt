#!/usr/bin/env python3
"""
Add package_id column to clients table for package support
"""
import os
import sys
import sqlite3
from pathlib import Path

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent))

def add_package_column():
    """Add package_id column to clients table"""
    
    # Database path
    db_path = "instance/app.db"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print("❌ Database not found at:", db_path)
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if package_id column already exists
        cursor.execute("PRAGMA table_info(clients)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'package_id' in columns:
            print("✅ package_id column already exists in clients table")
            conn.close()
            return True
        
        # Add the package_id column
        print("Adding package_id column to clients table...")
        cursor.execute("""
            ALTER TABLE clients 
            ADD COLUMN package_id INTEGER 
            REFERENCES client_packages(id)
        """)
        
        conn.commit()
        print("✅ Successfully added package_id column to clients table")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(clients)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'package_id' in columns:
            print("✅ Verified package_id column exists")
        else:
            print("❌ Failed to verify package_id column")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding package_id column: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("🔧 Adding package_id column to clients table...")
    success = add_package_column()
    
    if success:
        print("✅ Database migration completed successfully!")
        print("You can now retry running the package creation script.")
    else:
        print("❌ Database migration failed!")
        sys.exit(1)
