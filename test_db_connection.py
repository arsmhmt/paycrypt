import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

# Create a minimal Flask app
app = Flask(__name__)

# Set the database URI to use cpgateway.db
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
db_path = os.path.join(basedir, 'instance', 'cpgateway.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

def test_db_connection():
    with app.app_context():
        # Check if the database file exists
        print(f"Database path: {db_path}")
        print(f"Database file exists: {os.path.exists(db_path)}")
        
        # Try to connect to the database
        try:
            conn = db.engine.connect()
            print("Successfully connected to the database!")
            
            # List all tables
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print("\nTables in the database:")
            for table in tables:
                print(f"- {table}")
                
                # Get columns for each table
                columns = inspector.get_columns(table)
                print(f"  Columns: {', '.join(col['name'] for col in columns)}")
            
            conn.close()
        except Exception as e:
            print(f"Error connecting to the database: {e}")

if __name__ == '__main__':
    test_db_connection()
