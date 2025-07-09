
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
