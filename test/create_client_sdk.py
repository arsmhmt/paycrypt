#!/usr/bin/env python3
"""
Client API SDK and Integration Tools
Prepares client onboarding materials including SDK, Postman collections, and documentation
"""

import json
import os
from datetime import datetime

def create_postman_collection():
    """Create Postman collection for PayCrypt API"""
    
    collection = {
        "info": {
            "name": "PayCrypt API",
            "description": "Complete API collection for PayCrypt crypto payment gateway integration",
            "version": "1.0.0",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "auth": {
            "type": "bearer",
            "bearer": [
                {
                    "key": "token",
                    "value": "{{api_token}}",
                    "type": "string"
                }
            ]
        },
        "variable": [
            {
                "key": "base_url",
                "value": "https://api.paycrypt.online",
                "type": "string"
            },
            {
                "key": "api_token",
                "value": "your_api_token_here",
                "type": "string"
            }
        ],
        "item": [
            {
                "name": "Authentication",
                "item": [
                    {
                        "name": "Get API Token",
                        "request": {
                            "method": "POST",
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "client_id": "{{client_id}}",
                                    "client_secret": "{{client_secret}}"
                                }, indent=2)
                            },
                            "url": {
                                "raw": "{{base_url}}/auth/token",
                                "host": ["{{base_url}}"],
                                "path": ["auth", "token"]
                            }
                        }
                    }
                ]
            },
            {
                "name": "Payments",
                "item": [
                    {
                        "name": "Create Payment",
                        "request": {
                            "method": "POST",
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json"
                                },
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{api_token}}"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "amount": 100.00,
                                    "currency": "USD",
                                    "crypto_currency": "BTC",
                                    "order_id": "ORDER_12345",
                                    "callback_url": "https://your-site.com/payment/callback",
                                    "return_url": "https://your-site.com/payment/success",
                                    "description": "Payment for order #12345"
                                }, indent=2)
                            },
                            "url": {
                                "raw": "{{base_url}}/payments",
                                "host": ["{{base_url}}"],
                                "path": ["payments"]
                            }
                        }
                    },
                    {
                        "name": "Get Payment Status",
                        "request": {
                            "method": "GET",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{api_token}}"
                                }
                            ],
                            "url": {
                                "raw": "{{base_url}}/payments/{{payment_id}}",
                                "host": ["{{base_url}}"],
                                "path": ["payments", "{{payment_id}}"]
                            }
                        }
                    }
                ]
            },
            {
                "name": "Webhooks",
                "item": [
                    {
                        "name": "Get Webhook Events",
                        "request": {
                            "method": "GET",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{api_token}}"
                                }
                            ],
                            "url": {
                                "raw": "{{base_url}}/webhooks/events",
                                "host": ["{{base_url}}"],
                                "path": ["webhooks", "events"]
                            }
                        }
                    },
                    {
                        "name": "Configure Webhook",
                        "request": {
                            "method": "POST",
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json"
                                },
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{api_token}}"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "url": "https://your-site.com/webhook/paycrypt",
                                    "events": ["payment.completed", "payment.failed", "payment.pending"],
                                    "secret": "your_webhook_secret"
                                }, indent=2)
                            },
                            "url": {
                                "raw": "{{base_url}}/webhooks",
                                "host": ["{{base_url}}"],
                                "path": ["webhooks"]
                            }
                        }
                    }
                ]
            },
            {
                "name": "Account Management",
                "item": [
                    {
                        "name": "Get Account Info",
                        "request": {
                            "method": "GET",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{api_token}}"
                                }
                            ],
                            "url": {
                                "raw": "{{base_url}}/account",
                                "host": ["{{base_url}}"],
                                "path": ["account"]
                            }
                        }
                    },
                    {
                        "name": "Get Usage Statistics",
                        "request": {
                            "method": "GET",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{api_token}}"
                                }
                            ],
                            "url": {
                                "raw": "{{base_url}}/account/usage",
                                "host": ["{{base_url}}"],
                                "path": ["account", "usage"]
                            }
                        }
                    }
                ]
            }
        ]
    }
    
    # Create SDK directory
    os.makedirs("client_sdk", exist_ok=True)
    
    # Write Postman collection
    with open("client_sdk/PayCrypt_API.postman_collection.json", "w") as f:
        json.dump(collection, f, indent=2)
    
    print("✅ Postman collection created: client_sdk/PayCrypt_API.postman_collection.json")
    return True

def create_javascript_sdk():
    """Create JavaScript/Node.js SDK"""
    
    package_json = {
        "name": "paycrypt-sdk",
        "version": "1.0.0",
        "description": "Official PayCrypt API SDK for JavaScript/Node.js",
        "main": "index.js",
        "scripts": {
            "test": "jest",
            "build": "webpack --mode=production",
            "docs": "jsdoc -d docs src/"
        },
        "keywords": ["paycrypt", "crypto", "payment", "gateway", "api", "sdk"],
        "author": "PayCrypt Team",
        "license": "MIT",
        "dependencies": {
            "axios": "^1.6.0",
            "crypto": "^1.0.1"
        },
        "devDependencies": {
            "jest": "^29.0.0",
            "webpack": "^5.0.0",
            "jsdoc": "^4.0.0"
        }
    }
    
    js_sdk_code = """
/**
 * PayCrypt API SDK for JavaScript/Node.js
 * Official SDK for integrating with PayCrypt crypto payment gateway
 */

const axios = require('axios');
const crypto = require('crypto');

class PayCryptSDK {
    /**
     * Initialize PayCrypt SDK
     * @param {Object} config - Configuration object
     * @param {string} config.apiKey - Your API key
     * @param {string} config.apiSecret - Your API secret
     * @param {string} [config.baseURL='https://api.paycrypt.online'] - API base URL
     * @param {boolean} [config.sandbox=false] - Use sandbox environment
     */
    constructor(config) {
        this.apiKey = config.apiKey;
        this.apiSecret = config.apiSecret;
        this.baseURL = config.sandbox 
            ? 'https://sandbox-api.paycrypt.online' 
            : (config.baseURL || 'https://api.paycrypt.online');
        
        this.client = axios.create({
            baseURL: this.baseURL,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': 'PayCrypt-SDK-JS/1.0.0'
            }
        });
        
        // Add request interceptor for authentication
        this.client.interceptors.request.use((config) => {
            const timestamp = Date.now();
            const signature = this.generateSignature(config.method, config.url, config.data, timestamp);
            
            config.headers['X-API-Key'] = this.apiKey;
            config.headers['X-Timestamp'] = timestamp;
            config.headers['X-Signature'] = signature;
            
            return config;
        });
    }
    
    /**
     * Generate HMAC signature for request authentication
     * @param {string} method - HTTP method
     * @param {string} url - Request URL
     * @param {Object} data - Request data
     * @param {number} timestamp - Request timestamp
     * @returns {string} HMAC signature
     */
    generateSignature(method, url, data, timestamp) {
        const payload = method.toUpperCase() + url + JSON.stringify(data || {}) + timestamp;
        return crypto.createHmac('sha256', this.apiSecret).update(payload).digest('hex');
    }
    
    /**
     * Create a new payment
     * @param {Object} paymentData - Payment details
     * @param {number} paymentData.amount - Payment amount in USD
     * @param {string} paymentData.currency - Fiat currency (e.g., 'USD')
     * @param {string} paymentData.cryptoCurrency - Crypto currency (e.g., 'BTC', 'ETH')
     * @param {string} paymentData.orderId - Unique order identifier
     * @param {string} [paymentData.callbackUrl] - Webhook callback URL
     * @param {string} [paymentData.returnUrl] - Success redirect URL
     * @param {string} [paymentData.description] - Payment description
     * @returns {Promise<Object>} Payment object
     */
    async createPayment(paymentData) {
        try {
            const response = await this.client.post('/payments', paymentData);
            return response.data;
        } catch (error) {
            throw new Error(`Payment creation failed: ${error.response?.data?.message || error.message}`);
        }
    }
    
    /**
     * Get payment status
     * @param {string} paymentId - Payment ID
     * @returns {Promise<Object>} Payment status object
     */
    async getPayment(paymentId) {
        try {
            const response = await this.client.get(`/payments/${paymentId}`);
            return response.data;
        } catch (error) {
            throw new Error(`Failed to get payment: ${error.response?.data?.message || error.message}`);
        }
    }
    
    /**
     * Get account information
     * @returns {Promise<Object>} Account information
     */
    async getAccount() {
        try {
            const response = await this.client.get('/account');
            return response.data;
        } catch (error) {
            throw new Error(`Failed to get account: ${error.response?.data?.message || error.message}`);
        }
    }
    
    /**
     * Get usage statistics
     * @returns {Promise<Object>} Usage statistics
     */
    async getUsage() {
        try {
            const response = await this.client.get('/account/usage');
            return response.data;
        } catch (error) {
            throw new Error(`Failed to get usage: ${error.response?.data?.message || error.message}`);
        }
    }
    
    /**
     * Verify webhook signature
     * @param {string} payload - Webhook payload
     * @param {string} signature - Webhook signature
     * @param {string} secret - Webhook secret
     * @returns {boolean} True if signature is valid
     */
    static verifyWebhookSignature(payload, signature, secret) {
        const expectedSignature = crypto.createHmac('sha256', secret).update(payload).digest('hex');
        return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSignature));
    }
}

module.exports = PayCryptSDK;
"""
    
    readme_content = """
# PayCrypt JavaScript SDK

Official JavaScript/Node.js SDK for PayCrypt crypto payment gateway.

## Installation

```bash
npm install paycrypt-sdk
```

## Quick Start

```javascript
const PayCryptSDK = require('paycrypt-sdk');

// Initialize SDK
const paycrypt = new PayCryptSDK({
    apiKey: 'your_api_key',
    apiSecret: 'your_api_secret',
    sandbox: true // Use sandbox for testing
});

// Create a payment
async function createPayment() {
    try {
        const payment = await paycrypt.createPayment({
            amount: 100.00,
            currency: 'USD',
            cryptoCurrency: 'BTC',
            orderId: 'ORDER_12345',
            callbackUrl: 'https://your-site.com/webhook',
            returnUrl: 'https://your-site.com/success',
            description: 'Payment for order #12345'
        });
        
        console.log('Payment created:', payment);
        return payment;
    } catch (error) {
        console.error('Payment failed:', error.message);
    }
}

// Check payment status
async function checkPayment(paymentId) {
    try {
        const payment = await paycrypt.getPayment(paymentId);
        console.log('Payment status:', payment.status);
        return payment;
    } catch (error) {
        console.error('Failed to get payment:', error.message);
    }
}
```

## Webhook Verification

```javascript
const express = require('express');
const PayCryptSDK = require('paycrypt-sdk');

const app = express();
app.use(express.raw({ type: 'application/json' }));

app.post('/webhook/paycrypt', (req, res) => {
    const signature = req.headers['x-signature'];
    const secret = 'your_webhook_secret';
    
    if (PayCryptSDK.verifyWebhookSignature(req.body, signature, secret)) {
        const event = JSON.parse(req.body);
        console.log('Webhook event:', event);
        
        // Process the event
        handleWebhookEvent(event);
        
        res.status(200).send('OK');
    } else {
        res.status(400).send('Invalid signature');
    }
});
```

## API Reference

### PayCryptSDK

#### Constructor
- `new PayCryptSDK(config)` - Initialize SDK with configuration

#### Methods
- `createPayment(paymentData)` - Create a new payment
- `getPayment(paymentId)` - Get payment status
- `getAccount()` - Get account information
- `getUsage()` - Get usage statistics

#### Static Methods
- `PayCryptSDK.verifyWebhookSignature(payload, signature, secret)` - Verify webhook signature

## Configuration

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| apiKey | string | Yes | Your API key |
| apiSecret | string | Yes | Your API secret |
| baseURL | string | No | Custom API base URL |
| sandbox | boolean | No | Use sandbox environment |

## Error Handling

All SDK methods throw errors that should be caught and handled appropriately:

```javascript
try {
    const payment = await paycrypt.createPayment(paymentData);
} catch (error) {
    console.error('Error:', error.message);
    // Handle error appropriately
}
```

## Support

- Documentation: https://docs.paycrypt.online
- Support: support@paycrypt.online
- GitHub: https://github.com/paycrypt/sdk-js
"""
    
    # Write SDK files
    with open("client_sdk/package.json", "w") as f:
        json.dump(package_json, f, indent=2)
    
    with open("client_sdk/index.js", "w") as f:
        f.write(js_sdk_code)
    
    with open("client_sdk/README.md", "w") as f:
        f.write(readme_content)
    
    print("✅ JavaScript SDK created in client_sdk/ directory")
    return True

def create_python_sdk():
    """Create Python SDK"""
    
    setup_py = """
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="paycrypt-sdk",
    version="1.0.0",
    author="PayCrypt Team",
    author_email="dev@paycrypt.online",
    description="Official PayCrypt API SDK for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paycrypt/sdk-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "cryptography>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
)
"""
    
    python_sdk_code = """
\"\"\"
PayCrypt API SDK for Python
Official SDK for integrating with PayCrypt crypto payment gateway
\"\"\"

import hashlib
import hmac
import json
import time
from typing import Dict, Any, Optional
import requests


class PayCryptSDK:
    \"\"\"
    PayCrypt API SDK for Python
    
    Example:
        >>> sdk = PayCryptSDK(api_key='your_key', api_secret='your_secret')
        >>> payment = sdk.create_payment({
        ...     'amount': 100.00,
        ...     'currency': 'USD',
        ...     'crypto_currency': 'BTC',
        ...     'order_id': 'ORDER_12345'
        ... })
    \"\"\"
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = "https://api.paycrypt.online",
        sandbox: bool = False,
        timeout: int = 30
    ):
        \"\"\"
        Initialize PayCrypt SDK
        
        Args:
            api_key: Your API key
            api_secret: Your API secret
            base_url: API base URL (optional)
            sandbox: Use sandbox environment
            timeout: Request timeout in seconds
        \"\"\"
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://sandbox-api.paycrypt.online" if sandbox else base_url
        self.timeout = timeout
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'PayCrypt-SDK-Python/1.0.0'
        })
    
    def _generate_signature(self, method: str, url: str, data: Optional[Dict] = None, timestamp: int = None) -> str:
        \"\"\"Generate HMAC signature for request authentication\"\"\"
        if timestamp is None:
            timestamp = int(time.time() * 1000)
        
        payload = method.upper() + url + json.dumps(data or {}, separators=(',', ':')) + str(timestamp)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        \"\"\"Make authenticated API request\"\"\"
        url = f"{self.base_url}{endpoint}"
        timestamp = int(time.time() * 1000)
        signature = self._generate_signature(method, endpoint, data, timestamp)
        
        headers = {
            'X-API-Key': self.api_key,
            'X-Timestamp': str(timestamp),
            'X-Signature': signature
        }
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise PayCryptAPIError(f"API request failed: {e}")
    
    def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Create a new payment
        
        Args:
            payment_data: Payment details including amount, currency, etc.
            
        Returns:
            Payment object with payment_id, address, and other details
            
        Raises:
            PayCryptAPIError: If payment creation fails
        \"\"\"
        required_fields = ['amount', 'currency', 'crypto_currency', 'order_id']
        for field in required_fields:
            if field not in payment_data:
                raise ValueError(f"Missing required field: {field}")
        
        return self._make_request('POST', '/payments', payment_data)
    
    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        \"\"\"
        Get payment status
        
        Args:
            payment_id: Payment ID
            
        Returns:
            Payment status object
        \"\"\"
        return self._make_request('GET', f'/payments/{payment_id}')
    
    def get_account(self) -> Dict[str, Any]:
        \"\"\"Get account information\"\"\"
        return self._make_request('GET', '/account')
    
    def get_usage(self) -> Dict[str, Any]:
        \"\"\"Get usage statistics\"\"\"
        return self._make_request('GET', '/account/usage')
    
    def configure_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Configure webhook endpoint
        
        Args:
            webhook_data: Webhook configuration including URL and events
            
        Returns:
            Webhook configuration object
        \"\"\"
        return self._make_request('POST', '/webhooks', webhook_data)
    
    @staticmethod
    def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
        \"\"\"
        Verify webhook signature
        
        Args:
            payload: Webhook payload
            signature: Webhook signature
            secret: Webhook secret
            
        Returns:
            True if signature is valid
        \"\"\"
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)


class PayCryptAPIError(Exception):
    \"\"\"Exception raised for PayCrypt API errors\"\"\"
    pass


# Convenience functions
def create_sdk(api_key: str, api_secret: str, **kwargs) -> PayCryptSDK:
    \"\"\"Create PayCrypt SDK instance\"\"\"
    return PayCryptSDK(api_key=api_key, api_secret=api_secret, **kwargs)
"""
    
    python_readme = """
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
"""
    
    # Create Python SDK structure
    os.makedirs("client_sdk/python/paycrypt", exist_ok=True)
    
    # Write Python SDK files
    with open("client_sdk/python/setup.py", "w") as f:
        f.write(setup_py)
    
    with open("client_sdk/python/paycrypt/__init__.py", "w") as f:
        f.write(python_sdk_code)
    
    with open("client_sdk/python/README.md", "w") as f:
        f.write(python_readme)
    
    print("✅ Python SDK created in client_sdk/python/ directory")
    return True

def create_integration_examples():
    """Create integration examples for popular platforms"""
    
    # WordPress plugin example
    wordpress_example = """
<?php
/**
 * PayCrypt WordPress Plugin Example
 * Basic integration example for WordPress/WooCommerce
 */

class PayCrypt_Integration {
    private $api_key;
    private $api_secret;
    private $base_url;
    
    public function __construct($api_key, $api_secret, $sandbox = false) {
        $this->api_key = $api_key;
        $this->api_secret = $api_secret;
        $this->base_url = $sandbox 
            ? 'https://sandbox-api.paycrypt.online' 
            : 'https://api.paycrypt.online';
    }
    
    private function generate_signature($method, $url, $data, $timestamp) {
        $payload = strtoupper($method) . $url . json_encode($data) . $timestamp;
        return hash_hmac('sha256', $payload, $this->api_secret);
    }
    
    public function create_payment($payment_data) {
        $timestamp = time() * 1000;
        $url = '/payments';
        $signature = $this->generate_signature('POST', $url, $payment_data, $timestamp);
        
        $headers = [
            'Content-Type: application/json',
            'X-API-Key: ' . $this->api_key,
            'X-Timestamp: ' . $timestamp,
            'X-Signature: ' . $signature
        ];
        
        $ch = curl_init($this->base_url . $url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payment_data));
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        
        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($http_code === 200) {
            return json_decode($response, true);
        } else {
            throw new Exception('Payment creation failed: ' . $response);
        }
    }
    
    public function verify_webhook($payload, $signature, $secret) {
        $expected_signature = hash_hmac('sha256', $payload, $secret);
        return hash_equals($signature, $expected_signature);
    }
}

// Usage example
$paycrypt = new PayCrypt_Integration('your_api_key', 'your_api_secret', true);

$payment = $paycrypt->create_payment([
    'amount' => 100.00,
    'currency' => 'USD',
    'crypto_currency' => 'BTC',
    'order_id' => 'WC_ORDER_123',
    'callback_url' => 'https://yoursite.com/wp-json/paycrypt/webhook',
    'return_url' => 'https://yoursite.com/order-received/'
]);
?>
"""
    
    # Shopify integration example
    shopify_example = """
/**
 * PayCrypt Shopify Integration Example
 * JavaScript integration for Shopify themes
 */

class PayCryptShopify {
    constructor(config) {
        this.apiKey = config.apiKey;
        this.baseURL = config.sandbox 
            ? 'https://sandbox-api.paycrypt.online' 
            : 'https://api.paycrypt.online';
    }
    
    async createPayment(orderData) {
        const paymentData = {
            amount: orderData.total_price / 100, // Shopify uses cents
            currency: orderData.currency,
            crypto_currency: 'BTC', // or allow customer to choose
            order_id: orderData.order_number,
            callback_url: `${window.location.origin}/apps/paycrypt/webhook`,
            return_url: `${window.location.origin}/orders/${orderData.token}`,
            description: `Shopify Order #${orderData.order_number}`
        };
        
        // In a real implementation, this would go through your backend
        // to securely sign the request
        const response = await fetch('/apps/paycrypt/create-payment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(paymentData)
        });
        
        return response.json();
    }
    
    showPaymentModal(payment) {
        const modal = document.createElement('div');
        modal.className = 'paycrypt-modal';
        modal.innerHTML = `
            <div class="paycrypt-modal-content">
                <h3>Complete Your Crypto Payment</h3>
                <p>Send exactly <strong>${payment.crypto_amount} ${payment.crypto_currency}</strong> to:</p>
                <div class="payment-address">
                    <code>${payment.address}</code>
                    <button onclick="navigator.clipboard.writeText('${payment.address}')">Copy</button>
                </div>
                <div class="qr-code">
                    <img src="${payment.qr_code}" alt="Payment QR Code" />
                </div>
                <p>Payment will be confirmed automatically when received.</p>
                <button onclick="this.closest('.paycrypt-modal').remove()">Close</button>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
}

// Initialize on checkout
document.addEventListener('DOMContentLoaded', function() {
    const paycrypt = new PayCryptShopify({
        apiKey: 'your_public_api_key',
        sandbox: true
    });
    
    // Add crypto payment option to checkout
    const paymentOptions = document.querySelector('.payment-methods');
    if (paymentOptions) {
        const cryptoOption = document.createElement('div');
        cryptoOption.innerHTML = `
            <label>
                <input type="radio" name="payment_method" value="paycrypt" />
                Pay with Cryptocurrency
            </label>
        `;
        paymentOptions.appendChild(cryptoOption);
    }
});
"""
    
    # Create examples directory
    os.makedirs("client_sdk/examples", exist_ok=True)
    
    # Write example files
    with open("client_sdk/examples/wordpress_integration.php", "w") as f:
        f.write(wordpress_example)
    
    with open("client_sdk/examples/shopify_integration.js", "w") as f:
        f.write(shopify_example)
    
    # Create integration guide
    integration_guide = """
# PayCrypt Integration Examples

This directory contains integration examples for popular e-commerce platforms and frameworks.

## Available Examples

### WordPress/WooCommerce (`wordpress_integration.php`)
- Basic PHP integration class
- WooCommerce payment gateway example
- Webhook verification

### Shopify (`shopify_integration.js`)
- JavaScript integration for Shopify themes
- Custom payment method implementation
- Payment modal UI

## General Integration Steps

1. **Get API Credentials**
   - Sign up at https://dashboard.paycrypt.online
   - Generate API key and secret
   - Configure webhook endpoints

2. **Install SDK**
   - Use official SDK for your language
   - Or implement direct API calls

3. **Create Payment Flow**
   - Collect order information
   - Create payment via API
   - Display payment address/QR code to customer

4. **Handle Webhooks**
   - Implement webhook endpoint
   - Verify webhook signatures
   - Update order status based on payment events

5. **Test Integration**
   - Use sandbox environment
   - Test various payment scenarios
   - Verify webhook delivery

## Support

- Documentation: https://docs.paycrypt.online
- SDK Examples: https://github.com/paycrypt/examples
- Support: support@paycrypt.online
"""
    
    with open("client_sdk/examples/README.md", "w") as f:
        f.write(integration_guide)
    
    print("✅ Integration examples created in client_sdk/examples/ directory")
    return True

def create_admin_cli_tools():
    """Create advanced admin CLI tools for package switching and overrides"""
    
    admin_cli_code = """#!/usr/bin/env python3
\"\"\"
Advanced Admin CLI Tools
Provides command-line tools for administrators to manage clients, packages, and overrides
\"\"\"

import click
from flask.cli import with_appcontext
from app.models.client import Client
from app.models.client_package import ClientPackage
from app.extensions.extensions import db
from datetime import datetime, timedelta
import json

@click.group()
def admin():
    \"\"\"Advanced administration commands\"\"\"
    pass

@admin.command()
@click.option('--client-id', type=int, required=True, help='Client ID')
@click.option('--package-id', type=int, required=True, help='New package ID')
@click.option('--effective-date', help='Effective date (YYYY-MM-DD), default: now')
@click.option('--reason', help='Reason for package change')
@click.option('--dry-run', is_flag=True, help='Show what would be changed without applying')
@with_appcontext
def switch_package(client_id, package_id, effective_date, reason, dry_run):
    \"\"\"Switch client to a different package\"\"\"
    
    client = Client.query.get(client_id)
    if not client:
        click.echo(f"❌ Client {client_id} not found")
        return
    
    new_package = ClientPackage.query.get(package_id)
    if not new_package:
        click.echo(f"❌ Package {package_id} not found")
        return
    
    old_package = client.package
    
    click.echo(f"📦 Package Switch Request:")
    click.echo(f"   Client: {client.name} ({client.email})")
    click.echo(f"   From: {old_package.name if old_package else 'No package'}")
    click.echo(f"   To: {new_package.name}")
    click.echo(f"   Effective: {effective_date or 'Immediately'}")
    click.echo(f"   Reason: {reason or 'Not specified'}")
    
    if dry_run:
        click.echo("\\n🔍 DRY RUN - No changes will be made")
        return
    
    # Confirm the change
    if not click.confirm('\\nProceed with package switch?'):
        click.echo("❌ Package switch cancelled")
        return
    
    try:
        # Update client package
        client.package_id = package_id
        
        # Reset monthly usage if switching to a different package type
        if old_package and old_package.client_type != new_package.client_type:
            client.current_month_volume = 0.0
            client.last_reset_date = datetime.utcnow()
            click.echo("🔄 Monthly usage reset due to package type change")
        
        # Log the change (you could create a PackageChangeLog model)
        change_log = {
            'client_id': client_id,
            'old_package_id': old_package.id if old_package else None,
            'new_package_id': package_id,
            'changed_at': datetime.utcnow().isoformat(),
            'reason': reason,
            'changed_by': 'admin_cli'
        }
        
        # Save the log (implement proper logging table if needed)
        click.echo(f"📝 Change logged: {json.dumps(change_log, indent=2)}")
        
        db.session.commit()
        click.echo("✅ Package switch completed successfully")
        
    except Exception as e:
        db.session.rollback()
        click.echo(f"❌ Error switching package: {e}")

@admin.command()
@click.option('--client-id', type=int, required=True, help='Client ID')
@click.option('--commission-override', type=float, help='Override commission rate (e.g., 2.5 for 2.5%)')
@click.option('--volume-override', type=float, help='Override monthly volume limit')
@click.option('--margin-override', type=float, help='Override minimum margin requirement')
@click.option('--expires', help='Override expiration date (YYYY-MM-DD)')
@click.option('--reason', help='Reason for override')
@click.option('--dry-run', is_flag=True, help='Show what would be changed without applying')
@with_appcontext
def create_override(client_id, commission_override, volume_override, margin_override, expires, reason, dry_run):
    \"\"\"Create temporary overrides for client pricing/limits\"\"\"
    
    client = Client.query.get(client_id)
    if not client:
        click.echo(f"❌ Client {client_id} not found")
        return
    
    overrides = {}
    if commission_override is not None:
        overrides['commission_rate'] = commission_override
    if volume_override is not None:
        overrides['monthly_volume_limit'] = volume_override
    if margin_override is not None:
        overrides['minimum_margin'] = margin_override
    
    if not overrides:
        click.echo("❌ No overrides specified")
        return
    
    click.echo(f"🔧 Client Override Request:")
    click.echo(f"   Client: {client.name} ({client.email})")
    click.echo(f"   Current Package: {client.package.name if client.package else 'None'}")
    
    for key, value in overrides.items():
        click.echo(f"   {key.replace('_', ' ').title()}: {value}")
    
    click.echo(f"   Expires: {expires or 'No expiration'}")
    click.echo(f"   Reason: {reason or 'Not specified'}")
    
    if dry_run:
        click.echo("\\n🔍 DRY RUN - No changes will be made")
        return
    
    if not click.confirm('\\nCreate these overrides?'):
        click.echo("❌ Override creation cancelled")
        return
    
    try:
        # Store overrides in client model (you might want to create a separate ClientOverrides table)
        override_data = {
            'overrides': overrides,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': expires,
            'reason': reason,
            'created_by': 'admin_cli'
        }
        
        # For now, store as JSON in a text field (implement proper table later)
        client.admin_overrides = json.dumps(override_data)
        
        db.session.commit()
        click.echo("✅ Overrides created successfully")
        
    except Exception as e:
        db.session.rollback()
        click.echo(f"❌ Error creating overrides: {e}")

@admin.command()
@click.option('--package-type', type=click.Choice(['COMMISSION', 'FLAT_RATE']), help='Filter by package type')
@click.option('--status', type=click.Choice(['active', 'inactive']), help='Filter by client status')
@click.option('--high-usage', is_flag=True, help='Show only clients with >80% usage')
@click.option('--format', type=click.Choice(['table', 'json', 'csv']), default='table', help='Output format')
@with_appcontext
def list_clients(package_type, status, high_usage, format):
    \"\"\"List clients with detailed information\"\"\"
    
    query = Client.query.join(ClientPackage, isouter=True)
    
    if package_type:
        query = query.filter(ClientPackage.client_type == package_type)
    
    if status == 'active':
        query = query.filter(Client.is_active == True)
    elif status == 'inactive':
        query = query.filter(Client.is_active == False)
    
    clients = query.all()
    
    # Filter high usage clients
    if high_usage:
        filtered_clients = []
        for client in clients:
            if client.package and client.package.max_volume_per_month:
                usage_pct = (float(client.current_month_volume or 0) / float(client.package.max_volume_per_month)) * 100
                if usage_pct > 80:
                    filtered_clients.append(client)
        clients = filtered_clients
    
    if format == 'json':
        client_data = []
        for client in clients:
            usage_pct = 0
            if client.package and client.package.max_volume_per_month:
                usage_pct = (float(client.current_month_volume or 0) / float(client.package.max_volume_per_month)) * 100
            
            client_data.append({
                'id': client.id,
                'name': client.name,
                'email': client.email,
                'company': client.company_name,
                'package': client.package.name if client.package else None,
                'package_type': client.package.client_type if client.package else None,
                'current_volume': float(client.current_month_volume or 0),
                'max_volume': float(client.package.max_volume_per_month) if client.package and client.package.max_volume_per_month else None,
                'usage_percentage': round(usage_pct, 2),
                'is_active': client.is_active
            })
        
        click.echo(json.dumps(client_data, indent=2))
        
    elif format == 'csv':
        click.echo("ID,Name,Email,Company,Package,Type,Current Volume,Max Volume,Usage %,Active")
        for client in clients:
            usage_pct = 0
            if client.package and client.package.max_volume_per_month:
                usage_pct = (float(client.current_month_volume or 0) / float(client.package.max_volume_per_month)) * 100
            
            click.echo(f"{client.id},{client.name},{client.email},{client.company_name or ''},"
                      f"{client.package.name if client.package else ''},"
                      f"{client.package.client_type if client.package else ''},"
                      f"{client.current_month_volume or 0},"
                      f"{client.package.max_volume_per_month if client.package and client.package.max_volume_per_month else ''},"
                      f"{usage_pct:.2f},{client.is_active}")
    
    else:  # table format
        click.echo("\\n📊 Client List:")
        click.echo("-" * 120)
        click.echo(f"{'ID':<4} {'Name':<20} {'Email':<25} {'Package':<15} {'Type':<12} {'Usage':<10} {'Status':<8}")
        click.echo("-" * 120)
        
        for client in clients:
            usage_pct = 0
            if client.package and client.package.max_volume_per_month:
                usage_pct = (float(client.current_month_volume or 0) / float(client.package.max_volume_per_month)) * 100
            
            status_icon = "✅" if client.is_active else "❌"
            usage_display = f"{usage_pct:.1f}%" if client.package else "N/A"
            
            click.echo(f"{client.id:<4} {client.name[:19]:<20} {client.email[:24]:<25} "
                      f"{(client.package.name[:14] if client.package else 'None'):<15} "
                      f"{(client.package.client_type[:11] if client.package else 'N/A'):<12} "
                      f"{usage_display:<10} {status_icon:<8}")
        
        click.echo(f"\\nTotal clients: {len(clients)}")

@admin.command()
@click.option('--days', type=int, default=30, help='Report period in days')
@click.option('--format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@with_appcontext
def usage_report(days, format):
    \"\"\"Generate usage report for all clients\"\"\"
    
    from sqlalchemy import func, and_
    from app.models.usage_alert import UsageAlert
    
    # Get clients with usage data
    clients = Client.query.filter(
        Client.is_active == True,
        Client.package_id.isnot(None)
    ).all()
    
    report_data = []
    total_volume = 0
    high_usage_count = 0
    
    for client in clients:
        if not client.package:
            continue
            
        current_volume = float(client.current_month_volume or 0)
        max_volume = float(client.package.max_volume_per_month or 0)
        usage_pct = (current_volume / max_volume * 100) if max_volume > 0 else 0
        
        # Count alerts in the period
        alert_count = UsageAlert.query.filter(
            UsageAlert.client_id == client.id,
            UsageAlert.sent_at >= datetime.utcnow() - timedelta(days=days)
        ).count()
        
        report_data.append({
            'client_id': client.id,
            'name': client.name,
            'email': client.email,
            'package': client.package.name,
            'current_volume': current_volume,
            'max_volume': max_volume,
            'usage_percentage': round(usage_pct, 2),
            'alert_count': alert_count,
            'projected_overage': max(0, current_volume - max_volume) if max_volume > 0 else 0
        })
        
        total_volume += current_volume
        if usage_pct > 80:
            high_usage_count += 1
    
    if format == 'json':
        click.echo(json.dumps({
            'report_period_days': days,
            'generated_at': datetime.utcnow().isoformat(),
            'summary': {
                'total_clients': len(report_data),
                'total_volume': total_volume,
                'high_usage_clients': high_usage_count
            },
            'clients': report_data
        }, indent=2))
    else:
        click.echo(f"\\n📈 Usage Report - Last {days} days")
        click.echo(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo("=" * 100)
        
        click.echo(f"📊 Summary:")
        click.echo(f"   Total Active Clients: {len(report_data)}")
        click.echo(f"   Total Volume: ${total_volume:,.2f}")
        click.echo(f"   High Usage (>80%): {high_usage_count}")
        click.echo()
        
        # Sort by usage percentage
        report_data.sort(key=lambda x: x['usage_percentage'], reverse=True)
        
        click.echo("📋 Client Usage Details:")
        click.echo("-" * 100)
        click.echo(f"{'Name':<20} {'Package':<15} {'Usage':<8} {'Volume':<12} {'Alerts':<7} {'Status'}")
        click.echo("-" * 100)
        
        for data in report_data[:20]:  # Top 20
            usage_status = "🔴" if data['usage_percentage'] > 95 else "🟡" if data['usage_percentage'] > 80 else "🟢"
            
            click.echo(f"{data['name'][:19]:<20} {data['package'][:14]:<15} "
                      f"{data['usage_percentage']:>6.1f}% "
                      f"${data['current_volume']:>10,.0f} "
                      f"{data['alert_count']:>6} {usage_status}")
        
        if len(report_data) > 20:
            click.echo(f"... and {len(report_data) - 20} more clients")

def register_admin_commands(app):
    \"\"\"Register admin CLI commands with Flask app\"\"\"
    app.cli.add_command(admin)

# Export for easy registration
__all__ = ['register_admin_commands']
"""
    
    with open("app/commands/admin_cli.py", "w") as f:
        f.write(admin_cli_code)
    
    print("✅ Advanced admin CLI tools created at app/commands/admin_cli.py")
    return True

def main():
    """Set up all client SDK and integration tools"""
    print("🚀 Setting up client SDK and integration tools...")
    print()
    
    success_count = 0
    
    # Setup components
    components = [
        ("Postman Collection", create_postman_collection),
        ("JavaScript SDK", create_javascript_sdk),
        ("Python SDK", create_python_sdk),
        ("Integration Examples", create_integration_examples),
        ("Admin CLI Tools", create_admin_cli_tools)
    ]
    
    for name, func in components:
        try:
            print(f"Creating {name}...")
            if func():
                success_count += 1
                print(f"✅ {name} created successfully")
            else:
                print(f"❌ {name} creation failed")
        except Exception as e:
            print(f"❌ Error creating {name}: {e}")
        print()
    
    # Summary
    print("=" * 60)
    print(f"📊 Setup Summary: {success_count}/{len(components)} components successful")
    print()
    
    if success_count == len(components):
        print("🎉 All client SDK and integration tools created successfully!")
        print()
        print("📁 Files created:")
        print("   client_sdk/PayCrypt_API.postman_collection.json")
        print("   client_sdk/index.js (JavaScript SDK)")
        print("   client_sdk/python/ (Python SDK)")
        print("   client_sdk/examples/ (Integration examples)")
        print("   app/commands/admin_cli.py (Admin CLI tools)")
        print()
        print("📋 Next steps:")
        print("1. Test the SDKs with sandbox environment")
        print("2. Publish to npm/PyPI for easy installation")
        print("3. Register admin CLI commands in your Flask app")
        print("4. Create documentation website")
        print("5. Set up client onboarding process")
    else:
        print("⚠️  Some components failed to create. Check the errors above.")

if __name__ == '__main__':
    main()
