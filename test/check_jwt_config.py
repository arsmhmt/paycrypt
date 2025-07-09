import os
import sys
from flask import Flask
from flask_jwt_extended import JWTManager

def check_jwt_config():
    """Check JWT configuration and print details"""
    print("\n=== JWT Configuration Check ===\n")
    
    # Create a minimal Flask app
    app = Flask(__name__)
    
    # Load configuration
    try:
        from app.config import Config
        app.config.from_object(Config)
        print("✅ Loaded configuration from app.config.Config")
    except ImportError as e:
        print(f"❌ Failed to import config: {str(e)}")
        return False
    
    # Check required JWT settings
    required_settings = [
        'JWT_SECRET_KEY',
        'JWT_ACCESS_TOKEN_EXPIRES',
        'JWT_TOKEN_LOCATION',
        'JWT_COOKIE_SECURE',
        'JWT_COOKIE_HTTPONLY',
        'JWT_COOKIE_SAMESITE'
    ]
    
    all_settings_ok = True
    
    for setting in required_settings:
        try:
            value = app.config.get(setting)
            if value is None:
                print(f"❌ {setting}: Not set")
                all_settings_ok = False
            else:
                print(f"✅ {setting}: {value}")
        except Exception as e:
            print(f"❌ Error checking {setting}: {str(e)}")
            all_settings_ok = False
    
    # Initialize JWT and check for any initialization errors
    try:
        jwt = JWTManager()
        jwt.init_app(app)
        print("\n✅ JWT initialized successfully")
    except Exception as e:
        print(f"\n❌ Failed to initialize JWT: {str(e)}")
        all_settings_ok = False
    
    return all_settings_ok

if __name__ == "__main__":
    print("Starting JWT configuration check...")
    try:
        if check_jwt_config():
            print("\n✅ JWT configuration looks good!")
            sys.exit(0)
        else:
            print("\n❌ JWT configuration has issues. Please check above for details.")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during JWT configuration check: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
