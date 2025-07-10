from app import create_app
from app.extensions.extensions import db
from sqlalchemy import text
from datetime import datetime

def add_updated_at_column():
    app = create_app()
    with app.app_context():
        # Check if the column already exists
        inspector = db.inspect(db.engine)
        columns = [column['name'] for column in inspector.get_columns('features')]
        
        if 'updated_at' not in columns:
            print("Adding 'updated_at' column to 'features' table...")
            
            with db.engine.connect() as conn:
                # First, add the column without a default value
                conn.execute(text('''
                    ALTER TABLE features 
                    ADD COLUMN updated_at DATETIME
                '''))
                
                # Then update all existing rows with the current timestamp
                conn.execute(text('''
                    UPDATE features 
                    SET updated_at = :now
                '''), {'now': datetime.utcnow()})
                
                # Finally, set the default value for future inserts
                # Note: SQLite doesn't support ALTER COLUMN to set default after creation
                # So we'll need to create a new table and copy the data
                
                # 1. Rename existing table
                conn.execute(text('ALTER TABLE features RENAME TO features_old'))
                
                # 2. Create new table with the default value
                conn.execute(text('''
                    CREATE TABLE features (
                        id INTEGER NOT NULL, 
                        name VARCHAR(100) NOT NULL, 
                        description TEXT, 
                        feature_key VARCHAR(50) NOT NULL, 
                        category VARCHAR(50), 
                        is_premium BOOLEAN, 
                        created_at DATETIME, 
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
                        PRIMARY KEY (id), 
                        UNIQUE (name), 
                        UNIQUE (feature_key)
                    )
                '''))
                
                # 3. Copy data from old table to new table
                conn.execute(text('''
                    INSERT INTO features 
                    SELECT id, name, description, feature_key, category, is_premium, created_at, updated_at 
                    FROM features_old
                '''))
                
                # 4. Drop the old table
                conn.execute(text('DROP TABLE features_old'))
                
                conn.commit()
                
            print("Successfully added 'updated_at' column to 'features' table with default value.")
        else:
            print("'updated_at' column already exists in 'features' table.")

if __name__ == '__main__':
    add_updated_at_column()
