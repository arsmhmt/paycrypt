#!/usr/bin/env python3

"""
Test Script: Verify Client Navbar Steel Black Background
Confirms that the client dashboard top navbar background has been changed to steel black (#212529)
to match the admin dashboard.
"""

import sys
import os
import re

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_navbar_steel_black():
    """Test that client navbar has steel black background like admin"""
    
    print("🔍 Testing Client Navbar Steel Black Background...")
    print("=" * 60)
    
    # Test 1: Check client base template navbar HTML
    client_base_path = 'app/templates/client/base.html'
    
    if not os.path.exists(client_base_path):
        print(f"❌ Client base template not found: {client_base_path}")
        return False
    
    with open(client_base_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("1. Checking navbar HTML element...")
    
    # Check for steel black inline style
    navbar_inline_match = re.search(r'<nav[^>]*style="[^"]*background-color:\s*#212529[^"]*"[^>]*>', content)
    if navbar_inline_match:
        print(f"   ✅ Found steel black inline style: {navbar_inline_match.group()[:100]}...")
    else:
        print("   ❌ Steel black inline style not found in navbar element")
        return False
    
    print("2. Checking CSS .sb-topnav override...")
    
    # Check for CSS override with steel black
    css_override_match = re.search(r'\.sb-topnav\s*\{[^}]*background:\s*#212529[^}]*\}', content, re.DOTALL)
    if css_override_match:
        print(f"   ✅ Found CSS override: {css_override_match.group()[:80]}...")
    else:
        print("   ❌ CSS override for .sb-topnav with #212529 not found")
        return False
    
    print("3. Checking dark theme CSS override...")
    
    # Check for dark theme CSS override
    dark_theme_match = re.search(r'\.dark-theme\s+\.sb-topnav\s*\{[^}]*background:\s*#212529[^}]*\}', content, re.DOTALL)
    if dark_theme_match:
        print(f"   ✅ Found dark theme override: {dark_theme_match.group()[:80]}...")
    else:
        print("   ❌ Dark theme CSS override not found")
        return False
    
    print("4. Checking removal of brand gradient...")
    
    # Ensure no brand gradient remains in topnav
    brand_gradient_match = re.search(r'\.sb-topnav[^}]*var\(--brand-gradient\)', content)
    if brand_gradient_match:
        print("   ❌ Brand gradient still found in .sb-topnav")
        return False
    else:
        print("   ✅ Brand gradient removed from .sb-topnav")
    
    print("5. Comparing with admin navbar...")
    
    # Check admin CSS for comparison
    admin_css_path = 'app/static/css/admin.css'
    if os.path.exists(admin_css_path):
        with open(admin_css_path, 'r', encoding='utf-8') as f:
            admin_content = f.read()
        
        # Look for topbar-bg variable
        topbar_bg_match = re.search(r'--topbar-bg:\s*#212529', admin_content)
        if topbar_bg_match:
            print("   ✅ Admin uses same steel black color (#212529)")
        else:
            print("   ⚠️  Admin topbar-bg variable not found")
    
    print("\n" + "=" * 60)
    print("✅ CLIENT NAVBAR STEEL BLACK TEST PASSED!")
    print("🎯 Client dashboard navbar now matches admin with steel black background")
    print("🔧 Changes applied:")
    print("   • Navbar HTML: style='background-color: #212529 !important;'")
    print("   • CSS Override: .sb-topnav { background: #212529 !important; }")
    print("   • Dark Theme: .dark-theme .sb-topnav { background: #212529 !important; }")
    print("   • Removed: var(--brand-gradient) from topnav")
    
    return True

if __name__ == "__main__":
    success = test_navbar_steel_black()
    if success:
        print("\n🎉 Test completed successfully!")
        print("💡 Next: Open client dashboard in browser and refresh to see steel black navbar")
    else:
        print("\n❌ Test failed - navbar changes may need review")
    
    sys.exit(0 if success else 1)
