from dataclasses import dataclass
from uuid import UUID

seconds = int

Id = int | str | UUID

Query = dict | str


@dataclass(frozen=True, slots=True)
class PageNumberPagination:
    """Настройки постраничной пагинации."""

    page: int
    per_page: int
