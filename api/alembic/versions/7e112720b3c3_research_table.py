"""research_table

Revision ID: 7e112720b3c3
Revises: f30d45d3cd0a
Create Date: 2023-06-13 22:54:52.256361

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func, text, expression
from sqlalchemy.dialects.postgresql import UUID, ENUM

# revision identifiers, used by Alembic.
revision = '7e112720b3c3'
down_revision = 'f30d45d3cd0a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "research",
        sa.Column("id", sa.String, primary_key=True, unique=True, nullable=False), # *(required)
        sa.Column("name", sa.String(), nullable=False), # *(required)
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey('workspace.id'), nullable=False), # *(required)
        sa.Column("project_id", sa.String, sa.ForeignKey('project.id'), nullable=False), # *(required)
        sa.Column("creator_id", sa.String(), nullable=False, comment="user_id of the creator of this team"), # *(required)
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("status", sa.String(), server_default='pending'),
        sa.Column("workdir", sa.String(), nullable=False),
        sa.Column("goals", sa.JSON(), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_table("research")
