"""
Dynamic module importer for proxy route definitions.

This utility scans the `app.config.proxy_routes` package and ensures
each file is imported exactly once. This triggers execution of their
`route_registry.register()` calls and loads all declared proxy routes.

Intended to be used at application startup, before the middleware
depends on any registered routing logic.
"""

from importlib import import_module
from pathlib import Path
from pkgutil import iter_modules

PKG = 'app.config.proxy_routes'


def load_all() -> None:
    """
    Import every `.py` module in the `proxy_routes` package.

    This ensures all route registrations are executed during app startup.
    Skips private (`_`) and compiled (`.pyc`) files.

    Example:
        >>> load_all()
        # Automatically imports:
        # - app.config.proxy_routes.auth
        # - app.config.proxy_routes.agenda
        # - ...
    """

    package_dir = Path(import_module(PKG).__file__).parent
    for mod in iter_modules([str(package_dir)]):
        if mod.name.startswith('_'):
            continue  # skip private / compiled
        import_module(f'{PKG}.{mod.name}')
