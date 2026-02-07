"""Tests for Go parser."""

from __future__ import annotations

import pytest

from ir_extract_golang.parser import GolangParser


@pytest.fixture
def parser() -> GolangParser:
    """Create a parser instance."""
    return GolangParser()


class TestPackageExtraction:
    """Tests for package declaration extraction."""

    def test_simple_package(self, parser: GolangParser) -> None:
        """Test extracting simple package declaration."""
        source = "package main"
        result = parser.parse(source)
        assert result["package"] == "main"

    def test_package_with_comments(self, parser: GolangParser) -> None:
        """Test package with doc comments."""
        source = '''// Package utils provides utility functions.
package utils
'''
        result = parser.parse(source)
        assert result["package"] == "utils"


class TestImportExtraction:
    """Tests for import declaration extraction."""

    def test_single_import(self, parser: GolangParser) -> None:
        """Test single import."""
        source = '''package main

import "fmt"
'''
        result = parser.parse(source)
        assert len(result["imports"]) == 1
        assert result["imports"][0].path == "fmt"

    def test_multiple_imports(self, parser: GolangParser) -> None:
        """Test import block."""
        source = '''package main

import (
    "fmt"
    "os"
    "strings"
)
'''
        result = parser.parse(source)
        assert len(result["imports"]) == 3
        paths = [imp.path for imp in result["imports"]]
        assert "fmt" in paths
        assert "os" in paths
        assert "strings" in paths

    def test_aliased_import(self, parser: GolangParser) -> None:
        """Test import with alias."""
        source = '''package main

import (
    f "fmt"
    str "strings"
)
'''
        result = parser.parse(source)
        assert len(result["imports"]) == 2
        fmt_import = next(i for i in result["imports"] if i.path == "fmt")
        assert fmt_import.alias == "f"

    def test_blank_import(self, parser: GolangParser) -> None:
        """Test blank import for side effects."""
        source = '''package main

import _ "database/sql"
'''
        result = parser.parse(source)
        assert len(result["imports"]) == 1
        assert result["imports"][0].blank_import is True


class TestStructExtraction:
    """Tests for struct type extraction."""

    def test_simple_struct(self, parser: GolangParser) -> None:
        """Test simple struct definition."""
        source = '''package main

type User struct {
    Name  string
    Email string
    Age   int
}
'''
        result = parser.parse(source)
        assert len(result["structs"]) == 1
        user = result["structs"][0]
        assert user.name == "User"
        assert len(user.fields) == 3

    def test_struct_with_tags(self, parser: GolangParser) -> None:
        """Test struct with field tags."""
        source = '''package main

type User struct {
    Name  string `json:"name"`
    Email string `json:"email" validate:"email"`
}
'''
        result = parser.parse(source)
        user = result["structs"][0]
        name_field = next(f for f in user.fields if f.name == "Name")
        assert name_field.tag is not None
        assert "json" in name_field.tag

    def test_embedded_struct(self, parser: GolangParser) -> None:
        """Test struct with embedded types."""
        source = '''package main

type Base struct {
    ID int
}

type User struct {
    Base
    Name string
}
'''
        result = parser.parse(source)
        assert len(result["structs"]) == 2
        user = next(s for s in result["structs"] if s.name == "User")
        embedded = [f for f in user.fields if f.embedded]
        assert len(embedded) == 1

    def test_generic_struct(self, parser: GolangParser) -> None:
        """Test generic struct (Go 1.18+)."""
        source = '''package main

type Box[T any] struct {
    Value T
}
'''
        result = parser.parse(source)
        box = result["structs"][0]
        assert box.name == "Box"
        assert len(box.type_params) == 1
        assert box.type_params[0].name == "T"
        assert box.type_params[0].constraint == "any"


class TestInterfaceExtraction:
    """Tests for interface type extraction."""

    def test_simple_interface(self, parser: GolangParser) -> None:
        """Test simple interface definition."""
        source = '''package main

type Reader interface {
    Read(p []byte) (n int, err error)
}
'''
        result = parser.parse(source)
        assert len(result["interfaces"]) == 1
        reader = result["interfaces"][0]
        assert reader.name == "Reader"
        assert len(reader.methods) == 1

    def test_embedded_interface(self, parser: GolangParser) -> None:
        """Test interface with embedded interfaces."""
        source = '''package main

type ReadWriter interface {
    Reader
    Writer
}
'''
        result = parser.parse(source)
        rw = result["interfaces"][0]
        assert "Reader" in rw.embedded
        assert "Writer" in rw.embedded

    def test_empty_interface(self, parser: GolangParser) -> None:
        """Test empty interface."""
        source = '''package main

type Any interface{}
'''
        result = parser.parse(source)
        any_iface = result["interfaces"][0]
        assert any_iface.name == "Any"
        assert len(any_iface.methods) == 0


class TestFunctionExtraction:
    """Tests for function and method extraction."""

    def test_simple_function(self, parser: GolangParser) -> None:
        """Test simple function."""
        source = '''package main

func Add(a, b int) int {
    return a + b
}
'''
        result = parser.parse(source)
        assert len(result["functions"]) == 1
        add = result["functions"][0]
        assert add.name == "Add"
        assert len(add.parameters) == 2
        assert len(add.results) == 1

    def test_multiple_returns(self, parser: GolangParser) -> None:
        """Test function with multiple returns."""
        source = '''package main

func Divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}
'''
        result = parser.parse(source)
        divide = result["functions"][0]
        assert len(divide.results) == 2
        assert divide.returns_error is True

    def test_method(self, parser: GolangParser) -> None:
        """Test method with receiver."""
        source = '''package main

type Counter struct {
    count int
}

func (c *Counter) Increment() {
    c.count++
}
'''
        result = parser.parse(source)
        # Method should be associated with struct
        counter = result["structs"][0]
        assert len(counter.methods) == 1
        assert counter.methods[0].name == "Increment"

    def test_generic_function(self, parser: GolangParser) -> None:
        """Test generic function."""
        source = '''package main

func Map[T, U any](items []T, fn func(T) U) []U {
    result := make([]U, len(items))
    for i, item := range items {
        result[i] = fn(item)
    }
    return result
}
'''
        result = parser.parse(source)
        map_func = result["functions"][0]
        assert map_func.name == "Map"
        assert len(map_func.type_params) == 2


class TestConcurrencyExtraction:
    """Tests for concurrency pattern extraction."""

    def test_goroutine_detection(self, parser: GolangParser) -> None:
        """Test goroutine detection."""
        source = '''package main

func Process() {
    go func() {
        doWork()
    }()
}
'''
        result = parser.parse(source)
        process = result["functions"][0]
        assert len(process.goroutines) == 1

    def test_channel_operations(self, parser: GolangParser) -> None:
        """Test channel operation detection."""
        source = '''package main

func Worker(ch chan int) {
    value := <-ch
    ch <- value * 2
}
'''
        result = parser.parse(source)
        worker = result["functions"][0]
        assert len(worker.channel_ops) >= 1

    def test_defer_detection(self, parser: GolangParser) -> None:
        """Test defer statement detection."""
        source = '''package main

func ReadFile(path string) ([]byte, error) {
    f, err := os.Open(path)
    if err != nil {
        return nil, err
    }
    defer f.Close()
    return io.ReadAll(f)
}
'''
        result = parser.parse(source)
        read_file = result["functions"][0]
        assert len(read_file.defers) == 1


class TestConstantExtraction:
    """Tests for constant extraction."""

    def test_simple_constants(self, parser: GolangParser) -> None:
        """Test simple constant declarations."""
        source = '''package main

const Pi = 3.14159
const MaxSize = 1024
'''
        result = parser.parse(source)
        assert len(result["constants"]) == 2

    def test_iota_constants(self, parser: GolangParser) -> None:
        """Test iota constants."""
        source = '''package main

const (
    Sunday = iota
    Monday
    Tuesday
)
'''
        result = parser.parse(source)
        assert len(result["constants"]) == 3
        sunday = result["constants"][0]
        assert sunday.iota is True


class TestVariableExtraction:
    """Tests for variable extraction."""

    def test_package_variables(self, parser: GolangParser) -> None:
        """Test package-level variables."""
        source = '''package main

var Debug bool
var Version = "1.0.0"
'''
        result = parser.parse(source)
        assert len(result["variables"]) == 2


class TestVisibility:
    """Tests for visibility detection."""

    def test_exported_unexported(self, parser: GolangParser) -> None:
        """Test visibility based on capitalization."""
        source = '''package main

type PublicStruct struct {
    PublicField  string
    privateField string
}

func PublicFunc() {}
func privateFunc() {}
'''
        result = parser.parse(source)

        # Struct visibility
        struct = result["structs"][0]
        assert struct.exported is True

        # Field visibility
        public_field = next(f for f in struct.fields if f.name == "PublicField")
        private_field = next(f for f in struct.fields if f.name == "privateField")
        assert public_field.visibility.value == "exported"
        assert private_field.visibility.value == "unexported"

        # Function visibility
        public_func = next(f for f in result["functions"] if f.name == "PublicFunc")
        private_func = next(f for f in result["functions"] if f.name == "privateFunc")
        assert public_func.exported is True
        assert private_func.exported is False
