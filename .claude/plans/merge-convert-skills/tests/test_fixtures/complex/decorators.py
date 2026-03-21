"""Decorator patterns for testing attribute extraction."""

import functools
import time
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")


def simple_decorator(func: Callable[P, T]) -> Callable[P, T]:
    """A simple decorator that logs calls."""
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


def with_retry(max_attempts: int = 3):
    """Decorator factory for retry logic."""
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    time.sleep(0.1 * (2 ** attempt))
            raise RuntimeError(f"Failed after {max_attempts} attempts") from last_error
        return wrapper
    return decorator


def memoize(func: Callable[..., T]) -> Callable[..., T]:
    """Cache function results."""
    cache: dict = {}

    @functools.wraps(func)
    def wrapper(*args) -> T:
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper


def validate_args(*validators: Callable[[any], bool]):
    """Decorator to validate arguments."""
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for i, (arg, validator) in enumerate(zip(args, validators, strict=False)):
                if not validator(arg):
                    raise ValueError(f"Argument {i} failed validation")
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Usage examples
@simple_decorator
def greet(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}!"


@memoize
def fibonacci(n: int) -> int:
    """Calculate fibonacci number with memoization."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


@with_retry(max_attempts=5)
def unreliable_operation() -> str:
    """An operation that might fail."""
    import random
    if random.random() < 0.5:
        raise RuntimeError("Random failure")
    return "success"


@validate_args(lambda x: x > 0, lambda y: y >= 0)
def safe_divide(a: float, b: float) -> float:
    """Divide with validation."""
    return a / b
