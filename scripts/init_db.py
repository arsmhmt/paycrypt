import os
import sys
import json
from werkzeug.security import generate_password_hash
from flask_migrate import upgrade

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app and models
from app import create_app
from app.extensions import db
from app.models import Client, User

app = create_app()

with app.app_context():
    # Upgrade database to latest version
    upgrade()
    
    # Create admin user if not exists
    admin = User.query.filter_by(email='admin@paycrypt.online').first()
    if not admin:
        admin = User(
            email='admin@paycrypt.online',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created")
    else:
        print("Admin user already exists")

    print("Database initialized successfully")
