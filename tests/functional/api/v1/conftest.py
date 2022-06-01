import pytest

from roles import types as rt


@pytest.fixture
def role_dto(model_factory, role_uuid) -> rt.Role:
    return model_factory.create_factory(rt.Role).build(
        id=role_uuid, name="name", description="description")


@pytest.fixture
def another_role_dto(model_factory, role_uuid) -> rt.Role:
    return model_factory.create_factory(rt.Role).build(
        id=role_uuid, name="another", description="description")
