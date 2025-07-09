from flask_restx import Api, Resource, fields
from flask import Blueprint
from flask_restx import Api
from app.api.platform_routes import platform_api

# Create API instance
api = Api(
    version='1.0',
    title='Crypto Payment Gateway API',
    description='API documentation for the Crypto Payment Gateway',
    doc='/docs'
)

# Add API documentation to platform routes
api.init_app(platform_api)

# Create API instance
api = Api(
    version='1.0',
    title='Crypto Payment Gateway API',
    description='API documentation for the Crypto Payment Gateway',
    doc='/docs'
)

# Namespaces
platform_ns = api.namespace('platform', description='Platform operations')

# Models
payment_model = api.model('Payment', {
    'id': fields.Integer(required=True, description='Payment ID'),
    'amount': fields.Float(required=True, description='Payment amount'),
    'currency': fields.String(required=True, description='Currency code'),
    'status': fields.String(required=True, description='Payment status'),
    'created_at': fields.DateTime(required=True, description='Creation timestamp')
})

platform_model = api.model('Platform', {
    'id': fields.Integer(required=True, description='Platform ID'),
    'name': fields.String(required=True, description='Platform name'),
    'platform_type': fields.String(required=True, description='Platform type'),
    'api_key': fields.String(required=True, description='API key'),
    'webhook_url': fields.String(description='Webhook URL'),
    'callback_url': fields.String(description='Callback URL')
})

# Documentation endpoints
@platform_ns.route('/docs')
class PlatformDocs(Resource):
    @api.doc('get_platform_docs')
    def get(self):
        """Get platform API documentation"""
        return {
            'endpoints': {
                '/register': 'Register a new platform',
                '/payment/initiate': 'Initiate a new payment',
                '/payment/webhook': 'Payment webhook endpoint',
                '/settings': 'Get or update platform settings'
            },
            'authentication': {
                'required': True,
                'type': 'Bearer token'
            },
            'error_codes': {
                '400': 'Bad Request',
                '401': 'Unauthorized',
                '403': 'Forbidden',
                '404': 'Not Found',
                '500': 'Internal Server Error'
            }
        }




