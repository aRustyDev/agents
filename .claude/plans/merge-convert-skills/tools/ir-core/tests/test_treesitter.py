"""Tests for TreeSitter adapter."""

from __future__ import annotations

import pytest

from ir_core.treesitter import (
    TSSourceSpan,
    SourceSpan,  # Backwards compatibility alias
    TreeNode,
    ParseTree,
    TreeSitterAdapter,
    GASTNode,
    GASTKind,
    ASTNormalizer,
)
from ir_core.models import SourceSpan as IRSourceSpan


class TestTSSourceSpan:
    """Tests for TSSourceSpan (tree-sitter source span)."""

    def test_create_span(self) -> None:
        """Test creating a TSSourceSpan."""
        span = TSSourceSpan(
            file="test.py",
            start_byte=0,
            end_byte=10,
            start_point=(0, 0),
            end_point=(0, 10),
        )
        assert span.file == "test.py"
        assert span.start_line == 1  # 1-indexed
        assert span.start_col == 0
        assert span.end_line == 1
        assert span.end_col == 10


class TestTreeNode:
    """Tests for TreeNode wrapper."""

    def test_create_node(self) -> None:
        """Test creating a TreeNode."""
        span = TSSourceSpan(
            file="test.py",
            start_byte=0,
            end_byte=10,
            start_point=(0, 0),
            end_point=(0, 10),
        )
        node = TreeNode(
            type="identifier",
            text="hello",
            span=span,
            is_named=True,
            is_error=False,
        )
        assert node.type == "identifier"
        assert node.text == "hello"
        assert node.is_named is True

    def test_node_with_children(self) -> None:
        """Test TreeNode with children."""
        span = TSSourceSpan(
            file="test.py",
            start_byte=0,
            end_byte=20,
            start_point=(0, 0),
            end_point=(0, 20),
        )
        child = TreeNode(
            type="identifier",
            text="x",
            span=span,
            is_named=True,
            is_error=False,
        )
        parent = TreeNode(
            type="expression_statement",
            text="x = 1",
            span=span,
            is_named=True,
            is_error=False,
            children=[child],
        )
        child.parent = parent

        assert len(parent.children) == 1
        assert child.parent == parent

    def test_named_children(self) -> None:
        """Test filtering named children."""
        span = TSSourceSpan(
            file="test.py",
            start_byte=0,
            end_byte=20,
            start_point=(0, 0),
            end_point=(0, 20),
        )
        named = TreeNode(type="id", text="x", span=span, is_named=True, is_error=False)
        anon = TreeNode(type="(", text="(", span=span, is_named=False, is_error=False)

        parent = TreeNode(
            type="call",
            text="f(x)",
            span=span,
            is_named=True,
            is_error=False,
            children=[anon, named],
        )

        named_children = parent.named_children()
        assert len(named_children) == 1
        assert named_children[0] == named

    def test_find_first(self) -> None:
        """Test find_first method."""
        span = TSSourceSpan(
            file="test.py",
            start_byte=0,
            end_byte=20,
            start_point=(0, 0),
            end_point=(0, 20),
        )
        inner = TreeNode(type="identifier", text="x", span=span, is_named=True, is_error=False)
        outer = TreeNode(
            type="expression",
            text="x",
            span=span,
            is_named=True,
            is_error=False,
            children=[inner],
        )

        found = outer.find_first("identifier")
        assert found == inner

        not_found = outer.find_first("number")
        assert not_found is None

    def test_find_all(self) -> None:
        """Test find_all method."""
        span = TSSourceSpan(
            file="test.py",
            start_byte=0,
            end_byte=20,
            start_point=(0, 0),
            end_point=(0, 20),
        )
        id1 = TreeNode(type="identifier", text="x", span=span, is_named=True, is_error=False)
        id2 = TreeNode(type="identifier", text="y", span=span, is_named=True, is_error=False)
        parent = TreeNode(
            type="expression",
            text="x + y",
            span=span,
            is_named=True,
            is_error=False,
            children=[id1, id2],
        )

        found = parent.find_all("identifier")
        assert len(found) == 2


class TestTreeSitterAdapter:
    """Tests for TreeSitterAdapter."""

    def test_supported_languages(self) -> None:
        """Test list of supported languages."""
        languages = TreeSitterAdapter.supported_languages()
        assert "python" in languages
        assert "rust" in languages
        assert "typescript" in languages

    def test_unsupported_language_raises(self) -> None:
        """Test that unsupported language raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            TreeSitterAdapter("unsupported_lang")

        assert "unsupported" in str(exc_info.value).lower()


class TestTSSourceSpanToIR:
    """Tests for TSSourceSpan.to_ir_span() conversion."""

    def test_to_ir_span(self) -> None:
        """Test converting TSSourceSpan to IR SourceSpan."""
        ts_span = TSSourceSpan(
            file="test.py",
            start_byte=0,
            end_byte=50,
            start_point=(2, 4),  # 0-indexed: line 3, column 5
            end_point=(5, 10),    # 0-indexed: line 6, column 11
        )

        ir_span = ts_span.to_ir_span()

        # IR spans are 1-indexed for lines
        assert ir_span.file == "test.py"
        assert ir_span.start_line == 3  # 2 + 1 = 3
        assert ir_span.start_col == 4
        assert ir_span.end_line == 6    # 5 + 1 = 6
        assert ir_span.end_col == 10

        # Verify it's an IR SourceSpan (Pydantic model)
        assert isinstance(ir_span, IRSourceSpan)

    def test_backwards_compatibility_alias(self) -> None:
        """Test that SourceSpan alias still works."""
        # SourceSpan should be an alias for TSSourceSpan
        span = SourceSpan(
            file="test.py",
            start_byte=0,
            end_byte=10,
            start_point=(0, 0),
            end_point=(0, 10),
        )
        assert isinstance(span, TSSourceSpan)


class TestGASTNode:
    """Tests for Generic AST nodes."""

    def test_create_gast_node(self) -> None:
        """Test creating a GAST node."""
        span = TSSourceSpan(
            file="test.py",
            start_byte=0,
            end_byte=10,
            start_point=(0, 0),
            end_point=(0, 10),
        )
        node = GASTNode(
            kind=GASTKind.FUNCTION,
            span=span,
            attributes={
                "name": "my_func",
                "async": False,
            },
        )
        assert node.kind == GASTKind.FUNCTION
        assert node.get_attr("name") == "my_func"
        assert node.get_attr("async") is False
        assert node.get_attr("missing", "default") == "default"

    def test_set_attr(self) -> None:
        """Test setting attributes."""
        span = TSSourceSpan(
            file="test.py",
            start_byte=0,
            end_byte=10,
            start_point=(0, 0),
            end_point=(0, 10),
        )
        node = GASTNode(kind=GASTKind.IDENTIFIER, span=span)
        node.set_attr("name", "x")

        assert node.get_attr("name") == "x"


class TestGASTKind:
    """Tests for GAST node kinds."""

    def test_structural_kinds(self) -> None:
        """Test structural layer kinds."""
        assert GASTKind.MODULE == "module"
        assert GASTKind.IMPORT == "import"
        assert GASTKind.EXPORT == "export"

    def test_type_kinds(self) -> None:
        """Test type layer kinds."""
        assert GASTKind.TYPE_DEF == "type_def"
        assert GASTKind.TYPE_REF == "type_ref"

    def test_control_flow_kinds(self) -> None:
        """Test control flow layer kinds."""
        assert GASTKind.FUNCTION == "function"
        assert GASTKind.CLASS == "class"
        assert GASTKind.BRANCH == "branch"
        assert GASTKind.LOOP == "loop"

    def test_expression_kinds(self) -> None:
        """Test expression layer kinds."""
        assert GASTKind.CALL == "call"
        assert GASTKind.LITERAL == "literal"
        assert GASTKind.IDENTIFIER == "identifier"


class TestASTNormalizer:
    """Tests for AST normalizer base class."""

    def test_create_normalizer(self) -> None:
        """Test creating a normalizer."""
        normalizer = ASTNormalizer("python")
        assert normalizer.language == "python"

    def test_register_handler(self) -> None:
        """Test registering a handler."""
        normalizer = ASTNormalizer("python")

        def handle_function(node: TreeNode) -> GASTNode:
            return GASTNode(
                kind=GASTKind.FUNCTION,
                span=node.span,
                attributes={"name": node.text},
            )

        normalizer.register_handler("function_definition", handle_function)

        assert "function_definition" in normalizer._handlers
