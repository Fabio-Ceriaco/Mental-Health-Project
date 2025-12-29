from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
import sys
from pathlib import Path

# Ajusta sys.path para encontrar 'app'
repo_root = Path(__file__).resolve().parents[3]  # Alembic está em app/database/alembic/
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from APP.DATABASE.db_conn import Base, DATABASE_URL
import APP.MODELS  # importa todos os models listados em models/__init__.py

# Configuração Alembic
config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
