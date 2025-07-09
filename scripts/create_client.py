from app import db, create_app
from app.models import Payment, Client

# Create and configure the Flask app
app = create_app()

# Create database tables
with app.app_context():
    db.create_all()

# Create a new client within the app context
with app.app_context():
    client = Client(name="Test Client")
    db.session.add(client)
    db.session.commit()
    print("API Key:", client.api_key)
