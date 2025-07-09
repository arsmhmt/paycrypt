from app import create_app, db
from app.models.admin import AdminUser

def create_admin_user():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin = AdminUser.query.filter_by(username='testadmin').first()
        if not admin:
            admin = AdminUser(
                username='testadmin',
                email='testadmin@example.com',
                password='testpass123',
                first_name='Test',
                last_name='Admin',
                is_active=True,
                is_superuser=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Test admin user created successfully!")
            print(f"Username: testadmin")
            print(f"Password: testpass123")
        else:
            print("ℹ️  Test admin user already exists")
            print(f"Username: {admin.username}")
            print("To reset the password, run this in Python shell:")
            print(f"admin = AdminUser.query.filter_by(username='testadmin').first()")
            print("admin.set_password('new_password')")
            print("db.session.commit()")

if __name__ == "__main__":
    create_admin_user()
