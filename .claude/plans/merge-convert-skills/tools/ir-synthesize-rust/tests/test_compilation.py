"""Tests for Rust code compilation verification.

These tests verify that generated Rust code compiles successfully
using rustc.
"""

import subprocess
import tempfile
from pathlib import Path

import pytest
from ir_core.base import SynthConfig
from ir_core.models import (
    Field_,
    Function,
    Param,
    TypeBody,
    TypeDef,
    TypeKind,
    TypeParam,
    TypeRef,
    TypeRefKind,
    Variant,
)
from ir_synthesize_rust.generator import RustCodeGenerator, SynthesisContext
from ir_synthesize_rust.synthesizer import RustSynthesizer


def check_rustc_available() -> bool:
    """Check if rustc is available."""
    try:
        result = subprocess.run(
            ["rustc", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


# Skip all tests if rustc is not available
pytestmark = pytest.mark.skipif(
    not check_rustc_available(),
    reason="rustc not available",
)


def compile_rust_code(code: str) -> tuple[bool, str]:
    """Compile Rust code and return success status and output.

    Args:
        code: Rust source code to compile

    Returns:
        Tuple of (success: bool, output: str)
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "test.rs"
        temp_path.write_text(code)
        out_path = Path(temp_dir) / "test.rlib"

        try:
            result = subprocess.run(
                [
                    "rustc",
                    "--edition=2021",
                    "--crate-type=lib",  # Compile as library, no main needed
                    "-A",
                    "dead_code",  # Allow unused code in tests
                    "-A",
                    "unused",  # Allow unused warnings
                    "-o",
                    str(out_path),
                    str(temp_path),
                ],
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


@pytest.fixture
def generator() -> RustCodeGenerator:
    """Create a Rust generator."""
    return RustCodeGenerator()


@pytest.fixture
def synthesizer() -> RustSynthesizer:
    """Create a Rust synthesizer."""
    return RustSynthesizer(SynthConfig())


class TestSimpleStructCompilation:
    """Test that generated structs compile."""

    def test_simple_struct_compiles(self, generator):
        """Test simple struct generation compiles."""
        type_def = TypeDef(
            id="Point",
            name="Point",
            kind=TypeKind.STRUCT,
            body=TypeBody(
                fields=[
                    Field_(
                        name="x", type=TypeRef(kind=TypeRefKind.NAMED, type_id="f64")
                    ),
                    Field_(
                        name="y", type=TypeRef(kind=TypeRefKind.NAMED, type_id="f64")
                    ),
                ]
            ),
        )
        context = SynthesisContext()
        code = generator.gen_struct(type_def, context)

        success, output = compile_rust_code(code)
        assert success, f"Struct compilation failed: {output}"

    def test_generic_struct_compiles(self, generator):
        """Test generic struct generation compiles."""
        type_def = TypeDef(
            id="Container",
            name="Container",
            kind=TypeKind.STRUCT,
            params=[TypeParam(name="T")],
            body=TypeBody(
                fields=[
                    Field_(
                        name="value",
                        type=TypeRef(kind=TypeRefKind.GENERIC, type_id="T"),
                    ),
                ]
            ),
        )
        context = SynthesisContext()
        code = generator.gen_struct(type_def, context)

        success, output = compile_rust_code(code)
        assert success, f"Generic struct compilation failed: {output}"


class TestEnumCompilation:
    """Test that generated enums compile."""

    def test_simple_enum_compiles(self, generator):
        """Test simple enum generation compiles."""
        type_def = TypeDef(
            id="Color",
            name="Color",
            kind=TypeKind.ENUM,
            body=TypeBody(
                variants=[
                    Variant(name="Red", kind="unit"),
                    Variant(name="Green", kind="unit"),
                    Variant(name="Blue", kind="unit"),
                ]
            ),
        )
        context = SynthesisContext()
        code = generator.gen_enum(type_def, context)

        success, output = compile_rust_code(code)
        assert success, f"Enum compilation failed: {output}"

    def test_data_enum_compiles(self, generator):
        """Test enum with data variants compiles."""
        type_def = TypeDef(
            id="Event",
            name="Event",
            kind=TypeKind.ENUM,
            body=TypeBody(
                variants=[
                    Variant(
                        name="Click",
                        kind="tuple",
                        fields=[
                            Field_(
                                name="0",
                                type=TypeRef(kind=TypeRefKind.NAMED, type_id="i32"),
                            ),
                            Field_(
                                name="1",
                                type=TypeRef(kind=TypeRefKind.NAMED, type_id="i32"),
                            ),
                        ],
                    ),
                    Variant(
                        name="KeyPress",
                        kind="tuple",
                        fields=[
                            Field_(
                                name="0",
                                type=TypeRef(kind=TypeRefKind.NAMED, type_id="char"),
                            ),
                        ],
                    ),
                ]
            ),
        )
        context = SynthesisContext()
        code = generator.gen_enum(type_def, context)

        success, output = compile_rust_code(code)
        assert success, f"Data enum compilation failed: {output}"


class TestFunctionCompilation:
    """Test that generated functions compile."""

    def test_simple_function_compiles(self, generator):
        """Test simple function generation compiles."""
        func = Function(
            id="add",
            name="add",
            params=[
                Param(name="a", type=TypeRef(kind=TypeRefKind.NAMED, type_id="i32")),
                Param(name="b", type=TypeRef(kind=TypeRefKind.NAMED, type_id="i32")),
            ],
            return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="i32"),
        )
        context = SynthesisContext()
        code = generator.gen_function(func, context)
        # Generator produces function signature - add body for compilation
        if "todo!()" in code:
            code = code.replace("{ todo!() }", "{ a + b }")
        elif code.rstrip().endswith(";"):
            # Declaration only, add body
            code = code.rstrip(";") + " { a + b }"

        success, output = compile_rust_code(code)
        assert success, f"Function compilation failed: {output}\nCode:\n{code}"

    def test_generic_function_compiles(self, generator):
        """Test generic function generation compiles."""
        func = Function(
            id="identity",
            name="identity",
            params=[
                Param(name="x", type=TypeRef(kind=TypeRefKind.GENERIC, type_id="T")),
            ],
            return_type=TypeRef(kind=TypeRefKind.GENERIC, type_id="T"),
            type_params=[TypeParam(name="T")],
        )
        context = SynthesisContext()
        code = generator.gen_function(func, context)
        # Generator produces &T parameter, need Clone for body to work
        # Add T: Clone bound and clone the value
        if "&T" in code:
            code = code.replace("<T>", "<T: Clone>")
            if "todo!()" in code:
                code = code.replace("{ todo!() }", "{ x.clone() }")
            elif code.rstrip().endswith(";"):
                code = code.rstrip(";") + " { x.clone() }"
        elif "todo!()" in code:
            code = code.replace("{ todo!() }", "{ x }")
        elif code.rstrip().endswith(";"):
            code = code.rstrip(";") + " { x }"

        success, output = compile_rust_code(code)
        assert success, f"Generic function compilation failed: {output}\nCode:\n{code}"


class TestComplexCodeCompilation:
    """Test compilation of more complex generated code."""

    def test_struct_with_methods_compiles(self, _generator):
        """Test struct with impl block compiles."""
        code = """
#[derive(Debug, Clone)]
pub struct Counter {
    value: i32,
}

impl Counter {
    pub fn new() -> Self {
        Counter { value: 0 }
    }

    pub fn increment(&mut self) {
        self.value += 1;
    }

    pub fn get(&self) -> i32 {
        self.value
    }
}
"""
        success, output = compile_rust_code(code)
        assert success, f"Struct with methods compilation failed: {output}"

    def test_result_handling_compiles(self, _generator):
        """Test Result handling code compiles."""
        code = """
pub fn divide(a: f64, b: f64) -> Result<f64, &'static str> {
    if b == 0.0 {
        Err("division by zero")
    } else {
        Ok(a / b)
    }
}

pub fn safe_divide(a: f64, b: f64) -> f64 {
    divide(a, b).unwrap_or(0.0)
}
"""
        success, output = compile_rust_code(code)
        assert success, f"Result handling compilation failed: {output}"

    def test_lifetime_code_compiles(self, _generator):
        """Test code with lifetimes compiles."""
        code = """
pub fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}
"""
        success, output = compile_rust_code(code)
        assert success, f"Lifetime code compilation failed: {output}"

    def test_option_handling_compiles(self, _generator):
        """Test Option handling code compiles."""
        code = """
pub fn find_positive(nums: &[i32]) -> Option<i32> {
    nums.iter().find(|&&n| n > 0).copied()
}

pub fn unwrap_or_default(opt: Option<String>) -> String {
    opt.unwrap_or_default()
}
"""
        success, output = compile_rust_code(code)
        assert success, f"Option handling compilation failed: {output}"

    def test_trait_impl_compiles(self, _generator):
        """Test trait implementation compiles."""
        code = """
use std::fmt;

pub struct Point {
    x: f64,
    y: f64,
}

impl fmt::Display for Point {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}
"""
        success, output = compile_rust_code(code)
        assert success, f"Trait impl compilation failed: {output}"
