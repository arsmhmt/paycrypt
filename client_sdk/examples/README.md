
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
