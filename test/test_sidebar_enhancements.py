#!/usr/bin/env python3

"""
Test Script: Verify Sidebar Logo and Toggle Button
Confirms that the client sidebar has:
1. Logo max-height 80px (60px when collapsed)
2. Orange sidebar toggle button
3. Always visible logo
"""

import sys
import os
import re

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_sidebar_enhancements():
    """Test sidebar logo sizing and toggle button"""
    
    print("🔍 Testing Sidebar Logo & Toggle Button Enhancements...")
    print("=" * 60)
    
    # Test 1: Check client base template
    client_base_path = 'app/templates/client/base.html'
    
    if not os.path.exists(client_base_path):
        print(f"❌ Client base template not found: {client_base_path}")
        return False
    
    with open(client_base_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("1. Checking logo max-height (80px)...")
    
    # Check for 80px logo height
    logo_height_match = re.search(r'max-height:\s*80px', content)
    if logo_height_match:
        print("   ✅ Found 80px max-height for logo")
    else:
        print("   ❌ 80px max-height not found")
        return False
    
    print("2. Checking collapsed state CSS (60px)...")
    
    # Check for collapsed state CSS
    collapsed_css_match = re.search(r'body\.sb-sidenav-toggled\s+\.sidebar-logo[^}]*max-height:\s*60px', content, re.DOTALL)
    if collapsed_css_match:
        print("   ✅ Found collapsed state CSS with 60px")
    else:
        print("   ❌ Collapsed state CSS not found")
        return False
    
    print("3. Checking orange toggle button HTML...")
    
    # Check for orange toggle button
    orange_btn_match = re.search(r'btn-outline-warning[^>]*sidebar-toggle-btn[^>]*id="sidebarToggleInternal"', content)
    if orange_btn_match:
        print("   ✅ Found orange sidebar toggle button")
    else:
        print("   ❌ Orange sidebar toggle button not found")
        return False
    
    print("4. Checking orange toggle button CSS...")
    
    # Check for orange button CSS
    orange_css_match = re.search(r'\.sidebar-toggle-btn[^}]*color:\s*#FF6B35', content, re.DOTALL)
    if orange_css_match:
        print("   ✅ Found orange toggle button CSS")
    else:
        print("   ❌ Orange toggle button CSS not found")
        return False
    
    print("5. Checking JavaScript for both toggle buttons...")
    
    # Check for dual toggle functionality
    dual_toggle_match = re.search(r'sidebarToggleInternal.*addEventListener.*click', content, re.DOTALL)
    if dual_toggle_match:
        print("   ✅ Found JavaScript for internal toggle button")
    else:
        print("   ❌ JavaScript for internal toggle button not found")
        return False
    
    print("6. Checking always visible logo structure...")
    
    # Check for sidebar brand structure
    sidebar_brand_match = re.search(r'sidebar-brand.*sidebar-logo', content, re.DOTALL)
    if sidebar_brand_match:
        print("   ✅ Found sidebar brand structure with logo")
    else:
        print("   ❌ Sidebar brand structure not found")
        return False
    
    print("\n" + "=" * 60)
    print("✅ SIDEBAR ENHANCEMENTS TEST PASSED!")
    print("🎯 Client dashboard sidebar enhancements applied:")
    print("   • Logo: 80px max-height (60px when collapsed)")
    print("   • Orange toggle button inside sidebar")
    print("   • Always visible logo with smooth transitions")
    print("   • Dual toggle functionality (topnav + sidebar)")
    print("   • Orange color scheme (#FF6B35) for toggle button")
    
    return True

if __name__ == "__main__":
    success = test_sidebar_enhancements()
    if success:
        print("\n🎉 Test completed successfully!")
        print("💡 Next: Open client dashboard and test sidebar toggle functionality")
        print("🎨 The orange toggle button should be visible in the sidebar")
        print("📏 Logo should be 80px tall and resize to 60px when collapsed")
    else:
        print("\n❌ Test failed - sidebar enhancements may need review")
    
    sys.exit(0 if success else 1)
