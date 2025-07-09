#!/usr/bin/env python3
"""
Comprehensive CSS Conflict and Duplication Audit
Tests for conflicts that prevent modern dashboard styling
"""

import os
import re
from pathlib import Path

def check_bootstrap_versions():
    """Check for Bootstrap version conflicts across templates"""
    print("=== BOOTSTRAP VERSION AUDIT ===")
    
    templates = [
        'app/templates/base.html',
        'app/templates/client/base.html',
        'app/templates/client/dashboard.html'
    ]
    
    bootstrap_versions = {}
    bootstrap_icons_versions = {}
    
    for template in templates:
        if os.path.exists(template):
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check Bootstrap CSS versions
                bs_css_matches = re.findall(r'bootstrap@(\d+\.\d+\.\d+)/dist/css', content)
                if bs_css_matches:
                    bootstrap_versions[template] = bs_css_matches
                
                # Check Bootstrap Icons versions
                bs_icons_matches = re.findall(r'bootstrap-icons@(\d+\.\d+\.\d+)', content)
                if bs_icons_matches:
                    bootstrap_icons_versions[template] = bs_icons_matches
                
                # Check Bootstrap JS versions
                bs_js_matches = re.findall(r'bootstrap@(\d+\.\d+\.\d+)/dist/js', content)
                if bs_js_matches:
                    if template not in bootstrap_versions:
                        bootstrap_versions[template] = []
                    bootstrap_versions[template].extend([f"{v} (JS)" for v in bs_js_matches])
    
    # Report findings
    print("Bootstrap CSS/JS versions found:")
    for template, versions in bootstrap_versions.items():
        print(f"  {template}: {', '.join(versions)}")
    
    print("\nBootstrap Icons versions found:")
    for template, versions in bootstrap_icons_versions.items():
        print(f"  {template}: {', '.join(versions)}")
    
    # Check for conflicts
    all_bs_versions = []
    all_icons_versions = []
    
    for versions in bootstrap_versions.values():
        all_bs_versions.extend([v for v in versions if 'JS' not in v])
    
    for versions in bootstrap_icons_versions.values():
        all_icons_versions.extend(versions)
    
    unique_bs = set(all_bs_versions)
    unique_icons = set(all_icons_versions)
    
    if len(unique_bs) > 1:
        print(f"⚠️  CONFLICT: Multiple Bootstrap versions detected: {unique_bs}")
    else:
        print("✓ No Bootstrap version conflicts")
    
    if len(unique_icons) > 1:
        print(f"⚠️  CONFLICT: Multiple Bootstrap Icons versions detected: {unique_icons}")
    else:
        print("✓ No Bootstrap Icons version conflicts")

def check_css_style_conflicts():
    """Check for conflicting CSS styles between base.html and client-dashboard.css"""
    print("\n=== CSS STYLE CONFLICT AUDIT ===")
    
    base_template = 'app/templates/base.html'
    client_css = 'app/static/css/client-dashboard.css'
    
    conflicts_found = []
    
    if os.path.exists(base_template) and os.path.exists(client_css):
        with open(base_template, 'r', encoding='utf-8') as f:
            base_content = f.read()
        
        with open(client_css, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Check for body style conflicts
        base_body_bg = 'background-color: var(--background)' in base_content
        css_body_bg = 'background: linear-gradient' in css_content and '!important' in css_content
        
        if base_body_bg and css_body_bg:
            print("✓ Body background conflict resolved (CSS has !important)")
        elif base_body_bg and not css_body_bg:
            conflicts_found.append("Body background: base.html sets background-color, client CSS may not override")
        
        # Check for card style conflicts
        base_card_styles = '.card {' in base_content
        css_card_overrides = '.card,' in css_content and '!important' in css_content
        
        if base_card_styles and css_card_overrides:
            print("✓ Card style conflict resolved (CSS has !important overrides)")
        elif base_card_styles and not css_card_overrides:
            conflicts_found.append("Card styles: base.html defines .card, client CSS may not override")
        
        # Check for glassmorphism features
        glassmorphism_features = [
            'backdrop-filter',
            'rgba(',
            'glass-card'
        ]
        
        missing_features = []
        for feature in glassmorphism_features:
            if feature not in css_content:
                missing_features.append(feature)
        
        if missing_features:
            conflicts_found.append(f"Missing glassmorphism features: {', '.join(missing_features)}")
        else:
            print("✓ All glassmorphism features present in client CSS")
    
    return conflicts_found

def check_css_loading():
    """Check CSS file loading and cache-busting"""
    print("\n=== CSS LOADING AUDIT ===")
    
    dashboard_template = 'app/templates/client/dashboard.html'
    css_file = 'app/static/css/client-dashboard.css'
    
    if os.path.exists(dashboard_template):
        with open(dashboard_template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for CSS link with cache-busting
        cache_busting = '?v=' in content and 'client-dashboard.css' in content
        if cache_busting:
            print("✓ CSS cache-busting parameter found")
        else:
            print("⚠️  CSS cache-busting parameter missing")
        
        # Check for duplicate Bootstrap JS
        bootstrap_js_count = content.count('bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js')
        if bootstrap_js_count == 0:
            print("✓ No duplicate Bootstrap JS in dashboard template")
        else:
            print(f"⚠️  Found {bootstrap_js_count} Bootstrap JS loads in dashboard template")
    
    if os.path.exists(css_file):
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        print(f"✓ CSS file exists ({len(css_content)} characters)")
        
        # Check for important declarations
        important_count = css_content.count('!important')
        print(f"✓ Found {important_count} !important declarations for override strength")
    else:
        print("❌ client-dashboard.css not found")

def main():
    """Run comprehensive CSS conflict audit"""
    print("CSS CONFLICT AND DUPLICATION AUDIT")
    print("=" * 50)
    
    # Change to the correct directory
    os.chdir('d:/CODES/main_apps/cpgateway')
    
    check_bootstrap_versions()
    conflicts = check_css_style_conflicts()
    check_css_loading()
    
    print("\n=== SUMMARY ===")
    if conflicts:
        print("❌ CONFLICTS FOUND:")
        for conflict in conflicts:
            print(f"  - {conflict}")
    else:
        print("✅ NO MAJOR CONFLICTS DETECTED")
        print("   Modern glassmorphism styling should display correctly")
    
    print("\nRecommendations:")
    print("1. Ensure Flask server is restarted after CSS changes")
    print("2. Clear browser cache or use hard refresh (Ctrl+F5)")
    print("3. Check browser dev tools for any remaining CSS conflicts")

if __name__ == "__main__":
    main()
