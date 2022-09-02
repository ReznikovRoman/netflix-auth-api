from __future__ import annotations

from typing import TYPE_CHECKING

from flask import request

from auth.common.exceptions import RequiredHeaderMissingError

if TYPE_CHECKING:
    from flask import Flask


def register_before_request(app: Flask) -> None:

    @app.before_request
    def before_request() -> None:
        request_id = request.headers.get("X-Request-Id")
        if not request_id:
            raise RequiredHeaderMissingError(message="Required header `X-Request-Id` is missing")
