"""Metaprogramming patterns that may cause extraction issues."""

from typing import Any, TypeVar

T = TypeVar("T")


class SingletonMeta(type):
    """Metaclass for singleton pattern."""

    _instances: dict[type, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """Create or return singleton instance."""
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    """A singleton class."""

    def __init__(self, value: int = 0) -> None:
        """Initialize singleton."""
        self.value = value


class RegistryMeta(type):
    """Metaclass that registers all subclasses."""

    registry: dict[str, type] = {}

    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> type:
        """Create class and register it."""
        cls = super().__new__(mcs, name, bases, namespace)
        if name != "Registered":
            mcs.registry[name] = cls
        return cls


class Registered(metaclass=RegistryMeta):
    """Base class for registered types."""
    pass


class Validated:
    """Descriptor for validated attributes."""

    def __init__(self, validator: callable) -> None:
        """Initialize with validator."""
        self.validator = validator
        self.name = ""

    def __set_name__(self, owner: type, name: str) -> None:
        """Store attribute name."""
        self.name = f"_{name}"

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        """Get validated value."""
        if obj is None:
            return self
        return getattr(obj, self.name, None)

    def __set__(self, obj: Any, value: Any) -> None:
        """Validate and set value."""
        if not self.validator(value):
            raise ValueError(f"Invalid value for {self.name}: {value}")
        setattr(obj, self.name, value)


class Person:
    """Person with validated age."""

    age = Validated(lambda x: isinstance(x, int) and 0 <= x <= 150)

    def __init__(self, name: str, age: int) -> None:
        """Initialize person."""
        self.name = name
        self.age = age


def with_slots(*names: str):
    """Class decorator to add __slots__."""
    def decorator(cls: type) -> type:
        cls.__slots__ = names
        return cls
    return decorator


@with_slots("x", "y")
class SlottedPoint:
    """Point with __slots__."""

    def __init__(self, x: float, y: float) -> None:
        """Initialize point."""
        self.x = x
        self.y = y
