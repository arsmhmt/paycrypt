from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Client, ClientSetting, ClientSettingKey
from app.extensions import db
from app.models.audit import AuditTrail, AuditActionType
from app.utils.security import rate_limit, abuse_protection
from app.utils.audit import log_api_usage, log_security_event, log_client_setting_change
import secrets

client_settings_api = Blueprint('client_settings_api', __name__, url_prefix='/api/client/settings')

@client_settings_api.route('/api-keys', methods=['GET', 'POST'])
@jwt_required()
@rate_limit('client_api_keys', limit=10)
@abuse_protection('client_api_keys', threshold=20)
def manage_api_keys():
    """Manage client API keys"""
    current_user_id = get_jwt_identity()
    client = Client.query.get(current_user_id)
    
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    if request.method == 'GET':
        # Log API usage
        log_api_usage(
            user_id=client.id,
            endpoint='/api/client/settings/api-keys',
            method='GET',
            request_data=None,
            ip_address=request.remote_addr
        )
        
        # Get current API keys
        api_keys = ClientSetting.query.filter_by(
            client_id=client.id,
            key=ClientSettingKey.API_KEY
        ).all()
        
        return jsonify({
            'success': True,
            'api_keys': [key.value for key in api_keys]
        })
    
    if request.method == 'POST':
        # Log API usage
        log_api_usage(
            user_id=client.id,
            endpoint='/api/client/settings/api-keys',
            method='POST',
            request_data=request.get_json(),
            ip_address=request.remote_addr
        )
        
        # Generate new API key
        new_api_key = secrets.token_hex(32)
        
        # Store API key
        setting = ClientSetting(
            client_id=client.id,
            key=ClientSettingKey.API_KEY,
            value=new_api_key
        )
        db.session.add(setting)
        db.session.commit()
        
        # Log audit trail
        AuditTrail.log_action(
            user_id=client.id,
            action_type=AuditActionType.CREATE.value,
            entity_type='api_key',
            entity_id=setting.id,
            old_value=None,
            new_value={'api_key': new_api_key},
            request=request
        )
        
        # Log security event for API key generation
        log_security_event(
            event_type='api_key_generated',
            user_id=client.id,
            details={'client_id': client.id},
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'success': True,
            'api_key': new_api_key
        })

@client_settings_api.route('/webhook', methods=['GET', 'POST'])
@jwt_required()
@rate_limit('client_webhook', limit=15)
def manage_webhook():
    """Manage webhook settings"""
    current_user_id = get_jwt_identity()
    client = Client.query.get(current_user_id)
    
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    if request.method == 'GET':
        # Log API usage
        log_api_usage(
            user_id=client.id,
            endpoint='/api/client/settings/webhook',
            method='GET',
            request_data=None,
            ip_address=request.remote_addr
        )
        
        # Get current webhook settings
        webhook_url = ClientSetting.get_setting(client.id, ClientSettingKey.WEBHOOK_URL)
        webhook_secret = ClientSetting.get_setting(client.id, ClientSettingKey.WEBHOOK_SECRET)
        
        return jsonify({
            'success': True,
            'webhook_url': webhook_url,
            'webhook_secret': webhook_secret
        })
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Log API usage
        log_api_usage(
            user_id=client.id,
            endpoint='/api/client/settings/webhook',
            method='POST',
            request_data=data,
            ip_address=request.remote_addr
        )
        
        old_webhook_url = ClientSetting.get_setting(client.id, ClientSettingKey.WEBHOOK_URL)
        
        # Update webhook settings
        ClientSetting.update_setting(client.id, ClientSettingKey.WEBHOOK_URL, data.get('webhook_url'))
        ClientSetting.update_setting(client.id, ClientSettingKey.WEBHOOK_SECRET, secrets.token_hex(32))
        
        # Log audit trail
        AuditTrail.log_action(
            user_id=client.id,
            action_type=AuditActionType.UPDATE.value,
            entity_type='webhook',
            entity_id=client.id,
            old_value={'webhook_url': old_webhook_url},
            new_value=data,
            request=request
        )
        
        # Log client setting change
        log_client_setting_change(
            client_id=client.id,
            setting_key='webhook_settings',
            old_value={'webhook_url': old_webhook_url},
            new_value=data,
            changed_by=client.id,
            ip_address=request.remote_addr
        )
        
        # Log security event for webhook changes
        log_security_event(
            event_type='webhook_settings_changed',
            user_id=client.id,
            details={'client_id': client.id, 'new_webhook_url': data.get('webhook_url')},
            ip_address=request.remote_addr
        )
        
        return jsonify({'success': True})

@client_settings_api.route('/branding', methods=['GET', 'POST'])
@jwt_required()
@rate_limit('client_branding', limit=10)
def manage_branding():
    """Manage client branding"""
    current_user_id = get_jwt_identity()
    client = Client.query.get(current_user_id)
    
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    if request.method == 'GET':
        # Log API usage
        log_api_usage(
            user_id=client.id,
            endpoint='/api/client/settings/branding',
            method='GET',
            request_data=None,
            ip_address=request.remote_addr
        )
        
        # Get current branding settings
        logo_url = ClientSetting.get_setting(client.id, ClientSettingKey.LOGO_URL)
        primary_color = ClientSetting.get_setting(client.id, ClientSettingKey.PRIMARY_COLOR)
        secondary_color = ClientSetting.get_setting(client.id, ClientSettingKey.SECONDARY_COLOR)
        
        return jsonify({
            'success': True,
            'logo_url': logo_url,
            'primary_color': primary_color,
            'secondary_color': secondary_color
        })
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Log API usage
        log_api_usage(
            user_id=client.id,
            endpoint='/api/client/settings/branding',
            method='POST',
            request_data=data,
            ip_address=request.remote_addr
        )
        
        # Get old values for audit
        old_values = {
            'logo_url': ClientSetting.get_setting(client.id, ClientSettingKey.LOGO_URL),
            'primary_color': ClientSetting.get_setting(client.id, ClientSettingKey.PRIMARY_COLOR),
            'secondary_color': ClientSetting.get_setting(client.id, ClientSettingKey.SECONDARY_COLOR)
        }
        
        # Update branding settings
        ClientSetting.update_setting(client.id, ClientSettingKey.LOGO_URL, data.get('logo_url'))
        ClientSetting.update_setting(client.id, ClientSettingKey.PRIMARY_COLOR, data.get('primary_color'))
        ClientSetting.update_setting(client.id, ClientSettingKey.SECONDARY_COLOR, data.get('secondary_color'))
        
        # Log audit trail
        AuditTrail.log_action(
            user_id=client.id,
            action_type=AuditActionType.UPDATE.value,
            entity_type='branding',
            entity_id=client.id,
            old_value=old_values,
            new_value=data,
            request=request
        )
        
        # Log client setting change
        log_client_setting_change(
            client_id=client.id,
            setting_key='branding_settings',
            old_value=old_values,
            new_value=data,
            changed_by=client.id,
            ip_address=request.remote_addr
        )
        
        return jsonify({'success': True})
