import os
import sys
from datetime import datetime
from flask import Flask
from flask_migrate import Migrate
from sqlalchemy import Enum

# Import the application factory and db from the main package
from . import create_app
from app.extensions import db

# Create the application
app = create_app()

# Define models locally to avoid circular imports
class PaymentStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=True)
    coin = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    order_id = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    confirmations = db.Column(db.Integer, default=0)
    confirmed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    qr_code_path = db.Column(db.String(255), nullable=True)

class Client(db.Model):
    __tablename__ = 'client'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=True)
    password_hash = db.Column(db.String(200), nullable=True)
    api_key = db.Column(db.String(64), unique=True, nullable=False, default=lambda: secrets.token_hex(32))
    rate_limit = db.Column(db.Integer, default=1000)
    callback_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payments = db.relationship('Payment', backref='client_rel', lazy=True)

class Withdrawal(db.Model):
    __tablename__ = 'withdrawal'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    coin = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    tx_hash = db.Column(db.String(100), nullable=True)

class AdminUser(db.Model):
    __tablename__ = 'admin_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

# Import the rest after defining models to avoid circular imports
from app import create_app, db

def create_tables():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    with app.app_context():
        create_tables()
