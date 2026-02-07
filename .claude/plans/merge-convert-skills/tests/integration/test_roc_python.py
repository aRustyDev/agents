"""Integration tests for Roc <-> Python conversion."""

from __future__ import annotations

from pathlib import Path

import pytest
from ir_core.base import ExtractConfig, SynthConfig

# Import IR core
from ir_core.models import IRVersion, TypeDef, TypeKind
from ir_extract_python import PythonExtractor

# Import extractors and synthesizers
from ir_extract_roc import RocExtractor
from ir_synthesize_python import PythonSynthesizer
from ir_synthesize_roc import RocSynthesizer

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestRocExtraction:
    """Tests for Roc source extraction."""

    @pytest.fixture
    def extractor(self) -> RocExtractor:
        """Create Roc extractor."""
        return RocExtractor()

    @pytest.fixture
    def config(self) -> ExtractConfig:
        """Create extraction config."""
        return ExtractConfig()

    def test_extract_pure_functions(self, extractor: RocExtractor, config: ExtractConfig) -> None:
        """Test extraction of pure functions."""
        source = """
module [double, add]

double : I64 -> I64
double = \\n ->
    n * 2

add : I64, I64 -> I64
add = \\a, b ->
    a + b
"""
        ir = extractor.extract(source, "test.roc", config)

        assert ir.source_language == "roc"
        assert len(ir.functions) >= 2

        # Find double function
        double_fn = next((f for f in ir.functions if f.name == "double"), None)
        assert double_fn is not None
        assert double_fn.return_type == "I64"
        assert len(double_fn.parameters) == 1

    def test_extract_record_types(self, extractor: RocExtractor, config: ExtractConfig) -> None:
        """Test extraction of record types."""
        source = """
module [User, createUser]

User : {
    id : U64,
    name : Str,
    email : Str,
}

createUser : U64, Str, Str -> User
createUser = \\id, name, email ->
    { id, name, email }
"""
        ir = extractor.extract(source, "test.roc", config)

        # Find User type
        user_type = next((t for t in ir.types if t.name == "User"), None)
        assert user_type is not None
        assert user_type.kind == TypeKind.STRUCT

    def test_extract_tag_unions(self, extractor: RocExtractor, config: ExtractConfig) -> None:
        """Test extraction of tag unions."""
        source = """
module [Status, Color]

Status : [Pending, Active, Complete, Error Str]

Color : [Red, Green, Blue]
"""
        ir = extractor.extract(source, "test.roc", config)

        # Find Status type
        status_type = next((t for t in ir.types if t.name == "Status"), None)
        assert status_type is not None
        assert status_type.kind == TypeKind.ENUM

    def test_extract_pattern_matching(self, extractor: RocExtractor, config: ExtractConfig) -> None:
        """Test extraction of pattern matching."""
        source = """
module [describe]

describe : I64 -> Str
describe = \\n ->
    when n is
        0 -> "zero"
        1 -> "one"
        _ -> "many"
"""
        ir = extractor.extract(source, "test.roc", config)

        describe_fn = next((f for f in ir.functions if f.name == "describe"), None)
        assert describe_fn is not None


class TestRocSynthesis:
    """Tests for Roc code synthesis."""

    @pytest.fixture
    def synthesizer(self) -> RocSynthesizer:
        """Create Roc synthesizer."""
        return RocSynthesizer()

    @pytest.fixture
    def config(self) -> SynthConfig:
        """Create synthesis config."""
        return SynthConfig()

    def test_synthesize_simple_function(
        self, synthesizer: RocSynthesizer, config: SynthConfig
    ) -> None:
        """Test synthesis of simple function."""
        ir = IRVersion(
            version="ir-v1.0",
            source_language="python",
            source_path="test.py",
        )

        ir.functions.append(
            FunctionDef(
                name="double",
                parameters=[Parameter(name="n", type_annotation="I64")],
                return_type="I64",
            )
        )

        code = synthesizer.synthesize(ir, config)

        assert "double" in code
        assert "I64" in code
        assert "->" in code

    def test_synthesize_record_type(self, synthesizer: RocSynthesizer, config: SynthConfig) -> None:
        """Test synthesis of record type."""
        ir = IRVersion(
            version="ir-v1.0",
            source_language="python",
            source_path="test.py",
        )

        ir.types.append(
            TypeDef(
                name="User",
                kind=TypeKind.STRUCT,
                properties=[
                    {"name": "name", "type": "Str"},
                    {"name": "age", "type": "I64"},
                ],
            )
        )

        code = synthesizer.synthesize(ir, config)

        assert "User" in code
        assert "name : Str" in code
        assert "age : I64" in code

    def test_synthesize_tag_union(self, synthesizer: RocSynthesizer, config: SynthConfig) -> None:
        """Test synthesis of tag union."""
        ir = IRVersion(
            version="ir-v1.0",
            source_language="python",
            source_path="test.py",
        )

        ir.types.append(
            TypeDef(
                name="Status",
                kind=TypeKind.ENUM,
                enum_members=[
                    {"name": "Pending"},
                    {"name": "Active"},
                    {"name": "Complete"},
                ],
            )
        )

        code = synthesizer.synthesize(ir, config)

        assert "Pending" in code
        assert "Active" in code
        assert "Complete" in code


class TestPythonToRocConversion:
    """Tests for Python to Roc conversion."""

    @pytest.fixture
    def py_extractor(self) -> PythonExtractor:
        """Create Python extractor."""
        return PythonExtractor()

    @pytest.fixture
    def roc_synthesizer(self) -> RocSynthesizer:
        """Create Roc synthesizer."""
        return RocSynthesizer()

    def test_convert_simple_function(
        self, py_extractor: PythonExtractor, roc_synthesizer: RocSynthesizer
    ) -> None:
        """Test converting simple Python function to Roc."""
        python_code = """
def double(n: int) -> int:
    return n * 2
"""
        extract_config = ExtractConfig()
        ir = py_extractor.extract(python_code, "test.py", extract_config)

        synth_config = SynthConfig()
        roc_code = roc_synthesizer.synthesize(ir, synth_config)

        assert "double" in roc_code
        assert "I64" in roc_code

    def test_convert_dataclass_to_record(
        self, py_extractor: PythonExtractor, roc_synthesizer: RocSynthesizer
    ) -> None:
        """Test converting Python dataclass to Roc record."""
        python_code = """
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str
"""
        extract_config = ExtractConfig()
        ir = py_extractor.extract(python_code, "test.py", extract_config)

        synth_config = SynthConfig()
        roc_code = roc_synthesizer.synthesize(ir, synth_config)

        assert "User" in roc_code
        assert "Str" in roc_code or "name" in roc_code

    def test_gap_detection_exceptions(
        self, py_extractor: PythonExtractor, roc_synthesizer: RocSynthesizer
    ) -> None:
        """Test that Python exceptions are flagged as gaps."""
        python_code = """
def divide(a: int, b: int) -> int:
    if b == 0:
        raise ValueError("Division by zero")
    return a // b
"""
        extract_config = ExtractConfig()
        ir = py_extractor.extract(python_code, "test.py", extract_config)

        # Detect gaps for Roc target
        gaps = roc_synthesizer.detect_cross_language_gaps(ir, "roc")

        # Should detect exception usage
        gap_kinds = [g.kind for g in gaps]
        assert any("PY-ROC" in k for k in gap_kinds)


class TestRocToPythonConversion:
    """Tests for Roc to Python conversion."""

    @pytest.fixture
    def roc_extractor(self) -> RocExtractor:
        """Create Roc extractor."""
        return RocExtractor()

    @pytest.fixture
    def py_synthesizer(self) -> PythonSynthesizer:
        """Create Python synthesizer."""
        return PythonSynthesizer()

    def test_convert_pure_function(
        self, roc_extractor: RocExtractor, py_synthesizer: PythonSynthesizer
    ) -> None:
        """Test converting Roc pure function to Python."""
        roc_code = """
module [double]

double : I64 -> I64
double = \\n ->
    n * 2
"""
        extract_config = ExtractConfig()
        ir = roc_extractor.extract(roc_code, "test.roc", extract_config)

        synth_config = SynthConfig()
        python_code = py_synthesizer.synthesize(ir, synth_config)

        assert "def double" in python_code
        assert "int" in python_code

    def test_convert_record_to_dataclass(
        self, roc_extractor: RocExtractor, py_synthesizer: PythonSynthesizer
    ) -> None:
        """Test converting Roc record to Python dataclass."""
        roc_code = """
module [User]

User : {
    id : U64,
    name : Str,
    email : Str,
}
"""
        extract_config = ExtractConfig()
        ir = roc_extractor.extract(roc_code, "test.roc", extract_config)

        synth_config = SynthConfig()
        python_code = py_synthesizer.synthesize(ir, synth_config)

        assert "User" in python_code
        assert "str" in python_code or "name" in python_code


class TestRocRoundTrip:
    """Tests for Roc round-trip conversion."""

    @pytest.fixture
    def extractor(self) -> RocExtractor:
        """Create Roc extractor."""
        return RocExtractor()

    @pytest.fixture
    def synthesizer(self) -> RocSynthesizer:
        """Create Roc synthesizer."""
        return RocSynthesizer()

    def test_roundtrip_simple_function(
        self, extractor: RocExtractor, synthesizer: RocSynthesizer
    ) -> None:
        """Test Roc -> IR -> Roc round-trip."""
        original = """
module [double]

double : I64 -> I64
double = \\n ->
    n * 2
"""
        # Extract
        extract_config = ExtractConfig()
        ir = extractor.extract(original, "test.roc", extract_config)

        # Synthesize
        synth_config = SynthConfig()
        result = synthesizer.synthesize(ir, synth_config)

        # Verify key elements preserved
        assert "double" in result
        assert "I64" in result

    def test_roundtrip_record_type(
        self, extractor: RocExtractor, synthesizer: RocSynthesizer
    ) -> None:
        """Test record type round-trip."""
        original = """
module [Point]

Point : { x : I64, y : I64 }
"""
        extract_config = ExtractConfig()
        ir = extractor.extract(original, "test.roc", extract_config)

        synth_config = SynthConfig()
        result = synthesizer.synthesize(ir, synth_config)

        assert "Point" in result
        assert "x" in result
        assert "y" in result


class TestFixtureFiles:
    """Tests using fixture files."""

    @pytest.fixture
    def extractor(self) -> RocExtractor:
        """Create Roc extractor."""
        return RocExtractor()

    @pytest.fixture
    def config(self) -> ExtractConfig:
        """Create extraction config."""
        return ExtractConfig()

    def test_extract_pure_functions_fixture(
        self, extractor: RocExtractor, config: ExtractConfig
    ) -> None:
        """Test extraction from pure_functions.roc fixture."""
        fixture_path = FIXTURES_DIR / "roc" / "basics" / "pure_functions.roc"
        if not fixture_path.exists():
            pytest.skip(f"Fixture not found: {fixture_path}")

        source = fixture_path.read_text()
        ir = extractor.extract(source, str(fixture_path), config)

        assert ir.source_language == "roc"
        assert len(ir.functions) > 0

    def test_extract_records_fixture(self, extractor: RocExtractor, config: ExtractConfig) -> None:
        """Test extraction from records.roc fixture."""
        fixture_path = FIXTURES_DIR / "roc" / "types" / "records.roc"
        if not fixture_path.exists():
            pytest.skip(f"Fixture not found: {fixture_path}")

        source = fixture_path.read_text()
        ir = extractor.extract(source, str(fixture_path), config)

        assert len(ir.types) > 0

    def test_extract_tag_unions_fixture(
        self, extractor: RocExtractor, config: ExtractConfig
    ) -> None:
        """Test extraction from tag_unions.roc fixture."""
        fixture_path = FIXTURES_DIR / "roc" / "types" / "tag_unions.roc"
        if not fixture_path.exists():
            pytest.skip(f"Fixture not found: {fixture_path}")

        source = fixture_path.read_text()
        ir = extractor.extract(source, str(fixture_path), config)

        assert len(ir.types) > 0

    def test_extract_pattern_matching_fixture(
        self, extractor: RocExtractor, config: ExtractConfig
    ) -> None:
        """Test extraction from when_is.roc fixture."""
        fixture_path = FIXTURES_DIR / "roc" / "patterns" / "when_is.roc"
        if not fixture_path.exists():
            pytest.skip(f"Fixture not found: {fixture_path}")

        source = fixture_path.read_text()
        ir = extractor.extract(source, str(fixture_path), config)

        assert len(ir.functions) > 0
