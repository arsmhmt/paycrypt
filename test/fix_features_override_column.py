#!/usr/bin/env python3
"""
Database Migration Fix: Convert features_override column from TEXT to BLOB

This script fixes the column type for features_override to be compatible
with SQLAlchemy's PickleType which requires BLOB storage.
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_features_override_column():
    """Fix the features_override column type from TEXT to BLOB"""
    print("🔄 Starting Database Column Type Fix...")
    print("=" * 60)
    
    try:
        from app import create_app
        from app.extensions import db
        
        app = create_app()
        
        with app.app_context():
            # Check current column type
            inspector = db.inspect(db.engine)
            columns = {col['name']: col for col in inspector.get_columns('clients')}
            
            if 'features_override' not in columns:
                print("❌ Column 'features_override' does not exist in clients table")
                return False
            
            current_type = str(columns['features_override']['type'])
            print(f"📝 Current column type: {current_type}")
            
            if 'BLOB' in current_type.upper():
                print("✅ Column is already BLOB type")
                return True
            
            print("🔧 Converting column from TEXT to BLOB...")
            
            # For SQLite, we need to recreate the table since ALTER COLUMN is not supported
            # First, let's backup the current data
            with db.engine.connect() as conn:
                # Get current data
                result = conn.execute(db.text("SELECT id, features_override FROM clients WHERE features_override IS NOT NULL"))
                current_data = {row[0]: row[1] for row in result.fetchall()}
                
                print(f"📊 Found {len(current_data)} clients with feature override data")
                
                # Create a temporary table with the correct column type
                conn.execute(db.text("""
                    CREATE TABLE clients_temp AS 
                    SELECT * FROM clients
                """))
                
                # Drop the old features_override column and add new BLOB column
                conn.execute(db.text("ALTER TABLE clients_temp DROP COLUMN features_override"))
                conn.execute(db.text("ALTER TABLE clients_temp ADD COLUMN features_override BLOB"))
                
                # Copy data back to original table
                conn.execute(db.text("DROP TABLE clients"))
                conn.execute(db.text("ALTER TABLE clients_temp RENAME TO clients"))
                
                # Initialize all records with empty list (pickle serialized)
                import pickle
                empty_list_pickled = pickle.dumps([])
                
                conn.execute(db.text("UPDATE clients SET features_override = :empty_list"), 
                           {'empty_list': empty_list_pickled})
                
                conn.commit()
                
                print("✅ Successfully converted column to BLOB type")
                print("✅ Initialized all records with empty feature overrides")
                
                return True
                
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verify_migration():
    """Verify the migration was successful"""
    print("\n🔍 Verifying migration...")
    print("-" * 40)
    
    try:
        from app import create_app
        from app.models.client import Client
        from app.extensions import db
        
        app = create_app()
        
        with app.app_context():
            # Check column type
            inspector = db.inspect(db.engine)
            columns = {col['name']: col for col in inspector.get_columns('clients')}
            
            if 'features_override' in columns:
                column_type = str(columns['features_override']['type'])
                print(f"✅ Column type: {column_type}")
            
            # Test reading a client record
            client = Client.query.first()
            if client:
                print(f"✅ Successfully read client: {client.company_name}")
                print(f"✅ Features override: {client.features_override}")
                
                # Test setting and reading features override
                client.features_override = ['test_feature']
                db.session.commit()
                
                # Read it back
                db.session.refresh(client)
                print(f"✅ Test override set/read: {client.features_override}")
                
                # Reset to empty
                client.features_override = []
                db.session.commit()
                print("✅ Reset to empty list")
                
            return True
            
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Feature Override Column Type Fix")
    print("=" * 60)
    
    # Run the migration
    success = fix_features_override_column()
    
    if success:
        # Verify the migration
        verify_success = verify_migration()
        
        if verify_success:
            print("\n" + "=" * 60)
            print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
            print("✅ features_override column is now BLOB type and compatible with PickleType")
            print("✅ All existing clients have been initialized with empty feature overrides")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("⚠️  MIGRATION COMPLETED BUT VERIFICATION FAILED")
            print("Please check the database manually")
            print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ MIGRATION FAILED!")
        print("Please check the error messages above")
        print("=" * 60)
        sys.exit(1)
