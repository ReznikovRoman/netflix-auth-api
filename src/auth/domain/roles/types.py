import uuid
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Role:
    """User role."""

    id: uuid.UUID  # noqa: VNE003
    name: str
    description: str

    @classmethod
    def from_dict(cls, data: dict) -> "Role":
        dct = {"id": data["id"], "name": data["name"], "description": data["description"]}
        return cls(**dct)
