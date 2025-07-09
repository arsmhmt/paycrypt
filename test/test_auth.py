import pytest
from app import create_app, db
from app.models.admin import AdminUser
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        # Create a test admin user
        if not AdminUser.query.filter_by(username='testadmin').first():
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
        
        yield app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_admin_login_success(client, app):
    """Test successful admin login"""
    with app.app_context():
        # Test login with correct credentials
        response = client.post('/auth/login', data={
            'username': 'testadmin',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        # Should redirect to admin dashboard on success
        assert response.status_code == 200
        assert b'Admin Dashboard' in response.data
        
        # Check if access token is set in cookies
        cookies = response.headers.getlist('Set-Cookie')
        access_token_cookie = any('access_token_cookie' in cookie for cookie in cookies)
        assert access_token_cookie, "Access token cookie not set"

def test_admin_dashboard_access(client, app):
    """Test accessing admin dashboard with valid JWT"""
    # First login to get the token
    login_response = client.post('/auth/login', data={
        'username': 'testadmin',
        'password': 'testpass123'
    })
    
    # Now access the dashboard
    dashboard_response = client.get('/admin/dashboard', follow_redirects=True)
    assert dashboard_response.status_code == 200
    assert b'Admin Dashboard' in dashboard_response.data

def test_protected_route_without_token(client):
    """Test accessing protected route without token"""
    response = client.get('/admin/dashboard', follow_redirects=False)
    # Should redirect to login page
    assert response.status_code == 302
    assert '/auth/login' in response.location
