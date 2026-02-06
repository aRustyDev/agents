"""Comprehension examples for testing pattern detection."""

from typing import Iterable


def list_comprehension_examples() -> None:
    """Various list comprehension patterns."""
    # Simple list comprehension
    squares = [x ** 2 for x in range(10)]

    # With condition
    evens = [x for x in range(20) if x % 2 == 0]

    # Multiple conditions
    divisible = [x for x in range(100) if x % 2 == 0 if x % 3 == 0]

    # Nested iteration
    pairs = [(x, y) for x in range(3) for y in range(3)]

    # Nested comprehension
    matrix = [[i * j for j in range(5)] for i in range(5)]

    # With function call
    processed = [process(x) for x in items]

    # With method call
    upper_names = [name.upper() for name in names]


def dict_comprehension_examples() -> None:
    """Various dictionary comprehension patterns."""
    # Simple dict comprehension
    squares = {x: x ** 2 for x in range(10)}

    # From pairs
    mapping = {k: v for k, v in pairs}

    # With condition
    positive = {k: v for k, v in items.items() if v > 0}

    # Key transformation
    inverted = {v: k for k, v in original.items()}


def set_comprehension_examples() -> None:
    """Various set comprehension patterns."""
    # Simple set comprehension
    unique_squares = {x ** 2 for x in range(-5, 6)}

    # With condition
    unique_evens = {x for x in items if x % 2 == 0}


def generator_expression_examples() -> None:
    """Various generator expression patterns."""
    # As function argument
    total = sum(x ** 2 for x in range(100))

    # Assigned to variable
    gen = (x ** 2 for x in range(1000000))

    # With condition
    evens_gen = (x for x in range(100) if x % 2 == 0)


def complex_comprehension(data: dict[str, list[int]]) -> dict[str, int]:
    """Comprehension with complex expressions."""
    return {
        key: sum(value)
        for key, value in data.items()
        if len(value) > 0
    }


def nested_comprehension_complex() -> list[list[int]]:
    """Complex nested comprehension."""
    return [
        [i * j for j in range(1, 6) if j % 2 == 0]
        for i in range(1, 11)
        if i % 2 == 1
    ]


def walrus_in_comprehension() -> list[int]:
    """Comprehension with walrus operator (Python 3.8+)."""
    # Uses assignment expression
    return [y for x in range(10) if (y := x ** 2) > 25]
