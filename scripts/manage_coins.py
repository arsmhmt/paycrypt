"""
Utility script to manage coin configurations in the database.
"""
import sys
import click
from flask import current_app
from datetime import datetime

# Add the parent directory to the path to allow imports
sys.path.append('..')

def register_commands(app):
    """Register coin management commands with the Flask app."""
    
    @app.cli.group()
    def coin():
        """Coin management commands."""
        pass
    
    @coin.command('list')
    @click.option('--active-only', is_flag=True, help='Show only active coins')
    def list_coins(active_only):
        """List all coins in the system."""
        from app.models.coin import Coin
        
        query = Coin.query
        if active_only:
            query = query.filter_by(is_active=True)
            
        coins = query.order_by(Coin.symbol).all()
        
        if not coins:
            click.echo("No coins found in the database.")
            return
            
        click.echo(f"{'Symbol':<8} {'Name':<20} {'Status':<10} Decimals  Confirmations")
        click.echo("-" * 50)
        
        for coin in coins:
            status = 'Active' if coin.is_active else 'Inactive'
            click.echo(f"{coin.symbol:<8} {coin.name:<20} {status:<10} {coin.decimals:<9} {coin.min_confirmations}")
    
    @coin.command('add')
    @click.argument('symbol')
    @click.argument('name')
    @click.option('--decimals', type=int, default=8, help='Number of decimal places')
    @click.option('--confirmations', type=int, default=6, help='Minimum confirmations required')
    @click.option('--active/--inactive', default=True, help='Whether the coin is active')
    def add_coin(symbol, name, decimals, confirmations, active):
        """Add a new coin to the system."""
        from app.models.coin import Coin
        from app.extensions.extensions import db
        
        # Check if coin already exists
        existing = Coin.query.filter_by(symbol=symbol.upper()).first()
        if existing:
            click.echo(f"Error: A coin with symbol {symbol} already exists.")
            return 1
            
        # Create and save the new coin
        try:
            coin = Coin(
                symbol=symbol.upper(),
                name=name,
                decimals=decimals,
                min_confirmations=confirmations,
                is_active=active
            )
            db.session.add(coin)
            db.session.commit()
            click.echo(f"Successfully added {symbol.upper()} - {name}")
            return 0
        except Exception as e:
            db.session.rollback()
            click.echo(f"Error adding coin: {str(e)}", err=True)
            return 1
    
    @coin.command('update')
    @click.argument('symbol')
    @click.option('--name', help='Display name of the coin')
    @click.option('--decimals', type=int, help='Number of decimal places')
    @click.option('--confirmations', type=int, help='Minimum confirmations required')
    @click.option('--active/--inactive', help='Whether the coin is active')
    def update_coin(symbol, **kwargs):
        """Update an existing coin's properties."""
        from app.models.coin import Coin
        from app.extensions.extensions import db
        
        coin = Coin.query.filter_by(symbol=symbol.upper()).first()
        if not coin:
            click.echo(f"Error: No coin found with symbol {symbol}", err=True)
            return 1
            
        try:
            # Update only the provided fields
            for key, value in kwargs.items():
                if value is not None:
                    setattr(coin, key, value)
                    
            coin.updated_at = datetime.utcnow()
            db.session.commit()
            
            click.echo(f"Successfully updated {coin.symbol} - {coin.name}")
            return 0
            
        except Exception as e:
            db.session.rollback()
            click.echo(f"Error updating coin: {str(e)}", err=True)
            return 1
    
    @coin.command('sync')
    def sync_coins():
        """Sync coins from config to the database."""
        from app.models.coin import Coin
        from app.extensions.extensions import db
        
        # Get coins from config
        config_coins = {}
        for symbol in current_app.config['COIN_LIST']:
            config_coins[symbol] = {
                'name': current_app.config['COIN_DISPLAY_NAMES'].get(symbol, symbol),
                'is_active': True
            }
        
        # Get existing coins from database
        db_coins = {coin.symbol: coin for coin in Coin.query.all()}
        
        added = 0
        updated = 0
        
        # Add or update coins from config
        for symbol, coin_data in config_coins.items():
            if symbol in db_coins:
                # Update existing coin
                coin = db_coins[symbol]
                needs_update = False
                
                if coin.name != coin_data['name']:
                    coin.name = coin_data['name']
                    needs_update = True
                    
                if not coin.is_active:
                    coin.is_active = True
                    needs_update = True
                    
                if needs_update:
                    coin.updated_at = datetime.utcnow()
                    db.session.add(coin)
                    updated += 1
            else:
                # Add new coin
                coin = Coin(
                    symbol=symbol,
                    name=coin_data['name'],
                    is_active=True,
                    decimals=8,  # Default values
                    min_confirmations=6  # Default value
                )
                db.session.add(coin)
                added += 1
        
        # Deactivate coins not in config
        deactivated = 0
        for symbol, coin in db_coins.items():
            if symbol not in config_coins and coin.is_active:
                coin.is_active = False
                coin.updated_at = datetime.utcnow()
                db.session.add(coin)
                deactivated += 1
        
        try:
            db.session.commit()
            click.echo(f"Coin sync complete. Added: {added}, Updated: {updated}, Deactivated: {deactivated}")
            return 0
        except Exception as e:
            db.session.rollback()
            click.echo(f"Error syncing coins: {str(e)}", err=True)
            return 1
