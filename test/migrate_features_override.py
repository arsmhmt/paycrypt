#!/usr/bin/env python3
"""
Database Migration: Add features_override column to clients table

This script adds the features_override column to support manual feature overrides.
"""

import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_database():
    """Add features_override column to clients table"""
    print("🔄 Starting Database Migration...")
    print("=" * 60)
    
    try:
        from app import create_app
        from app.extensions import db
        
        app = create_app()
        
        with app.app_context():
            # Check if column already exists
            inspector = db.inspect(db.engine)
            columns = [column['name'] for column in inspector.get_columns('clients')]
            
            if 'features_override' in columns:
                print("✅ Column 'features_override' already exists in clients table")
                return True
            
            print("📝 Adding 'features_override' column to clients table...")
            
            # Add the column using raw SQL
            try:
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE clients ADD COLUMN features_override TEXT"))
                    conn.commit()
                print("✅ Successfully added 'features_override' column")
                
                # Update existing records to have empty list
                with db.engine.connect() as conn:
                    conn.execute(db.text("UPDATE clients SET features_override = '[]' WHERE features_override IS NULL"))
                    conn.commit()
                print("✅ Initialized existing records with empty feature overrides")
                
                return True
                
            except Exception as e:
                print(f"❌ Error adding column: {str(e)}")
                return False
                
    except Exception as e:
        print(f"💥 Fatal error during migration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verify_migration():
    """Verify the migration was successful"""
    print("\n🔍 Verifying migration...")
    print("=" * 60)
    
    try:
        from app import create_app
        from app.extensions import db
        
        app = create_app()
        
        with app.app_context():
            inspector = db.inspect(db.engine)
            columns = [column['name'] for column in inspector.get_columns('clients')]
            
            if 'features_override' in columns:
                print("✅ Migration verified: 'features_override' column exists")
                
                # Check if we can query it
                with db.engine.connect() as conn:
                    result = conn.execute(db.text("SELECT COUNT(*) FROM clients WHERE features_override IS NOT NULL"))
                    count = result.fetchone()[0]
                print(f"✅ Found {count} client records with features_override data")
                
                return True
            else:
                print("❌ Migration failed: 'features_override' column not found")
                return False
                
    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Database Migration Tool")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run migration
    success = migrate_database()
    
    if success:
        # Verify the migration worked
        verify_migration()
        
        print(f"\n🏁 Migration completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n🎉 You can now run the sync_client_status.py script!")
        return True
    else:
        print("\n💥 Migration failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
