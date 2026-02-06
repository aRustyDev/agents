"""Tests for IR data models."""

from __future__ import annotations

import pytest
from datetime import datetime

from ir_core.models import (
    # Enums
    GapType,
    Severity,
    PreservationLevel,
    Visibility,
    Mutability,
    LifetimeKind,
    TypeKind,
    TypeRefKind,
    EffectKind,
    ExtractionMode,
    # Models
    SourceSpan,
    TypeRef,
    TypeParam,
    TypeDef,
    TypeBody,
    Effect,
    Param,
    Function,
    Binding,
    Lifetime,
    Module,
    ModuleMetadata,
    Import,
    Export,
    Definition,
    DefinitionRef,
    SemanticAnnotation,
    GapMarker,
    PreservationStatus,
    LevelEvidence,
    IRVersion,
    # Errors
    ExtractionError,
    ExtractionErrorCode,
    ValidationError,
    ValidationErrorCode,
)


class TestSourceSpan:
    """Tests for SourceSpan model."""

    def test_create_source_span(self) -> None:
        """Test creating a SourceSpan."""
        span = SourceSpan(
            file="test.py",
            start_line=10,
            start_col=5,
            end_line=10,
            end_col=20,
        )
        assert span.file == "test.py"
        assert span.start_line == 10
        assert span.start_col == 5
        assert span.end_line == 10
        assert span.end_col == 20

    def test_span_contains(self) -> None:
        """Test SourceSpan.contains method."""
        outer = SourceSpan(
            file="test.py",
            start_line=1,
            start_col=0,
            end_line=10,
            end_col=50,
        )
        inner = SourceSpan(
            file="test.py",
            start_line=5,
            start_col=10,
            end_line=5,
            end_col=30,
        )
        assert outer.contains(inner)
        assert not inner.contains(outer)

    def test_span_different_files(self) -> None:
        """Test that spans from different files don't contain each other."""
        span1 = SourceSpan(
            file="a.py",
            start_line=1,
            start_col=0,
            end_line=100,
            end_col=100,
        )
        span2 = SourceSpan(
            file="b.py",
            start_line=1,
            start_col=0,
            end_line=10,
            end_col=10,
        )
        assert not span1.contains(span2)


class TestTypeRef:
    """Tests for TypeRef model."""

    def test_named_type_ref(self) -> None:
        """Test creating a named type reference."""
        type_ref = TypeRef(
            kind=TypeRefKind.NAMED,
            type_id="type:String",
        )
        assert type_ref.kind == TypeRefKind.NAMED
        assert type_ref.type_id == "type:String"

    def test_generic_type_ref(self) -> None:
        """Test creating a generic type reference."""
        inner = TypeRef(kind=TypeRefKind.NAMED, type_id="type:i32")
        type_ref = TypeRef(
            kind=TypeRefKind.NAMED,
            type_id="type:Vec",
            args=[inner],
        )
        assert type_ref.type_id == "type:Vec"
        assert len(type_ref.args) == 1
        assert type_ref.args[0].type_id == "type:i32"

    def test_function_type_ref(self) -> None:
        """Test creating a function type reference."""
        type_ref = TypeRef(
            kind=TypeRefKind.FUNCTION,
            params=[
                TypeRef(kind=TypeRefKind.NAMED, type_id="type:i32"),
                TypeRef(kind=TypeRefKind.NAMED, type_id="type:i32"),
            ],
            return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:i32"),
        )
        assert type_ref.kind == TypeRefKind.FUNCTION
        assert len(type_ref.params) == 2
        assert type_ref.return_type is not None


class TestTypeDef:
    """Tests for TypeDef model."""

    def test_struct_type_def(self) -> None:
        """Test creating a struct type definition."""
        type_def = TypeDef(
            id="type:Point",
            name="Point",
            kind=TypeKind.STRUCT,
            body=TypeBody(
                fields=[],
            ),
        )
        assert type_def.id == "type:Point"
        assert type_def.kind == TypeKind.STRUCT

    def test_enum_type_def(self) -> None:
        """Test creating an enum type definition."""
        type_def = TypeDef(
            id="type:Option",
            name="Option",
            kind=TypeKind.ENUM,
            params=[
                TypeParam(name="T"),
            ],
        )
        assert type_def.kind == TypeKind.ENUM
        assert len(type_def.params) == 1


class TestFunction:
    """Tests for Function model."""

    def test_simple_function(self) -> None:
        """Test creating a simple function."""
        func = Function(
            id="fn:add",
            name="add",
            params=[
                Param(
                    name="a",
                    type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:i32"),
                ),
                Param(
                    name="b",
                    type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:i32"),
                ),
            ],
            return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:i32"),
        )
        assert func.name == "add"
        assert len(func.params) == 2

    def test_async_function(self) -> None:
        """Test creating an async function with effects."""
        func = Function(
            id="fn:fetch",
            name="fetch",
            params=[
                Param(
                    name="url",
                    type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:String"),
                ),
            ],
            return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:Response"),
            effects=[
                Effect(kind=EffectKind.ASYNC),
                Effect(
                    kind=EffectKind.THROWS,
                    type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:NetworkError"),
                ),
            ],
        )
        assert len(func.effects) == 2
        assert func.effects[0].kind == EffectKind.ASYNC


class TestBinding:
    """Tests for Binding model."""

    def test_immutable_binding(self) -> None:
        """Test creating an immutable binding."""
        binding = Binding(
            id="bind:x",
            name="x",
            type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:i32"),
            mutability=Mutability.IMMUTABLE,
        )
        assert binding.mutability == Mutability.IMMUTABLE

    def test_binding_with_lifetime(self) -> None:
        """Test creating a binding with lifetime."""
        binding = Binding(
            id="bind:data",
            name="data",
            type=TypeRef(kind=TypeRefKind.NAMED, type_id="type:Vec"),
            lifetime=Lifetime(
                kind=LifetimeKind.OWNED,
            ),
        )
        assert binding.lifetime.kind == LifetimeKind.OWNED


class TestModule:
    """Tests for Module model."""

    def test_simple_module(self) -> None:
        """Test creating a simple module."""
        module = Module(
            id="mod:mymodule",
            name="mymodule",
            path=["mypackage"],
            metadata=ModuleMetadata(
                source_file="mypackage/mymodule.py",
                source_language="python",
            ),
        )
        assert module.name == "mymodule"
        assert module.metadata.source_language == "python"

    def test_module_with_imports(self) -> None:
        """Test module with imports."""
        module = Module(
            id="mod:main",
            name="main",
            imports=[
                Import(
                    id="imp:typing",
                    module_path=["typing"],
                ),
            ],
            metadata=ModuleMetadata(
                source_file="main.py",
                source_language="python",
            ),
        )
        assert len(module.imports) == 1


class TestGapMarker:
    """Tests for GapMarker model."""

    def test_create_gap_marker(self) -> None:
        """Test creating a gap marker."""
        gap = GapMarker(
            id="gap-001",
            location="fn:process",
            gap_type=GapType.STRUCTURAL,
            severity=Severity.HIGH,
            description="GC to ownership conversion needed",
            source_concept="garbage collection",
            target_concept="ownership model",
            suggested_mitigations=[
                "Add Rc/Arc wrappers",
                "Redesign ownership hierarchy",
            ],
        )
        assert gap.gap_type == GapType.STRUCTURAL
        assert gap.severity == Severity.HIGH
        assert len(gap.suggested_mitigations) == 2


class TestPreservationStatus:
    """Tests for PreservationStatus model."""

    def test_preservation_status(self) -> None:
        """Test creating preservation status."""
        status = PreservationStatus(
            id="pres-001",
            unit_id="mod:main",
            current_level=PreservationLevel.SEMANTIC,
            max_achievable_level=PreservationLevel.IDIOMATIC,
            blocking_gaps=["gap-001"],
            level_evidence={
                0: LevelEvidence(achieved=True, verifier="rustc"),
                1: LevelEvidence(achieved=True, test_coverage=0.85),
            },
        )
        assert status.current_level == PreservationLevel.SEMANTIC
        assert status.level_evidence[0].achieved is True


class TestIRVersion:
    """Tests for IRVersion model."""

    def test_create_ir_version(self) -> None:
        """Test creating a complete IRVersion."""
        ir = IRVersion(
            version="ir-v1.0",
            module=Module(
                id="mod:test",
                name="test",
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                ),
            ),
        )
        assert ir.version == "ir-v1.0"
        assert ir.module.name == "test"

    def test_content_hash(self) -> None:
        """Test content hash computation."""
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
        hash1 = ir.content_hash()

        # Same content should produce same hash
        ir2 = IRVersion(
            module=Module(
                id="mod:test",
                name="test",
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                ),
            ),
        )
        hash2 = ir2.content_hash()

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length

    def test_different_content_different_hash(self) -> None:
        """Test that different content produces different hash."""
        ir1 = IRVersion(
            module=Module(
                id="mod:a",
                name="a",
                metadata=ModuleMetadata(
                    source_file="a.py",
                    source_language="python",
                ),
            ),
        )
        ir2 = IRVersion(
            module=Module(
                id="mod:b",
                name="b",
                metadata=ModuleMetadata(
                    source_file="b.py",
                    source_language="python",
                ),
            ),
        )
        assert ir1.content_hash() != ir2.content_hash()


class TestErrors:
    """Tests for error classes."""

    def test_extraction_error(self) -> None:
        """Test ExtractionError."""
        error = ExtractionError(
            code=ExtractionErrorCode.E001,
            message="Syntax error",
            location=SourceSpan(
                file="test.py",
                start_line=10,
                start_col=5,
                end_line=10,
                end_col=10,
            ),
        )
        assert error.code == ExtractionErrorCode.E001
        assert "E001" in str(error)

    def test_validation_error(self) -> None:
        """Test ValidationError."""
        error = ValidationError(
            code=ValidationErrorCode.V001,
            message="Schema mismatch",
            path="$.module.name",
        )
        assert error.code == ValidationErrorCode.V001
        assert error.path == "$.module.name"
