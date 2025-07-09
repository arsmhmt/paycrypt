import os
import sys
from app import create_app
from app.extensions import db, jwt
from app.models.admin import AdminUser

def test_jwt_setup():
    """Test JWT configuration and token generation"""
    app = create_app()
    
    with app.app_context():
        print("\n=== Testing JWT Configuration ===")
        
        # 1. Check if admin user exists
        admin = AdminUser.query.filter_by(username='testadmin').first()
        if not admin:
            print("❌ Test admin user not found. Creating one...")
            admin = AdminUser(
                username='testadmin',
                email='testadmin@example.com',
                password='testpass123',
                first_name='Test',
                last_name='Admin',
                is_active=True,
                is_superuser=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Created test admin user")
        else:
            print("✅ Found test admin user")
        
        # 2. Test JWT token creation
        from flask_jwt_extended import create_access_token, decode_token
        
        identity = {
            'id': admin.id,
            'type': 'admin',
            'is_admin': True
        }
        
        # Create token
        access_token = create_access_token(identity=identity)
        print(f"\n✅ Created JWT token:")
        print(f"Token: {access_token[:50]}...")
        
        # Decode token to verify
        try:
            decoded = decode_token(access_token)
            print("\n✅ Successfully decoded token:")
            print(f"Identity: {decoded['sub']}")
            print(f"Expires: {decoded['exp']}")
            print(f"Type: {decoded.get('type')}")
            print(f"Is Admin: {decoded.get('is_admin')}")
            return True
        except Exception as e:
            print(f"❌ Failed to decode token: {str(e)}")
            return False

if __name__ == "__main__":
    if test_jwt_setup():
        print("\n✅ JWT configuration test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ JWT configuration test failed!")
        sys.exit(1)
