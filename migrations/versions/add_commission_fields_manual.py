"""
Add commission fields to Client model

Revision ID: add_commission_fields_manual
Revises: 
Create Date: 2025-06-28 23:06:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_commission_fields_manual'
down_revision = 'add_client_commission_rates'
branch_labels = None
depends_on = None

def upgrade():
    # Add commission fields
    op.add_column('clients', sa.Column('deposit_commission', sa.Numeric(precision=5, scale=4), nullable=False, server_default='0.035'))
    op.add_column('clients', sa.Column('withdrawal_commission', sa.Numeric(precision=5, scale=4), nullable=False, server_default='0.015'))
    op.add_column('clients', sa.Column('deposit_commission_rate', sa.Float(), nullable=False, server_default='0.035'))
    op.add_column('clients', sa.Column('withdrawal_commission_rate', sa.Float(), nullable=False, server_default='0.015'))
    op.add_column('clients', sa.Column('balance', sa.Numeric(precision=18, scale=8), nullable=False, server_default='0'))

def downgrade():
    # Remove commission fields
    op.drop_column('clients', 'balance')
    op.drop_column('clients', 'withdrawal_commission_rate')
    op.drop_column('clients', 'deposit_commission_rate')
    op.drop_column('clients', 'withdrawal_commission')
    op.drop_column('clients', 'deposit_commission')
