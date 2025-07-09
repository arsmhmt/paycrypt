#!/usr/bin/env python3
"""
Check and fix client type enum values in database
"""
import sqlite3
import os

def check_client_types():
    """Check current client type values in database"""
    db_path = "instance/app.db"
    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current client types
        cursor.execute("SELECT id, type FROM clients LIMIT 10")
        clients = cursor.fetchall()
        
        print("Current client types in database:")
        for client_id, client_type in clients:
            print(f"  Client ID {client_id}: '{client_type}'")
        
        # Count different type values
        cursor.execute("SELECT type, COUNT(*) FROM clients GROUP BY type")
        type_counts = cursor.fetchall()
        
        print("\nType distribution:")
        for type_val, count in type_counts:
            print(f"  '{type_val}': {count} clients")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

def fix_client_types():
    """Fix client type enum values to match the model"""
    db_path = "instance/app.db"
    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Fixing client type enum values...")
        
        # Update lowercase to uppercase
        cursor.execute("UPDATE clients SET type = 'INDIVIDUAL' WHERE type = 'individual'")
        individual_updated = cursor.rowcount
        
        cursor.execute("UPDATE clients SET type = 'COMPANY' WHERE type = 'company'")
        company_updated = cursor.rowcount
        
        # Handle any NULL or other values
        cursor.execute("UPDATE clients SET type = 'INDIVIDUAL' WHERE type IS NULL OR type NOT IN ('INDIVIDUAL', 'COMPANY')")
        null_updated = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"✅ Updated {individual_updated} clients from 'individual' to 'INDIVIDUAL'")
        print(f"✅ Updated {company_updated} clients from 'company' to 'COMPANY'")
        if null_updated > 0:
            print(f"✅ Updated {null_updated} clients with NULL/invalid types to 'INDIVIDUAL'")
        
        print("✅ Client type enum values fixed!")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == '__main__':
    print("🔍 CHECKING CLIENT TYPE ENUM VALUES")
    print("=" * 50)
    
    check_client_types()
    
    print("\n" + "=" * 50)
    fix_client_types()
    
    print("\n" + "=" * 50)
    print("🔍 VERIFYING FIXES")
    print("=" * 50)
    
    check_client_types()
