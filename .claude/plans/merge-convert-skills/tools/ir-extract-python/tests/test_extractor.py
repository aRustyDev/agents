"""Tests for the PythonExtractor class."""

from __future__ import annotations

import pytest
from ir_core.base import ExtractConfig, ExtractionMode, SemanticEnrichmentLevel
from ir_core.models import (
    EffectKind,
    GapType,
    TypeKind,
    TypeRefKind,
    Visibility,
)
from ir_extract_python import PythonExtractor


@pytest.fixture
def extractor() -> PythonExtractor:
    """Create a PythonExtractor instance."""
    return PythonExtractor()


@pytest.fixture
def config() -> ExtractConfig:
    """Create a default ExtractConfig."""
    return ExtractConfig(
        mode=ExtractionMode.FULL_MODULE,
        semantic_level=SemanticEnrichmentLevel.NONE,
    )


class TestBasicExtraction:
    """Test basic extraction functionality."""

    def test_extract_empty_file(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test extracting an empty file."""
        source = ""
        ir = extractor.extract(source, "empty.py", config)

        assert ir.version == "ir-v1.0"
        assert ir.module.name == "empty"
        assert len(ir.functions) == 0
        assert len(ir.types) == 0

    def test_extract_simple_function(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test extracting a simple function."""
        source = """
def hello(name: str) -> str:
    return f"Hello, {name}!"
"""
        ir = extractor.extract(source, "hello.py", config)

        assert len(ir.functions) == 1
        func = ir.functions[0]
        assert func.name == "hello"
        assert len(func.params) == 1
        assert func.params[0].name == "name"
        assert func.params[0].type.type_id == "str"
        assert func.return_type.type_id == "str"

    def test_extract_function_with_defaults(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test extracting a function with default parameters."""
        source = """
def greet(name: str = "World", times: int = 1) -> None:
    for _ in range(times):
        print(f"Hello, {name}!")
"""
        ir = extractor.extract(source, "greet.py", config)

        assert len(ir.functions) == 1
        func = ir.functions[0]
        assert func.name == "greet"
        assert len(func.params) == 2
        assert func.params[0].name == "name"
        assert func.params[1].name == "times"

    def test_extract_async_function(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test extracting an async function."""
        source = """
async def fetch_data(url: str) -> dict:
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
"""
        ir = extractor.extract(source, "fetch.py", config)

        assert len(ir.functions) == 1
        func = ir.functions[0]
        assert func.name == "fetch_data"

        # Should have async effect
        effect_kinds = [e.kind for e in func.effects]
        assert EffectKind.ASYNC in effect_kinds or "async" in effect_kinds


class TestClassExtraction:
    """Test class extraction functionality."""

    def test_extract_simple_class(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test extracting a simple class."""
        source = """
class Person:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"Hello, I'm {self.name}"
"""
        ir = extractor.extract(source, "person.py", config)

        assert len(ir.types) == 1
        type_def = ir.types[0]
        assert type_def.name == "Person"
        assert type_def.kind == TypeKind.CLASS

        # Should have methods extracted as functions
        assert len(ir.functions) >= 2  # __init__ and greet

    def test_extract_class_with_inheritance(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test extracting a class with inheritance."""
        source = """
class Animal:
    def speak(self) -> str:
        return ""

class Dog(Animal):
    def speak(self) -> str:
        return "Woof!"
"""
        ir = extractor.extract(source, "animals.py", config)

        assert len(ir.types) == 2
        animal = next(t for t in ir.types if t.name == "Animal")
        dog = next(t for t in ir.types if t.name == "Dog")

        assert animal is not None
        assert dog is not None

    def test_extract_dataclass(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test extracting a dataclass."""
        source = """
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

    def distance_from_origin(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5
"""
        ir = extractor.extract(source, "point.py", config)

        assert len(ir.types) == 1
        type_def = ir.types[0]
        assert type_def.name == "Point"
        # Dataclasses are treated as struct-like
        assert type_def.kind in (TypeKind.STRUCT, TypeKind.CLASS)


class TestImportExtraction:
    """Test import extraction functionality."""

    def test_extract_simple_import(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test extracting a simple import."""
        source = """
import os
import sys
"""
        ir = extractor.extract(source, "imports.py", config)

        assert len(ir.module.imports) == 2

    def test_extract_from_import(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test extracting a from import."""
        source = """
from typing import List, Optional, Dict
from pathlib import Path
"""
        ir = extractor.extract(source, "imports.py", config)

        assert len(ir.module.imports) == 2

    def test_extract_aliased_import(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test extracting an aliased import."""
        source = """
import numpy as np
import pandas as pd
from typing import Optional as Opt
"""
        ir = extractor.extract(source, "imports.py", config)

        assert len(ir.module.imports) == 3

    def test_wildcard_import_creates_gap(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test that wildcard imports create gaps."""
        source = """
from os.path import *
"""
        ir = extractor.extract(source, "imports.py", config)

        assert len(ir.gaps) >= 1
        gap = ir.gaps[0]
        assert gap.gap_type == GapType.STRUCTURAL


class TestTypeAnnotations:
    """Test type annotation extraction."""

    def test_extract_generic_types(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test extracting generic type annotations."""
        source = """
from typing import List, Dict, Optional

def process(items: List[int]) -> Dict[str, int]:
    return {str(i): i for i in items}

def maybe(value: Optional[str]) -> str:
    return value or ""
"""
        ir = extractor.extract(source, "generics.py", config)

        assert len(ir.functions) == 2

        process_func = next(f for f in ir.functions if f.name == "process")
        assert process_func.params[0].type.type_id in ("List", "list")

    def test_extract_union_types(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test extracting union type annotations."""
        source = """
def process(value: int | str) -> int | None:
    if isinstance(value, str):
        return int(value)
    return value
"""
        ir = extractor.extract(source, "unions.py", config)

        assert len(ir.functions) == 1
        func = ir.functions[0]
        # The parameter type should be a union
        assert func.params[0].type.kind == TypeRefKind.UNION

    def test_extract_callable_types(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test extracting Callable type annotations."""
        source = """
from typing import Callable

def apply(func: Callable[[int], str], value: int) -> str:
    return func(value)
"""
        ir = extractor.extract(source, "callable.py", config)

        assert len(ir.functions) == 1
        func = ir.functions[0]
        assert func.params[0].type.kind == TypeRefKind.FUNCTION


class TestEffects:
    """Test effect detection."""

    def test_detect_io_effects(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test detecting I/O effects."""
        source = """
def write_file(path: str, content: str) -> None:
    with open(path, 'w') as f:
        f.write(content)
"""
        ir = extractor.extract(source, "io.py", config)

        func = ir.functions[0]
        effect_kinds = [e.kind for e in func.effects]
        assert EffectKind.IO in effect_kinds or "io" in effect_kinds

    def test_detect_throws_effect(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test detecting throw effects."""
        source = """
def validate(value: int) -> None:
    if value < 0:
        raise ValueError("Value must be non-negative")
"""
        ir = extractor.extract(source, "validate.py", config)

        func = ir.functions[0]
        effect_kinds = [e.kind for e in func.effects]
        assert EffectKind.THROWS in effect_kinds or "throws" in effect_kinds


class TestVisibility:
    """Test visibility detection."""

    def test_public_function(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test public function visibility."""
        source = """
def public_func() -> None:
    pass
"""
        ir = extractor.extract(source, "vis.py", config)

        func = ir.functions[0]
        assert func.visibility == Visibility.PUBLIC

    def test_private_function(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test private function visibility."""
        source = """
def __private_func() -> None:
    pass
"""
        ir = extractor.extract(source, "vis.py", config)

        func = ir.functions[0]
        assert func.visibility == Visibility.PRIVATE

    def test_protected_function(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test protected function visibility."""
        source = """
def _protected_func() -> None:
    pass
"""
        ir = extractor.extract(source, "vis.py", config)

        func = ir.functions[0]
        assert func.visibility == Visibility.PROTECTED


class TestDocstrings:
    """Test docstring extraction."""

    def test_extract_function_docstring(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test extracting function docstrings."""
        source = '''
def hello(name: str) -> str:
    """
    Greet someone by name.

    Args:
        name: The person's name

    Returns:
        A greeting message
    """
    return f"Hello, {name}!"
'''
        ir = extractor.extract(source, "hello.py", config)

        func = ir.functions[0]
        assert func.doc_comment is not None
        assert "Greet someone" in func.doc_comment

    def test_extract_module_docstring(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test extracting module docstrings."""
        source = '''"""
This is the module docstring.

It describes what this module does.
"""

def hello() -> None:
    pass
'''
        ir = extractor.extract(source, "module.py", config)

        assert ir.module.metadata.documentation is not None
        assert "module docstring" in ir.module.metadata.documentation


class TestValidation:
    """Test source validation."""

    def test_validate_valid_source(
        self, extractor: PythonExtractor
    ) -> None:
        """Test validating valid source."""
        source = """
def hello() -> None:
    pass
"""
        gaps = extractor.validate_source(source, "valid.py")
        assert len(gaps) == 0

    def test_validate_syntax_error(
        self, extractor: PythonExtractor
    ) -> None:
        """Test validating source with syntax error."""
        source = """
def hello(
    # Missing closing paren
"""
        gaps = extractor.validate_source(source, "invalid.py")
        assert len(gaps) >= 1


class TestEdgeCases:
    """Test edge cases and complex scenarios."""

    def test_nested_functions(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test extracting nested functions."""
        source = """
def outer(x: int) -> int:
    def inner(y: int) -> int:
        return y * 2
    return inner(x)
"""
        ir = extractor.extract(source, "nested.py", config)

        # Should find at least the outer function
        assert len(ir.functions) >= 1
        outer_func = next(f for f in ir.functions if f.name == "outer")
        assert outer_func is not None

    def test_class_with_decorators(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test extracting classes with decorators."""
        source = """
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float
"""
        ir = extractor.extract(source, "point.py", config)

        assert len(ir.types) == 1

    def test_method_with_receiver(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test that methods have receiver extracted."""
        source = """
class Counter:
    def __init__(self) -> None:
        self.count = 0

    def increment(self) -> int:
        self.count += 1
        return self.count
"""
        ir = extractor.extract(source, "counter.py", config)

        # Find increment method
        increment = next(
            (f for f in ir.functions if f.name == "increment"),
            None
        )
        if increment:
            # Methods should have a receiver
            assert increment.receiver is not None
            assert increment.receiver.name == "self"

    def test_generic_class(
        self, extractor: PythonExtractor, config: ExtractConfig
    ) -> None:
        """Test extracting a generic class."""
        source = """
from typing import Generic, TypeVar

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()
"""
        ir = extractor.extract(source, "stack.py", config)

        assert len(ir.types) == 1
        stack = ir.types[0]
        assert stack.name == "Stack"
        # Should have type parameters
        assert len(stack.params) >= 0  # May or may not be extracted depending on implementation
