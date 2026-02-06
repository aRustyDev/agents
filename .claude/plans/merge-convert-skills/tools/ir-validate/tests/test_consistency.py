"""Tests for cross-layer consistency checking."""

import pytest
from typing import Any

from ir_validate.consistency import (
    ConsistencyChecker,
    check_consistency,
)
from ir_validate.errors import ValidationErrorCode


class TestConsistencyChecker:
    """Tests for ConsistencyChecker."""

    def test_valid_module_consistency(self) -> None:
        """Test validation of consistent module structure."""
        ir_data = {
            "version": "ir-v1.0",
            "metadata": {"created_at": "2026-02-05T10:00:00Z"},
            "modules": [
                {
                    "id": "mod_main",
                    "name": "main",
                    "path": ["main"],
                    "visibility": "public",
                    "definitions": [
                        {
                            "id": "def_func",
                            "kind": "function",
                            "visibility": "public",
                        }
                    ],
                },
            ],
        }

        errors = check_consistency(ir_data)
        consistency_errors = [
            e for e in errors
            if e.code.startswith("V003")
        ]
        assert len(consistency_errors) == 0

    def test_invalid_visibility(self) -> None:
        """Test detection of invalid visibility values."""
        ir_data = {
            "version": "ir-v1.0",
            "metadata": {"created_at": "2026-02-05T10:00:00Z"},
            "modules": [
                {
                    "id": "mod_main",
                    "name": "main",
                    "path": ["main"],
                    "visibility": "invalid_visibility",
                },
            ],
        }

        errors = check_consistency(ir_data)
        visibility_errors = [
            e for e in errors
            if ValidationErrorCode.V003_VISIBILITY_INCONSISTENT.value in e.code
        ]
        assert len(visibility_errors) >= 1

    def test_private_exported_as_public(self) -> None:
        """Test detection of private definitions exported as public."""
        ir_data = {
            "version": "ir-v1.0",
            "metadata": {"created_at": "2026-02-05T10:00:00Z"},
            "modules": [
                {
                    "id": "mod_main",
                    "name": "main",
                    "path": ["main"],
                    "visibility": "public",
                    "definitions": [
                        {
                            "id": "def_private",
                            "kind": "function",
                            "visibility": "private",
                        }
                    ],
                    "exports": [
                        {
                            "id": "exp_1",
                            "item": {
                                "module_id": "mod_main",
                                "definition_id": "def_private",
                            },
                            "visibility": "public",
                        }
                    ],
                },
            ],
        }

        errors = check_consistency(ir_data)
        visibility_errors = [
            e for e in errors
            if ValidationErrorCode.V003_VISIBILITY_INCONSISTENT.value in e.code
        ]
        assert len(visibility_errors) >= 1

    def test_valid_type_definition(self) -> None:
        """Test validation of consistent type definition."""
        ir_data = {
            "version": "ir-v1.0",
            "metadata": {"created_at": "2026-02-05T10:00:00Z"},
            "modules": [],
            "type_definitions": [
                {
                    "id": "type:User",
                    "name": "User",
                    "kind": "struct",
                    "params": [],
                    "visibility": "public",
                    "body": {
                        "fields": [
                            {"name": "id", "type": {"kind": "named", "type_id": "int"}},
                        ],
                    },
                },
            ],
        }

        errors = check_consistency(ir_data)
        type_errors = [
            e for e in errors
            if e.code.startswith("V003")
        ]
        assert len(type_errors) == 0

    def test_invalid_type_kind(self) -> None:
        """Test detection of invalid type kind."""
        ir_data = {
            "version": "ir-v1.0",
            "metadata": {"created_at": "2026-02-05T10:00:00Z"},
            "modules": [],
            "type_definitions": [
                {
                    "id": "type:Bad",
                    "name": "Bad",
                    "kind": "invalid_kind",
                    "params": [],
                    "visibility": "public",
                },
            ],
        }

        errors = check_consistency(ir_data)
        layer_errors = [
            e for e in errors
            if ValidationErrorCode.V003_LAYER_MISMATCH.value in e.code
        ]
        assert len(layer_errors) >= 1

    def test_enum_without_variants(self) -> None:
        """Test warning for enum without variants."""
        ir_data = {
            "version": "ir-v1.0",
            "metadata": {"created_at": "2026-02-05T10:00:00Z"},
            "modules": [],
            "type_definitions": [
                {
                    "id": "type:EmptyEnum",
                    "name": "EmptyEnum",
                    "kind": "enum",
                    "params": [],
                    "visibility": "public",
                    "body": {},
                },
            ],
        }

        errors = check_consistency(ir_data)
        # Should have a warning about empty enum
        enum_warnings = [
            e for e in errors
            if "variants" in e.message.lower() or "enum" in e.message.lower()
        ]
        assert len(enum_warnings) >= 1

    def test_alias_without_aliased_type(self) -> None:
        """Test error for type alias without aliased_type."""
        ir_data = {
            "version": "ir-v1.0",
            "metadata": {"created_at": "2026-02-05T10:00:00Z"},
            "modules": [],
            "type_definitions": [
                {
                    "id": "type:BadAlias",
                    "name": "BadAlias",
                    "kind": "alias",
                    "params": [],
                    "visibility": "public",
                    "body": {},
                },
            ],
        }

        errors = check_consistency(ir_data)
        alias_errors = [
            e for e in errors
            if "alias" in e.message.lower()
        ]
        assert len(alias_errors) >= 1

    def test_constraint_references_unknown_param(self) -> None:
        """Test error for constraint referencing unknown type parameter."""
        ir_data = {
            "version": "ir-v1.0",
            "metadata": {"created_at": "2026-02-05T10:00:00Z"},
            "modules": [],
            "type_definitions": [
                {
                    "id": "type:Generic",
                    "name": "Generic",
                    "kind": "struct",
                    "params": [{"name": "T"}],
                    "constraints": [
                        {"kind": "type_bound", "param": "U", "bound": {"kind": "named", "type_id": "Eq"}},
                    ],
                    "visibility": "public",
                },
            ],
        }

        errors = check_consistency(ir_data)
        missing_errors = [
            e for e in errors
            if ValidationErrorCode.V003_TYPE_DEFINITION_MISSING.value in e.code
        ]
        assert len(missing_errors) >= 1


class TestGapMarkerConsistency:
    """Tests for gap marker consistency checking."""

    def test_valid_gap_marker(self) -> None:
        """Test validation of valid gap marker."""
        ir_data = {
            "version": "ir-v1.0",
            "metadata": {"created_at": "2026-02-05T10:00:00Z"},
            "modules": [
                {
                    "id": "mod_main",
                    "name": "main",
                    "path": ["main"],
                    "visibility": "public",
                },
            ],
            "gap_markers": [
                {
                    "id": "gap_001",
                    "location": "mod_main",
                    "gap_type": "structural",
                    "severity": "medium",
                    "description": "Test gap",
                    "source_concept": "dynamic typing",
                    "preservation_level": 2,
                    "affected_layers": [3, 4],
                },
            ],
        }

        errors = check_consistency(ir_data)
        gap_errors = [
            e for e in errors
            if e.code.startswith("V004") or "gap" in e.message.lower()
        ]
        # Should have no errors for valid gap marker
        assert len([e for e in gap_errors if e.severity == "error"]) == 0

    def test_invalid_layer_number(self) -> None:
        """Test detection of invalid layer number in affected_layers."""
        ir_data = {
            "version": "ir-v1.0",
            "metadata": {"created_at": "2026-02-05T10:00:00Z"},
            "modules": [],
            "gap_markers": [
                {
                    "id": "gap_001",
                    "location": "some_node",
                    "gap_type": "structural",
                    "severity": "medium",
                    "description": "Test",
                    "source_concept": "test",
                    "preservation_level": 2,
                    "affected_layers": [5],  # Invalid: max is 4
                },
            ],
        }

        errors = check_consistency(ir_data)
        layer_errors = [
            e for e in errors
            if ValidationErrorCode.V003_LAYER_MISMATCH.value in e.code
        ]
        assert len(layer_errors) >= 1


class TestPreservationConsistency:
    """Tests for preservation status consistency checking."""

    def test_valid_preservation_status(self) -> None:
        """Test validation of valid preservation status."""
        ir_data = {
            "version": "ir-v1.0",
            "metadata": {"created_at": "2026-02-05T10:00:00Z"},
            "modules": [
                {
                    "id": "mod_main",
                    "name": "main",
                    "path": ["main"],
                    "visibility": "public",
                },
            ],
            "gap_markers": [
                {
                    "id": "gap_001",
                    "location": "mod_main",
                    "gap_type": "structural",
                    "severity": "medium",
                    "description": "Test",
                    "source_concept": "test",
                    "preservation_level": 2,
                },
            ],
            "preservation_statuses": [
                {
                    "id": "pres_001",
                    "unit_id": "mod_main",
                    "current_level": 1,
                    "max_achievable_level": 2,
                    "blocking_gaps": ["gap_001"],
                },
            ],
        }

        errors = check_consistency(ir_data)
        pres_errors = [
            e for e in errors
            if e.code.startswith("V004")
        ]
        assert len([e for e in pres_errors if e.severity == "error"]) == 0

    def test_invalid_preservation_level_value(self) -> None:
        """Test detection of invalid preservation level value."""
        ir_data = {
            "version": "ir-v1.0",
            "metadata": {"created_at": "2026-02-05T10:00:00Z"},
            "modules": [],
            "preservation_statuses": [
                {
                    "id": "pres_001",
                    "unit_id": "some_unit",
                    "current_level": 5,  # Invalid: max is 3
                    "max_achievable_level": 2,
                },
            ],
        }

        errors = check_consistency(ir_data)
        level_errors = [
            e for e in errors
            if ValidationErrorCode.V004_INVALID_PRESERVATION_LEVEL.value in e.code
        ]
        assert len(level_errors) >= 1

    def test_current_exceeds_max(self) -> None:
        """Test detection of current_level exceeding max_achievable_level."""
        ir_data = {
            "version": "ir-v1.0",
            "metadata": {"created_at": "2026-02-05T10:00:00Z"},
            "modules": [],
            "preservation_statuses": [
                {
                    "id": "pres_001",
                    "unit_id": "some_unit",
                    "current_level": 3,
                    "max_achievable_level": 1,  # Current > max
                },
            ],
        }

        errors = check_consistency(ir_data)
        consistency_errors = [
            e for e in errors
            if "exceeds" in e.message.lower()
        ]
        assert len(consistency_errors) >= 1

    def test_blocking_gap_not_found(self) -> None:
        """Test detection of blocking_gaps referencing nonexistent gaps."""
        ir_data = {
            "version": "ir-v1.0",
            "metadata": {"created_at": "2026-02-05T10:00:00Z"},
            "modules": [],
            "gap_markers": [],
            "preservation_statuses": [
                {
                    "id": "pres_001",
                    "unit_id": "some_unit",
                    "current_level": 1,
                    "max_achievable_level": 2,
                    "blocking_gaps": ["gap_nonexistent"],
                },
            ],
        }

        errors = check_consistency(ir_data)
        ref_errors = [
            e for e in errors
            if ValidationErrorCode.V002_DANGLING_REF.value in e.code
        ]
        assert len(ref_errors) >= 1
