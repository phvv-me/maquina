from __future__ import annotations

from typing import Any, ClassVar


class Registry:
    """Mixin giving each hierarchy automatic subclass registration.

    Each direct child of `Registry` becomes a registry root. Every subclass
    below a root registers itself into that root's list as it is defined, so
    importing a provider module is enough to make it discoverable.
    """

    _registry: ClassVar[list[type[Registry]]]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Register each subclass into the nearest registry root."""
        super().__init_subclass__(**kwargs)

        if Registry in cls.__bases__:
            cls._registry = []
        cls.registry().append(cls)

    @classmethod
    def registry(cls) -> list[type[Registry]]:
        """Return the nearest registry root's registered subclasses."""
        root = next(base for base in cls.__mro__ if "_registry" in base.__dict__)
        return root._registry
