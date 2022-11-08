from user_agents import parse

from auth.common.types import PageNumberPagination
from auth.infrastructure.db.postgres import db_session

from .. import types
from ..models import LoginLog


class LoginLogRepository:
    """Login log records repository."""

    @staticmethod
    def get_user_login_history(
        user: types.User, pagination: PageNumberPagination | None = None,
    ) -> list[types.LoginLog]:
        """Get paginated user login log records."""
        login_logs = LoginLog.query.filter_by(user_id=user.id)
        if pagination is None:
            return [login_log.to_dto(user=user) for login_log in login_logs]
        login_logs = login_logs.paginate(pagination.page, pagination.per_page, error_out=False)
        return [login_log.to_dto(user=user) for login_log in login_logs.items]

    def create_log_record(self, user: types.User, ip_addr: str, user_agent: str) -> types.LoginLog:
        """Create new login log record."""
        device_type = self._get_device_type_from_user_agent(user_agent)
        login_log = LoginLog(user_id=user.id, user_agent=user_agent, ip_addr=ip_addr, device_type=device_type)
        with db_session() as session:
            session.add(login_log)
        return login_log.to_dto(user=user)

    @staticmethod
    def _get_device_type_from_user_agent(user_agent: str) -> types.LoginLog.DeviceType:
        """Identify device by a 'User Agent'."""
        user_agent = parse(user_agent)
        if user_agent.is_mobile:
            return types.LoginLog.DeviceType.MOBILE
        elif user_agent.is_tablet:
            return types.LoginLog.DeviceType.TABLET
        return types.LoginLog.DeviceType.PC
