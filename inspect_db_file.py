import os
import sqlite3
import binascii

def inspect_database_file():
    db_path = os.path.join('instance', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at: {os.path.abspath(db_path)}")
        return
    
    print(f"Database file: {os.path.abspath(db_path)}")
    print(f"Size: {os.path.getsize(db_path)} bytes\n")
    
    # Check if the file is a valid SQLite database
    with open(db_path, 'rb') as f:
        header = f.read(16)
        print(f"SQLite header: {binascii.hexlify(header).decode('ascii')}")
        
        # SQLite database file header starts with "SQLite format 3\000"
        if header.startswith(b'SQLite format 3\x00'):
            print("This appears to be a valid SQLite database file.")
        else:
            print("WARNING: This does not appear to be a valid SQLite database file!")
    
    try:
        # Try to connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get the list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("\nNo tables found in the database!")
        else:
            print("\nTables in the database:")
            for table in tables:
                print(f"- {table[0]}")
        
        # Try to get some schema information
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
        schemas = cursor.fetchall()
        
        if schemas:
            print("\nTable schemas:")
            for schema in schemas:
                print(f"\n{schema[0]}")
        
        conn.close()
        
    except sqlite3.DatabaseError as e:
        print(f"\nError accessing database: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    inspect_database_file()
