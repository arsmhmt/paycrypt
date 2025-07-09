class Config:
    # Safe default cache config for Flask-Caching
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    SECRET_KEY = 'your-secret-key'
    # SQLALCHEMY_DATABASE_URI is set in the app factory to ensure correct path
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail Configuration
    MAIL_DEFAULT_SENDER = 'paycryptonline@proton.me'
    MAIL_SERVER = 'smtp.protonmail.ch'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'paycryptonline@proton.me'  # Set your ProtonMail username
    import os
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')  # Set your mail password in environment variable MAIL_PASSWORD

    # Usage for developers:
    # To use this configuration, set the MAIL_PASSWORD environment variable before running the application.
    # For example, on Linux or macOS, you can run the following command:
    # export MAIL_PASSWORD='your_mail_password'
    # On Windows, you can run the following command:
    # set MAIL_PASSWORD='your_mail_password'

    # Babel Configuration
    LANGUAGES = {
        'en': 'English',
        'tr': 'Türkçe',
        'ru': 'Русский'
    }
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    # ... other config ...

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

JWT_CONFIG = {
    # ... your JWT config ...
}