"""
Simple Database Migration Script
Adds the missing columns for pricing structure updates
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add app to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_migration():
    """Run the database migration to add missing columns"""
    
    # Connect to the database
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
    print(f"Connecting to database: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Creating new database...")
        # Make sure instance directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Starting database migration...")
    
    # List of migrations to run
    migrations = [
        # Add usage tracking columns to clients table
        {
            'name': 'Add usage tracking to clients',
            'sql': [
                'ALTER TABLE clients ADD COLUMN current_month_volume DECIMAL(20,2) DEFAULT 0.00',
                'ALTER TABLE clients ADD COLUMN current_month_transactions INTEGER DEFAULT 0',
                'ALTER TABLE clients ADD COLUMN last_usage_reset DATETIME',
            ]
        },
        # Add volume and margin columns to client_packages table
        {
            'name': 'Add volume limits to packages',
            'sql': [
                'ALTER TABLE client_packages ADD COLUMN max_volume_per_month DECIMAL(20,2)',
                'ALTER TABLE client_packages ADD COLUMN min_margin_percent DECIMAL(5,2) DEFAULT 1.20',
            ]
        },
        # Add slug column to client_packages table
        {
            'name': 'Add slug column to client_packages',
            'sql': [
                'ALTER TABLE client_packages ADD COLUMN slug VARCHAR(64)'
            ]
        }
    ]
    
    success_count = 0
    
    for migration in migrations:
        print(f"\n📝 Running: {migration['name']}")
        
        for sql in migration['sql']:
            try:
                cursor.execute(sql)
                print(f"   ✅ {sql}")
            except sqlite3.OperationalError as e:
                if 'duplicate column name' in str(e).lower():
                    print(f"   ⚠️  Column already exists: {sql}")
                else:
                    print(f"   ❌ Error: {e}")
                    print(f"   SQL: {sql}")
        
        success_count += 1
    
    # Commit changes
    conn.commit()
    
    print(f"\n✅ Migration completed successfully!")
    print(f"   Migrations run: {success_count}/{len(migrations)}")
    
    # Verify the changes
    print(f"\n🔍 Verifying changes...")
    
    # Check clients table structure
    cursor.execute("PRAGMA table_info(clients)")
    client_columns = [row[1] for row in cursor.fetchall()]
    
    expected_client_columns = ['current_month_volume', 'current_month_transactions', 'last_usage_reset']
    for col in expected_client_columns:
        if col in client_columns:
            print(f"   ✅ clients.{col} exists")
        else:
            print(f"   ❌ clients.{col} missing")
    
    # Check client_packages table structure
    cursor.execute("PRAGMA table_info(client_packages)")
    package_columns = [row[1] for row in cursor.fetchall()]
    
    expected_package_columns = ['max_volume_per_month', 'min_margin_percent', 'slug']
    for col in expected_package_columns:
        if col in package_columns:
            print(f"   ✅ client_packages.{col} exists")
        else:
            print(f"   ❌ client_packages.{col} missing")
    
    conn.close()
    print(f"\n🎉 Database migration completed!")

if __name__ == '__main__':
    run_migration()
