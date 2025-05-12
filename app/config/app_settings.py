"""
SQLAlchemy async configuration for the application.
Sets up database engine, sessions, and migrations.
"""

from advanced_alchemy.base import orm_registry
from advanced_alchemy.extensions.litestar import (
    AlembicAsyncConfig,
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
)
from personal_growth_sdk.multi_agent.models import *  # noqa: F403
from personal_growth_sdk.multi_agent.models.base import multi_aget_metadata as metadata

from app.config.base_settings import get_settings

# Configure route_registry with project metadata
orm_registry.metadata = metadata
settings = get_settings()

orm_registry.metadata.schema = settings.postgres.SCHEMA

# Main SQLAlchemy async configuration
alchemy = SQLAlchemyAsyncConfig(
    engine_instance=settings.postgres.get_engine(),
    before_send_handler='autocommit',  # Auto-commit transactions
    session_dependency_key='db_session',  # DI key for sessions
    session_config=AsyncSessionConfig(
        expire_on_commit=False  # Keep instances after commit
    ),
    alembic_config=AlembicAsyncConfig(
        version_table_name=settings.postgres.MIGRATION_DDL_VERSION_TABLE,
        script_config=settings.postgres.MIGRATION_CONFIG,
        script_location=settings.postgres.MIGRATION_PATH,
        version_table_schema=settings.postgres.SCHEMA,
    ),
    metadata=orm_registry.metadata,
)
