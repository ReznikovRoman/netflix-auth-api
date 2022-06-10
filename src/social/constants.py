import enum
from typing import Final, Sequence


class SocialProviderSlug(enum.Enum):
    """Доступные социальные провайдеры для авторизации."""

    YANDEX = "yandex"
    GOOGLE = "google"


SOCIAL_AUTH_AVAILABLE_PROVIDER_SLUGS: Final[Sequence[str]] = [provider.value for provider in SocialProviderSlug]
