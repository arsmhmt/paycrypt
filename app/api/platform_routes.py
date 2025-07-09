from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import (
    Platform, PlatformType, PlatformSetting,
    Payment, PaymentStatus, Client
)
from app.extensions import db
from app.models.audit import AuditTrail, AuditActionType
from app.models.notification import NotificationType, NotificationEvent
from app.utils.security import rate_limit, abuse_protection
from app.utils.audit import log_api_usage, log_security_event
from app.utils.fraud_detection import FraudDetectionService
from app.utils.webhook_security import WebhookHandler
import hashlib
import hmac
import json
import secrets

platform_api = Blueprint('platform_api', __name__, url_prefix='/api/platform')

def verify_webhook_signature(request, webhook_secret):
    """Verify webhook signature"""
    signature = request.headers.get('X-Signature')
    if not signature:
        return False
    
    payload = request.get_data()
    expected_signature = hmac.new(
        webhook_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

@platform_api.route('/register', methods=['POST'])
@rate_limit('platform_register', limit=5)
@abuse_protection('platform_register', threshold=10)
def register_platform():
    """Register a new platform"""
    data = request.get_json()
    
    try:
        # Log API usage
        log_api_usage(
            user_id=None,
            endpoint='/api/platform/register',
            method='POST',
            request_data=data,
            ip_address=request.remote_addr
        )
        
        platform = Platform(
            name=data['name'],
            platform_type=data['platform_type'],
            api_key=Platform.generate_api_key(),
            api_secret=secrets.token_hex(32),
            webhook_url=data.get('webhook_url'),
            callback_url=data.get('callback_url')
        )
        
        db.session.add(platform)
        db.session.commit()
        
        # Log audit trail
        AuditTrail.log_action(
            user_id=None,
            action_type=AuditActionType.CREATE.value,
            entity_type='platform',
            entity_id=platform.id,
            old_value=None,
            new_value=platform.to_dict(),
            request=request
        )
        
        # Log security event
        log_security_event(
            event_type='platform_registered',
            user_id=None,
            details={
                'platform_id': platform.id,
                'platform_name': platform.name,
                'platform_type': platform.platform_type
            },
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'success': True,
            'api_key': platform.api_key,
            'api_secret': platform.api_secret
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log_security_event(
            event_type='platform_registration_failed',
            user_id=None,
            details={'error': str(e)},
            ip_address=request.remote_addr
        )
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@platform_api.route('/payment/initiate', methods=['POST'])
@jwt_required()
@rate_limit('payment_initiate', limit=30)
@abuse_protection('payment_initiate', threshold=100)
def initiate_payment():
    """Initiate a new payment for a platform"""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    platform = Platform.query.get(current_user_id)
    
    if not platform:
        return jsonify({'error': 'Platform not found'}), 404
    
    try:
        # Log API usage
        log_api_usage(
            user_id=platform.id,
            endpoint='/api/platform/payment/initiate',
            method='POST',
            request_data=data,
            ip_address=request.remote_addr
        )
        
        # Run fraud detection
        fraud_service = FraudDetectionService()
        risk_score = fraud_service.analyze_payment_creation(
            platform_id=platform.id,
            amount=data['amount'],
            client_id=data['client_id'],
            ip_address=request.remote_addr
        )
        
        if risk_score > 0.8:  # High risk threshold
            log_security_event(
                event_type='high_risk_payment_blocked',
                user_id=platform.id,
                details={
                    'risk_score': risk_score,
                    'amount': data['amount'],
                    'client_id': data['client_id']
                },
                ip_address=request.remote_addr
            )
            return jsonify({
                'success': False,
                'error': 'Payment blocked due to security concerns'
            }), 403
        
        payment = Payment(
            platform_id=platform.id,
            client_id=data['client_id'],
            amount=data['amount'],
            currency=data['currency'],
            payment_method=data['payment_method'],
            reference=data.get('reference'),
            status=PaymentStatus.PENDING
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # Log audit trail
        AuditTrail.log_action(
            user_id=platform.id,
            action_type=AuditActionType.CREATE.value,
            entity_type='payment',
            entity_id=payment.id,
            old_value=None,
            new_value=payment.to_dict(),
            request=request
        )
        
        # Send webhook notification
        if platform.webhook_url:
            webhook_data = {
                'event': 'payment_created',
                'payment': payment.to_dict()
            }
            
            # Send to platform's webhook URL
            # Implementation for webhook sending
            pass
        
        return jsonify({
            'success': True,
            'payment_id': payment.id,
            'payment_url': f"{request.host_url}payment/{payment.id}/process"
        })
        
    except Exception as e:
        db.session.rollback()
        log_security_event(
            event_type='payment_initiation_failed',
            user_id=platform.id,
            details={'error': str(e)},
            ip_address=request.remote_addr
        )
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@platform_api.route('/payment/webhook', methods=['POST'])
@rate_limit('payment_webhook', limit=60)
def payment_webhook():
    """Handle payment webhook notifications"""
    webhook_handler = WebhookHandler()
    
    try:
        # Verify webhook signature and timestamp
        if not webhook_handler.verify_webhook(request):
            log_security_event(
                event_type='invalid_webhook_signature',
                user_id=None,
                details={'endpoint': '/api/platform/payment/webhook'},
                ip_address=request.remote_addr
            )
            return jsonify({'error': 'Invalid signature'}), 401
        
        data = request.get_json()
        payment_id = data.get('payment_id')
        status = data.get('status')
        
        # Log API usage
        log_api_usage(
            user_id=None,
            endpoint='/api/platform/payment/webhook',
            method='POST',
            request_data=data,
            ip_address=request.remote_addr
        )
        
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        old_status = payment.status
        
        # Update payment status
        payment.status = status
        db.session.commit()
        
        # Log audit trail
        AuditTrail.log_action(
            user_id=payment.platform_id,
            action_type=AuditActionType.UPDATE.value,
            entity_type='payment',
            entity_id=payment.id,
            old_value={'status': old_status},
            new_value={'status': status},
            request=request
        )
        
        # Send notification to client
        if payment.client.notification_preferences.filter_by(
            notification_type='payment_status_changed',
            channel='email',
            enabled=True
        ).first():
            # Send email notification
            pass
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        log_security_event(
            event_type='webhook_processing_failed',
            user_id=None,
            details={'error': str(e)},
            ip_address=request.remote_addr
        )
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@platform_api.route('/settings', methods=['GET', 'POST'])
@jwt_required()
@rate_limit('platform_settings', limit=20)
def platform_settings():
    """Get or update platform settings"""
    current_user_id = get_jwt_identity()
    platform = Platform.query.get(current_user_id)
    
    if not platform:
        return jsonify({'error': 'Platform not found'}), 404
    
    if request.method == 'GET':
        # Log API usage
        log_api_usage(
            user_id=platform.id,
            endpoint='/api/platform/settings',
            method='GET',
            request_data=None,
            ip_address=request.remote_addr
        )
        
        settings = PlatformSetting.query.filter_by(platform_id=platform.id).all()
        return jsonify({
            'success': True,
            'settings': {s.key: s.value for s in settings}
        })
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Log API usage
        log_api_usage(
            user_id=platform.id,
            endpoint='/api/platform/settings',
            method='POST',
            request_data=data,
            ip_address=request.remote_addr
        )
        
        old_settings = {}
        for key, value in data.items():
            setting = PlatformSetting.query.filter_by(
                platform_id=platform.id,
                key=key
            ).first()
            
            if setting:
                old_settings[key] = setting.value
                setting.value = value
            else:
                old_settings[key] = None
                setting = PlatformSetting(
                    platform_id=platform.id,
                    key=key,
                    value=value
                )
                db.session.add(setting)
        
        db.session.commit()
        
        # Log audit trail
        AuditTrail.log_action(
            user_id=platform.id,
            action_type=AuditActionType.UPDATE.value,
            entity_type='platform_settings',
            entity_id=platform.id,
            old_value=old_settings,
            new_value=data,
            request=request
        )
        
        # Log security event for sensitive settings
        sensitive_keys = ['webhook_url', 'api_secret', 'security_settings']
        if any(key in sensitive_keys for key in data.keys()):
            log_security_event(
                event_type='sensitive_platform_settings_changed',
                user_id=platform.id,
                details={'changed_keys': list(data.keys())},
                ip_address=request.remote_addr
            )
        
        return jsonify({'success': True})
