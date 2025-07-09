from flask import Blueprint, request, jsonify, current_app
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta
from functools import wraps
from app.utils.exchange import get_exchange_rate, convert_fiat_to_crypto
from app.utils.security import rate_limit, abuse_protection
from app.utils.audit import log_api_usage

bp = Blueprint('exchange', __name__, url_prefix='/api/exchange')

def validate_currency(f):
    """Decorator to validate currency parameters"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        fiat = request.args.get('fiat_currency', 'USD').upper()
        crypto = request.args.get('crypto_currency', 'BTC').upper()
        
        # Validate fiat currency (add more as needed)
        valid_fiats = {'USD', 'EUR', 'GBP', 'TRY'}
        if fiat not in valid_fiats:
            return jsonify({
                'success': False,
                'error': f'Unsupported fiat currency. Supported: {sorted(valid_fiats)}'
            }), 400
            
        # Validate crypto currency
        valid_cryptos = {'BTC', 'ETH'}  # Add more as needed
        if crypto not in valid_cryptos:
            return jsonify({
                'success': False,
                'error': f'Unsupported cryptocurrency. Supported: {sorted(valid_cryptos)}'
            }), 400
            
        return f(fiat, crypto, *args, **kwargs)
    return decorated_function

@bp.route('/rate', methods=['GET'])
@validate_currency
@rate_limit('exchange_rate', limit=60)
@abuse_protection('exchange_rate', threshold=200)
def get_rate(fiat_currency, crypto_currency):
    """
    Get the current exchange rate for a fiat to crypto pair
    
    Query Parameters:
        fiat_currency: The fiat currency code (e.g., USD, EUR, TRY)
        crypto_currency: The cryptocurrency code (e.g., BTC, ETH)
        
    Returns:
        JSON with rate, expiry, and other metadata
    """
    try:
        # Log API usage
        log_api_usage(
            user_id=None,
            endpoint='/api/exchange/rate',
            method='GET',
            request_data={
                'fiat_currency': fiat_currency,
                'crypto_currency': crypto_currency
            },
            ip_address=request.remote_addr
        )
        
        rate = get_exchange_rate(fiat_currency, crypto_currency)
        if not rate:
            return jsonify({
                'success': False,
                'error': 'Could not fetch exchange rate. Please try again later.'
            }), 503
            
        expiry = (datetime.utcnow() + timedelta(minutes=15)).isoformat()
        
        return jsonify({
            'success': True,
            'fiat_currency': fiat_currency,
            'crypto_currency': crypto_currency,
            'rate': str(rate),
            'rate_expiry': expiry,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in get_rate: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred while fetching the exchange rate.'
        }), 500

@bp.route('/convert', methods=['GET'])
@validate_currency
@rate_limit('exchange_convert', limit=30)
@abuse_protection('exchange_convert', threshold=100)
def convert(fiat_currency, crypto_currency):
    """
    Convert a fiat amount to crypto amount
    
    Query Parameters:
        fiat_currency: The fiat currency code (e.g., USD, EUR, TRY)
        crypto_currency: The cryptocurrency code (e.g., BTC, ETH)
        amount: The fiat amount to convert
        
    Returns:
        JSON with converted amount and rate information
    """
    try:
        amount_str = request.args.get('amount')
        if not amount_str:
            return jsonify({
                'success': False,
                'error': 'Amount parameter is required'
            }), 400
            
        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, InvalidOperation) as e:
            return jsonify({
                'success': False,
                'error': 'Invalid amount. Please provide a positive number.'
            }), 400
        
        # Log API usage
        log_api_usage(
            user_id=None,
            endpoint='/api/exchange/convert',
            method='GET',
            request_data={
                'fiat_currency': fiat_currency,
                'crypto_currency': crypto_currency,
                'amount': amount_str
            },
            ip_address=request.remote_addr
        )
            
        # Get the exchange rate
        rate = get_exchange_rate(fiat_currency, crypto_currency)
        if not rate:
            return jsonify({
                'success': False,
                'error': 'Could not fetch exchange rate. Please try again later.'
            }), 503
            
        # Calculate the crypto amount
        crypto_amount = amount / rate
        expiry = (datetime.utcnow() + timedelta(minutes=15)).isoformat()
        
        return jsonify({
            'success': True,
            'fiat_amount': str(amount),
            'fiat_currency': fiat_currency,
            'crypto_amount': str(crypto_amount.quantize(Decimal('0.00000001'))),
            'crypto_currency': crypto_currency,
            'exchange_rate': str(rate),
            'rate_expiry': expiry,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in convert: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred during conversion.'
        }), 500
