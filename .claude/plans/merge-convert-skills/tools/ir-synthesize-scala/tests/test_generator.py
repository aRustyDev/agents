"""Tests for Scala code generator."""

from __future__ import annotations

import pytest
from ir_synthesize_scala.generator import ScalaCodeGenerator


@pytest.fixture
def generator() -> ScalaCodeGenerator:
    """Create a generator instance."""
    return ScalaCodeGenerator()


class TestTypeConversion:
    """Tests for type conversion."""

    def test_python_types(self, generator: ScalaCodeGenerator) -> None:
        """Test Python type conversion."""
        assert generator._convert_type("int") == "Int"
        assert generator._convert_type("float") == "Double"
        assert generator._convert_type("str") == "String"
        assert generator._convert_type("bool") == "Boolean"
        assert generator._convert_type("bytes") == "Array[Byte]"

    def test_rust_types(self, generator: ScalaCodeGenerator) -> None:
        """Test Rust type conversion."""
        assert generator._convert_type("i32") == "Int"
        assert generator._convert_type("i64") == "Long"
        assert generator._convert_type("f64") == "Double"
        assert generator._convert_type("String") == "String"

    def test_typescript_types(self, generator: ScalaCodeGenerator) -> None:
        """Test TypeScript type conversion."""
        assert generator._convert_type("number") == "Double"
        assert generator._convert_type("string") == "String"
        assert generator._convert_type("boolean") == "Boolean"
        assert generator._convert_type("void") == "Unit"

    def test_roc_types(self, generator: ScalaCodeGenerator) -> None:
        """Test Roc type conversion."""
        assert generator._convert_type("I64") == "Long"
        assert generator._convert_type("F64") == "Double"
        assert generator._convert_type("Str") == "String"
        assert generator._convert_type("Bool") == "Boolean"

    def test_generic_list(self, generator: ScalaCodeGenerator) -> None:
        """Test generic list conversion."""
        assert generator._convert_type("List[int]") == "List[Int]"
        assert generator._convert_type("Vec<i32>") == "List[Int]"

    def test_generic_dict(self, generator: ScalaCodeGenerator) -> None:
        """Test generic dict conversion."""
        assert generator._convert_type("Dict[str, int]") == "Map[String, Int]"
        assert generator._convert_type("HashMap<String, i32>") == "Map[String, Int]"

    def test_optional(self, generator: ScalaCodeGenerator) -> None:
        """Test optional type conversion."""
        assert generator._convert_type("Optional[int]") == "Option[Int]"
        assert generator._convert_type("Option<i32>") == "Option[Int]"


class TestTraitGeneration:
    """Tests for trait generation."""

    def test_simple_trait(self, generator: ScalaCodeGenerator) -> None:
        """Test simple trait generation."""
        from ir_core.models import TypeDef, TypeKind

        type_def = TypeDef(
            name="Greeting",
            kind=TypeKind.INTERFACE,
            methods=[
                {"name": "greet", "params": [{"name": "name", "type": "String"}], "return_type": "String"}
            ],
        )
        result = generator.generate_trait(type_def)
        assert "trait Greeting" in result
        assert "def greet" in result

    def test_trait_with_type_params(self, generator: ScalaCodeGenerator) -> None:
        """Test trait with type parameters."""
        from ir_core.models import TypeDef, TypeKind

        type_def = TypeDef(
            name="Container",
            kind=TypeKind.INTERFACE,
            type_params=[{"name": "T"}],
        )
        result = generator.generate_trait(type_def)
        assert "trait Container[T]" in result

    def test_trait_with_variance(self, generator: ScalaCodeGenerator) -> None:
        """Test trait with variance annotations."""
        from ir_core.models import TypeDef, TypeKind

        type_def = TypeDef(
            name="Producer",
            kind=TypeKind.INTERFACE,
            type_params=[{"name": "T", "variance": "covariant"}],
        )
        result = generator.generate_trait(type_def)
        assert "trait Producer[+T]" in result

    def test_trait_with_hkt(self, generator: ScalaCodeGenerator) -> None:
        """Test trait with higher-kinded type parameter."""
        from ir_core.models import TypeDef, TypeKind

        type_def = TypeDef(
            name="Functor",
            kind=TypeKind.INTERFACE,
            type_params=[{"name": "F", "kind": "higher_kinded", "arity": 1}],
        )
        result = generator.generate_trait(type_def)
        assert "trait Functor[F[_]]" in result


class TestCaseClassGeneration:
    """Tests for case class generation."""

    def test_simple_case_class(self, generator: ScalaCodeGenerator) -> None:
        """Test simple case class generation."""
        from ir_core.models import TypeDef, TypeKind

        type_def = TypeDef(
            name="Point",
            kind=TypeKind.STRUCT,
            properties=[
                {"name": "x", "type": "Int"},
                {"name": "y", "type": "Int"},
            ],
        )
        result = generator.generate_case_class(type_def)
        assert "case class Point" in result
        assert "x: Int" in result
        assert "y: Int" in result

    def test_case_class_with_defaults(self, generator: ScalaCodeGenerator) -> None:
        """Test case class with default values."""
        from ir_core.models import TypeDef, TypeKind

        type_def = TypeDef(
            name="Config",
            kind=TypeKind.STRUCT,
            properties=[
                {"name": "host", "type": "String", "default": '"localhost"'},
                {"name": "port", "type": "Int", "default": "8080"},
            ],
        )
        result = generator.generate_case_class(type_def)
        assert 'host: String = "localhost"' in result
        assert "port: Int = 8080" in result


class TestFunctionGeneration:
    """Tests for function generation."""

    def test_simple_function(self, generator: ScalaCodeGenerator) -> None:
        """Test simple function generation."""
        from ir_core.models import FunctionDef, Parameter

        func_def = FunctionDef(
            name="add",
            parameters=[
                Parameter(name="a", type_annotation="Int"),
                Parameter(name="b", type_annotation="Int"),
            ],
            return_type="Int",
        )
        result = generator.generate_function(func_def)
        assert "def add" in result
        assert "a: Int" in result
        assert "b: Int" in result
        assert ": Int" in result

    def test_function_with_type_params(self, generator: ScalaCodeGenerator) -> None:
        """Test function with type parameters."""
        from ir_core.models import FunctionDef, Parameter

        func_def = FunctionDef(
            name="identity",
            parameters=[Parameter(name="x", type_annotation="A")],
            return_type="A",
            metadata={"type_params": [{"name": "A"}]},
        )
        result = generator.generate_function(func_def)
        assert "def identity[A]" in result

    def test_function_with_implicits(self, generator: ScalaCodeGenerator) -> None:
        """Test function with implicit parameters."""
        from ir_core.models import FunctionDef, Parameter

        func_def = FunctionDef(
            name="sort",
            parameters=[Parameter(name="list", type_annotation="List[T]")],
            return_type="List[T]",
            metadata={
                "type_params": [{"name": "T"}],
                "implicit_params": [{"name": "ord", "type": "Ordering[T]"}],
            },
        )
        result = generator.generate_function(func_def)
        assert "def sort[T]" in result
        assert "using" in result
        assert "Ordering[T]" in result


class TestPatternMatch:
    """Tests for pattern match generation."""

    def test_simple_match(self, generator: ScalaCodeGenerator) -> None:
        """Test simple pattern match."""
        result = generator.generate_pattern_match(
            "x",
            [
                ("0", '"zero"'),
                ("1", '"one"'),
                ("_", '"many"'),
            ],
        )
        assert "x match {" in result
        assert 'case 0 => "zero"' in result
        assert 'case 1 => "one"' in result
        assert 'case _ => "many"' in result


class TestForComprehension:
    """Tests for for comprehension generation."""

    def test_simple_for(self, generator: ScalaCodeGenerator) -> None:
        """Test simple for comprehension."""
        result = generator.generate_for_comprehension(
            [("x", "xs"), ("y", "ys")],
            "(x, y)",
        )
        assert "for {" in result
        assert "x <- xs" in result
        assert "y <- ys" in result
        assert "yield (x, y)" in result


class TestGivenGeneration:
    """Tests for given instance generation."""

    def test_named_given(self, generator: ScalaCodeGenerator) -> None:
        """Test named given instance."""
        result = generator.generate_given("intOrd", "Ordering[Int]")
        assert "given intOrd: Ordering[Int]" in result

    def test_anonymous_given(self, generator: ScalaCodeGenerator) -> None:
        """Test anonymous given instance."""
        result = generator.generate_given(None, "Ordering[String]")
        assert "given Ordering[String]" in result
