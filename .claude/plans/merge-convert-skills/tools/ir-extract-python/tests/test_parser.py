"""Tests for the PythonParser class."""

from __future__ import annotations

import pytest

from ir_extract_python import PythonParser


@pytest.fixture
def parser() -> PythonParser:
    """Create a PythonParser instance."""
    return PythonParser()


class TestParsing:
    """Test basic parsing functionality."""

    def test_parse_empty_source(self, parser: PythonParser) -> None:
        """Test parsing empty source."""
        tree = parser.parse("", "empty.py")
        assert tree.root.type == "module"
        assert not tree.has_errors

    def test_parse_simple_function(self, parser: PythonParser) -> None:
        """Test parsing a simple function."""
        source = "def hello(): pass"
        tree = parser.parse(source, "hello.py")

        assert tree.root.type == "module"
        assert not tree.has_errors

        functions = parser.extract_functions(tree)
        assert len(functions) == 1
        assert functions[0].type == "function_definition"

    def test_parse_syntax_error(self, parser: PythonParser) -> None:
        """Test parsing source with syntax error."""
        source = "def hello(: pass"  # Invalid syntax
        tree = parser.parse(source, "invalid.py")

        assert tree.has_errors


class TestFunctionExtraction:
    """Test function extraction."""

    def test_extract_single_function(self, parser: PythonParser) -> None:
        """Test extracting a single function."""
        source = """
def greet(name: str) -> str:
    return f"Hello, {name}!"
"""
        tree = parser.parse(source, "greet.py")
        functions = parser.extract_functions(tree)

        assert len(functions) == 1

        func_info = parser.extract_function_info(functions[0])
        assert func_info.name == "greet"
        assert not func_info.is_async
        assert "name" in func_info.parameters

    def test_extract_async_function(self, parser: PythonParser) -> None:
        """Test extracting an async function."""
        source = """
async def fetch(url: str) -> bytes:
    pass
"""
        tree = parser.parse(source, "fetch.py")
        functions = parser.extract_functions(tree)

        assert len(functions) == 1

        func_info = parser.extract_function_info(functions[0])
        assert func_info.name == "fetch"
        assert func_info.is_async

    def test_extract_decorated_function(self, parser: PythonParser) -> None:
        """Test extracting a decorated function."""
        source = """
@decorator
@another(arg)
def decorated() -> None:
    pass
"""
        tree = parser.parse(source, "decorated.py")
        functions = parser.extract_functions(tree)

        assert len(functions) == 1

        func_info = parser.extract_function_info(functions[0])
        assert func_info.name == "decorated"
        assert len(func_info.decorators) == 2

    def test_extract_function_with_docstring(self, parser: PythonParser) -> None:
        """Test extracting function docstring."""
        source = '''
def documented():
    """This is the docstring."""
    pass
'''
        tree = parser.parse(source, "doc.py")
        functions = parser.extract_functions(tree)

        func_info = parser.extract_function_info(functions[0])
        assert func_info.docstring == "This is the docstring."


class TestClassExtraction:
    """Test class extraction."""

    def test_extract_single_class(self, parser: PythonParser) -> None:
        """Test extracting a single class."""
        source = """
class MyClass:
    pass
"""
        tree = parser.parse(source, "myclass.py")
        classes = parser.extract_classes(tree)

        assert len(classes) == 1

        class_info = parser.extract_class_info(classes[0])
        assert class_info.name == "MyClass"
        assert len(class_info.bases) == 0

    def test_extract_class_with_bases(self, parser: PythonParser) -> None:
        """Test extracting a class with base classes."""
        source = """
class Derived(Base, Mixin):
    pass
"""
        tree = parser.parse(source, "derived.py")
        classes = parser.extract_classes(tree)

        class_info = parser.extract_class_info(classes[0])
        assert class_info.name == "Derived"
        assert "Base" in class_info.bases
        assert "Mixin" in class_info.bases

    def test_extract_class_methods(self, parser: PythonParser) -> None:
        """Test extracting class methods."""
        source = """
class MyClass:
    def method_a(self):
        pass

    def method_b(self):
        pass
"""
        tree = parser.parse(source, "methods.py")
        classes = parser.extract_classes(tree)

        class_info = parser.extract_class_info(classes[0])
        assert "method_a" in class_info.methods
        assert "method_b" in class_info.methods

    def test_extract_class_attributes(self, parser: PythonParser) -> None:
        """Test extracting class-level attributes."""
        source = """
class MyClass:
    attr_a = 1
    attr_b = "hello"
"""
        tree = parser.parse(source, "attrs.py")
        classes = parser.extract_classes(tree)

        class_info = parser.extract_class_info(classes[0])
        assert "attr_a" in class_info.attributes
        assert "attr_b" in class_info.attributes


class TestImportExtraction:
    """Test import extraction."""

    def test_extract_simple_import(self, parser: PythonParser) -> None:
        """Test extracting a simple import."""
        source = "import os"
        tree = parser.parse(source, "imports.py")
        imports = parser.extract_imports(tree)

        assert len(imports) == 1

        import_info = parser.extract_import_info(imports[0])
        assert import_info.module == "os"
        assert not import_info.is_from

    def test_extract_from_import(self, parser: PythonParser) -> None:
        """Test extracting a from import."""
        source = "from os.path import join, dirname"
        tree = parser.parse(source, "imports.py")
        imports = parser.extract_imports(tree)

        assert len(imports) == 1

        import_info = parser.extract_import_info(imports[0])
        assert import_info.module == "os.path"
        assert import_info.is_from
        assert "join" in import_info.names
        assert "dirname" in import_info.names

    def test_extract_aliased_import(self, parser: PythonParser) -> None:
        """Test extracting an aliased import."""
        source = "import numpy as np"
        tree = parser.parse(source, "imports.py")
        imports = parser.extract_imports(tree)

        import_info = parser.extract_import_info(imports[0])
        assert "numpy" in import_info.aliases
        assert import_info.aliases["numpy"] == "np"

    def test_extract_relative_import(self, parser: PythonParser) -> None:
        """Test extracting a relative import."""
        source = "from ..utils import helper"
        tree = parser.parse(source, "imports.py")
        imports = parser.extract_imports(tree)

        import_info = parser.extract_import_info(imports[0])
        assert import_info.is_relative
        assert import_info.level == 2


class TestComprehensions:
    """Test comprehension detection."""

    def test_find_list_comprehension(self, parser: PythonParser) -> None:
        """Test finding list comprehensions."""
        source = "squares = [x**2 for x in range(10)]"
        tree = parser.parse(source, "comp.py")
        comps = parser.find_comprehensions(tree)

        assert len(comps) == 1
        assert comps[0].type == "list_comprehension"

    def test_find_dict_comprehension(self, parser: PythonParser) -> None:
        """Test finding dictionary comprehensions."""
        source = "mapping = {k: v for k, v in pairs}"
        tree = parser.parse(source, "comp.py")
        comps = parser.find_comprehensions(tree)

        assert len(comps) == 1
        assert comps[0].type == "dictionary_comprehension"

    def test_find_set_comprehension(self, parser: PythonParser) -> None:
        """Test finding set comprehensions."""
        source = "unique = {x for x in items}"
        tree = parser.parse(source, "comp.py")
        comps = parser.find_comprehensions(tree)

        assert len(comps) == 1
        assert comps[0].type == "set_comprehension"

    def test_find_generator_expression(self, parser: PythonParser) -> None:
        """Test finding generator expressions."""
        source = "total = sum(x**2 for x in range(10))"
        tree = parser.parse(source, "comp.py")
        comps = parser.find_comprehensions(tree)

        assert len(comps) == 1
        assert comps[0].type == "generator_expression"


class TestAsyncNodes:
    """Test async node detection."""

    def test_find_async_functions(self, parser: PythonParser) -> None:
        """Test finding async functions."""
        source = """
async def fetch():
    pass

def regular():
    pass
"""
        tree = parser.parse(source, "async.py")
        async_nodes = parser.find_async_nodes(tree)

        # Should find the async function
        async_funcs = [n for n in async_nodes if n.type == "async_function_definition"]
        assert len(async_funcs) == 1

    def test_find_await_expressions(self, parser: PythonParser) -> None:
        """Test finding await expressions."""
        source = """
async def fetch():
    result = await some_async_call()
    return result
"""
        tree = parser.parse(source, "async.py")
        async_nodes = parser.find_async_nodes(tree)

        awaits = [n for n in async_nodes if n.type == "await"]
        assert len(awaits) == 1

    def test_find_async_for(self, parser: PythonParser) -> None:
        """Test finding async for loops."""
        source = """
async def process():
    async for item in async_iterator:
        yield item
"""
        tree = parser.parse(source, "async.py")
        async_nodes = parser.find_async_nodes(tree)

        async_fors = [n for n in async_nodes if n.type == "async_for_statement"]
        assert len(async_fors) == 1


class TestPatternMatching:
    """Test pattern matching detection (Python 3.10+)."""

    def test_find_match_statement(self, parser: PythonParser) -> None:
        """Test finding match statements."""
        source = """
match command:
    case "quit":
        return False
    case "help":
        show_help()
    case _:
        unknown_command()
"""
        tree = parser.parse(source, "match.py")
        matches = parser.find_match_statements(tree)

        assert len(matches) == 1


class TestContextManagers:
    """Test context manager detection."""

    def test_find_with_statement(self, parser: PythonParser) -> None:
        """Test finding with statements."""
        source = """
with open("file.txt") as f:
    content = f.read()
"""
        tree = parser.parse(source, "with.py")
        withs = parser.find_with_statements(tree)

        assert len(withs) == 1

    def test_find_multiple_context_managers(self, parser: PythonParser) -> None:
        """Test finding with statements with multiple context managers."""
        source = """
with open("a.txt") as a, open("b.txt") as b:
    pass
"""
        tree = parser.parse(source, "with.py")
        withs = parser.find_with_statements(tree)

        assert len(withs) == 1


class TestExceptionHandling:
    """Test exception handling detection."""

    def test_find_try_statement(self, parser: PythonParser) -> None:
        """Test finding try statements."""
        source = """
try:
    risky()
except ValueError:
    handle_error()
finally:
    cleanup()
"""
        tree = parser.parse(source, "try.py")
        tries = parser.find_try_statements(tree)

        assert len(tries) == 1

    def test_find_nested_try(self, parser: PythonParser) -> None:
        """Test finding nested try statements."""
        source = """
try:
    try:
        inner_risky()
    except KeyError:
        pass
except ValueError:
    pass
"""
        tree = parser.parse(source, "try.py")
        tries = parser.find_try_statements(tree)

        assert len(tries) == 2


class TestNormalization:
    """Test GAST normalization."""

    def test_normalize_module(self, parser: PythonParser) -> None:
        """Test normalizing a module."""
        source = """
def hello():
    pass

class World:
    pass
"""
        tree = parser.parse(source, "module.py")
        gast = parser.normalize(tree)

        assert gast.kind == "module"

    def test_normalize_function(self, parser: PythonParser) -> None:
        """Test that functions are normalized."""
        source = "def hello(): pass"
        tree = parser.parse(source, "func.py")
        gast = parser.normalize(tree)

        # Find function in children
        func_nodes = [c for c in gast.children if c.kind == "function"]
        assert len(func_nodes) == 1
        assert func_nodes[0].attributes.get("name") == "hello"

    def test_normalize_async_function(self, parser: PythonParser) -> None:
        """Test that async functions are normalized with async flag."""
        source = "async def fetch(): pass"
        tree = parser.parse(source, "async.py")
        gast = parser.normalize(tree)

        func_nodes = [c for c in gast.children if c.kind == "function"]
        assert len(func_nodes) == 1
        assert func_nodes[0].attributes.get("async") is True
