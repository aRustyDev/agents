"""Basic function definitions for testing."""


def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtract b from a."""
    return a - b


def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divide a by b.

    Raises:
        ZeroDivisionError: If b is zero.
    """
    return a / b


def greet(name: str) -> str:
    """Create a greeting message."""
    return f"Hello, {name}!"


def identity(x: int) -> int:
    """Return the input unchanged."""
    return x


def constant() -> int:
    """Return a constant value."""
    return 42
