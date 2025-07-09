#!/usr/bin/env python3
"""
Migration script to add missing columns to the clients table.
This version handles SQLite's limitations with UNIQUE constraints.
"""
import logging
from sqlalchemy import text, inspect
from app import create_app, db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_column_exists(table_name, column_name):
    """Check if a column exists in the given table"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate_client_table():
    """Add missing columns to the clients table with SQLite-friendly approach"""
    logger.info("Starting client table migration...")
    
    # List of columns to add (without UNIQUE constraint for now)
    columns_to_add = [
        ("api_key", "VARCHAR(64)"),
        ("rate_limit", "INTEGER DEFAULT 1000"),
        ("theme_color", "VARCHAR(7)")
    ]
    
    try:
        for column_name, column_def in columns_to_add:
            if not check_column_exists('clients', column_name):
                logger.info(f"Adding column: {column_name}")
                db.session.execute(text(f"ALTER TABLE clients ADD COLUMN {column_name} {column_def}"))
                db.session.commit()
                logger.info(f"✅ Successfully added column: {column_name}")
            else:
                logger.info(f"⚠️  Column already exists: {column_name}")
        
        # Note: For api_key uniqueness, we'll handle it at the application level
        # since SQLite doesn't support adding UNIQUE constraints to existing columns
        logger.info("✅ All required columns have been added!")
        
        # Show current table structure
        logger.info("Current clients table structure:")
        inspector = inspect(db.engine)
        columns = inspector.get_columns('clients')
        for col in columns:
            logger.info(f"  - {col['name']}: {col['type']}")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        db.session.rollback()
        raise

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        migrate_client_table()
