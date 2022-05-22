from uuid import UUID

import pytest

from roles import types as rt
from users import types as ut

from .constants import ROLE_UUID, USER_UUID


@pytest.fixture
def user_uuid() -> str:
    return USER_UUID


@pytest.fixture
def role_uuid() -> str:
    return ROLE_UUID


@pytest.fixture
def user_dto(model_factory, user_uuid, role_uuid) -> ut.User:
    roles = [rt.Role(id=UUID(role_uuid), name="CustomRole", description="Description")]
    return model_factory.create_factory(ut.User).build(
        id=user_uuid, password="test", email="user@test.com", active=True, roles=roles)
