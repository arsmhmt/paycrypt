from flask import Blueprint
from .platform_routes import platform_api
from .client_settings import client_settings_api
from .exchange_routes import bp as exchange_bp

# Create main API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Add status and client endpoints
@api_bp.route('/status/heartbeat', methods=['GET'])
def status_heartbeat():
    """Simple heartbeat endpoint for status checks"""
    from flask import jsonify
    import datetime
    try:
        current_time = datetime.datetime.now()
        return jsonify({
            'status': 'ok',
            'timestamp': current_time.isoformat(),
            'api_status': 'operational',
            'payment_status': 'active'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.datetime.now().isoformat()
        }), 500

# Register API blueprints
def init_app(app):
    """Register API blueprints with the Flask application."""
    # Register the exchange routes
    api_bp.register_blueprint(exchange_bp)
    
    # Register other API blueprints
    api_bp.register_blueprint(platform_api, url_prefix='/platforms')
    api_bp.register_blueprint(client_settings_api, url_prefix='/client-settings')
    
    # Register the main API blueprint with the app
    app.register_blueprint(api_bp)
