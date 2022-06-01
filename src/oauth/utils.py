from functools import wraps
from typing import Any, Callable, Final

from jose import jwt

from flask import _request_ctx_stack, request

from .exceptions import OAuthError, OAuthPermissionError
from .validator import validate_token

TOKEN_TYPE: Final[str] = "Bearer"


def get_token_from_header() -> str:
    """Получение токена из заголовка 'Authorization'."""
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise OAuthError("Authorization header is expected", "authorization_header_missing")

    parts = auth.split()
    if parts[0].lower() != TOKEN_TYPE.lower():
        raise OAuthError(f"Authorization header must start with {TOKEN_TYPE}", "invalid_header")
    if len(parts) == 1:
        raise OAuthError("Token not found", "invalid_header")
    if len(parts) > 2:
        raise OAuthError(f"Authorization header must be {TOKEN_TYPE} token", "invalid_header")

    token = parts[1]
    return token


def has_scope(token: str, required_scope: str) -> bool:
    """Определяет есть ли у токена необходимый 'scope'."""
    unverified_claims = jwt.get_unverified_claims(token)
    if not unverified_claims.get("scope"):
        return False
    token_scopes = unverified_claims["scope"].split()
    return required_scope in token_scopes


class requires_auth:  # noqa
    """Декоратор для проверки access токена из запроса с помощью сервиса auth0.

    Attributes:
        required_scope: опциональный атрибут для указания необходимого 'scope' для доступа к ресурсу.
    """

    def __init__(self, required_scope: str | None = None):
        self.required_scope = required_scope

    def __call__(self, func) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            token = get_token_from_header()
            payload = validate_token(token)
            if self.required_scope is not None:
                self._check_permissions(token)
            _request_ctx_stack.top.current_user = payload
            return func(*args, **kwargs)
        return wrapper

    def _check_permissions(self, token: str) -> None:
        access_denied = not has_scope(token, self.required_scope)
        if access_denied:
            raise OAuthPermissionError
