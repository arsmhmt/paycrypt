"""
Script to create a new client with maximum features for Paycrypt integration
"""
import sys
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.client import Client
from app.models.client_package import ClientPackage, PackageFeature, ClientType
from app.models.feature import Feature
from app.models.api_key import ClientApiKey, ApiKeyScope
from app.models.payment import Payment, PaymentStatus
from app.models.platform import Platform, PlatformType
from app.models.client_package import ClientType, PackageStatus
import secrets
import string

def generate_api_key():
    """Generate a secure API key"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(64))

def create_paycrypt_client():
    """Create Paycrypt client with maximum features"""
    app = create_app()
    with app.app_context():
        # Check if Paycrypt client already exists
        client = Client.query.filter_by(company_name='Paycrypt').first()
        if client:
            print(f"Updating existing Paycrypt client (ID: {client.id})")
            # Update existing client
            client.email = 'admin@paycrypt.example.com'
            client.username = 'paycrypt_admin'
            client.contact_person = 'Paycrypt Admin'
            client.contact_email = 'admin@paycrypt.example.com'
            client.contact_phone = '+10000000000'
            client.is_active = True
            client.is_verified = True
            client.verified_at = datetime.utcnow()
        else:
            print("Creating new Paycrypt client")
            # Create new client
            client = Client(
                company_name='Paycrypt',
                email='admin@paycrypt.example.com',
                username='paycrypt_admin',
                contact_person='Paycrypt Admin',
                contact_email='admin@paycrypt.example.com',
                contact_phone='+10000000000',
                is_active=True,
                is_verified=True,
                verified_at=datetime.utcnow()
            )
            db.session.add(client)
        
        # Create the Paycrypt platform if it doesn't exist
        platform = Platform.query.filter_by(name='Paycrypt').first()
        if not platform:
            platform = Platform(
                name='Paycrypt',
                platform_type=PlatformType.SAAS,
                api_key=secrets.token_hex(32),
                api_secret=secrets.token_hex(32),
                webhook_url='https://api.paycrypt.example.com/webhook',
                callback_url='https://app.paycrypt.example.com/callback',
                logo_url='https://paycrypt.example.com/logo.png'
            )
            db.session.add(platform)
            db.session.commit()
        
        # Generate a secure password for the admin user if not exists
        admin_password = secrets.token_urlsafe(16)  # Generate a random password
        client.password_hash = generate_password_hash(admin_password)
        
        # Set or update client settings
        client.settings = {
            'theme': 'dark',
            'notifications': {
                'email': True,
                'sms': True,
                'push': True
            },
            'security': {
                '2fa_enabled': True,
                'ip_whitelist': [],
                'session_timeout': 1440  # 24 hours
            },
            'billing': {
                'billing_currency': 'USD',
                'auto_renew': True
            }
        }
        db.session.add(client)
        db.session.commit()
        
        # Create default flat rate packages if they don't exist
        from app.models.client_package import create_default_flat_rate_packages, ClientPackage, ClientType
        
        # Create/update packages and get the result
        result = create_default_flat_rate_packages()
        if not result['success']:
            print("Error creating packages:", result.get('error', 'Unknown error'))
            return None
            
        # Get the most expensive flat-rate package
        enterprise_package = ClientPackage.query.filter_by(
            client_type=ClientType.FLAT_RATE
        ).order_by(ClientPackage.monthly_price.desc()).first()
        
        if not enterprise_package:
            print("Error: No flat-rate packages found")
            return None
        
        # Assign the enterprise package to the client
        client.package_id = enterprise_package.id
        
        # Create an API key for Paycrypt with all flat-rate permissions
        from app.models.api_key import ApiKeyScope
        
        # Get all flat-rate permissions
        flat_rate_permissions = [
            ApiKeyScope.FLAT_RATE_PAYMENT_CREATE.value,
            ApiKeyScope.FLAT_RATE_PAYMENT_READ.value,
            ApiKeyScope.FLAT_RATE_PAYMENT_UPDATE.value,
            ApiKeyScope.FLAT_RATE_WITHDRAWAL_CREATE.value,
            ApiKeyScope.FLAT_RATE_WITHDRAWAL_READ.value,
            ApiKeyScope.FLAT_RATE_WITHDRAWAL_APPROVE.value,
            ApiKeyScope.FLAT_RATE_BALANCE_READ.value,
            ApiKeyScope.FLAT_RATE_BALANCE_UPDATE.value,
            ApiKeyScope.FLAT_RATE_WALLET_MANAGE.value,
            ApiKeyScope.FLAT_RATE_WEBHOOK_MANAGE.value,
            ApiKeyScope.FLAT_RATE_USER_MANAGE.value,
            ApiKeyScope.FLAT_RATE_INVOICE_CREATE.value,
            ApiKeyScope.FLAT_RATE_INVOICE_READ.value,
            ApiKeyScope.FLAT_RATE_PROFILE_READ.value,
            ApiKeyScope.FLAT_RATE_PROFILE_UPDATE.value
        ]
        
        # Create the API key using the class method
        client_api_key, api_key = ClientApiKey.create_key(
            client_id=client.id,
            name='Paycrypt Master Key',
            permissions=flat_rate_permissions,
            rate_limit=1000,  # High rate limit for master key
            expires_days=3650  # 10 years
        )
        
        # Create an initial payment record
        payment = Payment(
            client_id=client.id,
            platform_id=platform.id,
            amount=10000.00,  # $10,000 initial deposit
            currency='USD',
            status=PaymentStatus.COMPLETED.value,
            payment_method='bank_transfer',
            description='Initial deposit for Paycrypt account',
            transaction_id=f'INIT-{secrets.token_hex(8).upper()}')
        db.session.add(payment)
        
        db.session.commit()
        
        print(f"\n=== Paycrypt Admin Credentials ===")
        print(f"Client ID: {client.id}")
        print(f"Username: paycrypt_admin")
        print(f"Password: {admin_password}  # Save this password securely!")
        print(f"\n=== API Keys ===")
        print(f"Client API Key: {api_key}")
        print(f"Platform API Key: {platform.api_key}")
        print("\nNote: Please change the password after first login.")
        
        return client

if __name__ == '__main__':
    create_paycrypt_client()
