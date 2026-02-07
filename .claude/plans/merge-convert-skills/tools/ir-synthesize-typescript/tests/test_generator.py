"""Tests for the TypeScript code generator."""

import pytest
from ir_core.models import FunctionDef, Parameter, TypeDef, TypeKind
from ir_synthesize_typescript.generator import GeneratorConfig, TypeScriptCodeGenerator


class TestTypeScriptCodeGenerator:
    """Tests for TypeScriptCodeGenerator."""

    @pytest.fixture
    def generator(self):
        return TypeScriptCodeGenerator()

    def test_generate_interface(self, generator):
        """Test generating an interface."""
        type_def = TypeDef(
            name="User",
            kind=TypeKind.INTERFACE,
            visibility="public",
        )
        type_def.properties = [
            {"name": "id", "type": "number", "readonly": True},
            {"name": "name", "type": "string"},
            {"name": "email", "type": "string", "optional": True},
        ]

        code = generator.generate(types=[type_def], functions=[])

        assert "export interface User" in code
        assert "readonly id: number" in code
        assert "name: string" in code
        assert "email?: string" in code

    def test_generate_interface_with_generics(self, generator):
        """Test generating an interface with type parameters."""
        type_def = TypeDef(
            name="Container",
            kind=TypeKind.INTERFACE,
            visibility="public",
        )
        type_def.type_params = [
            {"name": "T", "constraint": "object", "default": "{}"}
        ]
        type_def.properties = [
            {"name": "value", "type": "T"},
        ]

        code = generator.generate(types=[type_def], functions=[])

        assert "interface Container<T extends object = {}>" in code
        assert "value: T" in code

    def test_generate_type_alias(self, generator):
        """Test generating a type alias."""
        type_def = TypeDef(
            name="StringOrNumber",
            kind=TypeKind.TYPE_ALIAS,
            visibility="public",
        )
        type_def.aliased_type = "string | number"

        code = generator.generate(types=[type_def], functions=[])

        assert "export type StringOrNumber = string | number" in code

    def test_generate_enum(self, generator):
        """Test generating an enum."""
        type_def = TypeDef(
            name="Status",
            kind=TypeKind.ENUM,
            visibility="public",
        )
        type_def.enum_members = [
            {"name": "Active", "value": "1"},
            {"name": "Inactive", "value": "2"},
        ]

        code = generator.generate(types=[type_def], functions=[])

        assert "export enum Status" in code
        assert "Active = 1" in code
        assert "Inactive = 2" in code

    def test_generate_const_enum(self, generator):
        """Test generating a const enum."""
        type_def = TypeDef(
            name="Direction",
            kind=TypeKind.ENUM,
            visibility="public",
        )
        type_def.const_enum = True
        type_def.enum_members = [
            {"name": "North"},
            {"name": "South"},
        ]

        code = generator.generate(types=[type_def], functions=[])

        assert "export const enum Direction" in code

    def test_generate_class(self, generator):
        """Test generating a class."""
        type_def = TypeDef(
            name="UserService",
            kind=TypeKind.CLASS,
            visibility="public",
        )
        type_def.properties = [
            {"name": "api", "type": "ApiClient", "visibility": "private"},
        ]
        type_def.methods = [
            {
                "name": "getUser",
                "parameters": [{"name": "id", "type": "number"}],
                "return_type": "User",
                "async": True,
            }
        ]

        code = generator.generate(types=[type_def], functions=[])

        assert "export class UserService" in code
        assert "private api: ApiClient" in code
        assert "async getUser(id: number): User" in code

    def test_generate_abstract_class(self, generator):
        """Test generating an abstract class."""
        type_def = TypeDef(
            name="Shape",
            kind=TypeKind.CLASS,
            visibility="public",
        )
        type_def.abstract = True
        type_def.methods = [
            {"name": "area", "parameters": [], "return_type": "number", "abstract": True}
        ]

        code = generator.generate(types=[type_def], functions=[])

        assert "export abstract class Shape" in code
        assert "abstract area(): number" in code

    def test_generate_function(self, generator):
        """Test generating a function."""
        func = FunctionDef(
            name="greet",
            visibility="public",
        )
        func.parameters = [
            Parameter(name="name", type_annotation="string"),
        ]
        func.return_type = "string"

        code = generator.generate(types=[], functions=[func])

        assert "export function greet(name: string): string" in code

    def test_generate_async_function(self, generator):
        """Test generating an async function."""
        func = FunctionDef(
            name="fetchData",
            visibility="public",
        )
        func.parameters = [
            Parameter(name="url", type_annotation="string"),
        ]
        func.return_type = "Data"
        func.async_ = True

        code = generator.generate(types=[], functions=[func])

        assert "export async function fetchData(url: string): Promise<Data>" in code

    def test_generate_generic_function(self, generator):
        """Test generating a generic function."""
        func = FunctionDef(
            name="identity",
            visibility="public",
        )
        func.type_params = [{"name": "T"}]
        func.parameters = [
            Parameter(name="value", type_annotation="T"),
        ]
        func.return_type = "T"

        code = generator.generate(types=[], functions=[func])

        assert "function identity<T>(value: T): T" in code

    def test_generate_imports(self, generator):
        """Test generating import statements."""
        imports = [
            {"module": "react", "default": "React"},
            {"module": "react", "named": [{"name": "useState"}, {"name": "useEffect"}]},
            {"module": "react", "named": [{"name": "FC"}], "type_only": True},
            {"module": "lodash", "namespace": "lodash"},
        ]

        code = generator.generate(types=[], functions=[], imports=imports)

        assert 'import React from "react"' in code
        assert 'import { useState, useEffect } from "react"' in code
        assert 'import type { FC } from "react"' in code
        assert 'import * as lodash from "lodash"' in code


class TestTypeMapping:
    """Tests for type mapping."""

    @pytest.fixture
    def generator(self):
        return TypeScriptCodeGenerator()

    def test_map_python_types(self, generator):
        """Test mapping Python types to TypeScript."""
        assert generator._map_type("int") == "number"
        assert generator._map_type("float") == "number"
        assert generator._map_type("str") == "string"
        assert generator._map_type("bool") == "boolean"
        assert generator._map_type("None") == "void"

    def test_map_rust_types(self, generator):
        """Test mapping Rust types to TypeScript."""
        assert generator._map_type("i32") == "number"
        assert generator._map_type("f64") == "number"
        assert generator._map_type("String") == "string"
        assert generator._map_type("&str") == "string"
        assert generator._map_type("i128") == "bigint"

    def test_map_generic_types(self, generator):
        """Test mapping generic types."""
        assert generator._map_type("List[int]") == "Array<number>"
        assert generator._map_type("Dict[str, int]") == "Record<string, number>"
        assert generator._map_type("Vec[String]") == "Array<string>"

    def test_map_optional_types(self, generator):
        """Test mapping optional types."""
        assert generator._map_type("Optional[str]") == "string | null"

    def test_map_union_types(self, generator):
        """Test mapping union types."""
        assert generator._map_type("int | str") == "number | string"


class TestGeneratorConfig:
    """Tests for generator configuration."""

    def test_custom_indent(self):
        """Test custom indentation."""
        config = GeneratorConfig(indent_size=4, use_tabs=False)
        generator = TypeScriptCodeGenerator(config)

        type_def = TypeDef(name="Test", kind=TypeKind.INTERFACE, visibility="public")
        type_def.properties = [{"name": "value", "type": "number"}]

        code = generator.generate(types=[type_def], functions=[])

        # Check for 4-space indentation
        lines = code.split("\n")
        property_line = [l for l in lines if "value" in l][0]
        assert property_line.startswith("    ")  # 4 spaces

    def test_tabs_indent(self):
        """Test tab indentation."""
        config = GeneratorConfig(use_tabs=True)
        generator = TypeScriptCodeGenerator(config)

        type_def = TypeDef(name="Test", kind=TypeKind.INTERFACE, visibility="public")
        type_def.properties = [{"name": "value", "type": "number"}]

        code = generator.generate(types=[type_def], functions=[])

        lines = code.split("\n")
        property_line = [l for l in lines if "value" in l][0]
        assert property_line.startswith("\t")

    def test_no_type_annotations(self):
        """Test generating without type annotations."""
        config = GeneratorConfig(emit_type_annotations=False)
        generator = TypeScriptCodeGenerator(config)

        func = FunctionDef(name="test", visibility="public")
        func.parameters = [Parameter(name="x", type_annotation="number")]
        func.return_type = "number"

        code = generator.generate(types=[], functions=[func])

        assert "function test(x)" in code
        assert ": number" not in code
