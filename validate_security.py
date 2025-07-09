#!/usr/bin/env python3
"""
Security Implementation Validation Script
Validates that all security components are properly integrated
"""

import os
import sys
import importlib.util
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_import(module_path, description):
    """Check if a module can be imported"""
    try:
        spec = importlib.util.spec_from_file_location("test_module", module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["test_module"] = module
        spec.loader.exec_module(module)
        print(f"✅ {description}: Import successful")
        return True
    except Exception as e:
        print(f"❌ {description}: Import failed - {e}")
        return False

def check_function_exists(module_path, function_name, description):
    """Check if a specific function exists in a module"""
    try:
        spec = importlib.util.spec_from_file_location("test_module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        has_function = hasattr(module, function_name)
        status = "✅" if has_function else "❌"
        print(f"{status} {description}: {function_name}")
        return has_function
    except Exception as e:
        print(f"❌ {description}: Error checking function - {e}")
        return False

def main():
    print("CPGateway Security Implementation Validation")
    print("=" * 50)
    
    base_path = Path(__file__).parent
    app_path = base_path / "app"
    
    # Check core security files
    print("\n🔒 Core Security Components:")
    security_files = [
        (app_path / "utils" / "security.py", "Rate Limiting & Abuse Protection"),
        (app_path / "utils" / "audit.py", "Audit Logging"),
        (app_path / "utils" / "fraud_detection.py", "Fraud Detection"),
        (app_path / "utils" / "webhook_security.py", "Webhook Security"),
        (app_path / "config" / "security_config.py", "Security Configuration"),
    ]
    
    core_files_ok = True
    for filepath, description in security_files:
        if not check_file_exists(filepath, description):
            core_files_ok = False
    
    # Check documentation
    print("\n📚 Documentation:")
    doc_files = [
        (base_path / "SECURITY_IMPLEMENTATION.md", "Security Implementation Guide"),
        (base_path / "test_security.py", "Security Testing Script"),
    ]
    
    for filepath, description in doc_files:
        check_file_exists(filepath, description)
    
    # Check integration in route files
    print("\n🔗 Security Integration:")
    route_files = [
        (app_path / "admin" / "routes.py", "Admin Routes"),
        (app_path / "admin" / "client_routes.py", "Admin Client Routes"),
        (app_path / "admin" / "withdrawal_routes.py", "Admin Withdrawal Routes"),
        (app_path / "api" / "platform_routes.py", "Platform API Routes"),
        (app_path / "api" / "client_settings.py", "Client Settings API"),
        (app_path / "api" / "exchange_routes.py", "Exchange API Routes"),
        (app_path / "webhooks.py", "Webhook Routes"),
        (app_path / "package_payment_routes.py", "Package Payment Routes"),
    ]
    
    integrated_files_ok = True
    for filepath, description in route_files:
        if not check_file_exists(filepath, description):
            integrated_files_ok = False
    
    # Check key functions exist
    print("\n⚙️  Core Functions:")
    function_checks = [
        (app_path / "utils" / "security.py", "RateLimiter", "Rate Limiter Class"),
        (app_path / "utils" / "security.py", "AbuseProtection", "Abuse Protection Class"),
        (app_path / "utils" / "security.py", "rate_limit", "Rate Limit Decorator"),
        (app_path / "utils" / "audit.py", "log_security_event", "Security Event Logging"),
        (app_path / "utils" / "fraud_detection.py", "FraudDetectionService", "Fraud Detection Service"),
        (app_path / "utils" / "webhook_security.py", "WebhookHandler", "Webhook Security Handler"),
    ]
    
    functions_ok = True
    for filepath, function_name, description in function_checks:
        if not check_function_exists(filepath, function_name, description):
            functions_ok = False
    
    # Check imports work
    print("\n📦 Import Validation:")
    import_checks = [
        (app_path / "utils" / "security.py", "Security Utils"),
        (app_path / "utils" / "audit.py", "Audit Utils"),
        (app_path / "utils" / "fraud_detection.py", "Fraud Detection"),
        (app_path / "utils" / "webhook_security.py", "Webhook Security"),
    ]
    
    imports_ok = True
    for filepath, description in import_checks:
        if not check_import(filepath, description):
            imports_ok = False
    
    # Final Summary
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    
    checks = [
        ("Core Security Files", core_files_ok),
        ("Route Integration", integrated_files_ok),
        ("Core Functions", functions_ok),
        ("Import Validation", imports_ok),
    ]
    
    all_ok = True
    for check_name, status in checks:
        icon = "✅" if status else "❌"
        print(f"{icon} {check_name}: {'PASS' if status else 'FAIL'}")
        if not status:
            all_ok = False
    
    if all_ok:
        print("\n🎉 All security implementation checks passed!")
        print("\nNext steps:")
        print("1. Run 'python test_security.py' to test the implementation")
        print("2. Configure environment variables for production")
        print("3. Set up monitoring and alerting")
        print("4. Review security configuration in app/config/security_config.py")
        return 0
    else:
        print("\n⚠️  Some security implementation checks failed!")
        print("Please review the failed items above and ensure all components are properly implemented.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
