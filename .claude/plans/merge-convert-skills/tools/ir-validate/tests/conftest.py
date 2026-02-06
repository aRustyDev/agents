"""Pytest fixtures for ir-validate tests."""

import pytest
from typing import Any


@pytest.fixture
def minimal_valid_ir() -> dict[str, Any]:
    """A minimal valid IR document."""
    return {
        "version": "ir-v1.0",
        "metadata": {
            "created_at": "2026-02-05T10:00:00Z",
        },
        "modules": [
            {
                "id": "mod_main",
                "name": "main",
                "path": ["main"],
                "visibility": "public",
            }
        ],
    }


@pytest.fixture
def complex_valid_ir() -> dict[str, Any]:
    """A more complex valid IR document with types and annotations."""
    return {
        "version": "ir-v1.0",
        "metadata": {
            "created_at": "2026-02-05T10:00:00Z",
            "source_language": "python",
            "extraction_tool": "ir-extract",
            "extraction_tool_version": "1.0.0",
        },
        "modules": [
            {
                "id": "mod_utils",
                "name": "utils",
                "path": ["project", "utils"],
                "visibility": "public",
                "imports": [
                    {
                        "id": "imp_typing",
                        "module_path": ["typing"],
                        "imported_items": [
                            {"name": "List", "kind": "type"},
                            {"name": "Optional", "kind": "type"},
                        ],
                    }
                ],
                "exports": [
                    {
                        "id": "exp_process",
                        "item": {
                            "module_id": "mod_utils",
                            "definition_id": "def_process",
                        },
                        "visibility": "public",
                    }
                ],
                "definitions": [
                    {
                        "id": "def_process",
                        "kind": "function",
                        "ref": "fn:process",
                        "visibility": "public",
                    },
                    {
                        "id": "def_helper",
                        "kind": "function",
                        "ref": "fn:helper",
                        "visibility": "private",
                    },
                ],
            }
        ],
        "type_definitions": [
            {
                "id": "type:User",
                "name": "User",
                "kind": "struct",
                "params": [],
                "visibility": "public",
                "body": {
                    "fields": [
                        {
                            "name": "id",
                            "type": {"kind": "named", "type_id": "int"},
                            "visibility": "public",
                        },
                        {
                            "name": "name",
                            "type": {"kind": "named", "type_id": "str"},
                            "visibility": "public",
                        },
                    ],
                },
            },
            {
                "id": "type:Status",
                "name": "Status",
                "kind": "enum",
                "params": [],
                "visibility": "public",
                "body": {
                    "variants": [
                        {"name": "Active", "kind": "unit"},
                        {"name": "Inactive", "kind": "unit"},
                        {"name": "Pending", "kind": "unit"},
                    ],
                },
            },
        ],
        "gap_markers": [
            {
                "id": "gap_001",
                "location": "def_process",
                "gap_type": "structural",
                "severity": "medium",
                "description": "Dynamic typing requires inference",
                "source_concept": "dynamic typing",
                "preservation_level": 2,
                "affected_layers": [1, 3],
            }
        ],
        "annotations": [
            {
                "id": "ann_001",
                "target": "def_process",
                "kind": "inferred_type",
                "value": {
                    "original": "dynamic",
                    "inferred": "List[User]",
                    "confidence": 0.85,
                },
                "source": "inferred",
            }
        ],
        "preservation_statuses": [
            {
                "id": "pres_001",
                "unit_id": "mod_utils",
                "current_level": 1,
                "max_achievable_level": 2,
                "blocking_gaps": ["gap_001"],
            }
        ],
    }


@pytest.fixture
def ir_with_missing_required() -> dict[str, Any]:
    """IR document missing required fields."""
    return {
        "version": "ir-v1.0",
        # Missing metadata
        "modules": [],
    }


@pytest.fixture
def ir_with_invalid_types() -> dict[str, Any]:
    """IR document with type errors."""
    return {
        "version": "ir-v1.0",
        "metadata": {
            "created_at": "2026-02-05T10:00:00Z",
        },
        "modules": "not an array",  # Should be array
    }


@pytest.fixture
def ir_with_dangling_refs() -> dict[str, Any]:
    """IR document with dangling references."""
    return {
        "version": "ir-v1.0",
        "metadata": {
            "created_at": "2026-02-05T10:00:00Z",
        },
        "modules": [
            {
                "id": "mod_main",
                "name": "main",
                "path": ["main"],
                "visibility": "public",
                "submodules": ["mod_nonexistent"],  # Dangling ref
            }
        ],
        "gap_markers": [
            {
                "id": "gap_001",
                "location": "nonexistent_node",  # Dangling ref
                "gap_type": "structural",
                "severity": "medium",
                "description": "Test gap",
                "source_concept": "test",
                "preservation_level": 2,
            }
        ],
    }


@pytest.fixture
def ir_with_circular_refs() -> dict[str, Any]:
    """IR document with circular module references."""
    return {
        "version": "ir-v1.0",
        "metadata": {
            "created_at": "2026-02-05T10:00:00Z",
        },
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
                "submodules": ["mod_a"],  # Creates cycle
            },
        ],
    }


@pytest.fixture
def ir_with_invalid_preservation() -> dict[str, Any]:
    """IR document with invalid preservation levels."""
    return {
        "version": "ir-v1.0",
        "metadata": {
            "created_at": "2026-02-05T10:00:00Z",
        },
        "modules": [
            {
                "id": "mod_main",
                "name": "main",
                "path": ["main"],
                "visibility": "public",
            }
        ],
        "preservation_statuses": [
            {
                "id": "pres_001",
                "unit_id": "mod_main",
                "current_level": 5,  # Invalid: max is 3
                "max_achievable_level": 2,
            }
        ],
    }


@pytest.fixture
def ir_with_inconsistent_visibility() -> dict[str, Any]:
    """IR document with visibility inconsistencies."""
    return {
        "version": "ir-v1.0",
        "metadata": {
            "created_at": "2026-02-05T10:00:00Z",
        },
        "modules": [
            {
                "id": "mod_main",
                "name": "main",
                "path": ["main"],
                "visibility": "public",
                "definitions": [
                    {
                        "id": "def_private_func",
                        "kind": "function",
                        "visibility": "private",
                    }
                ],
                "exports": [
                    {
                        "id": "exp_private",
                        "item": {
                            "module_id": "mod_main",
                            "definition_id": "def_private_func",
                        },
                        "visibility": "public",  # Exporting private as public
                    }
                ],
            }
        ],
    }
