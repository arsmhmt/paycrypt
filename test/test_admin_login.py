from app import create_app
from app.models.admin import AdminUser
from werkzeug.security import check_password_hash

app = create_app()

def test_login(username, password):
    with app.app_context():
        print(f"\n=== Testing login for: {username} ===")
        
        # Try to find user by username
        admin = AdminUser.query.filter_by(username=username).first()
        if not admin:
            # Try by email
            admin = AdminUser.query.filter_by(email=username).first()
        
        if not admin:
            print(f"❌ Error: User '{username}' not found in database")
            return False
        
        print(f"✅ Found user: {admin.username} (ID: {admin.id}, Email: {admin.email})")
        print(f"   - Active: {admin.is_active}")
        print(f"   - Superuser: {admin.is_superuser}")
        
        # Check password
        is_correct = admin.check_password(password)
        print(f"🔑 Password check: {'✅ Correct' if is_correct else '❌ Incorrect'}")
        
        if is_correct:
            print("✅ Login successful!")
        else:
            print("❌ Login failed: Invalid password")
        
        return is_correct

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python test_admin_login.py <username/email> <password>")
        print("Example: python test_admin_login.py admin yourpassword")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    test_login(username, password)
