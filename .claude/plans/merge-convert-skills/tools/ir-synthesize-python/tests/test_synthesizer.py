"""Tests for the Python synthesizer."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from ir_core.base import OutputFormat, SynthConfig
from ir_core.models import (
    Block,
    ControlFlowGraph,
    Effect,
    EffectKind,
    ExtractionMode,
    Field_,
    Function,
    Import,
    ImportedItem,
    IRVersion,
    Module,
    ModuleMetadata,
    Param,
    Terminator,
    TerminatorKind,
    TypeBody,
    TypeDef,
    TypeKind,
    TypeRef,
    TypeRefKind,
    Visibility,
)
from ir_synthesize_python import PythonSynthesizer


@pytest.fixture
def synthesizer() -> PythonSynthesizer:
    """Create a synthesizer instance."""
    return PythonSynthesizer()


@pytest.fixture
def basic_config() -> SynthConfig:
    """Create a basic synthesis config."""
    return SynthConfig(
        output_format=OutputFormat.SOURCE,
        emit_type_hints=True,
        emit_docstrings=True,
    )


@pytest.fixture
def minimal_ir() -> IRVersion:
    """Create a minimal valid IR."""
    return IRVersion(
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


class TestPythonSynthesizer:
    """Tests for PythonSynthesizer class."""

    def test_target_language(self, synthesizer: PythonSynthesizer) -> None:
        """Test that target language is Python."""
        assert synthesizer.target_language() == "python"

    def test_synthesize_empty_module(
        self,
        synthesizer: PythonSynthesizer,
        basic_config: SynthConfig,
        minimal_ir: IRVersion,
    ) -> None:
        """Test synthesizing an empty module."""
        code = synthesizer.synthesize(minimal_ir, basic_config)
        # Empty module should produce minimal output
        assert code is not None
        assert isinstance(code, str)

    def test_synthesize_with_module_docstring(
        self,
        synthesizer: PythonSynthesizer,
        basic_config: SynthConfig,
        minimal_ir: IRVersion,
    ) -> None:
        """Test synthesizing a module with a docstring."""
        minimal_ir.module.metadata.documentation = "This is a test module."
        code = synthesizer.synthesize(minimal_ir, basic_config)
        assert '"""This is a test module."""' in code

    def test_synthesize_simple_function(
        self,
        synthesizer: PythonSynthesizer,
        basic_config: SynthConfig,
        minimal_ir: IRVersion,
    ) -> None:
        """Test synthesizing a simple function."""
        minimal_ir.functions = [
            Function(
                id="func:test:0",
                name="hello",
                params=[
                    Param(
                        name="name",
                        type=TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
                    ),
                ],
                return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
                effects=[],
                body=ControlFlowGraph(
                    entry="block:0",
                    blocks=[
                        Block(
                            id="block:0",
                            statements=[],
                            terminator=Terminator(kind=TerminatorKind.RETURN),
                        ),
                    ],
                    exit="block:0",
                ),
                visibility=Visibility.PUBLIC,
            ),
        ]

        code = synthesizer.synthesize(minimal_ir, basic_config)

        assert "def hello(" in code
        assert "name: str" in code
        assert "-> str" in code

    def test_synthesize_async_function(
        self,
        synthesizer: PythonSynthesizer,
        basic_config: SynthConfig,
        minimal_ir: IRVersion,
    ) -> None:
        """Test synthesizing an async function."""
        minimal_ir.functions = [
            Function(
                id="func:test:0",
                name="fetch_data",
                params=[],
                return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
                effects=[
                    Effect(kind=EffectKind.ASYNC),
                ],
                visibility=Visibility.PUBLIC,
            ),
        ]

        code = synthesizer.synthesize(minimal_ir, basic_config)
        assert "async def fetch_data" in code

    def test_synthesize_function_with_docstring(
        self,
        synthesizer: PythonSynthesizer,
        basic_config: SynthConfig,
        minimal_ir: IRVersion,
    ) -> None:
        """Test synthesizing a function with a docstring."""
        minimal_ir.functions = [
            Function(
                id="func:test:0",
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
                doc_comment="Add two numbers together.",
            ),
        ]

        code = synthesizer.synthesize(minimal_ir, basic_config)
        assert '"""Add two numbers together."""' in code

    def test_synthesize_class(
        self,
        synthesizer: PythonSynthesizer,
        basic_config: SynthConfig,
        minimal_ir: IRVersion,
    ) -> None:
        """Test synthesizing a class."""
        minimal_ir.types = [
            TypeDef(
                id="type:test:0",
                name="Person",
                kind=TypeKind.CLASS,
                body=TypeBody(
                    fields=[
                        Field_(
                            name="name",
                            type=TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
                            visibility=Visibility.PUBLIC,
                        ),
                        Field_(
                            name="age",
                            type=TypeRef(kind=TypeRefKind.NAMED, type_id="int"),
                            visibility=Visibility.PUBLIC,
                        ),
                    ],
                ),
                visibility=Visibility.PUBLIC,
            ),
        ]

        code = synthesizer.synthesize(minimal_ir, basic_config)
        assert "class Person:" in code
        assert "name: str" in code
        assert "age: int" in code

    def test_synthesize_dataclass(
        self,
        synthesizer: PythonSynthesizer,
        basic_config: SynthConfig,
        minimal_ir: IRVersion,
    ) -> None:
        """Test synthesizing a dataclass."""
        minimal_ir.types = [
            TypeDef(
                id="type:test:0",
                name="Point",
                kind=TypeKind.STRUCT,  # Struct maps to dataclass
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
            ),
        ]

        code = synthesizer.synthesize(minimal_ir, basic_config)
        assert "@dataclass" in code
        assert "class Point:" in code
        assert "x: float" in code
        assert "y: float" in code

    def test_synthesize_imports(
        self,
        synthesizer: PythonSynthesizer,
        basic_config: SynthConfig,
        minimal_ir: IRVersion,
    ) -> None:
        """Test synthesizing import statements."""
        minimal_ir.module.imports = [
            Import(
                id="import:0",
                module_path=["os"],
                imported_items=[],
            ),
            Import(
                id="import:1",
                module_path=["typing"],
                imported_items=[
                    ImportedItem(name="List", alias=None, kind="type"),
                    ImportedItem(name="Dict", alias=None, kind="type"),
                ],
            ),
        ]

        code = synthesizer.synthesize(minimal_ir, basic_config)
        assert "import os" in code
        assert "from typing import" in code

    def test_synthesize_generic_types(
        self,
        synthesizer: PythonSynthesizer,
        basic_config: SynthConfig,
        minimal_ir: IRVersion,
    ) -> None:
        """Test synthesizing generic type annotations."""
        minimal_ir.functions = [
            Function(
                id="func:test:0",
                name="process_items",
                params=[
                    Param(
                        name="items",
                        type=TypeRef(
                            kind=TypeRefKind.NAMED,
                            type_id="list",
                            args=[TypeRef(kind=TypeRefKind.NAMED, type_id="str")],
                        ),
                    ),
                ],
                return_type=TypeRef(
                    kind=TypeRefKind.NAMED,
                    type_id="dict",
                    args=[
                        TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
                        TypeRef(kind=TypeRefKind.NAMED, type_id="int"),
                    ],
                ),
                effects=[],
                visibility=Visibility.PUBLIC,
            ),
        ]

        code = synthesizer.synthesize(minimal_ir, basic_config)
        assert "items: list[str]" in code
        assert "-> dict[str, int]" in code

    def test_synthesize_union_types(
        self,
        synthesizer: PythonSynthesizer,
        basic_config: SynthConfig,
        minimal_ir: IRVersion,
    ) -> None:
        """Test synthesizing union type annotations."""
        minimal_ir.functions = [
            Function(
                id="func:test:0",
                name="process",
                params=[
                    Param(
                        name="value",
                        type=TypeRef(
                            kind=TypeRefKind.UNION,
                            members=[
                                TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
                                TypeRef(kind=TypeRefKind.NAMED, type_id="int"),
                            ],
                        ),
                    ),
                ],
                return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="None"),
                effects=[],
                visibility=Visibility.PUBLIC,
            ),
        ]

        code = synthesizer.synthesize(minimal_ir, basic_config)
        assert "value: str | int" in code

    def test_synthesize_callable_types(
        self,
        synthesizer: PythonSynthesizer,
        basic_config: SynthConfig,
        minimal_ir: IRVersion,
    ) -> None:
        """Test synthesizing callable type annotations."""
        minimal_ir.functions = [
            Function(
                id="func:test:0",
                name="apply",
                params=[
                    Param(
                        name="func",
                        type=TypeRef(
                            kind=TypeRefKind.FUNCTION,
                            params=[TypeRef(kind=TypeRefKind.NAMED, type_id="int")],
                            return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
                        ),
                    ),
                ],
                return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
                effects=[],
                visibility=Visibility.PUBLIC,
            ),
        ]

        code = synthesizer.synthesize(minimal_ir, basic_config)
        assert "Callable[[int], str]" in code

    def test_synthesize_without_type_hints(
        self,
        synthesizer: PythonSynthesizer,
        minimal_ir: IRVersion,
    ) -> None:
        """Test synthesizing without type hints."""
        config = SynthConfig(
            output_format=OutputFormat.SOURCE,
            emit_type_hints=False,
        )

        minimal_ir.functions = [
            Function(
                id="func:test:0",
                name="hello",
                params=[
                    Param(
                        name="name",
                        type=TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
                    ),
                ],
                return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
                effects=[],
                visibility=Visibility.PUBLIC,
            ),
        ]

        code = synthesizer.synthesize(minimal_ir, config)
        assert "def hello(name):" in code
        assert ": str" not in code
        assert "-> str" not in code

    def test_estimate_output(
        self,
        synthesizer: PythonSynthesizer,
        minimal_ir: IRVersion,
    ) -> None:
        """Test output estimation."""
        minimal_ir.types = [
            TypeDef(
                id="type:test:0",
                name="Test",
                kind=TypeKind.CLASS,
                body=TypeBody(),
                visibility=Visibility.PUBLIC,
            ),
        ]
        minimal_ir.functions = [
            Function(
                id="func:test:0",
                name="test",
                params=[],
                return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="None"),
                effects=[],
                visibility=Visibility.PUBLIC,
            ),
        ]

        estimate = synthesizer.estimate_output(minimal_ir)

        assert "estimated_lines" in estimate
        assert "estimated_complexity" in estimate
        assert "type_count" in estimate
        assert estimate["type_count"] == 1
        assert estimate["function_count"] == 1


class TestPreservationLevels:
    """Tests for different preservation levels."""

    def test_correct_level(
        self,
        synthesizer: PythonSynthesizer,
        minimal_ir: IRVersion,
    ) -> None:
        """Test L1 (correct) preservation level."""
        config = SynthConfig(
            custom_options={"preservation_mode": "correct"},
        )

        minimal_ir.functions = [
            Function(
                id="func:test:0",
                name="example",
                params=[],
                return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="None"),
                effects=[],
                visibility=Visibility.PUBLIC,
            ),
        ]

        code = synthesizer.synthesize(minimal_ir, config)
        assert "def example" in code

    def test_idiomatic_level(
        self,
        synthesizer: PythonSynthesizer,
        minimal_ir: IRVersion,
    ) -> None:
        """Test L2 (idiomatic) preservation level."""
        config = SynthConfig(
            custom_options={"preservation_mode": "idiomatic"},
        )

        minimal_ir.types = [
            TypeDef(
                id="type:test:0",
                name="Data",
                kind=TypeKind.STRUCT,
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
            ),
        ]

        code = synthesizer.synthesize(minimal_ir, config)
        # Idiomatic level should use dataclass for structs
        assert "@dataclass" in code

    def test_optimized_level(
        self,
        synthesizer: PythonSynthesizer,
        minimal_ir: IRVersion,
    ) -> None:
        """Test L3 (optimized) preservation level."""
        config = SynthConfig(
            custom_options={"preservation_mode": "optimized"},
        )

        minimal_ir.functions = [
            Function(
                id="func:test:0",
                name="compute",
                params=[],
                return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="int"),
                effects=[],
                visibility=Visibility.PUBLIC,
            ),
        ]

        code = synthesizer.synthesize(minimal_ir, config)
        assert "def compute" in code


class TestGapTracking:
    """Tests for gap tracking during synthesis."""

    def test_gaps_collected(
        self,
        synthesizer: PythonSynthesizer,
        basic_config: SynthConfig,
        minimal_ir: IRVersion,
    ) -> None:
        """Test that synthesis gaps are collected."""
        # Add a wildcard import which should trigger a gap
        minimal_ir.module.imports = [
            Import(
                id="import:0",
                module_path=["os"],
                imported_items=[
                    ImportedItem(name="*", alias=None, kind="wildcard"),
                ],
            ),
        ]

        synthesizer.synthesize(minimal_ir, basic_config)

        # Check that gaps were recorded
        assert len(synthesizer.last_gaps) > 0
        assert any("wildcard" in g.description.lower() for g in synthesizer.last_gaps)
