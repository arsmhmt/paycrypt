
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
