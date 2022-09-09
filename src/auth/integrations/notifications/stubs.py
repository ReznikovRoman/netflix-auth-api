import logging

from .client import NetflixNotificationsClient
from .schemas import NotificationIn, NotificationShortDetails


class NetflixNotificationsClientStub(NetflixNotificationsClient):
    """Стаб клиента для работы с АПИ сервиса Netflix Notifications."""

    def send_notification(self, notification: NotificationIn) -> NotificationShortDetails:
        logging.info(f"Send notification to {notification.recipient_list}")
        return NotificationShortDetails(notification_id="xxx", queue="default")
