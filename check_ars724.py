from app import create_app
from app.extensions.extensions import db
from app.models.client import Client

def check_ars724():
    # Create the Flask app
    app = create_app()
    
    with app.app_context():
        try:
            # Search for client with username or company name containing 'ars724'
            clients = Client.query.filter(
                (Client.company_name.ilike('%ars724%')) |
                (Client.contact_person.ilike('%ars724%')) |
                (Client.contact_email.ilike('%ars724%'))
            ).all()
            
            if not clients:
                print("No client found matching 'ars724'")
                
                # Let's also check the users table
                from app.models.user import User
                users = User.query.filter(
                    (User.username.ilike('%ars724%')) |
                    (User.email.ilike('%ars724%'))
                ).all()
                
                if not users:
                    print("No user found matching 'ars724'")
                else:
                    print("\nMatching users found:")
                    for user in users:
                        print(f"- {user.username} ({user.email})")
            else:
                print("\nMatching clients found:")
                for client in clients:
                    print(f"- {client.company_name} (Contact: {client.contact_person}, Email: {client.contact_email})")
                    
                    # Get the associated user
                    user = client.user
                    if user:
                        print(f"  User: {user.username} (ID: {user.id}, Email: {user.email})")
            
        except Exception as e:
            print(f"Error searching for client: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_ars724()
