"""Simple function fixture for testing basic extraction."""


def greet(name: str) -> str:
    """Greet someone by name.

    Args:
        name: The person's name to greet.

    Returns:
        A greeting message.
    """
    return f"Hello, {name}!"


def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


def process_items(items: list[int], multiplier: int = 2) -> list[int]:
    """Process a list of items by multiplying each by a factor."""
    return [item * multiplier for item in items]
