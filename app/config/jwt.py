import os
from datetime import timedelta

JWT_CONFIG = {
    'JWT_SECRET_KEY': os.environ.get('JWT_SECRET_KEY', 'your-secret-key-here'),
    'JWT_ACCESS_TOKEN_EXPIRES': timedelta(minutes=15),
    'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=30),
    'JWT_TOKEN_LOCATION': ['cookies'],
    'JWT_COOKIE_SECURE': False,  # Set to True in production
    'JWT_COOKIE_CSRF_PROTECT': True,
    'JWT_ACCESS_COOKIE_NAME': 'access_token_cookie',
    'JWT_REFRESH_COOKIE_NAME': 'refresh_token_cookie',
    'JWT_COOKIE_SAMESITE': 'Lax'
}
