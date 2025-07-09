from app import create_app
from app.extensions.extensions import db
from app.models.user import User
from app.models.client import Client

def list_all_users():
    # Create the Flask app
    app = create_app()
    
    with app.app_context():
        try:
            # Get all users
            users = User.query.all()
            
            if not users:
                print("No users found in the database.")
                return
            
            print(f"\nFound {len(users)} user(s) in the database:")
            print("-" * 80)
            
            for user in users:
                print(f"User ID: {user.id}")
                print(f"Username: {user.username}")
                print(f"Email: {user.email}")
                print(f"Active: {user.is_active}")
                print(f"Verified: {user.is_verified}")
                print(f"Created at: {user.created_at}")
                
                # Get associated client if exists
                client = Client.query.filter_by(user_id=user.id).first()
                if client:
                    print(f"\n  Client Info:")
                    print(f"  - Company: {client.company_name}")
                    print(f"  - Contact: {client.contact_person}")
                    print(f"  - Email: {client.contact_email}")
                    print(f"  - Active: {client.is_active}")
                else:
                    print("  No associated client record found.")
                
                print("-" * 80)
            
        except Exception as e:
            print(f"Error listing users: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    list_all_users()
