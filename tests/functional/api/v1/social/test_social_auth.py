from ..base import BaseClientTest


class TestSocialAuth(BaseClientTest):
    """Тестирование авторизации через социальную сеть (стороннего провайдера)."""

    endpoint = "/api/v1/social/auth/{provider_slug}?state=XXX"
    method = "get"

    _wrong_endpoint = "/api/v1/social/auth/{provider_slug}"

    def test_ok(self):
        """Если все параметры в запросе на авторизацию корректные, то клиент получит пару ключей-доступов."""
        got = self.client.get(self.endpoint.format("yandex"))

        assert False, got

    def test_no_state(self):
        """Если в запросе на авторизацию нет query параметра `state`, то мы делаем редирект на страницу логина."""
        got = self.client.get(self._wrong_endpoint.format("yandex"))

        assert False, got

    def test_new_user_created(self):
        """Если пользователя с почтой от провайдера еще не было, то мы создаем такого пользователя."""
        got = self.client.get(self.endpoint.format("yandex"))

        assert False, got

    def test_user_exists(self):
        """Если пользователь с почтой от провайдера уже есть в системе, то мы не создаем нового."""
        got = self.client.get(self.endpoint.format("yandex"))

        assert False, got
