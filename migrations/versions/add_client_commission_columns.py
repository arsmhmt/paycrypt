"""
Add commission columns to clients table

Revision ID: add_client_commission_columns
Revises: 
Create Date: 2025-06-28 22:44:20
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_client_commission_columns'
down_revision = '1234abcd5678'
branch_labels = None
depends_on = None

def upgrade():
    # Add commission columns with default values
    op.add_column('clients', sa.Column('deposit_commission', sa.Numeric(precision=5, scale=4), nullable=False, server_default='0.035'))
    op.add_column('clients', sa.Column('withdrawal_commission', sa.Numeric(precision=5, scale=4), nullable=False, server_default='0.015'))
    op.add_column('clients', sa.Column('deposit_commission_rate', sa.Float(), nullable=False, server_default='0.035'))
    op.add_column('clients', sa.Column('withdrawal_commission_rate', sa.Float(), nullable=False, server_default='0.015'))

def downgrade():
    # Remove commission columns
    op.drop_column('clients', 'withdrawal_commission_rate')
    op.drop_column('clients', 'deposit_commission_rate')
    op.drop_column('clients', 'withdrawal_commission')
    op.drop_column('clients', 'deposit_commission')
