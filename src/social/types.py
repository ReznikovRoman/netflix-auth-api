import uuid
from dataclasses import dataclass
from typing import Protocol


class IOAuthClient(Protocol):
    """Интерфейс работы с OAuth клиентом."""

    def create_authorization_url(self, url: str, **kwargs) -> dict:
        """Создает ссылку для авторизации с использованием опциональных параметров."""

    def save_authorize_data(self, **kwargs) -> None:
        """Сохранение данных авторизации, `state`, в хранилище."""

    def get_access_token(self, **kwargs) -> str:
        """Получение и проверка access токена от провайдера."""

    def get_user_info(self, **kwargs) -> dict:
        """Получение информации о пользователе от провайдера."""


@dataclass(frozen=True, slots=True)
class UserSocialInfo:
    """Информация о пользователе от провайдера."""

    # идентификатор пользователя у внешнего провайдера
    social_id: str

    # название провайдера
    provider_slug: str

    email: str


@dataclass(frozen=True, slots=True)
class SocialAccount:
    """Социальный аккаунт пользователя."""

    id: uuid.UUID  # noqa: VNE003
    user_id: uuid.UUID
    social_id: str
    provider_slug: str
    email: str

    @classmethod
    def from_dict(cls, data: dict) -> "SocialAccount":
        dct = {
            "id": data["id"],
            "user_id": data["user_id"],
            "social_id": data["social_id"],
            "provider_slug": data["provider_slug"],
            "email": data["email"],
        }
        return cls(**dct)
