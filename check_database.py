import os
from app import create_app
from app.extensions.extensions import db

def check_database():
    app = create_app()
    
    with app.app_context():
        print("=== Database Information ===")
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"Instance path: {app.instance_path}")
        
        # Check if the database file exists
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        print(f"\nDatabase file path: {db_path}")
        print(f"Database file exists: {os.path.exists(db_path)}")
        
        # Try to connect to the database
        try:
            # Get database metadata
            meta = db.metadata
            print("\n=== Database Metadata ===")
            for table in meta.tables.values():
                print(f"\nTable: {table.name}")
                print("Columns:")
                for column in table.columns:
                    print(f"  {column.name} ({column.type})")
            
            # Try to query the database
            print("\n=== Database Content ===")
            
            # Check if users table exists and has data
            if 'users' in [t.name for t in meta.tables.values()]:
                print("\nUsers:")
                users = db.session.execute(db.select(User)).scalars().all()
                for user in users:
                    print(f"- {user.username} ({user.email})")
            else:
                print("\nNo users table found.")
            
            # Check if clients table exists and has data
            if 'clients' in [t.name for t in meta.tables.values()]:
                print("\nClients:")
                clients = db.session.execute(db.select(Client)).scalars().all()
                for client in clients:
                    print(f"- {client.company_name} (User ID: {client.user_id})")
            else:
                print("\nNo clients table found.")
                
        except Exception as e:
            print(f"\nError accessing database: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    # Import models here to avoid circular imports
    from app.models.user import User
    from app.models.client import Client
    check_database()
