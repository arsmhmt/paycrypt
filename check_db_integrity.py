import os
import sqlite3

def check_database_integrity():
    db_path = os.path.join('instance', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at: {os.path.abspath(db_path)}")
        return
    
    print(f"Database file: {os.path.abspath(db_path)}")
    print(f"Size: {os.path.getsize(db_path)} bytes\n")
    
    try:
        # Try to open and check the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the database is empty
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("The database is empty (no tables found).")
        else:
            print(f"Found {len(tables)} tables in the database:")
            for table in tables:
                print(f"- {table[0]}")
        
        # Check database integrity
        print("\nChecking database integrity...")
        try:
            cursor.execute("PRAGMA integrity_check;")
            result = cursor.fetchone()
            print(f"Integrity check: {result[0]}")
        except sqlite3.DatabaseError as e:
            print(f"Error checking database integrity: {e}")
        
        # Check if we can read the schema
        print("\nDatabase schema:")
        cursor.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL;")
        schemas = cursor.fetchall()
        
        if not schemas:
            print("No schema information found in the database.")
        else:
            for schema in schemas:
                print(schema[0])
        
        conn.close()
        
    except sqlite3.DatabaseError as e:
        print(f"\nDatabase error: {e}")
        print("The database file might be corrupted or not a valid SQLite database.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    check_database_integrity()
