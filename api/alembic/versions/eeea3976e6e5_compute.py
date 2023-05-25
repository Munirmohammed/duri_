"""compute

Revision ID: eeea3976e6e5
Revises: 706a423d8f36
Create Date: 2023-04-27 22:58:18.817171

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func, text
from sqlalchemy.dialects.postgresql import UUID, ENUM

# revision identifiers, used by Alembic.
revision = 'eeea3976e6e5'
down_revision = '706a423d8f36'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
		"resource",
		sa.Column("id", UUID(as_uuid=True), unique=True, nullable=False, primary_key=True, server_default=text("uuid_generate_v4()")),
		#sa.Column('workspace_id', UUID(as_uuid=True), sa.ForeignKey('workspace.id'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('user.id'), nullable=False),
        sa.Column("name", sa.String(), nullable=False, comment="user provided name of this resource"), 
        sa.Column("type", sa.String(), nullable=False, comment="resource-type one of compute | service |  "), 
        #sa.Column("subtype", sa.String(), nullable=False, comment="resource-sub-type, ie git, server,  "),  ## TODO
        sa.Column("provider", sa.String(), nullable=False, comment="the resource provider. one of k8s | aws | gcp "),
        sa.Column("meta", sa.JSON(), nullable=False, comment=""), ## TODO
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True),  nullable=True, ),
    )

    op.create_table(
		"credential",
		sa.Column("id", UUID(as_uuid=True), unique=True, nullable=False, primary_key=True, server_default=text("uuid_generate_v4()")),
		#sa.Column('workspace_id', UUID(as_uuid=True), sa.ForeignKey('workspace.id'), nullable=False),
		sa.Column('resource_id', UUID(as_uuid=True), sa.ForeignKey('resource.id'), nullable=False),
        sa.Column("type", sa.String(), nullable=False, comment="the credetials type, ssh, keystore, access_key, plain"), ## TODO 
        #sa.Column("config", sa.JSON(), nullable=False, comment="the credetials store"), ## TODO we need to encrypt this or use a secure secret store like aws secret manager
        sa.Column("store", sa.LargeBinary(), nullable=False, comment="the credetials store"), ## TODO we need to encrypt this or use a secure secret store like aws secret manager
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True),  nullable=True, ),
    )


def downgrade():
    op.drop_table("credential")
    op.drop_table("resource")
