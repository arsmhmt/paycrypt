#!/usr/bin/env python3
"""
Add missing fields to Client table for admin functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Client

def add_client_fields():
    """Add missing fields to the Client table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if the table exists and get its columns
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('client')]
            
            print(f"Existing columns in Client table: {existing_columns}")
            
            # Add missing columns if they don't exist
            fields_to_add = [
                ("name", "VARCHAR(255)"),
                ("api_key", "VARCHAR(255)"),
                ("rate_limit", "INTEGER DEFAULT 100"),
                ("logo_url", "TEXT"),
                ("theme_color", "VARCHAR(7) DEFAULT '#6c63ff'"),
            ]
            
            for field_name, field_type in fields_to_add:
                if field_name not in existing_columns:
                    print(f"Adding field {field_name}...")
                    sql = f"ALTER TABLE client ADD COLUMN {field_name} {field_type}"
                    db.engine.execute(sql)
                    print(f"✓ Added {field_name}")
                else:
                    print(f"Field {field_name} already exists")
            
            db.session.commit()
            print("✓ All client fields added successfully!")
            
        except Exception as e:
            print(f"Error adding fields: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_client_fields()
