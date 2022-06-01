from functools import lru_cache
from typing import Literal

from pydantic import BaseSettings, Field, validator


class EnvConfig(BaseSettings.Config):

    @classmethod
    def prepare_field(cls, field) -> None:
        if "env_names" in field.field_info.extra:
            return
        return super().prepare_field(field)


class Test(BaseSettings):
    """Настройки для функциональных тестов."""

    # Tests
    CLIENT_BASE_URL: str = Field(env="TEST_CLIENT_BASE_URL")

    # Postgres
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_DEFAULT_SCHEMA: str = "public"
    DB_URL: str = None

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DEFAULT_CHARSET: str = "utf-8"
    REDIS_DECODE_RESPONSES: bool | Literal[True, False] = True
    REDIS_RETRY_ON_TIMEOUT: bool = True
    REDIS_DEFAULT_TIMEOUT: int = 5

    # OAUTH
    AUTH0_API_AUDIENCE: str
    AUTH0_ISSUER: str
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: str
    AUTH0_AUTHORIZATION_URL: str

    class Config(EnvConfig):
        env_prefix = "NAA_"
        case_sensitive = True
        env_file = ".env"

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
def get_settings() -> "Test":
    return Test()
