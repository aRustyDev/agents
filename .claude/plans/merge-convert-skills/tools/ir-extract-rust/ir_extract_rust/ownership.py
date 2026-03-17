"""Ownership analysis for Rust code.

This module provides analysis of ownership semantics in Rust code,
tracking owned values, borrows (shared and mutable), moves, and copies.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tree_sitter import Node

logger = logging.getLogger(__name__)


class OwnershipKind(str, Enum):
    """Ownership classification for values."""

    OWNED = "owned"  # T - takes ownership
    BORROWED = "borrowed"  # &T - shared borrow
    MUT_BORROWED = "mut_borrowed"  # &mut T - exclusive borrow
    MOVED = "moved"  # value has been moved
    COPIED = "copied"  # value implements Copy


class UsageKind(str, Enum):
    """How a value is used in an expression."""

    READ = "read"  # value is read
    MUTATED = "mutated"  # value is mutated
    CONSUMED = "consumed"  # value is consumed/moved
    BORROWED = "borrowed"  # value is borrowed
    MUT_BORROWED = "mut_borrowed"  # value is mutably borrowed


@dataclass
class OwnershipInfo:
    """Ownership information for a binding.

    Attributes:
        name: Variable name
        kind: Current ownership state
        type_str: Type of the binding
        is_copy: Whether the type implements Copy
        borrows: Active borrows of this value
        moved_at: Location where value was moved (if moved)
        scope_depth: Lexical scope depth
    """

    name: str
    kind: OwnershipKind
    type_str: str
    is_copy: bool = False
    borrows: list[BorrowInfo] = field(default_factory=list)
    moved_at: str | None = None
    scope_depth: int = 0


@dataclass
class BorrowInfo:
    """Information about an active borrow.

    Attributes:
        borrower: Name of the borrowing binding
        kind: Borrow kind (shared or mutable)
        location: Source location of the borrow
        scope_depth: Scope depth where borrow starts
    """

    borrower: str
    kind: OwnershipKind  # BORROWED or MUT_BORROWED
    location: str
    scope_depth: int


@dataclass
class UsageInfo:
    """Information about a value usage.

    Attributes:
        binding: Name of the binding
        kind: How the value is used
        location: Source location
        consumes: Whether this usage consumes the value
    """

    binding: str
    kind: UsageKind
    location: str
    consumes: bool = False


@dataclass
class OwnershipAnalysis:
    """Results of ownership analysis.

    Attributes:
        bindings: Ownership info for each binding
        usages: List of value usages
        borrow_errors: Detected borrow checker violations
        move_errors: Detected use-after-move errors
    """

    bindings: dict[str, OwnershipInfo] = field(default_factory=dict)
    usages: list[UsageInfo] = field(default_factory=list)
    borrow_errors: list[str] = field(default_factory=list)
    move_errors: list[str] = field(default_factory=list)


# Types that implement Copy by default
COPY_TYPES = frozenset({
    "i8", "i16", "i32", "i64", "i128", "isize",
    "u8", "u16", "u32", "u64", "u128", "usize",
    "f32", "f64",
    "bool", "char",
    "()",  # unit
})


class OwnershipAnalyzer:
    """Analyze ownership semantics in Rust code.

    This analyzer tracks:
    - Owned values and their lifetimes
    - Borrows (shared and mutable)
    - Move operations
    - Copy semantics

    Example:
        analyzer = OwnershipAnalyzer()
        analysis = analyzer.analyze(source)
        for binding, info in analysis.bindings.items():
            print(f"{binding}: {info.kind}")
    """

    def __init__(self) -> None:
        """Initialize the ownership analyzer."""
        self.analysis = OwnershipAnalysis()
        self.scope_depth = 0

    def analyze(self, source: str, tree: Node) -> OwnershipAnalysis:
        """Analyze ownership in the source code.

        Args:
            source: Rust source code
            tree: Tree-sitter AST

        Returns:
            Ownership analysis results
        """
        self.analysis = OwnershipAnalysis()
        self.scope_depth = 0
        self._analyze_node(tree, source)
        return self.analysis

    def _analyze_node(self, node: Node, source: str) -> None:
        """Recursively analyze a node.

        Args:
            node: Tree-sitter node
            source: Full source code
        """
        # Track scope depth
        if node.type in ("block", "function_item", "impl_item"):
            self.scope_depth += 1
            for child in node.children:
                self._analyze_node(child, source)
            self.scope_depth -= 1
            self._end_scope()
            return

        # Analyze let bindings
        if node.type == "let_declaration":
            self._analyze_let(node, source)

        # Analyze assignments
        elif node.type == "assignment_expression":
            self._analyze_assignment(node, source)

        # Analyze function calls (may move/borrow arguments)
        elif node.type == "call_expression":
            self._analyze_call(node, source)

        # Analyze method calls
        elif node.type == "method_call_expression":
            self._analyze_method_call(node, source)

        # Analyze references
        elif node.type == "reference_expression":
            self._analyze_reference(node, source)

        # Recurse into children
        for child in node.children:
            self._analyze_node(child, source)

    def _get_text(self, node: Node, source: str) -> str:
        """Get text for a node."""
        return source[node.start_byte:node.end_byte]

    def _analyze_let(self, node: Node, source: str) -> None:
        """Analyze a let declaration.

        Args:
            node: let_declaration node
            source: Full source code
        """
        # Find pattern (name)
        name = ""
        is_mut = False
        type_str = ""
        has_value = False

        for child in node.children:
            if child.type == "mutable_specifier":
                is_mut = True
            elif child.type == "identifier":
                name = self._get_text(child, source)
            elif child.type == "mut_pattern":
                is_mut = True
                for sub in child.children:
                    if sub.type == "identifier":
                        name = self._get_text(sub, source)
            elif child.type.endswith("_type"):
                type_str = self._get_text(child, source)
            elif child.type == "=":
                has_value = True

        if not name:
            return

        # Determine ownership kind from type
        kind = OwnershipKind.OWNED
        is_copy = self._is_copy_type(type_str)

        # Check if initialized from a borrow
        for child in node.children:
            if child.type == "reference_expression":
                kind = OwnershipKind.BORROWED
                if any(c.type == "mutable_specifier" for c in child.children):
                    kind = OwnershipKind.MUT_BORROWED
                break

        self.analysis.bindings[name] = OwnershipInfo(
            name=name,
            kind=kind,
            type_str=type_str,
            is_copy=is_copy,
            scope_depth=self.scope_depth,
        )

        # If initialized from another binding, track the move/borrow
        if has_value:
            self._analyze_value_expr(node, source, name)

    def _analyze_value_expr(
        self, node: Node, source: str, target: str
    ) -> None:
        """Analyze the value expression in a binding.

        Args:
            node: Node containing the value
            source: Full source code
            target: Name of the target binding
        """
        # Find the value expression (after =)
        found_eq = False
        for child in node.children:
            if child.type == "=":
                found_eq = True
            elif found_eq:
                self._process_value_source(child, source, target)
                break

    def _process_value_source(
        self, node: Node, source: str, target: str
    ) -> None:
        """Process a value source expression.

        Args:
            node: Value expression node
            source: Full source code
            target: Target binding name
        """
        if node.type == "identifier":
            source_name = self._get_text(node, source)
            if source_name in self.analysis.bindings:
                info = self.analysis.bindings[source_name]
                if info.is_copy:
                    # Copy - original still valid
                    self.analysis.usages.append(UsageInfo(
                        binding=source_name,
                        kind=UsageKind.READ,
                        location=f"{node.start_point[0]}:{node.start_point[1]}",
                    ))
                else:
                    # Move - original is now invalid
                    info.kind = OwnershipKind.MOVED
                    info.moved_at = f"{node.start_point[0]}:{node.start_point[1]}"
                    self.analysis.usages.append(UsageInfo(
                        binding=source_name,
                        kind=UsageKind.CONSUMED,
                        location=info.moved_at,
                        consumes=True,
                    ))

        elif node.type == "reference_expression":
            # Borrowing
            for child in node.children:
                if child.type == "identifier":
                    source_name = self._get_text(child, source)
                    if source_name in self.analysis.bindings:
                        info = self.analysis.bindings[source_name]
                        is_mut = any(
                            c.type == "mutable_specifier"
                            for c in node.children
                        )
                        borrow_kind = (
                            OwnershipKind.MUT_BORROWED
                            if is_mut else
                            OwnershipKind.BORROWED
                        )
                        info.borrows.append(BorrowInfo(
                            borrower=target,
                            kind=borrow_kind,
                            location=f"{node.start_point[0]}:{node.start_point[1]}",
                            scope_depth=self.scope_depth,
                        ))
                        self.analysis.usages.append(UsageInfo(
                            binding=source_name,
                            kind=(
                                UsageKind.MUT_BORROWED
                                if is_mut else
                                UsageKind.BORROWED
                            ),
                            location=f"{node.start_point[0]}:{node.start_point[1]}",
                        ))

    def _analyze_assignment(self, node: Node, source: str) -> None:
        """Analyze an assignment expression.

        Args:
            node: assignment_expression node
            source: Full source code
        """
        # Find target
        target = ""
        for child in node.children:
            if child.type == "identifier":
                target = self._get_text(child, source)
                break

        if target and target in self.analysis.bindings:
            info = self.analysis.bindings[target]
            # Check if we have mutable borrows active
            active_borrows = [
                b for b in info.borrows
                if b.scope_depth >= self.scope_depth
            ]
            if any(b.kind == OwnershipKind.MUT_BORROWED for b in active_borrows):
                self.analysis.borrow_errors.append(
                    f"Cannot assign to `{target}` while mutably borrowed"
                )

            self.analysis.usages.append(UsageInfo(
                binding=target,
                kind=UsageKind.MUTATED,
                location=f"{node.start_point[0]}:{node.start_point[1]}",
            ))

    def _analyze_call(self, node: Node, source: str) -> None:
        """Analyze a function call expression.

        Args:
            node: call_expression node
            source: Full source code
        """
        # Find arguments
        args_node = None
        for child in node.children:
            if child.type == "arguments":
                args_node = child
                break

        if args_node:
            for child in args_node.children:
                self._analyze_argument(child, source)

    def _analyze_method_call(self, node: Node, source: str) -> None:
        """Analyze a method call expression.

        Args:
            node: method_call_expression node
            source: Full source code
        """
        # Find receiver
        for child in node.children:
            if child.type == "identifier":
                receiver = self._get_text(child, source)
                if receiver in self.analysis.bindings:
                    info = self.analysis.bindings[receiver]
                    if info.kind == OwnershipKind.MOVED:
                        self.analysis.move_errors.append(
                            f"Use of moved value: `{receiver}` "
                            f"(moved at {info.moved_at})"
                        )
                break

        # Analyze arguments
        args_node = None
        for child in node.children:
            if child.type == "arguments":
                args_node = child
                break

        if args_node:
            for child in args_node.children:
                self._analyze_argument(child, source)

    def _analyze_argument(self, node: Node, source: str) -> None:
        """Analyze a function argument.

        Args:
            node: Argument node
            source: Full source code
        """
        if node.type == "identifier":
            name = self._get_text(node, source)
            if name in self.analysis.bindings:
                info = self.analysis.bindings[name]
                if info.kind == OwnershipKind.MOVED:
                    self.analysis.move_errors.append(
                        f"Use of moved value: `{name}` "
                        f"(moved at {info.moved_at})"
                    )
                elif not info.is_copy:
                    # Assume move by default (conservative)
                    info.kind = OwnershipKind.MOVED
                    info.moved_at = f"{node.start_point[0]}:{node.start_point[1]}"
                    self.analysis.usages.append(UsageInfo(
                        binding=name,
                        kind=UsageKind.CONSUMED,
                        location=info.moved_at,
                        consumes=True,
                    ))

        elif node.type == "reference_expression":
            self._analyze_reference(node, source)

    def _analyze_reference(self, node: Node, source: str) -> None:
        """Analyze a reference expression.

        Args:
            node: reference_expression node
            source: Full source code
        """
        is_mut = any(c.type == "mutable_specifier" for c in node.children)

        for child in node.children:
            if child.type == "identifier":
                name = self._get_text(child, source)
                if name in self.analysis.bindings:
                    info = self.analysis.bindings[name]

                    if info.kind == OwnershipKind.MOVED:
                        self.analysis.move_errors.append(
                            f"Cannot borrow `{name}` as it has been moved "
                            f"(moved at {info.moved_at})"
                        )
                        return

                    # Check borrow conflicts
                    active_borrows = [
                        b for b in info.borrows
                        if b.scope_depth >= self.scope_depth
                    ]

                    if is_mut:
                        # Mutable borrow
                        if active_borrows:
                            self.analysis.borrow_errors.append(
                                f"Cannot borrow `{name}` as mutable because "
                                f"it is already borrowed"
                            )
                        else:
                            info.borrows.append(BorrowInfo(
                                borrower="_anonymous",
                                kind=OwnershipKind.MUT_BORROWED,
                                location=f"{node.start_point[0]}:{node.start_point[1]}",
                                scope_depth=self.scope_depth,
                            ))
                    # Shared borrow
                    elif any(b.kind == OwnershipKind.MUT_BORROWED for b in active_borrows):
                        self.analysis.borrow_errors.append(
                            f"Cannot borrow `{name}` as immutable because "
                            f"it is already borrowed as mutable"
                        )
                    else:
                        info.borrows.append(BorrowInfo(
                            borrower="_anonymous",
                            kind=OwnershipKind.BORROWED,
                            location=f"{node.start_point[0]}:{node.start_point[1]}",
                            scope_depth=self.scope_depth,
                        ))

                    self.analysis.usages.append(UsageInfo(
                        binding=name,
                        kind=UsageKind.MUT_BORROWED if is_mut else UsageKind.BORROWED,
                        location=f"{node.start_point[0]}:{node.start_point[1]}",
                    ))

    def _end_scope(self) -> None:
        """End the current scope, releasing borrows."""
        # Release borrows that started in this scope
        for info in self.analysis.bindings.values():
            info.borrows = [
                b for b in info.borrows
                if b.scope_depth < self.scope_depth
            ]

    def _is_copy_type(self, type_str: str) -> bool:
        """Check if a type implements Copy.

        Args:
            type_str: Type string

        Returns:
            True if the type is Copy
        """
        # Strip references and mutability
        clean = type_str.strip()
        if clean.startswith("&"):
            # References are Copy
            return True

        # Check primitive types
        base = clean.split("<")[0].strip()
        if base in COPY_TYPES:
            return True

        # Check for array of Copy types
        if clean.startswith("[") and clean.endswith("]"):
            inner = clean[1:-1].rsplit(";", 1)[0].strip()
            return self._is_copy_type(inner)

        # Check for tuples of Copy types
        if clean.startswith("(") and clean.endswith(")"):
            inner = clean[1:-1]
            parts = self._split_tuple_types(inner)
            return all(self._is_copy_type(p) for p in parts)

        return False

    def _split_tuple_types(self, inner: str) -> list[str]:
        """Split tuple type string into components.

        Args:
            inner: Tuple contents without parens

        Returns:
            List of type strings
        """
        parts: list[str] = []
        depth = 0
        current = ""

        for char in inner:
            if char in "(<[":
                depth += 1
                current += char
            elif char in ")>]":
                depth -= 1
                current += char
            elif char == "," and depth == 0:
                parts.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            parts.append(current.strip())

        return parts

    def get_ownership_for_param(
        self, type_str: str
    ) -> tuple[OwnershipKind, str | None]:
        """Determine ownership kind and lifetime for a parameter type.

        Args:
            type_str: Parameter type string

        Returns:
            (OwnershipKind, lifetime or None)
        """
        clean = type_str.strip()

        # Extract lifetime if present
        lifetime = None
        if "'" in clean:
            import re
            match = re.search(r"'(\w+)", clean)
            if match:
                lifetime = match.group(1)

        # Determine ownership
        if clean.startswith("&mut "):
            return OwnershipKind.MUT_BORROWED, lifetime
        elif clean.startswith("&"):
            return OwnershipKind.BORROWED, lifetime
        else:
            return OwnershipKind.OWNED, lifetime
