from .schemas import NotificationIn, NotificationShortDetails


class NetflixNotificationsClient:
    """Клиент для работы с АПИ сервиса Netflix Notifications."""

    # TODO [Дипломный проект]: сделать клиенты ко всем микросервисам и выложить в (закрытый) PyPI репозиторий
    # TODO [Дипломный проект]: добавить репозитории к integrations.notifications

    def send_notification(self, notification: NotificationIn) -> NotificationShortDetails:
        """Отправка уведомления пользователю."""
