from datetime import datetime
from enum import Enum
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, func
from ..extensions import db
from .base import BaseModel
from app.utils.crypto import validate_crypto_address

class WithdrawalStatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

class WithdrawalType(Enum):
    USER_REQUEST = 'user_request'      # B2C - Users withdrawing from client platforms  
    CLIENT_BALANCE = 'client_balance'  # B2B - Clients withdrawing their net balances

class WithdrawalRequest(BaseModel):
    __tablename__ = 'withdrawal_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    crypto_address = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Enum(WithdrawalStatus), default=WithdrawalStatus.PENDING)
    withdrawal_type = db.Column(db.Enum(WithdrawalType), default=WithdrawalType.USER_REQUEST)
    
    # Administrative fields
    approved_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    approved_at = db.Column(db.DateTime)
    rejected_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    rejected_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    # Fee information
    fee = db.Column(db.Float, default=0.0)
    net_amount = db.Column(db.Float)  # Amount after fees
    
    # User information (for user withdrawals)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # For B2C withdrawals
    user_wallet_address = db.Column(db.String(100))  # User's destination wallet
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', back_populates='withdrawal_requests')
    user = db.relationship('User', backref='withdrawal_requests')
    approved_by_admin = db.relationship('AdminUser', foreign_keys=[approved_by], backref='approved_withdrawals')
    rejected_by_admin = db.relationship('AdminUser', foreign_keys=[rejected_by], backref='rejected_withdrawals')
    
    # Relationship with Withdrawal
    withdrawal = db.relationship('Withdrawal', back_populates='request', uselist=False)
    
    def validate(self):
        if not validate_crypto_address(self.crypto_address, self.currency):
            raise ValueError(f"Invalid {self.currency} address")
        if self.amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        return True

class Withdrawal(BaseModel):
    __tablename__ = 'withdrawals'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('withdrawal_requests.id'), nullable=False)
    transaction_hash = db.Column(db.String(100))
    status = db.Column(db.Enum(WithdrawalStatus), default=WithdrawalStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    request = db.relationship('WithdrawalRequest', back_populates='withdrawal')
    
    # Relationship with Client
    client = db.relationship('Client', back_populates='withdrawals')

    def process(self):
        """Process withdrawal request"""
        if self.status != WithdrawalStatus.APPROVED:
            raise ValueError("Withdrawal must be approved first")
            
        # TODO: Implement actual crypto transfer
        # This would typically use a crypto wallet API (e.g., Binance)
        
        self.status = WithdrawalStatus.PROCESSING
        self.processed_at = datetime.utcnow()
        db.session.commit()
    
    def complete(self, tx_hash):
        """Mark withdrawal as completed"""
        self.status = WithdrawalStatus.COMPLETED
        self.tx_hash = tx_hash
        self.processed_at = datetime.utcnow()
        db.session.commit()
    
    def reject(self, reason):
        """Reject withdrawal request"""
        self.status = WithdrawalStatus.REJECTED
        self.rejection_reason = reason
        self.processed_at = datetime.utcnow()
        db.session.commit()

def get_client_balance(client_id):
    """Calculate client's available balance"""
    from .payment import Payment  # Import here to avoid circular imports
    
    # Get total deposits
    total_in = db.session.query(func.sum(Payment.amount)).filter_by(
        client_id=client_id,
        status='completed'
    ).scalar() or 0
    
    # Get total withdrawals
    total_out = db.session.query(func.sum(WithdrawalRequest.amount)).filter_by(
        client_id=client_id,
        status='completed'
    ).scalar() or 0
    
    # Get total commissions
    commission = db.session.query(func.sum(Payment.commission)).filter_by(
        client_id=client_id,
        status='completed'
    ).scalar() or 0
    
    return total_in - total_out - commission
