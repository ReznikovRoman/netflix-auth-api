from uuid import UUID

from db.postgres import db_session

from . import types
from .models import SocialAccount


class SocialAccountRepository:
    """Репозиторий для работы с данными социальных сетей пользователя."""

    @staticmethod
    def create(user_id: UUID, social_id: str, provider_slug: str, email: str) -> types.SocialAccount:
        """Создание новой социальной сети пользователя."""
        with db_session() as session:
            social_account = SocialAccount(
                user_id=user_id, social_id=social_id, provider_slug=provider_slug, email=email)
            session.add(social_account)
        return social_account.to_dto()

    @staticmethod
    def delete(social_account_id: UUID) -> None:
        """Удаление социальной сети пользователя."""
        with db_session():
            SocialAccount.query.filter_by(id=social_account_id).delete()
