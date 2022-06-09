"""Social account.
Revision ID: 3c98c28c5d5b
Revises: 08b8be69adec
Create Date: 2022-06-09 15:30:37.818839

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "3c98c28c5d5b"
down_revision = "08b8be69adec"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "socialaccount",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("social_id", sa.String(length=255), nullable=False),
        sa.Column("provider_slug", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(("user_id",), ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("social_id"),
        sa.UniqueConstraint("user_id", "provider_slug"),
        sa.UniqueConstraint("email", "provider_slug"),
        sa.UniqueConstraint("social_id", "provider_slug"),
    )


def downgrade():
    op.drop_table("socialaccount")
