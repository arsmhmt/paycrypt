"""Add first_name and last_name to users table

Revision ID: 20250707_add_first_last_name
Revises: 20250707_add_slug_constraint
Create Date: 2025-07-07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250707_add_first_last_name'
down_revision = '20250707_add_slug_constraint'
branch_labels = None
depends_on = None


def upgrade():
    # Add first_name and last_name columns to users table
    op.add_column('users', sa.Column('first_name', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(length=64), nullable=True))


def downgrade():
    # Drop the columns if we need to rollback
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
