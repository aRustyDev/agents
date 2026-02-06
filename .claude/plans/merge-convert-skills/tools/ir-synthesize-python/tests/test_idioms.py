"""Tests for the Python idiom generator."""

from __future__ import annotations

import pytest
from datetime import datetime, timezone

from ir_core.base import SynthConfig
from ir_core.models import (
    IRVersion,
    Module,
    ModuleMetadata,
    TypeDef,
    TypeKind,
    TypeBody,
    TypeRef,
    TypeRefKind,
    Field_,
    Visibility,
    ExtractionMode,
)

from ir_synthesize_python.synthesizer import SynthesisContext, PreservationMode
from ir_synthesize_python.idioms import (
    PythonIdiomGenerator,
    IdiomKind,
    Pattern,
)


@pytest.fixture
def idiom_gen() -> PythonIdiomGenerator:
    """Create an idiom generator instance."""
    return PythonIdiomGenerator(target_version="3.11")


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
                extraction_timestamp=datetime.now(timezone.utc),
            ),
        ),
        types=[],
        functions=[],
    )

    return SynthesisContext(
        ir=ir,
        config=SynthConfig(emit_type_hints=True),
        mode=PreservationMode.IDIOMATIC,
        imports_needed=set(),
        gaps=[],
        type_map={"int": "int", "str": "str", "float": "float"},
    )


class TestComprehensionGeneration:
    """Tests for comprehension generation."""

    def test_list_comprehension(self, idiom_gen: PythonIdiomGenerator) -> None:
        """Test generating a list comprehension."""
        pattern = Pattern(
            kind=IdiomKind.LIST_COMPREHENSION,
            source=None,
            metadata={
                "transform": "x * 2",
                "iterable": "numbers",
                "var": "x",
            },
        )

        result = idiom_gen.gen_comprehension(pattern)

        assert result.success
        assert result.code == "[x * 2 for x in numbers]"

    def test_list_comprehension_with_filter(self, idiom_gen: PythonIdiomGenerator) -> None:
        """Test generating a list comprehension with filter."""
        pattern = Pattern(
            kind=IdiomKind.LIST_COMPREHENSION,
            source=None,
            metadata={
                "transform": "x * 2",
                "iterable": "numbers",
                "var": "x",
                "filter": "x > 0",
            },
        )

        result = idiom_gen.gen_comprehension(pattern)

        assert result.success
        assert result.code == "[x * 2 for x in numbers if x > 0]"

    def test_dict_comprehension(self, idiom_gen: PythonIdiomGenerator) -> None:
        """Test generating a dict comprehension."""
        pattern = Pattern(
            kind=IdiomKind.DICT_COMPREHENSION,
            source=None,
            metadata={
                "key": "k",
                "value": "v * 2",
                "iterable": "items.items()",
                "var": "k, v",
            },
        )

        result = idiom_gen.gen_comprehension(pattern)

        assert result.success
        assert result.code == "{k: v * 2 for k, v in items.items()}"

    def test_set_comprehension(self, idiom_gen: PythonIdiomGenerator) -> None:
        """Test generating a set comprehension."""
        pattern = Pattern(
            kind=IdiomKind.SET_COMPREHENSION,
            source=None,
            metadata={
                "transform": "x.lower()",
                "iterable": "words",
                "var": "x",
            },
        )

        result = idiom_gen.gen_comprehension(pattern)

        assert result.success
        assert result.code == "{x.lower() for x in words}"

    def test_generator_expression(self, idiom_gen: PythonIdiomGenerator) -> None:
        """Test generating a generator expression."""
        pattern = Pattern(
            kind=IdiomKind.GENERATOR_EXPRESSION,
            source=None,
            metadata={
                "transform": "x ** 2",
                "iterable": "range(10)",
                "var": "x",
            },
        )

        result = idiom_gen.gen_comprehension(pattern)

        assert result.success
        assert result.code == "(x ** 2 for x in range(10))"


class TestContextManagerGeneration:
    """Tests for context manager generation."""

    def test_simple_context_manager(self, idiom_gen: PythonIdiomGenerator) -> None:
        """Test generating a simple context manager."""
        pattern = Pattern(
            kind=IdiomKind.CONTEXT_MANAGER,
            source=None,
            metadata={
                "resource_expr": 'open("file.txt")',
                "resource_name": "f",
                "body": "data = f.read()",
            },
        )

        result = idiom_gen.gen_context_manager(pattern)

        assert result.success
        assert 'with open("file.txt") as f:' in result.code
        assert "data = f.read()" in result.code


class TestDataclassGeneration:
    """Tests for dataclass generation."""

    def test_simple_dataclass(
        self, idiom_gen: PythonIdiomGenerator, context: SynthesisContext
    ) -> None:
        """Test generating a simple dataclass."""
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

        result = idiom_gen.gen_dataclass(type_def, context)

        assert result.success
        assert "@dataclass" in result.code
        assert "class Point:" in result.code
        assert "x: float" in result.code
        assert "y: float" in result.code
        assert "dataclasses.dataclass" in result.imports_needed


class TestAsyncPatternGeneration:
    """Tests for async pattern generation."""

    def test_await_expression(self, idiom_gen: PythonIdiomGenerator) -> None:
        """Test generating an await expression."""
        pattern = Pattern(
            kind=IdiomKind.ASYNC_AWAIT,
            source=None,
            metadata={
                "type": "await",
                "expression": "fetch_data()",
            },
        )

        result = idiom_gen.gen_async_pattern(pattern)

        assert result.success
        assert result.code == "await fetch_data()"

    def test_async_for(self, idiom_gen: PythonIdiomGenerator) -> None:
        """Test generating an async for loop."""
        pattern = Pattern(
            kind=IdiomKind.ASYNC_AWAIT,
            source=None,
            metadata={
                "type": "async_for",
                "var": "item",
                "iterable": "async_stream()",
                "body": "process(item)",
            },
        )

        result = idiom_gen.gen_async_pattern(pattern)

        assert result.success
        assert "async for item in async_stream():" in result.code
        assert "process(item)" in result.code

    def test_async_with(self, idiom_gen: PythonIdiomGenerator) -> None:
        """Test generating an async with statement."""
        pattern = Pattern(
            kind=IdiomKind.ASYNC_AWAIT,
            source=None,
            metadata={
                "type": "async_with",
                "resource": "aiofiles.open('file.txt')",
                "name": "f",
                "body": "data = await f.read()",
            },
        )

        result = idiom_gen.gen_async_pattern(pattern)

        assert result.success
        assert "async with aiofiles.open('file.txt') as f:" in result.code

    def test_asyncio_gather(self, idiom_gen: PythonIdiomGenerator) -> None:
        """Test generating asyncio.gather pattern."""
        pattern = Pattern(
            kind=IdiomKind.ASYNC_AWAIT,
            source=None,
            metadata={
                "type": "gather",
                "tasks": ["fetch_a()", "fetch_b()", "fetch_c()"],
            },
        )

        result = idiom_gen.gen_async_pattern(pattern)

        assert result.success
        assert "await asyncio.gather(fetch_a(), fetch_b(), fetch_c())" in result.code
        assert "asyncio" in result.imports_needed


class TestPatternMatchingGeneration:
    """Tests for pattern matching generation."""

    def test_match_statement_python_310(self, idiom_gen: PythonIdiomGenerator) -> None:
        """Test generating a match statement (Python 3.10+)."""
        pattern = Pattern(
            kind=IdiomKind.PATTERN_MATCHING,
            source=None,
            metadata={
                "subject": "command",
                "cases": [
                    {"pattern": '"start"', "body": "start_process()"},
                    {"pattern": '"stop"', "body": "stop_process()"},
                    {"pattern": "_", "body": "unknown_command()"},
                ],
            },
        )

        result = idiom_gen.gen_pattern_match(pattern)

        assert result.success
        assert "match command:" in result.code
        assert 'case "start":' in result.code
        assert 'case "stop":' in result.code
        assert "case _:" in result.code

    def test_match_with_guard(self, idiom_gen: PythonIdiomGenerator) -> None:
        """Test generating a match statement with guard."""
        pattern = Pattern(
            kind=IdiomKind.PATTERN_MATCHING,
            source=None,
            metadata={
                "subject": "value",
                "cases": [
                    {"pattern": "x", "guard": "x > 0", "body": "positive(x)"},
                    {"pattern": "_", "body": "other()"},
                ],
            },
        )

        result = idiom_gen.gen_pattern_match(pattern)

        assert result.success
        assert "if x > 0:" in result.code

    def test_match_fallback_for_old_python(self) -> None:
        """Test that match falls back to if/elif for Python < 3.10."""
        idiom_gen = PythonIdiomGenerator(target_version="3.9")

        pattern = Pattern(
            kind=IdiomKind.PATTERN_MATCHING,
            source=None,
            metadata={
                "subject": "value",
                "cases": [
                    {"pattern": "1", "body": "one()"},
                    {"pattern": "2", "body": "two()"},
                    {"pattern": "_", "body": "other()"},
                ],
            },
        )

        result = idiom_gen.gen_pattern_match(pattern)

        assert result.success
        assert "if" in result.code
        assert "elif" in result.code
        assert any("pre-Python 3.10" in note for note in result.notes)


class TestDecoratorGeneration:
    """Tests for decorator pattern generation."""

    def test_simple_decorator(self, idiom_gen: PythonIdiomGenerator) -> None:
        """Test generating a simple decorator."""
        pattern = Pattern(
            kind=IdiomKind.DECORATOR,
            source=None,
            metadata={
                "type": "simple",
                "name": "timer",
                "wrapper_body": "start = time.time()\nresult = func(*args, **kwargs)\nprint(f'Time: {time.time() - start}')\nreturn result",
            },
        )

        result = idiom_gen.gen_decorator_pattern(pattern)

        assert result.success
        assert "def timer(func):" in result.code
        assert "@functools.wraps(func)" in result.code
        assert "def wrapper(*args, **kwargs):" in result.code
        assert "functools" in result.imports_needed

    def test_parametrized_decorator(self, idiom_gen: PythonIdiomGenerator) -> None:
        """Test generating a parametrized decorator."""
        pattern = Pattern(
            kind=IdiomKind.DECORATOR,
            source=None,
            metadata={
                "type": "parametrized",
                "name": "retry",
                "params": ["max_attempts", "delay"],
                "wrapper_body": "for i in range(max_attempts): ...",
            },
        )

        result = idiom_gen.gen_decorator_pattern(pattern)

        assert result.success
        assert "def retry(max_attempts, delay):" in result.code
        assert "def decorator(func):" in result.code


class TestUnpackingGeneration:
    """Tests for unpacking pattern generation."""

    def test_simple_unpacking(self, idiom_gen: PythonIdiomGenerator) -> None:
        """Test generating simple tuple unpacking."""
        pattern = Pattern(
            kind=IdiomKind.UNPACKING,
            source=None,
            metadata={
                "source": "get_point()",
                "targets": ["x", "y"],
            },
        )

        result = idiom_gen.gen_unpacking(pattern)

        assert result.success
        assert result.code == "x, y = get_point()"

    def test_extended_unpacking(self, idiom_gen: PythonIdiomGenerator) -> None:
        """Test generating extended unpacking with *rest."""
        pattern = Pattern(
            kind=IdiomKind.UNPACKING,
            source=None,
            metadata={
                "source": "items",
                "targets": ["first", "second"],
                "rest": "rest",
            },
        )

        result = idiom_gen.gen_unpacking(pattern)

        assert result.success
        assert result.code == "first, *rest = items"


class TestWalrusOperator:
    """Tests for walrus operator generation."""

    def test_walrus_in_if(self, idiom_gen: PythonIdiomGenerator) -> None:
        """Test generating walrus operator in if statement."""
        pattern = Pattern(
            kind=IdiomKind.WALRUS,
            source=None,
            metadata={
                "target": "match",
                "value": "pattern.search(text)",
                "context": "if",
                "condition": "",
            },
        )

        result = idiom_gen.gen_walrus(pattern)

        assert result.success
        assert ":=" in result.code
        assert "match := pattern.search(text)" in result.code

    def test_walrus_requires_python_38(self) -> None:
        """Test that walrus operator fails for Python < 3.8."""
        idiom_gen = PythonIdiomGenerator(target_version="3.7")

        pattern = Pattern(
            kind=IdiomKind.WALRUS,
            source=None,
            metadata={
                "target": "x",
                "value": "compute()",
            },
        )

        result = idiom_gen.gen_walrus(pattern)

        assert not result.success
        assert any("3.8" in note for note in result.notes)


class TestFStringGeneration:
    """Tests for f-string generation."""

    def test_simple_f_string(self, idiom_gen: PythonIdiomGenerator) -> None:
        """Test generating a simple f-string."""
        pattern = Pattern(
            kind=IdiomKind.F_STRING,
            source=None,
            metadata={
                "template": "Hello, {name}!",
                "values": {"name": "name_var"},
            },
        )

        result = idiom_gen.gen_f_string(pattern)

        assert result.success
        assert 'f"Hello, {name}!"' in result.code


class TestVersionHandling:
    """Tests for Python version-specific handling."""

    def test_parse_version_dotted(self) -> None:
        """Test parsing dotted version string."""
        idiom_gen = PythonIdiomGenerator(target_version="3.10")
        assert idiom_gen._version_tuple == (3, 10)

    def test_parse_version_py_prefix(self) -> None:
        """Test parsing py-prefixed version string."""
        idiom_gen = PythonIdiomGenerator(target_version="py311")
        assert idiom_gen._version_tuple == (3, 11)

    def test_parse_version_short(self) -> None:
        """Test parsing short version string."""
        idiom_gen = PythonIdiomGenerator(target_version="39")
        assert idiom_gen._version_tuple == (3, 9)
