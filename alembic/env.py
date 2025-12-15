import os
import sys

# ДОБАВЬ ПУТИ К ТВОЕМУ КОДУ
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend/app'))

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Импорт твоих моделей
from app.database import Base
from app.models import *

target_metadata = Base.metadata

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    raise NotImplementedError("Offline mode not supported")
else:
    run_migrations_online()
