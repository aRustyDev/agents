"""Tests for the Rust code generator."""

import pytest

from ir_core.models import (
    Field_,
    Function,
    Param,
    TypeDef,
    TypeKind,
    TypeParam,
    TypeRef,
    TypeRefKind,
    TypeBody,
    Variant,
    Visibility,
)

from ir_synthesize_rust.generator import RustCodeGenerator, SynthesisContext


@pytest.fixture
def generator():
    """Create a code generator."""
    return RustCodeGenerator()


@pytest.fixture
def context():
    """Create a synthesis context."""
    return SynthesisContext()


class TestTypeRefGeneration:
    """Tests for type reference generation."""

    def test_simple_type(self, generator, context):
        """Test simple type generation."""
        type_ref = TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.int")
        result = generator.gen_type_ref(type_ref, context)
        assert result == "i64"

    def test_string_type(self, generator, context):
        """Test String type generation."""
        type_ref = TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.str")
        result = generator.gen_type_ref(type_ref, context)
        assert result == "String"

    def test_generic_type(self, generator, context):
        """Test generic type generation."""
        type_ref = TypeRef(
            kind=TypeRefKind.NAMED,
            type_id="builtins.list",
            args=[TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.int")],
        )
        result = generator.gen_type_ref(type_ref, context)
        assert result == "Vec<i64>"

    def test_reference_type(self, generator, context):
        """Test reference type generation."""
        type_ref = TypeRef(
            kind=TypeRefKind.REFERENCE,
            type_id="builtins.str",
            mutable=False,
        )
        result = generator.gen_type_ref(type_ref, context)
        assert "&" in result

    def test_mutable_reference(self, generator, context):
        """Test mutable reference generation."""
        type_ref = TypeRef(
            kind=TypeRefKind.REFERENCE,
            type_id="builtins.str",
            mutable=True,
        )
        result = generator.gen_type_ref(type_ref, context)
        assert "&mut" in result

    def test_tuple_type(self, generator, context):
        """Test tuple type generation."""
        type_ref = TypeRef(
            kind=TypeRefKind.TUPLE,
            elements=[
                TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.int"),
                TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.str"),
            ],
        )
        result = generator.gen_type_ref(type_ref, context)
        assert result == "(i64, String)"

    def test_function_type(self, generator, context):
        """Test function type generation."""
        type_ref = TypeRef(
            kind=TypeRefKind.FUNCTION,
            params=[TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.int")],
            return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.int"),
        )
        result = generator.gen_type_ref(type_ref, context)
        assert "fn" in result
        assert "->" in result


class TestStructGeneration:
    """Tests for struct generation."""

    def test_simple_struct(self, generator, context):
        """Test simple struct generation."""
        type_def = TypeDef(
            id="type:1",
            name="Point",
            kind=TypeKind.STRUCT,
            visibility=Visibility.PUBLIC,
            body=TypeBody(
                fields=[
                    Field_(
                        name="x",
                        type=TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.float"),
                        visibility=Visibility.PUBLIC,
                    ),
                    Field_(
                        name="y",
                        type=TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.float"),
                        visibility=Visibility.PUBLIC,
                    ),
                ]
            ),
        )
        result = generator.gen_struct(type_def, context)
        assert "pub struct Point" in result
        assert "x: f64" in result
        assert "y: f64" in result

    def test_generic_struct(self, generator, context):
        """Test generic struct generation."""
        type_def = TypeDef(
            id="type:1",
            name="Container",
            kind=TypeKind.STRUCT,
            params=[TypeParam(name="T", bounds=[])],
            body=TypeBody(
                fields=[
                    Field_(
                        name="value",
                        type=TypeRef(kind=TypeRefKind.GENERIC, type_id="T"),
                        visibility=Visibility.PRIVATE,
                    ),
                ]
            ),
        )
        result = generator.gen_struct(type_def, context)
        assert "struct Container<T>" in result


class TestEnumGeneration:
    """Tests for enum generation."""

    def test_simple_enum(self, generator, context):
        """Test simple enum generation."""
        type_def = TypeDef(
            id="type:1",
            name="Direction",
            kind=TypeKind.ENUM,
            visibility=Visibility.PUBLIC,
            body=TypeBody(
                variants=[
                    Variant(name="North", kind="unit"),
                    Variant(name="South", kind="unit"),
                    Variant(name="East", kind="unit"),
                    Variant(name="West", kind="unit"),
                ]
            ),
        )
        result = generator.gen_enum(type_def, context)
        assert "pub enum Direction" in result
        assert "North" in result
        assert "South" in result

    def test_tuple_variant(self, generator, context):
        """Test enum with tuple variant."""
        type_def = TypeDef(
            id="type:1",
            name="Event",
            kind=TypeKind.ENUM,
            body=TypeBody(
                variants=[
                    Variant(
                        name="Click",
                        kind="tuple",
                        types=[
                            TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.int"),
                            TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.int"),
                        ],
                    ),
                ]
            ),
        )
        result = generator.gen_enum(type_def, context)
        assert "Click(i64, i64)" in result


class TestFunctionGeneration:
    """Tests for function generation."""

    def test_simple_function(self, generator, context):
        """Test simple function generation."""
        func = Function(
            id="func:1",
            name="add",
            params=[
                Param(
                    name="a",
                    type=TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.int"),
                ),
                Param(
                    name="b",
                    type=TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.int"),
                ),
            ],
            return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.int"),
            visibility=Visibility.PUBLIC,
        )
        result = generator.gen_function(func, context)
        assert "pub fn add" in result
        assert "a:" in result
        assert "b:" in result
        assert "-> i64" in result

    def test_generic_function(self, generator, context):
        """Test generic function generation."""
        func = Function(
            id="func:1",
            name="identity",
            type_params=[TypeParam(name="T", bounds=[])],
            params=[
                Param(
                    name="x",
                    type=TypeRef(kind=TypeRefKind.GENERIC, type_id="T"),
                ),
            ],
            return_type=TypeRef(kind=TypeRefKind.GENERIC, type_id="T"),
        )
        result = generator.gen_function(func, context)
        assert "fn identity<T>" in result
