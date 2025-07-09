#!/usr/bin/env python3
"""
Simple test to check if CSS is loading with cache-busting
"""
import requests
import re

def test_css_direct():
    try:
        # Try to access CSS file directly
        css_response = requests.get('http://localhost:8080/static/css/client-dashboard.css')
        print(f"Direct CSS access status: {css_response.status_code}")
        print(f"CSS file size: {len(css_response.content)} bytes")
        
        if css_response.status_code == 200:
            css_content = css_response.text
            
            # Check for modern CSS features
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
                
            # Check specific glassmorphism CSS
            if 'backdrop-filter: blur(' in css_content:
                print("✓ Glassmorphism effects confirmed")
            
            # Check dark mode
            if 'prefers-color-scheme: dark' in css_content:
                print("✓ Dark mode styles confirmed")
                
            # Check first few lines to see CSS structure
            lines = css_content.split('\n')[:10]
            print("First 10 lines of CSS:")
            for i, line in enumerate(lines, 1):
                if line.strip():
                    print(f"  {i}: {line.strip()}")
                    
        else:
            print(f"Failed to access CSS file: {css_response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_css_direct()
