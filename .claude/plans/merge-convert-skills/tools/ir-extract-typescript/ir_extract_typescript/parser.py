"""Tree-sitter based TypeScript parser.

Provides a high-level interface for parsing TypeScript source code
and extracting structured information about types, functions, and modules.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class TypeKind(str, Enum):
    """Kind of TypeScript type definition."""

    INTERFACE = "interface"
    TYPE_ALIAS = "type_alias"
    CLASS = "class"
    ENUM = "enum"
    FUNCTION = "function"
    VARIABLE = "variable"
    NAMESPACE = "namespace"
    MODULE = "module"


class Visibility(str, Enum):
    """TypeScript visibility modifier."""

    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"


@dataclass
class TSTypeParameter:
    """TypeScript generic type parameter."""

    name: str
    constraint: str | None = None  # extends X
    default: str | None = None  # = T
    variance: str | None = None  # in, out, in out


@dataclass
class TSProperty:
    """TypeScript interface/class property."""

    name: str
    type_annotation: str | None
    optional: bool = False
    readonly: bool = False
    visibility: Visibility = Visibility.PUBLIC
    static: bool = False
    computed: bool = False  # [key: string]: T


@dataclass
class TSMethod:
    """TypeScript interface/class method."""

    name: str
    parameters: list[TSParameter] = field(default_factory=list)
    return_type: str | None = None
    type_params: list[TSTypeParameter] = field(default_factory=list)
    visibility: Visibility = Visibility.PUBLIC
    static: bool = False
    async_: bool = False
    generator: bool = False
    abstract: bool = False


@dataclass
class TSParameter:
    """TypeScript function parameter."""

    name: str
    type_annotation: str | None = None
    optional: bool = False
    rest: bool = False  # ...args
    default_value: str | None = None


@dataclass
class TSInterface:
    """TypeScript interface definition."""

    name: str
    type_params: list[TSTypeParameter] = field(default_factory=list)
    extends: list[str] = field(default_factory=list)
    properties: list[TSProperty] = field(default_factory=list)
    methods: list[TSMethod] = field(default_factory=list)
    index_signatures: list[tuple[str, str]] = field(default_factory=list)
    call_signatures: list[TSMethod] = field(default_factory=list)
    exported: bool = False
    declared: bool = False  # declare interface
    line: int = 0
    column: int = 0


@dataclass
class TSTypeAlias:
    """TypeScript type alias definition."""

    name: str
    type_params: list[TSTypeParameter] = field(default_factory=list)
    type_value: str = ""
    exported: bool = False
    declared: bool = False
    line: int = 0
    column: int = 0


@dataclass
class TSEnumMember:
    """TypeScript enum member."""

    name: str
    value: str | None = None  # string or numeric literal


@dataclass
class TSEnum:
    """TypeScript enum definition."""

    name: str
    members: list[TSEnumMember] = field(default_factory=list)
    const: bool = False  # const enum
    exported: bool = False
    declared: bool = False
    line: int = 0
    column: int = 0


@dataclass
class TSClass:
    """TypeScript class definition."""

    name: str
    type_params: list[TSTypeParameter] = field(default_factory=list)
    extends: str | None = None
    implements: list[str] = field(default_factory=list)
    properties: list[TSProperty] = field(default_factory=list)
    methods: list[TSMethod] = field(default_factory=list)
    constructor: TSMethod | None = None
    decorators: list[str] = field(default_factory=list)
    abstract: bool = False
    exported: bool = False
    declared: bool = False
    line: int = 0
    column: int = 0


@dataclass
class TSFunction:
    """TypeScript function definition."""

    name: str
    parameters: list[TSParameter] = field(default_factory=list)
    return_type: str | None = None
    type_params: list[TSTypeParameter] = field(default_factory=list)
    async_: bool = False
    generator: bool = False
    exported: bool = False
    declared: bool = False
    arrow: bool = False
    line: int = 0
    column: int = 0


@dataclass
class TSImport:
    """TypeScript import statement."""

    module_path: str
    default_import: str | None = None
    named_imports: list[tuple[str, str | None]] = field(
        default_factory=list
    )  # (name, alias)
    namespace_import: str | None = None  # import * as X
    type_only: bool = False  # import type
    line: int = 0


@dataclass
class TSExport:
    """TypeScript export statement."""

    names: list[str] = field(default_factory=list)
    from_module: str | None = None
    default: bool = False
    type_only: bool = False
    line: int = 0


class TypeScriptParser:
    """Tree-sitter based TypeScript parser."""

    def __init__(self) -> None:
        """Initialize the parser with tree-sitter."""
        self._parser: Any = None
        self._language: Any = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization of tree-sitter."""
        if self._initialized:
            return

        try:
            import tree_sitter as ts
            from tree_sitter_language_pack import get_language

            self._language = get_language("typescript")
            self._parser = ts.Parser(self._language)
            self._initialized = True
        except ImportError as e:
            raise ImportError(
                "tree-sitter and tree-sitter-language-pack are required. "
                "Install with: pip install tree-sitter tree-sitter-language-pack"
            ) from e

    def parse(self, source: str) -> dict[str, Any]:
        """Parse TypeScript source and return structured data.

        Args:
            source: TypeScript source code

        Returns:
            Dictionary with parsed information
        """
        self._ensure_initialized()

        tree = self._parser.parse(source.encode("utf-8"))
        root = tree.root_node

        result: dict[str, Any] = {
            "interfaces": [],
            "type_aliases": [],
            "enums": [],
            "classes": [],
            "functions": [],
            "imports": [],
            "exports": [],
            "variables": [],
            "errors": [],
        }

        # Check for parse errors
        if root.has_error:
            for child in self._walk_tree(root):
                if child.is_error or child.is_missing:
                    result["errors"].append(
                        {
                            "type": "parse_error",
                            "line": child.start_point[0] + 1,
                            "column": child.start_point[1],
                            "message": f"Parse error at {child.type}",
                        }
                    )

        # Extract declarations
        for child in root.children:
            self._extract_declaration(child, source, result)

        return result

    def _walk_tree(self, node: Any) -> Any:
        """Walk tree nodes recursively."""
        yield node
        for child in node.children:
            yield from self._walk_tree(child)

    def _get_text(self, node: Any, source: str) -> str:
        """Get text content of a node."""
        return source[node.start_byte : node.end_byte]

    def _extract_declaration(
        self, node: Any, source: str, result: dict[str, Any]
    ) -> None:
        """Extract a top-level declaration."""
        node_type = node.type

        # Handle export statements
        if node_type == "export_statement":
            self._extract_export(node, source, result)
        elif node_type == "import_statement":
            result["imports"].append(self._parse_import(node, source))
        elif node_type == "interface_declaration":
            result["interfaces"].append(
                self._parse_interface(node, source, exported=False)
            )
        elif node_type == "type_alias_declaration":
            result["type_aliases"].append(
                self._parse_type_alias(node, source, exported=False)
            )
        elif node_type == "enum_declaration":
            result["enums"].append(self._parse_enum(node, source, exported=False))
        elif node_type == "class_declaration":
            result["classes"].append(self._parse_class(node, source, exported=False))
        elif node_type == "function_declaration":
            result["functions"].append(
                self._parse_function(node, source, exported=False)
            )
        elif node_type == "lexical_declaration":
            self._extract_variables(node, source, result, exported=False)
        elif node_type == "ambient_declaration":
            # declare module, declare namespace, etc.
            self._extract_ambient(node, source, result)

    def _extract_export(
        self, node: Any, source: str, result: dict[str, Any]
    ) -> None:
        """Extract exported declaration."""
        # Check for export default
        is_default = any(
            child.type == "default" for child in node.children
        )
        is_type_export = any(
            child.type == "type" for child in node.children
        )

        for child in node.children:
            if child.type == "interface_declaration":
                iface = self._parse_interface(child, source, exported=True)
                result["interfaces"].append(iface)
            elif child.type == "type_alias_declaration":
                alias = self._parse_type_alias(child, source, exported=True)
                result["type_aliases"].append(alias)
            elif child.type == "enum_declaration":
                enum = self._parse_enum(child, source, exported=True)
                result["enums"].append(enum)
            elif child.type == "class_declaration":
                cls = self._parse_class(child, source, exported=True)
                result["classes"].append(cls)
            elif child.type == "function_declaration":
                func = self._parse_function(child, source, exported=True)
                result["functions"].append(func)
            elif child.type == "lexical_declaration":
                self._extract_variables(child, source, result, exported=True)
            elif child.type == "export_clause":
                export = TSExport(
                    type_only=is_type_export,
                    default=is_default,
                    line=node.start_point[0] + 1,
                )
                for spec in child.children:
                    if spec.type == "export_specifier":
                        name = self._get_export_specifier_name(spec, source)
                        if name:
                            export.names.append(name)
                result["exports"].append(export)

    def _get_export_specifier_name(self, node: Any, source: str) -> str | None:
        """Get name from export specifier."""
        for child in node.children:
            if child.type == "identifier":
                return self._get_text(child, source)
        return None

    def _parse_import(self, node: Any, source: str) -> TSImport:
        """Parse an import statement."""
        import_obj = TSImport(
            module_path="",
            line=node.start_point[0] + 1,
        )

        for child in node.children:
            if child.type == "type":
                import_obj.type_only = True
            elif child.type == "import_clause":
                self._parse_import_clause(child, source, import_obj)
            elif child.type == "string":
                # Remove quotes
                import_obj.module_path = self._get_text(child, source).strip("\"'")

        return import_obj

    def _parse_import_clause(
        self, node: Any, source: str, import_obj: TSImport
    ) -> None:
        """Parse import clause (the part after 'import')."""
        for child in node.children:
            if child.type == "identifier":
                import_obj.default_import = self._get_text(child, source)
            elif child.type == "namespace_import":
                for c in child.children:
                    if c.type == "identifier":
                        import_obj.namespace_import = self._get_text(c, source)
            elif child.type == "named_imports":
                for spec in child.children:
                    if spec.type == "import_specifier":
                        name, alias = self._parse_import_specifier(spec, source)
                        import_obj.named_imports.append((name, alias))

    def _parse_import_specifier(
        self, node: Any, source: str
    ) -> tuple[str, str | None]:
        """Parse import specifier to get name and optional alias."""
        identifiers = [
            self._get_text(c, source)
            for c in node.children
            if c.type == "identifier"
        ]
        if len(identifiers) == 2:
            return identifiers[0], identifiers[1]
        elif len(identifiers) == 1:
            return identifiers[0], None
        return "", None

    def _parse_interface(
        self, node: Any, source: str, exported: bool
    ) -> TSInterface:
        """Parse an interface declaration."""
        iface = TSInterface(
            name="",
            exported=exported,
            line=node.start_point[0] + 1,
            column=node.start_point[1],
        )

        for child in node.children:
            if child.type == "type_identifier":
                iface.name = self._get_text(child, source)
            elif child.type == "type_parameters":
                iface.type_params = self._parse_type_parameters(child, source)
            elif child.type == "extends_type_clause":
                iface.extends = self._parse_extends_clause(child, source)
            elif child.type == "object_type":
                self._parse_object_type(child, source, iface)

        return iface

    def _parse_type_parameters(
        self, node: Any, source: str
    ) -> list[TSTypeParameter]:
        """Parse type parameters (generics)."""
        params = []
        for child in node.children:
            if child.type == "type_parameter":
                param = self._parse_type_parameter(child, source)
                params.append(param)
        return params

    def _parse_type_parameter(self, node: Any, source: str) -> TSTypeParameter:
        """Parse a single type parameter."""
        param = TSTypeParameter(name="")

        for child in node.children:
            if child.type == "type_identifier":
                param.name = self._get_text(child, source)
            elif child.type == "constraint":
                # extends clause
                for c in child.children:
                    if c.type != "extends":
                        param.constraint = self._get_text(c, source)
            elif child.type == "default_type":
                for c in child.children:
                    if c.type != "=":
                        param.default = self._get_text(c, source)

        return param

    def _parse_extends_clause(self, node: Any, source: str) -> list[str]:
        """Parse extends clause for interfaces."""
        extends = []
        for child in node.children:
            if child.type not in {"extends", ","}:
                extends.append(self._get_text(child, source))
        return extends

    def _parse_object_type(
        self, node: Any, source: str, iface: TSInterface
    ) -> None:
        """Parse object type body (interface properties and methods)."""
        for child in node.children:
            if child.type == "property_signature":
                prop = self._parse_property_signature(child, source)
                iface.properties.append(prop)
            elif child.type == "method_signature":
                method = self._parse_method_signature(child, source)
                iface.methods.append(method)
            elif child.type == "index_signature":
                sig = self._parse_index_signature(child, source)
                if sig:
                    iface.index_signatures.append(sig)
            elif child.type == "call_signature":
                call = self._parse_call_signature(child, source)
                iface.call_signatures.append(call)

    def _parse_property_signature(self, node: Any, source: str) -> TSProperty:
        """Parse a property signature."""
        prop = TSProperty(name="", type_annotation=None)

        for child in node.children:
            if child.type == "property_identifier":
                prop.name = self._get_text(child, source)
            elif child.type == "type_annotation":
                prop.type_annotation = self._get_type_annotation(child, source)
            elif child.type == "?":
                prop.optional = True
            elif child.type == "readonly":
                prop.readonly = True

        return prop

    def _parse_method_signature(self, node: Any, source: str) -> TSMethod:
        """Parse a method signature."""
        method = TSMethod(name="")

        for child in node.children:
            if child.type == "property_identifier":
                method.name = self._get_text(child, source)
            elif child.type == "type_parameters":
                method.type_params = self._parse_type_parameters(child, source)
            elif child.type == "formal_parameters":
                method.parameters = self._parse_formal_parameters(child, source)
            elif child.type == "type_annotation":
                method.return_type = self._get_type_annotation(child, source)

        return method

    def _parse_index_signature(
        self, node: Any, source: str
    ) -> tuple[str, str] | None:
        """Parse an index signature [key: type]: value."""
        key_type = None
        value_type = None

        for child in node.children:
            if child.type == "index_signature_parameter":
                for c in child.children:
                    if c.type == "type_annotation":
                        key_type = self._get_type_annotation(c, source)
            elif child.type == "type_annotation":
                value_type = self._get_type_annotation(child, source)

        if key_type and value_type:
            return (key_type, value_type)
        return None

    def _parse_call_signature(self, node: Any, source: str) -> TSMethod:
        """Parse a call signature."""
        method = TSMethod(name="__call__")

        for child in node.children:
            if child.type == "type_parameters":
                method.type_params = self._parse_type_parameters(child, source)
            elif child.type == "formal_parameters":
                method.parameters = self._parse_formal_parameters(child, source)
            elif child.type == "type_annotation":
                method.return_type = self._get_type_annotation(child, source)

        return method

    def _get_type_annotation(self, node: Any, source: str) -> str:
        """Extract type annotation text."""
        # Skip the colon
        for child in node.children:
            if child.type != ":":
                return self._get_text(child, source)
        return ""

    def _parse_formal_parameters(
        self, node: Any, source: str
    ) -> list[TSParameter]:
        """Parse formal parameters."""
        params = []
        for child in node.children:
            if child.type in {
                "required_parameter",
                "optional_parameter",
                "rest_parameter",
            }:
                param = self._parse_parameter(child, source)
                params.append(param)
        return params

    def _parse_parameter(self, node: Any, source: str) -> TSParameter:
        """Parse a single parameter."""
        param = TSParameter(name="")

        for child in node.children:
            if child.type == "identifier":
                param.name = self._get_text(child, source)
            elif child.type == "type_annotation":
                param.type_annotation = self._get_type_annotation(child, source)
            elif child.type == "?":
                param.optional = True
            elif child.type == "...":
                param.rest = True

        if node.type == "optional_parameter":
            param.optional = True
        elif node.type == "rest_parameter":
            param.rest = True

        return param

    def _parse_type_alias(
        self, node: Any, source: str, exported: bool
    ) -> TSTypeAlias:
        """Parse a type alias declaration."""
        alias = TSTypeAlias(
            name="",
            exported=exported,
            line=node.start_point[0] + 1,
            column=node.start_point[1],
        )

        for child in node.children:
            if child.type == "type_identifier":
                alias.name = self._get_text(child, source)
            elif child.type == "type_parameters":
                alias.type_params = self._parse_type_parameters(child, source)
            elif child.type not in {"type", "=", "type_identifier", "type_parameters"}:
                # The type value
                alias.type_value = self._get_text(child, source)

        return alias

    def _parse_enum(self, node: Any, source: str, exported: bool) -> TSEnum:
        """Parse an enum declaration."""
        enum = TSEnum(
            name="",
            exported=exported,
            line=node.start_point[0] + 1,
            column=node.start_point[1],
        )

        for child in node.children:
            if child.type == "const":
                enum.const = True
            elif child.type == "type_identifier":
                enum.name = self._get_text(child, source)
            elif child.type == "enum_body":
                enum.members = self._parse_enum_body(child, source)

        return enum

    def _parse_enum_body(self, node: Any, source: str) -> list[TSEnumMember]:
        """Parse enum body."""
        members = []
        for child in node.children:
            if child.type == "enum_assignment":
                name = None
                value = None
                for c in child.children:
                    if c.type == "property_identifier":
                        name = self._get_text(c, source)
                    elif c.type not in {"=", ","}:
                        value = self._get_text(c, source)
                if name:
                    members.append(TSEnumMember(name=name, value=value))
            elif child.type == "property_identifier":
                members.append(TSEnumMember(name=self._get_text(child, source)))
        return members

    def _parse_class(self, node: Any, source: str, exported: bool) -> TSClass:
        """Parse a class declaration."""
        cls = TSClass(
            name="",
            exported=exported,
            line=node.start_point[0] + 1,
            column=node.start_point[1],
        )

        for child in node.children:
            if child.type == "abstract":
                cls.abstract = True
            elif child.type == "type_identifier":
                cls.name = self._get_text(child, source)
            elif child.type == "type_parameters":
                cls.type_params = self._parse_type_parameters(child, source)
            elif child.type == "class_heritage":
                self._parse_class_heritage(child, source, cls)
            elif child.type == "class_body":
                self._parse_class_body(child, source, cls)
            elif child.type == "decorator":
                cls.decorators.append(self._get_text(child, source))

        return cls

    def _parse_class_heritage(
        self, node: Any, source: str, cls: TSClass
    ) -> None:
        """Parse class heritage (extends, implements)."""
        for child in node.children:
            if child.type == "extends_clause":
                for c in child.children:
                    if c.type not in {"extends", ","}:
                        cls.extends = self._get_text(c, source)
                        break
            elif child.type == "implements_clause":
                for c in child.children:
                    if c.type not in {"implements", ","}:
                        cls.implements.append(self._get_text(c, source))

    def _parse_class_body(self, node: Any, source: str, cls: TSClass) -> None:
        """Parse class body (properties and methods)."""
        for child in node.children:
            if child.type == "public_field_definition":
                prop = self._parse_class_property(child, source)
                cls.properties.append(prop)
            elif child.type == "method_definition":
                method = self._parse_class_method(child, source)
                if method.name == "constructor":
                    cls.constructor = method
                else:
                    cls.methods.append(method)

    def _parse_class_property(self, node: Any, source: str) -> TSProperty:
        """Parse a class property."""
        prop = TSProperty(name="", type_annotation=None)

        for child in node.children:
            if child.type == "property_identifier":
                prop.name = self._get_text(child, source)
            elif child.type == "type_annotation":
                prop.type_annotation = self._get_type_annotation(child, source)
            elif child.type in {"public", "private", "protected"}:
                prop.visibility = Visibility(child.type)
            elif child.type == "readonly":
                prop.readonly = True
            elif child.type == "static":
                prop.static = True

        return prop

    def _parse_class_method(self, node: Any, source: str) -> TSMethod:
        """Parse a class method."""
        method = TSMethod(name="")

        for child in node.children:
            if child.type == "property_identifier":
                method.name = self._get_text(child, source)
            elif child.type == "type_parameters":
                method.type_params = self._parse_type_parameters(child, source)
            elif child.type == "formal_parameters":
                method.parameters = self._parse_formal_parameters(child, source)
            elif child.type == "type_annotation":
                method.return_type = self._get_type_annotation(child, source)
            elif child.type in {"public", "private", "protected"}:
                method.visibility = Visibility(child.type)
            elif child.type == "static":
                method.static = True
            elif child.type == "async":
                method.async_ = True
            elif child.type == "abstract":
                method.abstract = True

        return method

    def _parse_function(
        self, node: Any, source: str, exported: bool
    ) -> TSFunction:
        """Parse a function declaration."""
        func = TSFunction(
            name="",
            exported=exported,
            line=node.start_point[0] + 1,
            column=node.start_point[1],
        )

        for child in node.children:
            if child.type == "identifier":
                func.name = self._get_text(child, source)
            elif child.type == "type_parameters":
                func.type_params = self._parse_type_parameters(child, source)
            elif child.type == "formal_parameters":
                func.parameters = self._parse_formal_parameters(child, source)
            elif child.type == "type_annotation":
                func.return_type = self._get_type_annotation(child, source)
            elif child.type == "async":
                func.async_ = True
            elif child.type == "*":
                func.generator = True

        return func

    def _extract_variables(
        self, node: Any, source: str, result: dict[str, Any], exported: bool
    ) -> None:
        """Extract variable declarations."""
        for child in node.children:
            if child.type == "variable_declarator":
                name = None
                type_ann = None
                for c in child.children:
                    if c.type == "identifier":
                        name = self._get_text(c, source)
                    elif c.type == "type_annotation":
                        type_ann = self._get_type_annotation(c, source)
                if name:
                    result["variables"].append(
                        {
                            "name": name,
                            "type": type_ann,
                            "exported": exported,
                            "line": node.start_point[0] + 1,
                        }
                    )

    def _extract_ambient(
        self, node: Any, source: str, result: dict[str, Any]
    ) -> None:
        """Extract ambient declarations (declare keyword)."""
        for child in node.children:
            if child.type == "interface_declaration":
                iface = self._parse_interface(child, source, exported=False)
                iface.declared = True
                result["interfaces"].append(iface)
            elif child.type == "type_alias_declaration":
                alias = self._parse_type_alias(child, source, exported=False)
                alias.declared = True
                result["type_aliases"].append(alias)
            elif child.type == "function_signature":
                func = TSFunction(
                    name="",
                    declared=True,
                    line=child.start_point[0] + 1,
                    column=child.start_point[1],
                )
                for c in child.children:
                    if c.type == "identifier":
                        func.name = self._get_text(c, source)
                    elif c.type == "type_parameters":
                        func.type_params = self._parse_type_parameters(c, source)
                    elif c.type == "formal_parameters":
                        func.parameters = self._parse_formal_parameters(c, source)
                    elif c.type == "type_annotation":
                        func.return_type = self._get_type_annotation(c, source)
                result["functions"].append(func)
