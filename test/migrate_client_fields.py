#!/usr/bin/env python3
"""
Database migration script to add missing fields to Client table
Run this script to add the missing fields needed for the admin client management
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.extensions.extensions import db
from app.models.client import Client
from sqlalchemy import text

def migrate_client_table():
    """Add missing fields to the Client table"""
    try:
        # Check if columns exist before adding them
        inspector = db.inspect(db.engine)
        existing_columns = [col['name'] for col in inspector.get_columns('clients')]
        
        migrations = []
        
        # Add name field if missing
        if 'name' not in existing_columns:
            migrations.append("ALTER TABLE clients ADD COLUMN name VARCHAR(255)")
            
        # Add api_key field if missing
        if 'api_key' not in existing_columns:
            migrations.append("ALTER TABLE clients ADD COLUMN api_key VARCHAR(64) UNIQUE")
            
        # Add rate_limit field if missing
        if 'rate_limit' not in existing_columns:
            migrations.append("ALTER TABLE clients ADD COLUMN rate_limit INTEGER DEFAULT 100")
            
        # Add theme_color field if missing
        if 'theme_color' not in existing_columns:
            migrations.append("ALTER TABLE clients ADD COLUMN theme_color VARCHAR(7) DEFAULT '#6c63ff'")
        
        # Execute migrations
        if migrations:
            print(f"Executing {len(migrations)} database migrations...")
            for migration in migrations:
                print(f"  - {migration}")
                db.session.execute(text(migration))
            
            db.session.commit()
            print("✅ Database migration completed successfully!")
        else:
            print("✅ No migrations needed - all columns already exist!")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.session.rollback()
        raise

if __name__ == '__main__':
    # Import the app to initialize the database
    from app import create_app
    
    app = create_app()
    with app.app_context():
        migrate_client_table()
