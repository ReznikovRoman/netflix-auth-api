import uuid
from dataclasses import dataclass

from roles.types import Role


@dataclass(frozen=True, slots=True)
class User:
    id: uuid.UUID  # noqa: VNE003
    email: str
    active: bool
    roles: list[Role]

    @staticmethod
    def _prepare_fields(data: dict) -> dict:
        roles = [Role.from_dict(role) for role in data["roles"]]
        dct = {
            "id": data["id"],
            "email": data["email"],
            "active": data["active"],
            "roles": roles,
        }
        return dct

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        dct = cls._prepare_fields(data)
        return cls(**dct)


@dataclass(frozen=True, slots=True)
class JWTCredentials:
    access_token: str
    refresh_token: str
