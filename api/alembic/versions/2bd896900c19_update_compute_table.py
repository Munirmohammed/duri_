"""update compute table

Revision ID: 2bd896900c19
Revises: eeea3976e6e5
Create Date: 2023-05-24 20:25:12.780342

"""
from sqlalchemy import ForeignKeyConstraint, MetaData
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text

# revision identifiers, used by Alembic.
revision = '2bd896900c19'
down_revision = 'eeea3976e6e5'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_constraint('resource_workspace_id_fkey', 'resource', type_='foreignkey')
    op.drop_column('resource', 'workspace_id')
    op.add_column('resource', sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('user.id'), nullable=False))

def downgrade():
    op.add_column('resource', sa.Column('workspace_id', sa.UUID(as_uuid=True), sa.ForeignKey('workspace.id'), nullable=False))
    op.create_foreign_key('resource_workspace_id_fkey', 'resource', 'workspace', ['workspace_id'], ['id'])
    op.drop_column('resource', 'user_id')
