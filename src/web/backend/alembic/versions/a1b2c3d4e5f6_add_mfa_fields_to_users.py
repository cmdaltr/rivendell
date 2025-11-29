"""add_mfa_fields_to_users

Revision ID: a1b2c3d4e5f6
Revises: 60ac78591b89
Create Date: 2025-11-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '60ac78591b89'
branch_labels = None
depends_on = None


def upgrade():
    # Add MFA fields to users table
    op.add_column('users', sa.Column('mfa_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('mfa_secret', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('backup_codes', postgresql.JSON, nullable=True))
    op.add_column('users', sa.Column('last_mfa_verification', sa.DateTime(), nullable=True))


def downgrade():
    # Remove MFA fields from users table
    op.drop_column('users', 'last_mfa_verification')
    op.drop_column('users', 'backup_codes')
    op.drop_column('users', 'mfa_secret')
    op.drop_column('users', 'mfa_enabled')
