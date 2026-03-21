"""Code comparison utilities for round-trip validation.

This module provides comparison functions for verifying equivalence
at different preservation levels:

- L1 (Syntactic): AST structure comparison
- L2 (Operational): Execution trace comparison
- L3 (Semantic): I/O behavior comparison

Example:
    comparator = CodeComparator()

    # L1 comparison
    result = comparator.compare_l1_syntactic(source, target)
    if not result.equivalent:
        for diff in result.differences:
            print(f"AST diff: {diff}")

    # L3 comparison with test cases
    result = comparator.compare_l3_semantic(source, target, test_cases)
"""

from __future__ import annotations

import ast
import difflib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DifferenceKind(str, Enum):
    """Types of differences between source and target.

    Attributes:
        AST_STRUCTURE: Structural difference in AST
        AST_NODE_TYPE: Different node types at same position
        AST_NODE_COUNT: Different number of nodes
        NAME_MISMATCH: Different identifiers
        TYPE_MISMATCH: Different type annotations
        VALUE_MISMATCH: Different literal values
        OUTPUT_MISMATCH: Different outputs for same inputs
        EXCEPTION_MISMATCH: Different exception behavior
        TRACE_MISMATCH: Different execution traces
    """

    AST_STRUCTURE = "ast_structure"
    AST_NODE_TYPE = "ast_node_type"
    AST_NODE_COUNT = "ast_node_count"
    NAME_MISMATCH = "name_mismatch"
    TYPE_MISMATCH = "type_mismatch"
    VALUE_MISMATCH = "value_mismatch"
    OUTPUT_MISMATCH = "output_mismatch"
    EXCEPTION_MISMATCH = "exception_mismatch"
    TRACE_MISMATCH = "trace_mismatch"


@dataclass
class ASTDifference:
    """Difference in AST structure.

    Attributes:
        kind: Type of difference
        location: Location in AST (path from root)
        source_value: Value in source AST
        target_value: Value in target AST
        description: Human-readable description
    """

    kind: DifferenceKind
    location: str
    source_value: str | None = None
    target_value: str | None = None
    description: str = ""

    def __str__(self) -> str:
        if self.description:
            return f"{self.kind.value} at {self.location}: {self.description}"
        return f"{self.kind.value} at {self.location}: {self.source_value} -> {self.target_value}"


@dataclass
class SemanticDifference:
    """Difference in semantic behavior.

    Attributes:
        inputs: Input values that produced different outputs
        source_output: Output from source code
        target_output: Output from target code
        source_exception: Exception from source (if any)
        target_exception: Exception from target (if any)
    """

    inputs: dict[str, Any]
    source_output: Any = None
    target_output: Any = None
    source_exception: str | None = None
    target_exception: str | None = None

    @property
    def is_output_diff(self) -> bool:
        """Check if this is an output mismatch (not exception)."""
        return self.source_exception is None and self.target_exception is None

    @property
    def is_exception_diff(self) -> bool:
        """Check if this is an exception mismatch."""
        return self.source_exception != self.target_exception

    def __str__(self) -> str:
        inputs_str = ", ".join(f"{k}={v!r}" for k, v in self.inputs.items())
        if self.is_exception_diff:
            return (
                f"Exception mismatch for ({inputs_str}): "
                f"source raised {self.source_exception}, "
                f"target raised {self.target_exception}"
            )
        return (
            f"Output mismatch for ({inputs_str}): "
            f"source={self.source_output!r}, target={self.target_output!r}"
        )


@dataclass
class CompareResult:
    """Result of comparing source and target code.

    Attributes:
        equivalent: Whether codes are equivalent at the tested level
        level: Preservation level tested
        ast_differences: L1 AST differences
        semantic_differences: L3 semantic differences
        source_ast_dump: Dump of source AST (for debugging)
        target_ast_dump: Dump of target AST (for debugging)
        metadata: Additional comparison metadata
    """

    equivalent: bool
    level: str = "unknown"
    ast_differences: list[ASTDifference] = field(default_factory=list)
    semantic_differences: list[SemanticDifference] = field(default_factory=list)
    source_ast_dump: str | None = None
    target_ast_dump: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def summary(self) -> str:
        """Generate a summary of differences."""
        if self.equivalent:
            return f"Equivalent at {self.level}"

        parts = []
        if self.ast_differences:
            parts.append(f"{len(self.ast_differences)} AST difference(s)")
        if self.semantic_differences:
            parts.append(f"{len(self.semantic_differences)} semantic difference(s)")

        return f"Not equivalent at {self.level}: " + ", ".join(parts)

    @property
    def differences(self) -> list[str]:
        """Get all differences as strings."""
        result: list[str] = []
        for diff in self.ast_differences:
            result.append(str(diff))
        for diff in self.semantic_differences:
            result.append(str(diff))
        return result

    def unified_diff(self) -> str:
        """Generate a unified diff between AST dumps."""
        if self.source_ast_dump is None or self.target_ast_dump is None:
            return ""

        source_lines = self.source_ast_dump.splitlines(keepends=True)
        target_lines = self.target_ast_dump.splitlines(keepends=True)

        diff = difflib.unified_diff(
            source_lines,
            target_lines,
            fromfile="source",
            tofile="target",
        )
        return "".join(diff)


class ASTNormalizer(ast.NodeTransformer):
    """Normalize AST for comparison.

    Removes or normalizes elements that shouldn't affect equivalence:
    - Line/column information
    - Type comments
    - Docstrings (optionally)
    """

    def __init__(self, preserve_docstrings: bool = False) -> None:
        self.preserve_docstrings = preserve_docstrings
        super().__init__()

    def visit(self, node: ast.AST) -> ast.AST:
        """Visit and normalize a node."""
        # Remove location info
        for attr in ("lineno", "col_offset", "end_lineno", "end_col_offset"):
            if hasattr(node, attr):
                delattr(node, attr)

        # Remove type_comment
        if hasattr(node, "type_comment"):
            delattr(node, "type_comment")

        return super().visit(node)

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """Handle module node, optionally removing docstring."""
        self.generic_visit(node)
        if not self.preserve_docstrings and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                if isinstance(first.value.value, str):
                    node.body = node.body[1:]
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Handle function definition, optionally removing docstring."""
        self.generic_visit(node)
        if not self.preserve_docstrings and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                if isinstance(first.value.value, str):
                    node.body = node.body[1:]
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        """Handle async function definition."""
        self.generic_visit(node)
        if not self.preserve_docstrings and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                if isinstance(first.value.value, str):
                    node.body = node.body[1:]
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Handle class definition, optionally removing docstring."""
        self.generic_visit(node)
        if not self.preserve_docstrings and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                if isinstance(first.value.value, str):
                    node.body = node.body[1:]
        return node


class CodeComparator:
    """Compare source and target code at different preservation levels.

    This class provides methods for comparing Python code at L1, L2, and L3
    equivalence levels. Each level has different requirements:

    - L1: AST structure must match after normalization
    - L2: Execution traces must match (not fully implemented)
    - L3: Outputs must match for given inputs

    Example:
        comparator = CodeComparator()

        # L1: Syntactic comparison
        result = comparator.compare_l1_syntactic(source, target)

        # L3: Semantic comparison
        test_cases = [{"x": 1}, {"x": 2}]
        result = comparator.compare_l3_semantic(source, target, test_cases)
    """

    def __init__(self, preserve_docstrings: bool = False) -> None:
        """Initialize the comparator.

        Args:
            preserve_docstrings: Whether to include docstrings in L1 comparison
        """
        self.normalizer = ASTNormalizer(preserve_docstrings=preserve_docstrings)

    def compare_l1_syntactic(self, source: str, target: str) -> CompareResult:
        """L1: Compare AST structure after normalization.

        Two programs are L1-equivalent if their normalized ASTs are identical.
        This is the strictest level, rarely achieved in cross-language scenarios
        but often achievable in same-language round-trips.

        Args:
            source: Original source code
            target: Synthesized target code

        Returns:
            CompareResult with AST differences
        """
        try:
            source_ast = ast.parse(source)
            target_ast = ast.parse(target)
        except SyntaxError as e:
            return CompareResult(
                equivalent=False,
                level="L1_SYNTACTIC",
                ast_differences=[
                    ASTDifference(
                        kind=DifferenceKind.AST_STRUCTURE,
                        location="root",
                        description=f"Parse error: {e}",
                    )
                ],
            )

        # Normalize both ASTs
        source_normalized = self.normalizer.visit(source_ast)
        target_normalized = self.normalizer.visit(target_ast)

        # Dump for comparison
        source_dump = ast.dump(source_normalized, indent=2)
        target_dump = ast.dump(target_normalized, indent=2)

        if source_dump == target_dump:
            return CompareResult(
                equivalent=True,
                level="L1_SYNTACTIC",
                source_ast_dump=source_dump,
                target_ast_dump=target_dump,
            )

        # Find differences
        differences = self._find_ast_differences(
            source_normalized, target_normalized, "root"
        )

        return CompareResult(
            equivalent=False,
            level="L1_SYNTACTIC",
            ast_differences=differences,
            source_ast_dump=source_dump,
            target_ast_dump=target_dump,
        )

    def compare_l2_operational(self, source: str, target: str) -> CompareResult:
        """L2: Compare execution traces.

        Two programs are L2-equivalent if they visit corresponding states
        at each execution step. This is stricter than L3 but more relaxed
        than L1.

        Note: Full trace comparison is not implemented. This currently falls
        back to L1 comparison with relaxed criteria.

        Args:
            source: Original source code
            target: Synthesized target code

        Returns:
            CompareResult with operational differences
        """
        # For now, use L1 comparison with relaxed criteria
        # Full trace comparison would require instrumented execution
        l1_result = self.compare_l1_syntactic(source, target)

        # Relax some L1 criteria for L2
        # - Allow different variable names (if same structure)
        # - Allow different iteration implementations (for/while)
        relaxed_differences = [
            diff for diff in l1_result.ast_differences
            if diff.kind not in (
                DifferenceKind.NAME_MISMATCH,
            )
        ]

        return CompareResult(
            equivalent=len(relaxed_differences) == 0,
            level="L2_OPERATIONAL",
            ast_differences=relaxed_differences,
            source_ast_dump=l1_result.source_ast_dump,
            target_ast_dump=l1_result.target_ast_dump,
            metadata={"note": "L2 uses relaxed L1 criteria (full trace comparison not implemented)"},
        )

    def compare_l3_semantic(
        self,
        source: str,
        target: str,
        test_cases: list[dict[str, Any]],
    ) -> CompareResult:
        """L3: Compare I/O behavior.

        Two programs are L3-equivalent if they produce the same outputs
        for all tested inputs. This is the Phase 5 target level.

        Args:
            source: Original source code
            target: Synthesized target code
            test_cases: List of input dictionaries to test

        Returns:
            CompareResult with semantic differences
        """
        # Import here to avoid circular dependency
        from .executor import SafeExecutor

        if not test_cases:
            # No test cases - check syntax only
            try:
                ast.parse(source)
                ast.parse(target)
                return CompareResult(
                    equivalent=True,
                    level="L3_SEMANTIC",
                    metadata={"note": "No test cases provided, syntax-only check"},
                )
            except SyntaxError as e:
                return CompareResult(
                    equivalent=False,
                    level="L3_SEMANTIC",
                    semantic_differences=[
                        SemanticDifference(
                            inputs={},
                            source_exception=str(e) if "source" in str(e) else None,
                            target_exception=str(e) if "target" in str(e) else None,
                        )
                    ],
                )

        executor = SafeExecutor()
        semantic_differences: list[SemanticDifference] = []

        # Detect function name from source
        func_name = self._detect_function_name(source)
        if func_name is None:
            return CompareResult(
                equivalent=False,
                level="L3_SEMANTIC",
                semantic_differences=[
                    SemanticDifference(
                        inputs={},
                        source_exception="Could not detect function name",
                    )
                ],
            )

        for inputs in test_cases:
            source_result = executor.execute(source, inputs, func_name=func_name)
            target_result = executor.execute(target, inputs, func_name=func_name)

            if not executor.compare_outputs(source_result, target_result):
                semantic_differences.append(
                    SemanticDifference(
                        inputs=inputs,
                        source_output=source_result.return_value,
                        target_output=target_result.return_value,
                        source_exception=(
                            source_result.exception_type
                            if not source_result.success else None
                        ),
                        target_exception=(
                            target_result.exception_type
                            if not target_result.success else None
                        ),
                    )
                )

        return CompareResult(
            equivalent=len(semantic_differences) == 0,
            level="L3_SEMANTIC",
            semantic_differences=semantic_differences,
            metadata={
                "test_count": len(test_cases),
                "pass_count": len(test_cases) - len(semantic_differences),
                "fail_count": len(semantic_differences),
            },
        )

    def _find_ast_differences(
        self,
        source_node: ast.AST,
        target_node: ast.AST,
        path: str,
    ) -> list[ASTDifference]:
        """Recursively find differences between two AST nodes."""
        differences: list[ASTDifference] = []

        # Check node type
        if type(source_node) != type(target_node):
            differences.append(
                ASTDifference(
                    kind=DifferenceKind.AST_NODE_TYPE,
                    location=path,
                    source_value=type(source_node).__name__,
                    target_value=type(target_node).__name__,
                )
            )
            return differences

        # Compare fields
        for field_name, source_value in ast.iter_fields(source_node):
            target_value = getattr(target_node, field_name, None)

            if isinstance(source_value, list):
                if not isinstance(target_value, list):
                    differences.append(
                        ASTDifference(
                            kind=DifferenceKind.AST_STRUCTURE,
                            location=f"{path}.{field_name}",
                            description=f"Expected list, got {type(target_value).__name__}",
                        )
                    )
                    continue

                if len(source_value) != len(target_value):
                    differences.append(
                        ASTDifference(
                            kind=DifferenceKind.AST_NODE_COUNT,
                            location=f"{path}.{field_name}",
                            source_value=str(len(source_value)),
                            target_value=str(len(target_value)),
                        )
                    )

                for i, (s, t) in enumerate(zip(source_value, target_value, strict=False)):
                    if isinstance(s, ast.AST) and isinstance(t, ast.AST):
                        differences.extend(
                            self._find_ast_differences(
                                s, t, f"{path}.{field_name}[{i}]"
                            )
                        )
                    elif s != t:
                        differences.append(
                            ASTDifference(
                                kind=DifferenceKind.VALUE_MISMATCH,
                                location=f"{path}.{field_name}[{i}]",
                                source_value=repr(s),
                                target_value=repr(t),
                            )
                        )

            elif isinstance(source_value, ast.AST):
                if isinstance(target_value, ast.AST):
                    differences.extend(
                        self._find_ast_differences(
                            source_value, target_value, f"{path}.{field_name}"
                        )
                    )
                else:
                    differences.append(
                        ASTDifference(
                            kind=DifferenceKind.AST_STRUCTURE,
                            location=f"{path}.{field_name}",
                            description=f"Expected AST node, got {type(target_value).__name__}",
                        )
                    )

            elif source_value != target_value:
                # Check for name mismatches specifically
                kind = DifferenceKind.VALUE_MISMATCH
                if field_name in ("name", "id", "attr", "arg"):
                    kind = DifferenceKind.NAME_MISMATCH
                elif field_name == "annotation":
                    kind = DifferenceKind.TYPE_MISMATCH

                differences.append(
                    ASTDifference(
                        kind=kind,
                        location=f"{path}.{field_name}",
                        source_value=repr(source_value),
                        target_value=repr(target_value),
                    )
                )

        return differences

    def _detect_function_name(self, source: str) -> str | None:
        """Detect the first public function name in source."""
        try:
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith("_"):
                        return node.name
        except SyntaxError:
            pass
        return None
