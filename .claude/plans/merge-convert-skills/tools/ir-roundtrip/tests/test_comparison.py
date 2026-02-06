"""Tests for the CodeComparator class.

Tests cover:
- L1 (Syntactic) AST comparison
- L2 (Operational) trace comparison (limited)
- L3 (Semantic) I/O comparison
- AST normalization
- Difference detection
"""

from __future__ import annotations

import pytest

from ir_roundtrip.comparison import (
    CodeComparator,
    CompareResult,
    ASTDifference,
    DifferenceKind,
    ASTNormalizer,
)


class TestASTNormalizer:
    """Tests for AST normalization."""

    def test_removes_location_info(self) -> None:
        """Verify location information is removed."""
        import ast

        source = "x = 1"
        tree = ast.parse(source)
        normalizer = ASTNormalizer()
        normalized = normalizer.visit(tree)

        for node in ast.walk(normalized):
            assert not hasattr(node, "lineno")
            assert not hasattr(node, "col_offset")

    def test_removes_docstrings_by_default(self) -> None:
        """Verify docstrings are removed by default."""
        import ast

        source = '''def foo():
    """Docstring."""
    return 1
'''
        tree = ast.parse(source)
        normalizer = ASTNormalizer(preserve_docstrings=False)
        normalized = normalizer.visit(tree)

        # Get function body
        func = normalized.body[0]
        assert isinstance(func, ast.FunctionDef)

        # Docstring should be removed, only return statement
        assert len(func.body) == 1
        assert isinstance(func.body[0], ast.Return)

    def test_preserves_docstrings_when_configured(self) -> None:
        """Verify docstrings are preserved when configured."""
        import ast

        source = '''def foo():
    """Docstring."""
    return 1
'''
        tree = ast.parse(source)
        normalizer = ASTNormalizer(preserve_docstrings=True)
        normalized = normalizer.visit(tree)

        func = normalized.body[0]
        assert isinstance(func, ast.FunctionDef)

        # Should have docstring and return
        assert len(func.body) == 2


class TestL1Comparison:
    """Tests for L1 (Syntactic) comparison."""

    def test_identical_code_is_equivalent(self, simple_function: str) -> None:
        """Identical code should be L1 equivalent."""
        comparator = CodeComparator()
        result = comparator.compare_l1_syntactic(simple_function, simple_function)

        assert result.equivalent
        assert len(result.ast_differences) == 0

    def test_whitespace_differences_are_equivalent(self) -> None:
        """Whitespace-only differences should be L1 equivalent."""
        source = "def add(a, b): return a + b"
        target = """def add(a, b):
    return a + b
"""
        comparator = CodeComparator()
        result = comparator.compare_l1_syntactic(source, target)

        assert result.equivalent

    def test_comment_differences_are_equivalent(self) -> None:
        """Comment differences should be L1 equivalent (no comments in AST)."""
        source = """def add(a, b):
    # Add two numbers
    return a + b
"""
        target = """def add(a, b):
    return a + b  # Return sum
"""
        comparator = CodeComparator()
        result = comparator.compare_l1_syntactic(source, target)

        assert result.equivalent

    def test_different_function_names_not_equivalent(self) -> None:
        """Different function names should not be L1 equivalent."""
        source = "def add(a, b): return a + b"
        target = "def sum(a, b): return a + b"

        comparator = CodeComparator()
        result = comparator.compare_l1_syntactic(source, target)

        assert not result.equivalent
        assert any(d.kind == DifferenceKind.NAME_MISMATCH for d in result.ast_differences)

    def test_different_operations_not_equivalent(self) -> None:
        """Different operations should not be L1 equivalent."""
        source = "def calc(a, b): return a + b"
        target = "def calc(a, b): return a - b"

        comparator = CodeComparator()
        result = comparator.compare_l1_syntactic(source, target)

        assert not result.equivalent

    def test_different_structure_not_equivalent(self) -> None:
        """Different AST structure should not be L1 equivalent."""
        source = """def foo(x):
    if x > 0:
        return 1
    return 0
"""
        target = """def foo(x):
    return 1 if x > 0 else 0
"""
        comparator = CodeComparator()
        result = comparator.compare_l1_syntactic(source, target)

        assert not result.equivalent

    def test_syntax_error_handled(self) -> None:
        """Syntax errors should result in non-equivalent with error."""
        source = "def add(a, b): return a + b"
        target = "def add(a, b) return a + b"  # Missing colon

        comparator = CodeComparator()
        result = comparator.compare_l1_syntactic(source, target)

        assert not result.equivalent
        assert any("Parse error" in str(d) for d in result.ast_differences)


class TestL2Comparison:
    """Tests for L2 (Operational) comparison."""

    def test_identical_code_is_equivalent(self, simple_function: str) -> None:
        """Identical code should be L2 equivalent."""
        comparator = CodeComparator()
        result = comparator.compare_l2_operational(simple_function, simple_function)

        assert result.equivalent

    def test_equivalent_loops_may_differ(self) -> None:
        """Different loop implementations may still be L2 equivalent."""
        source = """def sum_list(lst):
    total = 0
    for x in lst:
        total += x
    return total
"""
        # Note: This test is limited as full trace comparison is not implemented
        comparator = CodeComparator()
        result = comparator.compare_l2_operational(source, source)

        assert result.equivalent


@pytest.mark.l3
class TestL3Comparison:
    """Tests for L3 (Semantic) comparison."""

    def test_identical_code_is_equivalent(
        self,
        simple_function: str,
        add_test_inputs: list[dict],
    ) -> None:
        """Identical code should be L3 equivalent."""
        comparator = CodeComparator()
        result = comparator.compare_l3_semantic(
            simple_function, simple_function, add_test_inputs
        )

        assert result.equivalent

    def test_different_implementation_same_semantics(
        self,
        add_test_inputs: list[dict],
    ) -> None:
        """Different implementations with same semantics should be L3 equivalent."""
        source = """def add(a: int, b: int) -> int:
    return a + b
"""
        target = """def add(a: int, b: int) -> int:
    result = a
    result = result + b
    return result
"""
        comparator = CodeComparator()
        result = comparator.compare_l3_semantic(source, target, add_test_inputs)

        assert result.equivalent

    def test_different_semantics_not_equivalent(
        self,
        add_test_inputs: list[dict],
    ) -> None:
        """Different semantics should not be L3 equivalent."""
        source = """def add(a: int, b: int) -> int:
    return a + b
"""
        target = """def add(a: int, b: int) -> int:
    return a - b
"""
        comparator = CodeComparator()
        result = comparator.compare_l3_semantic(source, target, add_test_inputs)

        assert not result.equivalent
        assert len(result.semantic_differences) > 0

    def test_exception_behavior_compared(self) -> None:
        """Exception behavior should be compared."""
        source = """def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Division by zero")
    return a / b
"""
        target = """def divide(a: int, b: int) -> float:
    return a / b  # Will raise ZeroDivisionError instead
"""
        test_inputs = [{"a": 10, "b": 0}]

        comparator = CodeComparator()
        result = comparator.compare_l3_semantic(source, target, test_inputs)

        # Both raise, but different exception types
        assert not result.equivalent

    def test_empty_test_cases_passes(self) -> None:
        """Empty test cases should pass with syntax-only check."""
        source = "def foo(x): return x"
        target = "def foo(x): return x"

        comparator = CodeComparator()
        result = comparator.compare_l3_semantic(source, target, [])

        assert result.equivalent


class TestCompareResult:
    """Tests for CompareResult class."""

    def test_summary_for_equivalent(self) -> None:
        """Summary should indicate equivalence."""
        result = CompareResult(equivalent=True, level="L1_SYNTACTIC")
        assert "Equivalent" in result.summary

    def test_summary_for_not_equivalent(self) -> None:
        """Summary should indicate differences."""
        result = CompareResult(
            equivalent=False,
            level="L1_SYNTACTIC",
            ast_differences=[
                ASTDifference(
                    kind=DifferenceKind.NAME_MISMATCH,
                    location="root",
                )
            ],
        )
        assert "Not equivalent" in result.summary
        assert "1 AST difference" in result.summary

    def test_differences_property(self) -> None:
        """differences property should return all difference strings."""
        result = CompareResult(
            equivalent=False,
            level="L1_SYNTACTIC",
            ast_differences=[
                ASTDifference(
                    kind=DifferenceKind.NAME_MISMATCH,
                    location="root.name",
                    source_value="add",
                    target_value="sum",
                ),
            ],
        )
        diffs = result.differences
        assert len(diffs) == 1
        assert "add" in diffs[0]
        assert "sum" in diffs[0]

    def test_unified_diff(self) -> None:
        """unified_diff should generate diff output."""
        result = CompareResult(
            equivalent=False,
            level="L1_SYNTACTIC",
            source_ast_dump="Line 1\nLine 2",
            target_ast_dump="Line 1\nLine 3",
        )
        diff = result.unified_diff()
        assert "---" in diff
        assert "+++" in diff


class TestASTDifference:
    """Tests for ASTDifference class."""

    def test_str_with_description(self) -> None:
        """String representation should include description."""
        diff = ASTDifference(
            kind=DifferenceKind.AST_STRUCTURE,
            location="root",
            description="Missing function body",
        )
        assert "Missing function body" in str(diff)

    def test_str_with_values(self) -> None:
        """String representation should include values."""
        diff = ASTDifference(
            kind=DifferenceKind.NAME_MISMATCH,
            location="root.name",
            source_value="foo",
            target_value="bar",
        )
        s = str(diff)
        assert "foo" in s
        assert "bar" in s
