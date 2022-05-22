"""Login History

Revision ID: 08b8be69adec
Revises: a666a2723b6a
Create Date: 2022-05-21 14:50:13.389776

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "08b8be69adec"
down_revision = "a666a2723b6a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "loginlog",
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=False),
        sa.Column("ip_addr", sa.String(length=255), nullable=True),
        sa.Column("device_type", postgresql.ENUM("PC", "MOBILE", "TABLET", name="device_type"), nullable=False),
        sa.ForeignKeyConstraint(("user_id",), ["user.id"]),
        sa.PrimaryKeyConstraint("id", "device_type"),
        sa.UniqueConstraint("id"),
    )
    op.create_unique_constraint("loginlog_role_uq_id", "role", ["id"])
    op.create_unique_constraint("loginlog_user_uq_id", "user", ["id"])


def downgrade():
    op.drop_constraint("loginlog_user_uq_id", "user", type_="unique")
    op.drop_constraint("loginlog_role_uq_id", "role", type_="unique")
    op.drop_table("loginlog")
