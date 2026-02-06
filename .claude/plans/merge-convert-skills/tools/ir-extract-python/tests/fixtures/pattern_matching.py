"""Pattern matching examples (Python 3.10+) for testing."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Point:
    """A 2D point for pattern matching examples."""

    x: float
    y: float


def match_literal(value: int) -> str:
    """Match against literal values."""
    match value:
        case 0:
            return "zero"
        case 1:
            return "one"
        case 2:
            return "two"
        case _:
            return "other"


def match_sequence(seq: list[int]) -> str:
    """Match against sequences."""
    match seq:
        case []:
            return "empty"
        case [x]:
            return f"single: {x}"
        case [x, y]:
            return f"pair: {x}, {y}"
        case [x, *rest]:
            return f"head: {x}, tail: {rest}"


def match_mapping(data: dict[str, Any]) -> str:
    """Match against mappings."""
    match data:
        case {"type": "error", "message": msg}:
            return f"Error: {msg}"
        case {"type": "success", "data": d}:
            return f"Success: {d}"
        case {"type": t}:
            return f"Unknown type: {t}"
        case _:
            return "Invalid data"


def match_class(obj: Any) -> str:
    """Match against class patterns."""
    match obj:
        case Point(x=0, y=0):
            return "origin"
        case Point(x=0, y=y):
            return f"on y-axis at {y}"
        case Point(x=x, y=0):
            return f"on x-axis at {x}"
        case Point(x=x, y=y):
            return f"point at ({x}, {y})"
        case _:
            return "not a point"


def match_with_guard(value: int) -> str:
    """Match with guard conditions."""
    match value:
        case n if n < 0:
            return "negative"
        case n if n == 0:
            return "zero"
        case n if n < 10:
            return "small positive"
        case n if n < 100:
            return "medium"
        case _:
            return "large"


def match_or_patterns(char: str) -> str:
    """Match with or patterns."""
    match char:
        case "a" | "e" | "i" | "o" | "u":
            return "vowel"
        case "y":
            return "sometimes vowel"
        case _:
            return "consonant"


def match_as_pattern(data: tuple[int, int]) -> str:
    """Match with as patterns."""
    match data:
        case (0, 0) as origin:
            return f"at origin: {origin}"
        case (x, y) as point if x == y:
            return f"on diagonal: {point}"
        case (x, y):
            return f"point: ({x}, {y})"


def match_nested(data: dict[str, Any]) -> str:
    """Match with nested patterns."""
    match data:
        case {"user": {"name": name, "role": "admin"}}:
            return f"Admin user: {name}"
        case {"user": {"name": name, "role": role}}:
            return f"User: {name} ({role})"
        case {"error": {"code": code, "message": msg}}:
            return f"Error {code}: {msg}"
        case _:
            return "Unknown format"


def match_complex_sequence(items: list[dict[str, Any]]) -> str:
    """Match complex sequence patterns."""
    match items:
        case []:
            return "empty"
        case [{"type": "header", "title": title}, *body, {"type": "footer"}]:
            return f"document: {title} with {len(body)} sections"
        case [{"type": "header", "title": title}, *body]:
            return f"document without footer: {title}"
        case _:
            return "malformed document"
