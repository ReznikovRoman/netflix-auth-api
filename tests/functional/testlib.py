from __future__ import annotations

import contextlib
import json
from typing import TYPE_CHECKING, Union
from urllib.parse import urljoin

import redis
import requests
import sqlalchemy
from requests.sessions import Session
from sqlalchemy.engine import Engine

from auth.domain.users.types import User

from .settings import get_settings

if TYPE_CHECKING:
    from requests import Response

    APIResponse = Union[str, dict, list[dict], dict[str, dict], dict[str, list[dict]], Response]


settings = get_settings()


class APIClient(Session):
    """Requests-based test client."""

    _access_token: str = None

    def __init__(self, base_url: str = "http://server:8002", user: User | None = None) -> None:
        super().__init__()
        self.base_url = base_url
        self.user = user

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.base_url, url)
        headers = kwargs.pop("headers", {})
        anon = kwargs.pop("anon", False)
        if self.user is not None and not anon:
            headers.update({"Authorization": f"Bearer {self.access_token}"})
        response = super(APIClient, self).request(method, url, headers=headers, *args, **kwargs)
        return response

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
        if self.is_json(response) and content:
            return json.loads(content)
        return content

    @staticmethod
    def is_json(response: Response) -> bool:
        content_type = response.headers.get("content-type", None)
        if content_type is None:
            return False
        return "json" in content_type

    @property
    def access_token(self):
        if self._access_token is not None:
            return self._access_token
        return self._get_access_token()

    def _get_access_token(self):
        body = {"email": self.user.email, "password": self.user.password}
        requests.post(urljoin(self.base_url, "/api/v1/auth/register"), data=body)
        credentials = requests.post(urljoin(self.base_url, "/api/v1/auth/login"), data=body).json()["data"]
        access_token = credentials["access_token"]
        self._access_token = access_token
        return access_token


class Auth0Client(APIClient):
    """Requests-based test client for tests with auth0 authorization."""

    _access_token: str = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.base_url, url)
        headers = kwargs.pop("headers", {})
        headers.update({"Authorization": f"Bearer {self.access_token}"})
        response = super(APIClient, self).request(method, url, headers=headers, *args, **kwargs)
        return response

    @property
    def access_token(self):
        if self._access_token is not None:
            return self._access_token
        return self._get_access_token()

    def _get_access_token(self):
        payload = {
            "client_id": settings.AUTH0_CLIENT_ID,
            "client_secret": settings.AUTH0_CLIENT_SECRET,
            "audience": settings.AUTH0_API_AUDIENCE,
            "grant_type": settings.AUTH0_GRANT_TYPE,
        }
        headers = {"content-type": "application/json"}

        got = requests.post(settings.AUTH0_AUTHORIZATION_URL, json=payload, headers=headers).json()

        access_token = got["access_token"]
        self._access_token = access_token
        return access_token


def create_anon_client() -> APIClient:
    return APIClient(base_url=settings.CLIENT_BASE_URL)


def create_auth_client(user: User) -> APIClient:
    return APIClient(base_url=settings.CLIENT_BASE_URL, user=user)


def create_auth0_client() -> Auth0Client:
    return Auth0Client(base_url=settings.CLIENT_BASE_URL)


def teardown_postgres(engine: Engine) -> None:
    # XXX: have to specify tables that won't be truncated
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
    throttling_client = redis.Redis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_THROTTLE_STORAGE_DB)
    redis_client.flushdb()
    throttling_client.flushdb()


def _format_table_name(table_name: str) -> str:
    formatted_name = f"{settings.DB_NAME}.{settings.DB_DEFAULT_SCHEMA}.{table_name}"
    return formatted_name
