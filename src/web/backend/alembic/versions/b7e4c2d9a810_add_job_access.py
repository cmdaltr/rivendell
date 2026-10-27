"""add_job_access

Who owns each job and who it's shared with, for server mode. JobStorage also creates
this table through create_all, so the migration skips it when it already exists.

Revision ID: b7e4c2d9a810
Revises: a1b2c3d4e5f6
Create Date: 2026-10-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b7e4c2d9a810'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    if 'job_access' in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        'job_access',
        sa.Column('job_id', sa.String(), primary_key=True),
        sa.Column('owner_id', sa.String(), nullable=True),
        sa.Column('owner_username', sa.String(), nullable=True),
        sa.Column('shared_with', sa.JSON(), nullable=True),
    )
    op.create_index(op.f('ix_job_access_owner_id'), 'job_access', ['owner_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_job_access_owner_id'), table_name='job_access')
    op.drop_table('job_access')
