"""Tests for IR validation."""

from __future__ import annotations

from ir_core.models import (
    AnnotationSource,
    Definition,
    DefinitionRef,
    Export,
    GapMarker,
    GapType,
    IRVersion,
    Module,
    ModuleMetadata,
    PreservationLevel,
    PreservationStatus,
    SemanticAnnotation,
    Severity,
    TypeBody,
    TypeDef,
    TypeKind,
)
from ir_core.validation import (
    SchemaValidator,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
    validate_ir,
)


class TestValidationResult:
    """Tests for ValidationResult."""

    def test_empty_result_is_valid(self) -> None:
        """Test that empty result is valid."""
        result = ValidationResult()
        assert result.is_valid
        assert result.error_count == 0
        assert result.warning_count == 0

    def test_add_error_invalidates(self) -> None:
        """Test that adding error invalidates result."""
        result = ValidationResult()
        from ir_core.models import ValidationErrorCode
        result.add_issue(ValidationIssue(
            code=ValidationErrorCode.V001,
            severity=ValidationSeverity.ERROR,
            message="Test error",
        ))
        assert not result.is_valid
        assert result.error_count == 1

    def test_add_warning_keeps_valid(self) -> None:
        """Test that adding warning keeps result valid."""
        result = ValidationResult()
        from ir_core.models import ValidationErrorCode
        result.add_issue(ValidationIssue(
            code=ValidationErrorCode.V001,
            severity=ValidationSeverity.WARNING,
            message="Test warning",
        ))
        assert result.is_valid
        assert result.warning_count == 1


class TestSchemaValidator:
    """Tests for SchemaValidator."""

    def test_validate_valid_ir(self) -> None:
        """Test validating a valid IR."""
        ir = IRVersion(
            version="ir-v1.0",
            module=Module(
                id="mod:test",
                name="test",
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                    extraction_version="ir-v1.0",
                ),
            ),
        )

        validator = SchemaValidator()
        result = validator.validate(ir)

        # Should pass basic validation
        # Note: May have warnings but should not have critical errors
        assert result.checked_count > 0

    def test_validate_missing_version(self) -> None:
        """Test validating IR dict with missing version."""
        ir_dict = {
            "module": {
                "id": "mod:test",
                "name": "test",
                "metadata": {
                    "source_file": "test.py",
                    "source_language": "python",
                },
            },
        }

        validator = SchemaValidator()
        result = validator.validate_schema(ir_dict)

        # Should detect missing version
        assert any("version" in str(issue) for issue in result.issues)

    def test_validate_cross_references(self) -> None:
        """Test cross-reference validation."""
        ir = IRVersion(
            module=Module(
                id="mod:test",
                name="test",
                definitions=[
                    Definition(
                        id="def:MyType",
                        kind="type",
                        ref="type:MyType",
                    ),
                ],
                exports=[
                    Export(
                        id="exp:MyType",
                        item=DefinitionRef(
                            module_id="mod:test",
                            definition_id="def:MyType",
                        ),
                    ),
                ],
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                ),
            ),
            types=[
                TypeDef(
                    id="type:MyType",
                    name="MyType",
                    kind=TypeKind.STRUCT,
                    body=TypeBody(),
                ),
            ],
        )

        validator = SchemaValidator()
        result = validator.validate(ir)

        # Should validate without cross-reference errors
        cross_ref_errors = [
            i for i in result.errors
            if i.code.value == "V002"
        ]
        assert len(cross_ref_errors) == 0

    def test_validate_export_references_undefined(self) -> None:
        """Test that exports referencing undefined definitions are flagged."""
        ir = IRVersion(
            module=Module(
                id="mod:test",
                name="test",
                definitions=[],  # No definitions
                exports=[
                    Export(
                        id="exp:Missing",
                        item=DefinitionRef(
                            module_id="mod:test",
                            definition_id="def:Missing",  # References non-existent
                        ),
                    ),
                ],
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                ),
            ),
        )

        validator = SchemaValidator()
        result = validator.validate(ir)

        # Should detect undefined reference
        consistency_errors = [
            i for i in result.issues
            if i.code.value == "V003"
        ]
        assert len(consistency_errors) > 0

    def test_validate_preservation_level_consistency(self) -> None:
        """Test that preservation level consistency is checked."""
        ir = IRVersion(
            module=Module(
                id="mod:test",
                name="test",
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                ),
            ),
            preservation=PreservationStatus(
                id="pres:test",
                unit_id="mod:test",
                current_level=PreservationLevel.OPTIMIZED,  # Level 3
                max_achievable_level=PreservationLevel.SEMANTIC,  # Level 1
            ),
        )

        validator = SchemaValidator()
        result = validator.validate(ir)

        # Should detect that current > max achievable
        semantic_errors = [
            i for i in result.issues
            if i.code.value == "V004" and "preservation level" in i.message.lower()
        ]
        assert len(semantic_errors) > 0

    def test_validate_annotation_confidence(self) -> None:
        """Test that annotation confidence is validated."""
        ir = IRVersion(
            module=Module(
                id="mod:test",
                name="test",
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                ),
            ),
            annotations=[
                SemanticAnnotation(
                    id="ann:test",
                    target="mod:test",
                    kind="test_annotation",
                    confidence=0.5,  # Valid
                    source=AnnotationSource.INFERRED,
                ),
            ],
        )

        validator = SchemaValidator()
        result = validator.validate(ir)

        # Valid confidence should not cause errors
        confidence_errors = [
            i for i in result.errors
            if "confidence" in i.message.lower()
        ]
        assert len(confidence_errors) == 0

    def test_validate_gap_severity_for_impossible(self) -> None:
        """Test that impossible gaps should have critical severity."""
        ir = IRVersion(
            module=Module(
                id="mod:test",
                name="test",
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                ),
            ),
            gaps=[
                GapMarker(
                    id="gap:test",
                    location="mod:test",
                    gap_type=GapType.IMPOSSIBLE,
                    severity=Severity.LOW,  # Should be critical
                    description="Test impossible gap",
                    source_concept="test",
                ),
            ],
        )

        validator = SchemaValidator()
        result = validator.validate(ir)

        # Should warn about severity mismatch
        severity_warnings = [
            i for i in result.warnings
            if "impossible" in i.message.lower() and "critical" in i.message.lower()
        ]
        assert len(severity_warnings) > 0


class TestValidateIRFunction:
    """Tests for validate_ir convenience function."""

    def test_validate_ir_function(self) -> None:
        """Test validate_ir convenience function."""
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

        result = validate_ir(ir)
        assert isinstance(result, ValidationResult)
        assert result.checked_count > 0
