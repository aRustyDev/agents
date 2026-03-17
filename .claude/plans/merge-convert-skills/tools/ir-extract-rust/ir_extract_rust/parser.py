"""Rust parser using tree-sitter.

This module provides the low-level parsing infrastructure for Rust source code
using tree-sitter-rust. It handles CST traversal and extraction of syntactic
constructs that form the basis for IR generation.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ir_core.treesitter import TreeSitterAdapter, TSSourceSpan

if TYPE_CHECKING:
    from tree_sitter import Node, Tree

logger = logging.getLogger(__name__)


@dataclass
class RustFunction:
    """Parsed Rust function."""

    name: str
    visibility: str
    is_async: bool
    is_unsafe: bool
    is_const: bool
    params: list[RustParam]
    return_type: str | None
    type_params: list[RustTypeParam]
    where_clause: list[RustWhereClause] | None
    body: Node | None
    span: TSSourceSpan
    doc_comment: str | None = None


@dataclass
class RustParam:
    """Parsed Rust function parameter."""

    name: str
    type_str: str
    is_self: bool = False
    self_mutability: str | None = None  # None, "ref", "mut"
    is_mut: bool = False
    lifetime: str | None = None


@dataclass
class RustTypeParam:
    """Parsed Rust generic type parameter."""

    name: str
    bounds: list[str]
    default: str | None = None


@dataclass
class RustWhereClause:
    """Parsed Rust where clause."""

    param: str
    bounds: list[str]


@dataclass
class RustStruct:
    """Parsed Rust struct."""

    name: str
    visibility: str
    type_params: list[RustTypeParam]
    where_clause: list[RustWhereClause] | None
    fields: list[RustField]
    is_tuple_struct: bool
    span: TSSourceSpan
    doc_comment: str | None = None


@dataclass
class RustField:
    """Parsed Rust struct field."""

    name: str | None  # None for tuple structs
    type_str: str
    visibility: str
    index: int | None = None  # For tuple structs


@dataclass
class RustEnum:
    """Parsed Rust enum."""

    name: str
    visibility: str
    type_params: list[RustTypeParam]
    where_clause: list[RustWhereClause] | None
    variants: list[RustVariant]
    span: TSSourceSpan
    doc_comment: str | None = None


@dataclass
class RustVariant:
    """Parsed Rust enum variant."""

    name: str
    kind: str  # "unit", "tuple", "struct"
    fields: list[RustField]
    discriminant: int | None = None


@dataclass
class RustTrait:
    """Parsed Rust trait."""

    name: str
    visibility: str
    type_params: list[RustTypeParam]
    where_clause: list[RustWhereClause] | None
    supertraits: list[str]
    items: list[RustTraitItem]
    span: TSSourceSpan
    is_unsafe: bool = False
    doc_comment: str | None = None


@dataclass
class RustTraitItem:
    """Parsed Rust trait item (method signature or associated type)."""

    kind: str  # "method", "type", "const"
    name: str
    signature: RustFunction | None = None  # For methods
    bounds: list[str] | None = None  # For associated types
    default: str | None = None  # Default type or value


@dataclass
class RustImpl:
    """Parsed Rust impl block."""

    type_params: list[RustTypeParam]
    trait_name: str | None  # None for inherent impl
    self_type: str
    where_clause: list[RustWhereClause] | None
    items: list[RustFunction]
    span: TSSourceSpan
    is_unsafe: bool = False


@dataclass
class RustUse:
    """Parsed Rust use statement."""

    path: list[str]
    alias: str | None
    items: list[tuple[str, str | None]]  # (name, alias) pairs for use groups
    is_glob: bool
    visibility: str


@dataclass
class RustMod:
    """Parsed Rust module."""

    name: str
    visibility: str
    is_inline: bool
    items: list[Node] | None  # For inline modules
    span: TSSourceSpan


class RustParser:
    """Tree-sitter based Rust parser.

    This class handles parsing of Rust source code into structured
    representations that can be transformed into IR.

    Example:
        parser = RustParser()
        functions = list(parser.iter_functions(source, "example.rs"))
        for func in functions:
            print(f"Found function: {func.name}")
    """

    def __init__(self) -> None:
        """Initialize the Rust parser."""
        self.adapter = TreeSitterAdapter("rust")

    def parse(self, source: str) -> Tree:
        """Parse Rust source code.

        Args:
            source: Rust source code

        Returns:
            Tree-sitter tree
        """
        return self.adapter.parse(source)

    def iter_functions(
        self, source: str, path: str
    ) -> Iterator[RustFunction]:
        """Iterate over all functions in the source.

        Args:
            source: Rust source code
            path: File path for span information

        Yields:
            RustFunction for each function found
        """
        tree = self.parse(source)
        for node in self._walk_tree(tree.root):
            if node.type == "function_item":
                func = self._parse_function(node, source, path)
                if func:
                    yield func

    def iter_structs(
        self, source: str, path: str
    ) -> Iterator[RustStruct]:
        """Iterate over all structs in the source.

        Args:
            source: Rust source code
            path: File path for span information

        Yields:
            RustStruct for each struct found
        """
        tree = self.parse(source)
        for node in self._walk_tree(tree.root):
            if node.type == "struct_item":
                struct = self._parse_struct(node, source, path)
                if struct:
                    yield struct

    def iter_enums(self, source: str, path: str) -> Iterator[RustEnum]:
        """Iterate over all enums in the source.

        Args:
            source: Rust source code
            path: File path for span information

        Yields:
            RustEnum for each enum found
        """
        tree = self.parse(source)
        for node in self._walk_tree(tree.root):
            if node.type == "enum_item":
                enum = self._parse_enum(node, source, path)
                if enum:
                    yield enum

    def iter_traits(self, source: str, path: str) -> Iterator[RustTrait]:
        """Iterate over all traits in the source.

        Args:
            source: Rust source code
            path: File path for span information

        Yields:
            RustTrait for each trait found
        """
        tree = self.parse(source)
        for node in self._walk_tree(tree.root):
            if node.type == "trait_item":
                trait = self._parse_trait(node, source, path)
                if trait:
                    yield trait

    def iter_impls(self, source: str, path: str) -> Iterator[RustImpl]:
        """Iterate over all impl blocks in the source.

        Args:
            source: Rust source code
            path: File path for span information

        Yields:
            RustImpl for each impl block found
        """
        tree = self.parse(source)
        for node in self._walk_tree(tree.root):
            if node.type == "impl_item":
                impl = self._parse_impl(node, source, path)
                if impl:
                    yield impl

    def iter_uses(self, source: str) -> Iterator[RustUse]:
        """Iterate over all use statements.

        Args:
            source: Rust source code

        Yields:
            RustUse for each use statement found
        """
        tree = self.parse(source)
        for node in self._walk_tree(tree.root):
            if node.type == "use_declaration":
                use = self._parse_use(node, source)
                if use:
                    yield use

    def _walk_tree(self, node: Node) -> Iterator[Node]:
        """Walk all nodes in the tree depth-first.

        Args:
            node: Starting node

        Yields:
            Each node in the tree
        """
        yield node
        for child in node.children:
            yield from self._walk_tree(child)

    def _get_text(self, node: Node, source: str) -> str:
        """Get the text for a node.

        Args:
            node: Tree-sitter node
            source: Full source code

        Returns:
            Text of the node
        """
        return source[node.start_byte:node.end_byte]

    def _get_span(self, node: Node, path: str) -> TSSourceSpan:
        """Get the source span for a node.

        Args:
            node: Tree-sitter node
            path: File path

        Returns:
            Source span for the node
        """
        return TSSourceSpan(
            file=path,
            start_byte=node.start_byte,
            end_byte=node.end_byte,
            start_point=node.start_point,
            end_point=node.end_point,
        )

    def _find_child_by_type(
        self, node: Node, type_name: str
    ) -> Node | None:
        """Find first child with given type.

        Args:
            node: Parent node
            type_name: Type name to find

        Returns:
            First matching child or None
        """
        for child in node.children:
            if child.type == type_name:
                return child
        return None

    def _find_children_by_type(
        self, node: Node, type_name: str
    ) -> list[Node]:
        """Find all children with given type.

        Args:
            node: Parent node
            type_name: Type name to find

        Returns:
            List of matching children
        """
        return [child for child in node.children if child.type == type_name]

    def _parse_visibility(self, node: Node, source: str) -> str:
        """Parse visibility from a visibility_modifier node.

        Args:
            node: The item node (not the visibility node itself)
            source: Full source code

        Returns:
            Visibility string: "public", "private", "pub_crate", "pub_super"
        """
        vis_node = self._find_child_by_type(node, "visibility_modifier")
        if vis_node is None:
            return "private"

        text = self._get_text(vis_node, source)
        if text == "pub":
            return "public"
        elif "crate" in text:
            return "pub_crate"
        elif "super" in text:
            return "pub_super"
        elif "self" in text:
            return "pub_self"
        elif "in" in text:
            return "pub_in"
        return "public"

    def _parse_doc_comment(self, node: Node, source: str) -> str | None:
        """Parse doc comments preceding a node.

        Args:
            node: The item node
            source: Full source code

        Returns:
            Combined doc comment text or None
        """
        # Look at siblings before this node
        parent = node.parent
        if parent is None:
            return None

        doc_lines: list[str] = []
        found_node = False

        for child in parent.children:
            if child.id == node.id:
                found_node = True
                break
            if child.type in ("line_comment", "block_comment"):
                text = self._get_text(child, source)
                if text.startswith("///") or text.startswith("//!"):
                    doc_lines.append(text[3:].strip())
                elif text.startswith("/**"):
                    # Block doc comment
                    inner = text[3:-2].strip()
                    doc_lines.extend(inner.split("\n"))

        if not found_node or not doc_lines:
            return None

        return "\n".join(doc_lines)

    def _parse_type_params(
        self, node: Node, source: str
    ) -> list[RustTypeParam]:
        """Parse generic type parameters.

        Args:
            node: Node containing type_parameters
            source: Full source code

        Returns:
            List of parsed type parameters
        """
        params: list[RustTypeParam] = []
        type_params_node = self._find_child_by_type(node, "type_parameters")
        if type_params_node is None:
            return params

        for child in type_params_node.children:
            if child.type == "type_identifier":
                params.append(RustTypeParam(
                    name=self._get_text(child, source),
                    bounds=[],
                    default=None,
                ))
            elif child.type == "type_parameter":
                # type_parameter wraps the type_identifier
                name_node = self._find_child_by_type(child, "type_identifier")
                if name_node:
                    name = self._get_text(name_node, source)
                    # Check for trait bounds within the type_parameter
                    bounds = self._parse_type_bounds(child, source)
                    params.append(RustTypeParam(name=name, bounds=bounds, default=None))
            elif child.type == "constrained_type_parameter":
                name_node = self._find_child_by_type(child, "type_identifier")
                if name_node:
                    name = self._get_text(name_node, source)
                    bounds = self._parse_type_bounds(child, source)
                    params.append(RustTypeParam(name=name, bounds=bounds))
            elif child.type == "optional_type_parameter":
                name_node = self._find_child_by_type(child, "type_identifier")
                if name_node:
                    name = self._get_text(name_node, source)
                    # Find default type
                    default = None
                    eq_found = False
                    for subchild in child.children:
                        if subchild.type == "=":
                            eq_found = True
                        elif eq_found and subchild.type.endswith("_type"):
                            default = self._get_text(subchild, source)
                            break
                    params.append(RustTypeParam(
                        name=name,
                        bounds=[],
                        default=default,
                    ))
            elif child.type == "lifetime":
                # Lifetime parameters like 'a
                lifetime_name = self._get_text(child, source)
                params.append(RustTypeParam(name=lifetime_name, bounds=[]))

        return params

    def _parse_type_bounds(
        self, node: Node, source: str
    ) -> list[str]:
        """Parse trait bounds from a constrained type parameter.

        Args:
            node: Constrained type parameter node
            source: Full source code

        Returns:
            List of bound strings
        """
        bounds: list[str] = []
        bounds_node = self._find_child_by_type(node, "trait_bounds")
        if bounds_node:
            for child in bounds_node.children:
                if child.type not in ("+", ":"):
                    bounds.append(self._get_text(child, source))
        return bounds

    def _parse_where_clause(
        self, node: Node, source: str
    ) -> list[RustWhereClause] | None:
        """Parse where clause.

        Args:
            node: Node containing where_clause
            source: Full source code

        Returns:
            List of where clauses or None
        """
        where_node = self._find_child_by_type(node, "where_clause")
        if where_node is None:
            return None

        clauses: list[RustWhereClause] = []
        for child in where_node.children:
            if child.type == "where_predicate":
                param = ""
                bounds: list[str] = []
                for subchild in child.children:
                    if subchild.type in ("type_identifier", "generic_type"):
                        param = self._get_text(subchild, source)
                    elif subchild.type == "trait_bounds":
                        bounds = self._parse_type_bounds_from_bounds_node(
                            subchild, source
                        )
                if param:
                    clauses.append(RustWhereClause(param=param, bounds=bounds))

        return clauses if clauses else None

    def _parse_type_bounds_from_bounds_node(
        self, node: Node, source: str
    ) -> list[str]:
        """Parse trait bounds from a trait_bounds node.

        Args:
            node: trait_bounds node
            source: Full source code

        Returns:
            List of bound strings
        """
        bounds: list[str] = []
        for child in node.children:
            if child.type not in ("+", ":", "?"):
                bounds.append(self._get_text(child, source))
        return bounds

    def _parse_function(
        self, node: Node, source: str, path: str
    ) -> RustFunction | None:
        """Parse a function item.

        Args:
            node: function_item node
            source: Full source code
            path: File path

        Returns:
            RustFunction or None if parsing fails
        """
        try:
            visibility = self._parse_visibility(node, source)
            doc_comment = self._parse_doc_comment(node, source)

            # Check modifiers - can be direct children or inside function_modifiers
            is_async = False
            is_unsafe = False
            is_const = False
            for c in node.children:
                if c.type == "async":
                    is_async = True
                elif c.type == "unsafe":
                    is_unsafe = True
                elif c.type == "const":
                    is_const = True
                elif c.type == "function_modifiers":
                    # Check inside modifiers container
                    for mod in c.children:
                        if mod.type == "async":
                            is_async = True
                        elif mod.type == "unsafe":
                            is_unsafe = True
                        elif mod.type == "const":
                            is_const = True

            # Get name
            name_node = self._find_child_by_type(node, "identifier")
            if name_node is None:
                return None
            name = self._get_text(name_node, source)

            # Type parameters
            type_params = self._parse_type_params(node, source)

            # Parameters
            params = self._parse_function_params(node, source)

            # Return type - find the type after the -> arrow
            return_type = None
            found_arrow = False
            for child in node.children:
                if child.type == "->":
                    found_arrow = True
                elif found_arrow and child.type.endswith("_type"):
                    return_type = self._get_text(child, source)
                    break

            # Where clause
            where_clause = self._parse_where_clause(node, source)

            # Body
            body = self._find_child_by_type(node, "block")

            return RustFunction(
                name=name,
                visibility=visibility,
                is_async=is_async,
                is_unsafe=is_unsafe,
                is_const=is_const,
                params=params,
                return_type=return_type,
                type_params=type_params,
                where_clause=where_clause,
                body=body,
                span=self._get_span(node, path),
                doc_comment=doc_comment,
            )
        except Exception as e:
            logger.warning("Failed to parse function: %s", e)
            return None

    def _parse_function_params(
        self, node: Node, source: str
    ) -> list[RustParam]:
        """Parse function parameters.

        Args:
            node: function_item node
            source: Full source code

        Returns:
            List of parsed parameters
        """
        params: list[RustParam] = []
        params_node = self._find_child_by_type(node, "parameters")
        if params_node is None:
            return params

        for child in params_node.children:
            if child.type == "self_parameter":
                # self, &self, &mut self
                text = self._get_text(child, source)
                mut = None
                if "&mut self" in text:
                    mut = "mut"
                elif "&self" in text:
                    mut = "ref"
                params.append(RustParam(
                    name="self",
                    type_str="Self",
                    is_self=True,
                    self_mutability=mut,
                ))
            elif child.type == "parameter":
                param = self._parse_single_param(child, source)
                if param:
                    params.append(param)

        return params

    def _parse_single_param(
        self, node: Node, source: str
    ) -> RustParam | None:
        """Parse a single function parameter.

        Args:
            node: parameter node
            source: Full source code

        Returns:
            RustParam or None
        """
        # Check for mutable binding
        is_mut = any(c.type == "mutable_specifier" for c in node.children)

        # Get pattern (name)
        name = ""
        for child in node.children:
            if child.type == "identifier":
                name = self._get_text(child, source)
                break
            elif child.type == "mut_pattern":
                # mut x: T
                id_node = self._find_child_by_type(child, "identifier")
                if id_node:
                    name = self._get_text(id_node, source)
                is_mut = True
                break

        # Get type
        type_str = ""
        for child in node.children:
            if child.type.endswith("_type"):
                type_str = self._get_text(child, source)
                break

        # Check for lifetime in type
        lifetime = None
        if "'" in type_str:
            # Extract lifetime
            import re
            match = re.search(r"'(\w+)", type_str)
            if match:
                lifetime = match.group(1)

        if not name:
            return None

        return RustParam(
            name=name,
            type_str=type_str,
            is_mut=is_mut,
            lifetime=lifetime,
        )

    def _parse_struct(
        self, node: Node, source: str, path: str
    ) -> RustStruct | None:
        """Parse a struct item.

        Args:
            node: struct_item node
            source: Full source code
            path: File path

        Returns:
            RustStruct or None
        """
        try:
            visibility = self._parse_visibility(node, source)
            doc_comment = self._parse_doc_comment(node, source)

            # Get name
            name_node = self._find_child_by_type(node, "type_identifier")
            if name_node is None:
                return None
            name = self._get_text(name_node, source)

            # Type parameters
            type_params = self._parse_type_params(node, source)

            # Where clause
            where_clause = self._parse_where_clause(node, source)

            # Check for tuple struct vs regular struct
            ordered_list = self._find_child_by_type(
                node, "ordered_field_declaration_list"
            )
            field_list = self._find_child_by_type(
                node, "field_declaration_list"
            )

            fields: list[RustField] = []
            is_tuple_struct = ordered_list is not None

            if ordered_list:
                # Tuple struct
                for i, child in enumerate(ordered_list.children):
                    if child.type == "ordered_field_declaration":
                        vis = self._parse_visibility(child, source)
                        type_node = None
                        for subchild in child.children:
                            if subchild.type.endswith("_type"):
                                type_node = subchild
                                break
                        if type_node:
                            fields.append(RustField(
                                name=None,
                                type_str=self._get_text(type_node, source),
                                visibility=vis,
                                index=i,
                            ))
            elif field_list:
                # Regular struct
                for child in field_list.children:
                    if child.type == "field_declaration":
                        field = self._parse_struct_field(child, source)
                        if field:
                            fields.append(field)

            return RustStruct(
                name=name,
                visibility=visibility,
                type_params=type_params,
                where_clause=where_clause,
                fields=fields,
                is_tuple_struct=is_tuple_struct,
                span=self._get_span(node, path),
                doc_comment=doc_comment,
            )
        except Exception as e:
            logger.warning("Failed to parse struct: %s", e)
            return None

    def _parse_struct_field(
        self, node: Node, source: str
    ) -> RustField | None:
        """Parse a struct field.

        Args:
            node: field_declaration node
            source: Full source code

        Returns:
            RustField or None
        """
        visibility = self._parse_visibility(node, source)

        name = ""
        type_str = ""

        for child in node.children:
            if child.type == "field_identifier":
                name = self._get_text(child, source)
            elif child.type.endswith("_type"):
                type_str = self._get_text(child, source)

        if not name:
            return None

        return RustField(
            name=name,
            type_str=type_str,
            visibility=visibility,
        )

    def _parse_enum(
        self, node: Node, source: str, path: str
    ) -> RustEnum | None:
        """Parse an enum item.

        Args:
            node: enum_item node
            source: Full source code
            path: File path

        Returns:
            RustEnum or None
        """
        try:
            visibility = self._parse_visibility(node, source)
            doc_comment = self._parse_doc_comment(node, source)

            # Get name
            name_node = self._find_child_by_type(node, "type_identifier")
            if name_node is None:
                return None
            name = self._get_text(name_node, source)

            # Type parameters
            type_params = self._parse_type_params(node, source)

            # Where clause
            where_clause = self._parse_where_clause(node, source)

            # Variants
            variants: list[RustVariant] = []
            body = self._find_child_by_type(node, "enum_variant_list")
            if body:
                for child in body.children:
                    if child.type == "enum_variant":
                        variant = self._parse_enum_variant(child, source)
                        if variant:
                            variants.append(variant)

            return RustEnum(
                name=name,
                visibility=visibility,
                type_params=type_params,
                where_clause=where_clause,
                variants=variants,
                span=self._get_span(node, path),
                doc_comment=doc_comment,
            )
        except Exception as e:
            logger.warning("Failed to parse enum: %s", e)
            return None

    def _parse_enum_variant(
        self, node: Node, source: str
    ) -> RustVariant | None:
        """Parse an enum variant.

        Args:
            node: enum_variant node
            source: Full source code

        Returns:
            RustVariant or None
        """
        name = ""
        for child in node.children:
            if child.type == "identifier":
                name = self._get_text(child, source)
                break

        if not name:
            return None

        # Check variant kind
        ordered_list = self._find_child_by_type(
            node, "ordered_field_declaration_list"
        )
        field_list = self._find_child_by_type(
            node, "field_declaration_list"
        )

        fields: list[RustField] = []
        discriminant = None

        # Check for discriminant
        for child in node.children:
            if child.type == "=":
                next_idx = node.children.index(child) + 1
                if next_idx < len(node.children):
                    disc_node = node.children[next_idx]
                    try:
                        discriminant = int(self._get_text(disc_node, source))
                    except ValueError:
                        pass

        if ordered_list:
            # Tuple variant
            for i, child in enumerate(ordered_list.children):
                if child.type.endswith("_type"):
                    fields.append(RustField(
                        name=None,
                        type_str=self._get_text(child, source),
                        visibility="private",
                        index=i,
                    ))
            return RustVariant(
                name=name,
                kind="tuple",
                fields=fields,
                discriminant=discriminant,
            )
        elif field_list:
            # Struct variant
            for child in field_list.children:
                if child.type == "field_declaration":
                    field = self._parse_struct_field(child, source)
                    if field:
                        fields.append(field)
            return RustVariant(
                name=name,
                kind="struct",
                fields=fields,
                discriminant=discriminant,
            )
        else:
            # Unit variant
            return RustVariant(
                name=name,
                kind="unit",
                fields=[],
                discriminant=discriminant,
            )

    def _parse_trait(
        self, node: Node, source: str, path: str
    ) -> RustTrait | None:
        """Parse a trait item.

        Args:
            node: trait_item node
            source: Full source code
            path: File path

        Returns:
            RustTrait or None
        """
        try:
            visibility = self._parse_visibility(node, source)
            doc_comment = self._parse_doc_comment(node, source)
            is_unsafe = any(c.type == "unsafe" for c in node.children)

            # Get name
            name_node = self._find_child_by_type(node, "type_identifier")
            if name_node is None:
                return None
            name = self._get_text(name_node, source)

            # Type parameters
            type_params = self._parse_type_params(node, source)

            # Supertraits
            supertraits: list[str] = []
            bounds_node = self._find_child_by_type(node, "trait_bounds")
            if bounds_node:
                supertraits = self._parse_type_bounds_from_bounds_node(
                    bounds_node, source
                )

            # Where clause
            where_clause = self._parse_where_clause(node, source)

            # Items
            items: list[RustTraitItem] = []
            body = self._find_child_by_type(node, "declaration_list")
            if body:
                for child in body.children:
                    if child.type == "function_signature_item":
                        sig = self._parse_function_signature(child, source, path)
                        if sig:
                            items.append(RustTraitItem(
                                kind="method",
                                name=sig.name,
                                signature=sig,
                            ))
                    elif child.type == "function_item":
                        # Default implementation
                        func = self._parse_function(child, source, path)
                        if func:
                            items.append(RustTraitItem(
                                kind="method",
                                name=func.name,
                                signature=func,
                            ))
                    elif child.type == "associated_type":
                        type_item = self._parse_associated_type(child, source)
                        if type_item:
                            items.append(type_item)

            return RustTrait(
                name=name,
                visibility=visibility,
                type_params=type_params,
                where_clause=where_clause,
                supertraits=supertraits,
                items=items,
                span=self._get_span(node, path),
                is_unsafe=is_unsafe,
                doc_comment=doc_comment,
            )
        except Exception as e:
            logger.warning("Failed to parse trait: %s", e)
            return None

    def _parse_function_signature(
        self, node: Node, source: str, path: str
    ) -> RustFunction | None:
        """Parse a function signature (without body).

        Args:
            node: function_signature_item node
            source: Full source code
            path: File path

        Returns:
            RustFunction or None
        """
        # Similar to _parse_function but without body
        try:
            is_async = any(c.type == "async" for c in node.children)
            is_unsafe = any(c.type == "unsafe" for c in node.children)

            name_node = self._find_child_by_type(node, "identifier")
            if name_node is None:
                return None
            name = self._get_text(name_node, source)

            type_params = self._parse_type_params(node, source)
            params = self._parse_function_params(node, source)

            # Return type - find the type after the -> arrow
            return_type = None
            found_arrow = False
            for child in node.children:
                if child.type == "->":
                    found_arrow = True
                elif found_arrow and child.type.endswith("_type"):
                    return_type = self._get_text(child, source)
                    break

            where_clause = self._parse_where_clause(node, source)

            return RustFunction(
                name=name,
                visibility="public",  # Trait methods are public by default
                is_async=is_async,
                is_unsafe=is_unsafe,
                is_const=False,
                params=params,
                return_type=return_type,
                type_params=type_params,
                where_clause=where_clause,
                body=None,
                span=self._get_span(node, path),
            )
        except Exception as e:
            logger.warning("Failed to parse function signature: %s", e)
            return None

    def _parse_associated_type(
        self, node: Node, source: str
    ) -> RustTraitItem | None:
        """Parse an associated type.

        Args:
            node: associated_type node
            source: Full source code

        Returns:
            RustTraitItem or None
        """
        name = ""
        for child in node.children:
            if child.type == "type_identifier":
                name = self._get_text(child, source)
                break

        if not name:
            return None

        bounds: list[str] = []
        bounds_node = self._find_child_by_type(node, "trait_bounds")
        if bounds_node:
            bounds = self._parse_type_bounds_from_bounds_node(bounds_node, source)

        # Check for default
        default = None
        for i, child in enumerate(node.children):
            if child.type == "=":
                if i + 1 < len(node.children):
                    default = self._get_text(node.children[i + 1], source)

        return RustTraitItem(
            kind="type",
            name=name,
            bounds=bounds,
            default=default,
        )

    def _parse_impl(
        self, node: Node, source: str, path: str
    ) -> RustImpl | None:
        """Parse an impl block.

        Args:
            node: impl_item node
            source: Full source code
            path: File path

        Returns:
            RustImpl or None
        """
        try:
            is_unsafe = any(c.type == "unsafe" for c in node.children)
            type_params = self._parse_type_params(node, source)

            # Find trait and self type
            trait_name = None
            self_type = ""

            for_found = False
            for child in node.children:
                if child.type == "for":
                    for_found = True
                elif child.type in ("type_identifier", "generic_type") and not for_found:
                    # This might be the trait
                    trait_name = self._get_text(child, source)
                elif child.type in ("type_identifier", "generic_type") and for_found:
                    # This is the self type
                    self_type = self._get_text(child, source)
                    break

            # If no "for", this is an inherent impl
            if not for_found and trait_name:
                self_type = trait_name
                trait_name = None

            where_clause = self._parse_where_clause(node, source)

            # Items
            items: list[RustFunction] = []
            body = self._find_child_by_type(node, "declaration_list")
            if body:
                for child in body.children:
                    if child.type == "function_item":
                        func = self._parse_function(child, source, path)
                        if func:
                            items.append(func)

            return RustImpl(
                type_params=type_params,
                trait_name=trait_name,
                self_type=self_type,
                where_clause=where_clause,
                items=items,
                span=self._get_span(node, path),
                is_unsafe=is_unsafe,
            )
        except Exception as e:
            logger.warning("Failed to parse impl: %s", e)
            return None

    def _parse_use(self, node: Node, source: str) -> RustUse | None:
        """Parse a use declaration.

        Args:
            node: use_declaration node
            source: Full source code

        Returns:
            RustUse or None
        """
        try:
            visibility = self._parse_visibility(node, source)

            # Get use clause - can be various node types
            clause = self._find_child_by_type(node, "use_clause")
            if clause is None:
                clause = self._find_child_by_type(node, "scoped_use_list")
            if clause is None:
                clause = self._find_child_by_type(node, "scoped_identifier")
            if clause is None:
                clause = self._find_child_by_type(node, "use_wildcard")
            if clause is None:
                clause = self._find_child_by_type(node, "use_as_clause")
            if clause is None:
                clause = self._find_child_by_type(node, "identifier")

            if clause is None:
                return None

            path, alias, items, is_glob = self._parse_use_clause(clause, source)

            return RustUse(
                path=path,
                alias=alias,
                items=items,
                is_glob=is_glob,
                visibility=visibility,
            )
        except Exception as e:
            logger.warning("Failed to parse use: %s", e)
            return None

    def _parse_use_clause(
        self, node: Node, source: str
    ) -> tuple[list[str], str | None, list[tuple[str, str | None]], bool]:
        """Parse a use clause.

        Returns:
            (path, alias, items, is_glob)
        """
        if node.type == "scoped_identifier":
            # use foo::bar
            text = self._get_text(node, source)
            path = text.split("::")
            return path, None, [], False

        elif node.type == "use_wildcard":
            # use foo::*
            text = self._get_text(node, source)
            path = text.rstrip("::*").split("::")
            return path, None, [], True

        elif node.type == "use_as_clause":
            # use foo::bar as baz
            path_parts: list[str] = []
            alias = None
            for child in node.children:
                if child.type == "scoped_identifier":
                    path_parts = self._get_text(child, source).split("::")
                elif child.type == "identifier":
                    if path_parts:  # This is the alias
                        alias = self._get_text(child, source)
                    else:  # Simple identifier
                        path_parts = [self._get_text(child, source)]
            return path_parts, alias, [], False

        elif node.type == "scoped_use_list":
            # use foo::{bar, baz}
            path_parts: list[str] = []
            items: list[tuple[str, str | None]] = []

            for child in node.children:
                if child.type == "scoped_identifier":
                    path_parts = self._get_text(child, source).split("::")
                elif child.type == "identifier":
                    path_parts = [self._get_text(child, source)]
                elif child.type == "use_list":
                    for item in child.children:
                        if item.type == "identifier":
                            items.append((self._get_text(item, source), None))
                        elif item.type == "use_as_clause":
                            name = ""
                            alias = None
                            for sub in item.children:
                                if sub.type == "identifier":
                                    if not name:
                                        name = self._get_text(sub, source)
                                    else:
                                        alias = self._get_text(sub, source)
                            if name:
                                items.append((name, alias))

            return path_parts, None, items, False

        elif node.type == "identifier":
            # Simple use foo
            return [self._get_text(node, source)], None, [], False

        else:
            # Try to get text and split
            text = self._get_text(node, source)
            return text.split("::"), None, [], False
