"""Add currency models and multi-currency support

Revision ID: 20250701_add_currency_models
Revises: add_client_commission_rates
Create Date: 2025-07-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '20250701_add_currency_models'
down_revision = 'add_commission_fields_manual'
branch_labels = None
depends_on = None

def upgrade():
    # Get current connection
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Check existing tables
    existing_tables = inspector.get_table_names()
    
    # Create currencies table
    if 'currencies' not in existing_tables:
        op.create_table(
            'currencies',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('code', sa.String(10), unique=True, nullable=False),
            sa.Column('name', sa.String(50)),
            sa.Column('symbol', sa.String(10)),
            sa.Column('is_active', sa.Boolean, default=True)
        )
    
    # Create client_balances table
    if 'client_balances' not in existing_tables:
        op.create_table(
            'client_balances',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('client_id', sa.Integer, sa.ForeignKey('clients.id'), nullable=False),
            sa.Column('currency', sa.String(10), nullable=False),
            sa.Column('balance', sa.Float, default=0.0),
            sa.UniqueConstraint('client_id', 'currency', name='uix_client_currency')
        )
    
    # Create client_commissions table
    if 'client_commissions' not in existing_tables:
        op.create_table(
            'client_commissions',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('client_id', sa.Integer, sa.ForeignKey('clients.id'), nullable=False),
            sa.Column('currency', sa.String(10), nullable=False),
            sa.Column('deposit_commission_rate', sa.Float, default=0.0),
            sa.Column('withdrawal_commission_rate', sa.Float, default=0.0),
            sa.UniqueConstraint('client_id', 'currency', name='uix_commission_client_currency')
        )
    
    # Create currency_rates table
    if 'currency_rates' not in existing_tables:
        op.create_table(
            'currency_rates',
            sa.Column('currency', sa.String(10), primary_key=True),
            sa.Column('btc_rate', sa.Float, nullable=False),
            sa.Column('updated_at', sa.DateTime, default=datetime.utcnow)
        )
    
    # Add currency and btc_value columns to transactions table
    transactions_columns = [col['name'] for col in inspector.get_columns('transactions')]
    
    if 'currency' not in transactions_columns:
        op.add_column('transactions', sa.Column('currency', sa.String(10)))
    if 'btc_value' not in transactions_columns:
        op.add_column('transactions', sa.Column('btc_value', sa.Float, default=0.0))

def downgrade():
    # Get current connection
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Check existing columns in transactions table
    transactions_columns = [col['name'] for col in inspector.get_columns('transactions')]
    
    # Drop columns only if they exist
    if 'btc_value' in transactions_columns:
        op.drop_column('transactions', 'btc_value')
    if 'currency' in transactions_columns:
        op.drop_column('transactions', 'currency')
    
    # Check existing tables
    existing_tables = inspector.get_table_names()
    
    # Drop tables only if they exist
    if 'currency_rates' in existing_tables:
        op.drop_table('currency_rates')
    if 'client_commissions' in existing_tables:
        op.drop_table('client_commissions')
    if 'client_balances' in existing_tables:
        op.drop_table('client_balances')
    if 'currencies' in existing_tables:
        op.drop_table('currencies')
