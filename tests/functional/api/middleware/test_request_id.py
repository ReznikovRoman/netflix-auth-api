import requests


class TestRequestIdMiddleware:
    """Test middleware that requires `X-Request-Id` headers in all requests."""

    def test_ok(self, settings):
        """If there is `X-Request-Id` header in the request, service will respond correctly."""
        got = requests.get(f"{settings.CLIENT_BASE_URL}/api/v1/health/")

        assert got.status_code == 200

    def test_missing_header(self, settings):
        """If there is no `X-Request-Id` header in the request, client will receive an appropriate error."""
        got = requests.get(f"{settings.SERVER_BASE_URL}/api/v1/health/")

        assert got.status_code == 400
        assert got.json()["error"]["code"] == "missing_header"
