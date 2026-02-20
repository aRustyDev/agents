"""TypeScript compilation verification tests.

These tests verify that generated TypeScript code compiles successfully
with tsc --strict. This ensures the synthesizer produces valid TypeScript.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import pytest

# Check if tsc is available
try:
    result = subprocess.run(
        ["tsc", "--version"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    TSC_AVAILABLE = result.returncode == 0
    TSC_VERSION = result.stdout.strip() if TSC_AVAILABLE else None
except (subprocess.TimeoutExpired, FileNotFoundError):
    TSC_AVAILABLE = False
    TSC_VERSION = None

pytestmark = pytest.mark.skipif(
    not TSC_AVAILABLE,
    reason="tsc not available",
)


def compile_typescript_code(code: str, strict: bool = True) -> tuple[bool, str]:
    """Compile TypeScript code and return success status and output.

    Args:
        code: TypeScript source code to compile
        strict: Whether to use --strict mode (default True)

    Returns:
        Tuple of (success, output) where output is error message if failed
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "test.ts"
        temp_path.write_text(code)

        args = [
            "tsc",
            "--noEmit",  # Don't output JS files
            "--skipLibCheck",  # Skip lib.d.ts checking for speed
            "--target",
            "ES2022",
            "--module",
            "ESNext",
            "--moduleResolution",
            "node",
        ]

        if strict:
            args.append("--strict")

        args.append(str(temp_path))

        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            success = result.returncode == 0
            output = result.stderr if not success else result.stdout
            return success, output
        except subprocess.TimeoutExpired:
            return False, "Compilation timed out"


class TestSimpleTypeCompilation:
    """Test compilation of simple type definitions."""

    def test_interface_compiles(self):
        """Test simple interface compiles."""
        code = """
interface User {
  id: number;
  name: string;
  email?: string;
}

const user: User = { id: 1, name: "Alice" };
"""
        success, output = compile_typescript_code(code)
        assert success, f"Interface compilation failed: {output}"

    def test_type_alias_compiles(self):
        """Test type alias compiles."""
        code = """
type StringOrNumber = string | number;
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

const value: StringOrNumber = 42;
const result: Result<string, Error> = { ok: true, value: "success" };
"""
        success, output = compile_typescript_code(code)
        assert success, f"Type alias compilation failed: {output}"

    def test_generic_interface_compiles(self):
        """Test generic interface compiles."""
        code = """
interface Container<T> {
  value: T;
  map<U>(fn: (value: T) => U): Container<U>;
}

class Box<T> implements Container<T> {
  constructor(public value: T) {}

  map<U>(fn: (value: T) => U): Container<U> {
    return new Box(fn(this.value));
  }
}
"""
        success, output = compile_typescript_code(code)
        assert success, f"Generic interface compilation failed: {output}"


class TestFunctionCompilation:
    """Test compilation of function definitions."""

    def test_simple_function_compiles(self):
        """Test simple function compiles."""
        code = """
function add(a: number, b: number): number {
  return a + b;
}

const result = add(1, 2);
"""
        success, output = compile_typescript_code(code)
        assert success, f"Simple function compilation failed: {output}"

    def test_generic_function_compiles(self):
        """Test generic function compiles."""
        code = """
function identity<T>(value: T): T {
  return value;
}

function map<T, U>(arr: T[], fn: (item: T) => U): U[] {
  return arr.map(fn);
}

const nums = map([1, 2, 3], (n) => n * 2);
"""
        success, output = compile_typescript_code(code)
        assert success, f"Generic function compilation failed: {output}"

    def test_async_function_compiles(self):
        """Test async function compiles."""
        code = """
async function fetchData(url: string): Promise<string> {
  const response = await fetch(url);
  return response.text();
}

async function processData(): Promise<void> {
  const data = await fetchData("https://example.com");
  console.log(data);
}
"""
        success, output = compile_typescript_code(code)
        assert success, f"Async function compilation failed: {output}"

    def test_overloaded_function_compiles(self):
        """Test function overloads compile."""
        code = """
function format(value: string): string;
function format(value: number): string;
function format(value: string | number): string {
  return String(value);
}

const s = format("hello");
const n = format(42);
"""
        success, output = compile_typescript_code(code)
        assert success, f"Overloaded function compilation failed: {output}"


class TestClassCompilation:
    """Test compilation of class definitions."""

    def test_simple_class_compiles(self):
        """Test simple class compiles."""
        code = """
class Point {
  constructor(public x: number, public y: number) {}

  distanceFromOrigin(): number {
    return Math.sqrt(this.x ** 2 + this.y ** 2);
  }
}

const p = new Point(3, 4);
console.log(p.distanceFromOrigin());
"""
        success, output = compile_typescript_code(code)
        assert success, f"Simple class compilation failed: {output}"

    def test_class_with_inheritance_compiles(self):
        """Test class inheritance compiles."""
        code = """
abstract class Shape {
  abstract area(): number;
}

class Rectangle extends Shape {
  constructor(private width: number, private height: number) {
    super();
  }

  area(): number {
    return this.width * this.height;
  }
}

const rect = new Rectangle(5, 3);
console.log(rect.area());
"""
        success, output = compile_typescript_code(code)
        assert success, f"Class inheritance compilation failed: {output}"

    def test_class_with_private_fields_compiles(self):
        """Test class with private fields compiles."""
        code = """
class Counter {
  #count = 0;

  increment(): void {
    this.#count++;
  }

  get value(): number {
    return this.#count;
  }
}

const counter = new Counter();
counter.increment();
console.log(counter.value);
"""
        success, output = compile_typescript_code(code)
        assert success, f"Private fields compilation failed: {output}"


class TestAdvancedTypesCompilation:
    """Test compilation of advanced type constructs."""

    def test_conditional_type_compiles(self):
        """Test conditional type compiles."""
        code = """
type IsString<T> = T extends string ? true : false;

type A = IsString<string>;  // true
type B = IsString<number>;  // false

const a: A = true;
const b: B = false;
"""
        success, output = compile_typescript_code(code)
        assert success, f"Conditional type compilation failed: {output}"

    def test_mapped_type_compiles(self):
        """Test mapped type compiles."""
        code = """
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

interface User {
  name: string;
  age: number;
}

type ReadonlyUser = Readonly<User>;

const user: ReadonlyUser = { name: "Alice", age: 30 };
"""
        success, output = compile_typescript_code(code)
        assert success, f"Mapped type compilation failed: {output}"

    def test_template_literal_type_compiles(self):
        """Test template literal type compiles."""
        code = """
type EventName = "click" | "focus" | "blur";
type Handler = `on${Capitalize<EventName>}`;

const handler: Handler = "onClick";
"""
        success, output = compile_typescript_code(code)
        assert success, f"Template literal type compilation failed: {output}"

    def test_discriminated_union_compiles(self):
        """Test discriminated union compiles."""
        code = """
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "rectangle"; width: number; height: number };

function getArea(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.radius ** 2;
    case "rectangle":
      return shape.width * shape.height;
  }
}

const area = getArea({ kind: "circle", radius: 5 });
"""
        success, output = compile_typescript_code(code)
        assert success, f"Discriminated union compilation failed: {output}"


class TestModuleCompilation:
    """Test compilation of module patterns."""

    def test_export_import_compiles(self):
        """Test export/import patterns compile."""
        code = """
export interface Config {
  apiUrl: string;
  timeout: number;
}

export function createConfig(url: string): Config {
  return { apiUrl: url, timeout: 5000 };
}

export default class Client {
  constructor(private config: Config) {}

  getUrl(): string {
    return this.config.apiUrl;
  }
}
"""
        success, output = compile_typescript_code(code)
        assert success, f"Export/import compilation failed: {output}"

    def test_namespace_compiles(self):
        """Test namespace compiles."""
        code = """
namespace Validation {
  export interface Result {
    isValid: boolean;
    errors: string[];
  }

  export function validate(value: string): Result {
    const errors: string[] = [];
    if (value.length === 0) {
      errors.push("Value cannot be empty");
    }
    return { isValid: errors.length === 0, errors };
  }
}

const result = Validation.validate("test");
"""
        success, output = compile_typescript_code(code)
        assert success, f"Namespace compilation failed: {output}"


class TestStrictModeCompilation:
    """Test that strict mode catches issues."""

    def test_strict_null_checks(self):
        """Test strictNullChecks catches null issues."""
        code = """
function process(value: string | null): number {
  return value.length;  // Error: value might be null
}
"""
        success, output = compile_typescript_code(code, strict=True)
        assert not success, "Should fail with strictNullChecks"

    def test_strict_null_checks_fixed(self):
        """Test proper null handling compiles."""
        code = """
function process(value: string | null): number {
  if (value === null) {
    return 0;
  }
  return value.length;
}
"""
        success, output = compile_typescript_code(code, strict=True)
        assert success, f"Proper null handling should compile: {output}"

    def test_no_implicit_any(self):
        """Test noImplicitAny catches untyped params."""
        code = """
function process(value) {  // Error: implicit any
  return value;
}
"""
        success, output = compile_typescript_code(code, strict=True)
        assert not success, "Should fail with noImplicitAny"

    def test_explicit_any_compiles(self):
        """Test explicit any compiles."""
        code = """
function process(value: unknown): string {
  return String(value);
}
"""
        success, output = compile_typescript_code(code, strict=True)
        assert success, f"Explicit unknown should compile: {output}"
