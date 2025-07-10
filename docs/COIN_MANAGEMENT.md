# Coin Management System

This document outlines the coin management system implemented in the PayCrypt application.

## Overview

The coin management system provides a way to:

1. Define which cryptocurrencies are supported
2. Restrict coin access based on client packages
3. Manage coin metadata (decimals, confirmations, etc.)
4. Provide utilities for displaying and working with coins in templates

## Configuration

### Package Coin Limits

Coin limits are defined in `app/config/config.py`:

```python
# Coin Configuration
COIN_LIST = [
    'BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'XRP', 'SOL', 'DOGE', 'TRX',
    'ADA', 'LTC', 'AVAX', 'MATIC', 'SHIB', 'DOT',  # First 15 (Starter)
    'LINK', 'XLM', 'DAI', 'ARB', 'OP',             # Next 5 (Business)
    'TON', 'CRO', 'FTM', 'APE', 'BCH'              # All 25 (Enterprise)
]

PACKAGE_COIN_LIMITS = {
    'starter_flat_rate': 15,
    'business_flat_rate': 20,
    'enterprise_flat_rate': 25
}
```

## Database Schema

The system uses the following database tables:

### coin_metadata

- `id` (PK): Unique identifier
- `symbol` (str): Coin symbol (e.g., 'BTC')
- `name` (str): Display name (e.g., 'Bitcoin')
- `is_active` (bool): Whether the coin is active
- `decimals` (int): Number of decimal places
- `min_confirmations` (int): Required confirmations
- `created_at` (datetime): When the record was created
- `updated_at` (datetime): When the record was last updated

## Usage

### In Python Code

```python
from app.models.coin import Coin

# Get all active coins
active_coins = Coin.get_active_coins()

# Get coins allowed for a specific package
coins = Coin.get_allowed_coins('starter_flat_rate')

# Check if a coin is allowed for a client
if client.is_coin_allowed('BTC'):
    # Process BTC transaction
    pass
```

### In Templates

```html
{% from "utils/coin_utils.html" import coin_icon, coin_name, coin_selector %}

<!-- Display a coin icon -->
{{ coin_icon('BTC') }}

<!-- Display a coin name -->
{{ coin_name('BTC') }}

<!-- Render a coin selector dropdown -->
{{ coin_selector(selected_coin='BTC') }}

<!-- Check if a coin is allowed -->
{% if is_coin_allowed('BTC') %}
    <!-- BTC is allowed -->
{% endif %}
```

### CLI Commands

```bash
# List all coins
flask coin list

# Add a new coin
flask coin add BTC Bitcoin --decimals 8 --confirmations 6 --active

# Update a coin
flask coin update BTC --name "Bitcoin" --decimals 8

# Sync coins with config
flask coin sync
```

## API Endpoints

### Get Allowed Coins

```
GET /api/coins
```

**Response**
```json
{
    "success": true,
    "coins": [
        {
            "symbol": "BTC",
            "name": "Bitcoin",
            "decimals": 8,
            "min_confirmations": 6
        },
        ...
    ]
}
```

### Check Coin Access

```
GET /api/coins/check?coin=BTC
```

**Response**
```json
{
    "success": true,
    "allowed": true,
    "coin": {
        "symbol": "BTC",
        "name": "Bitcoin",
        "decimals": 8,
        "min_confirmations": 6
    }
}
```

## Security Considerations

- Coin access is enforced at both the API and template levels
- Always validate coin access on the server side, even if UI restrictions are in place
- Use the provided validators for API endpoints that accept coin parameters

## Testing

To test the coin management system:

1. Run the test suite:
   ```bash
   python -m pytest tests/test_coin_management.py
   ```

2. Test the CLI commands:
   ```bash
   flask coin list
   flask coin add TEST "Test Coin" --decimals 8 --confirmations 6
   flask coin update TEST --name "Updated Test Coin"
   ```

3. Verify the API endpoints:
   ```bash
   curl http://localhost:5000/api/coins
   curl "http://localhost:5000/api/coins/check?coin=BTC"
   ```
