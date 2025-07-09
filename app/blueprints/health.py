
from flask import Blueprint, jsonify
from datetime import datetime
from app.extensions.extensions import db
from app.models.client import Client

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connectivity
        client_count = Client.query.count()
        
        # Check critical services
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'client_count': client_count,
            'version': '1.0.0',
            'environment': os.getenv('FLASK_ENV', 'production')
        }
        
        return jsonify(health_data), 200
        
    except Exception as e:
        error_data = {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e),
            'database': 'disconnected'
        }
        return jsonify(error_data), 503

@health_bp.route('/health/detailed')
def detailed_health_check():
    """Detailed health check with more metrics"""
    try:
        from app.models.client_package import ClientPackage
        from app.services.usage_alerts import UsageAlertService
        
        # Gather detailed metrics
        total_clients = Client.query.count()
        active_clients = Client.query.filter_by(is_active=True).count()
        packages_count = ClientPackage.query.count()
        
        # Check recent activity (if you have transaction logs)
        # recent_transactions = Transaction.query.filter(
        #     Transaction.created_at >= datetime.utcnow() - timedelta(hours=24)
        # ).count()
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': {
                'total_clients': total_clients,
                'active_clients': active_clients,
                'packages_available': packages_count,
                'database_status': 'connected',
                'uptime_check': True
            },
            'environment': os.getenv('FLASK_ENV', 'production'),
            'version': '1.0.0'
        }
        
        return jsonify(health_data), 200
        
    except Exception as e:
        error_data = {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }
        return jsonify(error_data), 503
