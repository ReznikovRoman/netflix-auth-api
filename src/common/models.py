import uuid

import sqlalchemy as sa
from flask_sqlalchemy import Model as _Model
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr


class BaseModel(_Model):
    """Базовая модель приложения."""

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):  # noqa: N805
        return cls.__name__.lower()


class TimeStampedMixin:
    """Миксин для определения timestamp полей."""

    __abstract__ = True

    __created_at_name__ = "created_at"
    __updated_at_name__ = "updated_at"
    __datetime_func__ = sa.func.now()

    created_at = sa.Column(
        __created_at_name__,
        sa.TIMESTAMP(timezone=False),
        default=__datetime_func__,
        nullable=False,
    )

    updated_at = sa.Column(
        __updated_at_name__,
        sa.TIMESTAMP(timezone=False),
        default=__datetime_func__,
        onupdate=__datetime_func__,
        nullable=False,
    )


class UUIDMixin:
    """Миксин для определения UUID в качестве PK."""

    __abstract__ = True

    __id_name__ = "id"
    __id_func__ = uuid.uuid4

    id = sa.Column(  # noqa: VNE003
        __id_name__,
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        default=__id_func__,
    )
