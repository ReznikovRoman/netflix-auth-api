import enum


class UserSignal(str, enum.Enum):
    """Сигналы в домене `Users`."""

    USER_REGISTERED = "users.registration.complete"
