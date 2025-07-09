#!/usr/bin/env python3
"""
Test CSS refresh with new cache-busting parameter
"""
import requests
import re
from urllib.parse import urlparse, parse_qs

# Test the dashboard page to see the new CSS URL
def test_css_refresh():
    session = requests.Session()
    
    # Login first
    login_data = {
        'username': 'smartbetslip',
        'password': 'Mahmut*1905'
    }
    
    try:
        # Get login page for CSRF token
        login_page = session.get('http://localhost:8080/client/login')
        print(f"Login page status: {login_page.status_code}")
        
        # Extract CSRF token
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_page.text)
        if csrf_match:
            login_data['csrf_token'] = csrf_match.group(1)
            print(f"CSRF token found: {login_data['csrf_token'][:20]}...")
        
        # Perform login
        login_response = session.post('http://localhost:8080/client/login', data=login_data)
        print(f"Login response status: {login_response.status_code}")
        
        if login_response.status_code == 302:
            print("Login successful - redirected")
        else:
            print(f"Login failed with status {login_response.status_code}")
            return
        
        # Get dashboard page
        dashboard_response = session.get('http://localhost:8080/client/dashboard')
        print(f"Dashboard status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            # Find the CSS link in the HTML
            css_pattern = r'<link href="([^"]*client-dashboard\.css[^"]*)"'
            css_match = re.search(css_pattern, dashboard_response.text)
            
            if css_match:
                css_url = css_match.group(1)
                print(f"CSS URL found: {css_url}")
                
                # Parse the version parameter
                if '?v=' in css_url:
                    version_param = css_url.split('?v=')[1]
                    print(f"Cache-busting parameter: {version_param}")
                    
                    # Try to access the CSS file directly
                    if css_url.startswith('/'):
                        full_css_url = f"http://localhost:8080{css_url}"
                    else:
                        full_css_url = css_url
                    
                    css_response = session.get(full_css_url)
                    print(f"CSS file status: {css_response.status_code}")
                    print(f"CSS file size: {len(css_response.content)} bytes")
                    
                    # Check for modern CSS features
                    css_content = css_response.text
                    modern_features = [
                        'backdrop-filter',
                        'glassmorphism',
                        'dark-mode',
                        '@media (prefers-color-scheme: dark)',
                        'gradient'
                    ]
                    
                    found_features = []
                    for feature in modern_features:
                        if feature in css_content:
                            found_features.append(feature)
                    
                    print(f"Modern CSS features found: {found_features}")
                    
                    if len(css_content) > 5000:
                        print("✓ CSS file appears to be the enhanced version (>5KB)")
                    else:
                        print("⚠ CSS file appears to be basic version (<5KB)")
                        
                else:
                    print("No cache-busting parameter found")
            else:
                print("CSS link not found in dashboard HTML")
        else:
            print(f"Failed to access dashboard: {dashboard_response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_css_refresh()
