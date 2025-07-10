import os
import logging  # ✅ Add this at the top
from datetime import datetime, timedelta
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import Unauthorized

from flask import Flask, jsonify, g, has_request_context
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from flask_babel import _

# Import context processors
from .context_processors import inject_coin_utils

# Import extensions from the central extensions module
from .extensions.extensions import init_app as init_extensions, db
from .config import config

# scheduler importunu kaldır, yerine burada oluştur
scheduler = BackgroundScheduler()

def create_app(config_class=None):
    """
    Create and configure the Flask application using the factory pattern.
    
    Args:
        config_class: Optional configuration class to use. If not provided,
                    will use the appropriate config based on FLASK_ENV.
    
    Returns:
        Flask: The configured Flask application instance.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Configure logging early
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        force=True  # Override any existing handlers
    )
    
    # Create the Flask app
    app = Flask(__name__, 
               instance_relative_config=True, 
               template_folder='templates', 
               static_folder='static')

    # Load configuration
    if config_class is None:
        env = os.getenv('FLASK_ENV', 'development')
        app.logger.info(f"Loading {env} configuration")
        app.config.from_object(config[env])
    else:
        app.logger.info("Loading custom configuration class")
        app.config.from_object(config_class)

    # Ensure required config values are set
    if not app.config.get('SECRET_KEY'):
        app.logger.warning("SECRET_KEY not set, using development default")
        app.config['SECRET_KEY'] = 'dev-key-123'

    # Always set the database URI before initializing extensions
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')

    # Initialize all Flask extensions (db, jwt, mail, login_manager, etc.)
    init_extensions(app)
    
    # Configure app logger
    app.logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)
    
    # Set SQLAlchemy logging level
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    
    app.logger.info("Application factory starting up...")
    
    # Load configuration
    if config_class is None:
        
        env = os.getenv('FLASK_ENV', 'development')
        app.logger.info(f"Loading {env} configuration")
        app.config.from_object(config[env])
    else:
        app.logger.info("Loading custom configuration class")
        app.config.from_object(config_class)
    
    # Ensure required config values are set
    if not app.config.get('SECRET_KEY'):
        app.logger.warning("SECRET_KEY not set, using development default")
        app.config['SECRET_KEY'] = 'dev-key-123'
    
    # Log configuration values for debugging
    app.logger.debug(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    app.logger.debug(f"Debug mode: {app.debug}")
    app.logger.debug(f"Testing mode: {app.testing}")
    app.logger.debug(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    
    # Initialize all extensions
    app.logger.info("Initializing extensions...")

    # Set the database URI for Google Cloud or fallback to SQLite
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')

    # Initialize all Flask extensions (db, jwt, mail, login_manager, etc.)
    init_extensions(app)

    # Import models after extensions are initialized
    with app.app_context():
        # Import models to register them with SQLAlchemy
        from . import models  # noqa: F401
        # Register Flask-Login user_loader
        from app.models.user import User
        from app.extensions.extensions import login_manager
        @login_manager.user_loader
        def load_user(user_id):
            try:
                return User.query.get(int(user_id))
            except Exception:
                return None
        
        # Set up model relationships after all models are loaded
        if hasattr(models, 'payment') and hasattr(models, 'recurring_payment'):
            Payment = models.payment.Payment
            RecurringPayment = models.recurring_payment.RecurringPayment
            
            if Payment and RecurringPayment:
                # Set up the relationship if it's not already set
                if not hasattr(Payment, 'recurring_payment'):
                    Payment.recurring_payment = db.relationship(
                        'RecurringPayment', 
                        back_populates='payments'
                    )
                
                if not hasattr(RecurringPayment, 'payments'):
                    RecurringPayment.payments = db.relationship(
                        'Payment',
                        back_populates='recurring_payment',
                        cascade='all, delete-orphan',
                        lazy='dynamic'
                    )
                
                app.logger.debug("Payment and RecurringPayment relationships configured")
    
    # Initialize security headers for production
    if not app.debug and not app.testing:
        app.logger.info("Initializing security headers for production...")
        try:
            from .security.headers import init_security_headers
            init_security_headers(app)
            app.logger.info("Security headers initialized successfully")
        except Exception as e:
            app.logger.error(f"Failed to initialize security headers: {e}")
    
    # Add translation function to template context (Flask-Babel)
    @app.context_processor
    def inject_translator():
        return {'_': _}

    # Add CSRF token to template context
    @app.context_processor
    def inject_csrf_token():
        try:
            # Import the CSRF token generator from flask_wtf
            from flask_wtf.csrf import generate_csrf
            
            def token_func():
                token = generate_csrf()
                # Log token generation for debugging
                app.logger.debug(f"CSRF token generated for session")
                return token
                
            return dict(csrf_token=token_func)
        except Exception as e:
            app.logger.warning(f"CSRF token context processor error: {e}")
            # Fallback function
            import secrets
            return dict(csrf_token=lambda: secrets.token_urlsafe(32))

    # Add sidebar stats to template context for admin templates
    @app.context_processor
    def inject_sidebar_stats():
        """Inject sidebar stats into all admin templates"""
        try:
            # Only inject for admin routes
            from flask import request
            if request and request.blueprint == 'admin':
                # Import here to avoid circular imports
                from app.admin.routes import get_sidebar_stats
                sidebar_stats = get_sidebar_stats()
                app.logger.debug(f"App context processor returning sidebar_stats: {sidebar_stats}")
                return dict(sidebar_stats=sidebar_stats)
        except Exception as e:
            app.logger.error(f"Error in app sidebar stats context processor: {str(e)}")
            # Return fallback data for admin routes
            if request and request.blueprint == 'admin':
                return dict(sidebar_stats={
                    'pending_withdrawals': 0,
                    'pending_user_withdrawals': 0,
                    'pending_client_withdrawals': 0,
                    'total_clients': 0,
                    'custom_wallets': 0,
                    'pending_tickets': 0
                })
        return dict()

    # Add package and feature management helpers to template context
    @app.context_processor
    def inject_package_helpers():
        """Make package and feature functionality available in all templates"""
        try:
            from app.config.packages import template_helpers
            helpers = template_helpers()
            app.logger.debug(f"Package helpers injected: {list(helpers.keys())}")
            return helpers
        except Exception as e:
            app.logger.error(f"Error in package helpers context processor: {str(e)}")
            return dict()

    # Add security headers to all responses
    @app.after_request
    def add_security_headers(response):
        app.logger.debug('[SECURITY] add_security_headers called')
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        # XSS Protection (legacy but still good to have)
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # Content Security Policy (allow CDN resources for styling)
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data:;"
        )
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # Remove server information
        response.headers.pop('Server', None)
        return response

    app.logger.debug("[LOGIN_MANAGER] Login manager configured")
    
    # Register context processors
    app.context_processor(inject_coin_utils)
    
    # Import and register blueprints with proper error handling
    try:
        from .auth_routes import bp as auth_bp
        from .main_routes import main
        from .admin.routes import admin_bp
        from .admin.withdrawal_routes import withdrawal_bp
        from .client_routes import client_bp
        from .api import api_bp
        from .package_payment_routes import package_payment
        
        # Register blueprints
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(main)
        app.register_blueprint(admin_bp)  # Secure admin path only
        app.register_blueprint(withdrawal_bp)
        app.register_blueprint(client_bp, url_prefix='/client')
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(package_payment, url_prefix='/package_payment')

        app.logger.info("Blueprints registered successfully")
        
    except ImportError as e:
        app.logger.error(f"Failed to import blueprints: {e}", exc_info=True)
        raise
    
    # Create database tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables verified/created")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {e}", exc_info=True)
            raise
    
    # Register error handlers
    @app.errorhandler(Unauthorized)
    def handle_unauthorized(e):
        app.logger.warning(f"Unauthorized access: {e}")
        return jsonify({
            "status": "error",
            "message": "Authentication required",
            "error": str(e.description) if hasattr(e, 'description') else 'Unauthorized'
        }), 401

    @app.errorhandler(404)
    def handle_not_found(e):
        app.logger.warning(f"Not found: {e}")
        return jsonify({
            "status": "error",
            "message": "The requested resource was not found"
        }), 404

    @app.errorhandler(500)
    def handle_server_error(e):
        app.logger.error(f"Server error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred"
        }), 500
    
    # Register core components (template filters, context processors, health check)
    try:
        from .core import register_core_components
        register_core_components(app)
        app.logger.info("Core components registered")
    except Exception as e:
        app.logger.error(f"Failed to register core components: {e}", exc_info=True)
        raise
    
    # Initialize database and create default admin user
    with app.app_context():
        try:
            from .models.admin import AdminUser
            
            admin_username = os.getenv('ADMIN_USERNAME', 'admin')
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin')
            admin_email = os.getenv('ADMIN_EMAIL', 'admin@paycrypt.online')

            if admin_username and admin_password:
                # Check if admin exists by username or email
                existing_admin = AdminUser.query.filter(
                    (AdminUser.username == admin_username) | 
                    (AdminUser.email == admin_email)
                ).first()
                
                if not existing_admin:
                    admin = AdminUser(
                        username=admin_username,
                        email=admin_email,
                        password=admin_password,
                        first_name='Admin',
                        last_name='User',
                        is_active=True,
                        is_superuser=True
                    )
                    db.session.add(admin)
                    try:
                        db.session.add(admin)
                        db.session.commit()
                        app.logger.info(f"Created admin user: {admin_username}")
                    except Exception as e:
                        db.session.rollback()
                        app.logger.error(f"Failed to create admin user: {e}", exc_info=True)
                        raise
                else:
                    app.logger.info(f"Admin user already exists: {existing_admin.username}")

                # Create default client admin if it doesn't exist
                try:
                    from .models.client import Client
                    if not Client.query.filter_by(email=admin_email).first():
                        client_admin = Client(
                            company_name='Admin Company',
                            email=admin_email,
                            is_active=True,
                            is_verified=True
                        )
                        client_admin.set_password(admin_password)
                        db.session.add(client_admin)
                        db.session.commit()
                        app.logger.info(f"Created client admin user: {admin_email}")
                except Exception as e:
                    app.logger.error(f"Failed to create client admin: {e}", exc_info=True)
                    db.session.rollback()

                # Create default platform if none exists
                try:
                    from .models.platform import Platform, PlatformType
                    if not Platform.query.first():
                        platform = Platform(
                            name='Default Platform',
                            platform_type=PlatformType.SAAS,
                            api_key=os.getenv('PLATFORM_API_KEY', 'default_api_key'),
                            api_secret=os.getenv('PLATFORM_API_SECRET', 'default_api_secret'),
                            webhook_url=os.getenv('PLATFORM_WEBHOOK_URL', 'https://example.com/webhook')
                        )
                        db.session.add(platform)
                        db.session.commit()
                        app.logger.info("Created default platform")
                except Exception as e:
                    app.logger.error(f"Failed to create default platform: {e}", exc_info=True)
                    db.session.rollback()

        except Exception as e:
            app.logger.error(f"Database initialization failed: {e}", exc_info=True)
            db.session.rollback()
            if os.getenv('FLASK_ENV') == 'production':
                raise  # In production, we want to fail fast

    # Start the scheduler if not already running
    if not scheduler.running:
        try:
            scheduler.start()
            app.logger.info("Background scheduler started successfully")
        except Exception as e:
            app.logger.error(f"Scheduler failed to start: {e}", exc_info=True)
    
    # Register CLI commands
    try:
        # Register usage alert commands
        from .services.usage_alerts import create_usage_alert_commands
        create_usage_alert_commands(app)
        
        # Register admin CLI commands
        from .commands.admin_cli import register_admin_commands
        register_admin_commands(app)
        
        # Add project root to Python path
        import sys
        from pathlib import Path
        project_root = str(Path(__file__).parent.parent)
        if project_root not in sys.path:
            sys.path.append(project_root)
        
        # Register coin management commands
        try:
            from scripts.manage_coins import register_commands as register_coin_commands
            register_coin_commands(app)
        except ImportError as e:
            app.logger.warning(f"Could not register coin management commands: {e}")
        
        # Register package management commands
        try:
            from scripts.manage_packages import package as package_commands
            app.cli.add_command(package_commands, name="package")
        except ImportError as e:
            app.logger.warning(f"Could not register package management commands: {e}")
        
        # Register test commands
        try:
            from scripts.test_package_management import register_commands as register_test_commands
            register_test_commands(app)
        except ImportError as e:
            app.logger.warning(f"Could not register test commands: {e}")
        
        # Initialize migrations - temporarily disabled to fix migration issues
        # from flask_migrate import upgrade
        # with app.app_context():
        #     upgrade()
        
        app.logger.info("CLI commands registered successfully")
    except Exception as e:
        app.logger.error(f"Failed to register CLI commands: {e}", exc_info=True)

    app.logger.info("Application factory initialization complete")
    return app
