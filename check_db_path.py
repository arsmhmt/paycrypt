import os
from app import create_app

def check_db_path():
    app = create_app()
    
    print("=== Database Configuration ===")
    print(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Instance path: {app.instance_path}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check if the database file exists
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    print(f"\nDatabase file path: {db_path}")
    print(f"Database file exists: {os.path.exists(db_path)}")
    
    # Search for any .db files in the project directory
    print("\nSearching for .db files in the project directory...")
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.db'):
                file_path = os.path.join(root, file)
                print(f"Found: {file_path} (Size: {os.path.getsize(file_path) / 1024:.2f} KB)")

if __name__ == '__main__':
    check_db_path()
