"""Add unique constraint for slug and client_type in client_packages

Revision ID: 20250707_add_slug_constraint
Revises: c13e49ad83e4
Create Date: 2025-07-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250707_add_slug_constraint'
down_revision = 'c13e49ad83e4'  # Current version in your database
branch_labels = None
depends_on = None


def upgrade():
    # Create a unique constraint for slug and client_type
    op.create_unique_constraint(
        'uq_package_slug_type',
        'client_packages',
        ['slug', 'client_type'],
        postgresql_where=sa.text('slug IS NOT NULL')
    )


def downgrade():
    # Drop the constraint
    op.drop_constraint('uq_package_slug_type', 'client_packages', type_='unique')
