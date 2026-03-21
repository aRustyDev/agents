"""Class definitions fixture for testing class extraction."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generic, Protocol, TypeVar

T = TypeVar("T")


class SimpleClass:
    """A simple class with attributes and methods."""

    class_attribute: str = "default"

    def __init__(self, name: str, value: int) -> None:
        """Initialize the instance.

        Args:
            name: Instance name.
            value: Instance value.
        """
        self.name = name
        self.value = value

    def get_info(self) -> str:
        """Get instance information."""
        return f"{self.name}: {self.value}"

    @property
    def doubled_value(self) -> int:
        """Get doubled value."""
        return self.value * 2

    @classmethod
    def from_string(cls, s: str) -> "SimpleClass":
        """Create instance from string."""
        parts = s.split(":")
        return cls(parts[0], int(parts[1]))

    @staticmethod
    def validate(value: int) -> bool:
        """Validate a value."""
        return value >= 0


class Animal(ABC):
    """Abstract base class for animals."""

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def speak(self) -> str:
        """Make the animal speak."""
        ...

    def greet(self) -> str:
        """Greet with the animal's sound."""
        return f"{self.name} says: {self.speak()}"


class Dog(Animal):
    """A dog that can bark."""

    def speak(self) -> str:
        """Dogs say woof."""
        return "Woof!"


class Cat(Animal):
    """A cat that can meow."""

    def speak(self) -> str:
        """Cats say meow."""
        return "Meow!"


@dataclass
class Point:
    """A 2D point."""

    x: float
    y: float

    def distance_from_origin(self) -> float:
        """Calculate distance from origin."""
        return (self.x ** 2 + self.y ** 2) ** 0.5


@dataclass(frozen=True)
class ImmutablePoint:
    """An immutable 2D point."""

    x: float
    y: float


@dataclass
class Rectangle:
    """A rectangle defined by two corner points."""

    top_left: Point
    bottom_right: Point
    tags: list[str] = field(default_factory=list)

    @property
    def width(self) -> float:
        """Get rectangle width."""
        return abs(self.bottom_right.x - self.top_left.x)

    @property
    def height(self) -> float:
        """Get rectangle height."""
        return abs(self.bottom_right.y - self.top_left.y)

    @property
    def area(self) -> float:
        """Get rectangle area."""
        return self.width * self.height


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

    def __len__(self) -> int:
        """Get stack size."""
        return len(self._items)


class Drawable(Protocol):
    """Protocol for drawable objects."""

    def draw(self) -> None:
        """Draw the object."""
        ...


class Sizeable(Protocol):
    """Protocol for objects with size."""

    def size(self) -> int:
        """Get the size."""
        ...


class ClassWithSlots:
    """A class using __slots__ for memory optimization."""

    __slots__ = ["x", "y", "z"]

    def __init__(self, x: int, y: int, z: int) -> None:
        self.x = x
        self.y = y
        self.z = z
