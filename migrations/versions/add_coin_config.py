"""Add coin configuration

Revision ID: 1234abcd5678
Revises: previous_migration_id
Create Date: 2025-07-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1234abcd5678'
down_revision = 'previous_migration_id'
branch_labels = None
depends_on = None

def upgrade():
    # Add coin column to transactions table if it doesn't exist
    op.add_column('transactions', sa.Column('coin', sa.String(10), nullable=True))
    
    # Create index on coin column for faster lookups
    op.create_index(op.f('ix_transactions_coin'), 'transactions', ['coin'], unique=False)
    
    # Create a table to store coin metadata if it doesn't exist
    op.create_table(
        'coin_metadata',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(10), nullable=False, unique=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('decimals', sa.Integer(), default=8, nullable=False),
        sa.Column('min_confirmations', sa.Integer(), default=6, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Insert initial coin data
    op.bulk_insert(
        sa.table('coin_metadata',
            sa.column('symbol', sa.String),
            sa.column('name', sa.String),
            sa.column('is_active', sa.Boolean),
            sa.column('decimals', sa.Integer),
            sa.column('min_confirmations', sa.Integer)
        ),
        [
            {'symbol': 'BTC', 'name': 'Bitcoin', 'is_active': True, 'decimals': 8, 'min_confirmations': 6},
            {'symbol': 'ETH', 'name': 'Ethereum', 'is_active': True, 'decimals': 18, 'min_confirmations': 12},
            {'symbol': 'USDT', 'name': 'Tether', 'is_active': True, 'decimals': 6, 'min_confirmations': 12},
            {'symbol': 'USDC', 'name': 'USD Coin', 'is_active': True, 'decimals': 6, 'min_confirmations': 12},
            {'symbol': 'BNB', 'name': 'Binance Coin', 'is_active': True, 'decimals': 18, 'min_confirmations': 12},
            {'symbol': 'XRP', 'name': 'Ripple', 'is_active': True, 'decimals': 6, 'min_confirmations': 1},
            {'symbol': 'SOL', 'name': 'Solana', 'is_active': True, 'decimals': 9, 'min_confirmations': 32},
            {'symbol': 'DOGE', 'name': 'Dogecoin', 'is_active': True, 'decimals': 8, 'min_confirmations': 30},
            {'symbol': 'TRX', 'name': 'TRON', 'is_active': True, 'decimals': 6, 'min_confirmations': 20},
            {'symbol': 'ADA', 'name': 'Cardano', 'is_active': True, 'decimals': 6, 'min_confirmations': 15},
            {'symbol': 'LTC', 'name': 'Litecoin', 'is_active': True, 'decimals': 8, 'min_confirmations': 6},
            {'symbol': 'AVAX', 'name': 'Avalanche', 'is_active': True, 'decimals': 18, 'min_confirmations': 30},
            {'symbol': 'MATIC', 'name': 'Polygon', 'is_active': True, 'decimals': 18, 'min_confirmations': 128},
            {'symbol': 'SHIB', 'name': 'Shiba Inu', 'is_active': True, 'decimals': 18, 'min_confirmations': 12},
            {'symbol': 'DOT', 'name': 'Polkadot', 'is_active': True, 'decimals': 10, 'min_confirmations': 12},
            {'symbol': 'LINK', 'name': 'Chainlink', 'is_active': True, 'decimals': 18, 'min_confirmations': 12},
            {'symbol': 'XLM', 'name': 'Stellar', 'is_active': True, 'decimals': 7, 'min_confirmations': 1},
            {'symbol': 'DAI', 'name': 'Dai', 'is_active': True, 'decimals': 18, 'min_confirmations': 12},
            {'symbol': 'ARB', 'name': 'Arbitrum', 'is_active': True, 'decimals': 18, 'min_confirmations': 12},
            {'symbol': 'OP', 'name': 'Optimism', 'is_active': True, 'decimals': 18, 'min_confirmations': 12},
            {'symbol': 'TON', 'name': 'Toncoin', 'is_active': True, 'decimals': 9, 'min_confirmations': 1},
            {'symbol': 'CRO', 'name': 'Cronos', 'is_active': True, 'decimals': 8, 'min_confirmations': 12},
            {'symbol': 'FTM', 'name': 'Fantom', 'is_active': True, 'decimals': 18, 'min_confirmations': 12},
            {'symbol': 'APE', 'name': 'ApeCoin', 'is_active': True, 'decimals': 18, 'min_confirmations': 12},
            {'symbol': 'BCH', 'name': 'Bitcoin Cash', 'is_active': True, 'decimals': 8, 'min_confirmations': 6},
        ]
    )

def downgrade():
    # Drop the index and column
    op.drop_index(op.f('ix_transactions_coin'), table_name='transactions')
    op.drop_column('transactions', 'coin')
    
    # Drop the coin_metadata table
    op.drop_table('coin_metadata')
