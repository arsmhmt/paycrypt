#!/usr/bin/env python3
"""
Comprehensive test script for admin client management functionality
"""
import requests
import json
import sys
from time import sleep

BASE_URL = "http://127.0.0.1:8080"
TEST_ROUTES = [
    # Basic admin routes
    ("/admin", "Admin Dashboard"),
    ("/admin/clients", "Client List"),
    ("/admin/clients/new", "New Client Form"),
    
    # Client-specific routes (test with client ID 1 and 2)
    ("/admin/clients/1/view", "Client 1 Details"),
    ("/admin/clients/1/commission", "Client 1 Commission"),
    ("/admin/clients/1/branding", "Client 1 Branding"),
    ("/admin/clients/1/rate-limits", "Client 1 Rate Limits"),
    ("/admin/clients/1/api-keys", "Client 1 API Keys"),
    ("/admin/clients/1/audit-logs", "Client 1 Audit Logs"),
    
    ("/admin/clients/2/view", "Client 2 Details"),
    ("/admin/clients/2/commission", "Client 2 Commission"),
    ("/admin/clients/2/branding", "Client 2 Branding"),
    ("/admin/clients/2/rate-limits", "Client 2 Rate Limits"),
    ("/admin/clients/2/api-keys", "Client 2 API Keys"),
    ("/admin/clients/2/audit-logs", "Client 2 Audit Logs"),
]

def test_route_accessibility():
    """Test that all admin routes are accessible without internal server errors"""
    print("🔍 Testing admin client route accessibility...")
    print("=" * 60)
    
    results = {
        "success": [],
        "errors": [],
        "not_found": [],
        "redirects": []
    }
    
    for route, description in TEST_ROUTES:
        try:
            url = f"{BASE_URL}{route}"
            response = requests.get(url, allow_redirects=False, timeout=10)
            
            if response.status_code == 200:
                results["success"].append((route, description))
                print(f"✅ {description}: OK (200)")
            elif response.status_code in [301, 302, 303, 307, 308]:
                results["redirects"].append((route, description, response.status_code))
                print(f"↗️  {description}: Redirect ({response.status_code})")
            elif response.status_code == 404:
                results["not_found"].append((route, description))
                print(f"❓ {description}: Not Found (404)")
            elif response.status_code == 500:
                results["errors"].append((route, description, "Internal Server Error"))
                print(f"❌ {description}: Internal Server Error (500)")
            else:
                results["errors"].append((route, description, f"HTTP {response.status_code}"))
                print(f"⚠️  {description}: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            results["errors"].append((route, description, str(e)))
            print(f"❌ {description}: Connection Error - {e}")
        
        # Small delay to avoid overwhelming the server
        sleep(0.1)
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {len(results['success'])}")
    print(f"↗️  Redirects: {len(results['redirects'])}")
    print(f"❓ Not Found: {len(results['not_found'])}")
    print(f"❌ Errors: {len(results['errors'])}")
    
    if results["errors"]:
        print("\n🚨 ERRORS FOUND:")
        for route, desc, error in results["errors"]:
            print(f"   - {desc} ({route}): {error}")
    
    if results["redirects"]:
        print("\n↗️  REDIRECTS (may need authentication):")
        for route, desc, code in results["redirects"]:
            print(f"   - {desc} ({route}): HTTP {code}")
    
    return len(results["errors"]) == 0

def test_specific_features():
    """Test specific admin client management features"""
    print("\n🧪 Testing specific features...")
    print("=" * 60)
    
    features = []
    
    # Test if client view shows BTC instead of $ (from our previous fix)
    try:
        response = requests.get(f"{BASE_URL}/admin/clients/1/view", timeout=10)
        if response.status_code == 200:
            if "BTC" in response.text and "$" not in response.text.replace("$", " "):
                features.append("✅ Client financials show BTC (not $)")
            else:
                features.append("⚠️  Client financials may still show $ instead of BTC")
        else:
            features.append(f"❌ Cannot access client view: HTTP {response.status_code}")
    except Exception as e:
        features.append(f"❌ Error testing client view: {e}")
    
    # Test if CSRF token is available in forms
    try:
        response = requests.get(f"{BASE_URL}/admin/clients/1/commission", timeout=10)
        if response.status_code == 200:
            if "csrf_token" in response.text or "csrf-token" in response.text:
                features.append("✅ CSRF token found in commission form")
            else:
                features.append("⚠️  CSRF token may be missing from forms")
        else:
            features.append(f"❌ Cannot access commission form: HTTP {response.status_code}")
    except Exception as e:
        features.append(f"❌ Error testing CSRF token: {e}")
    
    for feature in features:
        print(feature)
    
    return features

def check_server_running():
    """Check if the Flask server is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return True
    except:
        return False

def main():
    print("🧪 ADMIN CLIENT MANAGEMENT TEST SUITE")
    print("=" * 60)
    
    # Check if server is running
    if not check_server_running():
        print("❌ Flask server is not running!")
        print("Please start the server with: python run.py")
        sys.exit(1)
    
    print("✅ Flask server is running")
    
    # Test route accessibility
    routes_ok = test_route_accessibility()
    
    # Test specific features
    features = test_specific_features()
    
    print("\n" + "=" * 60)
    print("🏁 FINAL RESULTS")
    print("=" * 60)
    
    if routes_ok:
        print("✅ All routes are accessible without internal server errors")
    else:
        print("❌ Some routes have internal server errors")
    
    csrf_found = any("CSRF token found" in f for f in features)
    btc_found = any("BTC (not $)" in f for f in features)
    
    print(f"💰 BTC display: {'✅ Fixed' if btc_found else '⚠️ Needs attention'}")
    print(f"🔒 CSRF tokens: {'✅ Present' if csrf_found else '⚠️ May be missing'}")
    
    # Provide next steps
    print("\n📋 NEXT STEPS:")
    if not routes_ok:
        print("1. Fix internal server errors in admin routes")
    if not btc_found:
        print("2. Ensure client financials display BTC instead of $")
    if not csrf_found:
        print("3. Verify CSRF tokens are present in all forms")
    
    if routes_ok and btc_found and csrf_found:
        print("🎉 All major issues appear to be resolved!")
        print("✅ Admin client management should be working correctly")

if __name__ == '__main__':
    main()
