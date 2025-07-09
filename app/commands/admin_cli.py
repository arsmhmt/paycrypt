"""
Admin CLI commands for the application.
"""
import click
from flask.cli import with_appcontext
from app.extensions import db
from app.models import AdminUser, User, Client, AuditTrail

def register_admin_commands(app):
    """Register admin CLI commands with the Flask application."""
    @app.cli.group()
    def admin():
        """Admin management commands."""
        pass

    @admin.command('create')
    @click.argument('username')
    @click.argument('email')
    @click.argument('password')
    @with_appcontext
    def create_admin(username, email, password):
        """Create a new admin user."""
        from werkzeug.security import generate_password_hash
        
        if AdminUser.query.filter_by(username=username).first():
            click.echo(f'Error: Username {username} is already taken.')
            return
            
        if AdminUser.query.filter_by(email=email).first():
            click.echo(f'Error: Email {email} is already registered.')
            return
            
        admin = AdminUser(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_active=True,
            is_superuser=True
        )
        
        db.session.add(admin)
        db.session.commit()
        
        click.echo(f'Admin user {username} created successfully.')
        
    return admin