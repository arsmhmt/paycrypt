import sys
import requests
from app import create_app
from app.extensions import db
from app.models.admin import AdminUser

def test_admin_login():
    print("\n=== Testing Admin Authentication Flow ===")
    
    # Create test app
    app = create_app()
    
    with app.app_context():
        # Ensure test admin exists
        admin = AdminUser.query.filter_by(username='testadmin').first()
        if not admin:
            print("Creating test admin user...")
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
        
        # Test login endpoint
        test_client = app.test_client()
        
        # 1. Test GET login page
        print("\n1. Testing GET /auth/login")
        response = test_client.get('/auth/login')
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.content_type}")
        print(f"Has Form: {'form' in response.get_data(as_text=True).lower()}")
        
        # 2. Test POST login with correct credentials
        print("\n2. Testing POST /auth/login with correct credentials")
        response = test_client.post('/auth/login', data={
            'username': 'testadmin',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        print(f"Status Code: {response.status_code}")
        print(f"Redirected to: {response.request.path}")
        print(f"Cookies: {response.headers.getlist('Set-Cookie')}")
        
        # Check for JWT cookies
        cookies = response.headers.getlist('Set-Cookie')
        access_token = next((c for c in cookies if 'access_token_cookie' in c), None)
        refresh_token = next((c for c in cookies if 'refresh_token_cookie' in c), None)
        
        print(f"Access Token Cookie: {'✅ Found' if access_token else '❌ Missing'}")
        print(f"Refresh Token Cookie: {'✅ Found' if refresh_token else '❌ Missing'}")
        
        if not access_token or not refresh_token:
            print("\n❌ JWT cookies not set correctly")
            return False
            
        # 3. Test accessing protected route
        print("\n3. Testing access to protected route /admin/dashboard")
        response = test_client.get('/admin/dashboard', follow_redirects=True)
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.content_type}")
        
        if 'Admin Dashboard' in response.get_data(as_text=True):
            print("✅ Successfully accessed protected route")
        else:
            print("❌ Failed to access protected route")
            return False
            
        # 4. Test logout
        print("\n4. Testing logout")
        response = test_client.get('/auth/logout', follow_redirects=True)
        print(f"Status Code: {response.status_code}")
        print(f"Redirected to: {response.request.path}")
        
        # Check if cookies are cleared
        cookies = response.headers.getlist('Set-Cookie')
        access_token_cleared = any('access_token_cookie=;' in c for c in cookies)
        refresh_token_cleared = any('refresh_token_cookie=;' in c for c in cookies)
        
        print(f"Access Token Cleared: {'✅ Yes' if access_token_cleared else '❌ No'}")
        print(f"Refresh Token Cleared: {'✅ Yes' if refresh_token_cleared else '❌ No'}")
        
        return True

if __name__ == "__main__":
    print("Starting authentication flow test...")
    try:
        if test_admin_login():
            print("\n✅ Authentication flow test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Authentication flow test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
