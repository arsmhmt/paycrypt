#!/usr/bin/env python
"""
Debug script to test the context processor issue.
"""
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.extensions import db
from flask import url_for

def test_context_processor():
    """Test if context processor is working"""
    app = create_app()
    
    with app.app_context():
        print("=== Testing Context Processor ===")
        
        # Test if we can access the admin routes
        try:
            from app.admin_routes import get_sidebar_stats
            print("✓ get_sidebar_stats function imported successfully")
            
            # Test the function
            stats = get_sidebar_stats()
            print(f"✓ get_sidebar_stats returned: {stats}")
            
        except Exception as e:
            print(f"✗ Error calling get_sidebar_stats: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Test if we can access the context processor
        try:
            from app.admin_routes import inject_sidebar_stats
            print("✓ inject_sidebar_stats function imported successfully")
            
            # Test the context processor
            context = inject_sidebar_stats()
            print(f"✓ inject_sidebar_stats returned: {context}")
            
        except Exception as e:
            print(f"✗ Error calling inject_sidebar_stats: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Test if we can render a template with context
        try:
            with app.test_request_context('/admin/dashboard'):
                from flask import render_template_string
                test_template = """
                {% if sidebar_stats is defined %}
                sidebar_stats is defined: {{ sidebar_stats }}
                {% else %}
                sidebar_stats is NOT defined
                {% endif %}
                """
                result = render_template_string(test_template)
                print(f"✓ Template render test: {result.strip()}")
                
        except Exception as e:
            print(f"✗ Error rendering test template: {str(e)}")
            import traceback
            traceback.print_exc()

def test_dashboard_route():
    """Test the dashboard route specifically"""
    app = create_app()
    
    with app.test_client() as client:
        print("\n=== Testing Dashboard Route ===")
        
        # First we need to login
        try:
            # Check if we can access the login page
            response = client.get('/auth/login')
            print(f"✓ Login page status: {response.status_code}")
            
            # Try to access dashboard without login (should redirect)
            response = client.get('/admin/dashboard')
            print(f"✓ Dashboard access without login: {response.status_code}")
            
        except Exception as e:
            print(f"✗ Error testing dashboard route: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("Starting context processor debugging...")
    test_context_processor()
    test_dashboard_route()
    print("Context processor debugging complete.")
