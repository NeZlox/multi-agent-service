"""
Automatically discovers, imports, and instantiates AIAgentGatewayInterface subclasses
from modules in this package.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil

from app.lib.logger import logger

from .ai_agent_interface import AIAgentGatewayInterface


def discover_agents() -> dict[str, AIAgentGatewayInterface]:
    """
    Imports all agent modules and returns a dict of instantiated AIAgentGatewayInterface subclasses.
    """

    agents: dict[str, AIAgentGatewayInterface] = {}
    package = '.'.join(__name__.split('.')[:-1])
    for _, module_name, _ in pkgutil.iter_modules([package.replace('.', '/')]):
        module_path = f'{package}.{module_name}'
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, '__all__'):
                for cls_name in module.__all__:
                    cls = getattr(module, cls_name, None)
                    if (
                            isinstance(cls, type)
                            and issubclass(cls, AIAgentGatewayInterface)
                            and not inspect.isabstract(cls)
                    ):
                        agents[cls().name] = cls()
        except Exception as exc:
            logger.critical(f'Failed to import module {module_path}: {exc}')

    return agents
