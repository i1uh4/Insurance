from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.models.user_models import Base as UserBase
from app.models.insurance_models import Base as InsuranceBase
from app.models.recommendation_models import Base as RecommendationBase
from app.config import DATABASE_URL

config = context.config

fileConfig(config.config_file_name)

target_metadata = [UserBase.metadata, InsuranceBase.metadata, RecommendationBase.metadata]

combined_metadata = UserBase.metadata
for metadata in [InsuranceBase.metadata, RecommendationBase.metadata]:
    for table in metadata.tables.values():
        if table.name not in combined_metadata.tables:
            combined_metadata._add_table(table.name, table.schema, table)

config.set_main_option("sqlalchemy.url", DATABASE_URL)


def get_url():
    """Get database URL from environment variable"""
    return os.environ.get("DATABASE_URL", DATABASE_URL)


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=combined_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=combined_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()