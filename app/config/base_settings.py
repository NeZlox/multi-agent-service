"""
Application configuration settings loader.
Centralized environment variables and runtime configuration.
"""

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from litestar.data_extractors import RequestExtractorField, ResponseExtractorField
from litestar.serialization import decode_json, encode_json
from litestar.utils.module_loader import module_to_os_path
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

__all__ = ['get_settings']


def str_to_bool(value: str) -> bool:
    """
    Converts string to boolean (accepts multiple true formats)
    """

    return value.lower() in {'1', 'true', 'yes', 'on'}


BASE_DIR = module_to_os_path()


@dataclass
class PostgresSettings:
    """
    PostgresSQL database configuration
    """

    DSN: str = field(default_factory=lambda: os.getenv('POSTGRES_DSN'))

    POOL_MAX_OVERFLOW: int = field(default_factory=lambda: int(os.getenv('DATABASE_MAX_POOL_OVERFLOW', '20')))
    POOL_SIZE: int = field(default_factory=lambda: int(os.getenv('DATABASE_POOL_SIZE', '30')))
    POOL_TIMEOUT: int = field(default_factory=lambda: int(os.getenv('DATABASE_POOL_TIMEOUT', '30')))
    POOL_RECYCLE: int = field(default_factory=lambda: int(os.getenv('DATABASE_POOL_RECYCLE', '300')))

    MIGRATION_CONFIG: str = f'{BASE_DIR}/infrastructure/db/migrations/alembic.ini'
    MIGRATION_PATH: str = f'{BASE_DIR}/infrastructure/db/migrations'
    MIGRATION_DDL_VERSION_TABLE: str = 'ddl_version'

    SCHEMA: str = field(default_factory=lambda: os.getenv('POSTGRES_SCHEMA', 'public'))

    _engine_instance: AsyncEngine | None = None

    @property
    def engine(self) -> AsyncEngine:
        return self.get_engine()

    def get_engine(self) -> AsyncEngine:
        """
        Creates and configures async database engine
        """

        if self._engine_instance is not None:
            return self._engine_instance
        engine = create_async_engine(
            url=self.DSN,
            future=True,
            json_serializer=encode_json,
            json_deserializer=decode_json,
            # isolation_level='AUTOCOMMIT',
            max_overflow=self.POOL_MAX_OVERFLOW,
            pool_size=self.POOL_SIZE,
            pool_timeout=self.POOL_TIMEOUT,
            pool_recycle=self.POOL_RECYCLE,
            pool_use_lifo=True,
        )

        @event.listens_for(engine.sync_engine, 'connect')
        def _sqla_on_connect(dbapi_connection: Any, _: Any) -> Any:
            """
            Configures new database connections
            """

            def encoder(bin_value: bytes) -> bytes:
                return b'\x01' + encode_json(bin_value)

            def decoder(bin_value: bytes) -> Any:
                return decode_json(bin_value[1:])

            dbapi_connection.await_(
                dbapi_connection.driver_connection.set_type_codec(
                    'jsonb',
                    encoder=encoder,
                    decoder=decoder,
                    schema='pg_catalog',
                    format='binary',
                ),
            )
            dbapi_connection.await_(
                dbapi_connection.driver_connection.set_type_codec(
                    'json',
                    encoder=encoder,
                    decoder=decoder,
                    schema='pg_catalog',
                    format='binary',
                ),
            )

            # Schema initialization
            cursor = dbapi_connection.cursor()
            cursor.execute(f'CREATE SCHEMA IF NOT EXISTS {self.SCHEMA}')
            cursor.execute(f'SET search_path TO {self.SCHEMA}')
            cursor.execute(f'CREATE EXTENSION IF NOT EXISTS ltree SCHEMA {self.SCHEMA}')
            cursor.close()

        self._engine_instance = engine
        return self._engine_instance


@dataclass
class LogSettings:
    """
    Structured logging configuration
    """

    EXCLUDE_PATHS: str = r'\A(?!x)x'
    HTTP_EVENT: str = 'HTTP'
    INCLUDE_COMPRESSED_BODY: bool = False
    LEVEL: int = field(default_factory=lambda: int(os.getenv('LOG_LEVEL', '10')))
    REQUEST_FIELDS: list[RequestExtractorField] = field(
        default_factory=lambda: ['method', 'path', 'path_params', 'query', 'body'])
    RESPONSE_FIELDS: list[ResponseExtractorField] = field(default_factory=lambda: ['status_code'])
    JSON: bool = field(default_factory=lambda: str_to_bool(os.getenv('LOG_JSON', 'false')))


@dataclass
class AppSettings:
    """
    Core application settings
    """

    NAME: str = 'multi-agent-service'
    VERSION: str = '1.0.0'

    MODE: str = field(default_factory=lambda: os.getenv('MODE', 'DEV'))
    DEBUG: bool = field(default_factory=lambda: str_to_bool(os.getenv('DEBUG', 'False')))

    JWT_ALGORITHM: str = field(default_factory=lambda: os.getenv('JWT_ALGORITHM'))
    JWT_PUBLIC_KEY: str = field(default_factory=lambda: os.getenv('JWT_PUBLIC_KEY'))

    AUTH_SERVICE_URL: str = field(default_factory=lambda: os.getenv('AUTH_SERVICE_URL'))
    SNAPSHOT_SERVICE_URL: str = field(default_factory=lambda: os.getenv('SNAPSHOT_SERVICE_URL'))
    AGENDA_SERVICE_URL: str = field(default_factory=lambda: os.getenv('AGENDA_SERVICE_URL'))

    def __post_init__(self):
        """
        Post-initialization validation
        """

        if self.MODE not in {'PROD', 'STAGE', 'DEV', 'TEST'}:
            raise ValueError(f'Invalid MODE: {self.MODE}. Must be one of `PROD`, `STAGE`, `DEV`, `TEST`.')

        # Load from pyproject.toml if exists
        with open(f'{os.curdir}/pyproject.toml') as file:
            from app.lib.utils.pyproject import PyProject, decode
            content: PyProject = decode(file.read())
            self.NAME = content.tool['poetry']['name']
            self.VERSION = content.tool['poetry']['version']


@dataclass
class Settings:
    """
    Aggregate settings container
    """

    app: AppSettings = field(default_factory=AppSettings)
    postgres: PostgresSettings = field(default_factory=PostgresSettings)
    log: LogSettings = field(default_factory=LogSettings)

    @classmethod
    def from_env(cls, env_name='.env') -> 'Settings':
        """
        Load settings from environment file
        """

        env_path = Path(f'{os.curdir}/{env_name}')
        if env_path.is_file():
            from dotenv import load_dotenv

            load_dotenv(env_path)
        return Settings()


@lru_cache(maxsize=1, typed=True)
def get_settings() -> Settings:
    """
    Cached settings factory
    """

    return Settings.from_env()
