"""Tests for reference integrity checking."""

import pytest
from typing import Any

from ir_validate.references import (
    ReferenceIntegrityChecker,
    ReferenceRegistry,
    check_reference_integrity,
)
from ir_validate.errors import ValidationErrorCode


class TestReferenceRegistry:
    """Tests for ReferenceRegistry."""

    def test_add_definition(self) -> None:
        """Test adding definitions to registry."""
        registry = ReferenceRegistry()
        registry.add_definition("mod_main", "module")
        registry.add_definition("type:User", "type")

        assert "mod_main" in registry.module_ids
        assert "type:User" in registry.type_ids

    def test_all_defined_ids(self) -> None:
        """Test all_defined_ids property."""
        registry = ReferenceRegistry()
        registry.add_definition("mod_main", "module")
        registry.add_definition("type:User", "type")
        registry.add_definition("def_func", "definition")

        all_ids = registry.all_defined_ids
        assert "mod_main" in all_ids
        assert "type:User" in all_ids
        assert "def_func" in all_ids

    def test_add_reference(self) -> None:
        """Test adding references to registry."""
        registry = ReferenceRegistry()
        registry.add_reference("mod_other", "module", "$.modules[0].submodules[0]")

        assert len(registry.references) == 1
        ref_id, ref_type, location = registry.references[0]
        assert ref_id == "mod_other"
        assert ref_type == "module"
        assert location == "$.modules[0].submodules[0]"

    def test_add_submodule_ref(self) -> None:
        """Test adding submodule relationships."""
        registry = ReferenceRegistry()
        registry.add_submodule_ref("mod_parent", "mod_child1")
        registry.add_submodule_ref("mod_parent", "mod_child2")

        assert "mod_parent" in registry.submodule_refs
        assert "mod_child1" in registry.submodule_refs["mod_parent"]
        assert "mod_child2" in registry.submodule_refs["mod_parent"]


class TestReferenceIntegrityChecker:
    """Tests for ReferenceIntegrityChecker."""

    def test_valid_references(self) -> None:
        """Test document with all valid references."""
        ir_data = {
            "version": "ir-v1.0",
            "metadata": {"created_at": "2026-02-05T10:00:00Z"},
            "modules": [
                {
                    "id": "mod_main",
                    "name": "main",
                    "path": ["main"],
                    "visibility": "public",
                    "submodules": ["mod_sub"],
                },
                {
                    "id": "mod_sub",
                    "name": "sub",
                    "path": ["main", "sub"],
                    "visibility": "public",
                },
            ],
        }

        errors = check_reference_integrity(ir_data)
        dangling_errors = [
            e for e in errors
            if ValidationErrorCode.V002_DANGLING_REF.value in e.code
        ]
        assert len(dangling_errors) == 0

    def test_dangling_submodule_ref(self) -> None:
        """Test detection of dangling submodule reference."""
        ir_data = {
            "version": "ir-v1.0",
            "metadata": {"created_at": "2026-02-05T10:00:00Z"},
            "modules": [
                {
                    "id": "mod_main",
                    "name": "main",
                    "path": ["main"],
                    "visibility": "public",
                    "submodules": ["mod_nonexistent"],
                },
            ],
        }

        errors = check_reference_integrity(ir_data)
        dangling_errors = [
            e for e in errors
            if ValidationErrorCode.V002_DANGLING_REF.value in e.code
        ]
        assert len(dangling_errors) >= 1

    def test_dangling_gap_location(self) -> None:
        """Test detection of dangling gap marker location."""
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
                    "location": "nonexistent_node",
                    "gap_type": "structural",
                    "severity": "medium",
                    "description": "Test",
                    "source_concept": "test",
                    "preservation_level": 2,
                },
            ],
        }

        errors = check_reference_integrity(ir_data)
        dangling_errors = [
            e for e in errors
            if ValidationErrorCode.V002_DANGLING_REF.value in e.code
        ]
        assert len(dangling_errors) >= 1

    def test_circular_module_reference(self) -> None:
        """Test detection of circular module references."""
        ir_data = {
            "version": "ir-v1.0",
            "metadata": {"created_at": "2026-02-05T10:00:00Z"},
            "modules": [
                {
                    "id": "mod_a",
                    "name": "a",
                    "path": ["a"],
                    "visibility": "public",
                    "submodules": ["mod_b"],
                },
                {
                    "id": "mod_b",
                    "name": "b",
                    "path": ["b"],
                    "visibility": "public",
                    "submodules": ["mod_a"],  # Circular!
                },
            ],
        }

        errors = check_reference_integrity(ir_data)
        circular_errors = [
            e for e in errors
            if ValidationErrorCode.V002_CIRCULAR_REF.value in e.code
        ]
        assert len(circular_errors) >= 1

    def test_deep_circular_reference(self) -> None:
        """Test detection of deep circular references (A -> B -> C -> A)."""
        ir_data = {
            "version": "ir-v1.0",
            "metadata": {"created_at": "2026-02-05T10:00:00Z"},
            "modules": [
                {
                    "id": "mod_a",
                    "name": "a",
                    "path": ["a"],
                    "visibility": "public",
                    "submodules": ["mod_b"],
                },
                {
                    "id": "mod_b",
                    "name": "b",
                    "path": ["b"],
                    "visibility": "public",
                    "submodules": ["mod_c"],
                },
                {
                    "id": "mod_c",
                    "name": "c",
                    "path": ["c"],
                    "visibility": "public",
                    "submodules": ["mod_a"],  # Back to A
                },
            ],
        }

        errors = check_reference_integrity(ir_data)
        circular_errors = [
            e for e in errors
            if ValidationErrorCode.V002_CIRCULAR_REF.value in e.code
        ]
        assert len(circular_errors) >= 1

    def test_valid_blocking_gaps_reference(self) -> None:
        """Test valid blocking_gaps references in preservation status."""
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

        errors = check_reference_integrity(ir_data)
        dangling_errors = [
            e for e in errors
            if ValidationErrorCode.V002_DANGLING_REF.value in e.code
        ]
        assert len(dangling_errors) == 0

    def test_annotation_target_reference(self) -> None:
        """Test annotation target references are checked."""
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
            "annotations": [
                {
                    "id": "ann_001",
                    "target": "nonexistent_target",
                    "kind": "inferred_type",
                    "value": {},
                    "source": "inferred",
                },
            ],
        }

        errors = check_reference_integrity(ir_data)
        dangling_errors = [
            e for e in errors
            if ValidationErrorCode.V002_DANGLING_REF.value in e.code
        ]
        assert len(dangling_errors) >= 1
