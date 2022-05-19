"""Default roles

Revision ID: 954954de3916
Revises: 0eda18d0256f
Create Date: 2022-05-19 12:42:42.499635

"""
import datetime
import uuid

from alembic import op
import sqlalchemy as sa

from dataclasses import dataclass, field

# revision identifiers, used by Alembic.
from sqlalchemy import table
from sqlalchemy.dialects import postgresql

revision = "954954de3916"
down_revision = "b670298d2710"
branch_labels = None
depends_on = None


@dataclass
class Role:
    name: str
    description: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_dict(self) -> dict:
        dct = {
            "id": self.id, "name": self.name, "description": self.description,
            "created_at": self.created_at, "updated_at": self.updated_at,
        }
        return dct


default_roles = [
    Role("viewers", "Common viewers").to_dict(),
    Role("subscribers", "Paid subscribers").to_dict(),
]

roles_table = table(
    "role",
    sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column("name", sa.String(length=80), nullable=False),
    sa.Column("description", sa.String(length=255), server_default="", nullable=False),
    sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
    sa.Column("updated_at", sa.TIMESTAMP(), nullable=False),
)


def upgrade():
    op.bulk_insert(
        roles_table,
        default_roles,
    )


def downgrade():
    pass
