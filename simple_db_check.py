import os
import sqlite3

def check_db():
    # Path to the database file
    db_path = os.path.join('instance', 'cpgateway.db')
    
    print(f"Checking database at: {os.path.abspath(db_path)}")
    
    if not os.path.exists(db_path):
        print("Database file does not exist!")
        return
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get the list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database!")
            return
        
        print("\nTables in the database:")
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            
            # Get the table info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("Columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # Get the row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"  Rows: {count}")
            
            # Print first few rows if the table has data
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                rows = cursor.fetchall()
                print("  Sample data:")
                for row in rows:
                    print(f"    {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error accessing database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_db()
