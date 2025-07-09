"""
Wallet Service
Handles interactions with different wallet providers (Binance, Coinbase, etc.)
"""

import logging
import requests
import hashlib
import hmac
import time
import base64
from datetime import datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)


class WalletService:
    """Service to interact with various wallet providers"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PayCrypt-Gateway/1.0'
        })
    
    def test_provider_connection(self, provider) -> Dict[str, Any]:
        """Test connection to a wallet provider"""
        try:
            if provider.provider_type == 'binance':
                return self._test_binance_connection(provider)
            elif provider.provider_type == 'coinbase':
                return self._test_coinbase_connection(provider)
            elif provider.provider_type == 'kraken':
                return self._test_kraken_connection(provider)
            elif provider.provider_type == 'manual_wallet':
                return self._test_manual_wallet(provider)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported provider type: {provider.provider_type}'
                }
        
        except Exception as e:
            logger.error(f"Error testing provider connection: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def sync_provider_balances(self, provider) -> Dict[str, Any]:
        """Sync balances from a wallet provider"""
        try:
            from app.models.wallet_provider import WalletBalance
            
            if provider.provider_type == 'binance':
                balances = self._get_binance_balances(provider)
            elif provider.provider_type == 'coinbase':
                balances = self._get_coinbase_balances(provider)
            elif provider.provider_type == 'kraken':
                balances = self._get_kraken_balances(provider)
            elif provider.provider_type == 'manual_wallet':
                balances = self._get_manual_wallet_balances(provider)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported provider type: {provider.provider_type}'
                }
            
            if not balances.get('success'):
                return balances
            
            # Update database balances
            from app.extensions import db
            
            for currency_code, balance_data in balances['balances'].items():
                # Get or create balance record
                wallet_balance = WalletBalance.query.filter_by(
                    provider_id=provider.id,
                    currency_code=currency_code
                ).first()
                
                if not wallet_balance:
                    wallet_balance = WalletBalance(
                        provider_id=provider.id,
                        currency_code=currency_code
                    )
                    db.session.add(wallet_balance)
                
                # Update balance
                wallet_balance.available_balance = Decimal(str(balance_data.get('available', 0)))
                wallet_balance.locked_balance = Decimal(str(balance_data.get('locked', 0)))
                wallet_balance.total_balance = Decimal(str(balance_data.get('total', 0)))
                wallet_balance.last_updated = datetime.utcnow()
                wallet_balance.update_source = 'api'
            
            db.session.commit()
            
            return {
                'success': True,
                'balances': balances['balances']
            }
        
        except Exception as e:
            logger.error(f"Error syncing provider balances: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _test_binance_connection(self, provider) -> Dict[str, Any]:
        """Test Binance API connection"""
        try:
            if not provider.api_key or not provider.api_secret:
                return {
                    'success': False,
                    'error': 'API key and secret are required for Binance'
                }
            
            base_url = 'https://testnet.binance.vision' if provider.sandbox_mode else 'https://api.binance.com'
            endpoint = '/api/v3/account'
            
            timestamp = int(time.time() * 1000)
            query_string = f'timestamp={timestamp}'
            
            # Create signature
            signature = hmac.new(
                provider.api_secret.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            headers = {
                'X-MBX-APIKEY': provider.api_key
            }
            
            url = f"{base_url}{endpoint}?{query_string}&signature={signature}"
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'data': {
                        'account_type': data.get('accountType'),
                        'can_trade': data.get('canTrade'),
                        'can_withdraw': data.get('canWithdraw'),
                        'can_deposit': data.get('canDeposit')
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'Binance API error: {response.status_code} - {response.text}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Binance connection test failed: {str(e)}'
            }
    
    def _test_coinbase_connection(self, provider) -> Dict[str, Any]:
        """Test Coinbase API connection"""
        try:
            if not provider.api_key or not provider.api_secret or not provider.api_passphrase:
                return {
                    'success': False,
                    'error': 'API key, secret, and passphrase are required for Coinbase'
                }
            
            base_url = 'https://api-public.sandbox.pro.coinbase.com' if provider.sandbox_mode else 'https://api.pro.coinbase.com'
            endpoint = '/accounts'
            
            timestamp = str(time.time())
            message = timestamp + 'GET' + endpoint
            
            signature = base64.b64encode(
                hmac.new(
                    base64.b64decode(provider.api_secret),
                    message.encode('utf-8'),
                    hashlib.sha256
                ).digest()
            ).decode()
            
            headers = {
                'CB-ACCESS-KEY': provider.api_key,
                'CB-ACCESS-SIGN': signature,
                'CB-ACCESS-TIMESTAMP': timestamp,
                'CB-ACCESS-PASSPHRASE': provider.api_passphrase,
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                accounts = response.json()
                return {
                    'success': True,
                    'data': {
                        'accounts_count': len(accounts),
                        'currencies': [acc['currency'] for acc in accounts[:5]]  # First 5 currencies
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'Coinbase API error: {response.status_code} - {response.text}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Coinbase connection test failed: {str(e)}'
            }
    
    def _test_kraken_connection(self, provider) -> Dict[str, Any]:
        """Test Kraken API connection"""
        try:
            if not provider.api_key or not provider.api_secret:
                return {
                    'success': False,
                    'error': 'API key and secret are required for Kraken'
                }
            
            # Test with public endpoint first
            base_url = 'https://api.kraken.com'
            endpoint = '/0/private/Balance'
            
            nonce = str(int(time.time() * 1000))
            data = {'nonce': nonce}
            
            postdata = '&'.join([f"{key}={value}" for key, value in data.items()])
            encoded = (nonce + postdata).encode()
            message = endpoint.encode() + hashlib.sha256(encoded).digest()
            
            signature = hmac.new(
                base64.b64decode(provider.api_secret),
                message,
                hashlib.sha512
            )
            
            headers = {
                'API-Key': provider.api_key,
                'API-Sign': base64.b64encode(signature.digest()).decode()
            }
            
            response = self.session.post(
                f"{base_url}{endpoint}",
                data=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('error'):
                    return {
                        'success': False,
                        'error': f"Kraken API error: {', '.join(result['error'])}"
                    }
                else:
                    return {
                        'success': True,
                        'data': {
                            'balances_count': len(result.get('result', {}))
                        }
                    }
            else:
                return {
                    'success': False,
                    'error': f'Kraken API error: {response.status_code} - {response.text}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Kraken connection test failed: {str(e)}'
            }
    
    def _test_manual_wallet(self, provider) -> Dict[str, Any]:
        """Test manual wallet configuration"""
        try:
            addresses = provider.wallet_addresses_dict
            
            if not addresses:
                return {
                    'success': False,
                    'error': 'No wallet addresses configured'
                }
            
            # Validate address formats (basic validation)
            valid_addresses = {}
            for currency, address in addresses.items():
                if self._validate_address_format(currency, address):
                    valid_addresses[currency] = address
            
            if not valid_addresses:
                return {
                    'success': False,
                    'error': 'No valid wallet addresses found'
                }
            
            return {
                'success': True,
                'data': {
                    'configured_currencies': list(valid_addresses.keys()),
                    'addresses_count': len(valid_addresses)
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Manual wallet test failed: {str(e)}'
            }
    
    def _validate_address_format(self, currency: str, address: str) -> bool:
        """Basic address format validation"""
        if not address or len(address) < 10:
            return False
        
        # Basic validation rules (extend as needed)
        if currency == 'BTC':
            return address.startswith(('1', '3', 'bc1')) and len(address) >= 26
        elif currency == 'ETH':
            return address.startswith('0x') and len(address) == 42
        elif currency == 'USDT':
            # USDT can be on multiple chains, basic validation
            return (address.startswith('0x') and len(address) == 42) or \
                   (address.startswith(('1', '3', 'bc1')) and len(address) >= 26)
        elif currency == 'XRP':
            return len(address) >= 25 and len(address) <= 34
        else:
            return True  # Allow other currencies with basic length check
    
    def _get_binance_balances(self, provider) -> Dict[str, Any]:
        """Get balances from Binance"""
        try:
            base_url = 'https://testnet.binance.vision' if provider.sandbox_mode else 'https://api.binance.com'
            endpoint = '/api/v3/account'
            
            timestamp = int(time.time() * 1000)
            query_string = f'timestamp={timestamp}'
            
            signature = hmac.new(
                provider.api_secret.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            headers = {
                'X-MBX-APIKEY': provider.api_key
            }
            
            url = f"{base_url}{endpoint}?{query_string}&signature={signature}"
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                balances = {}
                
                for balance in data.get('balances', []):
                    asset = balance['asset']
                    free = float(balance['free'])
                    locked = float(balance['locked'])
                    
                    if free > 0 or locked > 0:  # Only include non-zero balances
                        balances[asset] = {
                            'available': free,
                            'locked': locked,
                            'total': free + locked
                        }
                
                return {
                    'success': True,
                    'balances': balances
                }
            else:
                return {
                    'success': False,
                    'error': f'Binance API error: {response.status_code} - {response.text}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get Binance balances: {str(e)}'
            }
    
    def _get_coinbase_balances(self, provider) -> Dict[str, Any]:
        """Get balances from Coinbase"""
        try:
            base_url = 'https://api-public.sandbox.pro.coinbase.com' if provider.sandbox_mode else 'https://api.pro.coinbase.com'
            endpoint = '/accounts'
            
            timestamp = str(time.time())
            message = timestamp + 'GET' + endpoint
            
            signature = base64.b64encode(
                hmac.new(
                    base64.b64decode(provider.api_secret),
                    message.encode('utf-8'),
                    hashlib.sha256
                ).digest()
            ).decode()
            
            headers = {
                'CB-ACCESS-KEY': provider.api_key,
                'CB-ACCESS-SIGN': signature,
                'CB-ACCESS-TIMESTAMP': timestamp,
                'CB-ACCESS-PASSPHRASE': provider.api_passphrase,
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                accounts = response.json()
                balances = {}
                
                for account in accounts:
                    currency = account['currency']
                    available = float(account['available'])
                    hold = float(account['hold'])
                    balance_total = float(account['balance'])
                    
                    if balance_total > 0:  # Only include non-zero balances
                        balances[currency] = {
                            'available': available,
                            'locked': hold,
                            'total': balance_total
                        }
                
                return {
                    'success': True,
                    'balances': balances
                }
            else:
                return {
                    'success': False,
                    'error': f'Coinbase API error: {response.status_code} - {response.text}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get Coinbase balances: {str(e)}'
            }
    
    def _get_kraken_balances(self, provider) -> Dict[str, Any]:
        """Get balances from Kraken"""
        try:
            base_url = 'https://api.kraken.com'
            endpoint = '/0/private/Balance'
            
            nonce = str(int(time.time() * 1000))
            data = {'nonce': nonce}
            
            postdata = '&'.join([f"{key}={value}" for key, value in data.items()])
            encoded = (nonce + postdata).encode()
            message = endpoint.encode() + hashlib.sha256(encoded).digest()
            
            signature = hmac.new(
                base64.b64decode(provider.api_secret),
                message,
                hashlib.sha512
            )
            
            headers = {
                'API-Key': provider.api_key,
                'API-Sign': base64.b64encode(signature.digest()).decode()
            }
            
            response = self.session.post(
                f"{base_url}{endpoint}",
                data=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('error'):
                    return {
                        'success': False,
                        'error': f"Kraken API error: {', '.join(result['error'])}"
                    }
                
                balances = {}
                for currency, balance in result.get('result', {}).items():
                    balance_float = float(balance)
                    if balance_float > 0:  # Only include non-zero balances
                        # Kraken uses different currency codes (e.g., XXBT for BTC)
                        normalized_currency = self._normalize_kraken_currency(currency)
                        balances[normalized_currency] = {
                            'available': balance_float,
                            'locked': 0,  # Kraken doesn't separate locked funds in balance endpoint
                            'total': balance_float
                        }
                
                return {
                    'success': True,
                    'balances': balances
                }
            else:
                return {
                    'success': False,
                    'error': f'Kraken API error: {response.status_code} - {response.text}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get Kraken balances: {str(e)}'
            }
    
    def _get_manual_wallet_balances(self, provider) -> Dict[str, Any]:
        """Get balances for manual wallets (placeholder - would need blockchain APIs)"""
        # For manual wallets, we can't automatically get balances
        # This would require integrating with blockchain APIs (e.g., BlockCypher, Etherscan)
        # For now, return empty balances - admin would need to manually update
        return {
            'success': True,
            'balances': {},
            'message': 'Manual wallet balances must be updated manually'
        }
    
    def _normalize_kraken_currency(self, kraken_currency: str) -> str:
        """Normalize Kraken currency codes to standard format"""
        mapping = {
            'XXBT': 'BTC',
            'XETH': 'ETH',
            'XLTC': 'LTC',
            'XXRP': 'XRP',
            'USDT': 'USDT',
            'ZUSD': 'USD',
            'ZEUR': 'EUR'
        }
        return mapping.get(kraken_currency, kraken_currency)
    
    def get_primary_provider(self):
        """Get the primary wallet provider"""
        from app.models.wallet_provider import WalletProvider
        return WalletProvider.get_primary()
    
    def get_provider_for_currency(self, currency_code: str):
        """Get the best provider for a specific currency"""
        from app.models.wallet_provider import WalletProvider, WalletProviderCurrency
        
        # Get active providers that support this currency, ordered by priority
        provider = db.session.query(WalletProvider).join(WalletProviderCurrency).filter(
            WalletProvider.is_active == True,
            WalletProviderCurrency.currency_code == currency_code,
            WalletProviderCurrency.is_enabled == True
        ).order_by(WalletProvider.priority.asc()).first()
        
        return provider
