"""Tests for Scala parser."""

from __future__ import annotations

import pytest

from ir_extract_scala.parser import (
    ScalaParser,
    TypeParamKind,
    Variance,
)


@pytest.fixture
def parser() -> ScalaParser:
    """Create a parser instance."""
    return ScalaParser()


class TestPackageParsing:
    """Tests for package declaration parsing."""

    def test_simple_package(self, parser: ScalaParser) -> None:
        """Test simple package declaration."""
        source = "package com.example"
        module = parser.parse(source)
        assert module.package == "com.example"

    def test_nested_package(self, parser: ScalaParser) -> None:
        """Test nested package declaration."""
        source = "package com.example.app.core"
        module = parser.parse(source)
        assert module.package == "com.example.app.core"


class TestImportParsing:
    """Tests for import statement parsing."""

    def test_simple_import(self, parser: ScalaParser) -> None:
        """Test simple import."""
        source = "import scala.collection.mutable"
        module = parser.parse(source)
        assert len(module.imports) == 1
        assert module.imports[0].path == "scala.collection.mutable"

    def test_wildcard_import(self, parser: ScalaParser) -> None:
        """Test wildcard import."""
        source = "import scala.collection.mutable.*"
        module = parser.parse(source)
        assert len(module.imports) == 1
        assert module.imports[0].is_wildcard

    def test_selective_import(self, parser: ScalaParser) -> None:
        """Test selective import."""
        source = "import scala.collection.{List, Map, Set}"
        module = parser.parse(source)
        assert len(module.imports) == 1
        assert "List" in module.imports[0].selectors
        assert "Map" in module.imports[0].selectors


class TestTraitParsing:
    """Tests for trait parsing."""

    def test_simple_trait(self, parser: ScalaParser) -> None:
        """Test simple trait."""
        source = """
trait Greeting {
  def greet(name: String): String
}
"""
        module = parser.parse(source)
        assert len(module.traits) == 1
        assert module.traits[0].name == "Greeting"

    def test_trait_with_type_param(self, parser: ScalaParser) -> None:
        """Test trait with type parameter."""
        source = """
trait Container[T] {
  def get: T
  def set(value: T): Unit
}
"""
        module = parser.parse(source)
        assert len(module.traits) == 1
        assert len(module.traits[0].type_params) == 1
        assert module.traits[0].type_params[0].name == "T"

    def test_trait_with_covariant_param(self, parser: ScalaParser) -> None:
        """Test trait with covariant type parameter."""
        source = """
trait Producer[+T] {
  def produce: T
}
"""
        module = parser.parse(source)
        assert len(module.traits) == 1
        param = module.traits[0].type_params[0]
        assert param.name == "T"
        assert param.variance == Variance.COVARIANT

    def test_trait_with_contravariant_param(self, parser: ScalaParser) -> None:
        """Test trait with contravariant type parameter."""
        source = """
trait Consumer[-T] {
  def consume(value: T): Unit
}
"""
        module = parser.parse(source)
        assert len(module.traits) == 1
        param = module.traits[0].type_params[0]
        assert param.name == "T"
        assert param.variance == Variance.CONTRAVARIANT

    def test_trait_with_hkt(self, parser: ScalaParser) -> None:
        """Test trait with higher-kinded type parameter."""
        source = """
trait Functor[F[_]] {
  def map[A, B](fa: F[A])(f: A => B): F[B]
}
"""
        module = parser.parse(source)
        assert len(module.traits) == 1
        param = module.traits[0].type_params[0]
        assert param.name == "F"
        assert param.kind == TypeParamKind.HIGHER_KINDED
        assert param.arity == 1

    def test_sealed_trait(self, parser: ScalaParser) -> None:
        """Test sealed trait."""
        source = """
sealed trait Option[+A] {
}
"""
        module = parser.parse(source)
        assert len(module.traits) == 1


class TestCaseClassParsing:
    """Tests for case class parsing."""

    def test_simple_case_class(self, parser: ScalaParser) -> None:
        """Test simple case class."""
        source = "case class Point(x: Int, y: Int)"
        module = parser.parse(source)
        assert len(module.case_classes) == 1
        cc = module.case_classes[0]
        assert cc.name == "Point"
        assert len(cc.fields) == 2

    def test_case_class_with_defaults(self, parser: ScalaParser) -> None:
        """Test case class with default values."""
        source = 'case class Config(host: String = "localhost", port: Int = 8080)'
        module = parser.parse(source)
        assert len(module.case_classes) == 1
        cc = module.case_classes[0]
        assert cc.fields[0].default_value == '"localhost"'
        assert cc.fields[1].default_value == "8080"

    def test_case_class_with_type_params(self, parser: ScalaParser) -> None:
        """Test case class with type parameters."""
        source = "case class Pair[A, B](first: A, second: B)"
        module = parser.parse(source)
        assert len(module.case_classes) == 1
        cc = module.case_classes[0]
        assert len(cc.type_params) == 2


class TestClassParsing:
    """Tests for class parsing."""

    def test_simple_class(self, parser: ScalaParser) -> None:
        """Test simple class."""
        source = """
class Counter(initial: Int) {
  private var count = initial
  def increment(): Unit = count += 1
  def get: Int = count
}
"""
        module = parser.parse(source)
        assert len(module.classes) == 1
        cls = module.classes[0]
        assert cls.name == "Counter"

    def test_abstract_class(self, parser: ScalaParser) -> None:
        """Test abstract class."""
        source = """
abstract class Animal {
  def speak: String
}
"""
        module = parser.parse(source)
        assert len(module.classes) == 1
        assert module.classes[0].is_abstract

    def test_sealed_class(self, parser: ScalaParser) -> None:
        """Test sealed class."""
        source = """
sealed class Result {
}
"""
        module = parser.parse(source)
        assert len(module.classes) == 1
        assert module.classes[0].is_sealed


class TestObjectParsing:
    """Tests for object parsing."""

    def test_simple_object(self, parser: ScalaParser) -> None:
        """Test simple object."""
        source = """
object MathUtils {
  def square(x: Int): Int = x * x
}
"""
        module = parser.parse(source)
        assert len(module.objects) == 1
        assert module.objects[0].name == "MathUtils"

    def test_object_extends(self, parser: ScalaParser) -> None:
        """Test object extending trait."""
        source = """
object StringOrdering extends Ordering[String] {
  def compare(x: String, y: String): Int = x.compareTo(y)
}
"""
        module = parser.parse(source)
        assert len(module.objects) == 1
        assert "Ordering[String]" in module.objects[0].extends


class TestMethodParsing:
    """Tests for method parsing."""

    def test_simple_method(self, parser: ScalaParser) -> None:
        """Test simple method."""
        source = """
trait Example {
  def add(a: Int, b: Int): Int = a + b
}
"""
        module = parser.parse(source)
        methods = module.traits[0].methods
        assert len(methods) >= 1

    def test_method_with_type_params(self, parser: ScalaParser) -> None:
        """Test method with type parameters."""
        source = """
trait Container {
  def map[A, B](f: A => B): Container
}
"""
        module = parser.parse(source)
        methods = module.traits[0].methods
        assert len(methods) >= 1

    def test_method_with_implicit_param(self, parser: ScalaParser) -> None:
        """Test method with implicit parameter."""
        source = """
trait Sortable {
  def sort[T](list: List[T])(implicit ord: Ordering[T]): List[T]
}
"""
        module = parser.parse(source)
        methods = module.traits[0].methods
        assert len(methods) >= 1


class TestGivenParsing:
    """Tests for given instance parsing."""

    def test_named_given(self, parser: ScalaParser) -> None:
        """Test named given instance."""
        source = """
given intOrd: Ordering[Int] with
  def compare(x: Int, y: Int): Int = x - y
"""
        module = parser.parse(source)
        assert len(module.givens) == 1
        assert module.givens[0].name == "intOrd"
        assert "Ordering[Int]" in module.givens[0].type_expr

    def test_anonymous_given(self, parser: ScalaParser) -> None:
        """Test anonymous given instance."""
        source = """
given Ordering[String] with
  def compare(x: String, y: String): Int = x.compareTo(y)
"""
        module = parser.parse(source)
        assert len(module.givens) == 1


class TestTypeParameterParsing:
    """Tests for type parameter parsing."""

    def test_upper_bound(self, parser: ScalaParser) -> None:
        """Test upper bound."""
        source = """
trait Container[T <: AnyRef] {
}
"""
        module = parser.parse(source)
        params = module.traits[0].type_params
        assert len(params) == 1

    def test_multiple_type_params(self, parser: ScalaParser) -> None:
        """Test multiple type parameters."""
        source = """
trait BiFunction[A, B, C] {
  def apply(a: A, b: B): C
}
"""
        module = parser.parse(source)
        params = module.traits[0].type_params
        assert len(params) == 3
        assert params[0].name == "A"
        assert params[1].name == "B"
        assert params[2].name == "C"
