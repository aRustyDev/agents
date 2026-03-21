"""Generic type patterns for testing type extraction."""

from collections.abc import Callable, Iterable, Sequence
from typing import Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")
K = TypeVar("K")
V = TypeVar("V")


class Box(Generic[T]):
    """A generic container for a single value."""

    def __init__(self, value: T) -> None:
        """Initialize with a value."""
        self._value = value

    def get(self) -> T:
        """Get the contained value."""
        return self._value

    def map(self, fn: Callable[[T], U]) -> "Box[U]":
        """Apply a function to the contained value."""
        return Box(fn(self._value))


class Stack(Generic[T]):
    """A generic stack implementation."""

    def __init__(self) -> None:
        """Initialize empty stack."""
        self._items: list[T] = []

    def push(self, item: T) -> None:
        """Push item onto stack."""
        self._items.append(item)

    def pop(self) -> T:
        """Pop item from stack."""
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()

    def peek(self) -> T:
        """Peek at top item."""
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items[-1]

    def is_empty(self) -> bool:
        """Check if stack is empty."""
        return len(self._items) == 0


class Pair(Generic[T, U]):
    """A generic pair of values."""

    def __init__(self, first: T, second: U) -> None:
        """Initialize pair."""
        self.first = first
        self.second = second

    def swap(self) -> "Pair[U, T]":
        """Swap the pair elements."""
        return Pair(self.second, self.first)


def identity(x: T) -> T:
    """Identity function."""
    return x


def compose(f: Callable[[T], U], g: Callable[[U], V]) -> Callable[[T], V]:
    """Compose two functions."""
    def composed(x: T) -> V:
        return g(f(x))
    return composed


def map_values(items: Sequence[T], fn: Callable[[T], U]) -> list[U]:
    """Map a function over a sequence."""
    return [fn(item) for item in items]


def filter_values(items: Iterable[T], predicate: Callable[[T], bool]) -> list[T]:
    """Filter items by predicate."""
    return [item for item in items if predicate(item)]


def group_by(items: Iterable[T], key_fn: Callable[[T], K]) -> dict[K, list[T]]:
    """Group items by a key function."""
    result: dict[K, list[T]] = {}
    for item in items:
        key = key_fn(item)
        if key not in result:
            result[key] = []
        result[key].append(item)
    return result
