"""Tests for the Rust parser."""

import pytest

# Skip all tests if tree-sitter-rust is not available
pytest.importorskip("tree_sitter_rust")

from ir_extract_rust.parser import RustParser


@pytest.fixture
def parser():
    """Create a parser instance."""
    return RustParser()


class TestFunctionParsing:
    """Tests for function parsing."""

    def test_simple_function(self, parser):
        """Test parsing a simple function."""
        source = """
fn add(a: i32, b: i32) -> i32 {
    a + b
}
"""
        functions = list(parser.iter_functions(source, "test.rs"))
        assert len(functions) == 1

        func = functions[0]
        assert func.name == "add"
        assert len(func.params) == 2
        assert func.params[0].name == "a"
        assert func.params[0].type_str == "i32"
        assert func.return_type == "i32"
        assert func.visibility == "private"

    def test_public_function(self, parser):
        """Test parsing a public function."""
        source = """
pub fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}
"""
        functions = list(parser.iter_functions(source, "test.rs"))
        assert len(functions) == 1
        assert functions[0].visibility == "public"

    def test_async_function(self, parser):
        """Test parsing an async function."""
        source = """
async fn fetch() -> String {
    String::new()
}
"""
        functions = list(parser.iter_functions(source, "test.rs"))
        assert len(functions) == 1
        assert functions[0].is_async

    def test_unsafe_function(self, parser):
        """Test parsing an unsafe function."""
        source = """
unsafe fn dangerous() {
}
"""
        functions = list(parser.iter_functions(source, "test.rs"))
        assert len(functions) == 1
        assert functions[0].is_unsafe

    def test_generic_function(self, parser):
        """Test parsing a generic function."""
        source = """
fn swap<T>(a: T, b: T) -> (T, T) {
    (b, a)
}
"""
        functions = list(parser.iter_functions(source, "test.rs"))
        assert len(functions) == 1
        assert len(functions[0].type_params) == 1
        assert functions[0].type_params[0].name == "T"

    def test_function_with_lifetime(self, parser):
        """Test parsing a function with lifetime parameters."""
        source = """
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
"""
        functions = list(parser.iter_functions(source, "test.rs"))
        assert len(functions) == 1
        # Lifetimes are included in type params
        assert any(p.name.startswith("'") for p in functions[0].type_params)

    def test_self_parameter(self, parser):
        """Test parsing methods with self parameter."""
        source = """
impl Foo {
    fn method(&self) {}
    fn mut_method(&mut self) {}
    fn consume(self) {}
}
"""
        impls = list(parser.iter_impls(source, "test.rs"))
        assert len(impls) == 1
        assert len(impls[0].items) == 3

        method = impls[0].items[0]
        assert any(p.is_self for p in method.params)


class TestStructParsing:
    """Tests for struct parsing."""

    def test_simple_struct(self, parser):
        """Test parsing a simple struct."""
        source = """
struct Point {
    x: f64,
    y: f64,
}
"""
        structs = list(parser.iter_structs(source, "test.rs"))
        assert len(structs) == 1

        struct = structs[0]
        assert struct.name == "Point"
        assert len(struct.fields) == 2
        assert struct.fields[0].name == "x"
        assert struct.fields[0].type_str == "f64"
        assert not struct.is_tuple_struct

    def test_tuple_struct(self, parser):
        """Test parsing a tuple struct."""
        source = """
struct Color(u8, u8, u8);
"""
        structs = list(parser.iter_structs(source, "test.rs"))
        assert len(structs) == 1

        struct = structs[0]
        assert struct.name == "Color"
        assert struct.is_tuple_struct
        assert len(struct.fields) == 3

    def test_generic_struct(self, parser):
        """Test parsing a generic struct."""
        source = """
struct Container<T> {
    value: T,
}
"""
        structs = list(parser.iter_structs(source, "test.rs"))
        assert len(structs) == 1
        assert len(structs[0].type_params) == 1
        assert structs[0].type_params[0].name == "T"


class TestEnumParsing:
    """Tests for enum parsing."""

    def test_simple_enum(self, parser):
        """Test parsing a simple enum."""
        source = """
enum Direction {
    North,
    South,
    East,
    West,
}
"""
        enums = list(parser.iter_enums(source, "test.rs"))
        assert len(enums) == 1

        enum = enums[0]
        assert enum.name == "Direction"
        assert len(enum.variants) == 4
        assert all(v.kind == "unit" for v in enum.variants)

    def test_tuple_variant(self, parser):
        """Test parsing enum with tuple variants."""
        source = """
enum Event {
    Click(i32, i32),
    KeyPress(char),
}
"""
        enums = list(parser.iter_enums(source, "test.rs"))
        assert len(enums) == 1
        assert enums[0].variants[0].kind == "tuple"

    def test_struct_variant(self, parser):
        """Test parsing enum with struct variants."""
        source = """
enum Shape {
    Circle { radius: f64 },
}
"""
        enums = list(parser.iter_enums(source, "test.rs"))
        assert len(enums) == 1
        assert enums[0].variants[0].kind == "struct"


class TestTraitParsing:
    """Tests for trait parsing."""

    def test_simple_trait(self, parser):
        """Test parsing a simple trait."""
        source = """
trait Drawable {
    fn draw(&self);
}
"""
        traits = list(parser.iter_traits(source, "test.rs"))
        assert len(traits) == 1

        trait = traits[0]
        assert trait.name == "Drawable"
        assert len(trait.items) == 1
        assert trait.items[0].kind == "method"
        assert trait.items[0].name == "draw"

    def test_trait_with_supertraits(self, parser):
        """Test parsing a trait with supertraits."""
        source = """
trait Sortable: Ord + Clone {
    fn sort_self(&mut self);
}
"""
        traits = list(parser.iter_traits(source, "test.rs"))
        assert len(traits) == 1
        assert len(traits[0].supertraits) >= 1


class TestUseParsing:
    """Tests for use statement parsing."""

    def test_simple_use(self, parser):
        """Test parsing a simple use statement."""
        source = """
use std::collections::HashMap;
"""
        uses = list(parser.iter_uses(source))
        assert len(uses) == 1
        assert uses[0].path == ["std", "collections", "HashMap"]

    def test_use_with_alias(self, parser):
        """Test parsing use with alias."""
        source = """
use std::collections::HashMap as Map;
"""
        uses = list(parser.iter_uses(source))
        assert len(uses) == 1
        assert uses[0].alias == "Map"

    def test_grouped_use(self, parser):
        """Test parsing grouped use statement."""
        source = """
use std::collections::{HashMap, HashSet};
"""
        uses = list(parser.iter_uses(source))
        assert len(uses) == 1
        assert len(uses[0].items) == 2

    def test_glob_use(self, parser):
        """Test parsing glob use statement."""
        source = """
use std::collections::*;
"""
        uses = list(parser.iter_uses(source))
        assert len(uses) == 1
        assert uses[0].is_glob
