from app import create_app
from app.extensions.extensions import db
from sqlalchemy import inspect

def test_db():
    app = create_app()
    with app.app_context():
        # Get the database engine
        engine = db.engine
        print(f"Database URL: {engine.url}")
        
        # Check if the database exists
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print("\nTables in the database:")
        for table in tables:
            print(f"- {table}")
            
            # Get columns for each table
            columns = inspector.get_columns(table)
            print(f"  Columns: {', '.join(col['name'] for col in columns)}")

if __name__ == '__main__':
    test_db()
