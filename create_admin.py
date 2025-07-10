from app import create_app, db
from app.models.admin import AdminUser

app = create_app()

with app.app_context():
    # Check if admin user already exists
    admin = AdminUser.query.filter_by(username='admin').first()
    if admin:
        print("Admin user already exists. Updating password...")
        admin.set_password('Aylin*2024+')
    else:
        print("Creating new admin user...")
        admin = AdminUser(
            username='admin',
            email='admin@paycrypt.online',
            password='Aylin*2024+',
            is_superuser=True
        )
        db.session.add(admin)
    
    db.session.commit()
    print("Admin user created/updated successfully!")
