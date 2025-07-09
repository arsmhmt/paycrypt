"""Add fiat to crypto conversion fields

Revision ID: 1234abcd5678
Revises: 
Create Date: 2025-06-27 00:32:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1234abcd5678'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Get current connection
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = [col['name'] for col in inspector.get_columns('payments')]
    
    # Add new columns only if they don't exist
    if 'fiat_amount' not in existing_columns:
        op.add_column('payments', sa.Column('fiat_amount', sa.Numeric(precision=18, scale=2), nullable=True))
    if 'fiat_currency' not in existing_columns:
        op.add_column('payments', sa.Column('fiat_currency', sa.String(length=5), nullable=True))
    if 'crypto_amount' not in existing_columns:
        op.add_column('payments', sa.Column('crypto_amount', sa.Numeric(precision=18, scale=8), nullable=True))
    if 'crypto_currency' not in existing_columns:
        op.add_column('payments', sa.Column('crypto_currency', sa.String(length=5), server_default='BTC', nullable=True))
    if 'exchange_rate' not in existing_columns:
        op.add_column('payments', sa.Column('exchange_rate', sa.Numeric(precision=18, scale=8), nullable=True))
    if 'rate_expiry' not in existing_columns:
        op.add_column('payments', sa.Column('rate_expiry', sa.DateTime(), nullable=True))
    if 'expires_at' not in existing_columns:
        op.add_column('payments', sa.Column('expires_at', sa.DateTime(), nullable=True))
    
    # Update existing records to set default values for legacy fields
    op.execute("""
        UPDATE payments 
        SET 
            crypto_amount = amount,
            crypto_currency = 'BTC',
            fiat_currency = 'USD',
            fiat_amount = amount * 60000  -- Default rate for backward compatibility
        WHERE crypto_amount IS NULL
    """)
    
    # Make amount and currency nullable (they are now legacy fields)
    # Only alter if needed - this might fail if already done
    try:
        op.alter_column('payments', 'amount', existing_type=sa.FLOAT(), nullable=True)
    except:
        pass  # Column might already be nullable
    
    try:
        op.alter_column('payments', 'currency', existing_type=sa.VARCHAR(length=3), type_=sa.String(length=10), nullable=True)
    except:
        pass  # Column might already be modified

def downgrade():
    # Copy data back to legacy fields before dropping
    op.execute("""
        UPDATE payments 
        SET 
            amount = crypto_amount,
            currency = COALESCE(crypto_currency, 'BTC')
        WHERE amount IS NULL
    """)
    
    # Make amount and currency non-nullable again
    op.alter_column('payments', 'currency', existing_type=sa.String(length=10), type_=sa.VARCHAR(length=3), nullable=False)
    op.alter_column('payments', 'amount', existing_type=sa.FLOAT(), nullable=False)
    
    # Drop the new columns
    op.drop_column('payments', 'expires_at')
    op.drop_column('payments', 'rate_expiry')
    op.drop_column('payments', 'exchange_rate')
    op.drop_column('payments', 'crypto_currency')
    op.drop_column('payments', 'crypto_amount')
    op.drop_column('payments', 'fiat_currency')
    op.drop_column('payments', 'fiat_amount')
