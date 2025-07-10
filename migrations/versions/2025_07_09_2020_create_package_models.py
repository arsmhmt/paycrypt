""create package models

Revision ID: 2025_07_09_2020
Revises: 
Create Date: 2025-07-09 20:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2025_07_09_2020'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create package_features table
    op.create_table('package_features',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False, index=True),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('is_parameterized', sa.Boolean(), nullable=False, server_default='f'),
        sa.Column('default_value', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='t'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create packages table
    op.create_table('packages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False, index=True),
        sa.Column('slug', sa.String(length=64), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='t'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='f'),
        sa.Column('price_monthly', sa.Numeric(10, 2), nullable=False, server_default='0'),
        sa.Column('price_yearly', sa.Numeric(10, 2), nullable=False, server_default='0'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    
    # Create package_feature_assignments table
    op.create_table('package_feature_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('package_id', sa.Integer(), nullable=False, index=True),
        sa.Column('feature_id', sa.Integer(), nullable=False, index=True),
        sa.Column('value', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['package_id'], ['packages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['feature_id'], ['package_features.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('package_id', 'feature_id', name='_package_feature_uc')
    )
    
    # Create indexes
    op.create_index('idx_package_features_name', 'package_features', ['name'], unique=True)
    op.create_index('idx_packages_name', 'packages', ['name'], unique=True)
    op.create_index('idx_packages_slug', 'packages', ['slug'], unique=True)


def downgrade():
    # Drop indexes first
    op.drop_index('idx_packages_slug', table_name='packages')
    op.drop_index('idx_packages_name', table_name='packages')
    op.drop_index('idx_package_features_name', table_name='package_features')
    
    # Drop tables in reverse order of creation
    op.drop_table('package_feature_assignments')
    op.drop_table('packages')
    op.drop_table('package_features')
