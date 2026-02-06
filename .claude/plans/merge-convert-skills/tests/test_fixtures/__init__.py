"""Test fixtures for integration tests.

This package contains Python source files organized by complexity:

- simple/: Basic functions and simple classes
- complex/: Complex patterns (async, generics, decorators, comprehensions)
- edge_cases/: Edge cases and error conditions
- preservation/: Files for each preservation level verification

Each fixture is designed to test specific aspects of the extraction/synthesis
pipeline.
"""

from pathlib import Path

FIXTURES_DIR = Path(__file__).parent


def load_fixture(category: str, name: str) -> str:
    """Load a fixture file.

    Args:
        category: Fixture category (simple, complex, edge_cases, preservation)
        name: Fixture file name (without .py extension)

    Returns:
        Source code as string
    """
    path = FIXTURES_DIR / category / f"{name}.py"
    return path.read_text()


def list_fixtures(category: str) -> list[str]:
    """List available fixtures in a category.

    Args:
        category: Fixture category

    Returns:
        List of fixture names (without .py extension)
    """
    category_dir = FIXTURES_DIR / category
    if not category_dir.exists():
        return []
    return [f.stem for f in category_dir.glob("*.py") if f.name != "__init__.py"]
