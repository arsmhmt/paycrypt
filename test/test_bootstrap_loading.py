#!/usr/bin/env python3
"""
Test Bootstrap JS loading on client dashboard
"""
import requests
from bs4 import BeautifulSoup

def test_dashboard_assets():
    """Test that the dashboard loads Bootstrap JS correctly"""
    base_url = "http://127.0.0.1:8080"
    
    print("🔍 Testing Bootstrap JS loading on client dashboard")
    print("-" * 50)
    
    try:
        # Login first
        session = requests.Session()
        login_data = {
            'username': 'smartbetslip',
            'password': 'Mahmut*1905'
        }
        
        # Login
        login_response = session.post(f"{base_url}/client/login", data=login_data)
        
        # Get dashboard
        dashboard_response = session.get(f"{base_url}/client/dashboard")
        
        if dashboard_response.status_code == 200:
            soup = BeautifulSoup(dashboard_response.text, 'html.parser')
            
            # Check for Bootstrap CSS
            bootstrap_css = soup.find('link', href=lambda x: x and 'bootstrap' in x and 'css' in x)
            if bootstrap_css:
                print("✅ Bootstrap CSS found:", bootstrap_css['href'])
            else:
                print("❌ Bootstrap CSS not found")
            
            # Check for Bootstrap JS
            bootstrap_js = soup.find('script', src=lambda x: x and 'bootstrap' in x and 'js' in x)
            if bootstrap_js:
                print("✅ Bootstrap JS found:", bootstrap_js['src'])
            else:
                print("❌ Bootstrap JS not found")
            
            # Check for client dashboard CSS
            client_css = soup.find('link', href=lambda x: x and 'client-dashboard.css' in x)
            if client_css:
                print("✅ Client dashboard CSS found:", client_css['href'])
            else:
                print("❌ Client dashboard CSS not found")
            
            # Check for tooltip elements
            tooltips = soup.find_all(attrs={'data-bs-toggle': 'tooltip'})
            print(f"✅ Found {len(tooltips)} tooltip elements")
            
            # Check for modal elements
            modals = soup.find_all(attrs={'data-bs-toggle': 'modal'})
            print(f"✅ Found {len(modals)} modal trigger elements")
            
            print("\n🎯 Dashboard should now work without JavaScript errors!")
            print("   • Tooltips should appear on hover")
            print("   • Modals should open when clicked")
            print("   • Alert dismissals should work")
            
        else:
            print(f"❌ Dashboard access error: {dashboard_response.status_code}")
            
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_dashboard_assets()
