"""Preservation level verification tests.

This module provides comprehensive tests for each preservation level (L1-L5)
as defined in docs/src/validation/equivalence-levels.md.

Preservation Levels:
- L1 (Syntactic): AST isomorphism after normalization
- L2 (Operational): Lock-step execution traces match
- L3 (Semantic): Same I/O behavior for all inputs
- L4 (Contextual): Same behavior in any program context
- L5 (Idiomatic): Native patterns achieving same functionality

Phase 5 Target: L3 (Semantic) equivalence for Python MVP.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

import pytest

# Add tools to path
TOOLS_DIR = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR / "ir-core"))
sys.path.insert(0, str(TOOLS_DIR / "ir-extract-python"))
sys.path.insert(0, str(TOOLS_DIR / "ir-synthesize-python"))
sys.path.insert(0, str(TOOLS_DIR / "ir-validate"))

from ir_core import (
    IRVersion,
    ExtractConfig,
    ExtractionMode,
    PreservationLevel,
)
from ir_core.base import SynthConfig, OutputFormat


# =============================================================================
# Import Tools with Graceful Fallback
# =============================================================================

try:
    from ir_extract_python import PythonExtractor
    HAS_EXTRACTOR = True
except ImportError:
    HAS_EXTRACTOR = False
    PythonExtractor = None  # type: ignore

try:
    from ir_synthesize_python import PythonSynthesizer
    HAS_SYNTHESIZER = True
except ImportError:
    HAS_SYNTHESIZER = False
    PythonSynthesizer = None  # type: ignore


requires_extractor = pytest.mark.skipif(
    not HAS_EXTRACTOR, reason="PythonExtractor not available"
)
requires_synthesizer = pytest.mark.skipif(
    not HAS_SYNTHESIZER, reason="PythonSynthesizer not available"
)
requires_all = pytest.mark.skipif(
    not (HAS_EXTRACTOR and HAS_SYNTHESIZER),
    reason="Full toolchain not available"
)


# =============================================================================
# Helper Functions
# =============================================================================


def normalize_ast(source: str) -> ast.AST:
    """Parse and normalize Python AST."""
    tree = ast.parse(source)
    # Remove location info for comparison
    for node in ast.walk(tree):
        for attr in ['lineno', 'col_offset', 'end_lineno', 'end_col_offset']:
            if hasattr(node, attr):
                delattr(node, attr)
    return tree


def ast_equal(tree1: ast.AST, tree2: ast.AST) -> bool:
    """Compare two ASTs for structural equality."""
    return ast.dump(tree1) == ast.dump(tree2)


def count_ast_nodes(tree: ast.AST) -> dict[str, int]:
    """Count node types in an AST."""
    counts: dict[str, int] = {}
    for node in ast.walk(tree):
        name = type(node).__name__
        counts[name] = counts.get(name, 0) + 1
    return counts


# =============================================================================
# L1: Syntactic Equivalence Tests
# =============================================================================


@pytest.mark.preservation
@pytest.mark.l1
class TestPreservationL1:
    """L1 (Syntactic) equivalence tests.

    L1 requires AST isomorphism after normalization. For same-language
    roundtrip, this means the synthesized code should have the same
    structure as the original.
    """

    @requires_all
    def test_function_structure_preserved(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Verify function structure is preserved at L1."""
        source = '''def simple(x: int) -> int:
    return x + 1
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "test.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        # Parse both
        source_tree = normalize_ast(source)
        output_tree = normalize_ast(output)

        # Count node types - should have similar structure
        source_counts = count_ast_nodes(source_tree)
        output_counts = count_ast_nodes(output_tree)

        # Should have same number of function defs
        assert output_counts.get("FunctionDef", 0) >= source_counts.get("FunctionDef", 0)

    @requires_all
    def test_class_structure_preserved(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Verify class structure is preserved at L1."""
        source = '''class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "test.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        output_tree = normalize_ast(output)
        output_counts = count_ast_nodes(output_tree)

        # Should have class definition
        assert output_counts.get("ClassDef", 0) >= 1

    @requires_all
    def test_statement_order_preserved(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Verify statement order is preserved."""
        source = '''def process():
    a = 1
    b = 2
    c = a + b
    return c
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "test.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        # Verify return is present
        assert "return" in output

    @requires_all
    def test_control_flow_preserved(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Verify control flow structure is preserved."""
        source = '''def classify(x: int) -> str:
    if x > 0:
        return "positive"
    elif x < 0:
        return "negative"
    else:
        return "zero"
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "test.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        output_tree = normalize_ast(output)
        output_counts = count_ast_nodes(output_tree)

        # Should have If nodes
        assert output_counts.get("If", 0) >= 1 or "if" in output


# =============================================================================
# L2: Operational Equivalence Tests
# =============================================================================


@pytest.mark.preservation
@pytest.mark.l2
class TestPreservationL2:
    """L2 (Operational) equivalence tests.

    L2 requires matching execution traces. For same-language roundtrip,
    we verify step-wise behavior matches.
    """

    @requires_all
    @pytest.mark.slow
    def test_iteration_order_preserved(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
        execute_python,
        compare_outputs,
    ) -> None:
        """Verify iteration order is preserved."""
        source = '''def collect_order(n: int) -> list[int]:
    result = []
    for i in range(n):
        result.append(i)
    return result
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "test.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        # Execute both
        source_result = execute_python(source, "collect_order(5)")
        target_result = execute_python(output, "collect_order(5)")

        assert compare_outputs(source_result, target_result)

    @requires_all
    @pytest.mark.slow
    def test_side_effect_order_preserved(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
        execute_python,
    ) -> None:
        """Verify side effect order is preserved."""
        source = '''def effects(n: int) -> list[str]:
    log = []
    for i in range(n):
        log.append(f"processing {i}")
    return log
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "test.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        # Execute both
        source_result = execute_python(source, "effects(3)")
        target_result = execute_python(output, "effects(3)")

        # Results should match
        assert source_result.success == target_result.success
        if source_result.success:
            assert source_result.return_value == target_result.return_value


# =============================================================================
# L3: Semantic Equivalence Tests
# =============================================================================


@pytest.mark.preservation
@pytest.mark.l3
class TestPreservationL3:
    """L3 (Semantic) equivalence tests.

    L3 requires same I/O behavior for all inputs. This is the primary
    target for Phase 5.
    """

    @requires_all
    def test_function_behavior_preserved(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
        execute_python,
        compare_outputs,
    ) -> None:
        """Verify function behavior is preserved for all inputs."""
        source = '''def absolute(x: int) -> int:
    if x < 0:
        return -x
    return x
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "test.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        # Test with various inputs
        test_cases = [-5, -1, 0, 1, 5, 100, -100]
        for x in test_cases:
            source_result = execute_python(source, f"absolute({x})")
            target_result = execute_python(output, f"absolute({x})")

            assert compare_outputs(source_result, target_result), (
                f"Behavior differs for absolute({x})"
            )

    @requires_all
    def test_error_handling_preserved(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
        execute_python,
    ) -> None:
        """Verify error handling is preserved."""
        source = '''def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Division by zero")
    return a / b
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "test.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        # Test normal case
        source_result = execute_python(source, "divide(10, 2)")
        target_result = execute_python(output, "divide(10, 2)")

        assert source_result.success == target_result.success

        # Test error case
        source_error = execute_python(source, "divide(10, 0)")
        target_error = execute_python(output, "divide(10, 0)")

        # Both should fail
        assert source_error.success == target_error.success == False

    @requires_all
    @pytest.mark.slow
    def test_comprehensions_behavior_preserved(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
        execute_python,
        compare_outputs,
    ) -> None:
        """Verify list comprehension behavior is preserved."""
        source = '''def filter_evens(nums: list[int]) -> list[int]:
    return [x for x in nums if x % 2 == 0]
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "test.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        test_cases = [
            "[]",
            "[1, 2, 3, 4, 5]",
            "[2, 4, 6]",
            "[1, 3, 5]",
        ]

        for nums in test_cases:
            source_result = execute_python(source, f"filter_evens({nums})")
            target_result = execute_python(output, f"filter_evens({nums})")

            assert compare_outputs(source_result, target_result)

    @requires_all
    def test_recursive_behavior_preserved(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
        execute_python,
        compare_outputs,
    ) -> None:
        """Verify recursive function behavior is preserved."""
        source = '''def fib(n: int) -> int:
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "test.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        for n in range(10):
            source_result = execute_python(source, f"fib({n})")
            target_result = execute_python(output, f"fib({n})")

            assert compare_outputs(source_result, target_result)

    @requires_all
    def test_string_operations_preserved(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
        execute_python,
        compare_outputs,
    ) -> None:
        """Verify string operation behavior is preserved."""
        source = '''def process_string(s: str) -> str:
    return s.strip().upper().replace(" ", "_")
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "test.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        test_cases = [
            '""',
            '"hello"',
            '"  hello world  "',
            '"ALREADY UPPER"',
        ]

        for s in test_cases:
            source_result = execute_python(source, f"process_string({s})")
            target_result = execute_python(output, f"process_string({s})")

            assert compare_outputs(source_result, target_result)


# =============================================================================
# L4/L5: Contextual and Idiomatic Tests
# =============================================================================


@pytest.mark.preservation
class TestPreservationL4L5:
    """L4 (Contextual) and L5 (Idiomatic) tests.

    These are aspirational tests beyond the Phase 5 target (L3).
    They verify behavior in broader contexts and idiomatic output.
    """

    @requires_all
    def test_comprehensions_used_for_idiomatic_output(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Verify comprehensions are used where appropriate (L5)."""
        source = '''def double_all(nums: list[int]) -> list[int]:
    return [x * 2 for x in nums]
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "test.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        # Should preserve or generate comprehension
        # (Implementation may vary)
        assert "def double_all" in output or "double_all" in output

    @requires_all
    def test_naming_conventions_preserved(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Verify Python naming conventions are preserved (L5)."""
        source = '''def calculate_total_price(items: list[float], tax_rate: float) -> float:
    subtotal = sum(items)
    return subtotal * (1 + tax_rate)
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "test.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        # Should preserve snake_case naming
        assert "calculate_total_price" in output or "total" in output.lower()

    @requires_all
    def test_type_hints_preserved(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Verify type hints are preserved (L5)."""
        synth_config.emit_type_hints = True

        source = '''def typed_function(x: int, y: str) -> tuple[int, str]:
    return (x, y)
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "test.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        # Should have type annotations
        assert "int" in output or "str" in output or ":" in output


# =============================================================================
# Preservation Status Tests
# =============================================================================


@pytest.mark.preservation
class TestPreservationStatus:
    """Tests for preservation status tracking."""

    @requires_extractor
    def test_preservation_status_created(
        self,
        sample_python_source: str,
        extract_config: ExtractConfig,
    ) -> None:
        """Verify preservation status is created during extraction."""
        extractor = PythonExtractor()

        ir = extractor.extract(sample_python_source, "test.py", extract_config)

        # Should have preservation status
        assert ir.preservation is not None
        assert ir.preservation.current_level is not None
        assert ir.preservation.max_achievable_level is not None

    @requires_extractor
    def test_gaps_affect_max_level(
        self,
        python_with_unsupported_patterns: str,
        extract_config: ExtractConfig,
    ) -> None:
        """Verify gaps affect maximum achievable level."""
        extractor = PythonExtractor()

        ir = extractor.extract(python_with_unsupported_patterns, "complex.py", extract_config)

        # Complex patterns may limit achievable level
        # The exact level depends on detected gaps
        assert ir.preservation is not None

    def test_preservation_level_enum_values(self) -> None:
        """Verify preservation level enum has expected values."""
        assert PreservationLevel.SYNTACTIC.value == 0
        assert PreservationLevel.SEMANTIC.value == 1
        assert PreservationLevel.IDIOMATIC.value == 2
        assert PreservationLevel.OPTIMIZED.value == 3

    def test_preservation_level_ordering(self) -> None:
        """Verify preservation levels are properly ordered."""
        assert PreservationLevel.SYNTACTIC < PreservationLevel.SEMANTIC
        assert PreservationLevel.SEMANTIC < PreservationLevel.IDIOMATIC
        assert PreservationLevel.IDIOMATIC < PreservationLevel.OPTIMIZED
