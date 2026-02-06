"""Tests for gap detection."""

from __future__ import annotations

import pytest

from ir_core.models import (
    Binding,
    Effect,
    EffectKind,
    Function,
    GapType,
    IRVersion,
    Module,
    ModuleMetadata,
    Mutability,
    Param,
    PreservationLevel,
    Severity,
    TypeDef,
    TypeKind,
    TypeRef,
    TypeRefKind,
    TypeBody,
    Field_,
)
from ir_core.gaps import (
    GapDetector,
    GapPattern,
    DetectionContext,
    ALL_PATTERNS,
    detect_gaps,
)


class TestGapPattern:
    """Tests for GapPattern definitions."""

    def test_patterns_exist(self) -> None:
        """Test that expected patterns are defined."""
        assert "TS-001" in ALL_PATTERNS
        assert "MM-002" in ALL_PATTERNS
        assert "EF-001" in ALL_PATTERNS
        assert "CC-001" in ALL_PATTERNS

    def test_pattern_structure(self) -> None:
        """Test that patterns have required fields."""
        for pattern_id, pattern in ALL_PATTERNS.items():
            assert pattern.id == pattern_id
            assert pattern.name
            assert pattern.category
            assert pattern.description
            assert isinstance(pattern.gap_type, GapType)
            assert isinstance(pattern.severity, Severity)
            assert isinstance(pattern.preservation_impact, PreservationLevel)


class TestGapDetector:
    """Tests for GapDetector."""

    def test_detect_empty_ir(self) -> None:
        """Test detection on minimal IR produces no errors."""
        ir = IRVersion(
            module=Module(
                id="mod:test",
                name="test",
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                ),
            ),
        )

        detector = GapDetector()
        # Same language conversion should have minimal gaps
        gaps = detector.detect(ir, "python", "python")

        # Should not crash and should assign IDs
        for gap in gaps:
            assert gap.id

    def test_detect_dynamic_to_static(self) -> None:
        """Test detection of dynamic to static typing gap."""
        ir = IRVersion(
            module=Module(
                id="mod:test",
                name="test",
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                ),
            ),
            bindings=[
                Binding(
                    id="bind:data",
                    name="data",
                    type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:Any"),
                    mutability=Mutability.IMMUTABLE,
                ),
            ],
        )

        detector = GapDetector()
        gaps = detector.detect(ir, "python", "rust")

        # Should detect TS-001 (dynamic to static)
        ts001_gaps = [g for g in gaps if g.gap_pattern_id == "TS-001"]
        assert len(ts001_gaps) > 0

    def test_detect_gc_to_ownership(self) -> None:
        """Test detection of GC to ownership gap."""
        ir = IRVersion(
            module=Module(
                id="mod:test",
                name="test",
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                ),
            ),
            bindings=[
                Binding(
                    id="bind:items",
                    name="items",
                    type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:List"),
                    mutability=Mutability.MUTABLE,
                ),
            ],
        )

        detector = GapDetector()
        gaps = detector.detect(ir, "python", "rust")

        # Should detect MM-002 (GC to ownership)
        mm002_gaps = [g for g in gaps if g.gap_pattern_id == "MM-002"]
        assert len(mm002_gaps) > 0

    def test_detect_exceptions_to_result(self) -> None:
        """Test detection of exception to Result gap."""
        ir = IRVersion(
            module=Module(
                id="mod:test",
                name="test",
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                ),
            ),
            functions=[
                Function(
                    id="fn:read_file",
                    name="read_file",
                    params=[
                        Param(
                            name="path",
                            type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:str"),
                        ),
                    ],
                    return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:str"),
                    effects=[
                        Effect(
                            kind=EffectKind.THROWS,
                            type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:IOError"),
                        ),
                    ],
                ),
            ],
        )

        detector = GapDetector()
        gaps = detector.detect(ir, "python", "rust")

        # Should detect EF-001 (exceptions to Result)
        ef001_gaps = [g for g in gaps if g.gap_pattern_id == "EF-001"]
        assert len(ef001_gaps) > 0

    def test_detect_actors_to_threads(self) -> None:
        """Test detection of actor to thread gap."""
        ir = IRVersion(
            module=Module(
                id="mod:server",
                name="server",
                metadata=ModuleMetadata(
                    source_file="server.ex",
                    source_language="elixir",
                ),
            ),
        )

        detector = GapDetector()
        gaps = detector.detect(ir, "elixir", "rust")

        # Should detect CC-001 (actors to threads)
        cc001_gaps = [g for g in gaps if g.gap_pattern_id == "CC-001"]
        assert len(cc001_gaps) > 0

    def test_detect_multiple_mutable_params(self) -> None:
        """Test detection of aliasing risk from multiple mutable params."""
        ir = IRVersion(
            module=Module(
                id="mod:test",
                name="test",
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                ),
            ),
            functions=[
                Function(
                    id="fn:transfer",
                    name="transfer",
                    params=[
                        Param(
                            name="from_account",
                            type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:Account"),
                            mutability=Mutability.MUTABLE,
                        ),
                        Param(
                            name="to_account",
                            type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:Account"),
                            mutability=Mutability.MUTABLE,
                        ),
                    ],
                    return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:None"),
                ),
            ],
        )

        detector = GapDetector()
        gaps = detector.detect(ir, "python", "rust")

        # Should detect MM-003 (shared to linear)
        mm003_gaps = [g for g in gaps if g.gap_pattern_id == "MM-003"]
        assert len(mm003_gaps) > 0

    def test_detect_thread_safety(self) -> None:
        """Test detection of thread safety requirements."""
        ir = IRVersion(
            module=Module(
                id="mod:test",
                name="test",
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                ),
            ),
            types=[
                TypeDef(
                    id="type:Counter",
                    name="Counter",
                    kind=TypeKind.STRUCT,
                    body=TypeBody(
                        fields=[
                            Field_(
                                name="value",
                                type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:i32"),
                                mutability=Mutability.MUTABLE,
                            ),
                        ],
                    ),
                ),
            ],
        )

        detector = GapDetector()
        gaps = detector.detect(ir, "python", "rust")

        # Should detect CC-012 (thread safety)
        cc012_gaps = [g for g in gaps if g.gap_pattern_id == "CC-012"]
        assert len(cc012_gaps) > 0

    def test_register_custom_pattern(self) -> None:
        """Test registering a custom gap pattern."""
        custom_pattern = GapPattern(
            id="CUSTOM-001",
            name="Custom Pattern",
            category="custom",
            description="A custom gap pattern for testing",
            gap_type=GapType.STRUCTURAL,
            severity=Severity.LOW,
        )

        detector = GapDetector()
        detector.register_pattern(custom_pattern)

        assert "CUSTOM-001" in detector._patterns

    def test_register_custom_detector(self) -> None:
        """Test registering a custom detector function."""
        ir = IRVersion(
            module=Module(
                id="mod:test",
                name="test",
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                ),
            ),
        )

        def custom_detector(ctx: DetectionContext) -> list:
            from ir_core.models import GapMarker, AutomationLevel
            return [
                GapMarker(
                    id="custom-gap",
                    location=ctx.ir.module.id,
                    gap_type=GapType.IDIOMATIC,
                    severity=Severity.LOW,
                    description="Custom detected gap",
                    source_concept="custom",
                )
            ]

        detector = GapDetector()
        detector.register_detector(custom_detector)

        gaps = detector.detect(ir, "python", "rust")

        # Should include custom gap
        custom_gaps = [g for g in gaps if g.description == "Custom detected gap"]
        assert len(custom_gaps) > 0


class TestDetectGapsFunction:
    """Tests for detect_gaps convenience function."""

    def test_detect_gaps_function(self) -> None:
        """Test detect_gaps convenience function."""
        ir = IRVersion(
            module=Module(
                id="mod:test",
                name="test",
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                ),
            ),
        )

        gaps = detect_gaps(ir, "python", "rust")

        # Should return list of gaps
        assert isinstance(gaps, list)

    def test_gap_marker_fields(self) -> None:
        """Test that detected gaps have required fields."""
        ir = IRVersion(
            module=Module(
                id="mod:test",
                name="test",
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                ),
            ),
            bindings=[
                Binding(
                    id="bind:x",
                    name="x",
                    type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:Any"),
                    mutability=Mutability.MUTABLE,
                ),
            ],
        )

        gaps = detect_gaps(ir, "python", "rust")

        for gap in gaps:
            assert gap.id
            assert gap.location
            assert gap.gap_type
            assert gap.severity
            assert gap.description
            assert gap.source_concept
