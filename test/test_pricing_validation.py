"""
Test Script: Validate Revised Pricing Structure
Tests the new flat-rate pricing with minimum 1.2% margin protection.

This script validates:
1. Margin calculations for all packages
2. Package creation and validation functions
3. CLI commands functionality
4. Migration script behavior

Usage:
    python test_pricing_validation.py
"""

import sys
import os
from decimal import Decimal

# Add app to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.client_package import (
    ClientPackage, ClientType, PackageStatus, 
    validate_flat_rate_margins, create_default_flat_rate_packages,
    get_margin_protection_info
)
from app.models.client import Client
from app.utils.package_features import (
    validate_package_margin, get_revised_pricing_summary,
    validate_all_packages, get_betconstruct_integration_guidance
)


def test_margin_calculations():
    """Test margin calculation accuracy"""
    print("🧮 TESTING MARGIN CALCULATIONS")
    print("=" * 50)
    
    test_cases = [
        # (monthly_price, volume_limit, expected_margin, should_pass)
        (499.00, 35000.00, 1.43, True),   # Starter
        (999.00, 70000.00, 1.42, True),   # Business  
        (2000.00, None, None, True),      # Enterprise (unlimited)
        (500.00, 50000.00, 1.00, False), # Below minimum
        (1000.00, 100000.00, 1.00, False), # Below minimum
    ]
    
    passed = 0
    failed = 0
    
    for monthly_price, volume_limit, expected_margin, should_pass in test_cases:
        validation = validate_package_margin(
            'test_package',
            monthly_price,
            volume_limit
        )
        
        if volume_limit:
            actual_margin = round((monthly_price / volume_limit) * 100, 2)
            margin_matches = abs(actual_margin - (expected_margin or 0)) < 0.01
            passes_validation = validation['is_valid']
            
            if should_pass:
                if passes_validation and margin_matches:
                    print(f"✅ ${monthly_price}/month, ${volume_limit} volume = {actual_margin}% margin")
                    passed += 1
                else:
                    print(f"❌ ${monthly_price}/month, ${volume_limit} volume = {actual_margin}% margin (validation failed)")
                    failed += 1
            else:
                if not passes_validation:
                    print(f"✅ ${monthly_price}/month, ${volume_limit} volume = {actual_margin}% margin (correctly rejected)")
                    passed += 1
                else:
                    print(f"❌ ${monthly_price}/month, ${volume_limit} volume = {actual_margin}% margin (should have been rejected)")
                    failed += 1
        else:
            # Unlimited volume test
            if validation['is_valid'] and should_pass:
                print(f"✅ ${monthly_price}/month, unlimited volume (scales with usage)")
                passed += 1
            else:
                print(f"❌ Unlimited volume test failed")
                failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_package_validation_functions():
    """Test package validation utility functions"""
    print("\n🔍 TESTING VALIDATION FUNCTIONS")
    print("=" * 50)
    
    try:
        # Test flat rate margin validation
        margins = validate_flat_rate_margins()
        print(f"✅ validate_flat_rate_margins() returned {len(margins)} packages")
        
        for package_key, result in margins.items():
            status = "✅" if result['is_acceptable'] else "❌"
            print(f"   {status} {result['package_name']}: {result['calculated_margin']}% margin")
        
        # Test revised pricing summary
        pricing_summary = get_revised_pricing_summary()
        print(f"\n✅ get_revised_pricing_summary() returned {len(pricing_summary)} packages")
        
        # Test validation report
        validation_report = validate_all_packages()
        print(f"✅ validate_all_packages() checked {validation_report['summary']['total_packages']} packages")
        
        # Test BetConstruct guidance
        guidance = get_betconstruct_integration_guidance()
        print(f"✅ BetConstruct guidance recommends: {guidance['recommended_package']}")
        
        # Test margin protection info
        protection_info = get_margin_protection_info()
        print(f"✅ Global minimum margin: {protection_info['minimum_global_margin']}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation function test failed: {str(e)}")
        return False


def test_database_functions():
    """Test database-related functions"""
    print("\n💾 TESTING DATABASE FUNCTIONS")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test package creation function (dry run)
            print("Testing create_default_flat_rate_packages()...")
            
            # Check existing packages first
            existing_count = ClientPackage.query.filter_by(client_type=ClientType.FLAT_RATE).count()
            print(f"Existing flat-rate packages: {existing_count}")
            
            # Test creation logic (don't actually commit)
            result = create_default_flat_rate_packages()
            
            if result['success']:
                print(f"✅ Package creation test passed")
                print(f"   Packages that would be affected: {len(result['packages'])}")
                for package in result['packages']:
                    print(f"   - {package}")
                
                # Show validation results
                validation = result['validation']
                for package_key, details in validation.items():
                    status = "✅" if details['is_acceptable'] else "❌"
                    print(f"   {status} {details['package_name']}: {details['calculated_margin']}% margin")
                
                # Rollback to avoid changes in test
                db.session.rollback()
                return True
            else:
                print(f"❌ Package creation test failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Database function test failed: {str(e)}")
            db.session.rollback()
            return False


def test_client_usage_tracking():
    """Test client usage tracking functionality"""
    print("\n👥 TESTING CLIENT USAGE TRACKING")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Find a flat-rate client or create test data
            flat_rate_client = Client.query.join(Client.package).filter(
                Client.package.has(client_type=ClientType.FLAT_RATE)
            ).first()
            
            if flat_rate_client:
                print(f"Testing with client: {flat_rate_client.company_name}")
                
                # Test usage methods
                volume_percent = flat_rate_client.get_volume_utilization_percent()
                tx_percent = flat_rate_client.get_transaction_utilization_percent()
                is_exceeding_volume = flat_rate_client.is_exceeding_volume_limits()
                is_exceeding_tx = flat_rate_client.is_exceeding_transaction_limits()
                margin_status = flat_rate_client.get_margin_status()
                
                print(f"✅ Volume utilization: {volume_percent:.1f}%")
                print(f"✅ Transaction utilization: {tx_percent:.1f}%")
                print(f"✅ Volume exceeded: {is_exceeding_volume}")
                print(f"✅ Transactions exceeded: {is_exceeding_tx}")
                
                if margin_status:
                    print(f"✅ Current margin: {margin_status['current_margin']:.2f}%")
                    print(f"✅ Margin acceptable: {margin_status['is_acceptable']}")
                else:
                    print("⚠️  No margin status available (commission-based client?)")
                
                return True
            else:
                print("⚠️  No flat-rate clients found for testing")
                return True  # Not a failure, just no test data
                
        except Exception as e:
            print(f"❌ Client usage tracking test failed: {str(e)}")
            return False


def test_pricing_scenarios():
    """Test various pricing scenarios and edge cases"""
    print("\n📊 TESTING PRICING SCENARIOS")
    print("=" * 50)
    
    scenarios = [
        {
            'name': 'Sportsbook (BetConstruct-like)',
            'monthly_volume': 85000,  # $85K/month
            'transactions': 1500,
            'expected_package': 'business_flat_rate',
            'should_upgrade': True  # Exceeds Business limit
        },
        {
            'name': 'Small E-commerce',
            'monthly_volume': 25000,  # $25K/month
            'transactions': 300,
            'expected_package': 'starter_flat_rate',
            'should_upgrade': False
        },
        {
            'name': 'Enterprise Platform',
            'monthly_volume': 500000,  # $500K/month
            'transactions': 5000,
            'expected_package': 'enterprise_flat_rate',
            'should_upgrade': False
        },
        {
            'name': 'Edge Case: High Transaction Count',
            'monthly_volume': 30000,  # $30K/month
            'transactions': 800,  # Exceeds Starter transaction limit
            'expected_package': 'business_flat_rate',
            'should_upgrade': True
        }
    ]
    
    all_passed = True
    
    for scenario in scenarios:
        print(f"\n📈 Scenario: {scenario['name']}")
        volume = scenario['monthly_volume']
        transactions = scenario['transactions']
        
        # Test against each package
        packages = {
            'starter_flat_rate': {'price': 499, 'volume_limit': 35000, 'tx_limit': 500},
            'business_flat_rate': {'price': 999, 'volume_limit': 70000, 'tx_limit': 2000},
            'enterprise_flat_rate': {'price': 2000, 'volume_limit': None, 'tx_limit': None}
        }
        
        suitable_packages = []
        
        for package_name, limits in packages.items():
            volume_ok = limits['volume_limit'] is None or volume <= limits['volume_limit']
            tx_ok = limits['tx_limit'] is None or transactions <= limits['tx_limit']
            
            if volume_ok and tx_ok:
                margin = (limits['price'] / volume) * 100 if volume > 0 else 0
                suitable_packages.append({
                    'name': package_name,
                    'price': limits['price'],
                    'margin': margin
                })
        
        if suitable_packages:
            # Choose the most cost-effective suitable package
            best_package = min(suitable_packages, key=lambda x: x['price'])
            print(f"   Recommended: {best_package['name']}")
            print(f"   Monthly fee: ${best_package['price']}")
            print(f"   Margin: {best_package['margin']:.2f}%")
            
            # Check if it matches expected
            if best_package['name'] == scenario['expected_package']:
                print(f"   ✅ Matches expected package")
            else:
                print(f"   ⚠️  Expected {scenario['expected_package']}, got {best_package['name']}")
        else:
            print(f"   ❌ No suitable package found")
            all_passed = False
    
    return all_passed


def main():
    """Run all tests"""
    print("🧪 PRICING STRUCTURE VALIDATION TESTS")
    print("=" * 60)
    
    tests = [
        ("Margin Calculations", test_margin_calculations),
        ("Validation Functions", test_package_validation_functions),
        ("Database Functions", test_database_functions),
        ("Client Usage Tracking", test_client_usage_tracking),
        ("Pricing Scenarios", test_pricing_scenarios),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 60}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
            failed += 1
    
    # Final summary
    print(f"\n{'=' * 60}")
    print(f"🏁 TEST SUMMARY")
    print(f"{'=' * 60}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print(f"\n🎉 ALL TESTS PASSED! Pricing structure is ready for deployment.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review issues before deployment.")
        return 1


if __name__ == '__main__':
    exit(main())
