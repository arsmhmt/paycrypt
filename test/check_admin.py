from app import create_app
from app.models.admin import AdminUser
from app.extensions import db

# Create app context
app = create_app()

# Check both admin users
with app.app_context():
    # Check paycrypt admin
    paycrypt = AdminUser.query.filter_by(username='paycrypt').first()
    if paycrypt:
        print(f"\nPaycrypt admin user:")
        print(f"Username: {paycrypt.username}")
        print(f"is_superuser: {paycrypt.is_superuser}")
        print(f"is_active: {paycrypt.is_active}")
    
    # Check testadmin
    testadmin = AdminUser.query.filter_by(username='testadmin').first()
    if testadmin:
        print(f"\nTestadmin user:")
        print(f"Username: {testadmin.username}")
        print(f"is_superuser: {testadmin.is_superuser}")
        print(f"is_active: {testadmin.is_active}")
    
    # Update testadmin if needed
    if testadmin and not testadmin.is_superuser:
        print("\nUpdating testadmin to superuser...")
        testadmin.is_superuser = True
        db.session.commit()
        print("Updated testadmin is_superuser to True")
