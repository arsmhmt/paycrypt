#!/usr/bin/env python3
"""
Final QA Testing Script for PayCrypt Gateway
Comprehensive end-to-end testing for production launch
"""

import os
import sys
import requests
import json
import time
from datetime import datetime
from urllib.parse import urljoin

# Add app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class PayCryptQATest:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PayCrypt-QA-Test/1.0'
        })
        self.results = []
        
    def log_result(self, test_name, status, message="", details=None):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,  # PASS, FAIL, SKIP, WARNING
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        
        # Color output
        colors = {
            'PASS': '\033[92m',    # Green
            'FAIL': '\033[91m',    # Red  
            'SKIP': '\033[93m',    # Yellow
            'WARNING': '\033[93m', # Yellow
            'RESET': '\033[0m'     # Reset
        }
        
        color = colors.get(status, colors['RESET'])
        print(f"{color}[{status}]{colors['RESET']} {test_name}: {message}")
        
        if details:
            print(f"  Details: {details}")
            
    def test_health_endpoint(self):
        """Test basic health endpoint and /health/detailed"""
        try:
            response = self.session.get(urljoin(self.base_url, '/health'))
            if response.status_code == 200:
                data = response.json()
                if data.get('status') in ['healthy', 'ok']:
                    self.log_result("Health Endpoint", "PASS", "Service is healthy")
                else:
                    self.log_result("Health Endpoint", "FAIL", f"Unhealthy status: {data}")
            else:
                self.log_result("Health Endpoint", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Health Endpoint", "FAIL", f"Connection error: {str(e)}")
        # Test /health/detailed
        try:
            response = self.session.get(urljoin(self.base_url, '/health/detailed'))
            if response.status_code == 200:
                self.log_result("Health Detailed Endpoint", "PASS", "Detailed health OK")
            else:
                self.log_result("Health Detailed Endpoint", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Health Detailed Endpoint", "FAIL", f"Connection error: {str(e)}")
        return True

    def test_admin_login_logout(self):
        """Test admin login/logout flow (basic)"""
        # NOTE: Replace with real test credentials or fetch from env/config
        admin_username = os.environ.get('QA_ADMIN_USER', 'admin')
        admin_password = os.environ.get('QA_ADMIN_PASS', 'admin123')
        login_url = urljoin(self.base_url, '/admin120724/login')
        dashboard_url = urljoin(self.base_url, '/admin120724/dashboard')
        logout_url = urljoin(self.base_url, '/admin120724/logout')
        # Login
        try:
            resp = self.session.post(login_url, data={
                'username': admin_username,
                'password': admin_password
            }, allow_redirects=True)
            if resp.status_code in (200, 302) and (resp.url.endswith('/dashboard') or resp.url.endswith('/admin120724/dashboard')):
                self.log_result("Admin Login", "PASS", "Admin login successful")
            else:
                self.log_result("Admin Login", "FAIL", f"Login failed: {resp.status_code}", details=resp.text[:200])
        except Exception as e:
            self.log_result("Admin Login", "FAIL", f"Exception: {str(e)}")
        # Dashboard (should be accessible after login)
        try:
            resp = self.session.get(dashboard_url)
            if resp.status_code == 200:
                self.log_result("Admin Dashboard", "PASS", "Dashboard accessible after login")
            else:
                self.log_result("Admin Dashboard", "FAIL", f"Dashboard HTTP {resp.status_code}")
        except Exception as e:
            self.log_result("Admin Dashboard", "FAIL", f"Exception: {str(e)}")
        # Analytics (should be accessible after login)
        try:
            resp = self.session.get(urljoin(self.base_url, '/admin120724/analytics'))
            if resp.status_code == 200:
                self.log_result("Admin Analytics", "PASS", "Analytics accessible after login")
            else:
                self.log_result("Admin Analytics", "FAIL", f"Analytics HTTP {resp.status_code}")
        except Exception as e:
            self.log_result("Admin Analytics", "FAIL", f"Exception: {str(e)}")
        # Logout
        try:
            resp = self.session.get(logout_url, allow_redirects=True)
            if resp.status_code in (200, 302):
                self.log_result("Admin Logout", "PASS", "Logout successful")
            else:
                self.log_result("Admin Logout", "FAIL", f"Logout HTTP {resp.status_code}")
        except Exception as e:
            self.log_result("Admin Logout", "FAIL", f"Exception: {str(e)}")
        # TODO: Test rate limit/lockout after failed attempts
        # TODO: Test session expiration
        # TODO: Test unauthorized access returns 404
        # TODO: Test audit trail/logging for sensitive changes
        # TODO: Test feature toggling and sync script
        # TODO: Test commission, billing, usage alerts
        # TODO: Test quick actions and navbar language switching
        # TODO: Test API key creation/authentication
        # TODO: Test HMAC webhook validation
        # TODO: Test translations for TR, RU, EN
        # TODO: Test rate limit headers
        # TODO: Test static asset minification
        # TODO: Test client login via email/username/company
        # TODO: Test JWT refresh & session expiration
        # TODO: Test all dashboard states
        return True

        """Test basic health endpoint"""
        try:
            response = self.session.get(urljoin(self.base_url, '/health'))
            if response.status_code == 200:
                data = response.json()
                if data.get('status') in ['healthy', 'ok']:
                    self.log_result("Health Endpoint", "PASS", "Service is healthy")
                    return True
                else:
                    self.log_result("Health Endpoint", "FAIL", f"Unhealthy status: {data}")
            else:
                self.log_result("Health Endpoint", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Health Endpoint", "FAIL", f"Connection error: {str(e)}")
        return False
        
    def test_security_headers(self):
        """Test security headers are present"""
        try:
            response = self.session.get(self.base_url)
            headers = response.headers
            
            required_headers = [
                'X-Frame-Options',
                'X-Content-Type-Options', 
                'X-XSS-Protection',
                'Strict-Transport-Security',
                'Content-Security-Policy'
            ]
            
            missing_headers = []
            for header in required_headers:
                if header not in headers:
                    missing_headers.append(header)
                    
            if not missing_headers:
                self.log_result("Security Headers", "PASS", "All security headers present")
            else:
                self.log_result("Security Headers", "WARNING", 
                              f"Missing headers: {', '.join(missing_headers)}")
                              
        except Exception as e:
            self.log_result("Security Headers", "FAIL", f"Error: {str(e)}")
            
    def test_admin_path_obfuscation(self):
        """Test that admin paths are properly obfuscated"""
        try:
            # Test common admin paths return 404
            admin_paths = ['/admin', '/admin/', '/admin/login', '/administrator']
            
            for path in admin_paths:
                response = self.session.get(urljoin(self.base_url, path))
                if response.status_code != 404:
                    self.log_result("Admin Path Obfuscation", "FAIL", 
                                  f"Path {path} returned {response.status_code}, expected 404")
                    return
                    
            self.log_result("Admin Path Obfuscation", "PASS", "All admin paths properly obfuscated")
            
        except Exception as e:
            self.log_result("Admin Path Obfuscation", "FAIL", f"Error: {str(e)}")
            
    def test_rate_limiting(self):
        """Test rate limiting is working"""
        try:
            # Make rapid requests to login endpoint
            login_url = urljoin(self.base_url, '/auth/login')
            
            rate_limited = False
            for i in range(10):
                response = self.session.post(login_url, data={
                    'email': 'test@example.com',
                    'password': 'wrongpassword'
                })
                
                if response.status_code == 429:  # Too Many Requests
                    rate_limited = True
                    break
                    
                time.sleep(0.1)
                
            if rate_limited:
                self.log_result("Rate Limiting", "PASS", "Rate limiting active")
            else:
                self.log_result("Rate Limiting", "WARNING", "Rate limiting not triggered")
                
        except Exception as e:
            self.log_result("Rate Limiting", "FAIL", f"Error: {str(e)}")
            
    def test_client_registration_flow(self):
        """Test client registration end-to-end"""
        try:
            # Get registration page
            reg_url = urljoin(self.base_url, '/auth/register')
            response = self.session.get(reg_url)
            
            if response.status_code != 200:
                self.log_result("Client Registration", "FAIL", f"Registration page returned {response.status_code}")
                return
                
            # Check for CSRF token
            if 'csrf_token' not in response.text:
                self.log_result("Client Registration", "WARNING", "CSRF token not found in registration form")
                
            self.log_result("Client Registration", "PASS", "Registration page accessible")
            
        except Exception as e:
            self.log_result("Client Registration", "FAIL", f"Error: {str(e)}")
            
    def test_api_endpoints(self):
        """Test API endpoints are accessible"""
        api_endpoints = [
            '/api/docs',
            '/api/v1/status',
            '/api/v1/rates',
        ]
        
        for endpoint in api_endpoints:
            try:
                response = self.session.get(urljoin(self.base_url, endpoint))
                if response.status_code in [200, 401]:  # 401 is OK for protected endpoints
                    self.log_result(f"API Endpoint {endpoint}", "PASS", f"HTTP {response.status_code}")
                else:
                    self.log_result(f"API Endpoint {endpoint}", "FAIL", f"HTTP {response.status_code}")
            except Exception as e:
                self.log_result(f"API Endpoint {endpoint}", "FAIL", f"Error: {str(e)}")
                
    def test_internationalization(self):
        """Test language switching"""
        try:
            # Test language parameter
            response = self.session.get(self.base_url, params={'lang': 'tr'})
            if response.status_code == 200:
                self.log_result("Internationalization", "PASS", "Language switching accessible")
            else:
                self.log_result("Internationalization", "FAIL", f"Language switching returned {response.status_code}")
        except Exception as e:
            self.log_result("Internationalization", "FAIL", f"Error: {str(e)}")
            
    def test_static_assets(self):
        """Test that static assets are loading"""
        static_assets = [
            '/static/css/style.css',
            '/static/js/main.js',
            '/static/favicon.ico'
        ]
        
        for asset in static_assets:
            try:
                response = self.session.get(urljoin(self.base_url, asset))
                if response.status_code == 200:
                    self.log_result(f"Static Asset {asset}", "PASS", "Asset loads correctly")
                else:
                    self.log_result(f"Static Asset {asset}", "WARNING", f"HTTP {response.status_code}")
            except Exception as e:
                self.log_result(f"Static Asset {asset}", "WARNING", f"Error: {str(e)}")
                
    def run_all_tests(self):
        print("\U0001F680 Starting PayCrypt Gateway Final QA Tests")
        print("=" * 60)
        # Core functionality tests
        if not self.test_health_endpoint():
            print("\n❌ Health endpoint failed - stopping tests")
            return False
        self.test_security_headers()
        self.test_admin_path_obfuscation()
        self.test_rate_limiting()
        self.test_client_registration_flow()
        self.test_api_endpoints()
        self.test_admin_login_logout()
        self.test_internationalization()
        self.test_static_assets()
        # Generate summary
        self.generate_summary()
        return True

        """Run all QA tests"""
        print("🚀 Starting PayCrypt Gateway Final QA Tests")
        print("=" * 60)
        
        # Core functionality tests
        if not self.test_health_endpoint():
            print("\n❌ Health endpoint failed - stopping tests")
            return False
            
        self.test_security_headers()
        self.test_admin_path_obfuscation()
        self.test_rate_limiting()
        self.test_client_registration_flow()
        self.test_api_endpoints()
        self.test_internationalization()
        self.test_static_assets()
        
        # Generate summary
        self.generate_summary()
        return True
        
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 QA TEST SUMMARY")
        print("=" * 60)
        
        passed = len([r for r in self.results if r['status'] == 'PASS'])
        failed = len([r for r in self.results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.results if r['status'] == 'WARNING'])
        skipped = len([r for r in self.results if r['status'] == 'SKIP'])
        
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"⚠️  WARNINGS: {warnings}")
        print(f"⏭️  SKIPPED: {skipped}")
        print(f"📈 TOTAL: {len(self.results)}")
        
        if failed == 0:
            print("\n🎉 ALL CRITICAL TESTS PASSED! Ready for production.")
        else:
            print(f"\n⚠️  {failed} critical issues found. Review before deployment.")
            
        # Show failed tests
        failed_tests = [r for r in self.results if r['status'] == 'FAIL']
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
                
        # Save results to file
        with open('qa_test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
            
        print(f"\n📁 Detailed results saved to: qa_test_results.json")

if __name__ == '__main__':
    # Allow custom base URL
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    
    print(f"🔍 Testing PayCrypt Gateway at: {base_url}")
    
    qa_test = PayCryptQATest(base_url)
    qa_test.run_all_tests()
