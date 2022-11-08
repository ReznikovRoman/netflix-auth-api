import uuid
from dataclasses import dataclass
from typing import Protocol


class IOAuthClient(Protocol):
    """Oauth client interface."""

    def create_authorization_url(self, url: str, **kwargs) -> dict:
        """Build authorization url with optional parameters."""

    def save_authorize_data(self, **kwargs) -> None:
        """Save authorization related data to state."""

    def get_access_token(self, **kwargs) -> str:
        """Receive access token from social provider."""

    def get_user_info(self, **kwargs) -> dict:
        """Get user info from social provider."""


@dataclass(frozen=True, slots=True)
class UserSocialInfo:
    """User info from social provider."""

    # user id from social provider
    social_id: str

    # social provider slug
    provider_slug: str

    email: str

    def to_dict(self) -> dict:
        dct = {
            "social_id": self.social_id,
            "provider_slug": self.provider_slug,
            "email": self.email,
        }
        return dct


@dataclass(frozen=True, slots=True)
class SocialAccount:
    """User social account."""

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
