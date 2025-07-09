from app import create_app, db
from app.models import Client

app = create_app()

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    
    print("Creating all tables...")
    db.create_all()
    
    print("Marking migration as up-to-date...")
    from flask_migrate import stamp
    stamp()
    
    print("Database repaired successfully!")
