"""
Database Migration: Update Flat-Rate Package Pricing Structure
Implements revised pricing with minimum 1.2% margin protection.

Run this script to update existing packages with new pricing:
- Starter: $499/month, $35K volume (1.43% margin)
- Business: $999/month, $70K volume (1.42% margin) 
- Enterprise: $2000/month, Unlimited volume

Usage:
    python migrate_pricing_structure.py [--dry-run] [--backup]
"""

import sys
import os
from decimal import Decimal
from datetime import datetime

# Add app to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.client_package import ClientPackage, ClientType, PackageStatus
from app.models.client import Client
from app.utils.package_features import validate_package_margin, get_revised_pricing_summary, validate_all_packages


# Revised pricing configuration with margin protection
REVISED_PRICING_CONFIG = {
    'starter_flat_rate': {
        'name': 'Starter Flat Rate',
        'monthly_price': Decimal('499.00'),
        'max_volume_per_month': Decimal('35000.00'),  # 1.43% margin
        'min_margin_percent': Decimal('1.43'),
        'max_transactions_per_month': 500,
        'max_api_calls_per_month': 10000,
        'max_wallets': 1,
        'description': 'Perfect for small businesses getting started with crypto payments. No real-time features.',
        'sort_order': 1
    },
    'business_flat_rate': {
        'name': 'Business Flat Rate',
        'monthly_price': Decimal('999.00'),
        'max_volume_per_month': Decimal('70000.00'),  # 1.42% margin
        'min_margin_percent': Decimal('1.42'),
        'max_transactions_per_month': 2000,
        'max_api_calls_per_month': 50000,
        'max_wallets': 3,
        'description': 'Ideal for growing businesses with moderate transaction volumes. Includes webhooks and analytics.',
        'sort_order': 2,
        'is_popular': True
    },
    'enterprise_flat_rate': {
        'name': 'Enterprise Flat Rate',
        'monthly_price': Decimal('2000.00'),
        'max_volume_per_month': None,  # Unlimited
        'min_margin_percent': Decimal('1.20'),
        'max_transactions_per_month': None,  # Unlimited
        'max_api_calls_per_month': None,  # Unlimited
        'max_wallets': None,  # Unlimited
        'description': 'Full-featured enterprise solution with unlimited scaling and dedicated support.',
        'sort_order': 3
    }
}


def create_backup_table():
    """Create backup of current packages before migration"""
    try:
        # Create backup table
        db.engine.execute('''
            CREATE TABLE IF NOT EXISTS client_packages_backup AS 
            SELECT *, CURRENT_TIMESTAMP as backup_created_at 
            FROM client_packages
        ''')
        print("✅ Backup table created: client_packages_backup")
        return True
    except Exception as e:
        print(f"❌ Failed to create backup: {str(e)}")
        return False


def validate_current_packages():
    """Validate current package margins and return report"""
    print("\n📊 CURRENT PACKAGE ANALYSIS")
    print("=" * 50)
    
    flat_rate_packages = ClientPackage.query.filter_by(
        client_type=ClientType.FLAT_RATE,
        status=PackageStatus.ACTIVE
    ).all()
    
    analysis = []
    
    for package in flat_rate_packages:
        if package.monthly_price and package.max_volume_per_month:
            current_margin = (float(package.monthly_price) / float(package.max_volume_per_month)) * 100
            is_acceptable = current_margin >= 1.20
            
            analysis.append({
                'id': package.id,
                'name': package.name,
                'monthly_price': float(package.monthly_price),
                'max_volume': float(package.max_volume_per_month),
                'current_margin': round(current_margin, 2),
                'is_acceptable': is_acceptable,
                'clients_count': package.clients.count() if hasattr(package, 'clients') else 0
            })
            
            status = "✅" if is_acceptable else "❌"
            print(f"{status} {package.name}: ${package.monthly_price}/month, ${package.max_volume_per_month} volume = {current_margin:.2f}% margin")
        else:
            print(f"⚠️  {package.name}: Missing pricing data")
    
    return analysis


def update_packages(dry_run=False):
    """Update packages with revised pricing structure"""
    print(f"\n🔄 {'DRY RUN: ' if dry_run else ''}UPDATING PACKAGES")
    print("=" * 50)
    
    updated_packages = []
    created_packages = []
    errors = []
    
    for package_key, config in REVISED_PRICING_CONFIG.items():
        try:
            # Try to find existing package by name
            existing = ClientPackage.query.filter_by(
                name=config['name'],
                client_type=ClientType.FLAT_RATE
            ).first()
            
            if existing:
                # Update existing package
                print(f"🔄 Updating: {existing.name}")
                
                if not dry_run:
                    existing.monthly_price = config['monthly_price']
                    existing.max_volume_per_month = config['max_volume_per_month']
                    existing.min_margin_percent = config['min_margin_percent']
                    existing.max_transactions_per_month = config['max_transactions_per_month']
                    existing.max_api_calls_per_month = config['max_api_calls_per_month']
                    existing.max_wallets = config['max_wallets']
                    existing.description = config['description']
                    existing.sort_order = config['sort_order']
                    existing.is_popular = config.get('is_popular', False)
                    existing.updated_at = datetime.utcnow()
                
                updated_packages.append(existing.name)
                
                # Validate new margin
                validation = validate_package_margin(
                    package_key,
                    float(config['monthly_price']),
                    float(config['max_volume_per_month']) if config['max_volume_per_month'] else None
                )
                print(f"   New margin: {validation.get('margin_percent', 'N/A')}% ({'✅' if validation['is_valid'] else '❌'})")
                
            else:
                # Create new package
                print(f"➕ Creating: {config['name']}")
                
                if not dry_run:
                    new_package = ClientPackage(
                        name=config['name'],
                        description=config['description'],
                        client_type=ClientType.FLAT_RATE,
                        monthly_price=config['monthly_price'],
                        max_volume_per_month=config['max_volume_per_month'],
                        min_margin_percent=config['min_margin_percent'],
                        max_transactions_per_month=config['max_transactions_per_month'],
                        max_api_calls_per_month=config['max_api_calls_per_month'],
                        max_wallets=config['max_wallets'],
                        sort_order=config['sort_order'],
                        is_popular=config.get('is_popular', False),
                        status=PackageStatus.ACTIVE
                    )
                    
                    db.session.add(new_package)
                
                created_packages.append(config['name'])
                
        except Exception as e:
            error_msg = f"Failed to update {config['name']}: {str(e)}"
            errors.append(error_msg)
            print(f"❌ {error_msg}")
    
    if not dry_run and (updated_packages or created_packages):
        try:
            db.session.commit()
            print(f"\n✅ Database updated successfully")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Database update failed: {str(e)}")
            return {
                'updated': [],
                'created': [],
                'errors': [f"Database commit failed: {str(e)}"]
            }
    
    return {
        'updated': updated_packages,
        'created': created_packages,
        'errors': errors
    }


def check_client_impact():
    """Check how many clients will be affected by pricing changes"""
    print("\n👥 CLIENT IMPACT ANALYSIS")
    print("=" * 50)
    
    # Get clients with flat-rate packages
    flat_rate_clients = Client.query.join(Client.package).filter(
        Client.package.has(client_type=ClientType.FLAT_RATE)
    ).all()
    
    impact = {
        'total_clients': len(flat_rate_clients),
        'by_package': {},
        'high_volume_clients': [],
        'margin_violations': []
    }
    
    for client in flat_rate_clients:
        package_name = client.package.name if client.package else 'Unknown'
        
        if package_name not in impact['by_package']:
            impact['by_package'][package_name] = 0
        impact['by_package'][package_name] += 1
        
        # Check for high volume clients
        current_volume = float(client.current_month_volume or 0)
        if current_volume > 50000:  # High volume threshold
            impact['high_volume_clients'].append({
                'id': client.id,
                'company_name': client.company_name,
                'package': package_name,
                'current_volume': current_volume
            })
        
        # Check for potential margin violations
        margin_status = client.get_margin_status()
        if margin_status and not margin_status['is_acceptable']:
            impact['margin_violations'].append({
                'id': client.id,
                'company_name': client.company_name,
                'package': package_name,
                'current_margin': margin_status['current_margin']
            })
    
    print(f"Total flat-rate clients: {impact['total_clients']}")
    
    for package, count in impact['by_package'].items():
        print(f"  - {package}: {count} clients")
    
    if impact['high_volume_clients']:
        print(f"\n⚠️  High volume clients ({len(impact['high_volume_clients'])}):")
        for client in impact['high_volume_clients'][:5]:  # Show first 5
            print(f"  - {client['company_name']}: ${client['current_volume']:,.0f}/month")
    
    if impact['margin_violations']:
        print(f"\n🔴 Clients with margin violations ({len(impact['margin_violations'])}):")
        for client in impact['margin_violations'][:5]:  # Show first 5
            print(f"  - {client['company_name']}: {client['current_margin']:.2f}% margin")
    
    return impact


def generate_migration_report():
    """Generate comprehensive migration report"""
    print("\n📋 MIGRATION SUMMARY REPORT")
    print("=" * 50)
    
    # Get pricing summary
    pricing_summary = get_revised_pricing_summary()
    
    print("New Pricing Structure:")
    for package_slug, details in pricing_summary.items():
        margin_info = details['margin_validation']
        print(f"\n📦 {details['name']}")
        print(f"   Price: {details['pricing_display']}")
        print(f"   Margin: {details['margin_display']}")
        print(f"   Features: {details['features']} included")
        print(f"   Target: {details['target_market']}")
        print(f"   Status: {'✅ Valid' if margin_info['is_valid'] else '❌ Invalid'}")
    
    # Validate all packages
    validation_report = validate_all_packages()
    print(f"\nValidation Summary:")
    print(f"  - Valid packages: {validation_report['summary']['valid_packages']}")
    print(f"  - Invalid packages: {validation_report['summary']['invalid_packages']}")
    print(f"  - Unlimited packages: {validation_report['summary']['unlimited_packages']}")


def main():
    """Main migration script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate flat-rate package pricing structure')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without executing')
    parser.add_argument('--backup', action='store_true', help='Create backup before migration')
    parser.add_argument('--skip-validation', action='store_true', help='Skip pre-migration validation')
    
    args = parser.parse_args()
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        print("🚀 FLAT-RATE PRICING MIGRATION")
        print("=" * 50)
        print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE EXECUTION'}")
        print(f"Backup: {'Enabled' if args.backup else 'Disabled'}")
        
        # Create backup if requested
        if args.backup and not args.dry_run:
            if not create_backup_table():
                print("❌ Backup failed, aborting migration")
                return 1
        
        # Pre-migration validation
        if not args.skip_validation:
            current_analysis = validate_current_packages()
            client_impact = check_client_impact()
        
        # Execute migration
        result = update_packages(dry_run=args.dry_run)
        
        # Generate report
        generate_migration_report()
        
        # Summary
        print(f"\n🏁 MIGRATION {'PREVIEW' if args.dry_run else 'COMPLETED'}")
        print("=" * 50)
        print(f"Updated packages: {len(result['updated'])}")
        print(f"Created packages: {len(result['created'])}")
        print(f"Errors: {len(result['errors'])}")
        
        if result['errors']:
            print("\nErrors encountered:")
            for error in result['errors']:
                print(f"  - {error}")
            return 1
        
        if args.dry_run:
            print("\n💡 Run without --dry-run to execute the migration")
        else:
            print("\n✅ Migration completed successfully!")
            print("   - Review client impact and communicate changes")
            print("   - Monitor client usage for margin violations")
            print("   - Update pricing page and documentation")
        
        return 0


if __name__ == '__main__':
    exit(main())
