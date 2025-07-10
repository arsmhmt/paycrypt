"""
Package Management Commands

This module provides CLI commands for managing packages and features.
"""
import click
from flask import current_app
from flask.cli import with_appcontext
from app.services.package_service import PackageService
from app.models.client_package import ClientPackage, ClientType, PackageStatus
from app.models.feature import Feature
from app.utils.logger import logger


@click.group()
def package():
    """Package management commands."""
    pass


@package.command('init')
@with_appcontext
def init_packages():
    """Initialize default packages and features."""
    click.echo("Initializing default packages and features...")
    if PackageService.initialize_default_packages():
        click.echo("✓ Successfully initialized packages and features")
    else:
        click.echo("✗ Failed to initialize packages and features")

@package.command('list')
@with_appcontext
def list_packages():
    """List all packages and their features."""
    from app.extensions import db
    
    with db.session() as session:
        packages = session.query(ClientPackage).order_by(ClientPackage.sort_order).all()
        
        if not packages:
            click.echo("No packages found.")
            return
            
        for pkg in packages:
            click.echo(f"\n\033[1m{pkg.name} ({pkg.slug})\033[0m")
            click.echo(f"Type: {pkg.client_type.value}")
            click.echo(f"Status: {pkg.status.value}")
            click.echo(f"Popular: {'Yes' if pkg.is_popular else 'No'}")
            
            if pkg.client_type == ClientType.FLAT_RATE:
                click.echo(f"Monthly Price: ${pkg.monthly_price}")
                click.echo(f"Annual Price: ${pkg.annual_price} (10% discount)")
            else:
                click.echo(f"Commission Rate: {float(pkg.commission_rate)*100}%")
                
            click.echo(f"Max Transactions/Month: {pkg.max_transactions_per_month or 'Unlimited'}")
            click.echo(f"Max API Calls/Month: {pkg.max_api_calls_per_month or 'Unlimited'}")
            
            click.echo("Features:")
            features = PackageService.get_package_features(pkg.id)
            if not features:
                click.echo("  No features assigned")
                continue
                
            for assignment, feature in features:
                limit_str = f" (limit: {assignment.limit_value})" if assignment.limit_value else ""
                click.echo(f"  - {feature.name} ({feature.feature_key}){limit_str}")

@package.command('create')
@click.argument('name')
@click.argument('client_type', type=click.Choice(['commission', 'flat_rate']))
@click.option('--description', default='', help='Package description')
@click.option('--monthly', type=float, help='Monthly price (for flat-rate packages)')
@click.option('--commission', type=float, help='Commission rate (for commission packages, e.g., 2.5 for 2.5%)')
@click.option('--max-tx', type=int, help='Maximum transactions per month')
@click.option('--max-api', type=int, default=1000, help='Maximum API calls per month')
@click.option('--popular', is_flag=True, help='Mark as a popular package')
@with_appcontext
def create_package(name, client_type, description, monthly, commission, max_tx, max_api, popular):
    """Create a new package."""
    from app.extensions import db
    
    client_type_enum = ClientType[client_type.upper()]
    
    # Validate package type specific parameters
    if client_type_enum == ClientType.FLAT_RATE and monthly is None:
        click.echo("✗ Monthly price is required for flat-rate packages")
        return
    elif client_type_enum == ClientType.COMMISSION and commission is None:
        click.echo("✗ Commission rate is required for commission-based packages")
        return
    
    try:
        with db.session() as session:
            package = PackageService.create_package(
                name=name,
                description=description,
                client_type=client_type_enum,
                monthly_price=monthly,
                commission_rate=commission/100 if commission else None,  # Convert percentage to decimal
                is_popular=popular,
                max_transactions_per_month=max_tx,
                max_api_calls_per_month=max_api
            )
            
            if package:
                session.add(package)
                session.commit()
                click.echo(f"✓ Created {client_type} package: {package.name} (ID: {package.id})")
            else:
                session.rollback()
                click.echo("✗ Failed to create package")
    except Exception as e:
        db.session.rollback()
        click.echo(f"✗ Error creating package: {str(e)}")

@package.command('add-feature')
@click.argument('package_id', type=int)
@click.argument('feature_key')
@click.option('--limit', type=int, help='Optional limit for the feature')
@with_appcontext
def add_feature(package_id, feature_key, limit):
    """Add a feature to a package."""
    from app.extensions import db
    
    try:
        with db.session() as session:
            package = session.get(ClientPackage, package_id)
            if not package:
                click.echo(f"✗ Package not found with ID: {package_id}")
                return
                
            assignment = PackageService.assign_feature_to_package(
                package_id=package_id,
                feature_key=feature_key,
                is_included=True,
                limit_value=limit
            )
            
            if assignment:
                session.add(assignment)
                session.commit()
                click.echo(f"✓ Added feature '{feature_key}' to package '{package.name}'")
                if limit is not None:
                    click.echo(f"   Set limit: {limit}")
            else:
                session.rollback()
                click.echo(f"✗ Failed to add feature to package")
                click.echo("Available features:")
                for feature in session.query(Feature).all():
                    click.echo(f"  - {feature.feature_key} ({feature.name})")
    except Exception as e:
        db.session.rollback()
        click.echo(f"✗ Error adding feature: {str(e)}")

# Add the package group to the CLI
package.add_command(init_packages)
package.add_command(list_packages)
package.add_command(create_package)
package.add_command(add_feature)
