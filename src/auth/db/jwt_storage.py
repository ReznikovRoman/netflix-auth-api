from datetime import timedelta

from auth.common.types import seconds
from auth.core.config import get_settings
from auth.db.cache.base import Cache

settings = get_settings()


class JWTStorage:
    """JWT хранилище."""

    def __init__(self, cache: Cache):
        self.cache = cache

    def is_token_revoked(self, jti: str) -> bool:
        return bool(self.cache.exists(jti))

    def invalidate_tokens(self, access_jwt: dict) -> None:
        """Сохраняем инвалидированные токены в хранилище blacklisted токенов."""
        jti = access_jwt["jti"]
        refresh_jti = access_jwt["refresh_jti"]
        self.invalidate_token(jti, settings.JWT_ACCESS_TOKEN_EXPIRES)
        self.invalidate_token(refresh_jti, settings.JWT_REFRESH_TOKEN_EXPIRES)

    def invalidate_token(self, jti: str, timeout: seconds | timedelta) -> bool:
        return self.cache.set(jti, "", timeout=timeout)
