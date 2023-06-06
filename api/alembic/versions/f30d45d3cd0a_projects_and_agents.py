"""projects and agents

Revision ID: f30d45d3cd0a
Revises: eeea3976e6e5
Create Date: 2023-06-01 23:36:43.065355

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func, text, expression
from sqlalchemy.dialects.postgresql import UUID, ENUM


# revision identifiers, used by Alembic.
revision = 'f30d45d3cd0a'
down_revision = 'eeea3976e6e5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "project",
        sa.Column("id", sa.String, primary_key=True, unique=True, nullable=False), # *(required)
        sa.Column("name", sa.String(), nullable=False), # *(required)
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey('workspace.id'), nullable=False), # *(required)
        sa.Column("creator_id", sa.String(), nullable=False, comment="user_id of the creator of this team"), # *(required)
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("status", sa.String(), server_default='pending'),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "goal",
        sa.Column("id", sa.String(), primary_key=True, unique=True, nullable=False, server_default=text("uuid_generate_v4()")), # *(required)
        sa.Column("description", sa.String(), nullable=False), # *(required)
        sa.Column("project_id", sa.String, sa.ForeignKey('project.id'), nullable=False), # *(required)
        sa.Column("status", sa.String(), server_default='pending'),
        sa.Column("tasks", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "agent",
        sa.Column("id", sa.String(), primary_key=True, unique=True, nullable=False, server_default=text("uuid_generate_v4()")), # *(required)
        sa.Column("role", sa.String(), nullable=False), # *(required)
        sa.Column("scope", sa.String(), nullable=True), # *(required)
        sa.Column("project_id", sa.String, sa.ForeignKey('project.id'), nullable=False), # *(required)
        sa.Column("goal_id", sa.String(), sa.ForeignKey('goal.id'), nullable=False), # *(required)
        sa.Column("collaborators", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_table("agent")
    op.drop_table("goal")
    op.drop_table("project")
