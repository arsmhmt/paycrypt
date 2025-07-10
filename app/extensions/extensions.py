from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_caching import Cache
from flask_apscheduler import APScheduler
from flask_login import LoginManager, current_user
from flask_wtf import CSRFProtect
from flask_babel import Babel, gettext as _
from flask import Flask, current_app, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_cors import CORS
from flask_compress import Compress
from flask_assets import Environment, Bundle
from flask_cdn import CDN
from flask_marshmallow import Marshmallow
from flask_principal import Principal, Permission, RoleNeed
from flask_oauthlib.client import OAuth
from flask_restful import Api
from flask_socketio import SocketIO

# Create extension instances
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
migrate = Migrate()
cache = Cache()
scheduler = APScheduler()
login_manager = LoginManager()

# User loader will be registered in init_app to avoid circular imports
csrf = CSRFProtect()
babel = Babel()

# Export extensions for app initialization
__all__ = [
    'db', 'jwt', 'mail', 'migrate', 'cache', 
    'scheduler', 'login_manager', 'csrf', 'babel',
    'init_app', 'get_extension'
]

# Will store the bound Flask application instance once `init_app` is called
app = None

def init_app(app_):
    print('DEBUG: extensions.init_app called')
    app_.logger.info('DEBUG: extensions.init_app called, initializing login_manager')
    global app
    
    # Store the app instance
    app = app_
    
    # Configure the user_loader after the app context is available
    @login_manager.user_loader
    def load_user(user_id):
        try:
            from app.models.admin import AdminUser
            from app.models.user import User
            
            # First try to load as AdminUser
            admin = AdminUser.query.get(int(user_id))
            if admin:
                app_.logger.debug(f"[AUTH] Loaded admin user: {admin.username}")
                return admin
                
            # If not an admin, try to load as regular User
            user = User.query.get(int(user_id))
            if user:
                app_.logger.debug(f"[AUTH] Loaded regular user: {user.username}")
            return user
                
        except Exception as e:
            import traceback
            app_.logger.error(f"Error loading user {user_id}: {e}")
            app_.logger.error(traceback.format_exc())
            return None
    
    # Initialize SQLAlchemy only if not already registered
    if not getattr(app, "extensions", None) or 'sqlalchemy' not in app.extensions:
        db.init_app(app)
    
    # Initialize other extensions
    jwt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    # Defensive fix for Flask-Caching: ensure app.extensions['cache'] is not a Cache object
    if getattr(app, 'extensions', None) and 'cache' in app.extensions and not isinstance(app.extensions['cache'], dict):
        del app.extensions['cache']
    cache.init_app(app)
    
    # Configure scheduler
    scheduler.init_app(app)
    if not scheduler.running:
        scheduler.start()
    
    login_manager.init_app(app)
    csrf.init_app(app)
    # Initialize Babel
    babel.init_app(app)
    
    # Configure Babel locale selector
    @babel.localeselector
    def get_locale():
        from flask import request, session
        languages = app.config.get('LANGUAGES', {'en': 'English', 'tr': 'Türkçe', 'ru': 'Русский'})
        if 'language' in session and session['language'] in languages:
            return session['language']
        lang = request.args.get('lang')
        if lang and lang in languages:
            session['language'] = lang
            return lang
        return request.accept_languages.best_match(languages.keys()) or 'en'
    
    # Set default languages if not configured
    if 'LANGUAGES' not in app.config:
        app.config['LANGUAGES'] = {'en': 'English', 'tr': 'Türkçe', 'ru': 'Русский'}
        
    # Add get_locale to template context
    @app.context_processor
    def inject_get_locale():
        return dict(get_locale=get_locale)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    

    # Initialize CSRF protection
    try:
        # Configure CSRF protection with session settings
        app.config['WTF_CSRF_ENABLED'] = True
        app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
        app.config['WTF_CSRF_SSL_STRICT'] = False  # Allow CSRF protection on non-HTTPS
        app.config['WTF_CSRF_CHECK_DEFAULT'] = True  # Enable CSRF checking by default
        
        # Initialize CSRF protection
        csrf.init_app(app)
        
        # Set up CSRF error handler
        @app.errorhandler(400)
        def handle_csrf_error(e):
            app.logger.warning(f"CSRF Error: {e}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'status': 'error',
                    'message': 'CSRF token validation failed. Please refresh the page and try again.'
                }), 400
                
            try:
                return render_template('error/400.html', 
                                    error="Your session has expired. Please refresh the page and try again.",
                                    title="Session Expired"), 400
            except Exception as render_error:
                app.logger.error(f"Error rendering 400 template: {render_error}")
                return """
                <h1>Session Expired</h1>
                <p>Your session has expired. Please refresh the page and try again.</p>
                <p><a href="/">Return to Home</a></p>
                """, 400
                                 
        app.logger.debug("[SECURITY] CSRF protection initialized with enhanced settings")
    except Exception as e:
        app.logger.critical(f"[SECURITY] Failed to initialize CSRF protection: {e}")
        raise

    # Store references on the app for convenient lookup elsewhere
    app.extensions = getattr(app, "extensions", {})
    app.extensions.update({
        'sqlalchemy': db,
        'jwt': jwt,
        'mail': mail,
        'cache': cache,
        'scheduler': scheduler,
        'login_manager': login_manager,
        'csrf': csrf,
        'babel': babel,
    })

# Make extensions available through app.extensions
def get_extension(name):
    """Get an extension instance from app.extensions"""
    if app is None:
        raise RuntimeError("Extensions not initialized. Call init_app() first.")
    return app.extensions.get(name)

# Add extension getters for convenience
get_db = lambda: get_extension('sqlalchemy')
get_jwt = lambda: get_extension('jwt')
get_mail = lambda: get_extension('mail')
get_migrate = lambda: get_extension('migrate')
get_cache = lambda: get_extension('cache')
get_scheduler = lambda: get_extension('scheduler')
