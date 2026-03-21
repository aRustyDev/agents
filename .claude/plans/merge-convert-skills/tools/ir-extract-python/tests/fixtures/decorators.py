"""Decorator examples for testing decorator pattern extraction."""

from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property, lru_cache, wraps
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


# Simple decorator
def simple_decorator(func: Callable[P, R]) -> Callable[P, R]:
    """A simple decorator that wraps a function."""
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


# Decorator factory
def repeat(times: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator factory that repeats a function."""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for _ in range(times - 1):
                func(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Decorator with arguments
def validate_args(**validators: Callable[[Any], bool]) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator that validates arguments."""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Validation logic would go here
            return func(*args, **kwargs)
        return wrapper
    return decorator


@simple_decorator
def decorated_function() -> str:
    """A function with a simple decorator."""
    return "hello"


@repeat(3)
def repeated_function() -> None:
    """A function that repeats."""
    print("repeating")


@validate_args(x=lambda v: v > 0, y=lambda v: isinstance(v, str))
def validated_function(x: int, y: str) -> str:
    """A function with argument validation."""
    return f"{y}: {x}"


# Multiple decorators
@simple_decorator
@repeat(2)
def multiply_decorated() -> None:
    """Function with multiple decorators."""
    print("decorated")


# Class with decorated methods
class DecoratedMethods:
    """Class demonstrating method decorators."""

    @property
    def value(self) -> int:
        """A property decorator."""
        return self._value

    @value.setter
    def value(self, v: int) -> None:
        """Property setter."""
        self._value = v

    @classmethod
    def from_string(cls, s: str) -> "DecoratedMethods":
        """Class method decorator."""
        return cls()

    @staticmethod
    def utility() -> int:
        """Static method decorator."""
        return 42

    @lru_cache(maxsize=100)
    def cached_computation(self, x: int) -> int:
        """Method with lru_cache."""
        return x ** 2

    @cached_property
    def expensive_value(self) -> int:
        """Cached property decorator."""
        return sum(range(1000))


@dataclass
class DataClassExample:
    """Dataclass decorator."""
    name: str
    value: int


@dataclass(frozen=True)
class FrozenDataClass:
    """Frozen dataclass."""
    x: int
    y: int


@dataclass(order=True, slots=True)
class SlottedDataClass:
    """Dataclass with slots and ordering."""
    name: str
    priority: int


# Context manager decorator
@contextmanager
def managed_resource(name: str):
    """Context manager using decorator."""
    print(f"Acquiring {name}")
    try:
        yield name
    finally:
        print(f"Releasing {name}")


# Custom class decorator
def singleton(cls: type[R]) -> type[R]:
    """Singleton decorator for classes."""
    instances: dict[type, Any] = {}

    @wraps(cls)
    def wrapper(*args: Any, **kwargs: Any) -> R:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper  # type: ignore


@singleton
class SingletonClass:
    """A singleton class."""

    def __init__(self, value: int) -> None:
        self.value = value


# Decorator that modifies the class
def add_method(cls: type) -> type:
    """Decorator that adds a method to a class."""
    def new_method(self: Any) -> str:
        return "added method"
    cls.added_method = new_method
    return cls


@add_method
class ClassWithAddedMethod:
    """Class with dynamically added method."""
    pass


# Async decorator
def async_decorator(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator for async functions."""
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print("Before async call")
        result = await func(*args, **kwargs)  # type: ignore
        print("After async call")
        return result
    return wrapper  # type: ignore


@async_decorator
async def decorated_async_function() -> str:
    """Async function with decorator."""
    return "async result"
