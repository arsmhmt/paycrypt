from app import create_app
from app.extensions.extensions import db
from app.models.user import User
from app.models.client import Client

def check_database():
    # Create the Flask app
    app = create_app()
    
    with app.app_context():
        try:
            # Print database URI
            print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Check if tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print("\nTables in the database:")
            for table in tables:
                print(f"- {table}")
            
            # Check if we can query the User table
            if 'user' in tables:
                print("\nUsers in the database:")
                users = User.query.all()
                for user in users:
                    print(f"- {user.username} ({user.email})")
            
            # Check if we can query the Client table
            if 'client' in tables:
                print("\nClients in the database:")
                clients = Client.query.all()
                for client in clients:
                    print(f"- {client.company_name} (Contact: {client.contact_person})")
            
        except Exception as e:
            print(f"\nError checking database: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_database()
