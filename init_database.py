from app import create_app
from app.extensions.extensions import db

def init_db():
    """Initialize the database."""
    app = create_app()
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    init_db()
