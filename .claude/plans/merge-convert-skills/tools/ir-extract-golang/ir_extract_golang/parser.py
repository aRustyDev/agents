"""Go source code parser using tree-sitter.

Parses Go source code and extracts:
- Package declarations
- Imports
- Type definitions (structs, interfaces, type aliases)
- Functions and methods
- Channel operations
- Goroutine invocations
- Defer statements
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class Visibility(Enum):
    """Go visibility based on capitalization."""

    EXPORTED = "exported"
    UNEXPORTED = "unexported"


@dataclass
class GoTypeParameter:
    """Type parameter for generics (Go 1.18+)."""

    name: str
    constraint: str | None = None


@dataclass
class GoField:
    """Struct field or interface method."""

    name: str
    type_annotation: str
    tag: str | None = None
    embedded: bool = False
    line: int = 0
    column: int = 0

    @property
    def visibility(self) -> Visibility:
        """Determine visibility from name capitalization."""
        if self.name and self.name[0].isupper():
            return Visibility.EXPORTED
        return Visibility.UNEXPORTED


@dataclass
class GoParameter:
    """Function/method parameter."""

    name: str
    type_annotation: str
    variadic: bool = False
    line: int = 0
    column: int = 0


@dataclass
class GoResult:
    """Function/method result (return value)."""

    name: str | None
    type_annotation: str


@dataclass
class GoMethod:
    """Interface method signature or struct method."""

    name: str
    parameters: list[GoParameter] = field(default_factory=list)
    results: list[GoResult] = field(default_factory=list)
    type_params: list[GoTypeParameter] = field(default_factory=list)
    receiver: tuple[str, str] | None = None  # (name, type)
    line: int = 0
    column: int = 0

    @property
    def visibility(self) -> Visibility:
        """Determine visibility from name capitalization."""
        if self.name and self.name[0].isupper():
            return Visibility.EXPORTED
        return Visibility.UNEXPORTED

    @property
    def returns_error(self) -> bool:
        """Check if function returns error as last result."""
        if self.results:
            last = self.results[-1]
            return last.type_annotation == "error"
        return False


@dataclass
class GoStruct:
    """Go struct type definition."""

    name: str
    fields: list[GoField] = field(default_factory=list)
    type_params: list[GoTypeParameter] = field(default_factory=list)
    methods: list[GoMethod] = field(default_factory=list)
    line: int = 0
    column: int = 0

    @property
    def exported(self) -> bool:
        """Check if struct is exported."""
        return bool(self.name and self.name[0].isupper())


@dataclass
class GoInterface:
    """Go interface type definition."""

    name: str
    methods: list[GoMethod] = field(default_factory=list)
    embedded: list[str] = field(default_factory=list)
    type_params: list[GoTypeParameter] = field(default_factory=list)
    line: int = 0
    column: int = 0

    @property
    def exported(self) -> bool:
        """Check if interface is exported."""
        return bool(self.name and self.name[0].isupper())


@dataclass
class GoTypeAlias:
    """Go type alias definition."""

    name: str
    aliased_type: str
    type_params: list[GoTypeParameter] = field(default_factory=list)
    line: int = 0
    column: int = 0

    @property
    def exported(self) -> bool:
        """Check if type alias is exported."""
        return bool(self.name and self.name[0].isupper())


@dataclass
class GoFunction:
    """Go function definition."""

    name: str
    parameters: list[GoParameter] = field(default_factory=list)
    results: list[GoResult] = field(default_factory=list)
    type_params: list[GoTypeParameter] = field(default_factory=list)
    receiver: tuple[str, str] | None = None  # (name, type) for methods
    body: str | None = None
    defers: list[str] = field(default_factory=list)
    goroutines: list[str] = field(default_factory=list)
    channel_ops: list[dict[str, Any]] = field(default_factory=list)
    line: int = 0
    column: int = 0

    @property
    def exported(self) -> bool:
        """Check if function is exported."""
        return bool(self.name and self.name[0].isupper())

    @property
    def returns_error(self) -> bool:
        """Check if function returns error as last result."""
        if self.results:
            last = self.results[-1]
            return last.type_annotation == "error"
        return False

    @property
    def is_method(self) -> bool:
        """Check if this is a method (has receiver)."""
        return self.receiver is not None


@dataclass
class GoImport:
    """Go import declaration."""

    path: str
    alias: str | None = None
    dot_import: bool = False
    blank_import: bool = False
    line: int = 0


@dataclass
class GoConst:
    """Go constant declaration."""

    name: str
    type_annotation: str | None
    value: str
    iota: bool = False
    line: int = 0
    column: int = 0

    @property
    def exported(self) -> bool:
        """Check if constant is exported."""
        return bool(self.name and self.name[0].isupper())


@dataclass
class GoVar:
    """Go variable declaration."""

    name: str
    type_annotation: str | None
    value: str | None
    line: int = 0
    column: int = 0

    @property
    def exported(self) -> bool:
        """Check if variable is exported."""
        return bool(self.name and self.name[0].isupper())


@dataclass
class GoChannel:
    """Channel type information."""

    element_type: str
    direction: str  # "bidirectional", "send", "receive"
    buffered: bool = False
    buffer_size: int | None = None


class GolangParser:
    """Parser for Go source code using tree-sitter."""

    def __init__(self) -> None:
        """Initialize the parser with tree-sitter."""
        self._parser = None
        self._language = None
        self._init_parser()

    def _init_parser(self) -> None:
        """Initialize tree-sitter parser."""
        try:
            import tree_sitter_language_pack as tslp

            self._language = tslp.get_language("go")
            import tree_sitter

            self._parser = tree_sitter.Parser(self._language)
        except ImportError:
            logger.warning("tree-sitter-language-pack not available")
        except Exception as e:
            logger.warning(f"Failed to initialize Go parser: {e}")

    def parse(self, source: str) -> dict[str, Any]:
        """Parse Go source code and return extracted information.

        Args:
            source: Go source code

        Returns:
            Dictionary with extracted elements:
            - package: Package name
            - imports: List of GoImport
            - structs: List of GoStruct
            - interfaces: List of GoInterface
            - type_aliases: List of GoTypeAlias
            - functions: List of GoFunction
            - constants: List of GoConst
            - variables: List of GoVar
            - errors: List of parse errors
        """
        result: dict[str, Any] = {
            "package": "",
            "imports": [],
            "structs": [],
            "interfaces": [],
            "type_aliases": [],
            "functions": [],
            "constants": [],
            "variables": [],
            "errors": [],
        }

        if not self._parser:
            result["errors"].append(
                {"message": "Parser not initialized", "line": 0}
            )
            return result

        try:
            tree = self._parser.parse(source.encode("utf-8"))
            root = tree.root_node

            # Check for parse errors
            if root.has_error:
                self._collect_errors(root, result["errors"])

            # Extract package
            result["package"] = self._extract_package(root, source)

            # Extract imports
            result["imports"] = self._extract_imports(root, source)

            # Extract type definitions
            self._extract_type_definitions(root, source, result)

            # Extract functions
            result["functions"] = self._extract_functions(root, source)

            # Extract constants
            result["constants"] = self._extract_constants(root, source)

            # Extract variables
            result["variables"] = self._extract_variables(root, source)

            # Associate methods with structs
            self._associate_methods(result)

        except Exception as e:
            logger.error(f"Parse error: {e}")
            result["errors"].append({"message": str(e), "line": 0})

        return result

    def _collect_errors(
        self, node: Any, errors: list[dict[str, Any]]
    ) -> None:
        """Collect parse errors from the AST."""
        if node.type == "ERROR":
            errors.append(
                {
                    "message": "Syntax error",
                    "line": node.start_point[0] + 1,
                    "column": node.start_point[1],
                }
            )
        for child in node.children:
            self._collect_errors(child, errors)

    def _get_text(self, node: Any, source: str) -> str:
        """Get text content of a node."""
        return source[node.start_byte : node.end_byte]

    def _extract_package(self, root: Any, source: str) -> str:
        """Extract package name."""
        for node in root.children:
            if node.type == "package_clause":
                for child in node.children:
                    if child.type == "package_identifier":
                        return self._get_text(child, source)
        return ""

    def _extract_imports(self, root: Any, source: str) -> list[GoImport]:
        """Extract import declarations."""
        imports = []

        for node in root.children:
            if node.type == "import_declaration":
                imports.extend(self._parse_import_decl(node, source))

        return imports

    def _parse_import_decl(
        self, node: Any, source: str
    ) -> list[GoImport]:
        """Parse an import declaration."""
        imports = []

        for child in node.children:
            if child.type == "import_spec":
                imports.append(self._parse_import_spec(child, source))
            elif child.type == "import_spec_list":
                for spec in child.children:
                    if spec.type == "import_spec":
                        imports.append(self._parse_import_spec(spec, source))

        return imports

    def _parse_import_spec(self, node: Any, source: str) -> GoImport:
        """Parse a single import spec."""
        path = ""
        alias = None
        dot_import = False
        blank_import = False

        for child in node.children:
            if child.type == "interpreted_string_literal":
                path = self._get_text(child, source).strip('"')
            elif child.type == "package_identifier":
                alias = self._get_text(child, source)
            elif child.type == "dot":
                dot_import = True
            elif child.type == "blank_identifier":
                blank_import = True

        return GoImport(
            path=path,
            alias=alias,
            dot_import=dot_import,
            blank_import=blank_import,
            line=node.start_point[0] + 1,
        )

    def _extract_type_definitions(
        self, root: Any, source: str, result: dict[str, Any]
    ) -> None:
        """Extract all type definitions."""
        for node in root.children:
            if node.type == "type_declaration":
                self._parse_type_decl(node, source, result)

    def _parse_type_decl(
        self, node: Any, source: str, result: dict[str, Any]
    ) -> None:
        """Parse a type declaration."""
        for child in node.children:
            if child.type == "type_spec":
                self._parse_type_spec(child, source, result)

    def _parse_type_spec(
        self, node: Any, source: str, result: dict[str, Any]
    ) -> None:
        """Parse a single type spec."""
        name = ""
        type_params: list[GoTypeParameter] = []
        type_node = None

        for child in node.children:
            if child.type == "type_identifier":
                name = self._get_text(child, source)
            elif child.type == "type_parameter_list":
                type_params = self._parse_type_params(child, source)
            elif child.type in (
                "struct_type",
                "interface_type",
                "type_identifier",
                "pointer_type",
                "slice_type",
                "array_type",
                "map_type",
                "channel_type",
                "function_type",
                "qualified_type",
            ):
                type_node = child

        if not name or not type_node:
            return

        line = node.start_point[0] + 1
        column = node.start_point[1]

        if type_node.type == "struct_type":
            struct = self._parse_struct_type(type_node, source, name)
            struct.type_params = type_params
            struct.line = line
            struct.column = column
            result["structs"].append(struct)
        elif type_node.type == "interface_type":
            iface = self._parse_interface_type(type_node, source, name)
            iface.type_params = type_params
            iface.line = line
            iface.column = column
            result["interfaces"].append(iface)
        else:
            # Type alias
            aliased_type = self._get_text(type_node, source)
            result["type_aliases"].append(
                GoTypeAlias(
                    name=name,
                    aliased_type=aliased_type,
                    type_params=type_params,
                    line=line,
                    column=column,
                )
            )

    def _parse_type_params(
        self, node: Any, source: str
    ) -> list[GoTypeParameter]:
        """Parse type parameters (generics)."""
        params = []

        for child in node.children:
            if child.type == "type_parameter_declaration":
                name = ""
                constraint = None

                for part in child.children:
                    if part.type == "identifier":
                        name = self._get_text(part, source)
                    elif part.type in (
                        "type_identifier",
                        "interface_type",
                        "union_type",
                    ):
                        constraint = self._get_text(part, source)

                if name:
                    params.append(GoTypeParameter(name=name, constraint=constraint))

        return params

    def _parse_struct_type(
        self, node: Any, source: str, name: str
    ) -> GoStruct:
        """Parse a struct type definition."""
        struct = GoStruct(name=name)

        for child in node.children:
            if child.type == "field_declaration_list":
                for field_node in child.children:
                    if field_node.type == "field_declaration":
                        fields = self._parse_field_declaration(
                            field_node, source
                        )
                        struct.fields.extend(fields)

        return struct

    def _parse_field_declaration(
        self, node: Any, source: str
    ) -> list[GoField]:
        """Parse a field declaration (may have multiple names)."""
        fields = []
        names: list[str] = []
        type_annotation = ""
        tag = None
        embedded = False
        line = node.start_point[0] + 1
        column = node.start_point[1]

        for child in node.children:
            if child.type == "field_identifier":
                names.append(self._get_text(child, source))
            elif child.type in (
                "type_identifier",
                "pointer_type",
                "slice_type",
                "array_type",
                "map_type",
                "channel_type",
                "function_type",
                "qualified_type",
                "struct_type",
                "interface_type",
            ):
                type_annotation = self._get_text(child, source)
                # Check for embedded field
                if not names:
                    embedded = True
                    # Extract the type name as the field name
                    if child.type == "type_identifier":
                        names.append(self._get_text(child, source))
                    elif child.type == "pointer_type":
                        # *Type becomes embedded as Type
                        for part in child.children:
                            if part.type == "type_identifier":
                                names.append(self._get_text(part, source))
                                break
            elif child.type == "raw_string_literal" or child.type == "interpreted_string_literal":
                tag = self._get_text(child, source)

        for name in names:
            fields.append(
                GoField(
                    name=name,
                    type_annotation=type_annotation,
                    tag=tag,
                    embedded=embedded,
                    line=line,
                    column=column,
                )
            )

        return fields

    def _parse_interface_type(
        self, node: Any, source: str, name: str
    ) -> GoInterface:
        """Parse an interface type definition."""
        iface = GoInterface(name=name)

        for child in node.children:
            if child.type == "method_spec_list":
                for spec in child.children:
                    if spec.type == "method_spec":
                        method = self._parse_method_spec(spec, source)
                        if method:
                            iface.methods.append(method)
                    elif spec.type == "type_identifier":
                        # Embedded interface
                        iface.embedded.append(self._get_text(spec, source))
                    elif spec.type == "qualified_type":
                        # Embedded interface from another package
                        iface.embedded.append(self._get_text(spec, source))

        return iface

    def _parse_method_spec(
        self, node: Any, source: str
    ) -> GoMethod | None:
        """Parse a method specification in an interface."""
        name = ""
        params: list[GoParameter] = []
        results: list[GoResult] = []
        type_params: list[GoTypeParameter] = []

        for child in node.children:
            if child.type == "field_identifier":
                name = self._get_text(child, source)
            elif child.type == "type_parameter_list":
                type_params = self._parse_type_params(child, source)
            elif child.type == "parameter_list":
                params = self._parse_parameters(child, source)
            elif child.type == "result":
                results = self._parse_results(child, source)

        if not name:
            return None

        return GoMethod(
            name=name,
            parameters=params,
            results=results,
            type_params=type_params,
            line=node.start_point[0] + 1,
            column=node.start_point[1],
        )

    def _parse_parameters(
        self, node: Any, source: str
    ) -> list[GoParameter]:
        """Parse function parameters."""
        params = []

        for child in node.children:
            if child.type == "parameter_declaration":
                params.extend(
                    self._parse_parameter_declaration(child, source)
                )

        return params

    def _parse_parameter_declaration(
        self, node: Any, source: str
    ) -> list[GoParameter]:
        """Parse a parameter declaration (may have multiple names)."""
        params = []
        names: list[str] = []
        type_annotation = ""
        variadic = False

        for child in node.children:
            if child.type == "identifier":
                names.append(self._get_text(child, source))
            elif child.type == "variadic_parameter_declaration":
                variadic = True
                for part in child.children:
                    if part.type == "identifier":
                        names.append(self._get_text(part, source))
                    elif part.type not in ("...",):
                        type_annotation = self._get_text(part, source)
            elif child.type in (
                "type_identifier",
                "pointer_type",
                "slice_type",
                "array_type",
                "map_type",
                "channel_type",
                "function_type",
                "qualified_type",
                "struct_type",
                "interface_type",
            ):
                type_annotation = self._get_text(child, source)

        # If no names, it's an unnamed parameter
        if not names:
            names = [""]

        for name in names:
            params.append(
                GoParameter(
                    name=name,
                    type_annotation=type_annotation,
                    variadic=variadic,
                )
            )

        return params

    def _parse_results(self, node: Any, source: str) -> list[GoResult]:
        """Parse function results (return types)."""
        results = []

        for child in node.children:
            if child.type == "parameter_list":
                # Named return values
                for param in child.children:
                    if param.type == "parameter_declaration":
                        for r in self._parse_result_declaration(
                            param, source
                        ):
                            results.append(r)
            elif child.type in (
                "type_identifier",
                "pointer_type",
                "slice_type",
                "array_type",
                "map_type",
                "channel_type",
                "function_type",
                "qualified_type",
                "struct_type",
                "interface_type",
            ):
                # Single unnamed return
                results.append(
                    GoResult(
                        name=None,
                        type_annotation=self._get_text(child, source),
                    )
                )

        return results

    def _parse_result_declaration(
        self, node: Any, source: str
    ) -> list[GoResult]:
        """Parse a result declaration (may have multiple names)."""
        results = []
        names: list[str | None] = []
        type_annotation = ""

        for child in node.children:
            if child.type == "identifier":
                names.append(self._get_text(child, source))
            elif child.type in (
                "type_identifier",
                "pointer_type",
                "slice_type",
                "array_type",
                "map_type",
                "channel_type",
                "function_type",
                "qualified_type",
            ):
                type_annotation = self._get_text(child, source)

        if not names:
            names = [None]

        for name in names:
            results.append(GoResult(name=name, type_annotation=type_annotation))

        return results

    def _extract_functions(
        self, root: Any, source: str
    ) -> list[GoFunction]:
        """Extract all function declarations."""
        functions = []

        for node in root.children:
            if node.type == "function_declaration":
                func = self._parse_function(node, source)
                if func:
                    functions.append(func)
            elif node.type == "method_declaration":
                func = self._parse_method(node, source)
                if func:
                    functions.append(func)

        return functions

    def _parse_function(self, node: Any, source: str) -> GoFunction | None:
        """Parse a function declaration."""
        name = ""
        params: list[GoParameter] = []
        results: list[GoResult] = []
        type_params: list[GoTypeParameter] = []
        body = None
        defers: list[str] = []
        goroutines: list[str] = []
        channel_ops: list[dict[str, Any]] = []

        for child in node.children:
            if child.type == "identifier":
                name = self._get_text(child, source)
            elif child.type == "type_parameter_list":
                type_params = self._parse_type_params(child, source)
            elif child.type == "parameter_list":
                params = self._parse_parameters(child, source)
            elif child.type == "result":
                results = self._parse_results(child, source)
            elif child.type == "block":
                body = self._get_text(child, source)
                defers, goroutines, channel_ops = self._analyze_body(
                    child, source
                )

        if not name:
            return None

        return GoFunction(
            name=name,
            parameters=params,
            results=results,
            type_params=type_params,
            body=body,
            defers=defers,
            goroutines=goroutines,
            channel_ops=channel_ops,
            line=node.start_point[0] + 1,
            column=node.start_point[1],
        )

    def _parse_method(self, node: Any, source: str) -> GoFunction | None:
        """Parse a method declaration (function with receiver)."""
        name = ""
        receiver: tuple[str, str] | None = None
        params: list[GoParameter] = []
        results: list[GoResult] = []
        type_params: list[GoTypeParameter] = []
        body = None
        defers: list[str] = []
        goroutines: list[str] = []
        channel_ops: list[dict[str, Any]] = []

        for child in node.children:
            if child.type == "parameter_list" and receiver is None:
                # First parameter_list is the receiver
                recv = self._parse_receiver(child, source)
                if recv:
                    receiver = recv
            elif child.type == "field_identifier":
                name = self._get_text(child, source)
            elif child.type == "type_parameter_list":
                type_params = self._parse_type_params(child, source)
            elif child.type == "parameter_list" and receiver is not None:
                params = self._parse_parameters(child, source)
            elif child.type == "result":
                results = self._parse_results(child, source)
            elif child.type == "block":
                body = self._get_text(child, source)
                defers, goroutines, channel_ops = self._analyze_body(
                    child, source
                )

        if not name:
            return None

        return GoFunction(
            name=name,
            parameters=params,
            results=results,
            type_params=type_params,
            receiver=receiver,
            body=body,
            defers=defers,
            goroutines=goroutines,
            channel_ops=channel_ops,
            line=node.start_point[0] + 1,
            column=node.start_point[1],
        )

    def _parse_receiver(
        self, node: Any, source: str
    ) -> tuple[str, str] | None:
        """Parse method receiver."""
        name = ""
        type_annotation = ""

        for child in node.children:
            if child.type == "parameter_declaration":
                for part in child.children:
                    if part.type == "identifier":
                        name = self._get_text(part, source)
                    elif part.type in (
                        "type_identifier",
                        "pointer_type",
                    ):
                        type_annotation = self._get_text(part, source)

        if type_annotation:
            return (name, type_annotation)
        return None

    def _analyze_body(
        self, node: Any, source: str
    ) -> tuple[list[str], list[str], list[dict[str, Any]]]:
        """Analyze function body for defer, goroutine, and channel operations."""
        defers: list[str] = []
        goroutines: list[str] = []
        channel_ops: list[dict[str, Any]] = []

        self._walk_body(node, source, defers, goroutines, channel_ops)

        return defers, goroutines, channel_ops

    def _walk_body(
        self,
        node: Any,
        source: str,
        defers: list[str],
        goroutines: list[str],
        channel_ops: list[dict[str, Any]],
    ) -> None:
        """Walk the body looking for specific constructs."""
        if node.type == "defer_statement":
            defers.append(self._get_text(node, source))
        elif node.type == "go_statement":
            goroutines.append(self._get_text(node, source))
        elif node.type == "send_statement":
            channel_ops.append(
                {
                    "type": "send",
                    "text": self._get_text(node, source),
                    "line": node.start_point[0] + 1,
                }
            )
        elif node.type == "receive_statement":
            channel_ops.append(
                {
                    "type": "receive",
                    "text": self._get_text(node, source),
                    "line": node.start_point[0] + 1,
                }
            )
        elif node.type == "unary_expression":
            # Check for channel receive expression <-ch
            for child in node.children:
                if child.type == "<-":
                    channel_ops.append(
                        {
                            "type": "receive",
                            "text": self._get_text(node, source),
                            "line": node.start_point[0] + 1,
                        }
                    )
                    break

        for child in node.children:
            self._walk_body(child, source, defers, goroutines, channel_ops)

    def _extract_constants(
        self, root: Any, source: str
    ) -> list[GoConst]:
        """Extract constant declarations."""
        constants = []

        for node in root.children:
            if node.type == "const_declaration":
                constants.extend(self._parse_const_decl(node, source))

        return constants

    def _parse_const_decl(
        self, node: Any, source: str
    ) -> list[GoConst]:
        """Parse a const declaration."""
        constants = []
        iota_counter = 0

        for child in node.children:
            if child.type == "const_spec":
                const = self._parse_const_spec(child, source, iota_counter)
                if const:
                    constants.append(const)
                    iota_counter += 1

        return constants

    def _parse_const_spec(
        self, node: Any, source: str, iota_value: int
    ) -> GoConst | None:
        """Parse a single const spec."""
        name = ""
        type_annotation = None
        value = ""
        uses_iota = False

        for child in node.children:
            if child.type == "identifier":
                name = self._get_text(child, source)
            elif child.type in (
                "type_identifier",
                "pointer_type",
                "slice_type",
            ):
                type_annotation = self._get_text(child, source)
            elif child.type == "expression_list":
                value = self._get_text(child, source)
                if "iota" in value:
                    uses_iota = True

        if not name:
            return None

        return GoConst(
            name=name,
            type_annotation=type_annotation,
            value=value,
            iota=uses_iota,
            line=node.start_point[0] + 1,
            column=node.start_point[1],
        )

    def _extract_variables(
        self, root: Any, source: str
    ) -> list[GoVar]:
        """Extract variable declarations."""
        variables = []

        for node in root.children:
            if node.type == "var_declaration":
                variables.extend(self._parse_var_decl(node, source))

        return variables

    def _parse_var_decl(self, node: Any, source: str) -> list[GoVar]:
        """Parse a var declaration."""
        variables = []

        for child in node.children:
            if child.type == "var_spec":
                vars_ = self._parse_var_spec(child, source)
                variables.extend(vars_)

        return variables

    def _parse_var_spec(self, node: Any, source: str) -> list[GoVar]:
        """Parse a single var spec."""
        variables = []
        names: list[str] = []
        type_annotation = None
        value = None

        for child in node.children:
            if child.type == "identifier":
                names.append(self._get_text(child, source))
            elif child.type in (
                "type_identifier",
                "pointer_type",
                "slice_type",
                "array_type",
                "map_type",
                "channel_type",
            ):
                type_annotation = self._get_text(child, source)
            elif child.type == "expression_list":
                value = self._get_text(child, source)

        for name in names:
            variables.append(
                GoVar(
                    name=name,
                    type_annotation=type_annotation,
                    value=value,
                    line=node.start_point[0] + 1,
                    column=node.start_point[1],
                )
            )

        return variables

    def _associate_methods(self, result: dict[str, Any]) -> None:
        """Associate methods with their receiver types."""
        struct_map: dict[str, GoStruct] = {}

        for struct in result["structs"]:
            struct_map[struct.name] = struct
            # Also handle pointer receivers
            struct_map[f"*{struct.name}"] = struct

        for func in result["functions"]:
            if func.receiver:
                recv_name, recv_type = func.receiver
                # Strip pointer for matching
                base_type = recv_type.lstrip("*")
                if base_type in struct_map:
                    method = GoMethod(
                        name=func.name,
                        parameters=func.parameters,
                        results=func.results,
                        type_params=func.type_params,
                        receiver=func.receiver,
                        line=func.line,
                        column=func.column,
                    )
                    struct_map[base_type].methods.append(method)
