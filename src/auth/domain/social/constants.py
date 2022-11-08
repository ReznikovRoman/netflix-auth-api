import enum
from typing import Final, Sequence


class SocialProviderSlug(enum.Enum):
    """Available social providers."""

    YANDEX = "yandex"
    GOOGLE = "google"


# List of slugs of available social providers
SOCIAL_AUTH_AVAILABLE_PROVIDER_SLUGS: Final[Sequence[str]] = [provider.value for provider in SocialProviderSlug]
