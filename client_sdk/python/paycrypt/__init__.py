
"""
PayCrypt API SDK for Python
Official SDK for integrating with PayCrypt crypto payment gateway
"""

import hashlib
import hmac
import json
import time
from typing import Dict, Any, Optional
import requests


class PayCryptSDK:
    """
    PayCrypt API SDK for Python
    
    Example:
        >>> sdk = PayCryptSDK(api_key='your_key', api_secret='your_secret')
        >>> payment = sdk.create_payment({
        ...     'amount': 100.00,
        ...     'currency': 'USD',
        ...     'crypto_currency': 'BTC',
        ...     'order_id': 'ORDER_12345'
        ... })
    """
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = "https://api.paycrypt.online",
        sandbox: bool = False,
        timeout: int = 30
    ):
        """
        Initialize PayCrypt SDK
        
        Args:
            api_key: Your API key
            api_secret: Your API secret
            base_url: API base URL (optional)
            sandbox: Use sandbox environment
            timeout: Request timeout in seconds
        """
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
        """Generate HMAC signature for request authentication"""
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
        """Make authenticated API request"""
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
        """
        Create a new payment
        
        Args:
            payment_data: Payment details including amount, currency, etc.
            
        Returns:
            Payment object with payment_id, address, and other details
            
        Raises:
            PayCryptAPIError: If payment creation fails
        """
        required_fields = ['amount', 'currency', 'crypto_currency', 'order_id']
        for field in required_fields:
            if field not in payment_data:
                raise ValueError(f"Missing required field: {field}")
        
        return self._make_request('POST', '/payments', payment_data)
    
    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Get payment status
        
        Args:
            payment_id: Payment ID
            
        Returns:
            Payment status object
        """
        return self._make_request('GET', f'/payments/{payment_id}')
    
    def get_account(self) -> Dict[str, Any]:
        """Get account information"""
        return self._make_request('GET', '/account')
    
    def get_usage(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return self._make_request('GET', '/account/usage')
    
    def configure_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure webhook endpoint
        
        Args:
            webhook_data: Webhook configuration including URL and events
            
        Returns:
            Webhook configuration object
        """
        return self._make_request('POST', '/webhooks', webhook_data)
    
    @staticmethod
    def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
        """
        Verify webhook signature
        
        Args:
            payload: Webhook payload
            signature: Webhook signature
            secret: Webhook secret
            
        Returns:
            True if signature is valid
        """
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)


class PayCryptAPIError(Exception):
    """Exception raised for PayCrypt API errors"""
    pass


# Convenience functions
def create_sdk(api_key: str, api_secret: str, **kwargs) -> PayCryptSDK:
    """Create PayCrypt SDK instance"""
    return PayCryptSDK(api_key=api_key, api_secret=api_secret, **kwargs)
