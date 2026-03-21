"""Tests for the PythonPatternMatcher class."""

from __future__ import annotations

import pytest
from ir_core.models import AutomationLevel
from ir_extract_python import PythonParser, PythonPatternMatcher
from ir_extract_python.patterns import PatternKind


@pytest.fixture
def parser() -> PythonParser:
    """Create a PythonParser instance."""
    return PythonParser()


@pytest.fixture
def matcher() -> PythonPatternMatcher:
    """Create a PythonPatternMatcher instance."""
    return PythonPatternMatcher()


class TestComprehensionPatterns:
    """Test comprehension pattern detection."""

    def test_detect_list_comprehension(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting list comprehensions."""
        source = "squares = [x**2 for x in range(10)]"
        tree = parser.parse(source, "comp.py")
        patterns = matcher.detect_comprehensions(tree.root)

        assert len(patterns) == 1
        assert patterns[0].kind == PatternKind.LIST_COMPREHENSION

    def test_detect_dict_comprehension(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting dictionary comprehensions."""
        source = "mapping = {k: v for k, v in pairs}"
        tree = parser.parse(source, "comp.py")
        patterns = matcher.detect_comprehensions(tree.root)

        assert len(patterns) == 1
        assert patterns[0].kind == PatternKind.DICT_COMPREHENSION

    def test_detect_nested_comprehension(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting nested comprehensions."""
        source = "matrix = [[i*j for j in range(5)] for i in range(5)]"
        tree = parser.parse(source, "comp.py")
        patterns = matcher.detect_comprehensions(tree.root)

        # Should find 2 list comprehensions (outer and inner)
        assert len(patterns) == 2

    def test_comprehension_with_condition(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test comprehension with condition details."""
        source = "evens = [x for x in range(10) if x % 2 == 0]"
        tree = parser.parse(source, "comp.py")
        patterns = matcher.detect_comprehensions(tree.root)

        assert len(patterns) == 1
        assert patterns[0].details.get("condition_count") == "1"


class TestDecoratorPatterns:
    """Test decorator pattern detection."""

    def test_detect_simple_decorator(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting simple decorators."""
        source = """
@decorator
def func():
    pass
"""
        tree = parser.parse(source, "dec.py")
        patterns = matcher.detect_decorators(tree.root)

        assert len(patterns) == 1
        assert patterns[0].kind == PatternKind.DECORATOR

    def test_detect_decorator_factory(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting decorator factories."""
        source = """
@decorator(arg1, arg2)
def func():
    pass
"""
        tree = parser.parse(source, "dec.py")
        patterns = matcher.detect_decorators(tree.root)

        assert len(patterns) == 1
        assert patterns[0].kind == PatternKind.DECORATOR_FACTORY

    def test_detect_property_decorator(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting @property decorator."""
        source = """
class MyClass:
    @property
    def value(self):
        return self._value
"""
        tree = parser.parse(source, "prop.py")
        patterns = matcher.detect_decorators(tree.root)

        assert len(patterns) == 1
        assert patterns[0].kind == PatternKind.PROPERTY_DECORATOR

    def test_detect_classmethod_decorator(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting @classmethod decorator."""
        source = """
class MyClass:
    @classmethod
    def from_string(cls, s):
        pass
"""
        tree = parser.parse(source, "cls.py")
        patterns = matcher.detect_decorators(tree.root)

        assert len(patterns) == 1
        assert patterns[0].kind == PatternKind.CLASSMETHOD_DECORATOR

    def test_detect_staticmethod_decorator(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting @staticmethod decorator."""
        source = """
class MyClass:
    @staticmethod
    def utility():
        pass
"""
        tree = parser.parse(source, "static.py")
        patterns = matcher.detect_decorators(tree.root)

        assert len(patterns) == 1
        assert patterns[0].kind == PatternKind.STATICMETHOD_DECORATOR

    def test_detect_dataclass_decorator(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting @dataclass decorator."""
        source = """
@dataclass
class Point:
    x: float
    y: float
"""
        tree = parser.parse(source, "dc.py")
        patterns = matcher.detect_decorators(tree.root)

        assert len(patterns) == 1
        assert patterns[0].kind == PatternKind.DATACLASS


class TestContextManagerPatterns:
    """Test context manager pattern detection."""

    def test_detect_with_statement(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting with statements."""
        source = """
with open("file.txt") as f:
    content = f.read()
"""
        tree = parser.parse(source, "ctx.py")
        patterns = matcher.detect_context_managers(tree.root)

        assert len(patterns) == 1
        assert patterns[0].kind == PatternKind.CONTEXT_MANAGER

    def test_detect_async_with(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting async with statements."""
        source = """
async with aiofiles.open("file.txt") as f:
    content = await f.read()
"""
        tree = parser.parse(source, "ctx.py")
        patterns = matcher.detect_context_managers(tree.root)

        assert len(patterns) == 1
        assert patterns[0].kind == PatternKind.ASYNC_WITH

    def test_detect_context_manager_protocol(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting classes implementing context manager protocol."""
        source = """
class MyContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
"""
        tree = parser.parse(source, "ctx.py")
        patterns = matcher.detect_context_managers(tree.root)

        # Should detect the protocol implementation
        protocol_patterns = [
            p for p in patterns
            if p.kind == PatternKind.CONTEXT_MANAGER_PROTOCOL
        ]
        assert len(protocol_patterns) == 1


class TestAsyncPatterns:
    """Test async pattern detection."""

    def test_detect_async_function(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting async functions."""
        source = """
async def fetch(url):
    pass
"""
        tree = parser.parse(source, "async.py")
        patterns = matcher.detect_async_patterns(tree.root)

        async_funcs = [p for p in patterns if p.kind == PatternKind.ASYNC_FUNCTION]
        assert len(async_funcs) == 1

    def test_detect_async_generator(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting async generators."""
        source = """
async def stream():
    for i in range(10):
        yield i
"""
        tree = parser.parse(source, "async.py")
        patterns = matcher.detect_async_patterns(tree.root)

        async_gens = [p for p in patterns if p.kind == PatternKind.ASYNC_GENERATOR]
        assert len(async_gens) == 1

    def test_detect_await_expression(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting await expressions."""
        source = """
async def fetch():
    result = await some_call()
    return result
"""
        tree = parser.parse(source, "async.py")
        patterns = matcher.detect_async_patterns(tree.root)

        awaits = [p for p in patterns if p.kind == PatternKind.AWAIT_EXPRESSION]
        assert len(awaits) == 1

    def test_detect_async_for(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting async for loops."""
        source = """
async def process():
    async for item in async_iter:
        print(item)
"""
        tree = parser.parse(source, "async.py")
        patterns = matcher.detect_async_patterns(tree.root)

        async_fors = [p for p in patterns if p.kind == PatternKind.ASYNC_FOR]
        assert len(async_fors) == 1


class TestPatternMatchingPatterns:
    """Test structural pattern matching detection (Python 3.10+)."""

    def test_detect_match_statement(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting match statements."""
        source = """
match command:
    case "quit":
        return False
    case "help":
        show_help()
    case _:
        unknown()
"""
        tree = parser.parse(source, "match.py")
        patterns = matcher.detect_pattern_matching(tree.root)

        match_patterns = [p for p in patterns if p.kind == PatternKind.PATTERN_MATCH]
        assert len(match_patterns) == 1
        assert match_patterns[0].details.get("case_count") == "3"


class TestExceptionPatterns:
    """Test exception handling pattern detection."""

    def test_detect_try_except(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting try/except."""
        source = """
try:
    risky()
except ValueError:
    handle()
"""
        tree = parser.parse(source, "exc.py")
        patterns = matcher.detect_exception_patterns(tree.root)

        handlers = [p for p in patterns if p.kind == PatternKind.EXCEPTION_HANDLER]
        assert len(handlers) == 1

    def test_detect_exception_chain(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting exception chaining."""
        source = """
try:
    something()
except ValueError as e:
    raise RuntimeError("Failed") from e
"""
        tree = parser.parse(source, "exc.py")
        patterns = matcher.detect_exception_patterns(tree.root)

        chains = [p for p in patterns if p.kind == PatternKind.EXCEPTION_CHAIN]
        assert len(chains) == 1


class TestTypePatterns:
    """Test typing-related pattern detection."""

    def test_detect_protocol(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting Protocol classes."""
        source = """
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None:
        ...
"""
        tree = parser.parse(source, "proto.py")
        patterns = matcher.detect_type_patterns(tree.root)

        protocols = [p for p in patterns if p.kind == PatternKind.PROTOCOL]
        assert len(protocols) == 1

    def test_detect_generic_class(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting Generic classes."""
        source = """
from typing import Generic, TypeVar

T = TypeVar('T')

class Stack(Generic[T]):
    pass
"""
        tree = parser.parse(source, "gen.py")
        patterns = matcher.detect_type_patterns(tree.root)

        generics = [p for p in patterns if p.kind == PatternKind.GENERIC_CLASS]
        assert len(generics) == 1

    def test_detect_typevar(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting TypeVar definitions."""
        source = """
from typing import TypeVar

T = TypeVar('T')
K = TypeVar('K', bound=str)
"""
        tree = parser.parse(source, "tv.py")
        patterns = matcher.detect_type_patterns(tree.root)

        typevars = [p for p in patterns if p.kind == PatternKind.TYPEVAR]
        assert len(typevars) == 2


class TestPythonSpecificPatterns:
    """Test Python-specific syntax patterns."""

    def test_detect_walrus_operator(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting walrus operator."""
        source = """
if (n := len(items)) > 10:
    print(n)
"""
        tree = parser.parse(source, "walrus.py")
        patterns = matcher.detect_python_specific(tree.root)

        walrus = [p for p in patterns if p.kind == PatternKind.WALRUS_OPERATOR]
        assert len(walrus) == 1

    def test_detect_fstring(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting f-strings."""
        source = '''
name = "World"
greeting = f"Hello, {name}!"
'''
        tree = parser.parse(source, "fstr.py")
        patterns = matcher.detect_python_specific(tree.root)

        fstrings = [p for p in patterns if p.kind == PatternKind.FSTRING]
        assert len(fstrings) == 1


class TestClassPatterns:
    """Test class-related pattern detection."""

    def test_detect_slots(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting __slots__."""
        source = """
class MyClass:
    __slots__ = ['x', 'y']
"""
        tree = parser.parse(source, "slots.py")
        patterns = matcher.detect_class_patterns(tree.root)

        slots = [p for p in patterns if p.kind == PatternKind.SLOTS]
        assert len(slots) == 1

    def test_detect_dunder_method(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting dunder methods."""
        source = """
class MyClass:
    def __init__(self):
        pass

    def __repr__(self):
        return "MyClass()"

    def __eq__(self, other):
        return True
"""
        tree = parser.parse(source, "dunder.py")
        patterns = matcher.detect_class_patterns(tree.root)

        dunders = [p for p in patterns if p.kind == PatternKind.DUNDER_METHOD]
        # __init__ is excluded, so should find __repr__ and __eq__
        assert len(dunders) == 2

    def test_detect_metaclass(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting metaclass usage."""
        source = """
class MyMeta(type):
    pass

class MyClass(metaclass=MyMeta):
    pass
"""
        tree = parser.parse(source, "meta.py")
        patterns = matcher.detect_class_patterns(tree.root)

        metaclasses = [p for p in patterns if p.kind == PatternKind.METACLASS]
        assert len(metaclasses) == 1


class TestUnsupportedPatterns:
    """Test detection of unsupported/problematic patterns."""

    def test_detect_exec(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting exec() calls."""
        source = """
exec("print('hello')")
"""
        tree = parser.parse(source, "exec.py")
        patterns = matcher.detect_unsupported(tree.root)

        execs = [p for p in patterns if p.kind == PatternKind.EXEC_STATEMENT]
        assert len(execs) == 1
        assert execs[0].automation_level == AutomationLevel.NONE

    def test_detect_eval(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting eval() calls."""
        source = """
result = eval("1 + 2")
"""
        tree = parser.parse(source, "eval.py")
        patterns = matcher.detect_unsupported(tree.root)

        evals = [p for p in patterns if p.kind == PatternKind.EVAL_CALL]
        assert len(evals) == 1
        assert evals[0].automation_level == AutomationLevel.NONE

    def test_detect_globals_locals(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting globals()/locals() calls."""
        source = """
g = globals()
l = locals()
"""
        tree = parser.parse(source, "gl.py")
        patterns = matcher.detect_unsupported(tree.root)

        gl = [p for p in patterns if p.kind == PatternKind.GLOBALS_LOCALS]
        assert len(gl) == 2


class TestDetectAll:
    """Test the detect_all method."""

    def test_detect_all_patterns(
        self, parser: PythonParser, matcher: PythonPatternMatcher
    ) -> None:
        """Test detecting all patterns at once."""
        source = """
from typing import Protocol

@dataclass
class Point:
    x: float
    y: float

class Drawable(Protocol):
    def draw(self) -> None:
        ...

async def process(items):
    squares = [x**2 for x in items]
    async for item in async_iter:
        yield item

with open("file.txt") as f:
    content = f.read()
"""
        tree = parser.parse(source, "all.py")
        patterns = list(matcher.detect_all(tree.root))

        # Should find multiple different pattern types
        kinds = {p.kind for p in patterns}
        assert PatternKind.DATACLASS in kinds
        assert PatternKind.PROTOCOL in kinds
        assert PatternKind.LIST_COMPREHENSION in kinds
        assert PatternKind.CONTEXT_MANAGER in kinds
