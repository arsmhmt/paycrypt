# Script to reset the admin password for user 'paycrypt'
from app import create_app
from app.extensions import db
from app.models import AdminUser

app = create_app()

with app.app_context():
    admin = AdminUser.query.filter_by(username='paycrypt').first()
    if not admin:
        print('Admin user not found!')
    else:
        admin.set_password('Aylin2024++')
        db.session.commit()
        print('Password reset successfully for user: paycrypt')
