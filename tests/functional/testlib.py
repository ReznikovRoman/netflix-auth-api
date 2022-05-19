from __future__ import annotations

import contextlib
import json
from typing import TYPE_CHECKING, Union
from urllib.parse import urljoin

import redis
import sqlalchemy
from requests.sessions import Session
from sqlalchemy.engine import Engine

from .settings import get_settings

if TYPE_CHECKING:
    from requests import Response

    APIResponse = Union[dict, str, list[dict], dict[str, dict], Response]


settings = get_settings()


class APIClient(Session):
    """Requests-based клиент для тестов."""

    def __init__(self, base_url: str = "http://server:8002") -> None:
        super().__init__()
        self.base_url = base_url

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.base_url, url)
        return super(APIClient, self).request(method, url, *args, **kwargs)

    def head(self, *args, **kwargs) -> APIResponse:
        return self._api_call("head", kwargs.get("expected_status_code", 200), *args, **kwargs)

    def get(self, *args, **kwargs) -> APIResponse:
        return self._api_call("get", kwargs.get("expected_status_code", 200), *args, **kwargs)

    def post(self, *args, **kwargs) -> APIResponse:
        return self._api_call("post", kwargs.get("expected_status_code", 201), *args, **kwargs)

    def put(self, *args, **kwargs) -> APIResponse:
        return self._api_call("put", kwargs.get("expected_status_code", 200), *args, **kwargs)

    def patch(self, *args, **kwargs) -> APIResponse:
        return self._api_call("patch", kwargs.get("expected_status_code", 200), *args, **kwargs)

    def delete(self, *args, **kwargs) -> APIResponse:
        return self._api_call("delete", kwargs.get("expected_status_code", 204), *args, **kwargs)

    def _api_call(self, method: str, expected: int, *args, **kwargs) -> APIResponse:
        kwargs.pop("expected_status_code", None)
        as_response = kwargs.pop("as_response", False)

        method = getattr(super(), method)
        response = method(*args, **kwargs)
        if as_response:
            return response

        content = self._decode(response)

        error_message = f"Got {response.status_code} instead of {expected}. Content is '{content}'"
        assert response.status_code == expected, error_message

        return content

    def _decode(self, response: Response) -> APIResponse:
        content = response.content.decode("utf-8", errors="ignore")
        if self.is_json(response):
            return json.loads(content)
        return content

    @staticmethod
    def is_json(response: Response) -> bool:
        content_type = response.headers.get("content-type", None)
        if content_type is None:
            return False
        return "json" in content_type


def create_anon_client() -> APIClient:
    return APIClient(base_url=settings.CLIENT_BASE_URL)


def teardown_postgres(engine: Engine) -> None:
    # XXX: указываем вручную таблицы, которые не должны очищаться
    tables_to_exclude = (
        "alembic_version",
    )
    table_names = ",".join(
        _format_table_name(table_name)
        for table_name in sqlalchemy.inspect(engine).get_table_names()
        if table_name not in tables_to_exclude
    )
    with contextlib.closing(engine.connect()) as connection:
        transaction = connection.begin()
        connection.execute(f"""TRUNCATE {table_names} RESTART IDENTITY;""")
        transaction.commit()


def flush_redis_cache() -> None:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        encoding=settings.REDIS_DEFAULT_CHARSET,
        decode_responses=settings.REDIS_DECODE_RESPONSES,
        retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
    )
    redis_client.flushdb()


def _format_table_name(table_name: str) -> str:
    formatted_name = f"{settings.DB_NAME}.{settings.DB_DEFAULT_SCHEMA}.{table_name}"
    return formatted_name
