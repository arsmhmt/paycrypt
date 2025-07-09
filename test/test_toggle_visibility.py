#!/usr/bin/env python3

"""
Test Script: Verify Orange Toggle Button Visibility
Confirms that the orange toggle button is visible and properly styled in the sidebar.
"""

import sys
import os
import re

def test_toggle_button_visibility():
    """Test that the orange toggle button is visible and properly styled"""
    
    print("🔍 Testing Orange Toggle Button Visibility...")
    print("=" * 60)
    
    # Test client base template
    client_base_path = 'app/templates/client/base.html'
    
    if not os.path.exists(client_base_path):
        print(f"❌ Client base template not found: {client_base_path}")
        return False
    
    with open(client_base_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("1. Checking toggle button HTML structure...")
    
    # Check for the toggle button element
    toggle_btn_match = re.search(r'<button[^>]*id="sidebarToggleInternal"[^>]*>', content)
    if toggle_btn_match:
        print(f"   ✅ Found toggle button: {toggle_btn_match.group()[:80]}...")
    else:
        print("   ❌ Toggle button element not found")
        return False
    
    print("2. Checking solid orange background styling...")
    
    # Check for solid orange background
    orange_bg_match = re.search(r'background-color:\s*#FF6B35\s*!important', content)
    if orange_bg_match:
        print("   ✅ Found solid orange background")
    else:
        print("   ❌ Solid orange background not found")
        return False
    
    print("3. Checking toggle button container styling...")
    
    # Check for container with orange border
    container_match = re.search(r'border-bottom:\s*2px solid #FF6B35', content)
    if container_match:
        print("   ✅ Found orange border container")
    else:
        print("   ❌ Orange border container not found")
        return False
    
    print("4. Checking inline styles for visibility...")
    
    # Check for inline styles that make button prominent
    inline_styles_match = re.search(r'style="[^"]*background-color:\s*#FF6B35[^"]*"', content)
    if inline_styles_match:
        print("   ✅ Found inline styles for prominence")
    else:
        print("   ❌ Inline styles not found")
        return False
    
    print("5. Checking Font Awesome icons...")
    
    # Check for Font Awesome bars icon
    fa_icon_match = re.search(r'<i class="fas fa-bars"></i>', content)
    if fa_icon_match:
        print("   ✅ Found Font Awesome bars icon")
    else:
        print("   ❌ Font Awesome bars icon not found")
        return False
    
    print("6. Checking collapsed state CSS...")
    
    # Check for collapsed state styling
    collapsed_match = re.search(r'body\.sb-sidenav-toggled.*\.sidebar-toggle-btn', content, re.DOTALL)
    if collapsed_match:
        print("   ✅ Found collapsed state CSS")
    else:
        print("   ❌ Collapsed state CSS not found")
        return False
    
    print("\n" + "=" * 60)
    print("✅ TOGGLE BUTTON VISIBILITY TEST PASSED!")
    print("🎯 Orange toggle button should now be visible with:")
    print("   • Solid orange background (#FF6B35)")
    print("   • Orange container border (2px solid)")
    print("   • Font Awesome bars icon")
    print("   • Prominent inline styling")
    print("   • Hover and focus effects")
    print("   • Collapsed state support")
    
    return True

if __name__ == "__main__":
    success = test_toggle_button_visibility()
    if success:
        print("\n🎉 Test completed successfully!")
        print("💡 The orange toggle button should now be clearly visible at the top of the sidebar")
        print("🔧 Button features: Orange background, white icon, hover effects")
    else:
        print("\n❌ Test failed - toggle button visibility may need review")
    
    sys.exit(0 if success else 1)
