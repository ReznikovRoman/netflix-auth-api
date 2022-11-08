from uuid import UUID

from sqlalchemy.exc import IntegrityError, NoResultFound

from auth.common.exceptions import ConflictError, NotFoundError
from auth.infrastructure.db.postgres import db, db_session

from . import types
from .models import SocialAccount
from .types import UserSocialInfo


class SocialAccountRepository:
    """User social accounts repository."""

    @staticmethod
    def create(user_id: UUID, user_social_info: UserSocialInfo) -> types.SocialAccount:
        """Create a new social account for user."""
        try:
            social_account = SocialAccount(user_id=user_id, **user_social_info.to_dict())
            db.session.add(social_account)
            db.session.commit()
        except IntegrityError:
            raise ConflictError(message="Social Account already exists", code="social_account_conflict")
        except Exception as e:
            db.session.rollback()
            raise e
        return social_account.to_dto()

    @staticmethod
    def find_by_email(email: str, provider_slug: str) -> types.SocialAccount:
        """Find social account by email."""
        try:
            social_account = SocialAccount.query.filter_by(email=email, provider_slug=provider_slug).one()
        except NoResultFound:
            raise NotFoundError
        return social_account.to_dto()

    @staticmethod
    def delete_user_social_account(user_id: UUID, provider_slug: str) -> None:
        """Delete user social account by provider slug."""
        with db_session():
            SocialAccount.query.filter_by(user_id=user_id, provider_slug=provider_slug).delete()
