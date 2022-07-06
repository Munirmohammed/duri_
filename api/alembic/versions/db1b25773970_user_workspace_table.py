"""user-workspace table

Revision ID: db1b25773970
Revises: 
Create Date: 2022-07-06 20:59:41.669739

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func, text, expression
from sqlalchemy.dialects.postgresql import UUID, ENUM

# revision identifiers, used by Alembic.
revision = 'db1b25773970'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    connection = op.get_bind()
    ## add uuid-ossp for auto-generation of uuids 
    connection.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'), execution_options={'autocommit':True})

    op.create_table(
        "user",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, unique=True, nullable=False), # *(required) , cognito user-id
        sa.Column("email", sa.String(), unique=True, nullable=False), # *(required)
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "workspace",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, server_default=text("uuid_generate_v4()")), # *(required)
        sa.Column("name", sa.String(), primary_key=True, unique=True, nullable=False), # *(required)
        sa.Column("creator_id", sa.String(), nullable=False, comment="user_id of the creator of this workspace"), # *(required)
        sa.Column("active", sa.Boolean(), nullable=False, server_default=expression.true(), comment='if false then the group is not in the cognito group'),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("tags", sa.ARRAY(sa.String()), nullable=True, comment="tags"),
        sa.Column("avatar", sa.String(), nullable=True, comment="an image url thats publicly accessible"), ## an avatar image url thats publicly accessible
        sa.Column("ui_customization", sa.JSON(), nullable=True, comment="a json object with ui customizable items for ui ie the object would have entry `background_image` for background image of the cards"), ## an avatar image url thats publicly accessible
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "team",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, server_default=text("uuid_generate_v4()")), # *(required)
        sa.Column("name", sa.String(), primary_key=True, unique=True, nullable=False), # *(required)
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey('workspace.id'), nullable=False), # *(required)
        sa.Column("creator_id", sa.String(), nullable=False, comment="user_id of the creator of this team"), # *(required)
        sa.Column("active", sa.Boolean(), nullable=False, server_default=expression.true(), comment='if false then the team is disabled'),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("tags", sa.ARRAY(sa.String()), nullable=True, comment="tags"),
        sa.Column("avatar", sa.String(), nullable=True, comment="an image url thats publicly accessible"), ## an avatar image url thats publicly accessible
        sa.Column("ui_customization", sa.JSON(), nullable=True, comment="a json object with ui customizable items for ui ie the object would have entry `background_image` for background image of the cards"), ## an avatar image url thats publicly accessible
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "user_workspace",
        sa.Column("user_id", UUID(as_uuid=True),  sa.ForeignKey('user.id'), primary_key=True, nullable=False), # *(required)
        sa.Column("workspace_id", UUID(as_uuid=True),  sa.ForeignKey('workspace.id'), primary_key=True, nullable=False), # *(required)
        sa.Column("membership", sa.String(), nullable=True, server_default="user", comment="membership type to that group, ie user | admin"), # user | admin
    )
    op.create_table(
        "user_team",
        sa.Column("user_id", UUID(as_uuid=True),  sa.ForeignKey('user.id'), primary_key=True, nullable=False), # *(required)
        sa.Column("team_id", UUID(as_uuid=True),  sa.ForeignKey('team.id'), primary_key=True, nullable=False), # *(required)
        sa.Column("membership", sa.String(), nullable=True, server_default="user", comment="membership type to that group, ie user | admin"), # user | admin
    )


def downgrade():
    op.drop_table("user_team")
    op.drop_table("user_workspace")
    op.drop_table("team")
    op.drop_table("workspace")
    op.drop_table("user")
