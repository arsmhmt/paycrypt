"""
Security Headers Configuration for PayCrypt Gateway
Implements comprehensive security headers using Flask-Talisman
"""

from flask_talisman import Talisman
from flask import request

def init_security_headers(app):
    """Initialize security headers for production deployment"""
    
    # Content Security Policy for PayCrypt Gateway
    csp = {
        'default-src': "'self'",
        'script-src': [
            "'self'",
            "'unsafe-inline'",  # Required for inline scripts in dashboard
            "'unsafe-eval'",    # Required for Chart.js and dynamic content
            "https://code.jquery.com",
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com",
            "https://unpkg.com"
        ],
        'style-src': [
            "'self'",
            "'unsafe-inline'",  # Required for dynamic styles
            "https://fonts.googleapis.com",
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com"
        ],
        'font-src': [
            "'self'",
            "https://fonts.gstatic.com",
            "https://cdnjs.cloudflare.com",
            "data:"
        ],
        'img-src': [
            "'self'",
            "data:",
            "https:",
            "blob:"
        ],
        'connect-src': [
            "'self'",
            "https://api.coingecko.com",  # For exchange rates
            "wss:",  # WebSocket support
            "https:"
        ],
        'frame-src': "'none'",
        'object-src': "'none'",
        'base-uri': "'self'",
        'form-action': "'self'"
    }
    
    # Development vs Production Configuration
    if app.config.get('ENV') == 'development':
        # Relaxed CSP for development
        csp['script-src'].append("'unsafe-eval'")
        force_https = False
        strict_transport_security = False
    else:
        # Strict CSP for production
        force_https = True
        strict_transport_security = True
        strict_transport_security_max_age = 31536000  # 1 year
    
    # Initialize Talisman with comprehensive security headers
    Talisman(
        app,
        # HTTPS Enforcement
        force_https=force_https,
        strict_transport_security=strict_transport_security,
        strict_transport_security_max_age=31536000 if not app.debug else None,
        strict_transport_security_include_subdomains=True,
        
        # Content Security Policy
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src', 'style-src'],
        
        # Additional Security Headers
        referrer_policy='strict-origin-when-cross-origin',
        permissions_policy={
            'geolocation': '()',
            'microphone': '()',
            'camera': '()',
            'payment': '(self)',  # Allow payment APIs
            'usb': '()',
            'magnetometer': '()',
            'gyroscope': '()',
            'accelerometer': '()'
        },
        
        # Feature Policy (for older browsers)
        feature_policy={
            'geolocation': "'none'",
            'microphone': "'none'",
            'camera': "'none'",
            'payment': "'self'",
            'usb': "'none'"
        },
        
        # Content Type Options
        content_type_options=True,
        
        # X-Frame-Options
        frame_options='DENY',
        
        # XSS Protection
        content_security_policy_report_only=False,
        
        # Session Security
        session_cookie_secure=not app.debug,
        session_cookie_http_only=True,
        session_cookie_samesite='Lax'
    )
    
    # Additional custom security headers
    @app.after_request
    def add_security_headers(response):
        """Add additional security headers"""
        
        # Server header hiding
        response.headers['Server'] = 'PayCrypt-Gateway'
        
        # Additional security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Expect-CT'] = 'max-age=86400, enforce'
        
        # API-specific headers
        if request.path.startswith('/api/'):
            response.headers['X-API-Version'] = '1.0'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
        
        # Admin panel additional security
        if request.path.startswith('/admin') or 'admin' in request.path:
            response.headers['X-Admin-Security'] = 'enhanced'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        
        return response
    
    app.logger.info("Security headers initialized with Flask-Talisman")
    return app
