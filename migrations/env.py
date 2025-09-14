from __future__ import with_statement
 codex/update-test-setup-to-use-migrations
import logging
from logging.config import fileConfig

from logging.config import fileConfig
import os

 main
from alembic import context
from flask import current_app

config = context.config
 codex/update-test-setup-to-use-migrations
if config.config_file_name:


# Interpret the config file for Python logging.
if config.config_file_name is not None and os.path.exists(config.config_file_name):
 main
    fileConfig(config.config_file_name)

target_metadata = current_app.extensions['migrate'].db.metadata

 codex/update-test-setup-to-use-migrations
def run_migrations_offline():
    url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={'paramstyle': 'named'})
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = current_app.extensions['migrate'].db.engine
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()



def run_migrations_offline() -> None:
    url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = current_app.extensions['migrate'].db.engine

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


 main
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
