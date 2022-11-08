from dataclasses import dataclass
from uuid import UUID

seconds = int

Id = int | str | UUID

Query = dict | str


@dataclass(frozen=True, slots=True)
class PageNumberPagination:
    """Page number pagination params."""

    page: int
    per_page: int
