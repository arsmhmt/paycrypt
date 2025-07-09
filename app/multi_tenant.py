from flask import Flask, request
from werkzeug.middleware.proxy_fix import ProxyFix
from app.models import Client
from app.extensions import db

class MultiTenantMiddleware:
    def __init__(self, app: Flask):
        self.app = app
        self.app.wsgi_app = ProxyFix(self.app.wsgi_app)
        
    def __call__(self, environ, start_response):
        # Get the hostname from the request
        host = environ.get('HTTP_HOST', '').split(':')[0]
        
        # Check if this is a subdomain request
        if '.' in host:
            subdomain = host.split('.')[0]
            
            # Try to find client by subdomain
            client = Client.query.filter_by(subdomain=subdomain).first()
            
            if client:
                # Store client ID in the environment
                environ['CLIENT_ID'] = str(client.id)
                
                # Apply client-specific branding
                self.apply_branding(client, environ)
        
        return self.app(environ, start_response)
    
    def apply_branding(self, client: Client, environ):
        """Apply client-specific branding to the request"""
        # Get branding settings
        logo_url = client.settings.filter_by(key='logo_url').first()
        primary_color = client.settings.filter_by(key='primary_color').first()
        secondary_color = client.settings.filter_by(key='secondary_color').first()
        
        # Store branding settings in environment
        environ['BRANDING'] = {
            'logo_url': logo_url.value if logo_url else None,
            'primary_color': primary_color.value if primary_color else '#007bff',
            'secondary_color': secondary_color.value if secondary_color else '#6c757d'
        }

def init_multi_tenant(app: Flask):
    """Initialize multi-tenant support"""
    # Add middleware
    app.wsgi_app = MultiTenantMiddleware(app)
    
    # Add template context processor for branding
    @app.context_processor
    def inject_branding():
        def get_branding():
            return request.environ.get('BRANDING', {
                'logo_url': None,
                'primary_color': '#007bff',
                'secondary_color': '#6c757d'
            })
        return dict(get_branding=get_branding)
    
    # Add URL converters for subdomains
    class SubdomainConverter:
        def to_python(self, value):
            return value
        
        def to_url(self, value):
            return value
    
    app.url_map.converters['subdomain'] = SubdomainConverter
    
    # Add error handlers
    @app.errorhandler(404)
    def handle_404(e):
        client_id = request.environ.get('CLIENT_ID')
        if client_id:
            # Try to redirect to client-specific error page
            return render_template('errors/404.html', client_id=client_id), 404
        return render_template('errors/404.html'), 404
