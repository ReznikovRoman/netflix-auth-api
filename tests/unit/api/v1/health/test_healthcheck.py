def test_ok(anon_client):
    """Endpoint /healthcheck returns 200 HTTP status."""
    got = anon_client.get("/api/v1/health/")

    assert got["status"] == "ok"
