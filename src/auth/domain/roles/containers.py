from dependency_injector import containers, providers

from . import repositories


class RoleContainer(containers.DeclarativeContainer):
    """App DI container."""

    role_repository = providers.Singleton(repositories.RoleRepository)
