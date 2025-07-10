# Context processors for the application.
# These make certain variables and functions available to all templates.
from flask import current_app, g, has_request_context
from .models.coin import Coin

def inject_coin_utils():
    """Make coin-related utilities available in templates."""
    def get_coin_by_symbol(symbol):
        """Get coin metadata by symbol."""
        if not hasattr(g, '_coin_cache'):
            g._coin_cache = {}
            
        if not symbol:
            return None
            
        symbol = symbol.upper()
        if symbol not in g._coin_cache:
            g._coin_cache[symbol] = Coin.get_by_symbol(symbol)
            
        return g._coin_cache[symbol]
    
    # Only proceed if we have a request context and a logged-in user
    if not has_request_context() or not hasattr(g, 'user') or not hasattr(g.user, 'client'):
        return {}
    
    # Get allowed coins for the current client
    allowed_coins = []
    if hasattr(g.user, 'client') and hasattr(g.user.client, 'package'):
        allowed_coins = Coin.get_allowed_coins(g.user.client.package.slug)
    
    return {
        # Coin data
        'allowed_coins': allowed_coins,
        'get_coin_by_symbol': get_coin_by_symbol,
        
        # Coin display functions (from utils/coins.py)
        'get_coin_display_name': lambda s: current_app.config.get('COIN_DISPLAY_NAMES', {}).get(s.upper(), s.upper()),
        'get_coin_icon': lambda s: f"crypto-icon crypto-{s.lower()}",
        'is_coin_allowed': lambda s: any(c.symbol == s.upper() for c in allowed_coins) if allowed_coins else False,
    }
