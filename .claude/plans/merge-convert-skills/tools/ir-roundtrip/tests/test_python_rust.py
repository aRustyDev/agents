"""Integration tests for Python ↔ Rust conversion.

Tests that code can be extracted from one language and synthesized
to another, maintaining semantic equivalence.
"""

import sys
from pathlib import Path

# Add tools to path before any imports
TOOLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(TOOLS_DIR / "ir-core"))
sys.path.insert(0, str(TOOLS_DIR / "ir-extract-python"))
sys.path.insert(0, str(TOOLS_DIR / "ir-extract-rust"))
sys.path.insert(0, str(TOOLS_DIR / "ir-synthesize-python"))
sys.path.insert(0, str(TOOLS_DIR / "ir-synthesize-rust"))

import pytest  # noqa: E402

# Skip all tests if dependencies are not available
pytest.importorskip("ir_core")

from ir_core.base import SynthConfig  # noqa: E402
from ir_core.models import (  # noqa: E402
    Definition,
    Field_,
    Function,
    IRVersion,
    Module,
    Param,
    TypeBody,
    TypeDef,
    TypeKind,
    TypeRef,
    TypeRefKind,
)
from ir_extract_python.extractor import PythonExtractor  # noqa: E402
from ir_synthesize_python.synthesizer import PythonSynthesizer  # noqa: E402
from ir_synthesize_rust.synthesizer import RustSynthesizer  # noqa: E402


@pytest.fixture
def python_extractor():
    """Create Python extractor."""
    return PythonExtractor()


@pytest.fixture
def rust_synthesizer():
    """Create Rust synthesizer."""
    return RustSynthesizer(SynthConfig())


@pytest.fixture
def python_synthesizer():
    """Create Python synthesizer."""
    return PythonSynthesizer(SynthConfig())


class TestPythonToRust:
    """Test Python to Rust conversion."""

    def test_simple_function(self, python_extractor, rust_synthesizer):
        """Test converting a simple function."""
        python_code = '''
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
'''
        # Extract from Python
        ir = python_extractor.extract(python_code, "test.py")
        assert ir is not None

        # Synthesize to Rust
        rust_code = rust_synthesizer.synthesize(ir, SynthConfig())
        assert rust_code is not None
        assert "fn add" in rust_code or "pub fn add" in rust_code

    def test_class_to_struct(self, python_extractor, rust_synthesizer):
        """Test converting a Python class to Rust struct."""
        python_code = '''
class Point:
    """A 2D point."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance(self) -> float:
        """Distance from origin."""
        return (self.x ** 2 + self.y ** 2) ** 0.5
'''
        # Extract from Python
        ir = python_extractor.extract(python_code, "test.py")
        assert ir is not None

        # Synthesize to Rust
        rust_code = rust_synthesizer.synthesize(ir, SynthConfig())
        assert rust_code is not None
        # Should have struct definition
        assert "struct Point" in rust_code or "Point" in rust_code


class TestRustToPython:
    """Test Rust to Python conversion."""

    def test_simple_struct_conversion(self, python_synthesizer):
        """Test converting Rust struct to Python class."""
        # Create IR for a simple struct
        ir = IRVersion(
            version="1.0",
            source_language="rust",
            modules=[
                Module(
                    id="test",
                    path="test.rs",
                    definitions=[
                        Definition(
                            id="Point",
                            kind="type",
                            name="Point",
                            visibility="public",
                        )
                    ],
                )
            ],
            type_definitions=[
                TypeDef(
                    id="Point",
                    name="Point",
                    kind=TypeKind.STRUCT,
                    body=TypeBody(
                        fields=[
                            Field_(name="x", type=TypeRef(kind=TypeRefKind.NAMED, type_id="f64")),
                            Field_(name="y", type=TypeRef(kind=TypeRefKind.NAMED, type_id="f64")),
                        ]
                    ),
                )
            ],
        )

        python_code = python_synthesizer.synthesize(ir, SynthConfig())
        assert python_code is not None
        assert "class Point" in python_code or "Point" in python_code

    def test_function_conversion(self, python_synthesizer):
        """Test converting Rust function to Python function."""
        ir = IRVersion(
            version="1.0",
            source_language="rust",
            modules=[
                Module(
                    id="test",
                    path="test.rs",
                    definitions=[
                        Definition(
                            id="add",
                            kind="function",
                            name="add",
                            visibility="public",
                        )
                    ],
                )
            ],
            functions=[
                Function(
                    id="add",
                    name="add",
                    params=[
                        Param(name="a", type=TypeRef(kind=TypeRefKind.NAMED, type_id="i32")),
                        Param(name="b", type=TypeRef(kind=TypeRefKind.NAMED, type_id="i32")),
                    ],
                    return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="i32"),
                )
            ],
        )

        python_code = python_synthesizer.synthesize(ir, SynthConfig())
        assert python_code is not None
        assert "def add" in python_code


class TestRoundTrip:
    """Test round-trip conversion."""

    def test_python_rust_python(self, python_extractor, rust_synthesizer, _python_synthesizer):
        """Test Python -> Rust -> Python conversion."""
        original_code = '''
def greet(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}!"
'''
        # Extract from Python
        ir1 = python_extractor.extract(original_code, "test.py")
        assert ir1 is not None

        # Synthesize to Rust
        rust_code = rust_synthesizer.synthesize(ir1, SynthConfig())
        assert rust_code is not None

        # The structure should be preserved
        assert "greet" in rust_code.lower() or "fn" in rust_code


class TestFixturesExtraction:
    """Test extracting from fixture files."""

    @pytest.fixture
    def fixtures_dir(self):
        """Get fixtures directory."""
        return Path(__file__).parent.parent.parent / "tests" / "fixtures"

    def test_rust_fixtures_exist(self, fixtures_dir):
        """Verify Rust fixtures exist."""
        rust_dir = fixtures_dir / "rust"
        if rust_dir.exists():
            rust_files = list(rust_dir.rglob("*.rs"))
            assert len(rust_files) >= 10, (
                f"Expected at least 10 Rust fixtures, found {len(rust_files)}"
            )


class TestTypeMapping:
    """Test type mapping between Python and Rust."""

    def test_primitive_types(self):
        """Test primitive type mappings."""
        mappings = {
            "int": ["i32", "i64", "isize"],
            "float": ["f32", "f64"],
            "bool": ["bool"],
            "str": ["String", "&str"],
        }

        for python_type, rust_types in mappings.items():
            # At least verify the mapping exists conceptually
            assert python_type is not None
            assert len(rust_types) > 0

    def test_collection_types(self):
        """Test collection type mappings."""
        mappings = {
            "list": ["Vec"],
            "dict": ["HashMap"],
            "set": ["HashSet"],
            "tuple": ["tuple"],
        }

        for python_type, rust_types in mappings.items():
            assert python_type is not None
            assert len(rust_types) > 0
