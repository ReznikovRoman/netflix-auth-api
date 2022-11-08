import enum


class NotificationType(str, enum.Enum):
    """Notification type."""

    EMAIL = "email"


class NotificationPriority(str, enum.Enum):
    """Notification priority."""

    URGENT = "urgent"
    COMMON = "common"
    DEFAULT = "default"
