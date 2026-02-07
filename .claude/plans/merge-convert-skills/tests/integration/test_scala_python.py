"""Integration tests for Scala <-> Python conversion."""

from __future__ import annotations

import pytest
from pathlib import Path

from ir_core.models import IRVersion, TypeDef, TypeKind, FunctionDef, Parameter
from ir_core.base import ExtractConfig, SynthConfig

from ir_extract_scala import ScalaExtractor
from ir_synthesize_scala import ScalaSynthesizer
from ir_extract_python import PythonExtractor
from ir_synthesize_python import PythonSynthesizer


FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestScalaExtraction:
    """Tests for Scala source extraction."""

    @pytest.fixture
    def extractor(self) -> ScalaExtractor:
        return ScalaExtractor()

    @pytest.fixture
    def config(self) -> ExtractConfig:
        return ExtractConfig()

    def test_extract_case_class(
        self, extractor: ScalaExtractor, config: ExtractConfig
    ) -> None:
        """Test extraction of case class."""
        source = '''
case class Point(x: Int, y: Int)
'''
        ir = extractor.extract(source, "test.scala", config)

        assert ir.source_language == "scala"
        assert len(ir.types) >= 1

        point = next((t for t in ir.types if t.name == "Point"), None)
        assert point is not None
        assert point.kind == TypeKind.STRUCT

    def test_extract_trait(
        self, extractor: ScalaExtractor, config: ExtractConfig
    ) -> None:
        """Test extraction of trait."""
        source = '''
trait Greeting {
  def greet(name: String): String
}
'''
        ir = extractor.extract(source, "test.scala", config)

        assert len(ir.types) >= 1
        greeting = next((t for t in ir.types if t.name == "Greeting"), None)
        assert greeting is not None
        assert greeting.kind == TypeKind.INTERFACE

    def test_extract_hkt(
        self, extractor: ScalaExtractor, config: ExtractConfig
    ) -> None:
        """Test extraction of higher-kinded type."""
        source = '''
trait Functor[F[_]] {
  def map[A, B](fa: F[A])(f: A => B): F[B]
}
'''
        ir = extractor.extract(source, "test.scala", config)

        functor = next((t for t in ir.types if t.name == "Functor"), None)
        assert functor is not None

        # Check for HKT annotation
        hkt_annotations = [a for a in ir.annotations if a.kind == "SC-001"]
        assert len(hkt_annotations) > 0

    def test_extract_variance(
        self, extractor: ScalaExtractor, config: ExtractConfig
    ) -> None:
        """Test extraction of variance annotations."""
        source = '''
trait Producer[+T] {
  def produce: T
}

trait Consumer[-T] {
  def consume(t: T): Unit
}
'''
        ir = extractor.extract(source, "test.scala", config)

        # Check for variance annotations
        variance_annotations = [a for a in ir.annotations if a.kind == "SC-002"]
        assert len(variance_annotations) >= 2


class TestScalaSynthesis:
    """Tests for Scala code synthesis."""

    @pytest.fixture
    def synthesizer(self) -> ScalaSynthesizer:
        return ScalaSynthesizer()

    @pytest.fixture
    def config(self) -> SynthConfig:
        return SynthConfig()

    def test_synthesize_case_class(
        self, synthesizer: ScalaSynthesizer, config: SynthConfig
    ) -> None:
        """Test synthesis of case class."""
        ir = IRVersion(
            version="ir-v1.0",
            source_language="python",
            source_path="test.py",
        )

        ir.types.append(TypeDef(
            name="User",
            kind=TypeKind.STRUCT,
            properties=[
                {"name": "name", "type": "String"},
                {"name": "age", "type": "Int"},
            ],
        ))

        code = synthesizer.synthesize(ir, config)

        assert "case class User" in code
        assert "name: String" in code
        assert "age: Int" in code

    def test_synthesize_trait(
        self, synthesizer: ScalaSynthesizer, config: SynthConfig
    ) -> None:
        """Test synthesis of trait."""
        ir = IRVersion(
            version="ir-v1.0",
            source_language="python",
            source_path="test.py",
        )

        ir.types.append(TypeDef(
            name="Printable",
            kind=TypeKind.INTERFACE,
            methods=[
                {"name": "print", "return_type": "String"}
            ],
        ))

        code = synthesizer.synthesize(ir, config)

        assert "trait Printable" in code
        assert "def print" in code

    def test_synthesize_function(
        self, synthesizer: ScalaSynthesizer, config: SynthConfig
    ) -> None:
        """Test synthesis of function."""
        ir = IRVersion(
            version="ir-v1.0",
            source_language="python",
            source_path="test.py",
        )

        ir.functions.append(FunctionDef(
            name="double",
            parameters=[Parameter(name="n", type_annotation="Int")],
            return_type="Int",
        ))

        code = synthesizer.synthesize(ir, config)

        assert "def double" in code
        assert "n: Int" in code
        assert ": Int" in code


class TestPythonToScalaConversion:
    """Tests for Python to Scala conversion."""

    @pytest.fixture
    def py_extractor(self) -> PythonExtractor:
        return PythonExtractor()

    @pytest.fixture
    def scala_synthesizer(self) -> ScalaSynthesizer:
        return ScalaSynthesizer()

    def test_convert_dataclass(
        self, py_extractor: PythonExtractor, scala_synthesizer: ScalaSynthesizer
    ) -> None:
        """Test converting Python dataclass to Scala case class."""
        python_code = '''
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str
'''
        extract_config = ExtractConfig()
        ir = py_extractor.extract(python_code, "test.py", extract_config)

        synth_config = SynthConfig()
        scala_code = scala_synthesizer.synthesize(ir, synth_config)

        assert "case class" in scala_code or "User" in scala_code

    def test_convert_function(
        self, py_extractor: PythonExtractor, scala_synthesizer: ScalaSynthesizer
    ) -> None:
        """Test converting Python function to Scala."""
        python_code = '''
def double(n: int) -> int:
    return n * 2
'''
        extract_config = ExtractConfig()
        ir = py_extractor.extract(python_code, "test.py", extract_config)

        synth_config = SynthConfig()
        scala_code = scala_synthesizer.synthesize(ir, synth_config)

        assert "double" in scala_code
        assert "Int" in scala_code

    def test_gap_detection(
        self, py_extractor: PythonExtractor, scala_synthesizer: ScalaSynthesizer
    ) -> None:
        """Test that Python-specific patterns are flagged."""
        python_code = '''
def dynamic_function(x):
    if isinstance(x, int):
        return x * 2
    return str(x)
'''
        extract_config = ExtractConfig()
        ir = py_extractor.extract(python_code, "test.py", extract_config)

        gaps = scala_synthesizer.detect_cross_language_gaps(ir, "scala")

        gap_kinds = [g.kind for g in gaps]
        assert any("PY-SC" in k for k in gap_kinds)


class TestScalaToPythonConversion:
    """Tests for Scala to Python conversion."""

    @pytest.fixture
    def scala_extractor(self) -> ScalaExtractor:
        return ScalaExtractor()

    @pytest.fixture
    def py_synthesizer(self) -> PythonSynthesizer:
        return PythonSynthesizer()

    def test_convert_case_class(
        self, scala_extractor: ScalaExtractor, py_synthesizer: PythonSynthesizer
    ) -> None:
        """Test converting Scala case class to Python."""
        scala_code = '''
case class Point(x: Int, y: Int)
'''
        extract_config = ExtractConfig()
        ir = scala_extractor.extract(scala_code, "test.scala", extract_config)

        synth_config = SynthConfig()
        python_code = py_synthesizer.synthesize(ir, synth_config)

        assert "Point" in python_code
        assert "int" in python_code or "x" in python_code


class TestFixtureFiles:
    """Tests using fixture files."""

    @pytest.fixture
    def extractor(self) -> ScalaExtractor:
        return ScalaExtractor()

    @pytest.fixture
    def config(self) -> ExtractConfig:
        return ExtractConfig()

    def test_extract_case_classes_fixture(
        self, extractor: ScalaExtractor, config: ExtractConfig
    ) -> None:
        """Test extraction from case_classes.scala fixture."""
        fixture_path = FIXTURES_DIR / "scala" / "types" / "case_classes.scala"
        if not fixture_path.exists():
            pytest.skip(f"Fixture not found: {fixture_path}")

        source = fixture_path.read_text()
        ir = extractor.extract(source, str(fixture_path), config)

        assert ir.source_language == "scala"
        assert len(ir.types) > 0

    def test_extract_higher_kinded_fixture(
        self, extractor: ScalaExtractor, config: ExtractConfig
    ) -> None:
        """Test extraction from higher_kinded.scala fixture."""
        fixture_path = FIXTURES_DIR / "scala" / "types" / "higher_kinded.scala"
        if not fixture_path.exists():
            pytest.skip(f"Fixture not found: {fixture_path}")

        source = fixture_path.read_text()
        ir = extractor.extract(source, str(fixture_path), config)

        # Should detect HKT patterns
        hkt_annotations = [a for a in ir.annotations if "SC-001" in a.kind]
        assert len(hkt_annotations) > 0 or len(ir.types) > 0

    def test_extract_variance_fixture(
        self, extractor: ScalaExtractor, config: ExtractConfig
    ) -> None:
        """Test extraction from variance.scala fixture."""
        fixture_path = FIXTURES_DIR / "scala" / "types" / "variance.scala"
        if not fixture_path.exists():
            pytest.skip(f"Fixture not found: {fixture_path}")

        source = fixture_path.read_text()
        ir = extractor.extract(source, str(fixture_path), config)

        assert len(ir.types) > 0
