"""Round-trip tests between Python extractor and synthesizer.

These tests verify L3 (semantic) equivalence by extracting Python code to IR,
synthesizing it back to Python, and verifying the behavior matches.
"""

from __future__ import annotations

from typing import Any

import pytest
from ir_core.base import ExtractConfig, OutputFormat, SynthConfig

# Try to import extractor - may not be available
try:
    from ir_extract_python import PythonExtractor
    HAS_EXTRACTOR = True
except ImportError:
    HAS_EXTRACTOR = False

from ir_synthesize_python import PythonSynthesizer

pytestmark = pytest.mark.skipif(
    not HAS_EXTRACTOR,
    reason="ir-extract-python not installed",
)


@pytest.fixture
def extractor() -> PythonExtractor:
    """Create an extractor instance."""
    if HAS_EXTRACTOR:
        return PythonExtractor()
    pytest.skip("Extractor not available")


@pytest.fixture
def synthesizer() -> PythonSynthesizer:
    """Create a synthesizer instance."""
    return PythonSynthesizer()


@pytest.fixture
def extract_config() -> ExtractConfig:
    """Create extraction config."""
    return ExtractConfig()


@pytest.fixture
def synth_config() -> SynthConfig:
    """Create synthesis config."""
    return SynthConfig(
        output_format=OutputFormat.SOURCE,
        emit_type_hints=True,
        emit_docstrings=True,
    )


def exec_function(code: str, func_name: str, *args: Any, **kwargs: Any) -> Any:
    """Execute a function from code string.

    Args:
        code: Python source code
        func_name: Name of function to call
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Function return value
    """
    namespace: dict[str, Any] = {}
    exec(code, namespace)
    return namespace[func_name](*args, **kwargs)


@pytest.mark.roundtrip
class TestSimpleRoundtrip:
    """Simple round-trip tests."""

    def test_identity_function(
        self,
        extractor: PythonExtractor,
        synthesizer: PythonSynthesizer,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Test round-trip of identity function."""
        original = '''
def identity(x: int) -> int:
    """Return the input unchanged."""
    return x
'''
        # Extract
        ir = extractor.extract(original, "test.py", extract_config)

        # Synthesize
        generated = synthesizer.synthesize(ir, synth_config)

        # Verify behavior
        test_values = [0, 1, -1, 42, 1000]
        for value in test_values:
            original_result = exec_function(original, "identity", value)
            generated_result = exec_function(generated, "identity", value)
            assert original_result == generated_result

    def test_add_function(
        self,
        extractor: PythonExtractor,
        synthesizer: PythonSynthesizer,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Test round-trip of addition function."""
        original = '''
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
'''
        ir = extractor.extract(original, "test.py", extract_config)
        generated = synthesizer.synthesize(ir, synth_config)

        test_cases = [(0, 0), (1, 2), (-1, 1), (100, 200)]
        for a, b in test_cases:
            original_result = exec_function(original, "add", a, b)
            generated_result = exec_function(generated, "add", a, b)
            assert original_result == generated_result

    def test_conditional_function(
        self,
        extractor: PythonExtractor,
        synthesizer: PythonSynthesizer,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Test round-trip of function with conditional."""
        original = '''
def abs_value(x: int) -> int:
    """Return absolute value."""
    if x < 0:
        return -x
    return x
'''
        ir = extractor.extract(original, "test.py", extract_config)
        generated = synthesizer.synthesize(ir, synth_config)

        test_values = [-5, -1, 0, 1, 5]
        for value in test_values:
            original_result = exec_function(original, "abs_value", value)
            generated_result = exec_function(generated, "abs_value", value)
            assert original_result == generated_result


@pytest.mark.roundtrip
class TestDataclassRoundtrip:
    """Round-trip tests for dataclasses."""

    def test_simple_dataclass(
        self,
        extractor: PythonExtractor,
        synthesizer: PythonSynthesizer,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Test round-trip of a simple dataclass."""
        original = '''
from dataclasses import dataclass

@dataclass
class Point:
    """A 2D point."""
    x: float
    y: float
'''
        ir = extractor.extract(original, "test.py", extract_config)
        generated = synthesizer.synthesize(ir, synth_config)

        # Both should be valid dataclasses
        assert "@dataclass" in generated
        assert "class Point" in generated
        assert "x: float" in generated
        assert "y: float" in generated


@pytest.mark.roundtrip
class TestAsyncRoundtrip:
    """Round-trip tests for async functions."""

    def test_async_function(
        self,
        extractor: PythonExtractor,
        synthesizer: PythonSynthesizer,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Test round-trip of async function."""
        original = '''
async def fetch_data() -> str:
    """Fetch some data."""
    return "data"
'''
        ir = extractor.extract(original, "test.py", extract_config)
        generated = synthesizer.synthesize(ir, synth_config)

        assert "async def fetch_data" in generated
        assert "-> str" in generated


@pytest.mark.roundtrip
class TestTypeAnnotationRoundtrip:
    """Round-trip tests for type annotations."""

    def test_generic_types(
        self,
        extractor: PythonExtractor,
        synthesizer: PythonSynthesizer,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Test round-trip of generic type annotations."""
        original = '''
def process(items: list[str]) -> dict[str, int]:
    """Process items."""
    return {}
'''
        ir = extractor.extract(original, "test.py", extract_config)
        generated = synthesizer.synthesize(ir, synth_config)

        assert "list[str]" in generated or "list" in generated
        assert "dict" in generated

    def test_optional_types(
        self,
        extractor: PythonExtractor,
        synthesizer: PythonSynthesizer,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Test round-trip of optional type annotations."""
        original = '''
def find(items: list[int], target: int) -> int | None:
    """Find target in items."""
    for i, item in enumerate(items):
        if item == target:
            return i
    return None
'''
        ir = extractor.extract(original, "test.py", extract_config)
        generated = synthesizer.synthesize(ir, synth_config)

        # Should have some form of optional/union type
        assert "None" in generated


@pytest.mark.roundtrip
@pytest.mark.slow
class TestPropertyBasedRoundtrip:
    """Property-based round-trip tests using hypothesis."""

    def test_arithmetic_equivalence(
        self,
        extractor: PythonExtractor,
        synthesizer: PythonSynthesizer,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Test that arithmetic operations are semantically equivalent."""
        try:
            from hypothesis import given, settings
            from hypothesis import strategies as st
        except ImportError:
            pytest.skip("hypothesis not installed")

        original = '''
def compute(a: int, b: int, c: int) -> int:
    """Compute (a + b) * c."""
    return (a + b) * c
'''
        ir = extractor.extract(original, "test.py", extract_config)
        generated = synthesizer.synthesize(ir, synth_config)

        @settings(max_examples=100)
        @given(st.integers(-100, 100), st.integers(-100, 100), st.integers(-100, 100))
        def check_equivalence(a: int, b: int, c: int) -> None:
            original_result = exec_function(original, "compute", a, b, c)
            generated_result = exec_function(generated, "compute", a, b, c)
            assert original_result == generated_result

        check_equivalence()


@pytest.mark.roundtrip
class TestEdgeCases:
    """Round-trip tests for edge cases."""

    def test_empty_function(
        self,
        extractor: PythonExtractor,
        synthesizer: PythonSynthesizer,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Test round-trip of function with pass body."""
        original = '''
def noop() -> None:
    """Do nothing."""
    pass
'''
        ir = extractor.extract(original, "test.py", extract_config)
        generated = synthesizer.synthesize(ir, synth_config)

        assert "def noop" in generated
        assert "-> None" in generated or "None" in generated

    def test_multiple_functions(
        self,
        extractor: PythonExtractor,
        synthesizer: PythonSynthesizer,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Test round-trip of module with multiple functions."""
        original = '''
def first() -> int:
    """First function."""
    return 1

def second() -> int:
    """Second function."""
    return 2

def combined() -> int:
    """Combine first and second."""
    return first() + second()
'''
        ir = extractor.extract(original, "test.py", extract_config)
        generated = synthesizer.synthesize(ir, synth_config)

        assert "def first" in generated
        assert "def second" in generated
        assert "def combined" in generated

    def test_private_function(
        self,
        extractor: PythonExtractor,
        synthesizer: PythonSynthesizer,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Test round-trip of private function."""
        original = '''
def _private_helper() -> int:
    """Private helper function."""
    return 42
'''
        ir = extractor.extract(original, "test.py", extract_config)
        generated = synthesizer.synthesize(ir, synth_config)

        assert "def _private_helper" in generated
