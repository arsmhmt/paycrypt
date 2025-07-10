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
    MAIL_USERNAME = 'paycryptonline@proton.me'
    import os
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')

    # Babel Configuration
    LANGUAGES = {
        'en': 'English',
        'tr': 'Türkçe',
        'ru': 'Русский'
    }
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'

    # Coin Configuration
    COIN_LIST = [
        'BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'XRP', 'SOL', 'DOGE', 'TRX',
        'ADA', 'LTC', 'AVAX', 'MATIC', 'SHIB', 'DOT',  # First 15 (Starter)
        'LINK', 'XLM', 'DAI', 'ARB', 'OP',             # Next 5 (Business)
        'TON', 'CRO', 'FTM', 'APE', 'BCH'              # All 25 (Enterprise)
    ]

    PACKAGE_COIN_LIMITS = {
        'starter_flat_rate': 15,
        'business_flat_rate': 20,
        'enterprise_flat_rate': 25
    }

    COIN_DISPLAY_NAMES = {
        'BTC': 'Bitcoin',
        'ETH': 'Ethereum',
        'USDT': 'Tether',
        'USDC': 'USD Coin',
        'BNB': 'Binance Coin',
        'XRP': 'Ripple',
        'SOL': 'Solana',
        'DOGE': 'Dogecoin',
        'TRX': 'TRON',
        'ADA': 'Cardano',
        'LTC': 'Litecoin',
        'AVAX': 'Avalanche',
        'MATIC': 'Polygon',
        'SHIB': 'Shiba Inu',
        'DOT': 'Polkadot',
        'LINK': 'Chainlink',
        'XLM': 'Stellar',
        'DAI': 'Dai',
        'ARB': 'Arbitrum',
        'OP': 'Optimism',
        'TON': 'Toncoin',
        'CRO': 'Cronos',
        'FTM': 'Fantom',
        'APE': 'ApeCoin',
        'BCH': 'Bitcoin Cash'
    }

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