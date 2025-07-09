"""Add slug column to client_packages

Revision ID: 20250707_add_slug
Revises: c13e49ad83e4
Create Date: 2025-07-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250707_add_slug'
down_revision = 'c13e49ad83e4'  # Current version in your database
branch_labels = None
depends_on = None


def upgrade():
    # Add the slug column
    op.add_column('client_packages', 
                 sa.Column('slug', sa.String(length=100), nullable=True))
    
    # Create a unique index for the slug+client_type combination
    op.create_index('uq_package_slug_type', 'client_packages', 
                   ['slug', 'client_type'],
                   unique=True,
                   postgresql_where=sa.text('slug IS NOT NULL'))


def downgrade():
    # Drop the index first
    op.drop_index('uq_package_slug_type', table_name='client_packages')
    
    # Then drop the column
    with op.batch_alter_table('client_packages') as batch_op:
        batch_op.drop_column('slug')
