import datetime
import uuid
from dataclasses import dataclass

from auth.common.enums import ExtendedEnum
from auth.domain.roles.types import Role


@dataclass(slots=True)
class User:
    """User."""

    id: uuid.UUID  # noqa: VNE003
    email: str
    password: str
    active: bool
    roles: list[Role]

    @staticmethod
    def _prepare_fields(data: dict) -> dict:
        roles = [Role.from_dict(role) for role in data["roles"]]
        dct = {
            "id": data["id"],
            "email": data["email"],
            "password": data["password"],
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
    """JWT credentials."""

    access_token: str
    refresh_token: str


@dataclass(frozen=True, slots=True)
class LoginLog:
    """Login log record."""

    class DeviceType(ExtendedEnum):
        """Device type that was used to log in to the account."""

        PC = "pc"
        MOBILE = "mobile"
        TABLET = "tablet"

    id: uuid.UUID  # noqa: VNE003
    created_at: datetime.datetime
    user: "User"
    user_agent: str
    ip_addr: str
    device_type: DeviceType
