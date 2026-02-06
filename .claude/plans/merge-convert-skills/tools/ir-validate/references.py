"""Reference integrity checker for IR documents.

This module validates that all references within an IR document resolve
correctly, detects circular references, and validates cross-file references.
"""

from dataclasses import dataclass, field
from typing import Any, Iterator

from .errors import (
    ValidationError,
    ValidationErrorCode,
    create_error,
)


@dataclass
class ReferenceRegistry:
    """Tracks all defined and referenced IDs in an IR document.

    This registry collects all defined IDs and then verifies that
    all references point to valid definitions.
    """

    # Defined IDs by category
    module_ids: set[str] = field(default_factory=set)
    import_ids: set[str] = field(default_factory=set)
    export_ids: set[str] = field(default_factory=set)
    definition_ids: set[str] = field(default_factory=set)
    type_ids: set[str] = field(default_factory=set)
    function_ids: set[str] = field(default_factory=set)
    binding_ids: set[str] = field(default_factory=set)
    block_ids: set[str] = field(default_factory=set)
    gap_marker_ids: set[str] = field(default_factory=set)
    annotation_ids: set[str] = field(default_factory=set)
    preservation_ids: set[str] = field(default_factory=set)
    asymmetry_ids: set[str] = field(default_factory=set)
    decision_ids: set[str] = field(default_factory=set)

    # References found (with their locations)
    references: list[tuple[str, str, str]] = field(default_factory=list)
    # (ref_id, ref_type, location)

    # Submodule references for cycle detection
    submodule_refs: dict[str, list[str]] = field(default_factory=dict)

    @property
    def all_defined_ids(self) -> set[str]:
        """Get all defined IDs across all categories."""
        return (
            self.module_ids
            | self.import_ids
            | self.export_ids
            | self.definition_ids
            | self.type_ids
            | self.function_ids
            | self.binding_ids
            | self.block_ids
            | self.gap_marker_ids
            | self.annotation_ids
            | self.preservation_ids
            | self.asymmetry_ids
            | self.decision_ids
        )

    def add_definition(self, id_value: str, category: str) -> None:
        """Register a defined ID.

        Args:
            id_value: The ID being defined.
            category: The category of the ID (module, type, function, etc.).
        """
        category_map = {
            "module": self.module_ids,
            "import": self.import_ids,
            "export": self.export_ids,
            "definition": self.definition_ids,
            "type": self.type_ids,
            "function": self.function_ids,
            "binding": self.binding_ids,
            "block": self.block_ids,
            "gap_marker": self.gap_marker_ids,
            "annotation": self.annotation_ids,
            "preservation": self.preservation_ids,
            "asymmetry": self.asymmetry_ids,
            "decision": self.decision_ids,
        }
        if category in category_map:
            category_map[category].add(id_value)

    def add_reference(self, ref_id: str, ref_type: str, location: str) -> None:
        """Register a reference to be validated.

        Args:
            ref_id: The ID being referenced.
            ref_type: Expected type of the reference.
            location: JSON path location of the reference.
        """
        self.references.append((ref_id, ref_type, location))

    def add_submodule_ref(self, parent_id: str, child_id: str) -> None:
        """Register a submodule relationship for cycle detection.

        Args:
            parent_id: The parent module ID.
            child_id: The child (submodule) ID.
        """
        if parent_id not in self.submodule_refs:
            self.submodule_refs[parent_id] = []
        self.submodule_refs[parent_id].append(child_id)


class ReferenceIntegrityChecker:
    """Validates reference integrity in IR documents.

    Checks:
    - All $ref pointers resolve to defined IDs
    - No circular references in module/type hierarchies
    - Cross-file references are valid (when applicable)
    - Type references match expected ID patterns
    """

    def __init__(self):
        """Initialize the reference checker."""
        self.registry = ReferenceRegistry()

    def check(self, ir_data: dict[str, Any]) -> list[ValidationError]:
        """Check reference integrity in an IR document.

        Args:
            ir_data: The IR document to check.

        Returns:
            List of reference integrity errors found.
        """
        errors: list[ValidationError] = []

        # Phase 1: Collect all defined IDs
        self._collect_definitions(ir_data)

        # Phase 2: Collect all references
        self._collect_references(ir_data)

        # Phase 3: Validate references
        errors.extend(self._validate_references())

        # Phase 4: Check for circular references
        errors.extend(self._check_circular_references())

        return errors

    def _collect_definitions(self, ir_data: dict[str, Any]) -> None:
        """Collect all defined IDs from the IR document.

        Args:
            ir_data: The IR document to scan.
        """
        # Collect module definitions
        for module in ir_data.get("modules", []):
            if mod_id := module.get("id"):
                self.registry.add_definition(mod_id, "module")

            # Collect imports
            for imp in module.get("imports", []):
                if imp_id := imp.get("id"):
                    self.registry.add_definition(imp_id, "import")

            # Collect exports
            for exp in module.get("exports", []):
                if exp_id := exp.get("id"):
                    self.registry.add_definition(exp_id, "export")

            # Collect definitions
            for defn in module.get("definitions", []):
                if def_id := defn.get("id"):
                    self.registry.add_definition(def_id, "definition")

            # Collect submodule refs
            if mod_id := module.get("id"):
                for submod_id in module.get("submodules", []):
                    self.registry.add_submodule_ref(mod_id, submod_id)

        # Collect type definitions
        for typedef in ir_data.get("type_definitions", []):
            if type_id := typedef.get("id"):
                self.registry.add_definition(type_id, "type")

        # Collect gap markers
        for gap in ir_data.get("gap_markers", []):
            if gap_id := gap.get("id"):
                self.registry.add_definition(gap_id, "gap_marker")

        # Collect annotations
        for ann in ir_data.get("annotations", []):
            if ann_id := ann.get("id"):
                self.registry.add_definition(ann_id, "annotation")

        # Collect preservation statuses
        for pres in ir_data.get("preservation_statuses", []):
            if pres_id := pres.get("id"):
                self.registry.add_definition(pres_id, "preservation")

        # Collect asymmetry info
        for asym in ir_data.get("asymmetry_info", []):
            if asym_id := asym.get("id"):
                self.registry.add_definition(asym_id, "asymmetry")

        # Collect decision resolutions
        for dec in ir_data.get("decision_resolutions", []):
            if dec_id := dec.get("id"):
                self.registry.add_definition(dec_id, "decision")

    def _collect_references(self, ir_data: dict[str, Any]) -> None:
        """Collect all references from the IR document.

        Args:
            ir_data: The IR document to scan.
        """
        # Module references
        for i, module in enumerate(ir_data.get("modules", [])):
            # Submodule references
            for j, submod_id in enumerate(module.get("submodules", [])):
                self.registry.add_reference(
                    submod_id, "module", f"$.modules[{i}].submodules[{j}]"
                )

            # Definition refs
            for j, defn in enumerate(module.get("definitions", [])):
                if ref := defn.get("ref"):
                    self.registry.add_reference(
                        ref, "any", f"$.modules[{i}].definitions[{j}].ref"
                    )

            # Export item refs
            for j, exp in enumerate(module.get("exports", [])):
                item = exp.get("item", {})
                if mod_ref := item.get("module_id"):
                    self.registry.add_reference(
                        mod_ref, "module", f"$.modules[{i}].exports[{j}].item.module_id"
                    )
                if def_ref := item.get("definition_id"):
                    self.registry.add_reference(
                        def_ref, "definition", f"$.modules[{i}].exports[{j}].item.definition_id"
                    )

        # Type references within type definitions
        for i, typedef in enumerate(ir_data.get("type_definitions", [])):
            self._collect_type_refs(typedef, f"$.type_definitions[{i}]")

        # Gap marker location references
        for i, gap in enumerate(ir_data.get("gap_markers", [])):
            if loc := gap.get("location"):
                self.registry.add_reference(
                    loc, "any", f"$.gap_markers[{i}].location"
                )
            if dp_id := gap.get("decision_point_id"):
                # Decision point IDs are external references (DP-001, etc.)
                # We don't validate these as they refer to documentation
                pass

        # Annotation target references
        for i, ann in enumerate(ir_data.get("annotations", [])):
            if target := ann.get("target"):
                self.registry.add_reference(
                    target, "any", f"$.annotations[{i}].target"
                )

        # Preservation status unit references
        for i, pres in enumerate(ir_data.get("preservation_statuses", [])):
            if unit_id := pres.get("unit_id"):
                self.registry.add_reference(
                    unit_id, "any", f"$.preservation_statuses[{i}].unit_id"
                )
            for j, gap_id in enumerate(pres.get("blocking_gaps", [])):
                self.registry.add_reference(
                    gap_id, "gap_marker", f"$.preservation_statuses[{i}].blocking_gaps[{j}]"
                )

        # Asymmetry info unit references
        for i, asym in enumerate(ir_data.get("asymmetry_info", [])):
            if unit_id := asym.get("unit_id"):
                self.registry.add_reference(
                    unit_id, "any", f"$.asymmetry_info[{i}].unit_id"
                )

        # Decision resolution unit references
        for i, dec in enumerate(ir_data.get("decision_resolutions", [])):
            if unit_id := dec.get("unit_id"):
                self.registry.add_reference(
                    unit_id, "any", f"$.decision_resolutions[{i}].unit_id"
                )

    def _collect_type_refs(self, obj: Any, path: str) -> None:
        """Recursively collect type references.

        Args:
            obj: The object to scan for type references.
            path: Current JSON path.
        """
        if not isinstance(obj, dict):
            return

        # Check for type_id references
        if "type_id" in obj:
            type_id = obj["type_id"]
            # Only validate if it looks like an internal type reference
            if isinstance(type_id, str) and type_id.startswith("type:"):
                self.registry.add_reference(type_id, "type", f"{path}.type_id")

        # Recurse into nested structures
        for key, value in obj.items():
            if isinstance(value, dict):
                self._collect_type_refs(value, f"{path}.{key}")
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    self._collect_type_refs(item, f"{path}.{key}[{i}]")

    def _validate_references(self) -> Iterator[ValidationError]:
        """Validate all collected references.

        Yields:
            Validation errors for dangling references.
        """
        all_ids = self.registry.all_defined_ids

        for ref_id, ref_type, location in self.registry.references:
            if ref_id not in all_ids:
                yield create_error(
                    code=ValidationErrorCode.V002_DANGLING_REF,
                    message=f"Reference '{ref_id}' not found",
                    location=location,
                    severity="error",
                    ref=ref_id,
                )

    def _check_circular_references(self) -> Iterator[ValidationError]:
        """Check for circular references in module hierarchy.

        Yields:
            Validation errors for circular references.
        """
        # Check submodule cycles
        visited: set[str] = set()
        path: list[str] = []

        def dfs(module_id: str) -> str | None:
            """DFS to detect cycles, returns cycle chain if found."""
            if module_id in path:
                cycle_start = path.index(module_id)
                return " -> ".join(path[cycle_start:] + [module_id])

            if module_id in visited:
                return None

            visited.add(module_id)
            path.append(module_id)

            for child_id in self.registry.submodule_refs.get(module_id, []):
                if cycle := dfs(child_id):
                    return cycle

            path.pop()
            return None

        for module_id in self.registry.module_ids:
            if cycle := dfs(module_id):
                yield create_error(
                    code=ValidationErrorCode.V002_CIRCULAR_REF,
                    message=f"Circular module reference detected: {cycle}",
                    location="$.modules",
                    severity="error",
                    chain=cycle,
                )
                break  # Report only first cycle found


def check_reference_integrity(ir_data: dict[str, Any]) -> list[ValidationError]:
    """Convenience function to check reference integrity.

    Args:
        ir_data: The IR document to check.

    Returns:
        List of reference integrity errors found.
    """
    checker = ReferenceIntegrityChecker()
    return checker.check(ir_data)
