"""
Core application functionality including template filters, context processors, and utility functions.
"""
from datetime import datetime
from flask import jsonify

def register_core_components(app):
    """Register core components with the Flask application."""
    # Register template filters
    @app.template_filter('currency')
    def format_currency(value, currency='USD'):
        """Format a number as a currency string."""
        if value is None:
            return ""
        return f"${value:,.2f} {currency}"

    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
        """Format a datetime object as a string."""
        if value is None:
            return ""
        return value.strftime(format)
    
    # Register context processors
    @app.context_processor
    def inject_now():
        """Inject the current UTC time into all templates."""
        return {'now': datetime.utcnow()}
    
    # Register health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for load balancers and monitoring."""
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': app.config.get('ENV', 'development')
        })
