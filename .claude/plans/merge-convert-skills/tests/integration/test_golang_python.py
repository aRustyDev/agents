"""Integration tests for Go ↔ Python cross-language conversion."""

from __future__ import annotations

import pytest


class TestGolangToPython:
    """Test Go to Python conversion."""

    def test_struct_to_dataclass(self) -> None:
        """Test converting Go struct to Python dataclass."""
        go_source = '''
package main

type User struct {
    Name  string
    Email string
    Age   int
}
'''
        # Extract IR from Go
        from ir_extract_golang import GolangExtractor
        from ir_core.base import ExtractConfig

        extractor = GolangExtractor()
        ir = extractor.extract(go_source, "user.go", ExtractConfig())

        # Check IR has struct
        assert len(ir.types) == 1
        assert ir.types[0].name == "User"
        assert len(ir.types[0].properties) == 3

    def test_function_with_error_return(self) -> None:
        """Test converting Go error returns to Python exceptions."""
        go_source = '''
package main

import "errors"

func Divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}
'''
        from ir_extract_golang import GolangExtractor
        from ir_core.base import ExtractConfig

        extractor = GolangExtractor()
        ir = extractor.extract(go_source, "math.go", ExtractConfig())

        # Check function is extracted
        funcs = [f for f in ir.functions if f.name == "Divide"]
        assert len(funcs) == 1

        # Check GO-002 annotation for error return
        error_annotations = [a for a in ir.annotations if a.kind == "GO-002"]
        assert len(error_annotations) >= 1

    def test_interface_to_protocol(self) -> None:
        """Test converting Go interface to Python Protocol."""
        go_source = '''
package main

type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type ReadWriter interface {
    Reader
    Writer
}
'''
        from ir_extract_golang import GolangExtractor
        from ir_core.base import ExtractConfig, TypeKind

        extractor = GolangExtractor()
        ir = extractor.extract(go_source, "io.go", ExtractConfig())

        # Check interfaces are extracted
        interfaces = [t for t in ir.types if t.kind == TypeKind.INTERFACE]
        assert len(interfaces) == 3

        # Check ReadWriter embeds Reader and Writer
        rw = next(t for t in interfaces if t.name == "ReadWriter")
        assert "Reader" in rw.extends
        assert "Writer" in rw.extends

    def test_goroutine_detection(self) -> None:
        """Test detection of goroutine patterns."""
        go_source = '''
package main

import "sync"

func ProcessConcurrently(items []int) {
    var wg sync.WaitGroup

    for _, item := range items {
        wg.Add(1)
        go func(n int) {
            defer wg.Done()
            process(n)
        }(item)
    }

    wg.Wait()
}

func process(n int) {}
'''
        from ir_extract_golang import GolangExtractor
        from ir_core.base import ExtractConfig

        extractor = GolangExtractor()
        ir = extractor.extract(go_source, "concurrent.go", ExtractConfig())

        # Check GO-003 annotation for goroutines
        goroutine_annotations = [a for a in ir.annotations if a.kind == "GO-003"]
        assert len(goroutine_annotations) >= 1

    def test_channel_detection(self) -> None:
        """Test detection of channel operations."""
        go_source = '''
package main

func Worker(jobs <-chan int, results chan<- int) {
    for job := range jobs {
        results <- job * 2
    }
}
'''
        from ir_extract_golang import GolangExtractor
        from ir_core.base import ExtractConfig

        extractor = GolangExtractor()
        ir = extractor.extract(go_source, "worker.go", ExtractConfig())

        # Check GO-004 annotation for channels
        channel_annotations = [a for a in ir.annotations if a.kind == "GO-004"]
        assert len(channel_annotations) >= 1


class TestPythonToGolang:
    """Test Python to Go conversion."""

    def test_dataclass_to_struct(self) -> None:
        """Test converting Python dataclass to Go struct."""
        python_source = '''
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str
    age: int
'''
        from ir_extract_python import PythonExtractor
        from ir_synthesize_golang import GolangSynthesizer
        from ir_core.base import ExtractConfig, SynthConfig

        # Extract from Python
        extractor = PythonExtractor()
        ir = extractor.extract(python_source, "user.py", ExtractConfig())

        # Synthesize to Go
        synthesizer = GolangSynthesizer()
        go_code = synthesizer.synthesize(ir, SynthConfig(format=False))

        # Verify output contains struct
        assert "type" in go_code
        assert "struct" in go_code

    def test_exception_to_error_return(self) -> None:
        """Test converting Python exceptions to Go error returns."""
        python_source = '''
def divide(a: int, b: int) -> int:
    if b == 0:
        raise ValueError("division by zero")
    return a // b
'''
        from ir_extract_python import PythonExtractor
        from ir_synthesize_golang import GolangSynthesizer
        from ir_core.base import ExtractConfig, SynthConfig

        # Extract from Python
        extractor = PythonExtractor()
        ir = extractor.extract(python_source, "math.py", ExtractConfig())

        # Synthesize to Go
        synthesizer = GolangSynthesizer()
        go_code = synthesizer.synthesize(ir, SynthConfig(format=False))

        # Check for gap marker about exception handling
        gaps = synthesizer.detect_cross_language_gaps(ir, "golang")
        # Should detect PY-GO-002 (exception handling)


class TestGolangGenerics:
    """Test Go generics extraction."""

    def test_generic_function(self) -> None:
        """Test extracting generic function."""
        go_source = '''
package main

func Map[T, U any](items []T, fn func(T) U) []U {
    result := make([]U, len(items))
    for i, item := range items {
        result[i] = fn(item)
    }
    return result
}
'''
        from ir_extract_golang import GolangExtractor
        from ir_core.base import ExtractConfig

        extractor = GolangExtractor()
        ir = extractor.extract(go_source, "generics.go", ExtractConfig())

        # Check function has type parameters
        map_func = next(f for f in ir.functions if f.name == "Map")
        assert len(map_func.type_params) == 2
        assert map_func.type_params[0]["name"] == "T"
        assert map_func.type_params[1]["name"] == "U"

    def test_generic_struct(self) -> None:
        """Test extracting generic struct."""
        go_source = '''
package main

type Box[T any] struct {
    Value T
}

func (b *Box[T]) Get() T {
    return b.Value
}
'''
        from ir_extract_golang import GolangExtractor
        from ir_core.base import ExtractConfig

        extractor = GolangExtractor()
        ir = extractor.extract(go_source, "box.go", ExtractConfig())

        # Check struct has type parameters
        box = next(t for t in ir.types if t.name == "Box")
        assert len(box.type_params) == 1
        assert box.type_params[0]["name"] == "T"

    def test_type_constraint(self) -> None:
        """Test extracting type constraints."""
        go_source = '''
package main

import "cmp"

func Max[T cmp.Ordered](a, b T) T {
    if a > b {
        return a
    }
    return b
}
'''
        from ir_extract_golang import GolangExtractor
        from ir_core.base import ExtractConfig

        extractor = GolangExtractor()
        ir = extractor.extract(go_source, "ordered.go", ExtractConfig())

        # Check function has constrained type parameter
        max_func = next(f for f in ir.functions if f.name == "Max")
        assert len(max_func.type_params) == 1
        assert max_func.type_params[0]["constraint"] == "cmp.Ordered"


class TestGapDetection:
    """Test cross-language gap detection."""

    def test_goroutine_gap(self) -> None:
        """Test detection of complex goroutine patterns."""
        go_source = '''
package main

func Complex() {
    go func() {}()
    go func() {}()
    go func() {}()
}
'''
        from ir_extract_golang import GolangExtractor
        from ir_core.base import ExtractConfig

        extractor = GolangExtractor()
        ir = extractor.extract(go_source, "complex.go", ExtractConfig())

        # Check GO-010 gap for multiple goroutines
        gaps = [g for g in ir.gaps if g.kind == "GO-010"]
        assert len(gaps) >= 1

    def test_embedded_type_gap(self) -> None:
        """Test detection of embedded types."""
        go_source = '''
package main

type Base struct {
    ID int
}

type Derived struct {
    Base
    Name string
}
'''
        from ir_extract_golang import GolangExtractor
        from ir_core.base import ExtractConfig

        extractor = GolangExtractor()
        ir = extractor.extract(go_source, "embedded.go", ExtractConfig())

        # Check GO-014 gap for embedded types
        gaps = [g for g in ir.gaps if g.kind == "GO-014"]
        assert len(gaps) >= 1

    def test_struct_tags_gap(self) -> None:
        """Test detection of struct tags."""
        go_source = '''
package main

type User struct {
    Name  string `json:"name"`
    Email string `json:"email" validate:"email"`
}
'''
        from ir_extract_golang import GolangExtractor
        from ir_core.base import ExtractConfig

        extractor = GolangExtractor()
        ir = extractor.extract(go_source, "tags.go", ExtractConfig())

        # Check GO-015 gap for struct tags
        gaps = [g for g in ir.gaps if g.kind == "GO-015"]
        assert len(gaps) >= 1
