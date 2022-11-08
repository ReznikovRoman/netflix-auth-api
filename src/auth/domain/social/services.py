from __future__ import annotations

from typing import TYPE_CHECKING

from auth.common.exceptions import NotFoundError
from auth.domain.users.types import User

from .types import UserSocialInfo

if TYPE_CHECKING:
    from auth.domain.users.repositories import UserRepository

    from .repositories import SocialAccountRepository


class SocialAccountService:
    """User social account service."""

    def __init__(self, social_account_repository: SocialAccountRepository, user_repository: UserRepository):
        self.social_account_repository = social_account_repository
        self.user_repository = user_repository

    def handle_social_auth(self, user_social_info: UserSocialInfo) -> User:
        """Create user and social account if needed."""
        email = user_social_info.email
        try:
            user = self.user_repository.get_active_by_email(email)
        except NotFoundError:
            # XXX: specifying a default password, so user could change it in the future
            # ref: `02_user_social_temp_password.md` decision
            user = self.user_repository.create(email, "XXX")
        try:
            self.social_account_repository.find_by_email(email=email, provider_slug=user_social_info.provider_slug)
        except NotFoundError:
            self.social_account_repository.create(user.id, user_social_info)
        return user
