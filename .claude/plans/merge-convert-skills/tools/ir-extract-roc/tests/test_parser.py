"""Tests for Roc parser."""

from __future__ import annotations

import pytest

from ir_extract_roc.parser import Purity, RocParser


@pytest.fixture
def parser() -> RocParser:
    """Create a parser instance."""
    return RocParser()


class TestAppParsing:
    """Tests for app header parsing."""

    def test_simple_app(self, parser: RocParser) -> None:
        """Test parsing simple app header."""
        source = '''app [main] { pf: platform "https://github.com/roc-lang/basic-cli/releases/download/0.7.0/bkGby8jb0tmZYsy2hg1E_B2QrCgcSTxdUlHtETwm5m4.tar.br" }

main = "Hello, World!"
'''
        result = parser.parse(source)
        assert result["app"] is not None
        assert result["app"].provides == ["main"]
        assert "basic-cli" in result["app"].platform

    def test_app_with_multiple_provides(self, parser: RocParser) -> None:
        """Test app with multiple provided values."""
        source = '''app [main, helper, Model] { pf: platform "..." }
'''
        result = parser.parse(source)
        assert result["app"] is not None
        assert len(result["app"].provides) == 3


class TestImportParsing:
    """Tests for import declaration parsing."""

    def test_simple_import(self, parser: RocParser) -> None:
        """Test simple import."""
        source = '''import pf.Stdout
'''
        result = parser.parse(source)
        assert len(result["imports"]) == 1
        assert result["imports"][0].module == "pf.Stdout"

    def test_import_with_exposing(self, parser: RocParser) -> None:
        """Test import with exposing clause."""
        source = '''import pf.Task exposing [Task, await]
'''
        result = parser.parse(source)
        assert len(result["imports"]) == 1
        assert result["imports"][0].module == "pf.Task"
        assert "Task" in result["imports"][0].exposing
        assert "await" in result["imports"][0].exposing


class TestRecordParsing:
    """Tests for record type parsing."""

    def test_simple_record(self, parser: RocParser) -> None:
        """Test simple record type."""
        source = '''User : { name: Str, age: I64 }
'''
        result = parser.parse(source)
        assert len(result["records"]) == 1
        user = result["records"][0]
        assert user.name == "User"
        assert len(user.fields) == 2

    def test_record_with_optional_field(self, parser: RocParser) -> None:
        """Test record with optional field."""
        source = '''Config : { host: Str, port?: I64 }
'''
        result = parser.parse(source)
        config = result["records"][0]
        port_field = next(f for f in config.fields if f.name == "port")
        assert port_field.optional is True


class TestTagUnionParsing:
    """Tests for tag union parsing."""

    def test_simple_tag_union(self, parser: RocParser) -> None:
        """Test simple tag union."""
        source = '''Result a e : [Ok a, Err e]
'''
        result = parser.parse(source)
        assert len(result["tag_unions"]) == 1
        union = result["tag_unions"][0]
        assert union.name == "Result a e"
        assert len(union.variants) == 2

    def test_tag_union_without_payload(self, parser: RocParser) -> None:
        """Test tag union without payload."""
        source = '''Status : [Pending, Active, Complete]
'''
        result = parser.parse(source)
        union = result["tag_unions"][0]
        assert len(union.variants) == 3
        for variant in union.variants:
            assert len(variant.payload_types) == 0


class TestFunctionParsing:
    """Tests for function parsing."""

    def test_simple_function(self, parser: RocParser) -> None:
        """Test simple function."""
        source = '''add : I64, I64 -> I64
add = \\a, b -> a + b
'''
        result = parser.parse(source)
        assert len(result["functions"]) == 1
        func = result["functions"][0]
        assert func.name == "add"
        assert func.purity == Purity.PURE

    def test_function_returning_task(self, parser: RocParser) -> None:
        """Test function returning Task."""
        source = '''greet : Str -> Task {} *
greet = \\name ->
    Stdout.line "Hello, $(name)!"
'''
        result = parser.parse(source)
        func = result["functions"][0]
        assert func.is_task is True
        assert func.purity == Purity.PLATFORM_TASK

    def test_function_returning_result(self, parser: RocParser) -> None:
        """Test function returning Result."""
        source = '''parseInt : Str -> Result I64 [InvalidNumber]
parseInt = \\str ->
    when Str.toI64 str is
        Ok n -> Ok n
        Err _ -> Err InvalidNumber
'''
        result = parser.parse(source)
        func = result["functions"][0]
        assert func.returns_result is True


class TestPatternMatching:
    """Tests for pattern matching detection."""

    def test_has_pattern_matching(self, parser: RocParser) -> None:
        """Test detection of when...is expression."""
        source = '''
process = \\value ->
    when value is
        Ok n -> n * 2
        Err _ -> 0
'''
        assert parser.has_pattern_matching(source) is True

    def test_extract_pattern_matches(self, parser: RocParser) -> None:
        """Test extraction of pattern match branches."""
        source = '''
describe = \\animal ->
    when animal is
        Dog -> "A dog"
        Cat -> "A cat"
        Bird -> "A bird"
'''
        matches = parser.extract_pattern_matches(source)
        assert len(matches) == 1
        assert len(matches[0]["branches"]) == 3


class TestPurity:
    """Tests for purity detection."""

    def test_pure_function(self, parser: RocParser) -> None:
        """Test pure function detection."""
        source = '''double : I64 -> I64
double = \\n -> n * 2
'''
        result = parser.parse(source)
        assert result["functions"][0].purity == Purity.PURE

    def test_effectful_function(self, parser: RocParser) -> None:
        """Test effectful function detection."""
        source = '''main : Task {} *
main = Stdout.line "Hello"
'''
        result = parser.parse(source)
        assert result["functions"][0].purity == Purity.PLATFORM_TASK
