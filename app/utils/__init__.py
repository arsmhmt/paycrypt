# This file makes the utils directory a Python package
from .crypto_utils import generate_address, generate_order_id, create_qr
from app.decorators import admin_required as _admin_required
from .crypto import validate_crypto_address
from .helpers import generate_api_key, generate_secure_token, is_valid_api_key

# Export admin_required as a function
admin_required = _admin_required

__all__ = [
    'validate_crypto_address',
    'generate_api_key',
    'generate_secure_token',
    'is_valid_api_key',
    'generate_order_id',
    'create_qr',
    'admin_required'
]
