#!/usr/bin/env python3
"""
Add missing columns to client_packages table
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db

def add_missing_columns():
    """Add missing columns to client_packages table"""
    app = create_app()
    with app.app_context():
        print("Adding missing columns to client_packages table...")
        
        # List of columns to add
        columns_to_add = [
            'annual_price NUMERIC(10, 2)',
            'setup_fee NUMERIC(10, 2) DEFAULT 1000.00',
            'supports_monthly BOOLEAN DEFAULT 1',
            'supports_annual BOOLEAN DEFAULT 1', 
            'annual_discount_percent NUMERIC(5, 2) DEFAULT 10.0'
        ]
        
        for column in columns_to_add:
            try:
                sql = f"ALTER TABLE client_packages ADD COLUMN {column}"
                db.session.execute(db.text(sql))
                print(f"  Added column: {column}")
            except Exception as e:
                if 'duplicate column' in str(e).lower():
                    print(f"  Column already exists: {column.split()[0]}")
                else:
                    print(f"  Error adding {column}: {e}")
        
        db.session.commit()
        print("Done!")

if __name__ == '__main__':
    add_missing_columns()
