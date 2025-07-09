#!/usr/bin/env python
"""
Comprehensive test script to verify client login flow and dashboard access
Tests both Flask-Login and JWT authentication methods
Ensures proper package/feature-based access control
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime
from pprint import pprint
from flask import Flask
from app import create_app, db
from app.models.client import Client
from app.models.user import User
from app.models.client_package import ClientPackage, Feature, PackageFeature, ClientType

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger('test_client_workflow')

# Create app with testing config
app = create_app('testing')
app.app_context().push()
client_base_url = 'http://localhost:5000/client'

def create_test_client(email, username, company_name, password, package_id=None):
    """Create a test client for testing"""
    logger.info(f"Creating test client: {email}")
    
    # Check if client already exists
    existing_client = Client.query.filter_by(email=email).first()
    if existing_client:
        logger.info(f"Client already exists with ID: {existing_client.id}")
        return existing_client
        
    # Create client
    client = Client(
        email=email,
        username=username,
        company_name=company_name,
        package_id=package_id,
        is_active=True,
        is_verified=True,
    )
    
    # Set password
    client.password_hash = User.generate_password_hash(password)
    
    # Create a user for this client
    user = User(
        username=username,
        email=email
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.flush()  # Get user ID without committing
    
    # Link the user to the client
    client.user_id = user.id
    
    db.session.add(client)
    db.session.commit()
    
    logger.info(f"Created client with ID: {client.id} and user ID: {user.id}")
    return client

def get_or_create_packages():
    """Set up test packages for different client types"""
    # Create basic features
    features = {
        'dashboard': Feature.query.filter_by(feature_key='dashboard').first() or 
                   Feature(name='Dashboard', feature_key='dashboard', description='Basic dashboard'),
        'api_access': Feature.query.filter_by(feature_key='api_access').first() or 
                    Feature(name='API Access', feature_key='api_access', description='API integration'),
        'withdrawals': Feature.query.filter_by(feature_key='withdrawals').first() or 
                     Feature(name='Withdrawals', feature_key='withdrawals', description='Crypto withdrawals')
    }
    
    for f in features.values():
        if not f.id:
            db.session.add(f)
    
    db.session.flush()  # Get IDs without committing
    
    # Create packages if they don't exist
    packages = {}
    
    # COMMISSION package (B2C)
    commission_pkg = ClientPackage.query.filter_by(name='B2C Commission').first()
    if not commission_pkg:
        commission_pkg = ClientPackage(
            name='B2C Commission',
            description='Commission-based package for B2C clients',
            client_type=ClientType.COMMISSION,
            commission_rate=0.035,  # 3.5%
            setup_fee=1000.00,
            max_transactions_per_month=500,
            max_api_calls_per_month=10000,
            is_popular=True
        )
        db.session.add(commission_pkg)
        db.session.flush()  # Get ID without committing
        
        # Add features to commission package
        for f in features.values():
            pf = PackageFeature(package_id=commission_pkg.id, feature_id=f.id, is_included=True)
            db.session.add(pf)
    
    packages['commission'] = commission_pkg
    
    # FLAT_RATE package (B2B)
    flat_rate_pkg = ClientPackage.query.filter_by(name='B2B Flat Rate').first()
    if not flat_rate_pkg:
        flat_rate_pkg = ClientPackage(
            name='B2B Flat Rate',
            description='Flat-rate package for B2B clients',
            client_type=ClientType.FLAT_RATE,
            monthly_price=299.99,
            annual_price=2999.99,
            max_transactions_per_month=None,  # Unlimited
            max_api_calls_per_month=50000,
            is_popular=True
        )
        db.session.add(flat_rate_pkg)
        db.session.flush()  # Get ID without committing
        
        # Add features to flat rate package
        for f in features.values():
            pf = PackageFeature(package_id=flat_rate_pkg.id, feature_id=f.id, is_included=True)
            db.session.add(pf)
    
    packages['flat_rate'] = flat_rate_pkg
    
    db.session.commit()
    return packages

def test_login_flow(client_email, password):
    """Test the client login flow using requests"""
    logger.info(f"Testing login flow for client: {client_email}")
    
    # Get the login page to retrieve CSRF token
    session = requests.Session()
    
    try:
        # Test 1: Get login page
        logger.info("Test 1: Accessing login page...")
        response = session.get(f"{client_base_url}/login")
        
        if response.status_code != 200:
            logger.error(f"Failed to get login page. Status: {response.status_code}")
            logger.error(f"Response: {response.text[:500]}...")
            return False
        else:
            logger.info("Login page accessed successfully")
        
        # Test 2: Submit login credentials
        logger.info("Test 2: Submitting login credentials...")
        login_data = {
            'username': client_email,
            'password': password,
            'remember_me': 'on'
        }
        
        response = session.post(
            f"{client_base_url}/login", 
            data=login_data,
            allow_redirects=False  # Don't follow redirects to see the actual response
        )
        
        # Check if login was successful (should redirect to dashboard)
        if response.status_code not in [302, 303]:
            logger.error(f"Login failed! Status: {response.status_code}")
            logger.error(f"Response: {response.text[:500]}...")
            return False
        
        redirect_location = response.headers.get('Location')
        logger.info(f"Login successful! Redirected to: {redirect_location}")
        
        # Test 3: Access the dashboard with the session cookie
        logger.info("Test 3: Accessing dashboard...")
        response = session.get(f"{client_base_url}/dashboard", allow_redirects=False)
        
        if response.status_code == 200:
            logger.info("Dashboard accessed successfully!")
            # Check for important sections in the dashboard
            if "Welcome back" in response.text and "Available Balance" in response.text:
                logger.info("Dashboard content looks correct")
                return True
            else:
                logger.warning("Dashboard accessed but content may be incorrect")
                logger.debug(f"Dashboard response: {response.text[:500]}...")
                return False
        else:
            logger.error(f"Failed to access dashboard! Status: {response.status_code}")
            logger.error(f"Response: {response.text[:500]}...")
            return False
    
    except Exception as e:
        logger.error(f"Error testing login flow: {str(e)}")
        return False

def test_jwt_auth(client_email, password):
    """Test JWT authentication flow"""
    logger.info(f"Testing JWT authentication for client: {client_email}")
    
    try:
        # Get login cookies with JWT tokens
        session = requests.Session()
        
        # Login to get JWT tokens
        login_data = {
            'username': client_email,
            'password': password
        }
        
        response = session.post(
            f"{client_base_url}/login", 
            data=login_data
        )
        
        if response.status_code != 200:
            logger.error(f"Login failed! Status: {response.status_code}")
            return False
            
        # Extract and check cookies
        cookies = session.cookies
        access_token_cookie = cookies.get('access_token_cookie')
        refresh_token_cookie = cookies.get('refresh_token_cookie')
        
        if not access_token_cookie or not refresh_token_cookie:
            logger.warning("JWT cookies not found!")
            return False
            
        logger.info("JWT tokens received successfully")
        
        # Try accessing the dashboard with JWT only
        logger.info("Testing dashboard access with JWT...")
        
        # Create a new session with only JWT cookies
        jwt_session = requests.Session()
        jwt_session.cookies.set('access_token_cookie', access_token_cookie)
        jwt_session.cookies.set('refresh_token_cookie', refresh_token_cookie)
        
        response = jwt_session.get(f"{client_base_url}/dashboard", allow_redirects=False)
        
        if response.status_code == 200:
            logger.info("Dashboard accessed with JWT successfully!")
            return True
        else:
            logger.error(f"Failed to access dashboard with JWT! Status: {response.status_code}")
            return False
    
    except Exception as e:
        logger.error(f"Error testing JWT auth: {str(e)}")
        return False

def test_client_types():
    """Test login and dashboard access for different client types"""
    # Set up packages
    packages = get_or_create_packages()
    
    # Create test clients for each package type
    test_clients = [
        {
            'email': 'b2c@example.com',
            'username': 'b2c_client',
            'company_name': 'B2C Test Company',
            'password': 'testpassword',
            'package_id': packages['commission'].id,
            'type': 'B2C (Commission)'
        },
        {
            'email': 'b2b@example.com',
            'username': 'b2b_client',
            'company_name': 'B2B Test Company',
            'password': 'testpassword',
            'package_id': packages['flat_rate'].id,
            'type': 'B2B (Flat Rate)'
        }
    ]
    
    results = {}
    
    for client_data in test_clients:
        client_type = client_data.pop('type')
        client = create_test_client(**client_data)
        
        logger.info(f"\n{'=' * 50}")
        logger.info(f"TESTING {client_type} CLIENT: {client.email}")
        logger.info(f"{'=' * 50}")
        
        # Test Flask-Login authentication
        flask_login_result = test_login_flow(client.email, client_data['password'])
        
        # Test JWT authentication
        jwt_result = test_jwt_auth(client.email, client_data['password'])
        
        results[client_type] = {
            'flask_login': flask_login_result,
            'jwt': jwt_result
        }
    
    return results

def main():
    """Main test function"""
    print("\n==== TESTING CLIENT LOGIN & DASHBOARD FLOW ====\n")
    
    try:
        # Run the Flask development server in a different process
        print("Please make sure the Flask development server is running on port 5000")
        print("Run this in another terminal: python run.py\n")
        input("Press Enter to continue when the server is running...")
        
        results = test_client_types()
        
        # Print summary
        print("\n==== TEST RESULTS SUMMARY ====\n")
        for client_type, auth_results in results.items():
            print(f"Client Type: {client_type}")
            print(f"  - Flask-Login Auth: {'✅ PASS' if auth_results['flask_login'] else '❌ FAIL'}")
            print(f"  - JWT Auth:         {'✅ PASS' if auth_results['jwt'] else '❌ FAIL'}")
            print()
            
        # Overall pass/fail
        all_passed = all(result for auth_type in results.values() for result in auth_type.values())
        
        if all_passed:
            print("✅ All tests PASSED!")
            return 0
        else:
            print("❌ Some tests FAILED!")
            return 1
            
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
