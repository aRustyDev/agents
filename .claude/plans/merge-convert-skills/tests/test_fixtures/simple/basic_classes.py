"""Basic class definitions for testing."""


class Point:
    """A 2D point."""

    def __init__(self, x: float, y: float) -> None:
        """Initialize point with coordinates."""
        self.x = x
        self.y = y

    def distance_from_origin(self) -> float:
        """Calculate distance from origin."""
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def __repr__(self) -> str:
        """String representation."""
        return f"Point({self.x}, {self.y})"


class Rectangle:
    """A rectangle defined by width and height."""

    def __init__(self, width: float, height: float) -> None:
        """Initialize rectangle dimensions."""
        self.width = width
        self.height = height

    @property
    def area(self) -> float:
        """Calculate area."""
        return self.width * self.height

    @property
    def perimeter(self) -> float:
        """Calculate perimeter."""
        return 2 * (self.width + self.height)


class Counter:
    """A simple counter."""

    def __init__(self, initial: int = 0) -> None:
        """Initialize counter."""
        self._value = initial

    def increment(self) -> int:
        """Increment and return new value."""
        self._value += 1
        return self._value

    def decrement(self) -> int:
        """Decrement and return new value."""
        self._value -= 1
        return self._value

    @property
    def value(self) -> int:
        """Get current value."""
        return self._value
