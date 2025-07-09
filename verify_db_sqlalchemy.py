import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

def verify_database():
    # Set the database URI directly
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(basedir, 'instance', 'app.db')
    db_uri = f'sqlite:///{db_path}'
    
    print(f"Connecting to database: {db_uri}")
    
    try:
        # Create engine and connect
        engine = create_engine(db_uri)
        connection = engine.connect()
        print("Successfully connected to the database!")
        
        # Get table information
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print("\nNo tables found in the database!")
            return
        
        print("\nTables in the database:")
        for table_name in tables:
            print(f"\nTable: {table_name}")
            
            # Get column information
            columns = inspector.get_columns(table_name)
            print("  Columns:")
            for column in columns:
                print(f"    {column['name']} ({column['type']})")
            
            # Get row count
            result = connection.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = result.scalar()
            print(f"  Rows: {row_count}")
            
            # Get sample data
            if row_count > 0:
                result = connection.execute(f"SELECT * FROM {table_name} LIMIT 3")
                print("  Sample data:")
                for row in result:
                    print(f"    {row}")
        
        connection.close()
        
    except Exception as e:
        print(f"\nError accessing database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_database()
