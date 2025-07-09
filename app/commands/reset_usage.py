"""
Monthly Usage Reset CLI Command
Resets client monthly usage counters (volume and transactions) for flat-rate clients.
Used for production cron jobs or manual admin operations.
"""

import click
from datetime import datetime, timedelta
from flask.cli import with_appcontext
from sqlalchemy import and_
from app.extensions import db
from app.models.client import Client
from app.models.client_package import ClientType


@click.command()
@click.option('--dry-run', is_flag=True, help='Show what would be reset without making changes')
@click.option('--client-id', type=int, help='Reset usage for specific client ID only')
@click.option('--force', is_flag=True, help='Force reset even if already reset this month')
@with_appcontext
def reset_monthly_usage(dry_run, client_id, force):
    """
    Reset monthly usage counters for flat-rate clients.
    
    This command should be run at the beginning of each month to reset:
    - current_month_volume 
    - current_month_transactions
    - last_usage_reset timestamp
    
    Usage examples:
    flask reset-monthly-usage                  # Reset all eligible clients
    flask reset-monthly-usage --dry-run        # Preview changes
    flask reset-monthly-usage --client-id 123  # Reset specific client
    flask reset-monthly-usage --force          # Force reset all clients
    """
    
    click.echo(f"🔄 Monthly Usage Reset - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    click.echo(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    
    # Build query for flat-rate clients
    query = db.session.query(Client).join(Client.package).filter(
        Client.package.has(client_type=ClientType.FLAT_RATE),
        Client.is_active == True
    )
    
    # Filter by specific client if requested
    if client_id:
        query = query.filter(Client.id == client_id)
        click.echo(f"🎯 Targeting specific client ID: {client_id}")
    
    # Filter by reset eligibility (unless forced)
    if not force:
        # Only reset clients who haven't been reset this month
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(
            db.or_(
                Client.last_usage_reset.is_(None),
                Client.last_usage_reset < current_month_start
            )
        )
        click.echo(f"📅 Only resetting clients not yet reset since {current_month_start.date()}")
    else:
        click.echo("⚠️  FORCE mode: resetting all clients regardless of last reset date")
    
    clients = query.all()
    
    if not clients:
        click.echo("✅ No clients found matching criteria")
        return
    
    click.echo(f"📊 Found {len(clients)} client(s) to process:")
    
    reset_count = 0
    total_volume_reset = 0
    total_transactions_reset = 0
    
    for client in clients:
        package_name = client.package.name if client.package else "No Package"
        current_volume = float(client.current_month_volume or 0)
        current_transactions = client.current_month_transactions or 0
        last_reset = client.last_usage_reset.strftime('%Y-%m-%d') if client.last_usage_reset else "Never"
        
        click.echo(f"\n👤 Client: {client.company_name} (ID: {client.id})")
        click.echo(f"   📦 Package: {package_name}")
        click.echo(f"   💰 Current Volume: ${current_volume:,.2f}")
        click.echo(f"   📈 Current Transactions: {current_transactions:,}")
        click.echo(f"   🕒 Last Reset: {last_reset}")
        
        if not dry_run:
            # Perform the reset
            old_volume = client.current_month_volume
            old_transactions = client.current_month_transactions
            
            client.reset_monthly_usage()
            
            click.echo(f"   ✅ Reset completed")
            reset_count += 1
            total_volume_reset += current_volume
            total_transactions_reset += current_transactions
        else:
            click.echo(f"   🔍 Would reset volume and transactions")
            total_volume_reset += current_volume
            total_transactions_reset += current_transactions
    
    # Summary
    click.echo(f"\n{'=' * 50}")
    click.echo(f"📋 SUMMARY")
    click.echo(f"{'=' * 50}")
    
    if dry_run:
        click.echo(f"📊 Would reset {len(clients)} client(s)")
        click.echo(f"💰 Total volume to reset: ${total_volume_reset:,.2f}")
        click.echo(f"📈 Total transactions to reset: {total_transactions_reset:,}")
        click.echo(f"\n💡 Run without --dry-run to execute the reset")
    else:
        click.echo(f"✅ Successfully reset {reset_count} client(s)")
        click.echo(f"💰 Total volume reset: ${total_volume_reset:,.2f}")
        click.echo(f"📈 Total transactions reset: {total_transactions_reset:,}")
        
        if reset_count != len(clients):
            click.echo(f"⚠️  Warning: {len(clients) - reset_count} client(s) had issues during reset")
    
    click.echo(f"\n🏁 Reset operation completed at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")


@click.command()
@click.option('--client-id', type=int, required=True, help='Client ID to check usage for')
@with_appcontext  
def check_client_usage(client_id):
    """
    Check current usage status for a specific client.
    
    Usage: flask check-client-usage --client-id 123
    """
    
    client = Client.query.get(client_id)
    if not client:
        click.echo(f"❌ Client with ID {client_id} not found")
        return
    
    if not client.package:
        click.echo(f"⚠️  Client {client.company_name} has no package assigned")
        return
    
    if client.package.client_type != ClientType.FLAT_RATE:
        click.echo(f"ℹ️  Client {client.company_name} is not on a flat-rate plan")
        return
    
    click.echo(f"📊 Usage Report for: {client.company_name}")
    click.echo(f"{'=' * 50}")
    click.echo(f"📦 Package: {client.package.name}")
    click.echo(f"💰 Monthly Price: ${float(client.package.monthly_price or 0):,.2f}")
    
    # Current usage
    click.echo(f"\n📈 CURRENT MONTH USAGE:")
    click.echo(f"   Volume: ${float(client.current_month_volume or 0):,.2f}")
    click.echo(f"   Transactions: {client.current_month_transactions or 0:,}")
    click.echo(f"   Last Reset: {client.last_usage_reset.strftime('%Y-%m-%d %H:%M') if client.last_usage_reset else 'Never'}")
    
    # Limits and utilization
    if client.package.max_volume_per_month:
        volume_percent = client.get_volume_utilization_percent()
        click.echo(f"\n📊 VOLUME LIMITS:")
        click.echo(f"   Limit: ${float(client.package.max_volume_per_month):,.2f}")
        click.echo(f"   Used: {volume_percent:.1f}%")
        click.echo(f"   Status: {'🔴 EXCEEDED' if client.is_exceeding_volume_limits() else '✅ Within Limits'}")
    
    if client.package.max_transactions_per_month:
        tx_percent = client.get_transaction_utilization_percent()
        click.echo(f"\n📊 TRANSACTION LIMITS:")
        click.echo(f"   Limit: {client.package.max_transactions_per_month:,}")
        click.echo(f"   Used: {tx_percent:.1f}%")
        click.echo(f"   Status: {'🔴 EXCEEDED' if client.is_exceeding_transaction_limits() else '✅ Within Limits'}")
    
    # Margin status
    margin_status = client.get_margin_status()
    if margin_status:
        click.echo(f"\n💹 MARGIN STATUS:")
        click.echo(f"   Current Margin: {margin_status['current_margin']:.2f}%")
        click.echo(f"   Minimum Required: {margin_status['min_margin']:.2f}%")
        click.echo(f"   Status: {'✅ Acceptable' if margin_status['is_acceptable'] else '🔴 Below Minimum'}")


# Register commands with Flask CLI
def init_app(app):
    """Register CLI commands with Flask app"""
    app.cli.add_command(reset_monthly_usage, 'reset-monthly-usage')
    app.cli.add_command(check_client_usage, 'check-client-usage')
