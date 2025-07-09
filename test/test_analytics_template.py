#!/usr/bin/env python3
"""
Test script to verify the analytics template renders without errors
"""
from app import create_app
from datetime import datetime, timedelta
import traceback

def test_analytics_template():
    """Test rendering the analytics template with mock data"""
    app = create_app()
    
    with app.app_context():
        with app.test_request_context('/admin/analytics'):
            try:
                # Mock data matching what the analytics route actually provides
                mock_data = {
                    'total_transactions': 5,
                    'total_volume': 0.12345,
                    'chart_labels': ['Jan', 'Feb', 'Mar'],
                    'chart_data': {
                        'count': [1, 2, 2], 
                        'volume': [0.04, 0.05, 0.03]
                    },
                    'start_date': datetime.utcnow() - timedelta(days=30),
                    'end_date': datetime.utcnow(),
                    'time_period_days': 30
                }
                
                # Try to render the template
                from flask import render_template
                
                # Test template rendering
                rendered = render_template('admin/analytics.html', **mock_data)
                
                print("✅ Analytics template rendered successfully!")
                print(f"Template length: {len(rendered)} characters")
                
                # Check for common errors in the rendered HTML
                if 'UndefinedError' in rendered:
                    print("❌ Found UndefinedError in rendered template")
                    return False
                elif 'TemplateError' in rendered:
                    print("❌ Found TemplateError in rendered template")
                    return False
                elif 'jinja2.exceptions' in rendered:
                    print("❌ Found Jinja2 exception in rendered template")
                    return False
                else:
                    print("✅ No template errors found in rendered HTML")
                    return True
                    
            except Exception as e:
                print(f"❌ Error rendering analytics template: {e}")
                print("Full traceback:")
                traceback.print_exc()
                return False

if __name__ == "__main__":
    success = test_analytics_template()
    exit(0 if success else 1)
