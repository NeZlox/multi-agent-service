"""
Application plugins configuration.
Includes database, logging, and server plugins.
"""

from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin
from litestar.plugins.structlog import StructlogPlugin
from litestar_granian import GranianPlugin

from app.config import app_settings as config
from app.lib.logger import log

# Structured logging plugin
structlog = StructlogPlugin(config=log)

# SQLAlchemy database plugin
alchemy = SQLAlchemyPlugin(config=config.alchemy)

# Granian ASGI server plugin
granian = GranianPlugin()
