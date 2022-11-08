from typing import Any

from pydantic import BaseModel, EmailStr, Field, root_validator

from .enums import NotificationPriority, NotificationType
from .exceptions import MissingContentError
from .types import Queue


class NotificationIn(BaseModel):
    """New notification from an external service."""

    subject: str
    notification_type: NotificationType
    priority: NotificationPriority
    recipient_list: list[EmailStr]
    content: str | None = None
    template_slug: str | None = None
    context: dict[str, Any] | None = Field(default_factory=dict)

    @root_validator(pre=True)
    def clean_content_with_slug(cls, values: dict) -> dict:
        """Validate notification slug and content.

        If client uses built-in template with `template_slug`, `content` field is ignored.

        If template is `None`, then client has to specify notification `content`.
        """
        content = values.get("content")
        template_slug = values.get("template_slug")
        if template_slug is not None:
            values["content"] = None
            return values
        if content is None:
            raise MissingContentError()
        return values


class NotificationShortDetails(BaseModel):
    """Notification short details."""

    notification_id: str
    queue: Queue
