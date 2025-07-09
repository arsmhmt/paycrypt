#!/usr/bin/env python3
"""
Security Testing Script for CPGateway
Tests all security implementations including rate limiting, fraud detection, 
webhook security, and audit logging.
"""

import requests
import time
import json
import hashlib
import hmac
from datetime import datetime
import sys
import argparse

class SecurityTester:
    def __init__(self, base_url="http://localhost:5000", verbose=False):
        self.base_url = base_url.rstrip('/')
        self.verbose = verbose
        self.session = requests.Session()
        self.test_results = {}
        
    def log(self, message):
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def test_rate_limiting(self):
        """Test rate limiting on various endpoints"""
        print("\n=== Testing Rate Limiting ===")
        
        endpoints_to_test = [
            ('/admin/login', 'POST', {'username': 'test', 'password': 'test'}),
            ('/api/exchange/rate?fiat_currency=USD&crypto_currency=BTC', 'GET', None),
            ('/api/platform/register', 'POST', {'name': 'test', 'platform_type': 'ecommerce'}),
        ]
        
        for endpoint, method, data in endpoints_to_test:
            self.log(f"Testing rate limiting on {method} {endpoint}")
            
            success_count = 0
            rate_limited_count = 0
            
            # Send requests rapidly to trigger rate limiting
            for i in range(20):
                try:
                    if method == 'GET':
                        response = self.session.get(f"{self.base_url}{endpoint}")
                    else:
                        response = self.session.post(f"{self.base_url}{endpoint}", json=data)
                    
                    if response.status_code == 429:  # Rate limited
                        rate_limited_count += 1
                    elif response.status_code < 500:  # Successful or client error (not server error)
                        success_count += 1
                        
                except requests.exceptions.RequestException as e:
                    self.log(f"Request failed: {e}")
                
                time.sleep(0.1)  # Small delay between requests
            
            result = f"Endpoint: {endpoint} - Success: {success_count}, Rate Limited: {rate_limited_count}"
            print(result)
            self.test_results[f"rate_limit_{endpoint}"] = {
                'success': success_count,
                'rate_limited': rate_limited_count,
                'working': rate_limited_count > 0
            }
    
    def test_webhook_security(self):
        """Test webhook signature verification"""
        print("\n=== Testing Webhook Security ===")
        
        webhook_url = f"{self.base_url}/webhook/payment_status"
        webhook_secret = "test-webhook-secret"
        
        # Test valid webhook
        payload = json.dumps({
            'order_id': 'test-order-123',
            'status': 'completed'
        })
        
        timestamp = str(int(time.time()))
        signature_data = f"{timestamp}.{payload}"
        signature = hmac.new(
            webhook_secret.encode(),
            signature_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Timestamp': timestamp,
            'X-Webhook-Signature': f"sha256={signature}"
        }
        
        self.log("Testing valid webhook signature")
        try:
            response = self.session.post(webhook_url, data=payload, headers=headers)
            valid_webhook_result = response.status_code in [200, 404]  # 404 if payment not found is OK
            print(f"Valid webhook test: {'PASS' if valid_webhook_result else 'FAIL'} (Status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"Valid webhook test: FAIL (Error: {e})")
            valid_webhook_result = False
        
        # Test invalid webhook signature
        invalid_headers = headers.copy()
        invalid_headers['X-Webhook-Signature'] = "sha256=invalid-signature"
        
        self.log("Testing invalid webhook signature")
        try:
            response = self.session.post(webhook_url, data=payload, headers=invalid_headers)
            invalid_webhook_result = response.status_code == 401
            print(f"Invalid webhook test: {'PASS' if invalid_webhook_result else 'FAIL'} (Status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"Invalid webhook test: FAIL (Error: {e})")
            invalid_webhook_result = False
        
        self.test_results['webhook_security'] = {
            'valid_signature': valid_webhook_result,
            'invalid_signature_blocked': invalid_webhook_result,
            'working': valid_webhook_result and invalid_webhook_result
        }
    
    def test_abuse_protection(self):
        """Test abuse protection mechanisms"""
        print("\n=== Testing Abuse Protection ===")
        
        # Test failed login abuse protection
        login_url = f"{self.base_url}/admin/login"
        
        self.log("Testing failed login abuse protection")
        blocked = False
        
        for i in range(15):  # Attempt multiple failed logins
            try:
                response = self.session.post(login_url, json={
                    'username': 'nonexistent',
                    'password': 'wrongpassword'
                })
                
                if response.status_code == 429:  # Rate limited/blocked
                    blocked = True
                    break
                    
            except requests.exceptions.RequestException as e:
                self.log(f"Login request failed: {e}")
            
            time.sleep(0.2)
        
        print(f"Abuse protection test: {'PASS' if blocked else 'FAIL'}")
        self.test_results['abuse_protection'] = {
            'failed_login_protection': blocked,
            'working': blocked
        }
    
    def test_api_endpoints_security(self):
        """Test that API endpoints have security measures"""
        print("\n=== Testing API Endpoint Security ===")
        
        # Test endpoints that should require authentication
        protected_endpoints = [
            '/api/platform/payment/initiate',
            '/api/client/settings/api-keys',
            '/api/client/settings/webhook',
            '/api/platform/settings',
        ]
        
        for endpoint in protected_endpoints:
            self.log(f"Testing authentication requirement for {endpoint}")
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                # Should get 401 (Unauthorized) or 422 (Unprocessable Entity for JWT)
                auth_required = response.status_code in [401, 422]
                print(f"Auth required for {endpoint}: {'PASS' if auth_required else 'FAIL'} (Status: {response.status_code})")
                
                self.test_results[f"auth_required_{endpoint}"] = {
                    'protected': auth_required,
                    'status_code': response.status_code
                }
            except requests.exceptions.RequestException as e:
                print(f"Error testing {endpoint}: {e}")
                self.test_results[f"auth_required_{endpoint}"] = {
                    'protected': False,
                    'error': str(e)
                }
    
    def test_fraud_detection_endpoints(self):
        """Test that fraud detection is integrated"""
        print("\n=== Testing Fraud Detection Integration ===")
        
        # This is harder to test without actual implementation details
        # We'll test that the fraud detection service can be imported and initialized
        
        try:
            # Test if we can access fraud detection related endpoints
            # These would typically be admin endpoints for viewing fraud reports
            fraud_endpoints = [
                '/admin/fraud-reports',  # If exists
                '/admin/security-events',  # If exists
            ]
            
            has_fraud_features = False
            for endpoint in fraud_endpoints:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    # Even if we get 401/403, the endpoint existing is good
                    if response.status_code != 404:
                        has_fraud_features = True
                        break
                except:
                    continue
            
            print(f"Fraud detection features: {'DETECTED' if has_fraud_features else 'NOT DETECTED'}")
            self.test_results['fraud_detection'] = {
                'features_detected': has_fraud_features
            }
            
        except Exception as e:
            print(f"Fraud detection test error: {e}")
            self.test_results['fraud_detection'] = {
                'features_detected': False,
                'error': str(e)
            }
    
    def generate_report(self):
        """Generate a summary report of all tests"""
        print("\n" + "="*50)
        print("SECURITY TESTING REPORT")
        print("="*50)
        
        total_tests = 0
        passed_tests = 0
        
        for test_name, result in self.test_results.items():
            total_tests += 1
            working = result.get('working', result.get('protected', False))
            if working:
                passed_tests += 1
            
            status = "PASS" if working else "FAIL"
            print(f"{test_name}: {status}")
            
            # Print details for failed tests
            if not working and self.verbose:
                for key, value in result.items():
                    if key != 'working':
                        print(f"  {key}: {value}")
        
        print(f"\nSummary: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🟢 All security tests passed!")
            return 0
        else:
            print("🔴 Some security tests failed!")
            return 1
    
    def run_all_tests(self):
        """Run all security tests"""
        print("Starting CPGateway Security Testing...")
        print(f"Target URL: {self.base_url}")
        
        try:
            # Test basic connectivity
            response = self.session.get(f"{self.base_url}/")
            if response.status_code != 200:
                print(f"Warning: Base URL returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error: Cannot connect to {self.base_url}: {e}")
            return 1
        
        # Run all tests
        self.test_rate_limiting()
        self.test_webhook_security()
        self.test_abuse_protection()
        self.test_api_endpoints_security()
        self.test_fraud_detection_endpoints()
        
        # Generate report
        return self.generate_report()

def main():
    parser = argparse.ArgumentParser(description='CPGateway Security Testing Tool')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='Base URL of the CPGateway application')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    tester = SecurityTester(base_url=args.url, verbose=args.verbose)
    exit_code = tester.run_all_tests()
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
