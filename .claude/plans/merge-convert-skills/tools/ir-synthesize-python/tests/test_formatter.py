"""Tests for the Python formatter."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from ir_core.models import (
    ExtractionMode,
    Function,
    IRVersion,
    Module,
    ModuleMetadata,
    TypeRef,
    TypeRefKind,
    Visibility,
)
from ir_synthesize_python.formatter import FormatResult, FormatterConfig, PythonFormatter


@pytest.fixture
def formatter() -> PythonFormatter:
    """Create a formatter instance."""
    return PythonFormatter(line_length=88, use_black=False, use_ruff=False)


class TestBasicFormatting:
    """Tests for basic formatting operations."""

    def test_format_simple_code(self, formatter: PythonFormatter) -> None:
        """Test formatting simple code."""
        code = "def hello():return 'world'"
        result = formatter.format_with_result(code)
        assert result.success
        # Basic formatting should at least normalize line endings
        assert result.code is not None

    def test_format_removes_trailing_whitespace(self, formatter: PythonFormatter) -> None:
        """Test that trailing whitespace is removed."""
        code = "x = 1   \ny = 2  \n"
        result = formatter.format_with_result(code)
        assert result.success
        lines = result.code.split("\n")
        for line in lines:
            assert line == line.rstrip()

    def test_format_ensures_trailing_newline(self, formatter: PythonFormatter) -> None:
        """Test that file ends with newline."""
        code = "x = 1"
        result = formatter.format_with_result(code)
        assert result.success
        assert result.code.endswith("\n")

    def test_format_normalizes_blank_lines(self, formatter: PythonFormatter) -> None:
        """Test that multiple blank lines are normalized."""
        code = "x = 1\n\n\n\n\ny = 2"
        result = formatter.format_with_result(code)
        assert result.success
        # Should not have more than 2 consecutive blank lines
        assert "\n\n\n" not in result.code


class TestBlackIntegration:
    """Tests for black integration (may be skipped if black not available)."""

    def test_format_with_black_available(self) -> None:
        """Test formatting with black if available."""
        try:
            import black
        except ImportError:
            pytest.skip("black not installed")

        formatter = PythonFormatter(use_black=True)
        code = "def hello(   ):return 'world'"
        result = formatter.format_with_result(code)

        if formatter._black_available:
            assert result.success
            assert result.tool == "black"
            # Black should properly format the code
            assert "def hello():" in result.code

    def test_format_fallback_when_black_fails(self) -> None:
        """Test that formatting falls back when black fails."""
        formatter = PythonFormatter(use_black=True)
        # Invalid Python that black can't format
        code = "this is not valid python {"
        result = formatter.format_with_result(code)
        # Should fall back to basic formatting
        assert result.code is not None


class TestRuffIntegration:
    """Tests for ruff integration (may be skipped if ruff not available)."""

    def test_format_with_ruff_available(self) -> None:
        """Test formatting with ruff if available."""
        formatter = PythonFormatter(use_black=False, use_ruff=True)

        if not formatter._ruff_available:
            pytest.skip("ruff not installed")

        code = "def hello(   ):return 'world'"
        result = formatter.format_with_result(code)

        assert result.success
        assert result.tool == "ruff"


class TestDocstringAddition:
    """Tests for adding docstrings to code."""

    @pytest.fixture
    def minimal_ir(self) -> IRVersion:
        """Create minimal IR with docstrings."""
        return IRVersion(
            version="ir-v1.0",
            module=Module(
                id="module:test",
                name="test",
                path=["test"],
                visibility=Visibility.PUBLIC,
                imports=[],
                exports=[],
                definitions=[],
                submodules=[],
                extraction_scope="full",
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                    extraction_version="ir-v1.0",
                    extraction_mode=ExtractionMode.FULL_MODULE,
                    extraction_timestamp=datetime.now(UTC),
                    documentation="This is the module docstring.",
                ),
            ),
            types=[],
            functions=[
                Function(
                    id="func:test:0",
                    name="hello",
                    params=[],
                    return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="str"),
                    effects=[],
                    visibility=Visibility.PUBLIC,
                    doc_comment="Say hello.",
                ),
            ],
        )

    def test_add_docstrings(
        self, formatter: PythonFormatter, minimal_ir: IRVersion
    ) -> None:
        """Test adding docstrings to code."""
        code = '''def hello():
    return "world"
'''
        result = formatter.add_docstrings(code, minimal_ir)

        # Should have the function docstring added
        assert '"""Say hello."""' in result or "Say hello" in result


class TestFormatterConfig:
    """Tests for formatter configuration."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = FormatterConfig()
        assert config.line_length == 88
        assert config.indent_size == 4
        assert config.use_tabs is False
        assert config.target_version == "py311"

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = FormatterConfig(
            line_length=100,
            indent_size=2,
            use_tabs=True,
            target_version="py310",
        )
        assert config.line_length == 100
        assert config.indent_size == 2
        assert config.use_tabs is True
        assert config.target_version == "py310"


class TestHelperMethods:
    """Tests for helper methods."""

    def test_extract_def_name(self, formatter: PythonFormatter) -> None:
        """Test extracting function name from def line."""
        assert formatter._extract_def_name("def hello():") == "hello"
        assert formatter._extract_def_name("def add(a, b):") == "add"
        assert formatter._extract_def_name("async def fetch():") == "fetch"

    def test_extract_class_name(self, formatter: PythonFormatter) -> None:
        """Test extracting class name from class line."""
        assert formatter._extract_class_name("class MyClass:") == "MyClass"
        assert formatter._extract_class_name("class MyClass(Base):") == "MyClass"
        assert formatter._extract_class_name("class Generic[T]:") == "Generic"

    def test_is_docstring(self, formatter: PythonFormatter) -> None:
        """Test detecting docstring lines."""
        assert formatter._is_docstring('    """This is a docstring."""')
        assert formatter._is_docstring("    '''Single quotes.'''")
        assert not formatter._is_docstring("    x = 1")
        assert not formatter._is_docstring("    # comment")

    def test_get_indent(self, formatter: PythonFormatter) -> None:
        """Test getting indentation from lines."""
        assert formatter._get_indent("    x = 1") == "    "
        assert formatter._get_indent("        y = 2") == "        "
        assert formatter._get_indent("x = 1") == ""
        assert formatter._get_indent("\tx = 1") == "\t"


class TestFormatResult:
    """Tests for FormatResult class."""

    def test_success_result(self) -> None:
        """Test creating a success result."""
        result = FormatResult(
            code="formatted code",
            success=True,
            tool="black",
        )
        assert result.success
        assert result.code == "formatted code"
        assert result.tool == "black"
        assert result.error is None

    def test_failure_result(self) -> None:
        """Test creating a failure result."""
        result = FormatResult(
            code="original code",
            success=False,
            error="Formatting failed",
            tool="black",
        )
        assert not result.success
        assert result.error == "Formatting failed"
