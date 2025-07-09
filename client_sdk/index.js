
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
