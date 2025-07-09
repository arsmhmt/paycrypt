#!/usr/bin/env python3
"""
Migration: Add Usage Alerts Tracking Table
Creates table to track sent usage alerts and prevent duplicates
"""

from app import create_app
from app.extensions.extensions import db
from app.models.usage_alert import UsageAlert

def migrate_usage_alerts():
    """Create usage alerts tracking table"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Creating usage alerts tracking table...")
        
        try:
            # Create the table
            db.create_all()
            print("✅ Usage alerts table created successfully")
            
            # Check table exists
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'usage_alerts' in tables:
                print(f"✅ Confirmed: usage_alerts table exists")
                
                # Show table structure
                columns = inspector.get_columns('usage_alerts')
                print(f"📋 Table columns:")
                for col in columns:
                    print(f"   - {col['name']}: {col['type']}")
                    
            else:
                print("❌ Warning: usage_alerts table not found after creation")
                
        except Exception as e:
            print(f"❌ Error creating usage alerts table: {e}")
            raise

if __name__ == '__main__':
    migrate_usage_alerts()
