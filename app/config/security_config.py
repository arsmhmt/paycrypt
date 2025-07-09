"""
Security Configuration for CPGateway
Centralized configuration for rate limiting, abuse protection, and security settings
"""

# Rate Limiting Configuration (requests per minute)
RATE_LIMITS = {
    # Admin Authentication
    'admin_login': 10,
    'admin_logout': 20,
    
    # Admin Operations
    'admin_client_management': 30,
    'admin_withdrawal_approval': 20,
    'admin_payment_management': 25,
    'admin_settings': 15,
    'admin_user_management': 20,
    
    # Client Authentication & Management
    'client_login': 15,
    'client_registration': 5,
    'client_password_reset': 5,
    'client_api_keys': 10,
    'client_webhook': 15,
    'client_branding': 10,
    
    # API Platform Operations
    'platform_register': 5,
    'payment_initiate': 30,
    'payment_webhook': 60,
    'platform_settings': 20,
    
    # Exchange Operations
    'exchange_rate': 60,
    'exchange_convert': 30,
    
    # Package & Payment Operations
    'package_activation': 10,
    'create_payment': 20,
    'check_payment': 30,
    'simulate_payment': 5,  # Very restrictive for demo endpoint
    
    # Webhook Operations
    'payment_status_webhook': 100,
    'webhook_verification': 50,
    
    # General API Usage
    'api_general': 100,
    'file_upload': 10,
}

# Abuse Protection Configuration (threshold for blocking)
ABUSE_THRESHOLDS = {
    # Admin Authentication
    'admin_login': 20,
    'admin_logout': 50,
    
    # Admin Operations
    'admin_client_management': 100,
    'admin_withdrawal_approval': 50,
    'admin_payment_management': 75,
    'admin_settings': 30,
    'admin_user_management': 50,
    
    # Client Authentication & Management
    'client_login': 30,
    'client_registration': 10,
    'client_password_reset': 10,
    'client_api_keys': 20,
    'client_webhook': 30,
    'client_branding': 25,
    
    # API Platform Operations
    'platform_register': 10,
    'payment_initiate': 100,
    'payment_webhook': 300,
    'platform_settings': 50,
    
    # Exchange Operations
    'exchange_rate': 200,
    'exchange_convert': 100,
    
    # Package & Payment Operations
    'package_activation': 25,
    'create_payment': 50,
    'check_payment': 100,
    'simulate_payment': 10,  # Very restrictive for demo endpoint
    
    # Webhook Operations
    'payment_status_webhook': 300,
    'webhook_verification': 150,
    
    # General API Usage
    'api_general': 500,
    'file_upload': 25,
}

# Fraud Detection Configuration
FRAUD_DETECTION = {
    'enabled': True,
    'risk_thresholds': {
        'low': 0.3,
        'medium': 0.6,
        'high': 0.8,
        'critical': 0.9
    },
    'actions': {
        'low': 'log',  # Just log the event
        'medium': 'alert',  # Log and send alert
        'high': 'block',  # Block the action
        'critical': 'ban'  # Temporary ban
    },
    'failed_login_threshold': 5,  # Number of failed logins before flagging
    'suspicious_withdrawal_amount': 10000,  # USD equivalent
    'withdrawal_frequency_threshold': 10,  # Max withdrawals per hour
    'api_abuse_threshold': 1000,  # Requests per hour
}

# Webhook Security Configuration
WEBHOOK_SECURITY = {
    'signature_required': True,
    'timestamp_tolerance': 300,  # 5 minutes
    'replay_protection': True,
    'rate_limit_enabled': True,
    'ip_whitelist_enabled': False,
    'allowed_ips': [],
}

# Security Event Logging Configuration
SECURITY_LOGGING = {
    'enabled': True,
    'log_levels': {
        'authentication_events': 'INFO',
        'authorization_failures': 'WARNING',
        'fraud_detection': 'CRITICAL',
        'rate_limit_exceeded': 'WARNING',
        'webhook_security': 'WARNING',
        'admin_actions': 'INFO',
        'api_abuse': 'CRITICAL',
    },
    'retention_days': 90,
    'alert_on_critical': True,
}

# IP Blocking Configuration
IP_BLOCKING = {
    'enabled': True,
    'failed_login_threshold': 10,  # Block after 10 failed logins
    'block_duration': 3600,  # 1 hour in seconds
    'whitelist': ['127.0.0.1', '::1'],  # Never block localhost
    'permanent_blacklist': [],
}

# Session Security Configuration
SESSION_SECURITY = {
    'timeout_minutes': 30,
    'concurrent_sessions_limit': 3,
    'force_logout_on_suspicious_activity': True,
    'require_reauth_for_sensitive_operations': True,
}

# API Key Security Configuration
API_KEY_SECURITY = {
    'rotation_required_days': 90,
    'max_keys_per_client': 5,
    'key_length': 32,
    'rate_limit_per_key': 1000,  # Requests per hour per API key
}

# Audit Configuration
AUDIT_CONFIG = {
    'enabled': True,
    'log_admin_actions': True,
    'log_client_actions': True,
    'log_api_usage': True,
    'log_security_events': True,
    'retention_days': 365,  # 1 year retention for audit logs
    'encrypt_sensitive_data': True,
}

# Alert Configuration
ALERT_CONFIG = {
    'enabled': True,
    'channels': ['email', 'webhook'],
    'email_recipients': ['security@company.com', 'admin@company.com'],
    'webhook_url': None,  # Set in environment variables
    'alert_thresholds': {
        'failed_logins_per_hour': 50,
        'high_risk_transactions_per_hour': 10,
        'api_errors_per_hour': 100,
        'webhook_failures_per_hour': 20,
    }
}

def get_rate_limit(endpoint_key):
    """Get rate limit for a specific endpoint"""
    return RATE_LIMITS.get(endpoint_key, RATE_LIMITS['api_general'])

def get_abuse_threshold(endpoint_key):
    """Get abuse threshold for a specific endpoint"""
    return ABUSE_THRESHOLDS.get(endpoint_key, ABUSE_THRESHOLDS['api_general'])

def is_fraud_detection_enabled():
    """Check if fraud detection is enabled"""
    return FRAUD_DETECTION['enabled']

def get_fraud_risk_threshold(level):
    """Get fraud risk threshold for a specific level"""
    return FRAUD_DETECTION['risk_thresholds'].get(level, 0.5)

def should_alert_on_critical():
    """Check if alerts should be sent on critical events"""
    return SECURITY_LOGGING['alert_on_critical']
