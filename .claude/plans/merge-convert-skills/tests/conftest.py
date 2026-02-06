"""Shared pytest fixtures for integration tests.

This module provides fixtures for:
- Sample Python source code (simple, complex, edge cases)
- Sample IR structures
- Temporary database connections
- Configuration objects

The fixtures are organized to support testing at all preservation levels (L1-L5).
"""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator

import pytest

# Add tools to path for imports
TOOLS_DIR = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR / "ir-core"))
sys.path.insert(0, str(TOOLS_DIR / "ir-extract-python"))
sys.path.insert(0, str(TOOLS_DIR / "ir-synthesize-python"))
sys.path.insert(0, str(TOOLS_DIR / "ir-validate"))
sys.path.insert(0, str(TOOLS_DIR / "ir-query"))

from ir_core import (
    IRVersion,
    Module,
    ModuleMetadata,
    TypeDef,
    TypeKind,
    TypeBody,
    TypeRef,
    TypeRefKind,
    Function,
    Param,
    Binding,
    Lifetime,
    LifetimeKind,
    Mutability,
    Visibility,
    ControlFlowGraph,
    Block,
    Terminator,
    TerminatorKind,
    Effect,
    EffectKind,
    GapMarker,
    GapType,
    Severity,
    PreservationLevel,
    PreservationStatus,
    SemanticAnnotation,
    AnnotationSource,
    ExtractionMode,
    ExtractConfig,
)
from ir_core.base import SynthConfig, OutputFormat


# =============================================================================
# Marker Definitions
# =============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "roundtrip: marks tests as roundtrip tests")
    config.addinivalue_line("markers", "preservation: marks tests as preservation level tests")
    config.addinivalue_line("markers", "l1: marks tests for L1 (syntactic) equivalence")
    config.addinivalue_line("markers", "l2: marks tests for L2 (operational) equivalence")
    config.addinivalue_line("markers", "l3: marks tests for L3 (semantic) equivalence")


# =============================================================================
# Python Source Fixtures
# =============================================================================


@pytest.fixture
def sample_python_source() -> str:
    """Simple Python function for basic testing."""
    return '''"""Sample module for testing."""

def greet(name: str) -> str:
    """Greet someone by name.

    Args:
        name: The person's name.

    Returns:
        A greeting message.
    """
    return f"Hello, {name}!"


def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b
'''


@pytest.fixture
def sample_python_class() -> str:
    """Python class for testing type extraction."""
    return '''"""Sample class module."""

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class Point:
    """A 2D point."""
    x: float
    y: float

    def distance_from_origin(self) -> float:
        """Calculate distance from origin."""
        return (self.x ** 2 + self.y ** 2) ** 0.5


class Stack(Generic[T]):
    """A generic stack implementation."""

    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        """Push item onto stack."""
        self._items.append(item)

    def pop(self) -> T:
        """Pop item from stack."""
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()

    def is_empty(self) -> bool:
        """Check if stack is empty."""
        return len(self._items) == 0
'''


@pytest.fixture
def sample_python_async() -> str:
    """Async Python code for testing effect extraction."""
    return '''"""Async module for testing."""

import asyncio
from typing import AsyncIterator


async def fetch_data(url: str) -> str:
    """Fetch data from URL."""
    await asyncio.sleep(0.1)  # Simulate network delay
    return f"Data from {url}"


async def process_urls(urls: list[str]) -> list[str]:
    """Process multiple URLs concurrently."""
    tasks = [fetch_data(url) for url in urls]
    return await asyncio.gather(*tasks)


async def stream_numbers(count: int) -> AsyncIterator[int]:
    """Stream numbers asynchronously."""
    for i in range(count):
        await asyncio.sleep(0.01)
        yield i
'''


@pytest.fixture
def sample_python_complex() -> str:
    """Complex Python code with multiple patterns."""
    return '''"""Complex module with various patterns."""

from contextlib import contextmanager
from functools import lru_cache
from typing import Callable, Iterator, TypeVar

T = TypeVar("T")


@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    """Calculate fibonacci number with memoization."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def compose(*funcs: Callable[[T], T]) -> Callable[[T], T]:
    """Compose multiple functions."""
    def composed(x: T) -> T:
        result = x
        for f in reversed(funcs):
            result = f(result)
        return result
    return composed


@contextmanager
def managed_resource(name: str) -> Iterator[str]:
    """Context manager for resource management."""
    print(f"Acquiring {name}")
    try:
        yield name
    finally:
        print(f"Releasing {name}")


class Pipeline:
    """Data processing pipeline with chaining."""

    def __init__(self, data: list[int]) -> None:
        self._data = data

    def map(self, fn: Callable[[int], int]) -> "Pipeline":
        """Apply function to each element."""
        return Pipeline([fn(x) for x in self._data])

    def filter(self, predicate: Callable[[int], bool]) -> "Pipeline":
        """Filter elements by predicate."""
        return Pipeline([x for x in self._data if predicate(x)])

    def reduce(self, fn: Callable[[int, int], int], initial: int = 0) -> int:
        """Reduce to single value."""
        result = initial
        for item in self._data:
            result = fn(result, item)
        return result

    def collect(self) -> list[int]:
        """Collect results."""
        return self._data.copy()
'''


@pytest.fixture
def sample_python_error_handling() -> str:
    """Python code with exception handling patterns."""
    return '''"""Exception handling patterns."""

from typing import TypeVar, Generic

T = TypeVar("T")


class Result(Generic[T]):
    """Result type for error handling."""

    def __init__(self, value: T | None, error: str | None) -> None:
        self._value = value
        self._error = error

    @classmethod
    def ok(cls, value: T) -> "Result[T]":
        """Create success result."""
        return cls(value, None)

    @classmethod
    def err(cls, error: str) -> "Result[T]":
        """Create error result."""
        return cls(None, error)

    def is_ok(self) -> bool:
        """Check if result is success."""
        return self._error is None

    def unwrap(self) -> T:
        """Unwrap value or raise."""
        if self._error is not None:
            raise ValueError(self._error)
        return self._value  # type: ignore


def divide(a: int, b: int) -> Result[float]:
    """Divide with error handling."""
    if b == 0:
        return Result.err("Division by zero")
    return Result.ok(a / b)


def parse_int(s: str) -> Result[int]:
    """Parse integer with error handling."""
    try:
        return Result.ok(int(s))
    except ValueError as e:
        return Result.err(str(e))
'''


@pytest.fixture
def invalid_python_source() -> str:
    """Invalid Python source with syntax errors."""
    return '''"""Module with syntax errors."""

def broken_function(
    """This is not valid Python."""
    return 42
'''


@pytest.fixture
def python_with_unsupported_patterns() -> str:
    """Python code with patterns that may not fully convert."""
    return '''"""Module with challenging patterns."""

import ctypes
from typing import Any


# Dynamic code execution
def dynamic_eval(code: str, context: dict[str, Any]) -> Any:
    """Execute dynamic code."""
    return eval(code, context)


# Metaclass usage
class MetaRegistry(type):
    """Metaclass that registers all subclasses."""

    registry: dict[str, type] = {}

    def __new__(mcs, name: str, bases: tuple, attrs: dict) -> type:
        cls = super().__new__(mcs, name, bases, attrs)
        if name != "Base":
            mcs.registry[name] = cls
        return cls


class Base(metaclass=MetaRegistry):
    """Base class with registry."""
    pass


# Descriptor protocol
class Validated:
    """Descriptor that validates values."""

    def __init__(self, min_value: int, max_value: int) -> None:
        self.min_value = min_value
        self.max_value = max_value

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{name}"

    def __get__(self, obj: Any, objtype: type | None = None) -> int:
        if obj is None:
            return self  # type: ignore
        return getattr(obj, self.name, 0)

    def __set__(self, obj: Any, value: int) -> None:
        if not self.min_value <= value <= self.max_value:
            raise ValueError(f"Value must be between {self.min_value} and {self.max_value}")
        setattr(obj, self.name, value)
'''


# =============================================================================
# IR Fixtures
# =============================================================================


@pytest.fixture
def sample_ir() -> IRVersion:
    """Sample IR structure for testing."""
    metadata = ModuleMetadata(
        source_file="sample.py",
        source_language="python",
        extraction_version="ir-v1.0",
        extraction_mode=ExtractionMode.FULL_MODULE,
        source_hash="abc123",
        extraction_timestamp=datetime.now(timezone.utc),
        documentation="Sample module for testing.",
    )

    module = Module(
        id="module:sample.py",
        name="sample",
        path=["sample"],
        visibility=Visibility.PUBLIC,
        imports=[],
        exports=[],
        definitions=[],
        submodules=[],
        extraction_scope="full",
        metadata=metadata,
    )

    # Add a simple function
    func = Function(
        id="func:sample.py:0",
        name="greet",
        params=[
            Param(
                name="name",
                type=TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.str"),
            )
        ],
        return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.str"),
        effects=[Effect(kind=EffectKind.PURE, source=AnnotationSource.INFERRED)],
        body=ControlFlowGraph(
            entry="block:0",
            blocks=[
                Block(
                    id="block:0",
                    statements=[],
                    terminator=Terminator(kind=TerminatorKind.RETURN),
                )
            ],
            exit="block:0",
        ),
        visibility=Visibility.PUBLIC,
        doc_comment="Greet someone by name.",
    )

    return IRVersion(
        version="ir-v1.0",
        module=module,
        types=[],
        type_relationships=[],
        functions=[func],
        bindings=[],
        data_flow_nodes=[],
        expressions=[],
        annotations=[],
        gaps=[],
        preservation=PreservationStatus(
            id="preservation:module:sample.py",
            unit_id="module:sample.py",
            current_level=PreservationLevel.SYNTACTIC,
            max_achievable_level=PreservationLevel.IDIOMATIC,
        ),
    )


@pytest.fixture
def sample_ir_with_types() -> IRVersion:
    """Sample IR with type definitions."""
    metadata = ModuleMetadata(
        source_file="types.py",
        source_language="python",
        extraction_version="ir-v1.0",
        extraction_mode=ExtractionMode.FULL_MODULE,
    )

    module = Module(
        id="module:types.py",
        name="types",
        path=["types"],
        visibility=Visibility.PUBLIC,
        imports=[],
        exports=[],
        definitions=[],
        submodules=[],
        extraction_scope="full",
        metadata=metadata,
    )

    point_type = TypeDef(
        id="type:types.py:Point",
        name="Point",
        kind=TypeKind.STRUCT,
        body=TypeBody(
            fields=[],  # Simplified
        ),
        visibility=Visibility.PUBLIC,
    )

    return IRVersion(
        version="ir-v1.0",
        module=module,
        types=[point_type],
        type_relationships=[],
        functions=[],
        bindings=[],
    )


@pytest.fixture
def sample_ir_with_gaps() -> IRVersion:
    """Sample IR with gap markers."""
    metadata = ModuleMetadata(
        source_file="gaps.py",
        source_language="python",
        extraction_version="ir-v1.0",
        extraction_mode=ExtractionMode.FULL_MODULE,
    )

    module = Module(
        id="module:gaps.py",
        name="gaps",
        path=["gaps"],
        visibility=Visibility.PUBLIC,
        imports=[],
        exports=[],
        definitions=[],
        submodules=[],
        extraction_scope="full",
        metadata=metadata,
    )

    gaps = [
        GapMarker(
            id="gap:gaps.py:0",
            location="line:10",
            gap_type=GapType.STRUCTURAL,
            gap_pattern_id="TS-001",
            severity=Severity.MEDIUM,
            description="Dynamic type requires type inference",
            source_concept="dynamic typing",
            target_concept="static types",
            suggested_mitigations=["Add type annotations"],
            preservation_level=PreservationLevel.SEMANTIC,
        ),
        GapMarker(
            id="gap:gaps.py:1",
            location="line:20",
            gap_type=GapType.RUNTIME,
            gap_pattern_id="EF-001",
            severity=Severity.HIGH,
            description="Exception to Result conversion needed",
            source_concept="try/catch",
            target_concept="Result type",
            suggested_mitigations=["Wrap in Result"],
            preservation_level=PreservationLevel.IDIOMATIC,
        ),
    ]

    return IRVersion(
        version="ir-v1.0",
        module=module,
        types=[],
        type_relationships=[],
        functions=[],
        bindings=[],
        gaps=gaps,
        preservation=PreservationStatus(
            id="preservation:module:gaps.py",
            unit_id="module:gaps.py",
            current_level=PreservationLevel.SYNTACTIC,
            max_achievable_level=PreservationLevel.SEMANTIC,
            blocking_gaps=["gap:gaps.py:1"],
        ),
    )


@pytest.fixture
def invalid_ir() -> dict[str, Any]:
    """Invalid IR data for testing validation errors."""
    return {
        "version": "ir-v1.0",
        "module": {
            "id": "invalid",
            # Missing required fields: name, metadata
            "imports": [],
        },
        "types": [
            {
                "id": "type:broken",
                "name": "Broken",
                "kind": "invalid_kind",  # Invalid enum value
            }
        ],
        "functions": [],
    }


@pytest.fixture
def ir_with_dangling_refs() -> dict[str, Any]:
    """IR with dangling references for testing validation."""
    return {
        "version": "ir-v1.0",
        "module": {
            "id": "module:refs.py",
            "name": "refs",
            "path": ["refs"],
            "visibility": "public",
            "imports": [],
            "exports": [],
            "definitions": [],
            "submodules": [],
            "extraction_scope": "full",
            "metadata": {
                "source_file": "refs.py",
                "source_language": "python",
            },
        },
        "types": [],
        "functions": [
            {
                "id": "func:refs.py:0",
                "name": "broken",
                "params": [
                    {
                        "name": "x",
                        "type": {
                            "kind": "named",
                            "type_id": "NonExistentType",  # Dangling reference
                        },
                    }
                ],
                "return_type": {
                    "kind": "named",
                    "type_id": "AlsoMissing",  # Another dangling reference
                },
                "visibility": "public",
            }
        ],
        "bindings": [],
    }


# =============================================================================
# Database Fixtures
# =============================================================================


@pytest.fixture
def test_db(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary test database."""
    db_path = tmp_path / "test.db"

    # Create schema
    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS ir_versions (
            id INTEGER PRIMARY KEY,
            source_language TEXT,
            source_path TEXT,
            extraction_tool_version TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS ir_units (
            id INTEGER PRIMARY KEY,
            version_id INTEGER,
            layer INTEGER,
            unit_type TEXT,
            content_hash TEXT,
            content_json TEXT,
            FOREIGN KEY (version_id) REFERENCES ir_versions(id)
        );

        CREATE TABLE IF NOT EXISTS ir_patterns (
            id INTEGER PRIMARY KEY,
            skill_name TEXT,
            source_lang TEXT,
            target_lang TEXT,
            pattern_type TEXT,
            category TEXT,
            source_pattern TEXT,
            target_pattern TEXT,
            is_lossy INTEGER,
            severity TEXT,
            mitigation TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS languages (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            version TEXT,
            tier INTEGER,
            description TEXT,
            popularity_tiobe REAL,
            popularity_so REAL,
            github_repos INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS families (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            category TEXT,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS language_families (
            language_id INTEGER,
            family_id INTEGER,
            is_primary INTEGER,
            PRIMARY KEY (language_id, family_id),
            FOREIGN KEY (language_id) REFERENCES languages(id),
            FOREIGN KEY (family_id) REFERENCES families(id)
        );

        CREATE TABLE IF NOT EXISTS semantic_gaps (
            id INTEGER PRIMARY KEY,
            gap_category TEXT,
            concept TEXT,
            description TEXT,
            severity TEXT,
            mitigation TEXT,
            automation_level TEXT,
            from_family_id INTEGER,
            to_family_id INTEGER,
            notes TEXT,
            FOREIGN KEY (from_family_id) REFERENCES families(id),
            FOREIGN KEY (to_family_id) REFERENCES families(id)
        );

        CREATE TABLE IF NOT EXISTS decision_points (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            options TEXT,
            guidance TEXT,
            applicable_gaps TEXT
        );
    """)

    # Insert test data
    conn.execute("""
        INSERT INTO languages (name, version, tier, description)
        VALUES ('python', '3.11', 1, 'Python programming language')
    """)
    conn.execute("""
        INSERT INTO languages (name, version, tier, description)
        VALUES ('rust', '1.75', 1, 'Rust programming language')
    """)
    conn.execute("""
        INSERT INTO families (name, category, description)
        VALUES ('gc', 'memory_model', 'Garbage collected languages')
    """)
    conn.execute("""
        INSERT INTO families (name, category, description)
        VALUES ('ownership', 'memory_model', 'Ownership-based languages')
    """)

    conn.commit()
    conn.close()

    yield db_path


@pytest.fixture
def db_connection(test_db: Path) -> Generator[sqlite3.Connection, None, None]:
    """Create a database connection with row factory."""
    conn = sqlite3.connect(test_db)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


# =============================================================================
# Configuration Fixtures
# =============================================================================


@pytest.fixture
def extract_config() -> ExtractConfig:
    """Default extraction configuration."""
    return ExtractConfig(
        mode=ExtractionMode.FULL_MODULE,
        include_layer0=False,
        preserve_spans=True,
    )


@pytest.fixture
def extract_config_full() -> ExtractConfig:
    """Full extraction configuration with Layer 0."""
    return ExtractConfig(
        mode=ExtractionMode.FULL_MODULE,
        include_layer0=True,
        preserve_spans=True,
    )


@pytest.fixture
def synth_config() -> SynthConfig:
    """Default synthesis configuration."""
    return SynthConfig(
        output_format=OutputFormat.FORMATTED,
        emit_type_hints=True,
        emit_docstrings=True,
        line_length=88,
    )


@pytest.fixture
def synth_config_minimal() -> SynthConfig:
    """Minimal synthesis configuration."""
    return SynthConfig(
        output_format=OutputFormat.SOURCE,
        emit_type_hints=False,
        emit_docstrings=False,
    )


# =============================================================================
# Helper Fixtures
# =============================================================================


@dataclass
class ExecutionResult:
    """Result of code execution."""

    return_value: Any
    stdout: str
    stderr: str
    exception: str | None
    success: bool


@pytest.fixture
def execute_python():
    """Fixture that returns a function to execute Python code safely."""
    import subprocess

    def _execute(code: str, func_call: str, timeout: float = 5.0) -> ExecutionResult:
        """Execute Python code and return the result.

        Args:
            code: Python source code to execute
            func_call: Function call expression (e.g., "greet('World')")
            timeout: Maximum execution time

        Returns:
            ExecutionResult with execution details
        """
        wrapped = f'''
import json
import sys

{code}

try:
    result = {func_call}
    print(json.dumps({{"success": True, "result": repr(result)}}))
except Exception as e:
    print(json.dumps({{"success": False, "error": str(e)}}))
'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(wrapped)
            f.flush()

            try:
                result = subprocess.run(
                    [sys.executable, f.name],
                    capture_output=True,
                    timeout=timeout,
                    text=True
                )

                try:
                    output = json.loads(result.stdout.strip())
                    return ExecutionResult(
                        return_value=output.get("result"),
                        stdout=result.stdout,
                        stderr=result.stderr,
                        exception=output.get("error"),
                        success=output.get("success", False),
                    )
                except json.JSONDecodeError:
                    return ExecutionResult(
                        return_value=None,
                        stdout=result.stdout,
                        stderr=result.stderr,
                        exception="Failed to parse output",
                        success=False,
                    )
            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    return_value=None,
                    stdout="",
                    stderr="",
                    exception="Timeout",
                    success=False,
                )
            finally:
                Path(f.name).unlink(missing_ok=True)

    return _execute


@pytest.fixture
def compare_outputs():
    """Fixture that returns a function to compare execution outputs."""

    def _compare(
        source_result: ExecutionResult,
        target_result: ExecutionResult,
    ) -> bool:
        """Compare two execution results for L3 equivalence.

        Returns True if both succeeded with the same result,
        or both failed with the same type of error.
        """
        if source_result.success != target_result.success:
            return False

        if source_result.success:
            return source_result.return_value == target_result.return_value
        else:
            # Both failed - check exception types match
            return (
                source_result.exception is not None and
                target_result.exception is not None and
                type(source_result.exception).__name__ == type(target_result.exception).__name__
            )

    return _compare
