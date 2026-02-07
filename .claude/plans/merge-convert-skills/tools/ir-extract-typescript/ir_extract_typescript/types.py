"""TypeScript type system analysis.

Provides analysis of TypeScript's rich type system including:
- Union and intersection types
- Conditional types
- Mapped types
- Template literal types
- Type inference
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class TypeCategory(str, Enum):
    """Category of TypeScript type."""

    PRIMITIVE = "primitive"
    LITERAL = "literal"
    OBJECT = "object"
    ARRAY = "array"
    TUPLE = "tuple"
    UNION = "union"
    INTERSECTION = "intersection"
    FUNCTION = "function"
    CONDITIONAL = "conditional"
    MAPPED = "mapped"
    TEMPLATE_LITERAL = "template_literal"
    INDEXED_ACCESS = "indexed_access"
    KEYOF = "keyof"
    TYPEOF = "typeof"
    INFER = "infer"
    GENERIC = "generic"
    UNKNOWN = "unknown"


@dataclass
class TypeInfo:
    """Information about a TypeScript type."""

    raw: str
    category: TypeCategory
    is_nullable: bool = False
    is_optional: bool = False
    type_args: list[TypeInfo] = field(default_factory=list)
    members: list[tuple[str, TypeInfo]] = field(default_factory=list)

    # For union/intersection
    constituent_types: list[TypeInfo] = field(default_factory=list)

    # For function types
    param_types: list[TypeInfo] = field(default_factory=list)
    return_type: TypeInfo | None = None

    # For mapped types
    mapped_key_type: str | None = None
    mapped_value_type: TypeInfo | None = None

    # For conditional types
    check_type: TypeInfo | None = None
    extends_type: TypeInfo | None = None
    true_type: TypeInfo | None = None
    false_type: TypeInfo | None = None


class TypeAnalyzer:
    """Analyzes TypeScript types for semantic information."""

    # Primitive types
    PRIMITIVES = {
        "string",
        "number",
        "boolean",
        "null",
        "undefined",
        "void",
        "never",
        "any",
        "unknown",
        "symbol",
        "bigint",
        "object",
    }

    # Built-in utility types
    UTILITY_TYPES = {
        "Partial",
        "Required",
        "Readonly",
        "Record",
        "Pick",
        "Omit",
        "Exclude",
        "Extract",
        "NonNullable",
        "ReturnType",
        "Parameters",
        "InstanceType",
        "ConstructorParameters",
        "ThisParameterType",
        "OmitThisParameter",
        "Uppercase",
        "Lowercase",
        "Capitalize",
        "Uncapitalize",
        "Awaited",
    }

    def __init__(self) -> None:
        """Initialize the type analyzer."""
        self._type_cache: dict[str, TypeInfo] = {}

    def analyze(self, type_str: str | None) -> TypeInfo | None:
        """Analyze a type string and return TypeInfo.

        Args:
            type_str: TypeScript type as string

        Returns:
            TypeInfo with analysis results, or None if type_str is None
        """
        if not type_str:
            return None

        type_str = type_str.strip()

        # Check cache
        if type_str in self._type_cache:
            return self._type_cache[type_str]

        info = self._analyze_type(type_str)
        self._type_cache[type_str] = info
        return info

    def _analyze_type(self, type_str: str) -> TypeInfo:
        """Analyze a type string."""
        type_str = type_str.strip()

        # Check for union types (handle parentheses)
        if self._is_union_type(type_str):
            return self._analyze_union(type_str)

        # Check for intersection types
        if self._is_intersection_type(type_str):
            return self._analyze_intersection(type_str)

        # Check for array types
        if type_str.endswith("[]"):
            return self._analyze_array(type_str)

        # Check for tuple types
        if type_str.startswith("[") and type_str.endswith("]"):
            return self._analyze_tuple(type_str)

        # Check for function types
        if "=>" in type_str:
            return self._analyze_function(type_str)

        # Check for generic types
        if "<" in type_str and type_str.endswith(">"):
            return self._analyze_generic(type_str)

        # Check for mapped types
        if type_str.startswith("{") and "in" in type_str:
            return self._analyze_mapped(type_str)

        # Check for conditional types
        if " extends " in type_str and " ? " in type_str:
            return self._analyze_conditional(type_str)

        # Check for keyof
        if type_str.startswith("keyof "):
            return TypeInfo(
                raw=type_str,
                category=TypeCategory.KEYOF,
            )

        # Check for typeof
        if type_str.startswith("typeof "):
            return TypeInfo(
                raw=type_str,
                category=TypeCategory.TYPEOF,
            )

        # Check for indexed access
        if "[" in type_str and not type_str.startswith("["):
            return TypeInfo(
                raw=type_str,
                category=TypeCategory.INDEXED_ACCESS,
            )

        # Check for primitives
        if type_str in self.PRIMITIVES:
            return TypeInfo(
                raw=type_str,
                category=TypeCategory.PRIMITIVE,
            )

        # Check for literal types
        if self._is_literal_type(type_str):
            return TypeInfo(
                raw=type_str,
                category=TypeCategory.LITERAL,
            )

        # Check for object types
        if type_str.startswith("{") and type_str.endswith("}"):
            return self._analyze_object(type_str)

        # Template literal types
        if type_str.startswith("`"):
            return TypeInfo(
                raw=type_str,
                category=TypeCategory.TEMPLATE_LITERAL,
            )

        # Default to unknown (could be a type reference)
        return TypeInfo(
            raw=type_str,
            category=TypeCategory.UNKNOWN,
        )

    def _is_union_type(self, type_str: str) -> bool:
        """Check if type is a union type."""
        depth = 0
        for i, char in enumerate(type_str):
            if char in "(<{[":
                depth += 1
            elif char in ")>}]":
                depth -= 1
            elif char == "|" and depth == 0:
                return True
        return False

    def _is_intersection_type(self, type_str: str) -> bool:
        """Check if type is an intersection type."""
        depth = 0
        for i, char in enumerate(type_str):
            if char in "(<{[":
                depth += 1
            elif char in ")>}]":
                depth -= 1
            elif char == "&" and depth == 0:
                return True
        return False

    def _is_literal_type(self, type_str: str) -> bool:
        """Check if type is a literal type."""
        # String literal
        if (type_str.startswith('"') and type_str.endswith('"')) or (
            type_str.startswith("'") and type_str.endswith("'")
        ):
            return True
        # Number literal
        if re.match(r"^-?\d+(\.\d+)?$", type_str):
            return True
        # Boolean literal
        if type_str in {"true", "false"}:
            return True
        return False

    def _analyze_union(self, type_str: str) -> TypeInfo:
        """Analyze a union type."""
        parts = self._split_at_operator(type_str, "|")
        constituent_types = [self._analyze_type(p.strip()) for p in parts]

        is_nullable = any(
            t.raw in {"null", "undefined"} for t in constituent_types
        )

        return TypeInfo(
            raw=type_str,
            category=TypeCategory.UNION,
            is_nullable=is_nullable,
            constituent_types=constituent_types,
        )

    def _analyze_intersection(self, type_str: str) -> TypeInfo:
        """Analyze an intersection type."""
        parts = self._split_at_operator(type_str, "&")
        constituent_types = [self._analyze_type(p.strip()) for p in parts]

        return TypeInfo(
            raw=type_str,
            category=TypeCategory.INTERSECTION,
            constituent_types=constituent_types,
        )

    def _analyze_array(self, type_str: str) -> TypeInfo:
        """Analyze an array type."""
        element_type = type_str[:-2]
        return TypeInfo(
            raw=type_str,
            category=TypeCategory.ARRAY,
            type_args=[self._analyze_type(element_type)],
        )

    def _analyze_tuple(self, type_str: str) -> TypeInfo:
        """Analyze a tuple type."""
        inner = type_str[1:-1]
        if not inner:
            return TypeInfo(
                raw=type_str,
                category=TypeCategory.TUPLE,
                type_args=[],
            )

        elements = self._split_at_operator(inner, ",")
        type_args = [self._analyze_type(e.strip()) for e in elements]

        return TypeInfo(
            raw=type_str,
            category=TypeCategory.TUPLE,
            type_args=type_args,
        )

    def _analyze_function(self, type_str: str) -> TypeInfo:
        """Analyze a function type."""
        # Simple parsing for (params) => return
        arrow_idx = type_str.find("=>")
        if arrow_idx == -1:
            return TypeInfo(raw=type_str, category=TypeCategory.FUNCTION)

        params_part = type_str[:arrow_idx].strip()
        return_part = type_str[arrow_idx + 2 :].strip()

        # Parse return type
        return_type = self._analyze_type(return_part)

        # Parse parameter types (simplified)
        param_types = []
        if params_part.startswith("(") and params_part.endswith(")"):
            inner = params_part[1:-1]
            if inner:
                params = self._split_at_operator(inner, ",")
                for p in params:
                    if ":" in p:
                        _, type_part = p.split(":", 1)
                        param_types.append(self._analyze_type(type_part.strip()))
                    else:
                        param_types.append(
                            TypeInfo(raw="unknown", category=TypeCategory.UNKNOWN)
                        )

        return TypeInfo(
            raw=type_str,
            category=TypeCategory.FUNCTION,
            param_types=param_types,
            return_type=return_type,
        )

    def _analyze_generic(self, type_str: str) -> TypeInfo:
        """Analyze a generic type."""
        bracket_idx = type_str.index("<")
        base_type = type_str[:bracket_idx]
        args_part = type_str[bracket_idx + 1 : -1]

        type_args = []
        if args_part:
            args = self._split_at_operator(args_part, ",")
            type_args = [self._analyze_type(a.strip()) for a in args]

        return TypeInfo(
            raw=type_str,
            category=TypeCategory.GENERIC,
            type_args=type_args,
        )

    def _analyze_object(self, type_str: str) -> TypeInfo:
        """Analyze an object type."""
        return TypeInfo(
            raw=type_str,
            category=TypeCategory.OBJECT,
        )

    def _analyze_mapped(self, type_str: str) -> TypeInfo:
        """Analyze a mapped type."""
        return TypeInfo(
            raw=type_str,
            category=TypeCategory.MAPPED,
        )

    def _analyze_conditional(self, type_str: str) -> TypeInfo:
        """Analyze a conditional type."""
        return TypeInfo(
            raw=type_str,
            category=TypeCategory.CONDITIONAL,
        )

    def _split_at_operator(self, type_str: str, operator: str) -> list[str]:
        """Split type string at operator respecting nesting."""
        parts = []
        current = []
        depth = 0

        i = 0
        while i < len(type_str):
            char = type_str[i]
            if char in "(<{[":
                depth += 1
                current.append(char)
            elif char in ")>}]":
                depth -= 1
                current.append(char)
            elif char == operator and depth == 0:
                parts.append("".join(current))
                current = []
            else:
                current.append(char)
            i += 1

        if current:
            parts.append("".join(current))

        return parts

    def is_assignable_to(
        self, source: TypeInfo, target: TypeInfo
    ) -> tuple[bool, str]:
        """Check if source type is assignable to target type.

        Returns:
            Tuple of (is_assignable, reason)
        """
        # Same type
        if source.raw == target.raw:
            return True, "exact match"

        # any is assignable to anything
        if source.raw == "any" or target.raw == "any":
            return True, "any type"

        # unknown can only be assigned to unknown or any
        if source.raw == "unknown":
            if target.raw in {"unknown", "any"}:
                return True, "unknown to unknown/any"
            return False, "unknown is not assignable to specific types"

        # never is assignable to everything
        if source.raw == "never":
            return True, "never is assignable to all types"

        # null/undefined checks
        if source.raw in {"null", "undefined"}:
            if target.is_nullable:
                return True, "nullable target"
            if target.raw in {"null", "undefined", "any", "unknown"}:
                return True, "compatible nullable types"
            return False, "null/undefined not assignable to non-nullable"

        # Union type handling
        if source.category == TypeCategory.UNION:
            # All constituents must be assignable to target
            for const in source.constituent_types:
                is_assign, _ = self.is_assignable_to(const, target)
                if not is_assign:
                    return False, f"union member {const.raw} not assignable"
            return True, "all union members assignable"

        if target.category == TypeCategory.UNION:
            # Source must be assignable to at least one constituent
            for const in target.constituent_types:
                is_assign, _ = self.is_assignable_to(source, const)
                if is_assign:
                    return True, f"assignable to union member {const.raw}"
            return False, "not assignable to any union member"

        # Array handling
        if source.category == TypeCategory.ARRAY and target.category == TypeCategory.ARRAY:
            if source.type_args and target.type_args:
                return self.is_assignable_to(source.type_args[0], target.type_args[0])
            return True, "array types"

        # For complex types, fall back to structural comparison
        return False, "incompatible types"

    def get_common_type(self, types: list[TypeInfo]) -> TypeInfo:
        """Get the common type for a list of types."""
        if not types:
            return TypeInfo(raw="never", category=TypeCategory.PRIMITIVE)

        if len(types) == 1:
            return types[0]

        # If all types are the same, return that type
        if all(t.raw == types[0].raw for t in types):
            return types[0]

        # Otherwise, create a union type
        raw = " | ".join(t.raw for t in types)
        return TypeInfo(
            raw=raw,
            category=TypeCategory.UNION,
            constituent_types=types,
        )
