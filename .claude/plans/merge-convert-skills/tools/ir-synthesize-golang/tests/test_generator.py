"""Tests for Go code generator."""

from __future__ import annotations

import pytest

from ir_synthesize_golang.generator import GolangCodeGenerator, TYPE_MAP


@pytest.fixture
def generator() -> GolangCodeGenerator:
    """Create a generator instance."""
    return GolangCodeGenerator()


class TestTypeConversion:
    """Tests for type conversion."""

    def test_primitive_types(self, generator: GolangCodeGenerator) -> None:
        """Test primitive type conversion."""
        assert generator._convert_type("int") == "int"
        assert generator._convert_type("float") == "float64"
        assert generator._convert_type("str") == "string"
        assert generator._convert_type("bool") == "bool"

    def test_python_types(self, generator: GolangCodeGenerator) -> None:
        """Test Python type conversion."""
        assert generator._convert_type("bytes") == "[]byte"
        assert generator._convert_type("Any") == "any"
        assert generator._convert_type("None") == "any"

    def test_typescript_types(self, generator: GolangCodeGenerator) -> None:
        """Test TypeScript type conversion."""
        assert generator._convert_type("number") == "float64"
        assert generator._convert_type("string") == "string"
        assert generator._convert_type("boolean") == "bool"
        assert generator._convert_type("unknown") == "any"

    def test_rust_types(self, generator: GolangCodeGenerator) -> None:
        """Test Rust type conversion."""
        assert generator._convert_type("i32") == "int32"
        assert generator._convert_type("u64") == "uint64"
        assert generator._convert_type("f64") == "float64"
        assert generator._convert_type("char") == "rune"
        assert generator._convert_type("String") == "string"

    def test_generic_list_types(self, generator: GolangCodeGenerator) -> None:
        """Test generic list type conversion."""
        assert generator._convert_type("List[int]") == "[]int"
        assert generator._convert_type("Vec<i32>") == "[]int32"
        assert generator._convert_type("Array<string>") == "[]string"

    def test_generic_map_types(self, generator: GolangCodeGenerator) -> None:
        """Test generic map type conversion."""
        assert generator._convert_type("Dict[str, int]") == "map[string]int"
        assert generator._convert_type("HashMap<String, i32>") == "map[string]int32"
        assert generator._convert_type("Record<string, number>") == "map[string]float64"

    def test_optional_types(self, generator: GolangCodeGenerator) -> None:
        """Test optional type conversion."""
        assert generator._convert_type("Optional[int]") == "*int"
        assert generator._convert_type("Option<i32>") == "*int32"

    def test_go_types_passthrough(self, generator: GolangCodeGenerator) -> None:
        """Test that Go types pass through unchanged."""
        assert generator._convert_type("[]byte") == "[]byte"
        assert generator._convert_type("map[string]int") == "map[string]int"
        assert generator._convert_type("chan int") == "chan int"


class TestPackageGeneration:
    """Tests for package declaration generation."""

    def test_simple_package(self, generator: GolangCodeGenerator) -> None:
        """Test simple package declaration."""
        result = generator.generate_package("main")
        assert result == "package main\n"

    def test_lib_package(self, generator: GolangCodeGenerator) -> None:
        """Test library package declaration."""
        result = generator.generate_package("utils")
        assert result == "package utils\n"


class TestImportGeneration:
    """Tests for import generation."""

    def test_no_imports(self, generator: GolangCodeGenerator) -> None:
        """Test empty imports."""
        result = generator.generate_imports([])
        assert result == ""

    def test_single_import(self, generator: GolangCodeGenerator) -> None:
        """Test single import."""
        imports = [{"module": "fmt"}]
        result = generator.generate_imports(imports)
        assert '"fmt"' in result

    def test_multiple_imports(self, generator: GolangCodeGenerator) -> None:
        """Test multiple imports."""
        imports = [
            {"module": "fmt"},
            {"module": "os"},
            {"module": "strings"},
        ]
        result = generator.generate_imports(imports)
        assert '"fmt"' in result
        assert '"os"' in result
        assert '"strings"' in result

    def test_aliased_import(self, generator: GolangCodeGenerator) -> None:
        """Test import with alias."""
        imports = [{"module": "encoding/json", "alias": "js"}]
        result = generator.generate_imports(imports)
        assert 'js "encoding/json"' in result

    def test_blank_import(self, generator: GolangCodeGenerator) -> None:
        """Test blank import."""
        imports = [{"module": "database/sql", "blank_import": True}]
        result = generator.generate_imports(imports)
        assert '_ "database/sql"' in result

    def test_dot_import(self, generator: GolangCodeGenerator) -> None:
        """Test dot import."""
        imports = [{"module": "fmt", "dot_import": True}]
        result = generator.generate_imports(imports)
        assert '. "fmt"' in result


class TestStructGeneration:
    """Tests for struct generation."""

    def test_simple_struct(self, generator: GolangCodeGenerator) -> None:
        """Test simple struct generation."""
        from ir_core.models import TypeDef, TypeKind

        type_def = TypeDef(
            name="User",
            kind=TypeKind.STRUCT,
            properties=[
                {"name": "Name", "type": "string"},
                {"name": "Age", "type": "int"},
            ],
        )
        result = generator.generate_struct(type_def)
        assert "type User struct" in result
        assert "Name string" in result
        assert "Age int" in result

    def test_struct_with_tags(self, generator: GolangCodeGenerator) -> None:
        """Test struct with field tags."""
        from ir_core.models import TypeDef, TypeKind

        type_def = TypeDef(
            name="User",
            kind=TypeKind.STRUCT,
            properties=[
                {"name": "Name", "type": "string", "tag": '`json:"name"`'},
            ],
        )
        result = generator.generate_struct(type_def)
        assert 'Name string `json:"name"`' in result

    def test_generic_struct(self, generator: GolangCodeGenerator) -> None:
        """Test generic struct generation."""
        from ir_core.models import TypeDef, TypeKind

        type_def = TypeDef(
            name="Box",
            kind=TypeKind.STRUCT,
            type_params=[{"name": "T", "constraint": "any"}],
            properties=[{"name": "Value", "type": "T"}],
        )
        result = generator.generate_struct(type_def)
        assert "type Box[T any] struct" in result


class TestInterfaceGeneration:
    """Tests for interface generation."""

    def test_simple_interface(self, generator: GolangCodeGenerator) -> None:
        """Test simple interface generation."""
        from ir_core.models import TypeDef, TypeKind

        type_def = TypeDef(
            name="Reader",
            kind=TypeKind.INTERFACE,
            methods=[
                {
                    "name": "Read",
                    "parameters": [{"name": "p", "type": "[]byte"}],
                    "returns": [{"type": "int"}, {"type": "error"}],
                }
            ],
        )
        result = generator.generate_interface(type_def)
        assert "type Reader interface" in result
        assert "Read(p []byte)" in result

    def test_embedded_interface(self, generator: GolangCodeGenerator) -> None:
        """Test interface with embedding."""
        from ir_core.models import TypeDef, TypeKind

        type_def = TypeDef(
            name="ReadWriter",
            kind=TypeKind.INTERFACE,
            extends=["Reader", "Writer"],
        )
        result = generator.generate_interface(type_def)
        assert "Reader" in result
        assert "Writer" in result


class TestFunctionGeneration:
    """Tests for function generation."""

    def test_simple_function(self, generator: GolangCodeGenerator) -> None:
        """Test simple function generation."""
        from ir_core.models import FunctionDef, Parameter

        func_def = FunctionDef(
            name="Add",
            parameters=[
                Parameter(name="a", type_annotation="int"),
                Parameter(name="b", type_annotation="int"),
            ],
            return_type="int",
        )
        result = generator.generate_function(func_def)
        assert "func Add(a int, b int) int" in result

    def test_multiple_returns(self, generator: GolangCodeGenerator) -> None:
        """Test function with multiple returns."""
        from ir_core.models import FunctionDef, Parameter

        func_def = FunctionDef(
            name="Divide",
            parameters=[
                Parameter(name="a", type_annotation="int"),
                Parameter(name="b", type_annotation="int"),
            ],
            return_type="int",
        )
        func_def.additional_returns = [{"type": "error"}]
        result = generator.generate_function(func_def)
        assert "(int, error)" in result

    def test_method_with_receiver(self, generator: GolangCodeGenerator) -> None:
        """Test method with receiver."""
        from ir_core.models import FunctionDef

        func_def = FunctionDef(
            name="Increment",
            return_type="",
        )
        func_def.receiver = {"name": "c", "type": "*Counter"}
        result = generator.generate_function(func_def)
        assert "(c *Counter)" in result

    def test_variadic_function(self, generator: GolangCodeGenerator) -> None:
        """Test variadic function."""
        from ir_core.models import FunctionDef, Parameter

        func_def = FunctionDef(
            name="Sum",
            parameters=[
                Parameter(name="numbers", type_annotation="int", rest=True),
            ],
            return_type="int",
        )
        result = generator.generate_function(func_def)
        assert "...int" in result

    def test_generic_function(self, generator: GolangCodeGenerator) -> None:
        """Test generic function."""
        from ir_core.models import FunctionDef, Parameter

        func_def = FunctionDef(
            name="Map",
            parameters=[
                Parameter(name="items", type_annotation="[]T"),
                Parameter(name="fn", type_annotation="func(T) U"),
            ],
            return_type="[]U",
            type_params=[
                {"name": "T", "constraint": "any"},
                {"name": "U", "constraint": "any"},
            ],
        )
        result = generator.generate_function(func_def)
        assert "Map[T any, U any]" in result
