#!/usr/bin/env python
"""
Simple syntax check for Jinja2 template.
"""
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

def check_template_syntax():
    """Check template syntax"""
    print("=== Checking Template Syntax ===")
    
    try:
        from jinja2 import Environment, FileSystemLoader
        
        # Create Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), 'app', 'templates')
        env = Environment(loader=FileSystemLoader(template_dir))
        
        # Try to load the template
        template = env.get_template('admin/clients.html')
        print("✓ Template loaded successfully - no syntax errors")
        
        return True
        
    except Exception as e:
        print(f"✗ Template syntax error: {str(e)}")
        return False

if __name__ == '__main__':
    print("Checking template syntax...")
    success = check_template_syntax()
    if success:
        print("✓ All template syntax issues have been resolved!")
    else:
        print("✗ Template still has syntax issues")
    print("Check complete.")
