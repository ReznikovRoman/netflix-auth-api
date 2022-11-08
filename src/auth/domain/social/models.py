from sqlalchemy.dialects.postgresql import UUID

from auth.common.models import UUIDMixin
from auth.infrastructure.db.postgres import db

from . import types


class SocialAccount(UUIDMixin, db.Model):
    """User social account."""

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    user = db.relationship("User", backref=db.backref("social_accounts", cascade="all, delete-orphan"))

    social_id = db.Column(db.String(255), nullable=False)
    provider_slug = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)

    __table_args__ = (
        # user has only one account in the given social network
        db.UniqueConstraint("user_id", "provider_slug"),

        # one social account for each social account
        db.UniqueConstraint("email", "provider_slug"),

        # ID in the social network is unique
        db.UniqueConstraint("social_id", "provider_slug"),
    )

    def __str__(self) -> str:
        return f"{self.provider_slug}: {self.email}"

    def __repr__(self) -> str:
        return f"<{self}>"

    def to_dto(self) -> types.SocialAccount:
        social_account = types.SocialAccount(
            id=self.id, user_id=self.user_id,
            social_id=self.social_id, provider_slug=self.provider_slug, email=self.email,
        )
        return social_account
