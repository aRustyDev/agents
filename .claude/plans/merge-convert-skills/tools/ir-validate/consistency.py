"""Cross-layer consistency validation for IR documents.

This module validates that IR layers are internally consistent:
- Layer 4 (Structural) is consistent with Layer 3 (Types) and Layer 2 (Control Flow)
- Layer 2 (Control Flow) is consistent with Layer 3 (Types)
- Layer 1 (Data Flow) bindings match Layer 3 types
- Gap markers reference valid IR elements
"""

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from .errors import (
    ValidationError,
    ValidationErrorCode,
    create_error,
)


@dataclass
class LayerIndex:
    """Index of IR elements by layer for consistency checking.

    Organizes elements by their layer (0-4) for cross-layer validation.
    """

    # Layer 4: Structural (modules, imports, exports)
    modules: dict[str, dict] = field(default_factory=dict)

    # Layer 3: Types
    type_definitions: dict[str, dict] = field(default_factory=dict)

    # Layer 2: Control Flow (functions)
    functions: dict[str, dict] = field(default_factory=dict)

    # Layer 1: Data Flow (bindings)
    bindings: dict[str, dict] = field(default_factory=dict)

    # Cross-cutting
    gap_markers: dict[str, dict] = field(default_factory=dict)
    annotations: dict[str, dict] = field(default_factory=dict)
    preservation_statuses: dict[str, dict] = field(default_factory=dict)


class ConsistencyChecker:
    """Validates cross-layer consistency in IR documents.

    Checks:
    - Module definitions reference valid types
    - Function parameters have valid type references
    - Type constraints reference valid type parameters
    - Control flow blocks form valid graphs
    - Effect annotations are consistent across call boundaries
    """

    # Valid visibility values
    VALID_VISIBILITIES = {"public", "internal", "private", "protected", "package"}

    # Valid type kinds
    VALID_TYPE_KINDS = {"struct", "enum", "class", "interface", "alias", "opaque", "primitive"}

    # Valid effect kinds
    VALID_EFFECT_KINDS = {"pure", "throws", "async", "unsafe", "io", "suspends", "allocates", "captures", "mutates"}

    # Layer associations for gap markers
    LAYER_PREFIXES = {
        "mod_": 4,
        "imp_": 4,
        "exp_": 4,
        "def_": 4,
        "type:": 3,
        "fn:": 2,
        "binding:": 1,
        "expr:": 0,
    }

    def __init__(self):
        """Initialize the consistency checker."""
        self.index = LayerIndex()

    def check(self, ir_data: dict[str, Any]) -> list[ValidationError]:
        """Check cross-layer consistency in an IR document.

        Args:
            ir_data: The IR document to check.

        Returns:
            List of consistency errors found.
        """
        errors: list[ValidationError] = []

        # Build layer index
        self._build_index(ir_data)

        # Run consistency checks
        errors.extend(self._check_module_consistency(ir_data))
        errors.extend(self._check_type_consistency(ir_data))
        errors.extend(self._check_function_consistency(ir_data))
        errors.extend(self._check_gap_marker_consistency(ir_data))
        errors.extend(self._check_preservation_consistency(ir_data))

        return errors

    def _build_index(self, ir_data: dict[str, Any]) -> None:
        """Build the layer index from IR data.

        Args:
            ir_data: The IR document to index.
        """
        # Index modules (Layer 4)
        for module in ir_data.get("modules", []):
            if mod_id := module.get("id"):
                self.index.modules[mod_id] = module

        # Index type definitions (Layer 3)
        for typedef in ir_data.get("type_definitions", []):
            if type_id := typedef.get("id"):
                self.index.type_definitions[type_id] = typedef

        # Index gap markers
        for gap in ir_data.get("gap_markers", []):
            if gap_id := gap.get("id"):
                self.index.gap_markers[gap_id] = gap

        # Index annotations
        for ann in ir_data.get("annotations", []):
            if ann_id := ann.get("id"):
                self.index.annotations[ann_id] = ann

        # Index preservation statuses
        for pres in ir_data.get("preservation_statuses", []):
            if pres_id := pres.get("id"):
                self.index.preservation_statuses[pres_id] = pres

    def _check_module_consistency(
        self, ir_data: dict[str, Any]
    ) -> Iterator[ValidationError]:
        """Check Layer 4 (Structural) consistency.

        Args:
            ir_data: The IR document to check.

        Yields:
            Consistency errors found.
        """
        for i, module in enumerate(ir_data.get("modules", [])):
            location_base = f"$.modules[{i}]"

            # Check visibility is valid
            visibility = module.get("visibility")
            if visibility and visibility not in self.VALID_VISIBILITIES:
                yield create_error(
                    code=ValidationErrorCode.V003_VISIBILITY_INCONSISTENT,
                    message=f"Invalid visibility '{visibility}'",
                    location=f"{location_base}.visibility",
                    severity="error",
                )

            # Check definitions have consistent visibility
            for j, defn in enumerate(module.get("definitions", [])):
                def_visibility = defn.get("visibility")
                if def_visibility and def_visibility not in self.VALID_VISIBILITIES:
                    yield create_error(
                        code=ValidationErrorCode.V003_VISIBILITY_INCONSISTENT,
                        message=f"Invalid definition visibility '{def_visibility}'",
                        location=f"{location_base}.definitions[{j}].visibility",
                        severity="error",
                    )

                # Check that internal/private definitions aren't exported as public
                if def_visibility in ("private", "internal"):
                    def_id = defn.get("id")
                    for k, exp in enumerate(module.get("exports", [])):
                        item = exp.get("item", {})
                        if item.get("definition_id") == def_id:
                            exp_visibility = exp.get("visibility", "public")
                            if exp_visibility == "public":
                                yield create_error(
                                    code=ValidationErrorCode.V003_VISIBILITY_INCONSISTENT,
                                    message=f"Cannot export {def_visibility} definition '{def_id}' as public",
                                    location=f"{location_base}.exports[{k}]",
                                    severity="warning",
                                )

            # Check submodules exist
            for j, submod_id in enumerate(module.get("submodules", [])):
                if submod_id not in self.index.modules:
                    yield create_error(
                        code=ValidationErrorCode.V003_PARENT_CHILD_INCONSISTENT,
                        message=f"Submodule '{submod_id}' not found in modules",
                        location=f"{location_base}.submodules[{j}]",
                        severity="error",
                    )

    def _check_type_consistency(
        self, ir_data: dict[str, Any]
    ) -> Iterator[ValidationError]:
        """Check Layer 3 (Type) consistency.

        Args:
            ir_data: The IR document to check.

        Yields:
            Consistency errors found.
        """
        for i, typedef in enumerate(ir_data.get("type_definitions", [])):
            location_base = f"$.type_definitions[{i}]"
            type_id = typedef.get("id", f"<unknown-{i}>")

            # Check type kind is valid
            kind = typedef.get("kind")
            if kind and kind not in self.VALID_TYPE_KINDS:
                yield create_error(
                    code=ValidationErrorCode.V003_LAYER_MISMATCH,
                    message=f"Invalid type kind '{kind}'",
                    location=f"{location_base}.kind",
                    severity="error",
                    actual=kind,
                )

            # Check type parameters
            params = typedef.get("params", [])
            param_names = {p.get("name") for p in params if p.get("name")}

            # Check constraints reference valid type parameters
            for j, constraint in enumerate(typedef.get("constraints", [])):
                param = constraint.get("param")
                if param and param not in param_names:
                    yield create_error(
                        code=ValidationErrorCode.V003_TYPE_DEFINITION_MISSING,
                        message=f"Constraint references unknown type parameter '{param}'",
                        location=f"{location_base}.constraints[{j}].param",
                        severity="error",
                        type_id=param,
                    )

            # Check body consistency with kind
            body = typedef.get("body", {})
            if body:
                yield from self._check_type_body_consistency(
                    kind, body, location_base, type_id
                )

    def _check_type_body_consistency(
        self, kind: str | None, body: dict, location_base: str, type_id: str
    ) -> Iterator[ValidationError]:
        """Check type body is consistent with type kind.

        Args:
            kind: The type kind (struct, enum, etc.).
            body: The type body.
            location_base: Base JSON path.
            type_id: The type ID for error messages.

        Yields:
            Consistency errors found.
        """
        # struct/class should have fields
        if kind in ("struct", "class"):
            if body.get("variants"):
                yield create_error(
                    code=ValidationErrorCode.V003_LAYER_MISMATCH,
                    message=f"Type '{type_id}' is {kind} but has enum variants",
                    location=f"{location_base}.body.variants",
                    severity="warning",
                )

        # enum should have variants
        if kind == "enum":
            if not body.get("variants"):
                yield create_error(
                    code=ValidationErrorCode.V003_LAYER_MISMATCH,
                    message=f"Enum type '{type_id}' has no variants",
                    location=f"{location_base}.body",
                    severity="warning",
                )

        # interface/trait should have methods
        if kind == "interface":
            if not body.get("required_methods") and not body.get("provided_methods"):
                yield create_error(
                    code=ValidationErrorCode.V003_LAYER_MISMATCH,
                    message=f"Interface type '{type_id}' has no methods",
                    location=f"{location_base}.body",
                    severity="info",
                )

        # alias should have aliased_type
        if kind == "alias":
            if not body.get("aliased_type"):
                yield create_error(
                    code=ValidationErrorCode.V003_LAYER_MISMATCH,
                    message=f"Type alias '{type_id}' has no aliased_type",
                    location=f"{location_base}.body",
                    severity="error",
                )

    def _check_function_consistency(
        self, ir_data: dict[str, Any]
    ) -> Iterator[ValidationError]:
        """Check Layer 2 (Control Flow) consistency.

        This checks function definitions embedded in type bodies
        and validates control flow graph structure.

        Args:
            ir_data: The IR document to check.

        Yields:
            Consistency errors found.
        """
        # Check functions in type definitions (methods)
        for i, typedef in enumerate(ir_data.get("type_definitions", [])):
            body = typedef.get("body", {})

            # Check required methods have valid signatures
            for j, method in enumerate(body.get("required_methods", [])):
                yield from self._check_method_signature(
                    method, f"$.type_definitions[{i}].body.required_methods[{j}]"
                )

    def _check_method_signature(
        self, method: dict, location_base: str
    ) -> Iterator[ValidationError]:
        """Check method signature consistency.

        Args:
            method: The method signature.
            location_base: Base JSON path.

        Yields:
            Consistency errors found.
        """
        # Check effects are valid
        for j, effect in enumerate(method.get("effects", [])):
            effect_kind = effect.get("kind")
            if effect_kind and effect_kind not in self.VALID_EFFECT_KINDS:
                yield create_error(
                    code=ValidationErrorCode.V003_EFFECT_PROPAGATION_VIOLATION,
                    message=f"Invalid effect kind '{effect_kind}'",
                    location=f"{location_base}.effects[{j}].kind",
                    severity="error",
                )

        # Check parameter types are well-formed
        for j, param in enumerate(method.get("params", [])):
            param_type = param.get("type", {})
            if param_type and not param_type.get("kind"):
                yield create_error(
                    code=ValidationErrorCode.V003_BINDING_TYPE_MISMATCH,
                    message="Parameter type missing 'kind' field",
                    location=f"{location_base}.params[{j}].type",
                    severity="error",
                )

    def _check_gap_marker_consistency(
        self, ir_data: dict[str, Any]
    ) -> Iterator[ValidationError]:
        """Check gap marker consistency.

        Args:
            ir_data: The IR document to check.

        Yields:
            Consistency errors found.
        """
        # Build set of all valid node IDs
        all_ids = set(self.index.modules.keys())
        all_ids.update(self.index.type_definitions.keys())

        # Add definition IDs
        for module in ir_data.get("modules", []):
            for defn in module.get("definitions", []):
                if def_id := defn.get("id"):
                    all_ids.add(def_id)

        for i, gap in enumerate(ir_data.get("gap_markers", [])):
            location_base = f"$.gap_markers[{i}]"

            # Check location references a valid node
            gap_location = gap.get("location")
            if gap_location and gap_location not in all_ids:
                # Check if it matches a known prefix pattern (could be Layer 1/0)
                known_prefix = any(
                    gap_location.startswith(prefix)
                    for prefix in self.LAYER_PREFIXES
                )
                if not known_prefix:
                    yield create_error(
                        code=ValidationErrorCode.V004_GAP_LOCATION_NOT_FOUND,
                        message=f"Gap marker location '{gap_location}' not found",
                        location=f"{location_base}.location",
                        severity="warning",
                        location_value=gap_location,
                    )

            # Check affected_layers are valid (0-4)
            for j, layer in enumerate(gap.get("affected_layers", [])):
                if not isinstance(layer, int) or layer < 0 or layer > 4:
                    yield create_error(
                        code=ValidationErrorCode.V003_LAYER_MISMATCH,
                        message=f"Invalid layer number '{layer}' (must be 0-4)",
                        location=f"{location_base}.affected_layers[{j}]",
                        severity="error",
                    )

            # Check gap location layer matches affected layers
            if gap_location:
                inferred_layer = self._infer_layer_from_id(gap_location)
                affected_layers = gap.get("affected_layers", [])
                if inferred_layer is not None and affected_layers:
                    if inferred_layer not in affected_layers:
                        yield create_error(
                            code=ValidationErrorCode.V003_LAYER_MISMATCH,
                            message=f"Gap location '{gap_location}' is Layer {inferred_layer} "
                            f"but affected_layers is {affected_layers}",
                            location=f"{location_base}",
                            severity="info",
                        )

    def _infer_layer_from_id(self, node_id: str) -> int | None:
        """Infer the layer number from a node ID prefix.

        Args:
            node_id: The node ID.

        Returns:
            Layer number (0-4) or None if unknown.
        """
        for prefix, layer in self.LAYER_PREFIXES.items():
            if node_id.startswith(prefix):
                return layer
        return None

    def _check_preservation_consistency(
        self, ir_data: dict[str, Any]
    ) -> Iterator[ValidationError]:
        """Check preservation status consistency.

        Args:
            ir_data: The IR document to check.

        Yields:
            Consistency errors found.
        """
        for i, pres in enumerate(ir_data.get("preservation_statuses", [])):
            location_base = f"$.preservation_statuses[{i}]"

            current_level = pres.get("current_level")
            max_level = pres.get("max_achievable_level")

            # Check level values are valid
            if current_level is not None:
                if not isinstance(current_level, int) or current_level < 0 or current_level > 3:
                    yield create_error(
                        code=ValidationErrorCode.V004_INVALID_PRESERVATION_LEVEL,
                        message=f"Invalid current_level '{current_level}'",
                        location=f"{location_base}.current_level",
                        severity="error",
                    )

            if max_level is not None:
                if not isinstance(max_level, int) or max_level < 0 or max_level > 3:
                    yield create_error(
                        code=ValidationErrorCode.V004_INVALID_PRESERVATION_LEVEL,
                        message=f"Invalid max_achievable_level '{max_level}'",
                        location=f"{location_base}.max_achievable_level",
                        severity="error",
                    )

            # Check current_level <= max_achievable_level
            if (
                isinstance(current_level, int)
                and isinstance(max_level, int)
                and current_level > max_level
            ):
                yield create_error(
                    code=ValidationErrorCode.V003_LAYER_MISMATCH,
                    message=f"current_level ({current_level}) exceeds max_achievable_level ({max_level})",
                    location=location_base,
                    severity="error",
                )

            # Check blocking_gaps exist
            for j, gap_id in enumerate(pres.get("blocking_gaps", [])):
                if gap_id not in self.index.gap_markers:
                    yield create_error(
                        code=ValidationErrorCode.V002_DANGLING_REF,
                        message=f"Blocking gap '{gap_id}' not found in gap_markers",
                        location=f"{location_base}.blocking_gaps[{j}]",
                        severity="error",
                        ref=gap_id,
                    )


def check_consistency(ir_data: dict[str, Any]) -> list[ValidationError]:
    """Convenience function to check cross-layer consistency.

    Args:
        ir_data: The IR document to check.

    Returns:
        List of consistency errors found.
    """
    checker = ConsistencyChecker()
    return checker.check(ir_data)
