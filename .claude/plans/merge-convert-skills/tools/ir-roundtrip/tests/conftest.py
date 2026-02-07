"""Pytest fixtures for ir-roundtrip tests.

Provides fixtures for:
- Sample Python code at various complexity levels
- Test configurations
- Mock extractors and synthesizers
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

# Add tools to path
TOOLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(TOOLS_DIR / "ir-core"))
sys.path.insert(0, str(TOOLS_DIR / "ir-extract-python"))
sys.path.insert(0, str(TOOLS_DIR / "ir-extract-rust"))
sys.path.insert(0, str(TOOLS_DIR / "ir-synthesize-python"))
sys.path.insert(0, str(TOOLS_DIR / "ir-synthesize-rust"))
sys.path.insert(0, str(TOOLS_DIR / "ir-validate"))
sys.path.insert(0, str(TOOLS_DIR / "ir-roundtrip"))


# =============================================================================
# Marker Registration
# =============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests requiring full toolchain")
    config.addinivalue_line("markers", "l1: marks tests for L1 (syntactic) comparison")
    config.addinivalue_line("markers", "l2: marks tests for L2 (operational) comparison")
    config.addinivalue_line("markers", "l3: marks tests for L3 (semantic) comparison")


# =============================================================================
# Sample Code Fixtures
# =============================================================================


@pytest.fixture
def simple_function() -> str:
    """Simple function for basic testing."""
    return '''def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b
'''


@pytest.fixture
def simple_function_equivalent() -> str:
    """Equivalent function with different formatting."""
    return '''def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b
'''


@pytest.fixture
def simple_function_different() -> str:
    """Function with different semantics."""
    return '''def add(a: int, b: int) -> int:
    """Subtract two integers (intentionally wrong)."""
    return a - b
'''


@pytest.fixture
def function_with_conditionals() -> str:
    """Function with conditional logic."""
    return '''def classify(x: int) -> str:
    """Classify a number."""
    if x > 0:
        return "positive"
    elif x < 0:
        return "negative"
    else:
        return "zero"
'''


@pytest.fixture
def function_with_loop() -> str:
    """Function with loop."""
    return '''def sum_list(numbers: list[int]) -> int:
    """Sum a list of numbers."""
    total = 0
    for n in numbers:
        total += n
    return total
'''


@pytest.fixture
def function_with_comprehension() -> str:
    """Function using list comprehension."""
    return '''def double_evens(numbers: list[int]) -> list[int]:
    """Double all even numbers."""
    return [x * 2 for x in numbers if x % 2 == 0]
'''


@pytest.fixture
def recursive_function() -> str:
    """Recursive function."""
    return '''def factorial(n: int) -> int:
    """Calculate factorial recursively."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)
'''


@pytest.fixture
def class_with_methods() -> str:
    """Class with methods."""
    return '''class Counter:
    """A simple counter class."""

    def __init__(self, start: int = 0) -> None:
        self.value = start

    def increment(self) -> int:
        """Increment and return new value."""
        self.value += 1
        return self.value

    def decrement(self) -> int:
        """Decrement and return new value."""
        self.value -= 1
        return self.value
'''


@pytest.fixture
def async_function() -> str:
    """Async function."""
    return '''async def fetch(url: str) -> str:
    """Fetch data from URL (mock)."""
    await asyncio.sleep(0)
    return f"data from {url}"
'''


@pytest.fixture
def function_with_exception() -> str:
    """Function that raises exceptions."""
    return '''def divide(a: int, b: int) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Division by zero")
    return a / b
'''


@pytest.fixture
def complex_module() -> str:
    """Complex module with multiple definitions."""
    return '''"""Complex module for testing."""

from typing import Generic, TypeVar

T = TypeVar("T")


def helper(x: int) -> int:
    """Helper function."""
    return x * 2


class Container(Generic[T]):
    """Generic container class."""

    def __init__(self, value: T) -> None:
        self._value = value

    @property
    def value(self) -> T:
        """Get the value."""
        return self._value

    def map(self, fn) -> "Container":
        """Apply function to value."""
        return Container(fn(self._value))


def process(items: list[int]) -> list[int]:
    """Process items."""
    return [helper(x) for x in items if x > 0]
'''


# =============================================================================
# Test Input Fixtures
# =============================================================================


@pytest.fixture
def add_test_inputs() -> list[dict[str, Any]]:
    """Test inputs for add function."""
    return [
        {"a": 1, "b": 2},
        {"a": 0, "b": 0},
        {"a": -1, "b": 1},
        {"a": 100, "b": -100},
        {"a": -5, "b": -3},
    ]


@pytest.fixture
def classify_test_inputs() -> list[dict[str, Any]]:
    """Test inputs for classify function."""
    return [
        {"x": 1},
        {"x": -1},
        {"x": 0},
        {"x": 100},
        {"x": -100},
    ]


@pytest.fixture
def factorial_test_inputs() -> list[dict[str, Any]]:
    """Test inputs for factorial function."""
    return [
        {"n": 0},
        {"n": 1},
        {"n": 5},
        {"n": 10},
    ]


@pytest.fixture
def divide_test_inputs() -> list[dict[str, Any]]:
    """Test inputs for divide function (including error case)."""
    return [
        {"a": 10, "b": 2},
        {"a": 0, "b": 5},
        {"a": 7, "b": 3},
        {"a": 10, "b": 0},  # Error case
    ]


# =============================================================================
# Toolchain Availability
# =============================================================================


@pytest.fixture
def has_extractor() -> bool:
    """Check if extractor is available."""
    try:
        from ir_extract_python import PythonExtractor

        return True
    except ImportError:
        return False


@pytest.fixture
def has_synthesizer() -> bool:
    """Check if synthesizer is available."""
    try:
        from ir_synthesize_python import PythonSynthesizer

        return True
    except ImportError:
        return False


@pytest.fixture
def has_full_toolchain(has_extractor: bool, has_synthesizer: bool) -> bool:
    """Check if full toolchain is available."""
    return has_extractor and has_synthesizer


def _check_extractor_available() -> bool:
    """Check if extractor is importable."""
    try:
        from ir_extract_python import PythonExtractor

        return True
    except ImportError:
        return False


def _check_synthesizer_available() -> bool:
    """Check if synthesizer is importable."""
    try:
        from ir_synthesize_python import PythonSynthesizer

        return True
    except ImportError:
        return False


# Skip markers based on toolchain availability
requires_extractor = pytest.mark.skipif(
    not _check_extractor_available(),
    reason="ir-extract-python not available",
)

requires_synthesizer = pytest.mark.skipif(
    not _check_synthesizer_available(),
    reason="ir-synthesize-python not available",
)

requires_full_toolchain = pytest.mark.skipif(
    not (_check_extractor_available() and _check_synthesizer_available()),
    reason="Full toolchain not available",
)
