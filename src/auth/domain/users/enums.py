import enum


class UserSignal(str, enum.Enum):
    """Users domain signals."""

    USER_REGISTERED = "users.registration.complete"
