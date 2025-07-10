"""
API validation utilities for PayCrypt.
Handles request validation, authentication, and permission checks.
"""
from functools import wraps
from flask import request, jsonify, current_app, g
from ..models import db, Client, Package
from ..utils.coins import is_coin_allowed

def validate_coin(coin_param='coin'):
    """
    Decorator to validate if a coin is allowed for the client's package.
    
    Args:
        coin_param (str): The name of the parameter containing the coin symbol
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user') or not hasattr(g.user, 'client'):
                return jsonify({
                    'success': False,
                    'error': 'Authentication required',
                    'code': 'authentication_required'
                }), 401
                
            coin_symbol = request.args.get(coin_param) or request.json.get(coin_param)
            if not coin_symbol:
                return jsonify({
                    'success': False,
                    'error': f'Missing required parameter: {coin_param}',
                    'code': 'missing_parameter'
                }), 400
                
            if not is_coin_allowed(g.user.client, coin_symbol):
                return jsonify({
                    'success': False,
                    'error': f'Coin {coin_symbol} is not available in your plan',
                    'code': 'coin_not_allowed'
                }), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_package_limits(feature_key):
    """
    Decorator to validate if the client's package has access to a specific feature.
    
    Args:
        feature_key (str): The feature key to check against the package
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user') or not hasattr(g.user, 'client'):
                return jsonify({
                    'success': False,
                    'error': 'Authentication required',
                    'code': 'authentication_required'
                }), 401
                
            client = g.user.client
            if not client.has_feature(feature_key):
                return jsonify({
                    'success': False,
                    'error': 'This feature is not available in your current plan',
                    'code': 'feature_not_available',
                    'required_plan': get_upgrade_package_name(client.package.slug, feature_key)
                }), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_upgrade_package_name(current_package_slug, feature_key):
    """
    Determine which package a client needs to upgrade to for a specific feature.
    
    Args:
        current_package_slug (str): The client's current package slug
        feature_key (str): The feature key to check
        
    Returns:
        str: The display name of the package that includes this feature
    """
    # This is a simplified version - you might want to implement more complex logic
    # based on your package hierarchy
    packages = {
        'starter_flat_rate': 1,
        'business_flat_rate': 2,
        'enterprise_flat_rate': 3
    }
    
    current_level = packages.get(current_package_slug, 0)
    
    # This is a simplified example - you should map features to minimum package levels
    # For now, we'll just suggest the next package up
    if current_level < 3:  # If not already at the highest level
        for slug, level in packages.items():
            if level > current_level:
                # Get the display name for the package
                package = Package.query.filter_by(slug=slug).first()
                if package:
                    return package.name
                return slug.replace('_', ' ').title()
    
    return None
