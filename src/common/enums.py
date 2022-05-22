from enum import Enum
from typing import Any


class ExtendedEnum(Enum):

    @classmethod
    def names(cls) -> dict[str, str]:
        return {item.name: item.name for item in cls}

    @classmethod
    def list(cls) -> list[Any]:
        return list(map(lambda c: c.value, cls))
