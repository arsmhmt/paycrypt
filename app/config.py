"""
Application configuration settings.

This module contains the base configuration class and environment-specific
configuration subclasses. It also includes a configuration dictionary for
loading the appropriate configuration based on the FLASK_ENV environment variable.
"""
import os
from datetime import timedelta
from pathlib import Path

class Config:
    """Base configuration class. Contains settings common to all environments."""
    # App settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123'
    APP_NAME = 'Crypto Payment Gateway'
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5000')
    
    # Database settings
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{os.path.join(basedir, "instance", "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True in DevelopmentConfig if needed
    
    # Ensure instance and uploads directories exist
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
    
    # Session settings
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-123'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = False  # Set to True in production with HTTPS
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ACCESS_COOKIE_NAME = 'access_token_cookie'
    JWT_REFRESH_COOKIE_NAME = 'refresh_token_cookie'
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_COOKIE_HTTPONLY = True  # Prevent XSS
    JWT_SESSION_COOKIE = False  # Don't make the cookie session-only
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/auth/refresh'
    JWT_CSRF_IN_COOKIES = False  # Don't set CSRF in cookies
    JWT_ACCESS_CSRF_HEADER_NAME = 'X-CSRF-TOKEN'
    JWT_REFRESH_CSRF_HEADER_NAME = 'X-CSRF-REFRESH-TOKEN'
    JWT_ACCESS_CSRF_FIELD_NAME = 'csrf_token'
    JWT_REFRESH_CSRF_FIELD_NAME = 'csrf_token'
    
    # CSRF settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Email settings
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    
    # Admin settings
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    
    # Security settings
    # Security settings - non-guessable admin path for protection against bots/scanners
    ADMIN_SECRET_PATH = os.environ.get('ADMIN_SECRET_PATH', 'admin120724')  # Non-guessable default
    RATE_LIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    
    # Admin security settings
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_ATTEMPT_TIMEOUT = timedelta(minutes=15)
    ADMIN_SESSION_TIMEOUT = timedelta(hours=2)
    
    # Rate limiting
    RATELIMIT_DEFAULT = '200 per day;50 per hour'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Security
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', 'dev-password-salt-123')
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_CONFIRMABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    CORS_SUPPORTS_CREDENTIALS = True
    
    # API settings
    API_PREFIX = '/api/v1'
    
    # Cache settings
    CACHE_TYPE = 'simple'  # Can be 'redis', 'memcached', etc. in production
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Currency settings
    DEFAULT_CURRENCY = 'BTC'  # All totals and volumes should be displayed in BTC
    
    # Internationalization settings (Flask-Babel)
    LANGUAGES = {
        'en': 'English',
        'tr': 'Türkçe', 
        'ru': 'Русский'
    }
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    
    # Add any other common settings here
    
    @classmethod
    def init_app(cls, app):
        """Initialize configuration for the Flask app."""
        # Ensure upload folder exists
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        
        # Configure logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(cls.basedir, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # File handler for logs
        file_handler = RotatingFileHandler(
            os.path.join(logs_dir, 'app.log'),
            maxBytes=1024 * 1024 * 10,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = 'DEBUG'
    EXPLAIN_TEMPLATE_LOADING = False
    
    # Disable caching in development
    CACHE_TYPE = 'null'
    
    # Enable debug toolbar
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    
    # Show more detailed error messages
    TRAP_HTTP_EXCEPTIONS = True
    TRAP_BAD_REQUEST_ERRORS = True
    
    # Disable CSRF in development for easier testing
    WTF_CSRF_ENABLED = False
    
    # Allow all CORS in development
    CORS_ORIGINS = ['*']


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory SQLite for tests
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Disable mail sending during tests
    MAIL_SUPPRESS_SEND = True
    
    # Use a simpler password hashing for tests
    SECURITY_PASSWORD_HASH = 'plaintext'
    
    # Disable rate limiting in tests
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Security settings for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # JWT settings for production
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SAMESITE = 'Lax'
    
    # Enable CSRF protection in production
    WTF_CSRF_ENABLED = True
    
    # Use Redis for caching in production
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Email settings for production
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@yourdomain.com')
    
    # Log to stdout for production (handled by gunicorn)
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')
    
    @classmethod
    def init_app(cls, app):
        """Initialize configuration for the production app."""
        Config.init_app(app)
        
        # Log to stderr for production
        import logging
        from logging import StreamHandler
        
        stream_handler = StreamHandler()
        stream_handler.setLevel(logging.WARNING)
        app.logger.addHandler(stream_handler)


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# JWT configuration for Flask-JWT-Extended
JWT_CONFIG = {
    'JWT_SECRET_KEY': Config.JWT_SECRET_KEY,
    'JWT_ACCESS_TOKEN_EXPIRES': Config.JWT_ACCESS_TOKEN_EXPIRES,
    'JWT_REFRESH_TOKEN_EXPIRES': Config.JWT_REFRESH_TOKEN_EXPIRES,
    'JWT_TOKEN_LOCATION': Config.JWT_TOKEN_LOCATION,
    'JWT_COOKIE_SECURE': Config.JWT_COOKIE_SECURE,
    'JWT_COOKIE_CSRF_PROTECT': Config.JWT_COOKIE_CSRF_PROTECT,
    'JWT_ACCESS_COOKIE_NAME': Config.JWT_ACCESS_COOKIE_NAME,
    'JWT_REFRESH_COOKIE_NAME': Config.JWT_REFRESH_COOKIE_NAME,
    'JWT_COOKIE_SAMESITE': Config.JWT_COOKIE_SAMESITE,
    'JWT_COOKIE_HTTPONLY': Config.JWT_COOKIE_HTTPONLY,
    'JWT_SESSION_COOKIE': Config.JWT_SESSION_COOKIE,
    'JWT_ACCESS_COOKIE_PATH': Config.JWT_ACCESS_COOKIE_PATH,
    'JWT_REFRESH_COOKIE_PATH': Config.JWT_REFRESH_COOKIE_PATH,
    'JWT_CSRF_IN_COOKIES': Config.JWT_CSRF_IN_COOKIES,
    'JWT_ACCESS_CSRF_HEADER_NAME': Config.JWT_ACCESS_CSRF_HEADER_NAME,
    'JWT_REFRESH_CSRF_HEADER_NAME': Config.JWT_REFRESH_CSRF_HEADER_NAME,
    'JWT_ACCESS_CSRF_FIELD_NAME': Config.JWT_ACCESS_CSRF_FIELD_NAME,
    'JWT_REFRESH_CSRF_FIELD_NAME': Config.JWT_REFRESH_CSRF_FIELD_NAME
}

# File upload settings (moved to Config class)
# These are now defined in the Config class above

# Payment Provider Settings - Paycrypt's Own System
# We use our own integrated crypto payment system
# No external payment processors required
PAYCRYPT_PAYMENT_SYSTEM = True

# API Settings
API_RATE_LIMIT = os.getenv('API_RATE_LIMIT', '1000 per day')
API_KEY_LENGTH = 32
API_KEY_EXPIRY_DAYS = 90

# Notification Settings
DEFAULT_NOTIFICATION_METHOD = 'email'
NOTIFICATION_QUEUE_SIZE = 100

# Report Settings
REPORT_EXPORT_MAX_SIZE = 10 * 1024 * 1024  # 10MB max report size

# Recurring Payment Settings
RECURRING_PAYMENT_MAX_ATTEMPTS = 3
RECURRING_PAYMENT_RETRY_DELAY = timedelta(hours=24)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    JWT_COOKIE_SECURE = True
    
    def __init__(self):
        super().__init__()  # Important: call parent's __init__
        
        # In production, DATABASE_URL should be set in the environment
        if not os.getenv('DATABASE_URL'):
            raise ValueError('DATABASE_URL is required for production environment')
            
        # For backward compatibility, also support individual DB_* env vars
        if not self.SQLALCHEMY_DATABASE_URI and os.getenv('DB_USER') and os.getenv('DB_PASS') and os.getenv('DB_NAME') and os.getenv('CLOUD_SQL_CONNECTION_NAME'):
            self.SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@unix(/cloudsql/{os.getenv('CLOUD_SQL_CONNECTION_NAME')})/{os.getenv('DB_NAME')}"


# Config dictionary for Flask app
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
