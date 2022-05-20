from datetime import timedelta
from functools import lru_cache
from typing import Literal, Union

from pydantic import AnyHttpUrl, validator
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
    SERVER_NAME: str
    SERVER_HOSTS: Union[str, list[AnyHttpUrl]]
    PROJECT_NAME: str
    DEBUG: bool = False

    # JWT
    JWT_SECRET_KEY: str = None
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(days=3)

    # OAUTH
    AUTH0_DOMAIN: str
    AUTH0_API_AUDIENCE: str
    AUTH0_ISSUER: str
    AUTH0_ALGORITHMS: list[str] = ["RS256"]

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


@lru_cache()
def get_settings() -> "Settings":
    return Settings()
