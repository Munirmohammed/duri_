"""notification_table

Revision ID: 706a423d8f36
Revises: db1b25773970
Create Date: 2023-04-20 21:28:15.874482

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text, func
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '706a423d8f36'
down_revision = 'db1b25773970'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
		"notification",
		sa.Column("id", UUID(as_uuid=True), unique=True, nullable=False, primary_key=True, server_default=text("uuid_generate_v4()")),
        sa.Column("data", sa.JSON, nullable=False),
		sa.Column('workspace_id', UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now()),
    )

def downgrade():
    op.drop_table("notification")

