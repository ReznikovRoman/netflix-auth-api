from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union

from flask.testing import FlaskClient

if TYPE_CHECKING:
    from werkzeug.test import TestResponse

    APIResponse = Union[dict, str, list[dict], TestResponse]


class APIClient(FlaskClient):
    """API клиент для тестов."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def open(
        self,
        *args: Any,
        buffered: bool = False,
        follow_redirects: bool = False,
        **kwargs: Any,
    ) -> "TestResponse":
        headers = kwargs.pop("headers", {})
        headers.update({"X-Request-Id": "XXX-XXX-XXX"})
        response = super(APIClient, self).open(
            *args,
            buffered=buffered, follow_redirects=follow_redirects, headers=headers,
            **kwargs,
        )
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

    def _decode(self, response: TestResponse) -> APIResponse:
        if response.is_json:
            return response.json
        return response.text


def create_anon_client() -> APIClient:
    return APIClient()
