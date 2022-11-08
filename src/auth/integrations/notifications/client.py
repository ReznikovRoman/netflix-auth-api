from .schemas import NotificationIn, NotificationShortDetails


class NetflixNotificationsClient:
    """Netflix Notifications API client."""

    # TODO: create Netflix API clients and publish to PyPI repository/GitHub
    # TODO: add repository in `integrations.notifications`

    def send_notification(self, notification: NotificationIn) -> NotificationShortDetails:
        """Send notification to user."""
