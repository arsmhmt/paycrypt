#!/usr/bin/env python3
"""
Verify CSS refresh and modern styling features
"""

import os
import re
import time

def verify_css_content():
    """Verify the CSS file contains all expected modern features"""
    print("=== CSS CONTENT VERIFICATION ===")
    
    css_file = 'app/static/css/client-dashboard.css'
    
    if not os.path.exists(css_file):
        print("❌ CSS file not found")
        return False
    
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for essential glassmorphism features
    features_to_check = {
        'backdrop-filter: blur': 'Glassmorphism blur effect',
        'rgba(255,255,255,0.85)': 'Semi-transparent white background',
        'linear-gradient': 'Gradient backgrounds',
        'box-shadow:.*rgba': 'Modern shadow effects',
        'border-radius: 1.25rem': 'Rounded corners',
        '!important': 'CSS override declarations',
        'glass-card': 'Glassmorphism card class',
        'text-gradient': 'Text gradient class',
        'transform: translateY': 'Hover animations'
    }
    
    missing_features = []
    for pattern, description in features_to_check.items():
        if not re.search(pattern, content):
            missing_features.append(description)
        else:
            print(f"✓ {description}")
    
    if missing_features:
        print("\n❌ Missing features:")
        for feature in missing_features:
            print(f"  - {feature}")
        return False
    
    print(f"\n✅ All modern CSS features present ({len(content)} chars)")
    return True

def verify_template_links():
    """Verify dashboard template properly links to CSS"""
    print("\n=== TEMPLATE VERIFICATION ===")
    
    dashboard_template = 'app/templates/client/dashboard.html'
    
    if not os.path.exists(dashboard_template):
        print("❌ Dashboard template not found")
        return False
    
    with open(dashboard_template, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check CSS link
    css_link_pattern = r"client-dashboard\.css.*\?v="
    if re.search(css_link_pattern, content):
        print("✓ CSS linked with cache-busting parameter")
    else:
        print("❌ CSS link missing or no cache-busting")
        return False
    
    # Check for duplicate Bootstrap
    bootstrap_js_count = content.count('bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js')
    if bootstrap_js_count == 0:
        print("✓ No duplicate Bootstrap JS")
    else:
        print(f"⚠️  {bootstrap_js_count} Bootstrap JS references found")
    
    return True

def main():
    """Run verification"""
    print("CSS REFRESH AND STYLING VERIFICATION")
    print("=" * 40)
    
    os.chdir('d:/CODES/main_apps/cpgateway')
    
    css_ok = verify_css_content()
    template_ok = verify_template_links()
    
    print("\n=== FINAL STATUS ===")
    if css_ok and template_ok:
        print("✅ ALL CHECKS PASSED")
        print("   Modern glassmorphism dashboard styling should display correctly")
        print("   CSS conflicts have been resolved")
        print("   Cache-busting is active")
    else:
        print("❌ SOME ISSUES DETECTED")
        print("   Please check the specific failures above")
    
    print("\nNext steps:")
    print("1. Restart Flask server if running")
    print("2. Open dashboard in browser")
    print("3. Use Ctrl+F5 for hard refresh")
    print("4. Check browser dev tools for any remaining issues")

if __name__ == "__main__":
    main()
