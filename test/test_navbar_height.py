#!/usr/bin/env python3

"""
Test Script: Verify Top Navbar Height (90px)
Confirms that the top navbar has been set to 90px max-height with proper logo spacing.
"""

import sys
import os
import re

def test_navbar_height():
    """Test top navbar height adjustment"""
    
    print("🔍 Testing Top Navbar Height (90px)...")
    print("=" * 50)
    
    # Check client base template
    client_base_path = 'app/templates/client/base.html'
    
    if not os.path.exists(client_base_path):
        print(f"❌ Client base template not found: {client_base_path}")
        return False
    
    with open(client_base_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("1. Checking navbar max-height (90px)...")
    
    # Check for 90px max-height
    max_height_match = re.search(r'\.sb-topnav[^}]*max-height:\s*90px', content, re.DOTALL)
    if max_height_match:
        print("   ✅ Found max-height: 90px for .sb-topnav")
    else:
        print("   ❌ max-height: 90px not found")
        return False
    
    print("2. Checking navbar height (90px)...")
    
    # Check for 90px height
    height_match = re.search(r'\.sb-topnav[^}]*height:\s*90px', content, re.DOTALL)
    if height_match:
        print("   ✅ Found height: 90px for .sb-topnav")
    else:
        print("   ❌ height: 90px not found")
        return False
    
    print("3. Checking navbar padding (5px)...")
    
    # Check for 5px padding
    padding_match = re.search(r'\.sb-topnav[^}]*padding:\s*5px\s+0', content, re.DOTALL)
    if padding_match:
        print("   ✅ Found padding: 5px 0 for .sb-topnav")
    else:
        print("   ❌ padding: 5px 0 not found")
        return False
    
    print("4. Checking logo max-height (80px)...")
    
    # Check for 80px logo max-height
    logo_height_match = re.search(r'max-height:\s*80px', content)
    if logo_height_match:
        print("   ✅ Found max-height: 80px for logo")
    else:
        print("   ❌ max-height: 80px for logo not found")
        return False
    
    print("5. Checking navbar element alignment CSS...")
    
    # Check for navbar alignment CSS
    alignment_match = re.search(r'\.sb-topnav\s+\.navbar-nav[^}]*align-items:\s*center', content, re.DOTALL)
    if alignment_match:
        print("   ✅ Found navbar alignment CSS")
    else:
        print("   ❌ Navbar alignment CSS not found")
        return False
    
    print("\n" + "=" * 50)
    print("✅ NAVBAR HEIGHT TEST PASSED!")
    print("🎯 Top navbar specifications:")
    print("   • Navbar: 90px max-height and height")
    print("   • Padding: 5px top/bottom")
    print("   • Logo: 80px max-height (5px spacing)")
    print("   • Elements: Center-aligned")
    
    return True

if __name__ == "__main__":
    success = test_navbar_height()
    if success:
        print("\n🎉 Test completed successfully!")
        print("💡 The navbar is now 90px tall with proper logo spacing")
        print("📏 Logo has 5px top and bottom spacing within navbar")
    else:
        print("\n❌ Test failed - navbar height may need review")
    
    sys.exit(0 if success else 1)
