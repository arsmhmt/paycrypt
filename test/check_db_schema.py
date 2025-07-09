import sqlite3
import os

# Check if the database exists and what tables/columns are there
db_paths = ['instance/app.db', 'app.db', 'data/dev.db', 'instance/dev.db']

for db_path in db_paths:
    if os.path.exists(db_path):
        print(f'Found database: {db_path}')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if payments table exists
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="payments"')
        if cursor.fetchone():
            print('payments table exists')
            # Get column info for payments table
            cursor.execute('PRAGMA table_info(payments)')
            columns = cursor.fetchall()
            print('Columns in payments table:')
            for col in columns:
                print(f'  {col[1]} ({col[2]})')
        else:
            print('payments table does not exist')
        
        # Check alembic version table
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="alembic_version"')
        if cursor.fetchone():
            cursor.execute('SELECT version_num FROM alembic_version')
            version = cursor.fetchone()
            print(f'Current migration version: {version[0] if version else "None"}')
        else:
            print('alembic_version table does not exist')
        
        conn.close()
        break
else:
    print('No database found')
