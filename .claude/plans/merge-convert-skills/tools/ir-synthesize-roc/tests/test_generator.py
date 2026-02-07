"""Tests for Roc code generator."""

from __future__ import annotations

import pytest

from ir_synthesize_roc.generator import RocCodeGenerator, TYPE_MAP


@pytest.fixture
def generator() -> RocCodeGenerator:
    """Create a generator instance."""
    return RocCodeGenerator()


class TestTypeConversion:
    """Tests for type conversion."""

    def test_python_types(self, generator: RocCodeGenerator) -> None:
        """Test Python type conversion."""
        assert generator._convert_type("int") == "I64"
        assert generator._convert_type("float") == "F64"
        assert generator._convert_type("str") == "Str"
        assert generator._convert_type("bool") == "Bool"
        assert generator._convert_type("bytes") == "List U8"

    def test_rust_types(self, generator: RocCodeGenerator) -> None:
        """Test Rust type conversion."""
        assert generator._convert_type("i32") == "I32"
        assert generator._convert_type("u64") == "U64"
        assert generator._convert_type("f64") == "F64"
        assert generator._convert_type("String") == "Str"

    def test_typescript_types(self, generator: RocCodeGenerator) -> None:
        """Test TypeScript type conversion."""
        assert generator._convert_type("number") == "F64"
        assert generator._convert_type("string") == "Str"
        assert generator._convert_type("boolean") == "Bool"

    def test_generic_list(self, generator: RocCodeGenerator) -> None:
        """Test generic list conversion."""
        assert generator._convert_type("List[int]") == "List I64"
        assert generator._convert_type("Vec<i32>") == "List I32"

    def test_generic_dict(self, generator: RocCodeGenerator) -> None:
        """Test generic dict conversion."""
        assert generator._convert_type("Dict[str, int]") == "Dict Str I64"
        assert generator._convert_type("HashMap<String, i32>") == "Dict Str I32"

    def test_optional(self, generator: RocCodeGenerator) -> None:
        """Test optional type conversion."""
        assert generator._convert_type("Optional[int]") == "[Just I64, Nothing]"
        assert generator._convert_type("Option<i32>") == "[Just I32, Nothing]"


class TestAppHeader:
    """Tests for app header generation."""

    def test_simple_app(self, generator: RocCodeGenerator) -> None:
        """Test simple app header."""
        result = generator.generate_app_header(
            ["main"],
            "https://example.com/platform.tar.br",
        )
        assert "app [main]" in result
        assert "platform" in result

    def test_multiple_provides(self, generator: RocCodeGenerator) -> None:
        """Test app with multiple provides."""
        result = generator.generate_app_header(
            ["main", "helper", "Model"],
            "platform.tar.br",
        )
        assert "main, helper, Model" in result


class TestModuleHeader:
    """Tests for module header generation."""

    def test_simple_module(self, generator: RocCodeGenerator) -> None:
        """Test simple module header."""
        result = generator.generate_module_header(["func1", "func2"])
        assert "module [func1, func2]" in result


class TestImport:
    """Tests for import generation."""

    def test_simple_import(self, generator: RocCodeGenerator) -> None:
        """Test simple import."""
        result = generator.generate_import("pf.Stdout")
        assert result == "import pf.Stdout\n"

    def test_import_with_exposing(self, generator: RocCodeGenerator) -> None:
        """Test import with exposing."""
        result = generator.generate_import("pf.Task", ["Task", "await"])
        assert "exposing [Task, await]" in result


class TestRecordType:
    """Tests for record type generation."""

    def test_simple_record(self, generator: RocCodeGenerator) -> None:
        """Test simple record generation."""
        from ir_core.models import TypeDef, TypeKind

        type_def = TypeDef(
            name="User",
            kind=TypeKind.STRUCT,
            properties=[
                {"name": "name", "type": "Str"},
                {"name": "age", "type": "I64"},
            ],
        )
        result = generator.generate_record_type(type_def)
        assert "User" in result
        assert "name : Str" in result
        assert "age : I64" in result

    def test_record_with_optional(self, generator: RocCodeGenerator) -> None:
        """Test record with optional field."""
        from ir_core.models import TypeDef, TypeKind

        type_def = TypeDef(
            name="Config",
            kind=TypeKind.STRUCT,
            properties=[
                {"name": "host", "type": "Str"},
                {"name": "port", "type": "I64", "optional": True},
            ],
        )
        result = generator.generate_record_type(type_def)
        assert "port?" in result


class TestTagUnion:
    """Tests for tag union generation."""

    def test_simple_tag_union(self, generator: RocCodeGenerator) -> None:
        """Test simple tag union."""
        from ir_core.models import TypeDef, TypeKind

        type_def = TypeDef(
            name="Status",
            kind=TypeKind.ENUM,
            enum_members=[
                {"name": "Pending"},
                {"name": "Active"},
                {"name": "Complete"},
            ],
        )
        result = generator.generate_tag_union(type_def)
        assert "[Pending, Active, Complete]" in result

    def test_tag_union_with_payload(self, generator: RocCodeGenerator) -> None:
        """Test tag union with payload."""
        from ir_core.models import TypeDef, TypeKind

        type_def = TypeDef(
            name="Result a e",
            kind=TypeKind.ENUM,
            enum_members=[
                {"name": "Ok", "payload_types": ["a"]},
                {"name": "Err", "payload_types": ["e"]},
            ],
        )
        result = generator.generate_tag_union(type_def)
        assert "Ok a" in result
        assert "Err e" in result


class TestFunction:
    """Tests for function generation."""

    def test_simple_function(self, generator: RocCodeGenerator) -> None:
        """Test simple function."""
        from ir_core.models import FunctionDef, Parameter

        func_def = FunctionDef(
            name="double",
            parameters=[Parameter(name="n", type_annotation="I64")],
            return_type="I64",
        )
        result = generator.generate_function(func_def)
        assert "double :" in result
        assert "I64 -> I64" in result
        assert "\\n ->" in result

    def test_function_with_type_annotation(self, generator: RocCodeGenerator) -> None:
        """Test function with explicit type annotation."""
        from ir_core.models import FunctionDef

        func_def = FunctionDef(
            name="greet",
            return_type="Task {} *",
        )
        func_def.type_annotation = "Str -> Task {} *"
        result = generator.generate_function(func_def)
        assert "greet : Str -> Task {} *" in result


class TestPatternMatch:
    """Tests for pattern matching generation."""

    def test_simple_pattern_match(self, generator: RocCodeGenerator) -> None:
        """Test simple when...is."""
        result = generator.generate_pattern_match(
            "result",
            [
                ("Ok n", "n * 2"),
                ("Err _", "0"),
            ],
        )
        assert "when result is" in result
        assert "Ok n -> n * 2" in result
        assert "Err _ -> 0" in result

    def test_result_handling(self, generator: RocCodeGenerator) -> None:
        """Test Result handling pattern."""
        result = generator.generate_result_handling(
            "parseNumber input",
            "n",
            "n * 2",
            "_",
            "0",
        )
        assert "when parseNumber input is" in result
        assert "Ok n -> n * 2" in result
        assert "Err _ -> 0" in result
