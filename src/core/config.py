from datetime import timedelta
from functools import lru_cache
from typing import Literal, Union

from pydantic import AnyHttpUrl, Field, validator
from pydantic.env_settings import BaseSettings

from common.types import seconds


class EnvConfig(BaseSettings.Config):

    @classmethod
    def prepare_field(cls, field) -> None:
        if "env_names" in field.field_info.extra:
            return
        return super().prepare_field(field)


class Settings(BaseSettings):
    """Настройки проекта."""

    # Project
    SECRET_KEY: str
    PROJECT_BASE_URL: str
    API_V1_STR: str = "/api/v1"
    SERVER_NAME: str | None = Field(None, env="NAA_SERVER_NAME")
    SERVER_HOSTS: Union[str, list[AnyHttpUrl]]
    PROJECT_NAME: str
    THROTTLE_KEY_PREFIX: str = ""
    THROTTLE_DEFAULT_LIMITS: Union[str, list[str]] = Field(default_factory=list)
    THROTTLE_USER_REGISTRATION_LIMITS: str = Field("5/minute")
    DEBUG: bool = False

    # JWT
    JWT_SECRET_KEY: str = None
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(minutes=10)
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(days=3)

    # OAUTH
    AUTH0_DOMAIN: str
    AUTH0_API_AUDIENCE: str
    AUTH0_ISSUER: str
    AUTH0_ALGORITHMS: list[str] = ["RS256"]

    # Social
    SOCIAL_GOOGLE_CLIENT_ID: str
    SOCIAL_GOOGLE_CLIENT_SECRET: str
    SOCIAL_GOOGLE_METADATA_URL: str = Field("https://accounts.google.com/.well-known/openid-configuration")
    SOCIAL_YANDEX_CLIENT_ID: str
    SOCIAL_YANDEX_CLIENT_SECRET: str
    SOCIAL_YANDEX_ACCESS_TOKEN_URL: str = Field("https://oauth.yandex.ru/token")
    SOCIAL_YANDEX_USERINFO_ENDPOINT: str = Field("https://login.yandex.ru/info")
    SOCIAL_YANDEX_AUTHORIZE_URL: str = Field("https://oauth.yandex.ru/authorize")
    SOCIAL_USE_STUBS: bool = Field(False)

    # SQLAlchemy
    SQLALCHEMY_ECHO: bool = False

    # Postgres
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_URL: str = None

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_THROTTLE_STORAGE_DB: int
    REDIS_DEFAULT_CHARSET: str = "utf-8"
    REDIS_DECODE_RESPONSES: bool | Literal[True, False] = True
    REDIS_RETRY_ON_TIMEOUT: bool = True
    REDIS_DEFAULT_TIMEOUT: seconds = 5 * 60  # 5 минут

    class Config(EnvConfig):
        env_prefix = "NAA_"
        case_sensitive = True

    @validator("SERVER_HOSTS", pre=True)
    def _assemble_server_hosts(cls, server_hosts):
        if isinstance(server_hosts, str):
            return [item.strip() for item in server_hosts.split(",")]
        return server_hosts

    @validator("THROTTLE_DEFAULT_LIMITS", pre=True)
    def _assemble_throttle_default_limits(cls, throttle_default_limits):
        if isinstance(throttle_default_limits, str):
            return [item.strip() for item in throttle_default_limits.split(",")]
        return throttle_default_limits

    @validator("JWT_SECRET_KEY", pre=True)
    def _assemble_jwt_secret_key(cls, value, values):
        if value is not None:
            return value
        return values["SECRET_KEY"]

    @validator("DB_URL", pre=True)
    def get_db_url(cls, value, values) -> str:
        if value is not None:
            return value
        user = values["DB_USER"]
        password = values["DB_PASSWORD"]
        host = values["DB_HOST"]
        port = values["DB_PORT"]
        database = values["DB_NAME"]
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    @property
    def formatted_rate_limits(self) -> str:
        rate_limits = self.THROTTLE_DEFAULT_LIMITS
        if not rate_limits:
            return ""
        if len(rate_limits) == 1:
            return rate_limits[0]
        return "; ".join(rate_limits)


@lru_cache()
def get_settings() -> "Settings":
    return Settings()
