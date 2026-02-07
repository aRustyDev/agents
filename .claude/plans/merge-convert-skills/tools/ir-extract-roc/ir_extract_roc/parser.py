"""Roc source code parser.

Parses Roc source code and extracts:
- App/module declarations
- Platform imports
- Type definitions (records, tag unions, opaques)
- Function definitions with type annotations
- Pattern matching expressions
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class Purity(Enum):
    """Function purity level."""

    PURE = "pure"
    EFFECTFUL = "effectful"
    PLATFORM_TASK = "platform_task"


@dataclass
class RocTypeParameter:
    """Type parameter for polymorphic types."""

    name: str
    abilities: list[str] = field(default_factory=list)


@dataclass
class RocField:
    """Record field definition."""

    name: str
    type_annotation: str
    optional: bool = False
    line: int = 0


@dataclass
class RocVariant:
    """Tag union variant."""

    name: str
    payload_types: list[str] = field(default_factory=list)
    line: int = 0


@dataclass
class RocRecord:
    """Roc record type definition."""

    name: str
    fields: list[RocField] = field(default_factory=list)
    type_params: list[RocTypeParameter] = field(default_factory=list)
    line: int = 0
    column: int = 0


@dataclass
class RocTagUnion:
    """Roc tag union type definition."""

    name: str
    variants: list[RocVariant] = field(default_factory=list)
    type_params: list[RocTypeParameter] = field(default_factory=list)
    line: int = 0
    column: int = 0


@dataclass
class RocOpaque:
    """Roc opaque type definition."""

    name: str
    inner_type: str
    type_params: list[RocTypeParameter] = field(default_factory=list)
    abilities: list[str] = field(default_factory=list)
    line: int = 0
    column: int = 0


@dataclass
class RocParameter:
    """Function parameter."""

    name: str
    type_annotation: str | None = None
    line: int = 0


@dataclass
class RocFunction:
    """Roc function definition."""

    name: str
    type_annotation: str
    parameters: list[RocParameter] = field(default_factory=list)
    return_type: str = ""
    body: str = ""
    purity: Purity = Purity.PURE
    type_params: list[RocTypeParameter] = field(default_factory=list)
    abilities_required: list[str] = field(default_factory=list)
    line: int = 0
    column: int = 0

    @property
    def returns_result(self) -> bool:
        """Check if function returns Result type."""
        return "Result" in self.return_type

    @property
    def is_task(self) -> bool:
        """Check if function returns Task type."""
        return "Task" in self.return_type


@dataclass
class RocImport:
    """Roc import declaration."""

    module: str
    exposing: list[str] = field(default_factory=list)
    alias: str | None = None
    line: int = 0


@dataclass
class RocApp:
    """Roc app header."""

    provides: list[str] = field(default_factory=list)
    platform: str = ""
    platform_alias: str = ""
    line: int = 0


@dataclass
class RocModule:
    """Roc module header."""

    name: str
    exposes: list[str] = field(default_factory=list)
    line: int = 0


class RocParser:
    """Parser for Roc source code.

    Uses regex-based parsing as tree-sitter-roc may not be available.
    Handles Roc's unique syntax including:
    - Backslash lambdas
    - when...is pattern matching
    - Record syntax with colons
    - Tag unions with brackets
    """

    # Regex patterns for Roc syntax
    APP_PATTERN = re.compile(
        r'app\s+\[([^\]]+)\]\s*\{\s*(\w+)\s*:\s*platform\s+"([^"]+)"\s*\}'
    )
    MODULE_PATTERN = re.compile(
        r"module\s+\[([^\]]+)\]"
    )
    IMPORT_PATTERN = re.compile(
        r"import\s+(\w+(?:\.\w+)*)\s*(?:exposing\s+\[([^\]]+)\])?"
    )
    TYPE_ALIAS_PATTERN = re.compile(
        r"(\w+)\s*(?:\[([^\]]+)\])?\s*:\s*(.+?)(?=\n\w|\n\n|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    FUNCTION_TYPE_PATTERN = re.compile(
        r"^(\w+)\s*:\s*(.+?)\n\1\s*=",
        re.MULTILINE,
    )
    FUNCTION_IMPL_PATTERN = re.compile(
        r"^(\w+)\s*=\s*(.+?)(?=\n\w+\s*[=:]|\n\n|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    RECORD_TYPE_PATTERN = re.compile(
        r"\{\s*([^}]+)\s*\}"
    )
    TAG_UNION_PATTERN = re.compile(
        r"\[\s*([^\]]+)\s*\]"
    )
    WHEN_IS_PATTERN = re.compile(
        r"when\s+(.+?)\s+is\s*\n((?:\s+\w+(?:\s+\w+)*\s*->.+?\n?)+)",
        re.DOTALL,
    )

    def __init__(self) -> None:
        """Initialize the parser."""
        pass

    def parse(self, source: str) -> dict[str, Any]:
        """Parse Roc source code and return extracted information.

        Args:
            source: Roc source code

        Returns:
            Dictionary with extracted elements:
            - app: RocApp (if app file)
            - module: RocModule (if module file)
            - imports: List of RocImport
            - records: List of RocRecord
            - tag_unions: List of RocTagUnion
            - opaques: List of RocOpaque
            - functions: List of RocFunction
            - errors: List of parse errors
        """
        result: dict[str, Any] = {
            "app": None,
            "module": None,
            "imports": [],
            "records": [],
            "tag_unions": [],
            "opaques": [],
            "functions": [],
            "errors": [],
        }

        try:
            # Parse app header
            result["app"] = self._parse_app(source)

            # Parse module header
            result["module"] = self._parse_module(source)

            # Parse imports
            result["imports"] = self._parse_imports(source)

            # Parse type definitions
            self._parse_types(source, result)

            # Parse functions
            result["functions"] = self._parse_functions(source)

        except Exception as e:
            logger.error(f"Parse error: {e}")
            result["errors"].append({"message": str(e), "line": 0})

        return result

    def _parse_app(self, source: str) -> RocApp | None:
        """Parse app header."""
        match = self.APP_PATTERN.search(source)
        if not match:
            return None

        provides = [p.strip() for p in match.group(1).split(",")]
        platform_alias = match.group(2)
        platform = match.group(3)

        return RocApp(
            provides=provides,
            platform=platform,
            platform_alias=platform_alias,
            line=source[: match.start()].count("\n") + 1,
        )

    def _parse_module(self, source: str) -> RocModule | None:
        """Parse module header."""
        match = self.MODULE_PATTERN.search(source)
        if not match:
            return None

        exposes = [e.strip() for e in match.group(1).split(",")]
        # Module name would be from file path typically
        return RocModule(
            name="",
            exposes=exposes,
            line=source[: match.start()].count("\n") + 1,
        )

    def _parse_imports(self, source: str) -> list[RocImport]:
        """Parse import declarations."""
        imports = []

        for match in self.IMPORT_PATTERN.finditer(source):
            module = match.group(1)
            exposing = []
            if match.group(2):
                exposing = [e.strip() for e in match.group(2).split(",")]

            imports.append(
                RocImport(
                    module=module,
                    exposing=exposing,
                    line=source[: match.start()].count("\n") + 1,
                )
            )

        return imports

    def _parse_types(self, source: str, result: dict[str, Any]) -> None:
        """Parse type definitions (records, tag unions, opaques)."""
        # Find type annotations that define record types
        lines = source.split("\n")

        for i, line in enumerate(lines):
            # Skip if it looks like a function (has = on next line with same name)
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            # Check for type alias pattern: Name : Type
            if ":" in line and "=" not in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    type_str = parts[1].strip()

                    # Skip function types (contain ->)
                    if "->" in type_str:
                        continue

                    # Check for record type
                    if type_str.startswith("{"):
                        record = self._parse_record_type(name, type_str, i + 1)
                        if record:
                            result["records"].append(record)
                    # Check for tag union
                    elif type_str.startswith("["):
                        tag_union = self._parse_tag_union(name, type_str, i + 1)
                        if tag_union:
                            result["tag_unions"].append(tag_union)

    def _parse_record_type(
        self, name: str, type_str: str, line: int
    ) -> RocRecord | None:
        """Parse a record type definition."""
        match = self.RECORD_TYPE_PATTERN.search(type_str)
        if not match:
            return None

        fields = []
        fields_str = match.group(1)

        for field_part in fields_str.split(","):
            field_part = field_part.strip()
            if not field_part:
                continue

            if ":" in field_part:
                field_name, field_type = field_part.split(":", 1)
                optional = field_name.endswith("?")
                if optional:
                    field_name = field_name[:-1]
                fields.append(
                    RocField(
                        name=field_name.strip(),
                        type_annotation=field_type.strip(),
                        optional=optional,
                        line=line,
                    )
                )

        return RocRecord(name=name, fields=fields, line=line)

    def _parse_tag_union(
        self, name: str, type_str: str, line: int
    ) -> RocTagUnion | None:
        """Parse a tag union type definition."""
        match = self.TAG_UNION_PATTERN.search(type_str)
        if not match:
            return None

        variants = []
        variants_str = match.group(1)

        for variant_part in variants_str.split(","):
            variant_part = variant_part.strip()
            if not variant_part:
                continue

            # Parse variant name and optional payload
            parts = variant_part.split()
            variant_name = parts[0]
            payload_types = parts[1:] if len(parts) > 1 else []

            variants.append(
                RocVariant(
                    name=variant_name,
                    payload_types=payload_types,
                    line=line,
                )
            )

        return RocTagUnion(name=name, variants=variants, line=line)

    def _parse_functions(self, source: str) -> list[RocFunction]:
        """Parse function definitions."""
        functions = []

        # Find function type annotations
        for match in self.FUNCTION_TYPE_PATTERN.finditer(source):
            name = match.group(1)
            type_annotation = match.group(2).strip()
            line = source[: match.start()].count("\n") + 1

            # Parse type annotation
            params, return_type = self._parse_function_type(type_annotation)

            # Determine purity
            purity = self._determine_purity(type_annotation)

            # Find function body
            body = self._find_function_body(source, name, match.end())

            # Extract abilities required
            abilities = self._extract_abilities(type_annotation)

            functions.append(
                RocFunction(
                    name=name,
                    type_annotation=type_annotation,
                    parameters=params,
                    return_type=return_type,
                    body=body,
                    purity=purity,
                    abilities_required=abilities,
                    line=line,
                )
            )

        return functions

    def _parse_function_type(
        self, type_annotation: str
    ) -> tuple[list[RocParameter], str]:
        """Parse function type annotation into parameters and return type."""
        params = []

        # Split on -> to get parameter types and return type
        parts = type_annotation.split("->")
        if len(parts) < 2:
            return params, type_annotation

        # All but last are parameters
        param_types = parts[:-1]
        return_type = parts[-1].strip()

        for i, param_type in enumerate(param_types):
            param_type = param_type.strip()
            # Remove parentheses if present
            if param_type.startswith("(") and param_type.endswith(")"):
                param_type = param_type[1:-1]

            params.append(
                RocParameter(
                    name=f"arg{i}",
                    type_annotation=param_type,
                )
            )

        return params, return_type

    def _determine_purity(self, type_annotation: str) -> Purity:
        """Determine function purity from type annotation."""
        if "Task" in type_annotation:
            return Purity.PLATFORM_TASK
        if "IO" in type_annotation or "Effect" in type_annotation:
            return Purity.EFFECTFUL
        return Purity.PURE

    def _find_function_body(
        self, source: str, name: str, start_pos: int
    ) -> str:
        """Find and extract function body."""
        # Look for the implementation line
        impl_pattern = re.compile(
            rf"^{re.escape(name)}\s*=\s*(.+?)(?=\n\w+\s*[=:]|\n\n|\Z)",
            re.MULTILINE | re.DOTALL,
        )
        match = impl_pattern.search(source, start_pos)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_abilities(self, type_annotation: str) -> list[str]:
        """Extract ability constraints from type annotation."""
        abilities = []

        # Look for ability constraints like "a implements Eq"
        ability_pattern = re.compile(r"implements\s+(\w+)")
        for match in ability_pattern.finditer(type_annotation):
            abilities.append(match.group(1))

        return abilities

    def has_pattern_matching(self, source: str) -> bool:
        """Check if source uses pattern matching."""
        return bool(self.WHEN_IS_PATTERN.search(source))

    def extract_pattern_matches(
        self, source: str
    ) -> list[dict[str, Any]]:
        """Extract pattern matching expressions."""
        matches = []

        for match in self.WHEN_IS_PATTERN.finditer(source):
            expr = match.group(1).strip()
            branches_str = match.group(2)

            branches = []
            for branch_line in branches_str.strip().split("\n"):
                branch_line = branch_line.strip()
                if "->" in branch_line:
                    pattern, body = branch_line.split("->", 1)
                    branches.append({
                        "pattern": pattern.strip(),
                        "body": body.strip(),
                    })

            matches.append({
                "expression": expr,
                "branches": branches,
                "line": source[: match.start()].count("\n") + 1,
            })

        return matches
