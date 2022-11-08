from __future__ import annotations

from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject

from auth.containers import Container
from auth.integrations.notifications.enums import NotificationPriority, NotificationType
from auth.integrations.notifications.schemas import NotificationIn
from auth.signals import event_emitter

from .enums import UserSignal

if TYPE_CHECKING:
    from auth.integrations.notifications import NetflixNotificationsClient


@event_emitter.on(UserSignal.USER_REGISTERED.value)
@inject
def send_user_welcome_email(
    user_email: str, *,
    notification_client: NetflixNotificationsClient = Provide[Container.notification_client],
):
    """Send 'welcome' email to user after registration."""
    notification_client.send_notification(_build_welcome_notification_payload(email=user_email))


def _build_welcome_notification_payload(*, email: str) -> NotificationIn:
    notification = NotificationIn(
        subject="Thanks for registration",
        notification_type=NotificationType.EMAIL.value,
        priority=NotificationPriority.URGENT.value,
        recipient_list=[email],
        content="You have created an account on netflix.com",
    )
    return notification
