"""Fix payment status case

Revision ID: fix_payment_status_case
Revises: 
Create Date: 2025-07-10 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_payment_status_case'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Convert all payment statuses to lowercase for consistency
    op.execute("""
    UPDATE payments 
    SET status = LOWER(status)
    WHERE status != LOWER(status)
    """)

def downgrade():
    # This is a one-way migration as we want to enforce lowercase
    pass
