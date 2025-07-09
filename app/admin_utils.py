from app.extensions import db
from app.models.user import User
from app.models.client import Client
from app.utils.email import send_verification_email

def delete_user_by_username(username):
    """Delete a user and their client by username."""
    user = User.query.filter_by(username=username).first()
    if not user:
        return f"No user found with username: {username}"
    # Delete client if exists
    if user.client:
        db.session.delete(user.client)
    db.session.delete(user)
    db.session.commit()
    return f"User '{username}' and their client deleted."

def resend_verification(username):
    """Resend verification email to user by username if not verified."""
    user = User.query.filter_by(username=username).first()
    if not user:
        return f"No user found with username: {username}"
    if user.is_verified:
        return f"User '{username}' is already verified."
    send_verification_email(user)
    return f"Verification email resent to {user.email}."
