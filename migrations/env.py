from __future__ import with_statement
 codex/add-tests-for-social-media-posts-routes


import logging
from logging.config import fileConfig
 main

from alembic import context
from flask import current_app
from logging.config import fileConfig
import logging

config = context.config
 codex/add-tests-for-social-media-posts-routes


 main
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

target_metadata = current_app.extensions['migrate'].db.metadata

 codex/add-tests-for-social-media-posts-routes
def run_migrations_offline() -> None:
    context.configure(
        url=current_app.config.get('SQLALCHEMY_DATABASE_URI'),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )


def run_migrations_offline() -> None:
    url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True,
                      dialect_opts={'paramstyle': 'named'})
 main
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = current_app.extensions['migrate'].db.engine
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

 codex/add-tests-for-social-media-posts-routes


 main
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
