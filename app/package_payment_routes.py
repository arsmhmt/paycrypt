"""
Package activation payment routes
Handles the payment flow for package setup fees using Paycrypt's own payment system
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from decimal import Decimal
from datetime import datetime, timedelta
import secrets
import hashlib

from app import db
from app.models import Client, ClientPackage, PackageActivationPayment, FlatRateSubscriptionPayment, Payment, PaymentStatus, ClientType, SubscriptionBillingCycle
from app.decorators import client_required
from app.utils.exchange import get_exchange_rate, convert_fiat_to_crypto, format_crypto_amount, get_popular_cryptocurrencies
from app.utils.crypto_config import get_cryptocurrency_choices, get_cryptocurrency_info
from app.utils.security import rate_limit, abuse_protection
from app.utils.audit import log_api_usage, log_security_event
from app.utils.fraud_detection import FraudDetectionService

package_payment = Blueprint('package_payment', __name__, url_prefix='/package-payment')

@package_payment.route('/activate/<int:package_id>')
@login_required
@client_required
@rate_limit('package_activation', limit=10)
def initiate_activation(package_id):
    """
    Show payment options based on package type (commission vs flat-rate)
    """
    try:
        # Log API usage
        log_api_usage(
            user_id=current_user.id,
            endpoint=f'/package-payment/activate/{package_id}',
            method='GET',
            request_data=None,
            ip_address=request.remote_addr
        )
        
        # Get the package
        package = ClientPackage.query.get_or_404(package_id)
        
        # Check if client already has an active package
        if current_user.package_id and current_user.is_active:
            flash('You already have an active package.', 'info')
            return redirect(url_for('client.dashboard'))
        
        # Handle based on package type
        if package.client_type == ClientType.COMMISSION:
            return handle_commission_package_activation(package)
        elif package.client_type == ClientType.FLAT_RATE:
            return handle_flat_rate_package_activation(package)
        else:
            flash('Invalid package type.', 'error')
            return redirect(url_for('main.pricing'))
        
    except Exception as e:
        current_app.logger.error(f"Error initiating package activation: {e}")
        log_security_event(
            event_type='package_activation_error',
            user_id=current_user.id,
            details={'package_id': package_id, 'error': str(e)},
            ip_address=request.remote_addr
        )
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('main.pricing'))

def handle_commission_package_activation(package):
    """Handle commission-based package activation (one-time setup fee)"""
    # Check for existing pending payment
    existing_payment = PackageActivationPayment.query.filter_by(
        client_id=current_user.id,
        package_id=package.id,
        status=PaymentStatus.PENDING
    ).filter(PackageActivationPayment.expires_at > datetime.utcnow()).first()
    
    if existing_payment:
        return redirect(url_for('package_payment.payment_details', payment_id=existing_payment.id))
    
    # Get popular cryptocurrencies for selection
    popular_cryptos = get_popular_cryptocurrencies()
    crypto_options = []
    
    setup_fee = package.setup_fee or Decimal('1000.00')  # Default $1000 USD setup fee
    
    # Calculate amounts for popular cryptocurrencies
    for crypto_symbol in popular_cryptos:
        crypto_info = get_cryptocurrency_info(crypto_symbol)
        if crypto_info:
            crypto_amount, exchange_rate = convert_fiat_to_crypto(setup_fee, 'USD', crypto_symbol)
            if crypto_amount and exchange_rate:
                crypto_options.append({
                    'symbol': crypto_symbol,
                    'name': crypto_info['name'],
                    'amount': crypto_amount,
                    'formatted_amount': format_crypto_amount(crypto_amount, crypto_symbol),
                    'rate': exchange_rate,
                    'icon': crypto_info.get('icon', crypto_symbol.lower())
                })
    
    return render_template('package_payment/crypto_selection.html',
                         package=package,
                         setup_fee=setup_fee,
                         crypto_options=crypto_options,
                         payment_type='commission')

def handle_flat_rate_package_activation(package):
    """Handle flat-rate package activation (monthly/annual billing)"""
    # Check for existing pending payment
    existing_payment = FlatRateSubscriptionPayment.query.filter_by(
        client_id=current_user.id,
        package_id=package.id,
        status=PaymentStatus.PENDING
    ).filter(FlatRateSubscriptionPayment.expires_at > datetime.utcnow()).first()
    
    if existing_payment:
        return redirect(url_for('package_payment.flat_rate_payment_details', payment_id=existing_payment.id))
    
    return render_template('package_payment/billing_cycle_selection.html',
                         package=package,
                         payment_type='flat_rate')

@package_payment.route('/create-payment/<int:package_id>/<crypto_currency>')
@login_required
@client_required
@rate_limit('create_payment', limit=20)
@abuse_protection('create_payment', threshold=50)
def create_payment(package_id, crypto_currency):
    """
    Create payment with selected cryptocurrency
    """
    try:
        # Log API usage
        log_api_usage(
            user_id=current_user.id,
            endpoint=f'/package-payment/create-payment/{package_id}/{crypto_currency}',
            method='GET',
            request_data=None,
            ip_address=request.remote_addr
        )
        
        # Run fraud detection
        fraud_service = FraudDetectionService()
        risk_score = fraud_service.analyze_payment_creation(
            platform_id=None,
            amount=None,  # Will be filled based on package
            client_id=current_user.id,
            ip_address=request.remote_addr
        )
        
        if risk_score > 0.7:  # Medium-high risk threshold for package payments
            log_security_event(
                event_type='suspicious_package_payment_blocked',
                user_id=current_user.id,
                details={
                    'risk_score': risk_score,
                    'package_id': package_id,
                    'crypto_currency': crypto_currency
                },
                ip_address=request.remote_addr
            )
            flash('Payment blocked due to security concerns. Please contact support.', 'error')
            return redirect(url_for('package_payment.initiate_activation', package_id=package_id))
        
        # Validate cryptocurrency
        crypto_currency = crypto_currency.upper()
        crypto_info = get_cryptocurrency_info(crypto_currency)
        if not crypto_info:
            flash('Invalid cryptocurrency selected.', 'error')
            return redirect(url_for('package_payment.initiate_activation', package_id=package_id))
        
        # Get the package
        package = ClientPackage.query.get_or_404(package_id)
        
        # Check if client already has an active package
        if current_user.package_id and current_user.is_active:
            flash('You already have an active package.', 'info')
            return redirect(url_for('client.dashboard'))
        
        # Check for existing pending payment
        existing_payment = PackageActivationPayment.query.filter_by(
            client_id=current_user.id,
            package_id=package_id,
            status=PaymentStatus.PENDING
        ).filter(PackageActivationPayment.expires_at > datetime.utcnow()).first()
        
        if existing_payment:
            return redirect(url_for('package_payment.payment_details', payment_id=existing_payment.id))
        
        # Create new activation payment
        setup_fee = Decimal('1000.00')  # $1000 USD setup fee
        
        # Convert to selected cryptocurrency
        crypto_amount, exchange_rate = convert_fiat_to_crypto(setup_fee, 'USD', crypto_currency)
        if not crypto_amount or not exchange_rate:
            flash('Unable to get current exchange rate. Please try again later.', 'error')
            return redirect(url_for('package_payment.initiate_activation', package_id=package_id))
        
        # Generate unique payment address (simplified - in production, use proper wallet API)
        payment_address = generate_payment_address(crypto_currency)
        
        activation_payment = PackageActivationPayment(
            client_id=current_user.id,
            package_id=package_id,
            setup_fee_amount=setup_fee,
            setup_fee_currency='USD',
            crypto_amount=crypto_amount,
            crypto_currency=crypto_currency,
            crypto_address=payment_address,
            exchange_rate=exchange_rate,
            rate_timestamp=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        db.session.add(activation_payment)
        db.session.commit()
        
        return redirect(url_for('package_payment.payment_details', payment_id=activation_payment.id))
        
    except Exception as e:
        current_app.logger.error(f"Error creating package activation payment: {e}")
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('package_payment.initiate_activation', package_id=package_id))
        payment_address = generate_payment_address()
        
        activation_payment = PackageActivationPayment(
            client_id=current_user.id,
            package_id=package_id,
            setup_fee_amount=setup_fee,
            setup_fee_currency='USD',
            crypto_amount=btc_amount,
            crypto_currency='BTC',
            crypto_address=payment_address,
            exchange_rate=Decimal(str(btc_rate)),
            rate_timestamp=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        db.session.add(activation_payment)
        db.session.commit()
        
        return redirect(url_for('package_payment.payment_details', payment_id=activation_payment.id))
        
    except Exception as e:
        current_app.logger.error(f"Error initiating package activation: {e}")
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('main.pricing'))

@package_payment.route('/payment/<int:payment_id>')
@login_required
@client_required
def payment_details(payment_id):
    """
    Show payment details and QR code for crypto payment
    """
    try:
        payment = PackageActivationPayment.query.get_or_404(payment_id)
        
        # Verify payment belongs to current user
        if payment.client_id != current_user.id:
            flash('Payment not found.', 'error')
            return redirect(url_for('client.dashboard'))
        
        # Check if payment is expired
        if payment.is_expired:
            flash('Payment window has expired. Please create a new payment.', 'warning')
            return redirect(url_for('main.pricing'))
        
        # Check if already completed
        if payment.status == PaymentStatus.COMPLETED:
            flash('Package already activated!', 'success')
            return redirect(url_for('client.dashboard'))
        
        return render_template('package_payment/payment_details.html', payment=payment)
        
    except Exception as e:
        current_app.logger.error(f"Error showing payment details: {e}")
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('client.dashboard'))

@package_payment.route('/check-payment/<int:payment_id>')
@login_required
@client_required
@rate_limit('check_payment', limit=30)
def check_payment_status(payment_id):
    """
    AJAX endpoint to check payment status
    In production, this would query blockchain or payment processor
    """
    try:
        # Log API usage
        log_api_usage(
            user_id=current_user.id,
            endpoint=f'/package-payment/check-payment/{payment_id}',
            method='GET',
            request_data=None,
            ip_address=request.remote_addr
        )
        
        payment = PackageActivationPayment.query.get_or_404(payment_id)
        
        # Verify payment belongs to current user
        if payment.client_id != current_user.id:
            log_security_event(
                event_type='unauthorized_payment_access',
                user_id=current_user.id,
                details={'payment_id': payment_id, 'actual_owner': payment.client_id},
                ip_address=request.remote_addr
            )
            return jsonify({'error': 'Unauthorized'}), 403
        
        # For demo purposes, simulate payment detection
        # In production, integrate with blockchain API or payment processor
        
        return jsonify({
            'status': payment.status.value,
            'confirmations': payment.confirmations,
            'required_confirmations': payment.required_confirmations,
            'is_completed': payment.status == PaymentStatus.COMPLETED,
            'time_remaining': str(payment.time_remaining) if not payment.is_expired else '0:00:00'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error checking payment status: {e}")
        return jsonify({'error': 'An error occurred'}), 500

@package_payment.route('/simulate-payment/<int:payment_id>', methods=['POST'])
@login_required
@client_required
@rate_limit('simulate_payment', limit=5)
@abuse_protection('simulate_payment', threshold=10)
def simulate_payment(payment_id):
    """
    Demo endpoint to simulate successful payment
    Remove this in production!
    """
    try:
        # Log API usage (important for security monitoring in demo environment)
        log_api_usage(
            user_id=current_user.id,
            endpoint=f'/package-payment/simulate-payment/{payment_id}',
            method='POST',
            request_data={'payment_id': payment_id},
            ip_address=request.remote_addr
        )
        
        # Log security event for payment simulation
        log_security_event(
            event_type='payment_simulation_used',
            user_id=current_user.id,
            details={'payment_id': payment_id},
            ip_address=request.remote_addr
        )
        payment = PackageActivationPayment.query.get_or_404(payment_id)
        
        # Verify payment belongs to current user
        if payment.client_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Simulate successful payment
        payment.status = PaymentStatus.COMPLETED
        payment.confirmations = payment.required_confirmations
        payment.transaction_hash = f"demo_tx_{secrets.token_hex(16)}"
        
        # Activate the package
        success = payment.activate_package()
        
        if success:
            flash('Package activated successfully! Welcome to Paycrypt!', 'success')
            return jsonify({'success': True, 'redirect': url_for('client.dashboard')})
        else:
            return jsonify({'error': 'Failed to activate package'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error simulating payment: {e}")
        return jsonify({'error': 'An error occurred'}), 500

@package_payment.route('/flat-rate/<int:package_id>/<billing_cycle>')
@login_required
@client_required
def create_flat_rate_payment(package_id, billing_cycle):
    """Create flat-rate subscription payment (monthly or annual)"""
    try:
        # Validate billing cycle
        if billing_cycle not in ['monthly', 'annual']:
            flash('Invalid billing cycle selected.', 'error')
            return redirect(url_for('package_payment.initiate_activation', package_id=package_id))
        
        billing_cycle_enum = SubscriptionBillingCycle.MONTHLY if billing_cycle == 'monthly' else SubscriptionBillingCycle.ANNUAL
        
        # Get the package
        package = ClientPackage.query.get_or_404(package_id)
        
        if package.client_type != ClientType.FLAT_RATE:
            flash('Invalid package type for flat-rate billing.', 'error')
            return redirect(url_for('package_payment.initiate_activation', package_id=package_id))
        
        # Calculate billing amount
        if billing_cycle == 'monthly':
            billing_amount = package.monthly_price
        else:  # annual
            billing_amount = package.annual_price_calculated
            
        if not billing_amount:
            flash('Package pricing not configured properly.', 'error')
            return redirect(url_for('package_payment.initiate_activation', package_id=package_id))
        
        # Set billing period (start from today)
        period_start = datetime.utcnow()
        if billing_cycle == 'monthly':
            period_end = period_start + timedelta(days=30)
        else:  # annual
            period_end = period_start + timedelta(days=365)
        
        return render_template('package_payment/flat_rate_crypto_selection.html',
                             package=package,
                             billing_cycle=billing_cycle,
                             billing_amount=billing_amount,
                             period_start=period_start,
                             period_end=period_end)
        
    except Exception as e:
        current_app.logger.error(f"Error creating flat-rate payment: {e}")
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('package_payment.initiate_activation', package_id=package_id))

@package_payment.route('/flat-rate-payment/<int:payment_id>/<billing_cycle>/<crypto_currency>')
@login_required
@client_required
def create_flat_rate_crypto_payment(package_id, billing_cycle, crypto_currency):
    """Create flat-rate payment with selected cryptocurrency"""
    try:
        # Validate inputs
        if billing_cycle not in ['monthly', 'annual']:
            flash('Invalid billing cycle selected.', 'error')
            return redirect(url_for('package_payment.initiate_activation', package_id=package_id))
        
        crypto_currency = crypto_currency.upper()
        crypto_info = get_cryptocurrency_info(crypto_currency)
        if not crypto_info:
            flash('Invalid cryptocurrency selected.', 'error')
            return redirect(url_for('package_payment.create_flat_rate_payment', package_id=package_id, billing_cycle=billing_cycle))
        
        billing_cycle_enum = SubscriptionBillingCycle.MONTHLY if billing_cycle == 'monthly' else SubscriptionBillingCycle.ANNUAL
        
        # Get the package
        package = ClientPackage.query.get_or_404(package_id)
        
        # Calculate billing amount
        if billing_cycle == 'monthly':
            billing_amount = package.monthly_price
            discount_applied = None
        else:  # annual
            billing_amount = package.annual_price_calculated
            discount_applied = package.annual_discount_percent
        
        # Convert to cryptocurrency
        crypto_amount, exchange_rate = convert_fiat_to_crypto(billing_amount, 'USD', crypto_currency)
        if not crypto_amount or not exchange_rate:
            flash('Unable to get current exchange rate. Please try again later.', 'error')
            return redirect(url_for('package_payment.create_flat_rate_payment', package_id=package_id, billing_cycle=billing_cycle))
        
        # Generate payment address
        payment_address = generate_payment_address(crypto_currency)
        
        # Set billing period
        period_start = datetime.utcnow()
        if billing_cycle == 'monthly':
            period_end = period_start + timedelta(days=30)
        else:  # annual
            period_end = period_start + timedelta(days=365)
        
        # Create flat-rate subscription payment
        subscription_payment = FlatRateSubscriptionPayment(
            client_id=current_user.id,
            package_id=package_id,
            billing_cycle=billing_cycle_enum,
            billing_amount=billing_amount,
            billing_currency='USD',
            billing_period_start=period_start,
            billing_period_end=period_end,
            crypto_amount=crypto_amount,
            crypto_currency=crypto_currency,
            crypto_address=payment_address,
            exchange_rate=exchange_rate,
            rate_timestamp=datetime.utcnow(),
            discount_applied=discount_applied,
            expires_at=datetime.utcnow() + timedelta(hours=72)  # 72 hours for subscription payments
        )
        
        db.session.add(subscription_payment)
        db.session.commit()
        
        return redirect(url_for('package_payment.flat_rate_payment_details', payment_id=subscription_payment.id))
        
    except Exception as e:
        current_app.logger.error(f"Error creating flat-rate crypto payment: {e}")
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('package_payment.create_flat_rate_payment', package_id=package_id, billing_cycle=billing_cycle))

@package_payment.route('/flat-rate-payment/<int:payment_id>')
@login_required
@client_required
def flat_rate_payment_details(payment_id):
    """Show flat-rate subscription payment details"""
    try:
        payment = FlatRateSubscriptionPayment.query.get_or_404(payment_id)
        
        # Verify payment belongs to current user
        if payment.client_id != current_user.id:
            flash('Payment not found.', 'error')
            return redirect(url_for('client.dashboard'))
        
        # Check if payment is expired
        if payment.is_expired and payment.status == PaymentStatus.PENDING:
            flash('This payment has expired. Please create a new payment.', 'warning')
            return redirect(url_for('package_payment.initiate_activation', package_id=payment.package_id))
        
        return render_template('package_payment/flat_rate_payment_details.html', payment=payment)
        
    except Exception as e:
        current_app.logger.error(f"Error showing flat-rate payment details: {e}")
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('client.dashboard'))

@package_payment.route('/simulate-flat-rate-payment/<int:payment_id>')
@login_required
@client_required
def simulate_flat_rate_payment(payment_id):
    """Simulate flat-rate payment completion (demo mode)"""
    try:
        payment = FlatRateSubscriptionPayment.query.get_or_404(payment_id)
        
        # Verify payment belongs to current user
        if payment.client_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Simulate payment completion
        payment.status = PaymentStatus.COMPLETED
        payment.transaction_hash = f"demo_txn_{secrets.token_hex(16)}"
        payment.confirmations = 3
        payment.updated_at = datetime.utcnow()
        
        # Activate service
        payment.activate_service()
        
        db.session.commit()
        
        flash('Payment completed successfully! Your subscription is now active.', 'success')
        return redirect(url_for('client.dashboard'))
        
    except Exception as e:
        current_app.logger.error(f"Error simulating flat-rate payment: {e}")
        return jsonify({'error': 'An error occurred'}), 500

def generate_payment_address(crypto_currency='BTC'):
    """
    Generate a unique payment address for the specified cryptocurrency
    In production, integrate with wallet API for each supported crypto
    """
    crypto_currency = crypto_currency.upper()
    
    # Generate different address formats based on cryptocurrency
    if crypto_currency == 'BTC':
        # Bitcoin address format
        prefix = "1PayCrypt"
        random_part = secrets.token_hex(15)
        checksum = hashlib.sha256(f"{prefix}{random_part}".encode()).hexdigest()[:4]
        return f"{prefix}{random_part}{checksum}"
    
    elif crypto_currency == 'ETH':
        # Ethereum address format (42 characters, starts with 0x)
        return "0x" + secrets.token_hex(20)
    
    elif crypto_currency in ['USDT', 'USDC', 'LINK', 'UNI', 'AAVE', 'COMP', 'SHIB']:
        # ERC-20 tokens use Ethereum addresses
        return "0x" + secrets.token_hex(20)
    
    elif crypto_currency == 'LTC':
        # Litecoin address format
        prefix = "LPayCrypt"
        random_part = secrets.token_hex(15)
        checksum = hashlib.sha256(f"{prefix}{random_part}".encode()).hexdigest()[:4]
        return f"{prefix}{random_part}{checksum}"
    
    elif crypto_currency == 'BCH':
        # Bitcoin Cash address format
        prefix = "bitcoincash:q"
        random_part = secrets.token_hex(16)
        return f"{prefix}{random_part}"
    
    elif crypto_currency == 'XRP':
        # Ripple address format
        return "r" + secrets.token_hex(15) + secrets.token_hex(10)
    
    elif crypto_currency == 'ADA':
        # Cardano address format
        prefix = "addr1"
        random_part = secrets.token_hex(25)
        return f"{prefix}{random_part}"
    
    elif crypto_currency == 'SOL':
        # Solana address format (base58, ~44 characters)
        return secrets.token_urlsafe(32)[:44]
    
    elif crypto_currency == 'DOT':
        # Polkadot address format
        return "1" + secrets.token_hex(15) + secrets.token_hex(16)
    
    elif crypto_currency == 'BNB':
        # Binance Smart Chain address format (similar to Ethereum)
        return "0x" + secrets.token_hex(20)
    
    elif crypto_currency == 'MATIC':
        # Polygon uses Ethereum-compatible addresses
        return "0x" + secrets.token_hex(20)
    
    elif crypto_currency == 'AVAX':
        # Avalanche C-Chain uses Ethereum-compatible addresses
        return "0x" + secrets.token_hex(20)
    
    elif crypto_currency == 'ATOM':
        # Cosmos address format
        prefix = "cosmos1"
        random_part = secrets.token_hex(18)
        return f"{prefix}{random_part}"
    
    elif crypto_currency == 'TRX':
        # TRON address format
        prefix = "T"
        random_part = secrets.token_hex(16)
        checksum = hashlib.sha256(f"{prefix}{random_part}".encode()).hexdigest()[:4]
        return f"{prefix}{random_part}{checksum}"
    
    elif crypto_currency == 'XMR':
        # Monero address format (long address)
        return "4" + secrets.token_hex(47)
    
    elif crypto_currency == 'ZEC':
        # Zcash address format
        prefix = "t1"
        random_part = secrets.token_hex(16)
        return f"{prefix}{random_part}"
    
    elif crypto_currency == 'DOGE':
        # Dogecoin address format
        prefix = "D"
        random_part = secrets.token_hex(16)
        checksum = hashlib.sha256(f"{prefix}{random_part}".encode()).hexdigest()[:4]
        return f"{prefix}{random_part}{checksum}"
    
    elif crypto_currency == 'ETC':
        # Ethereum Classic uses Ethereum-like addresses
        return "0x" + secrets.token_hex(20)
    
    else:
        # Default to Bitcoin-like format for unknown currencies
        prefix = f"1{crypto_currency[:3]}"
        random_part = secrets.token_hex(15)
        checksum = hashlib.sha256(f"{prefix}{random_part}".encode()).hexdigest()[:4]
        return f"{prefix}{random_part}{checksum}"

def get_exchange_rate(from_currency, to_currency):
    """
    Get current exchange rate
    In production, integrate with price API
    """
    # Demo rates - in production, use real API
    demo_rates = {
        ('BTC', 'USD'): 45000.00,
        ('ETH', 'USD'): 3000.00,
        ('LTC', 'USD'): 100.00
    }
    
    return demo_rates.get((from_currency, to_currency), 45000.00)
