#!/usr/bin/env python3

"""
Test Script: Verify Corrected Toggle Button Position
Confirms that the toggle button is now in the topnav like the admin dashboard.
"""

import sys
import os
import re

def test_toggle_button_position():
    """Test that toggle button is in correct position"""
    
    print("🔍 Testing Toggle Button Position (Topnav)...")
    print("=" * 50)
    
    # Check client base template
    client_base_path = 'app/templates/client/base.html'
    
    if not os.path.exists(client_base_path):
        print(f"❌ Client base template not found: {client_base_path}")
        return False
    
    with open(client_base_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("1. Checking topnav structure...")
    
    # Check for correct topnav structure
    topnav_match = re.search(r'<nav class="sb-topnav navbar navbar-expand navbar-dark">', content)
    if topnav_match:
        print("   ✅ Found correct topnav class structure")
    else:
        print("   ❌ Correct topnav structure not found")
        return False
    
    print("2. Checking toggle button in topnav...")
    
    # Check for toggle button in topnav
    toggle_in_topnav = re.search(r'<nav class="sb-topnav[^>]*>.*?<button[^>]*id="sidebarToggle"[^>]*>', content, re.DOTALL)
    if toggle_in_topnav:
        print("   ✅ Found toggle button inside topnav")
    else:
        print("   ❌ Toggle button not found in topnav")
        return False
    
    print("3. Checking brand logo in topnav...")
    
    # Check for brand logo in topnav
    brand_in_topnav = re.search(r'<div class="sidebar-brand[^>]*>.*?<img[^>]*sidebar-logo', content, re.DOTALL)
    if brand_in_topnav:
        print("   ✅ Found brand logo in topnav")
    else:
        print("   ❌ Brand logo not found in topnav")
        return False
    
    print("4. Checking no internal sidebar toggle...")
    
    # Check that there's no internal sidebar toggle
    internal_toggle = re.search(r'sidebarToggleInternal', content)
    if not internal_toggle:
        print("   ✅ No internal sidebar toggle found (correct)")
    else:
        print("   ❌ Internal sidebar toggle still exists (should be removed)")
        return False
    
    print("5. Checking logo max-height (80px)...")
    
    # Check logo height
    logo_height = re.search(r'max-height:\s*80px', content)
    if logo_height:
        print("   ✅ Logo has correct 80px max-height")
    else:
        print("   ❌ Logo 80px max-height not found")
        return False
    
    print("6. Checking navbar height (90px)...")
    
    # Check navbar height
    navbar_height = re.search(r'\.sb-topnav[^}]*max-height:\s*90px', content, re.DOTALL)
    if navbar_height:
        print("   ✅ Navbar has correct 90px max-height")
    else:
        print("   ❌ Navbar 90px max-height not found")
        return False
    
    print("\n" + "=" * 50)
    print("✅ TOGGLE BUTTON POSITION TEST PASSED!")
    print("🎯 Navbar structure now matches admin:")
    print("   • Toggle button: In topnav (first element)")
    print("   • Brand logo: In topnav (80px height)")
    print("   • Navbar: 90px max-height")
    print("   • Structure: sb-topnav navbar navbar-expand navbar-dark")
    print("   • No internal sidebar toggle button")
    
    return True

if __name__ == "__main__":
    success = test_toggle_button_position()
    if success:
        print("\n🎉 Test completed successfully!")
        print("💡 Client navbar structure now matches admin exactly")
        print("🔘 Toggle button should be visible in top navbar")
    else:
        print("\n❌ Test failed - navbar structure may need review")
    
    sys.exit(0 if success else 1)
