#!/usr/bin/env python3
"""
Create test clients for Commission-Based vs Flat-Rate client model testing
"""

from app import create_app
from app.models.client import Client
from app.models.client_package import ClientPackage
from app.extensions import db
from werkzeug.security import generate_password_hash

def create_test_clients():
    """Create test clients for both Commission-Based and Flat-Rate models"""
    
    print("🔧 Creating Test Clients for API Integration Testing")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Check if test clients already exist
            commission_client = Client.query.filter_by(email='demo_commission@test.com').first()
            flat_rate_client = Client.query.filter_by(email='demo_flatrate@test.com').first()
            
            # Create Commission-Based Test Client
            if not commission_client:
                print("📊 Creating Commission-Based Test Client...")
                
                # Find or create a commission-based package
                commission_package = ClientPackage.query.filter_by(name='Commission Basic').first()
                if not commission_package:
                    commission_package = ClientPackage(
                        name='Commission Basic',
                        slug='commission_basic',
                        description='Basic commission-based package',
                        price=0.00,
                        billing_cycle='monthly',
                        is_active=True,
                        features={'api_basic': True, 'support_basic': True}
                    )
                    db.session.add(commission_package)
                    db.session.flush()
                
                commission_client = Client(
                    name='Commission Demo Client',
                    username='commission_demo',
                    company_name='SportsBet Commission Ltd',
                    email='demo_commission@test.com',
                    phone='+1-555-0101',
                    address='123 Commission Ave',
                    city='Las Vegas',
                    country='USA',
                    website='https://sportsbet-commission.example.com',
                    password_hash=generate_password_hash('demo123'),
                    is_active=True,
                    is_verified=True,
                    contact_person='John Commission',
                    contact_email='contact@sportsbet-commission.example.com',
                    contact_phone='+1-555-0102',
                    deposit_commission_rate=5.0,  # 5% commission
                    withdrawal_commission_rate=3.0,  # 3% commission
                    package_id=commission_package.id,
                    balance=0.00
                )
                db.session.add(commission_client)
                print(f"✓ Created commission client: {commission_client.company_name}")
            else:
                print(f"✓ Commission client already exists: {commission_client.company_name}")
                
            # Create Flat-Rate Test Client
            if not flat_rate_client:
                print("📈 Creating Flat-Rate Test Client...")
                
                # Find or create a flat-rate package
                flat_rate_package = ClientPackage.query.filter_by(name='Flat Rate Professional').first()
                if not flat_rate_package:
                    flat_rate_package = ClientPackage(
                        name='Flat Rate Professional',
                        slug='flat_rate_professional',
                        description='Professional flat-rate package with full API access',
                        price=299.99,
                        billing_cycle='monthly',
                        is_active=True,
                        features={
                            'api_basic': True,
                            'api_advanced': True,
                            'wallet_management': True,
                            'webhook_management': True,
                            'withdrawal_management': True,
                            'support_priority': True,
                            'analytics_advanced': True
                        }
                    )
                    db.session.add(flat_rate_package)
                    db.session.flush()
                
                flat_rate_client = Client(
                    name='Flat Rate Demo Client',
                    username='flatrate_demo',
                    company_name='BetConstruct Enterprise Ltd',
                    email='demo_flatrate@test.com',
                    phone='+1-555-0201',
                    address='456 Enterprise Blvd',
                    city='New York',
                    country='USA',
                    website='https://betconstruct-enterprise.example.com',
                    password_hash=generate_password_hash('demo123'),
                    is_active=True,
                    is_verified=True,
                    contact_person='Sarah Enterprise',
                    contact_email='contact@betconstruct-enterprise.example.com',
                    contact_phone='+1-555-0202',
                    deposit_commission_rate=0.0,  # No commission for flat-rate
                    withdrawal_commission_rate=0.0,  # No commission for flat-rate
                    package_id=flat_rate_package.id,
                    balance=50000.00  # Enterprise clients typically have higher balances
                )
                db.session.add(flat_rate_client)
                print(f"✓ Created flat-rate client: {flat_rate_client.company_name}")
            else:
                print(f"✓ Flat-rate client already exists: {flat_rate_client.company_name}")
                
            # Commit all changes
            db.session.commit()
            
            print("\n🎉 Test clients created successfully!")
            print("\nClient Summary:")
            print("-" * 40)
            
            commission_client = Client.query.filter_by(email='demo_commission@test.com').first()
            flat_rate_client = Client.query.filter_by(email='demo_flatrate@test.com').first()
            
            if commission_client:
                print(f"Commission Client: {commission_client.company_name}")
                print(f"  • Email: {commission_client.email}")
                print(f"  • Package: {commission_client.package.name if commission_client.package else 'None'}")
                print(f"  • Deposit Commission: {commission_client.deposit_commission_rate}%")
                print(f"  • Withdrawal Commission: {commission_client.withdrawal_commission_rate}%")
                print(f"  • Commission-based: {commission_client.is_commission_based()}")
                print(f"  • Flat-rate: {commission_client.is_flat_rate()}")
                
            print()
            
            if flat_rate_client:
                print(f"Flat-Rate Client: {flat_rate_client.company_name}")
                print(f"  • Email: {flat_rate_client.email}")
                print(f"  • Package: {flat_rate_client.package.name if flat_rate_client.package else 'None'}")
                print(f"  • Monthly Fee: ${flat_rate_client.package.price if flat_rate_client.package else 0}")
                print(f"  • Balance: ${flat_rate_client.balance}")
                print(f"  • Commission-based: {flat_rate_client.is_commission_based()}")
                print(f"  • Flat-rate: {flat_rate_client.is_flat_rate()}")
                
            print("\n✅ Test setup complete! You can now run:")
            print("python test_client_integration_complete.py")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating test clients: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    try:
        success = create_test_clients()
        if success:
            print("\n🚀 Ready for testing!")
        else:
            print("\n💥 Setup failed!")
    except Exception as e:
        print(f"💥 Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
