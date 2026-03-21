"""Tests for the Python code generator."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from ir_core.base import SynthConfig
from ir_core.models import (
    Effect,
    EffectKind,
    Expression,
    ExpressionKind,
    ExtractionMode,
    Field_,
    Function,
    IRVersion,
    Module,
    ModuleMetadata,
    Param,
    TypeBody,
    TypeDef,
    TypeKind,
    TypeRef,
    TypeRefKind,
    Visibility,
)
from ir_synthesize_python.generator import PythonCodeGenerator
from ir_synthesize_python.synthesizer import PreservationMode, SynthesisContext


@pytest.fixture
def generator() -> PythonCodeGenerator:
    """Create a code generator instance."""
    return PythonCodeGenerator()


@pytest.fixture
def context() -> SynthesisContext:
    """Create a synthesis context."""
    ir = IRVersion(
        version="ir-v1.0",
        module=Module(
            id="module:test",
            name="test",
            path=["test"],
            visibility=Visibility.PUBLIC,
            imports=[],
            exports=[],
            definitions=[],
            submodules=[],
            extraction_scope="full",
            metadata=ModuleMetadata(
                source_file="test.py",
                source_language="python",
                extraction_version="ir-v1.0",
                extraction_mode=ExtractionMode.FULL_MODULE,
                extraction_timestamp=datetime.now(UTC),
            ),
        ),
        types=[],
        functions=[],
    )

    return SynthesisContext(
        ir=ir,
        config=SynthConfig(
            emit_type_hints=True,
            emit_docstrings=True,
        ),
        mode=PreservationMode.IDIOMATIC,
        imports_needed=set(),
        gaps=[],
        type_map={
            "str": "str",
            "int": "int",
            "float": "float",
            "bool": "bool",
            "None": "None",
            "typing.Any": "Any",
            "builtins.str": "str",
            "builtins.int": "int",
        },
    )


class TestTypeAnnotationGeneration:
    """Tests for type annotation generation."""

    def test_simple_type(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating simple type annotations."""
        type_ref = TypeRef(kind=TypeRefKind.NAMED, type_id="str")
        result = generator.gen_type_annotation(type_ref, context)
        assert result == "str"

    def test_builtin_type(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating builtin type annotations."""
        type_ref = TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.int")
        result = generator.gen_type_annotation(type_ref, context)
        assert result == "int"

    def test_generic_type(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating generic type annotations."""
        type_ref = TypeRef(
            kind=TypeRefKind.NAMED,
            type_id="list",
            args=[TypeRef(kind=TypeRefKind.NAMED, type_id="str")],
        )
        result = generator.gen_type_annotation(type_ref, context)
        assert result == "list[str]"

    def test_nested_generic_type(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating nested generic type annotations."""
        type_ref = TypeRef(
            kind=TypeRefKind.NAMED,
            type_id="dict",
            args=[
                TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
                TypeRef(
                    kind=TypeRefKind.NAMED,
                    type_id="list",
                    args=[TypeRef(kind=TypeRefKind.NAMED, type_id="int")],
                ),
            ],
        )
        result = generator.gen_type_annotation(type_ref, context)
        assert result == "dict[str, list[int]]"

    def test_union_type(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating union type annotations."""
        type_ref = TypeRef(
            kind=TypeRefKind.UNION,
            members=[
                TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
                TypeRef(kind=TypeRefKind.NAMED, type_id="int"),
            ],
        )
        result = generator.gen_type_annotation(type_ref, context)
        assert result == "str | int"

    def test_optional_type(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating optional (union with None) type annotations."""
        type_ref = TypeRef(
            kind=TypeRefKind.UNION,
            members=[
                TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
                TypeRef(kind=TypeRefKind.NAMED, type_id="None"),
            ],
        )
        result = generator.gen_type_annotation(type_ref, context)
        assert result == "str | None"

    def test_tuple_type(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating tuple type annotations."""
        type_ref = TypeRef(
            kind=TypeRefKind.TUPLE,
            elements=[
                TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
                TypeRef(kind=TypeRefKind.NAMED, type_id="int"),
                TypeRef(kind=TypeRefKind.NAMED, type_id="float"),
            ],
        )
        result = generator.gen_type_annotation(type_ref, context)
        assert result == "tuple[str, int, float]"

    def test_callable_type(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating callable type annotations."""
        type_ref = TypeRef(
            kind=TypeRefKind.FUNCTION,
            params=[
                TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
                TypeRef(kind=TypeRefKind.NAMED, type_id="int"),
            ],
            return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="bool"),
        )
        result = generator.gen_type_annotation(type_ref, context)
        assert result == "Callable[[str, int], bool]"
        assert "typing.Callable" in context.imports_needed

    def test_generic_type_parameter(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating generic type parameter annotations."""
        type_ref = TypeRef(kind=TypeRefKind.GENERIC, type_id="T")
        result = generator.gen_type_annotation(type_ref, context)
        assert result == "T"


class TestFunctionGeneration:
    """Tests for function code generation."""

    def test_simple_function(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating a simple function."""
        func = Function(
            id="func:test",
            name="greet",
            params=[
                Param(
                    name="name",
                    type=TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
                ),
            ],
            return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
            effects=[],
            visibility=Visibility.PUBLIC,
        )

        code = generator.gen_function(func, context)
        assert "def greet(name: str) -> str:" in code

    def test_function_with_multiple_params(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating a function with multiple parameters."""
        func = Function(
            id="func:test",
            name="add",
            params=[
                Param(
                    name="a",
                    type=TypeRef(kind=TypeRefKind.NAMED, type_id="int"),
                ),
                Param(
                    name="b",
                    type=TypeRef(kind=TypeRefKind.NAMED, type_id="int"),
                ),
            ],
            return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="int"),
            effects=[],
            visibility=Visibility.PUBLIC,
        )

        code = generator.gen_function(func, context)
        assert "def add(a: int, b: int) -> int:" in code

    def test_async_function(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating an async function."""
        func = Function(
            id="func:test",
            name="fetch",
            params=[],
            return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
            effects=[Effect(kind=EffectKind.ASYNC)],
            visibility=Visibility.PUBLIC,
        )

        code = generator.gen_function(func, context)
        assert "async def fetch() -> str:" in code

    def test_function_with_docstring(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating a function with a docstring."""
        func = Function(
            id="func:test",
            name="process",
            params=[],
            return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="None"),
            effects=[],
            visibility=Visibility.PUBLIC,
            doc_comment="Process the data.",
        )

        code = generator.gen_function(func, context)
        assert '"""Process the data."""' in code

    def test_function_with_variadic_args(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating a function with *args."""
        func = Function(
            id="func:test",
            name="collect",
            params=[
                Param(
                    name="args",
                    type=TypeRef(kind=TypeRefKind.NAMED, type_id="tuple"),
                    variadic=True,
                ),
            ],
            return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="list"),
            effects=[],
            visibility=Visibility.PUBLIC,
        )

        code = generator.gen_function(func, context)
        assert "*args" in code


class TestExpressionGeneration:
    """Tests for expression code generation."""

    def test_literal_string(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating string literal."""
        expr = Expression(
            id="expr:0",
            kind=ExpressionKind.LITERAL,
            literal_kind="string",
            literal_value="hello",
        )
        result = generator._gen_expression(expr, context)
        assert result == "'hello'"

    def test_literal_integer(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating integer literal."""
        expr = Expression(
            id="expr:0",
            kind=ExpressionKind.LITERAL,
            literal_kind="integer",
            literal_value=42,
        )
        result = generator._gen_expression(expr, context)
        assert result == "42"

    def test_literal_boolean(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating boolean literal."""
        expr = Expression(
            id="expr:0",
            kind=ExpressionKind.LITERAL,
            literal_kind="boolean",
            literal_value=True,
        )
        result = generator._gen_expression(expr, context)
        assert result == "True"

    def test_identifier(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating identifier."""
        expr = Expression(
            id="expr:0",
            kind=ExpressionKind.IDENTIFIER,
            name="variable",
        )
        result = generator._gen_expression(expr, context)
        assert result == "variable"

    def test_binary_operator(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating binary operator."""
        expr = Expression(
            id="expr:0",
            kind=ExpressionKind.OPERATOR,
            operator="add",
            operands=[
                Expression(
                    id="expr:1",
                    kind=ExpressionKind.IDENTIFIER,
                    name="a",
                ),
                Expression(
                    id="expr:2",
                    kind=ExpressionKind.IDENTIFIER,
                    name="b",
                ),
            ],
        )
        result = generator._gen_expression(expr, context)
        assert result == "a + b"

    def test_comparison_operator(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating comparison operator."""
        expr = Expression(
            id="expr:0",
            kind=ExpressionKind.OPERATOR,
            operator="eq",
            operands=[
                Expression(
                    id="expr:1",
                    kind=ExpressionKind.IDENTIFIER,
                    name="x",
                ),
                Expression(
                    id="expr:2",
                    kind=ExpressionKind.LITERAL,
                    literal_kind="integer",
                    literal_value=0,
                ),
            ],
        )
        result = generator._gen_expression(expr, context)
        assert result == "x == 0"

    def test_member_access(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating member access."""
        expr = Expression(
            id="expr:0",
            kind=ExpressionKind.MEMBER_ACCESS,
            object=Expression(
                id="expr:1",
                kind=ExpressionKind.IDENTIFIER,
                name="obj",
            ),
            member="field",
        )
        result = generator._gen_expression(expr, context)
        assert result == "obj.field"

    def test_index_access(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating index access."""
        expr = Expression(
            id="expr:0",
            kind=ExpressionKind.INDEX,
            collection=Expression(
                id="expr:1",
                kind=ExpressionKind.IDENTIFIER,
                name="items",
            ),
            index=Expression(
                id="expr:2",
                kind=ExpressionKind.LITERAL,
                literal_kind="integer",
                literal_value=0,
            ),
        )
        result = generator._gen_expression(expr, context)
        assert result == "items[0]"

    def test_conditional_expression(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating conditional expression."""
        expr = Expression(
            id="expr:0",
            kind=ExpressionKind.CONDITIONAL,
            condition=Expression(
                id="expr:1",
                kind=ExpressionKind.IDENTIFIER,
                name="flag",
            ),
            then_expr=Expression(
                id="expr:2",
                kind=ExpressionKind.LITERAL,
                literal_kind="string",
                literal_value="yes",
            ),
            else_expr=Expression(
                id="expr:3",
                kind=ExpressionKind.LITERAL,
                literal_kind="string",
                literal_value="no",
            ),
        )
        result = generator._gen_expression(expr, context)
        assert result == "'yes' if flag else 'no'"

    def test_await_expression(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating await expression."""
        expr = Expression(
            id="expr:0",
            kind=ExpressionKind.AWAIT,
            operand=Expression(
                id="expr:1",
                kind=ExpressionKind.IDENTIFIER,
                name="coro",
            ),
        )
        result = generator._gen_expression(expr, context)
        assert result == "await coro"


class TestClassGeneration:
    """Tests for class code generation."""

    def test_simple_class(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating a simple class."""
        type_def = TypeDef(
            id="type:test",
            name="MyClass",
            kind=TypeKind.CLASS,
            body=TypeBody(
                fields=[
                    Field_(
                        name="value",
                        type=TypeRef(kind=TypeRefKind.NAMED, type_id="int"),
                        visibility=Visibility.PUBLIC,
                    ),
                ],
            ),
            visibility=Visibility.PUBLIC,
        )

        code = generator.gen_class(type_def, context)
        assert "class MyClass:" in code
        assert "value: int" in code

    def test_dataclass(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating a dataclass."""
        type_def = TypeDef(
            id="type:test",
            name="Point",
            kind=TypeKind.STRUCT,
            body=TypeBody(
                fields=[
                    Field_(
                        name="x",
                        type=TypeRef(kind=TypeRefKind.NAMED, type_id="float"),
                        visibility=Visibility.PUBLIC,
                    ),
                    Field_(
                        name="y",
                        type=TypeRef(kind=TypeRefKind.NAMED, type_id="float"),
                        visibility=Visibility.PUBLIC,
                    ),
                ],
            ),
            visibility=Visibility.PUBLIC,
        )

        code = generator.gen_class(type_def, context)
        assert "@dataclass" in code
        assert "class Point:" in code
        assert "x: float" in code
        assert "y: float" in code

    def test_protocol(
        self, generator: PythonCodeGenerator, context: SynthesisContext
    ) -> None:
        """Test generating a Protocol."""
        from ir_core.models import MethodSignature

        type_def = TypeDef(
            id="type:test",
            name="Drawable",
            kind=TypeKind.INTERFACE,
            body=TypeBody(
                required_methods=[
                    MethodSignature(
                        name="draw",
                        params=[],
                        return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="None"),
                    ),
                ],
            ),
            visibility=Visibility.PUBLIC,
        )

        code = generator.gen_class(type_def, context)
        assert "class Drawable" in code
        assert "(Protocol)" in code
        assert "def draw" in code


class TestIndentation:
    """Tests for code indentation."""

    def test_indent_single_level(self, generator: PythonCodeGenerator) -> None:
        """Test single level indentation."""
        code = "x = 1"
        result = generator.indent(code, level=1)
        assert result == "    x = 1"

    def test_indent_multiple_levels(self, generator: PythonCodeGenerator) -> None:
        """Test multiple level indentation."""
        code = "x = 1"
        result = generator.indent(code, level=2)
        assert result == "        x = 1"

    def test_indent_multiline(self, generator: PythonCodeGenerator) -> None:
        """Test indenting multiple lines."""
        code = "x = 1\ny = 2"
        result = generator.indent(code, level=1)
        assert result == "    x = 1\n    y = 2"

    def test_indent_preserves_empty_lines(self, generator: PythonCodeGenerator) -> None:
        """Test that empty lines are preserved without trailing spaces."""
        code = "x = 1\n\ny = 2"
        result = generator.indent(code, level=1)
        lines = result.split("\n")
        assert lines[1] == ""  # Empty line has no trailing spaces
