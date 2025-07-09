
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
