from app import create_app, db
from app.models.admin import AdminUser

app = create_app()

with app.app_context():
    # Find the existing admin user
    admin = AdminUser.query.filter_by(username='paycrypt').first()
    if admin:
        print(f"Found admin user: {admin.username}")
        print(f"Current password hash: {admin.password_hash}")
        
        # Update the password
        admin.set_password('Aylin*2024+')
        db.session.commit()
        
        print("Password updated successfully!")
        print(f"New password hash: {admin.password_hash}")
    else:
        print("Admin user not found. Creating new admin user...")
        admin = AdminUser(
            username='paycrypt',
            email='admin@paycrypt.online',
            password='Aylin*2024+',
            is_superuser=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
