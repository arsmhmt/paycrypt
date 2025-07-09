"""
Flask extensions initialization.

This module initializes all Flask extensions and makes them available for import.
To avoid circular imports, extensions are initialized in the application factory.
"""
from .extensions import (
    db, jwt, mail, migrate, cache, scheduler, login_manager, csrf, babel,
    init_app as _init_extensions, get_extension
)

# Re-export extensions for easier access
__all__ = [
    'db', 'jwt', 'mail', 'migrate', 'cache', 
    'scheduler', 'login_manager', 'csrf', 'babel',
    'init_extensions', 'get_extension'
]

def init_extensions(app):
    """
    Initialize all Flask extensions with the given app instance.
    
    Args:
        app: Flask application instance
    """
    # Initialize all extensions using the centralized init_app
    _init_extensions(app)
    
    # Configure JWT from the app's config
    from .extensions import jwt
    jwt.init_app(app)
    
    # Configure other extensions
    from .extensions import mail, migrate, cache, scheduler, login_manager, csrf, babel
    
    mail.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    scheduler.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    babel.init_app(app)
    
    # Configure babel
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
    
    return {
        'db': db,
        'jwt': jwt,
        'mail': mail,
        'cache': cache,
        'scheduler': scheduler,
        'login_manager': login_manager,
        'csrf': csrf,
        'babel': babel
    }

# Make extensions available through app.extensions
def get_extension(name):
    return globals()[name]

# Export extension getters for convenience
def get_db():
    return get_extension('db')

def get_jwt():
    return get_extension('jwt')

def get_mail():
    return get_extension('mail')

def get_cache():
    return get_extension('cache')

def get_scheduler():
    return get_extension('scheduler')

def get_login_manager():
    return get_extension('login_manager')