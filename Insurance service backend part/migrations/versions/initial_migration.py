"""Initial migration

Revision ID: 1a2b3c4d5e6f
Revises:
Create Date: 2023-05-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # This migration is empty because we're using the SQL script for initial setup
    pass


def downgrade():
    # This is the initial migration, so downgrade does nothing
    pass
