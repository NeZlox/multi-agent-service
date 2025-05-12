"""
Metaclass-based Singleton implementation.

This module provides `SingletonMeta`, a metaclass that ensures only one instance
of a given class is created during the application lifecycle.
"""
__all__ = ['SingletonMeta']

from typing import Any, ClassVar


class SingletonMeta(type):
    """
    Metaclass for implementing the Singleton pattern.
    """

    _instances: ClassVar[dict[type, Any]] = {}

    def __call__(cls, *args, **kwargs):
        """
        Return the cached instance or create one if this is the first call.

        This override guarantees “exactly one” semantics without changing the
        public constructor signature of the target class.

        Returns:
            The singleton instance of the class.
        """

        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)  # noqa: UP008
        return cls._instances[cls]
