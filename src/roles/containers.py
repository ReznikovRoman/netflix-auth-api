from dependency_injector import containers, providers

from . import repositories


class RoleContainer(containers.DeclarativeContainer):
    """Контейнер с зависимостями приложения."""

    role_repository = providers.Factory(
        repositories.RoleRepository,
    )
