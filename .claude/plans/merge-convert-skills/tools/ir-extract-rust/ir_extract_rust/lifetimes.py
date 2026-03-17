"""Lifetime extraction for Rust code.

This module handles extraction and analysis of Rust lifetimes, including
explicit lifetime annotations, lifetime elision, and lifetime bounds.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tree_sitter import Node

logger = logging.getLogger(__name__)


class LifetimeSource(str, Enum):
    """How a lifetime was determined."""

    EXPLICIT = "explicit"  # Declared in source
    ELIDED = "elided"  # Inferred via elision rules
    STATIC = "static"  # 'static lifetime
    ANONYMOUS = "anonymous"  # '_ anonymous lifetime


@dataclass
class LifetimeParam:
    """A lifetime parameter declaration.

    Attributes:
        name: Lifetime name (e.g., "a" for 'a)
        bounds: Other lifetimes this outlives
        source: How the lifetime was determined
    """

    name: str
    bounds: list[str] = field(default_factory=list)
    source: LifetimeSource = LifetimeSource.EXPLICIT


@dataclass
class LifetimeRef:
    """A reference to a lifetime in a type.

    Attributes:
        name: Lifetime name
        source: How it was determined
        location: Source location
    """

    name: str
    source: LifetimeSource
    location: str | None = None


@dataclass
class LifetimeConstraint:
    """A lifetime constraint (outlives relationship).

    Attributes:
        short: The shorter-lived lifetime
        long: The longer-lived lifetime (that short must outlive)
        location: Source location of the constraint
    """

    short: str
    long: str
    location: str | None = None


@dataclass
class FunctionLifetimes:
    """Lifetime information for a function.

    Attributes:
        lifetime_params: Declared lifetime parameters
        param_lifetimes: Lifetimes in parameter types
        return_lifetime: Lifetime of return type (if reference)
        constraints: Lifetime constraints from where clauses
        elision_applied: Whether lifetime elision was applied
    """

    lifetime_params: list[LifetimeParam] = field(default_factory=list)
    param_lifetimes: dict[str, list[LifetimeRef]] = field(default_factory=dict)
    return_lifetime: LifetimeRef | None = None
    constraints: list[LifetimeConstraint] = field(default_factory=list)
    elision_applied: bool = False


@dataclass
class TypeLifetimes:
    """Lifetime information for a type definition.

    Attributes:
        lifetime_params: Declared lifetime parameters
        field_lifetimes: Lifetimes used in each field
        constraints: Lifetime constraints from where clauses
    """

    lifetime_params: list[LifetimeParam] = field(default_factory=list)
    field_lifetimes: dict[str, list[LifetimeRef]] = field(default_factory=dict)
    constraints: list[LifetimeConstraint] = field(default_factory=list)


class LifetimeExtractor:
    """Extract lifetime information from Rust code.

    This extractor analyzes:
    - Explicit lifetime annotations
    - Lifetime elision patterns
    - Lifetime bounds and constraints
    - Lifetime relationships

    Example:
        extractor = LifetimeExtractor()
        lifetimes = extractor.extract_function_lifetimes(func_node, source)
        for param in lifetimes.lifetime_params:
            print(f"Lifetime '{param.name}")
    """

    def __init__(self) -> None:
        """Initialize the lifetime extractor."""
        self.lifetime_pattern = re.compile(r"'(\w+)")

    def extract_function_lifetimes(
        self, node: Node, source: str
    ) -> FunctionLifetimes:
        """Extract lifetime information from a function.

        Args:
            node: function_item or function_signature_item node
            source: Full source code

        Returns:
            FunctionLifetimes with all lifetime information
        """
        result = FunctionLifetimes()

        # Extract declared lifetime parameters
        result.lifetime_params = self._extract_lifetime_params(node, source)

        # Extract param lifetimes
        params_node = self._find_child_by_type(node, "parameters")
        if params_node:
            result.param_lifetimes = self._extract_param_lifetimes(
                params_node, source
            )

        # Extract return lifetime
        ret_node = self._find_child_by_type(node, "return_type")
        if ret_node:
            result.return_lifetime = self._extract_return_lifetime(
                ret_node, source
            )

        # Extract constraints from where clause
        where_node = self._find_child_by_type(node, "where_clause")
        if where_node:
            result.constraints = self._extract_lifetime_constraints(
                where_node, source
            )

        # Apply elision rules if no explicit lifetimes
        if not result.lifetime_params:
            result = self._apply_lifetime_elision(result)

        return result

    def extract_type_lifetimes(
        self, node: Node, source: str
    ) -> TypeLifetimes:
        """Extract lifetime information from a type definition.

        Args:
            node: struct_item, enum_item, or trait_item node
            source: Full source code

        Returns:
            TypeLifetimes with all lifetime information
        """
        result = TypeLifetimes()

        # Extract declared lifetime parameters
        result.lifetime_params = self._extract_lifetime_params(node, source)

        # Extract field lifetimes
        field_list = self._find_child_by_type(node, "field_declaration_list")
        if field_list:
            for child in field_list.children:
                if child.type == "field_declaration":
                    name = self._get_field_name(child, source)
                    type_node = self._find_type_node(child)
                    if name and type_node:
                        lifetimes = self._extract_lifetimes_from_type(
                            type_node, source
                        )
                        if lifetimes:
                            result.field_lifetimes[name] = lifetimes

        # Also check ordered fields (tuple structs)
        ordered_list = self._find_child_by_type(
            node, "ordered_field_declaration_list"
        )
        if ordered_list:
            for i, child in enumerate(ordered_list.children):
                type_node = self._find_type_node(child)
                if type_node:
                    lifetimes = self._extract_lifetimes_from_type(
                        type_node, source
                    )
                    if lifetimes:
                        result.field_lifetimes[f"_{i}"] = lifetimes

        # Extract constraints
        where_node = self._find_child_by_type(node, "where_clause")
        if where_node:
            result.constraints = self._extract_lifetime_constraints(
                where_node, source
            )

        return result

    def extract_lifetimes_from_type_str(
        self, type_str: str
    ) -> list[LifetimeRef]:
        """Extract lifetime references from a type string.

        Args:
            type_str: Type string (e.g., "&'a str")

        Returns:
            List of lifetime references
        """
        lifetimes: list[LifetimeRef] = []
        matches = self.lifetime_pattern.findall(type_str)

        for match in matches:
            if match == "static":
                lifetimes.append(LifetimeRef(
                    name="static",
                    source=LifetimeSource.STATIC,
                ))
            elif match == "_":
                lifetimes.append(LifetimeRef(
                    name="_",
                    source=LifetimeSource.ANONYMOUS,
                ))
            else:
                lifetimes.append(LifetimeRef(
                    name=match,
                    source=LifetimeSource.EXPLICIT,
                ))

        return lifetimes

    def infer_elided_lifetime(
        self,
        param_types: list[str],
        has_self: bool,
    ) -> str | None:
        """Infer the elided output lifetime based on Rust rules.

        Rust lifetime elision rules:
        1. Each elided lifetime in input gets a distinct lifetime
        2. If there's exactly one input lifetime, it's used for output
        3. If there's &self or &mut self, that lifetime is used for output

        Args:
            param_types: List of parameter type strings
            has_self: Whether the function has a self parameter

        Returns:
            Inferred lifetime name or None if ambiguous
        """
        # Rule 3: &self or &mut self
        if has_self:
            return "self"

        # Count input reference lifetimes
        ref_params = [t for t in param_types if t.strip().startswith("&")]

        # Rule 2: Exactly one input lifetime
        if len(ref_params) == 1:
            # Check if it has an explicit lifetime
            matches = self.lifetime_pattern.findall(ref_params[0])
            if matches:
                return matches[0]
            return "_elided_0"

        # Multiple input lifetimes - cannot elide output
        return None

    def _extract_lifetime_params(
        self, node: Node, source: str
    ) -> list[LifetimeParam]:
        """Extract lifetime parameter declarations.

        Args:
            node: Node with type_parameters
            source: Full source code

        Returns:
            List of lifetime parameters
        """
        params: list[LifetimeParam] = []
        type_params = self._find_child_by_type(node, "type_parameters")

        if type_params is None:
            return params

        for child in type_params.children:
            if child.type == "lifetime":
                name = self._get_text(child, source).lstrip("'")
                params.append(LifetimeParam(
                    name=name,
                    source=LifetimeSource.EXPLICIT,
                ))
            elif child.type == "constrained_type_parameter":
                # Could have lifetime bounds: 'a: 'b
                lifetime_node = self._find_child_by_type(child, "lifetime")
                if lifetime_node:
                    name = self._get_text(lifetime_node, source).lstrip("'")
                    bounds = self._extract_lifetime_bounds(child, source)
                    params.append(LifetimeParam(
                        name=name,
                        bounds=bounds,
                        source=LifetimeSource.EXPLICIT,
                    ))

        return params

    def _extract_lifetime_bounds(
        self, node: Node, source: str
    ) -> list[str]:
        """Extract lifetime bounds from a constrained type parameter.

        Args:
            node: constrained_type_parameter node
            source: Full source code

        Returns:
            List of lifetime names that this outlives
        """
        bounds: list[str] = []
        bounds_node = self._find_child_by_type(node, "trait_bounds")

        if bounds_node:
            for child in bounds_node.children:
                if child.type == "lifetime":
                    name = self._get_text(child, source).lstrip("'")
                    bounds.append(name)

        return bounds

    def _extract_param_lifetimes(
        self, params_node: Node, source: str
    ) -> dict[str, list[LifetimeRef]]:
        """Extract lifetimes from function parameters.

        Args:
            params_node: parameters node
            source: Full source code

        Returns:
            Dict mapping param name to lifetimes
        """
        result: dict[str, list[LifetimeRef]] = {}

        for child in params_node.children:
            if child.type == "self_parameter":
                lifetimes = self._extract_lifetimes_from_type(child, source)
                if lifetimes:
                    result["self"] = lifetimes

            elif child.type == "parameter":
                name = self._get_param_name(child, source)
                if name:
                    type_node = self._find_type_node(child)
                    if type_node:
                        lifetimes = self._extract_lifetimes_from_type(
                            type_node, source
                        )
                        if lifetimes:
                            result[name] = lifetimes

        return result

    def _extract_return_lifetime(
        self, ret_node: Node, source: str
    ) -> LifetimeRef | None:
        """Extract lifetime from return type.

        Args:
            ret_node: return_type node
            source: Full source code

        Returns:
            Lifetime reference or None
        """
        for child in ret_node.children:
            if child.type.endswith("_type"):
                lifetimes = self._extract_lifetimes_from_type(child, source)
                if lifetimes:
                    return lifetimes[0]

        return None

    def _extract_lifetimes_from_type(
        self, node: Node, source: str
    ) -> list[LifetimeRef]:
        """Extract lifetimes from a type node.

        Args:
            node: Type node
            source: Full source code

        Returns:
            List of lifetime references
        """
        type_str = self._get_text(node, source)
        return self.extract_lifetimes_from_type_str(type_str)

    def _extract_lifetime_constraints(
        self, where_node: Node, source: str
    ) -> list[LifetimeConstraint]:
        """Extract lifetime constraints from a where clause.

        Args:
            where_node: where_clause node
            source: Full source code

        Returns:
            List of lifetime constraints
        """
        constraints: list[LifetimeConstraint] = []

        for child in where_node.children:
            if child.type == "where_predicate":
                # Check for lifetime constraints ('a: 'b)
                lifetimes = []
                for sub in child.children:
                    if sub.type == "lifetime":
                        lifetimes.append(
                            self._get_text(sub, source).lstrip("'")
                        )

                if len(lifetimes) >= 2:
                    # First lifetime outlives the rest
                    short = lifetimes[0]
                    for long in lifetimes[1:]:
                        constraints.append(LifetimeConstraint(
                            short=short,
                            long=long,
                            location=f"{child.start_point[0]}:{child.start_point[1]}",
                        ))

        return constraints

    def _apply_lifetime_elision(
        self, lifetimes: FunctionLifetimes
    ) -> FunctionLifetimes:
        """Apply lifetime elision rules to fill in elided lifetimes.

        Args:
            lifetimes: FunctionLifetimes with explicit lifetimes

        Returns:
            FunctionLifetimes with elided lifetimes filled in
        """
        # Count input reference parameters
        ref_param_count = sum(
            1 for refs in lifetimes.param_lifetimes.values()
            if refs
        )

        has_self = "self" in lifetimes.param_lifetimes

        if lifetimes.return_lifetime is None and ref_param_count > 0:
            # Need to determine output lifetime
            if has_self:
                # Rule 3: Use self lifetime
                lifetimes.return_lifetime = LifetimeRef(
                    name="_self",
                    source=LifetimeSource.ELIDED,
                )
                lifetimes.elision_applied = True
            elif ref_param_count == 1:
                # Rule 2: Use the single input lifetime
                for param, refs in lifetimes.param_lifetimes.items():
                    if refs:
                        lifetimes.return_lifetime = LifetimeRef(
                            name=f"_elided_{param}",
                            source=LifetimeSource.ELIDED,
                        )
                        lifetimes.elision_applied = True
                        break

        return lifetimes

    def _find_child_by_type(
        self, node: Node, type_name: str
    ) -> Node | None:
        """Find first child with given type."""
        for child in node.children:
            if child.type == type_name:
                return child
        return None

    def _get_text(self, node: Node, source: str) -> str:
        """Get text for a node."""
        return source[node.start_byte:node.end_byte]

    def _get_param_name(self, node: Node, source: str) -> str | None:
        """Get parameter name from a parameter node."""
        for child in node.children:
            if child.type == "identifier":
                return self._get_text(child, source)
            elif child.type == "mut_pattern":
                for sub in child.children:
                    if sub.type == "identifier":
                        return self._get_text(sub, source)
        return None

    def _get_field_name(self, node: Node, source: str) -> str | None:
        """Get field name from a field declaration."""
        for child in node.children:
            if child.type == "field_identifier":
                return self._get_text(child, source)
        return None

    def _find_type_node(self, node: Node) -> Node | None:
        """Find the type node within a declaration."""
        for child in node.children:
            if child.type.endswith("_type"):
                return child
        return None
