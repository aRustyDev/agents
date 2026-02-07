"""Tests for the TypeScript parser."""

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_language_pack")

from ir_extract_typescript.parser import TypeScriptParser


class TestTypeScriptParser:
    """Tests for TypeScriptParser."""

    @pytest.fixture
    def parser(self):
        return TypeScriptParser()

    def test_parse_interface(self, parser):
        """Test parsing an interface."""
        source = '''
interface User {
    id: number;
    name: string;
    email?: string;
}
'''
        result = parser.parse(source)
        assert len(result["interfaces"]) == 1
        iface = result["interfaces"][0]
        assert iface.name == "User"
        assert len(iface.properties) == 3

    def test_parse_interface_with_generics(self, parser):
        """Test parsing an interface with generics."""
        source = '''
interface Container<T extends object = {}> {
    value: T;
    transform<U>(fn: (v: T) => U): Container<U>;
}
'''
        result = parser.parse(source)
        assert len(result["interfaces"]) == 1
        iface = result["interfaces"][0]
        assert iface.name == "Container"
        assert len(iface.type_params) == 1
        assert iface.type_params[0].name == "T"
        assert iface.type_params[0].constraint == "object"

    def test_parse_type_alias(self, parser):
        """Test parsing a type alias."""
        source = '''
type StringOrNumber = string | number;
type Handler<T> = (value: T) => void;
'''
        result = parser.parse(source)
        assert len(result["type_aliases"]) == 2
        assert result["type_aliases"][0].name == "StringOrNumber"
        assert result["type_aliases"][1].name == "Handler"

    def test_parse_enum(self, parser):
        """Test parsing an enum."""
        source = '''
enum Direction {
    North,
    South,
    East = "EAST",
    West = "WEST",
}
'''
        result = parser.parse(source)
        assert len(result["enums"]) == 1
        enum = result["enums"][0]
        assert enum.name == "Direction"
        assert len(enum.members) == 4

    def test_parse_const_enum(self, parser):
        """Test parsing a const enum."""
        source = '''
const enum Status {
    Active = 1,
    Inactive = 2,
}
'''
        result = parser.parse(source)
        assert len(result["enums"]) == 1
        enum = result["enums"][0]
        assert enum.const is True

    def test_parse_class(self, parser):
        """Test parsing a class."""
        source = '''
class Animal {
    private name: string;
    public age: number;

    constructor(name: string, age: number) {
        this.name = name;
        this.age = age;
    }

    speak(): void {}
}
'''
        result = parser.parse(source)
        assert len(result["classes"]) == 1
        cls = result["classes"][0]
        assert cls.name == "Animal"
        assert len(cls.properties) >= 2

    def test_parse_abstract_class(self, parser):
        """Test parsing an abstract class."""
        source = '''
abstract class Shape {
    abstract area(): number;
}
'''
        result = parser.parse(source)
        assert len(result["classes"]) == 1
        cls = result["classes"][0]
        assert cls.abstract is True

    def test_parse_function(self, parser):
        """Test parsing a function."""
        source = '''
function greet(name: string): string {
    return `Hello, ${name}!`;
}
'''
        result = parser.parse(source)
        assert len(result["functions"]) == 1
        func = result["functions"][0]
        assert func.name == "greet"
        assert len(func.parameters) == 1
        assert func.return_type == "string"

    def test_parse_async_function(self, parser):
        """Test parsing an async function."""
        source = '''
async function fetchData<T>(url: string): Promise<T> {
    const response = await fetch(url);
    return response.json();
}
'''
        result = parser.parse(source)
        assert len(result["functions"]) == 1
        func = result["functions"][0]
        assert func.async_ is True
        assert len(func.type_params) == 1

    def test_parse_generator_function(self, parser):
        """Test parsing a generator function."""
        source = '''
function* range(start: number, end: number): Generator<number> {
    for (let i = start; i < end; i++) {
        yield i;
    }
}
'''
        result = parser.parse(source)
        assert len(result["functions"]) == 1
        func = result["functions"][0]
        assert func.generator is True

    def test_parse_imports(self, parser):
        """Test parsing import statements."""
        source = '''
import React from "react";
import { useState, useEffect } from "react";
import type { FC, ReactNode } from "react";
import * as lodash from "lodash";
'''
        result = parser.parse(source)
        assert len(result["imports"]) == 4
        assert result["imports"][0].default_import == "React"
        assert len(result["imports"][1].named_imports) == 2
        assert result["imports"][2].type_only is True
        assert result["imports"][3].namespace_import == "lodash"

    def test_parse_exports(self, parser):
        """Test parsing export statements."""
        source = '''
export interface User {}
export type ID = string;
export function helper() {}
export const value = 42;
'''
        result = parser.parse(source)
        assert any(i.exported for i in result["interfaces"])
        assert any(a.exported for a in result["type_aliases"])
        assert any(f.exported for f in result["functions"])
        assert any(v.get("exported") for v in result["variables"])

    def test_parse_interface_extends(self, parser):
        """Test parsing interface inheritance."""
        source = '''
interface Named {
    name: string;
}

interface Aged {
    age: number;
}

interface Person extends Named, Aged {
    email: string;
}
'''
        result = parser.parse(source)
        person = [i for i in result["interfaces"] if i.name == "Person"][0]
        assert len(person.extends) == 2
        assert "Named" in person.extends
        assert "Aged" in person.extends

    def test_parse_class_implements(self, parser):
        """Test parsing class implementing interfaces."""
        source = '''
interface Printable {
    print(): void;
}

class Document implements Printable {
    print(): void {}
}
'''
        result = parser.parse(source)
        doc = result["classes"][0]
        assert "Printable" in doc.implements

    def test_parse_index_signature(self, parser):
        """Test parsing index signatures."""
        source = '''
interface StringMap {
    [key: string]: string;
}
'''
        result = parser.parse(source)
        iface = result["interfaces"][0]
        assert len(iface.index_signatures) == 1


class TestTypeScriptParserEdgeCases:
    """Edge case tests for TypeScriptParser."""

    @pytest.fixture
    def parser(self):
        return TypeScriptParser()

    def test_parse_empty_interface(self, parser):
        """Test parsing an empty interface."""
        source = "interface Empty {}"
        result = parser.parse(source)
        assert len(result["interfaces"]) == 1
        assert result["interfaces"][0].name == "Empty"

    def test_parse_readonly_properties(self, parser):
        """Test parsing readonly properties."""
        source = '''
interface Config {
    readonly id: string;
    readonly name: string;
}
'''
        result = parser.parse(source)
        iface = result["interfaces"][0]
        assert all(p.readonly for p in iface.properties)

    def test_parse_optional_parameters(self, parser):
        """Test parsing optional parameters."""
        source = '''
function greet(name: string, title?: string): string {
    return title ? `${title} ${name}` : name;
}
'''
        result = parser.parse(source)
        func = result["functions"][0]
        assert len(func.parameters) == 2
        assert func.parameters[1].optional is True

    def test_parse_rest_parameters(self, parser):
        """Test parsing rest parameters."""
        source = '''
function sum(...numbers: number[]): number {
    return numbers.reduce((a, b) => a + b, 0);
}
'''
        result = parser.parse(source)
        func = result["functions"][0]
        assert len(func.parameters) == 1
        assert func.parameters[0].rest is True
