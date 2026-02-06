"""Tests for ownership analysis."""

import pytest

# Skip all tests if tree-sitter-rust is not available
pytest.importorskip("tree_sitter_rust")

from ir_extract_rust.ownership import (
    OwnershipAnalyzer,
    OwnershipKind,
    UsageKind,
)
from ir_extract_rust.parser import RustParser


@pytest.fixture
def analyzer():
    """Create an ownership analyzer."""
    return OwnershipAnalyzer()


@pytest.fixture
def parser():
    """Create a parser."""
    return RustParser()


class TestOwnershipAnalysis:
    """Tests for ownership analysis."""

    def test_owned_binding(self, analyzer, parser):
        """Test owned binding detection."""
        source = """
fn test() {
    let x = String::from("hello");
}
"""
        tree = parser.parse(source)
        analysis = analyzer.analyze(source, tree.root_node)

        assert "x" in analysis.bindings
        assert analysis.bindings["x"].kind == OwnershipKind.OWNED

    def test_borrowed_binding(self, analyzer, parser):
        """Test borrowed binding detection."""
        source = """
fn test() {
    let s = String::from("hello");
    let x = &s;
}
"""
        tree = parser.parse(source)
        analysis = analyzer.analyze(source, tree.root_node)

        assert "x" in analysis.bindings
        assert analysis.bindings["x"].kind == OwnershipKind.BORROWED

    def test_mut_borrowed_binding(self, analyzer, parser):
        """Test mutable borrowed binding detection."""
        source = """
fn test() {
    let mut s = String::from("hello");
    let x = &mut s;
}
"""
        tree = parser.parse(source)
        analysis = analyzer.analyze(source, tree.root_node)

        assert "x" in analysis.bindings
        assert analysis.bindings["x"].kind == OwnershipKind.MUT_BORROWED

    def test_copy_type(self, analyzer, parser):
        """Test Copy type detection."""
        source = """
fn test() {
    let x: i32 = 42;
    let y = x;
}
"""
        tree = parser.parse(source)
        analysis = analyzer.analyze(source, tree.root_node)

        # x should still be valid (Copy)
        assert "x" in analysis.bindings
        assert analysis.bindings["x"].is_copy

    def test_move_detection(self, analyzer, parser):
        """Test move detection."""
        source = """
fn test() {
    let s = String::from("hello");
    let t = s;
}
"""
        tree = parser.parse(source)
        analysis = analyzer.analyze(source, tree.root_node)

        # s should be moved
        assert "s" in analysis.bindings
        assert analysis.bindings["s"].kind == OwnershipKind.MOVED


class TestBorrowTracking:
    """Tests for borrow tracking."""

    def test_shared_borrow(self, analyzer, parser):
        """Test shared borrow tracking."""
        source = """
fn test() {
    let s = String::from("hello");
    let r = &s;
}
"""
        tree = parser.parse(source)
        analysis = analyzer.analyze(source, tree.root_node)

        assert "s" in analysis.bindings
        assert len(analysis.bindings["s"].borrows) > 0

    def test_multiple_shared_borrows(self, analyzer, parser):
        """Test multiple shared borrows are allowed."""
        source = """
fn test() {
    let s = String::from("hello");
    let r1 = &s;
    let r2 = &s;
}
"""
        tree = parser.parse(source)
        analysis = analyzer.analyze(source, tree.root_node)

        # Should have no borrow errors
        assert len(analysis.borrow_errors) == 0


class TestOwnershipForParam:
    """Tests for parameter ownership inference."""

    def test_owned_param(self, analyzer):
        """Test owned parameter type."""
        kind, lifetime = analyzer.get_ownership_for_param("String")
        assert kind == OwnershipKind.OWNED
        assert lifetime is None

    def test_borrowed_param(self, analyzer):
        """Test borrowed parameter type."""
        kind, lifetime = analyzer.get_ownership_for_param("&str")
        assert kind == OwnershipKind.BORROWED

    def test_mut_borrowed_param(self, analyzer):
        """Test mutable borrowed parameter type."""
        kind, lifetime = analyzer.get_ownership_for_param("&mut Vec<i32>")
        assert kind == OwnershipKind.MUT_BORROWED

    def test_lifetime_extraction(self, analyzer):
        """Test lifetime extraction from type."""
        kind, lifetime = analyzer.get_ownership_for_param("&'a str")
        assert kind == OwnershipKind.BORROWED
        assert lifetime == "a"
