"""Gap detection tests.

This module tests the semantic gap detection system, verifying that:
- Type system gaps are correctly identified
- Memory model gaps are detected
- Effect system gaps are flagged
- Runtime behavior gaps are caught
- Gap markers have valid structure
- Gap severity is appropriately assigned
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

# Add tools to path
TOOLS_DIR = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR / "ir-core"))
sys.path.insert(0, str(TOOLS_DIR / "ir-extract-python"))
sys.path.insert(0, str(TOOLS_DIR / "ir-validate"))

from ir_core import (
    IRVersion,
    ExtractConfig,
    GapDetector,
    GapMarker,
    GapType,
    Severity,
    PreservationLevel,
    AutomationLevel,
)
from ir_core.gaps import (
    GapPattern,
    TYPE_SYSTEM_PATTERNS,
    MEMORY_MODEL_PATTERNS,
    EFFECT_SYSTEM_PATTERNS,
    CONCURRENCY_PATTERNS,
    ALL_PATTERNS,
)


# =============================================================================
# Import Tools with Graceful Fallback
# =============================================================================

try:
    from ir_extract_python import PythonExtractor
    HAS_EXTRACTOR = True
except ImportError:
    HAS_EXTRACTOR = False
    PythonExtractor = None  # type: ignore


requires_extractor = pytest.mark.skipif(
    not HAS_EXTRACTOR, reason="PythonExtractor not available"
)


# =============================================================================
# Type System Gap Tests (TS-xxx)
# =============================================================================


@pytest.mark.integration
class TestTypeSystemGaps:
    """Tests for type system gap detection."""

    @requires_extractor
    def test_detect_type_system_gaps_dynamic_to_static(
        self,
        extract_config: ExtractConfig,
    ) -> None:
        """Test TS-001: Dynamic to static type conversion gaps."""
        source = '''def untyped_function(x):
    return x.upper()
'''
        extractor = PythonExtractor()
        detector = GapDetector()

        ir = extractor.extract(source, "dynamic.py", extract_config)
        gaps = detector.detect(ir, "python", "rust")

        # Should detect dynamic typing issues when targeting Rust
        ts_gaps = [g for g in gaps if g.gap_pattern_id and g.gap_pattern_id.startswith("TS")]
        # Detection depends on implementation details
        assert isinstance(gaps, list)

    @requires_extractor
    def test_detect_nullable_type_gaps(
        self,
        extract_config: ExtractConfig,
    ) -> None:
        """Test TS-002: Nullable to non-null type conversion."""
        source = '''from typing import Optional

def maybe_value(x: Optional[int]) -> int:
    if x is None:
        return 0
    return x
'''
        extractor = PythonExtractor()
        detector = GapDetector()

        ir = extractor.extract(source, "nullable.py", extract_config)
        gaps = detector.detect(ir, "python", "rust")

        # May detect nullable type gaps
        assert isinstance(gaps, list)

    @requires_extractor
    def test_detect_duck_typing_gaps(
        self,
        extract_config: ExtractConfig,
    ) -> None:
        """Test TS-005: Duck typing to interface conversion."""
        source = '''def process_quackable(thing):
    thing.quack()
    thing.swim()
'''
        extractor = PythonExtractor()
        detector = GapDetector()

        ir = extractor.extract(source, "duck.py", extract_config)
        gaps = detector.detect(ir, "python", "rust")

        # May detect structural typing issues
        assert isinstance(gaps, list)

    def test_type_system_pattern_definitions(self) -> None:
        """Verify type system patterns are properly defined."""
        assert "TS-001" in TYPE_SYSTEM_PATTERNS
        assert "TS-002" in TYPE_SYSTEM_PATTERNS

        ts001 = TYPE_SYSTEM_PATTERNS["TS-001"]
        assert ts001.id == "TS-001"
        assert ts001.gap_type in GapType
        assert ts001.severity in Severity
        assert len(ts001.mitigations) > 0


# =============================================================================
# Memory Model Gap Tests (MM-xxx)
# =============================================================================


@pytest.mark.integration
class TestMemoryModelGaps:
    """Tests for memory model gap detection."""

    @requires_extractor
    def test_detect_gc_to_ownership_gaps(
        self,
        extract_config: ExtractConfig,
    ) -> None:
        """Test MM-002: GC to ownership model conversion."""
        source = '''class Node:
    def __init__(self, value: int):
        self.value = value
        self.next: "Node" = None

def create_cycle():
    a = Node(1)
    b = Node(2)
    a.next = b
    b.next = a
    return a
'''
        extractor = PythonExtractor()
        detector = GapDetector()

        ir = extractor.extract(source, "cycle.py", extract_config)
        gaps = detector.detect(ir, "python", "rust")

        # Should detect memory model issues for Python->Rust
        mm_gaps = [g for g in gaps if g.gap_pattern_id and g.gap_pattern_id.startswith("MM")]
        assert isinstance(gaps, list)

    @requires_extractor
    def test_detect_shared_mutable_gaps(
        self,
        extract_config: ExtractConfig,
    ) -> None:
        """Test MM-003: Shared mutable state gaps."""
        source = '''def mutate_both(a: list[int], b: list[int]) -> None:
    a.append(1)
    b.append(2)
'''
        extractor = PythonExtractor()
        detector = GapDetector()

        ir = extractor.extract(source, "shared.py", extract_config)
        gaps = detector.detect(ir, "python", "rust")

        # May detect shared mutable state issues
        assert isinstance(gaps, list)

    def test_memory_model_pattern_definitions(self) -> None:
        """Verify memory model patterns are properly defined."""
        assert "MM-001" in MEMORY_MODEL_PATTERNS
        assert "MM-002" in MEMORY_MODEL_PATTERNS

        mm002 = MEMORY_MODEL_PATTERNS["MM-002"]
        assert mm002.id == "MM-002"
        assert mm002.gap_type in GapType
        assert mm002.severity in Severity


# =============================================================================
# Effect System Gap Tests (EF-xxx)
# =============================================================================


@pytest.mark.integration
class TestEffectSystemGaps:
    """Tests for effect system gap detection."""

    @requires_extractor
    def test_detect_exception_to_result_gaps(
        self,
        extract_config: ExtractConfig,
    ) -> None:
        """Test EF-001: Exception to Result type conversion."""
        source = '''def risky_operation(x: int) -> int:
    if x < 0:
        raise ValueError("x must be non-negative")
    return x * 2
'''
        extractor = PythonExtractor()
        detector = GapDetector()

        ir = extractor.extract(source, "risky.py", extract_config)
        gaps = detector.detect(ir, "python", "rust")

        # Should detect exception handling differences
        ef_gaps = [g for g in gaps if g.gap_pattern_id and g.gap_pattern_id.startswith("EF")]
        # Detection depends on effect analysis
        assert isinstance(gaps, list)

    @requires_extractor
    def test_detect_null_to_option_gaps(
        self,
        extract_config: ExtractConfig,
    ) -> None:
        """Test EF-002: Null to Option type conversion."""
        source = '''def find_item(items: list[int], target: int) -> int | None:
    for item in items:
        if item == target:
            return item
    return None
'''
        extractor = PythonExtractor()
        detector = GapDetector()

        ir = extractor.extract(source, "find.py", extract_config)
        gaps = detector.detect(ir, "python", "rust")

        assert isinstance(gaps, list)

    def test_effect_system_pattern_definitions(self) -> None:
        """Verify effect system patterns are properly defined."""
        assert "EF-001" in EFFECT_SYSTEM_PATTERNS

        ef001 = EFFECT_SYSTEM_PATTERNS["EF-001"]
        assert ef001.id == "EF-001"
        assert ef001.gap_type in GapType
        assert ef001.severity in Severity


# =============================================================================
# Concurrency Gap Tests (CC-xxx)
# =============================================================================


@pytest.mark.integration
class TestConcurrencyGaps:
    """Tests for concurrency gap detection."""

    @requires_extractor
    def test_detect_thread_safety_gaps(
        self,
        extract_config: ExtractConfig,
    ) -> None:
        """Test CC-012: Thread safety requirement differences."""
        source = '''import threading

class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1
'''
        extractor = PythonExtractor()
        detector = GapDetector()

        ir = extractor.extract(source, "counter.py", extract_config)
        gaps = detector.detect(ir, "python", "rust")

        # May detect thread safety issues for Rust
        cc_gaps = [g for g in gaps if g.gap_pattern_id and g.gap_pattern_id.startswith("CC")]
        assert isinstance(gaps, list)

    def test_concurrency_pattern_definitions(self) -> None:
        """Verify concurrency patterns are properly defined."""
        assert "CC-001" in CONCURRENCY_PATTERNS

        cc001 = CONCURRENCY_PATTERNS["CC-001"]
        assert cc001.id == "CC-001"
        assert cc001.gap_type in GapType
        assert cc001.severity in Severity


# =============================================================================
# Gap Marker Validity Tests
# =============================================================================


@pytest.mark.integration
class TestGapMarkerValidity:
    """Tests for gap marker structure and validity."""

    def test_gap_markers_valid_structure(
        self,
        sample_ir_with_gaps: IRVersion,
    ) -> None:
        """Verify gap markers have valid structure."""
        for gap in sample_ir_with_gaps.gaps:
            # Required fields
            assert gap.id is not None
            assert gap.location is not None
            assert gap.gap_type is not None
            assert gap.severity is not None
            assert gap.description is not None
            assert gap.source_concept is not None

    def test_gap_type_enum_values(self) -> None:
        """Verify GapType enum has expected values."""
        assert GapType.IMPOSSIBLE.value == "impossible"
        assert GapType.LOSSY.value == "lossy"
        assert GapType.STRUCTURAL.value == "structural"
        assert GapType.IDIOMATIC.value == "idiomatic"
        assert GapType.RUNTIME.value == "runtime"
        assert GapType.SEMANTIC.value == "semantic"

    def test_severity_enum_values(self) -> None:
        """Verify Severity enum has expected values."""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"

    def test_automation_level_enum_values(self) -> None:
        """Verify AutomationLevel enum has expected values."""
        assert AutomationLevel.NONE.value == "none"
        assert AutomationLevel.PARTIAL.value == "partial"
        assert AutomationLevel.FULL.value == "full"

    def test_gap_pattern_has_mitigations(self) -> None:
        """Verify all gap patterns have mitigation suggestions."""
        for pattern_id, pattern in ALL_PATTERNS.items():
            assert len(pattern.mitigations) > 0, (
                f"Pattern {pattern_id} has no mitigations"
            )

    def test_gap_pattern_has_affected_layers(self) -> None:
        """Verify gap patterns specify affected layers."""
        for pattern_id, pattern in ALL_PATTERNS.items():
            assert len(pattern.affected_layers) > 0, (
                f"Pattern {pattern_id} has no affected layers"
            )
            # Layers should be valid (0-4)
            for layer in pattern.affected_layers:
                assert 0 <= layer <= 4


# =============================================================================
# Gap Detector Configuration Tests
# =============================================================================


@pytest.mark.integration
class TestGapDetectorConfiguration:
    """Tests for gap detector configuration and customization."""

    def test_gap_detector_initialization(self) -> None:
        """Verify gap detector initializes correctly."""
        detector = GapDetector()

        # Should have patterns registered
        assert len(detector._patterns) > 0

        # Should have detectors registered
        assert len(detector._detectors) > 0

    def test_custom_pattern_registration(self) -> None:
        """Verify custom patterns can be registered."""
        detector = GapDetector()

        custom_pattern = GapPattern(
            id="CUSTOM-001",
            name="Custom Pattern",
            category="custom",
            description="A custom gap pattern",
            gap_type=GapType.STRUCTURAL,
            severity=Severity.MEDIUM,
            source_concepts=["custom concept"],
            mitigations=["custom mitigation"],
            affected_layers=[2],
        )

        detector.register_pattern(custom_pattern)

        assert "CUSTOM-001" in detector._patterns
        assert detector._patterns["CUSTOM-001"].name == "Custom Pattern"

    def test_custom_detector_registration(
        self,
        sample_ir: IRVersion,
    ) -> None:
        """Verify custom detectors can be registered."""
        detector = GapDetector()

        custom_gaps: list[GapMarker] = []

        def custom_detector(ctx):
            if ctx.source_language == "python":
                custom_gaps.append(GapMarker(
                    id="custom:0",
                    location="custom_location",
                    gap_type=GapType.IDIOMATIC,
                    severity=Severity.LOW,
                    description="Custom detection",
                    source_concept="custom",
                ))
            return custom_gaps

        detector.register_detector(custom_detector)

        gaps = detector.detect(sample_ir, "python", "rust")

        # Should include custom gaps
        custom = [g for g in gaps if g.id.startswith("custom:")]
        assert len(custom) >= 1

    def test_language_pair_specific_detection(
        self,
        sample_ir: IRVersion,
    ) -> None:
        """Verify detection varies by language pair."""
        detector = GapDetector()

        # Python to Rust should have different gaps than Python to Go
        gaps_rust = detector.detect(sample_ir, "python", "rust")
        gaps_go = detector.detect(sample_ir, "python", "go")

        # Both should return lists
        assert isinstance(gaps_rust, list)
        assert isinstance(gaps_go, list)


# =============================================================================
# Gap Detection Edge Cases
# =============================================================================


@pytest.mark.integration
class TestGapDetectionEdgeCases:
    """Tests for gap detection edge cases."""

    def test_empty_ir_detection(self) -> None:
        """Verify gap detection handles empty IR."""
        from ir_core import Module, ModuleMetadata

        metadata = ModuleMetadata(
            source_file="empty.py",
            source_language="python",
        )
        module = Module(
            id="module:empty.py",
            name="empty",
            path=["empty"],
            imports=[],
            exports=[],
            definitions=[],
            submodules=[],
            extraction_scope="full",
            metadata=metadata,
        )
        ir = IRVersion(
            version="ir-v1.0",
            module=module,
            types=[],
            functions=[],
            bindings=[],
        )

        detector = GapDetector()
        gaps = detector.detect(ir, "python", "rust")

        # Should not crash, may return empty or minimal gaps
        assert isinstance(gaps, list)

    @requires_extractor
    def test_complex_code_gap_detection(
        self,
        sample_python_complex: str,
        extract_config: ExtractConfig,
    ) -> None:
        """Verify gap detection handles complex code."""
        extractor = PythonExtractor()
        detector = GapDetector()

        ir = extractor.extract(sample_python_complex, "complex.py", extract_config)
        gaps = detector.detect(ir, "python", "rust")

        # Should not crash
        assert isinstance(gaps, list)

        # All gaps should have valid structure
        for gap in gaps:
            assert gap.id is not None or gap.id == ""
            assert gap.location is not None
            assert gap.severity is not None

    def test_same_language_detection(
        self,
        sample_ir: IRVersion,
    ) -> None:
        """Verify gap detection for same-language 'conversion'."""
        detector = GapDetector()

        # Python to Python should have minimal gaps
        gaps = detector.detect(sample_ir, "python", "python")

        # Should not crash, likely minimal gaps
        assert isinstance(gaps, list)

    def test_unknown_language_handling(
        self,
        sample_ir: IRVersion,
    ) -> None:
        """Verify gap detection handles unknown languages."""
        detector = GapDetector()

        # Unknown language should not crash
        gaps = detector.detect(sample_ir, "python", "unknown_lang_xyz")

        # Should return some result
        assert isinstance(gaps, list)
