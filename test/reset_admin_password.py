from app import create_app
from app.models.admin import AdminUser
from app.extensions import db

NEW_PASSWORD = "Paycrypt2025!"

app = create_app()

with app.app_context():
    admin = AdminUser.query.filter_by(username="paycrypt").first()
    if not admin:
        print("Admin user 'paycrypt' not found.")
    else:
        admin.set_password(NEW_PASSWORD)
        db.session.commit()
        print(f"Password for 'paycrypt' reset to: {NEW_PASSWORD}")
