from uuid import UUID

from sqlalchemy.exc import IntegrityError, NoResultFound

from auth.common.exceptions import ConflictError, NotFoundError
from auth.db.postgres import db, db_session

from . import types
from .models import SocialAccount
from .types import UserSocialInfo


class SocialAccountRepository:
    """Репозиторий для работы с данными социальных сетей пользователя."""

    @staticmethod
    def create(user_id: UUID, user_social_info: UserSocialInfo) -> types.SocialAccount:
        """Создание новой социальной сети пользователя."""
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
        """Получить социальный аккаунт по почте."""
        try:
            social_account = SocialAccount.query.filter_by(email=email, provider_slug=provider_slug).one()
        except NoResultFound:
            raise NotFoundError
        return social_account.to_dto()

    @staticmethod
    def delete_user_social_account(user_id: UUID, provider_slug: str) -> None:
        """Удалить социальный аккаунт пользователя по названию провайдера."""
        with db_session():
            SocialAccount.query.filter_by(user_id=user_id, provider_slug=provider_slug).delete()
