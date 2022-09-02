from __future__ import with_statement, annotations

import logging
from logging.config import fileConfig
from typing import TYPE_CHECKING

from flask import current_app

from alembic import context

if TYPE_CHECKING:
    from sqlalchemy import Table

config = context.config

fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

config.set_main_option(
    "sqlalchemy.url",
    str(current_app.extensions["migrate"].db.get_engine().url).replace("%", "%%"),
)
target_metadata = current_app.extensions["migrate"].db.metadata


def include_object(object_: Table, name: str, type_: str, reflected, compare_to) -> bool:
    """Настраиваем правила автогенерации миграций.

    https://alembic.sqlalchemy.org/en/latest/autogenerate.html#omitting-based-on-object
    """
    tables_to_exclude = (
        "loginlog", "loginlog_mobile", "loginlog_tablet", "loginlog_pc",
    )
    if type_ == "table" and object_.name in tables_to_exclude:
        return False
    return True


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    connectable = current_app.extensions["migrate"].db.get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            include_object=include_object,
            **current_app.extensions["migrate"].configure_args
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
