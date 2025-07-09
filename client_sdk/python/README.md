
# PayCrypt Python SDK

Official Python SDK for PayCrypt crypto payment gateway.

## Installation

```bash
pip install paycrypt-sdk
```

## Quick Start

```python
from paycrypt import PayCryptSDK

# Initialize SDK
sdk = PayCryptSDK(
    api_key='your_api_key',
    api_secret='your_api_secret',
    sandbox=True  # Use sandbox for testing
)

# Create a payment
payment = sdk.create_payment({
    'amount': 100.00,
    'currency': 'USD',
    'crypto_currency': 'BTC',
    'order_id': 'ORDER_12345',
    'callback_url': 'https://your-site.com/webhook',
    'return_url': 'https://your-site.com/success',
    'description': 'Payment for order #12345'
})

print(f"Payment ID: {payment['payment_id']}")
print(f"Payment Address: {payment['address']}")
print(f"Amount to Pay: {payment['crypto_amount']} {payment['crypto_currency']}")

# Check payment status
status = sdk.get_payment(payment['payment_id'])
print(f"Payment Status: {status['status']}")
```

## Webhook Verification

```python
from flask import Flask, request
from paycrypt import PayCryptSDK

app = Flask(__name__)

@app.route('/webhook/paycrypt', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-Signature')
    secret = 'your_webhook_secret'
    
    if PayCryptSDK.verify_webhook_signature(request.data.decode(), signature, secret):
        event = request.json
        print(f"Webhook event: {event}")
        
        # Process the event
        handle_payment_event(event)
        
        return 'OK', 200
    else:
        return 'Invalid signature', 400

def handle_payment_event(event):
    if event['type'] == 'payment.completed':
        print(f"Payment {event['payment_id']} completed!")
    elif event['type'] == 'payment.failed':
        print(f"Payment {event['payment_id']} failed!")
```

## API Reference

### PayCryptSDK

#### Constructor
```python
PayCryptSDK(api_key, api_secret, base_url=None, sandbox=False, timeout=30)
```

#### Methods
- `create_payment(payment_data)` - Create a new payment
- `get_payment(payment_id)` - Get payment status
- `get_account()` - Get account information
- `get_usage()` - Get usage statistics
- `configure_webhook(webhook_data)` - Configure webhook endpoint

#### Static Methods
- `verify_webhook_signature(payload, signature, secret)` - Verify webhook signature

## Error Handling

```python
from paycrypt import PayCryptSDK, PayCryptAPIError

try:
    payment = sdk.create_payment(payment_data)
except PayCryptAPIError as e:
    print(f"API Error: {e}")
except ValueError as e:
    print(f"Invalid input: {e}")
```

## License

MIT License - see LICENSE file for details.
