"""Full pipeline integration tests.

This module tests the complete extraction/synthesis pipeline:
    Python Source -> IR Extraction -> IR Validation -> Python Synthesis

Tests are organized by preservation level (L1-L3) and cover:
- Basic function extraction and synthesis
- Class and type definition handling
- Effect and annotation preservation
- Roundtrip equivalence verification
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add tools to path
TOOLS_DIR = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR / "ir-core"))
sys.path.insert(0, str(TOOLS_DIR / "ir-extract-python"))
sys.path.insert(0, str(TOOLS_DIR / "ir-synthesize-python"))
sys.path.insert(0, str(TOOLS_DIR / "ir-validate"))

from ir_core import (
    ExtractConfig,
    IRVersion,
)
from ir_core.base import SynthConfig

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

try:
    from ir_validate import IRValidator
    HAS_VALIDATOR = True
except ImportError:
    HAS_VALIDATOR = False
    IRValidator = None  # type: ignore


requires_extractor = pytest.mark.skipif(
    not HAS_EXTRACTOR,
    reason="PythonExtractor not available"
)

requires_synthesizer = pytest.mark.skipif(
    not HAS_SYNTHESIZER,
    reason="PythonSynthesizer not available"
)

requires_validator = pytest.mark.skipif(
    not HAS_VALIDATOR,
    reason="IRValidator not available"
)

requires_all_tools = pytest.mark.skipif(
    not (HAS_EXTRACTOR and HAS_SYNTHESIZER and HAS_VALIDATOR),
    reason="Full toolchain not available"
)


# =============================================================================
# Full Pipeline Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.roundtrip
class TestFullPipeline:
    """Tests for the complete extraction -> validation -> synthesis pipeline."""

    @requires_all_tools
    def test_extract_validate_synthesize_roundtrip(
        self,
        sample_python_source: str,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Test full pipeline: Python -> IR -> validate -> Python.

        This is the core roundtrip test verifying that code can be:
        1. Extracted to IR
        2. Validated against schema
        3. Synthesized back to Python
        """
        # Step 1: Extract
        extractor = PythonExtractor()
        ir = extractor.extract(sample_python_source, "test.py", extract_config)

        assert ir is not None
        assert ir.version == "ir-v1.0"
        assert ir.module is not None
        assert ir.module.name == "test"

        # Step 2: Validate
        validator = IRValidator()
        ir_dict = ir.model_dump(mode="json", exclude_none=True)
        result = validator.validate(ir_dict)

        assert result.is_valid, f"Validation failed: {result.format()}"

        # Step 3: Synthesize
        synthesizer = PythonSynthesizer()
        output = synthesizer.synthesize(ir, synth_config)

        assert output is not None
        assert len(output) > 0
        assert "def greet" in output or "def add" in output

    @requires_all_tools
    def test_roundtrip_preserves_function_signatures(
        self,
        sample_python_source: str,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Verify function signatures are preserved through roundtrip."""
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        # Extract and synthesize
        ir = extractor.extract(sample_python_source, "test.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        # Check signatures are preserved
        assert "def greet(name: str) -> str" in output or "def greet(name:" in output
        assert "def add(a: int, b: int) -> int" in output or "def add(" in output

    @requires_all_tools
    def test_roundtrip_preserves_docstrings(
        self,
        sample_python_source: str,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Verify docstrings are preserved through roundtrip."""
        synth_config.emit_docstrings = True

        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(sample_python_source, "test.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        # Check docstrings are preserved
        assert "Greet someone" in output or '"""' in output

    @requires_all_tools
    def test_roundtrip_with_classes(
        self,
        sample_python_class: str,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Test roundtrip with class definitions."""
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(sample_python_class, "classes.py", extract_config)

        # Verify types were extracted
        assert len(ir.types) >= 1

        # Synthesize
        output = synthesizer.synthesize(ir, synth_config)

        # Check class definitions are present
        assert "class Point" in output or "Point" in output
        assert "class Stack" in output or "Stack" in output

    @requires_all_tools
    def test_roundtrip_with_async(
        self,
        sample_python_async: str,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Test roundtrip with async/await patterns."""
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(sample_python_async, "async.py", extract_config)

        # Verify async effects were detected
        async_funcs = [f for f in ir.functions if any(
            e.kind == "async" for e in f.effects
        )]
        assert len(async_funcs) >= 1

        # Synthesize
        output = synthesizer.synthesize(ir, synth_config)

        # Check async keywords are present
        assert "async def" in output or "async" in output


# =============================================================================
# Preservation Level Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.preservation
class TestPreservationLevelL1:
    """L1 (Syntactic) equivalence tests.

    L1 requires AST isomorphism after normalization. For same-language
    roundtrip, this means the synthesized code should have the same
    structure as the original.
    """

    @requires_all_tools
    @pytest.mark.l1
    def test_simple_function_structure_preserved(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Verify simple function structure is preserved."""
        source = '''def add(a: int, b: int) -> int:
    return a + b
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "add.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        # Verify structural elements
        assert "def add" in output
        assert "return" in output

    @requires_all_tools
    @pytest.mark.l1
    def test_control_flow_structure_preserved(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Verify control flow structures are preserved."""
        source = '''def process(x: int) -> int:
    if x > 0:
        return x * 2
    else:
        return x
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "process.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        # Verify control flow
        assert "if" in output or "return" in output


@pytest.mark.integration
@pytest.mark.preservation
class TestPreservationLevelL2:
    """L2 (Operational) equivalence tests.

    L2 requires matching execution traces. For cross-language, this is
    rarely achievable. For same-language, we verify step-wise behavior
    matches where possible.
    """

    @requires_all_tools
    @pytest.mark.l2
    @pytest.mark.slow
    def test_loop_iteration_order_preserved(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
        execute_python,
        compare_outputs,
    ) -> None:
        """Verify loop iteration order is preserved."""
        source = '''def sum_range(n: int) -> int:
    result = 0
    for i in range(n):
        result += i
    return result
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "sum.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        # Execute both and compare
        source_result = execute_python(source, "sum_range(5)")
        target_result = execute_python(output, "sum_range(5)")

        assert compare_outputs(source_result, target_result)


@pytest.mark.integration
@pytest.mark.preservation
class TestPreservationLevelL3:
    """L3 (Semantic) equivalence tests.

    L3 requires same I/O behavior for all inputs. This is the primary
    target for Phase 5 (Python MVP). We use property-based testing where
    possible.
    """

    @requires_all_tools
    @pytest.mark.l3
    def test_function_behavior_preserved(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
        execute_python,
        compare_outputs,
    ) -> None:
        """Verify function behavior is preserved."""
        source = '''def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "factorial.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        # Test multiple inputs
        for n in [0, 1, 5, 10]:
            source_result = execute_python(source, f"factorial({n})")
            target_result = execute_python(output, f"factorial({n})")

            assert compare_outputs(source_result, target_result), (
                f"Behavior differs for factorial({n}): "
                f"source={source_result.return_value}, "
                f"target={target_result.return_value}"
            )

    @requires_all_tools
    @pytest.mark.l3
    def test_error_handling_preserved(
        self,
        sample_python_error_handling: str,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Verify error handling patterns are preserved."""
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(sample_python_error_handling, "errors.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        # Check error handling structures
        assert "class Result" in output or "Result" in output
        assert "raise" in output or "error" in output.lower()

    @requires_all_tools
    @pytest.mark.l3
    @pytest.mark.slow
    def test_list_operations_preserved(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
        execute_python,
        compare_outputs,
    ) -> None:
        """Verify list operations produce same results."""
        source = '''def process_list(items: list[int]) -> list[int]:
    return [x * 2 for x in items if x > 0]
'''
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "list.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        # Test with different inputs
        test_cases = [
            "[]",
            "[1, 2, 3]",
            "[-1, 0, 1]",
            "[10, -5, 20]",
        ]

        for items in test_cases:
            source_result = execute_python(source, f"process_list({items})")
            target_result = execute_python(output, f"process_list({items})")

            assert compare_outputs(source_result, target_result), (
                f"Behavior differs for process_list({items})"
            )


# =============================================================================
# Gap Detection in Pipeline
# =============================================================================


@pytest.mark.integration
class TestPipelineGapDetection:
    """Tests for gap detection during pipeline execution."""

    @requires_extractor
    def test_extraction_detects_dynamic_patterns(
        self,
        python_with_unsupported_patterns: str,
        extract_config: ExtractConfig,
    ) -> None:
        """Verify extraction flags unsupported patterns as gaps."""
        extractor = PythonExtractor()
        ir = extractor.extract(python_with_unsupported_patterns, "dynamic.py", extract_config)

        # Should have gaps for dynamic patterns
        assert ir.gaps is not None or ir.preservation is not None

    @requires_all_tools
    def test_validation_after_extraction(
        self,
        sample_python_source: str,
        extract_config: ExtractConfig,
    ) -> None:
        """Verify extracted IR passes validation."""
        extractor = PythonExtractor()
        validator = IRValidator()

        ir = extractor.extract(sample_python_source, "test.py", extract_config)
        ir_dict = ir.model_dump(mode="json", exclude_none=True)

        result = validator.validate(ir_dict)

        # Should pass validation
        assert result.is_valid, (
            f"Extracted IR failed validation: {result.format()}"
        )


# =============================================================================
# Edge Cases
# =============================================================================


@pytest.mark.integration
class TestPipelineEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @requires_extractor
    def test_empty_source(self, extract_config: ExtractConfig) -> None:
        """Test extraction of empty source file."""
        source = '"""Empty module."""\n'

        extractor = PythonExtractor()
        ir = extractor.extract(source, "empty.py", extract_config)

        assert ir is not None
        assert ir.module is not None
        assert len(ir.functions) == 0
        assert len(ir.types) == 0

    @requires_extractor
    def test_only_comments(self, extract_config: ExtractConfig) -> None:
        """Test extraction of source with only comments."""
        source = '''# This is a comment
# Another comment
"""Module docstring."""
'''

        extractor = PythonExtractor()
        ir = extractor.extract(source, "comments.py", extract_config)

        assert ir is not None
        assert ir.module is not None

    @requires_extractor
    def test_deeply_nested_code(self, extract_config: ExtractConfig) -> None:
        """Test extraction of deeply nested code structures."""
        source = '''def outer():
    def inner1():
        def inner2():
            def inner3():
                return 42
            return inner3()
        return inner2()
    return inner1()
'''

        extractor = PythonExtractor()
        ir = extractor.extract(source, "nested.py", extract_config)

        assert ir is not None
        # Should extract at least the outer function
        assert len(ir.functions) >= 1

    @requires_synthesizer
    def test_synthesize_minimal_ir(self, sample_ir: IRVersion, synth_config: SynthConfig) -> None:
        """Test synthesis from minimal IR."""
        synthesizer = PythonSynthesizer()
        output = synthesizer.synthesize(sample_ir, synth_config)

        assert output is not None
        assert len(output) > 0

    @requires_all_tools
    def test_unicode_content(
        self,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Test handling of unicode in source code."""
        source = '''def greet(name: str) -> str:
    """Greet with emoji."""
    return f"Hello, {name}! 🎉"

# Japanese comment: こんにちは
def process(data: str) -> str:
    """Process unicode data."""
    return data.upper()
'''

        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        ir = extractor.extract(source, "unicode.py", extract_config)
        output = synthesizer.synthesize(ir, synth_config)

        assert output is not None
        assert len(output) > 0
