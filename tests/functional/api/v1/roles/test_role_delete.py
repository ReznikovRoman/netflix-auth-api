import os

import requests
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class TestRoleDelete:
    _access_token: str = None

    def test_delete_ok(self, anon_client, role_dto):
        role = self._create_role(anon_client, role_dto)
        headers = {"Authorization": f"Bearer {self.access_token}"}
        anon_client.delete(f"/api/v1/roles/{role['id']}", headers=headers, expected_status_code=204)

    @property
    def access_token(self):
        if self._access_token is not None:
            return self._access_token
        return self._get_access_token()

    def _create_role(self, anon_client, role_dto):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": role_dto.name, "description": role_dto.description}
        got = anon_client.post("/api/v1/roles", data=body, headers=headers)["data"]
        return got

    @classmethod
    def _get_access_token(cls):
        payload = {
            "client_id": os.environ.get("NAA_AUTH0_CLIENT_ID"),
            "client_secret": os.environ.get("NAA_AUTH0_CLIENT_SECRET"),
            "audience": os.environ.get("NAA_AUTH0_AUDIENCE"),
            "grant_type": "client_credentials",
        }
        headers = {"content-type": "application/json"}

        got = requests.post(os.environ.get("NAA_AUTH0_TOKEN_URL"), json=payload, headers=headers).json()

        access_token = got["access_token"]
        cls._access_token = access_token
        return access_token
