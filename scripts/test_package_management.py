"""
Test script for package management functionality.
Run with: flask test-packages
"""
import click
from flask import current_app
from flask.cli import with_appcontext
from app.services.package_service import PackageService
from app.models.client_package import ClientPackage, ClientType
from app.models.feature import Feature

@current_app.cli.group()
def test():
    """Test commands."""
    pass

@test.command('packages')
@with_appcontext
def test_packages():
    """Test package management functionality."""
    click.echo("Testing package management...")
    
    # Test listing packages
    click.echo("\n=== Listing all packages ===")
    from app.extensions import db
    with db.session() as session:
        packages = session.query(ClientPackage).order_by(ClientPackage.sort_order).all()
        if not packages:
            click.echo("No packages found. Creating default packages...")
            PackageService.initialize_default_packages()
            packages = session.query(ClientPackage).order_by(ClientPackage.sort_order).all()
        
        for pkg in packages:
            click.echo(f"\n\033[1m{pkg.name} ({pkg.slug})\033[0m")
            click.echo(f"Type: {pkg.client_type.value}")
            click.echo(f"Status: {pkg.status.value}")
            
            if pkg.client_type == ClientType.FLAT_RATE:
                click.echo(f"Monthly Price: ${pkg.monthly_price}")
                click.echo(f"Annual Price: ${pkg.annual_price} (10% discount)")
            else:
                click.echo(f"Commission Rate: {float(pkg.commission_rate)*100}%")
                
            click.echo(f"Max Transactions/Month: {pkg.max_transactions_per_month or 'Unlimited'}")
            click.echo(f"Max API Calls/Month: {pkg.max_api_calls_per_month or 'Unlimited'}")
            
            # Get package features
            features = PackageService.get_package_features(pkg.id)
            click.echo(f"Features ({len(features)}):")
            for assignment, feature in features:
                limit_str = f" (limit: {assignment.limit_value})" if assignment.limit_value else ""
                click.echo(f"  - {feature.name} ({feature.feature_key}){limit_str}")
    
    click.echo("\n✓ Package management tests completed successfully!")

# Register the test command group
def register_commands(app):
    app.cli.add_command(test)
