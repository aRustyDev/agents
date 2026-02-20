"""Tests for JSDoc parser."""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path for direct import
sys.path.insert(0, str(Path(__file__).parent.parent / "ir_extract_typescript"))


from jsdoc import (
    JSDocParser,
    extract_jsdoc_from_source,
    get_preceding_jsdoc,
)


class TestJSDocParser:
    """Test JSDoc parsing."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = JSDocParser()

    def test_parse_simple_description(self) -> None:
        """Test parsing simple description."""
        comment = """/**
         * A simple description.
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert result.description == "A simple description."

    def test_parse_param_tag(self) -> None:
        """Test parsing @param tag."""
        comment = """/**
         * @param {string} name - The user's name
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert len(result.params) == 1
        assert result.params[0].name == "name"
        assert result.params[0].type_annotation == "string"
        assert result.params[0].description == "The user's name"
        assert result.params[0].optional is False

    def test_parse_optional_param(self) -> None:
        """Test parsing optional @param tag."""
        comment = """/**
         * @param {number} [timeout] - Optional timeout
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert len(result.params) == 1
        assert result.params[0].name == "timeout"
        assert result.params[0].optional is True

    def test_parse_param_with_default(self) -> None:
        """Test parsing @param with default value."""
        comment = """/**
         * @param {number} [retries=3] - Number of retries
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert len(result.params) == 1
        assert result.params[0].name == "retries"
        assert result.params[0].optional is True
        assert result.params[0].default_value == "3"

    def test_parse_returns_tag(self) -> None:
        """Test parsing @returns tag."""
        comment = """/**
         * @returns {string} The formatted result
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert result.returns is not None
        assert result.returns.type_annotation == "string"
        assert result.returns.description == "The formatted result"

    def test_parse_template_tag(self) -> None:
        """Test parsing @template tag."""
        comment = """/**
         * @template T - The type parameter
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert len(result.templates) == 1
        assert result.templates[0].name == "T"
        assert result.templates[0].description == "The type parameter"

    def test_parse_template_with_constraint(self) -> None:
        """Test parsing @template with extends constraint."""
        comment = """/**
         * @template T extends object
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert len(result.templates) == 1
        assert result.templates[0].name == "T"
        assert result.templates[0].constraint == "object"

    def test_parse_deprecated_tag(self) -> None:
        """Test parsing @deprecated tag."""
        comment = """/**
         * @deprecated Use newFunction instead
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert result.is_deprecated
        assert result.deprecated == "Use newFunction instead"

    def test_parse_deprecated_tag_empty(self) -> None:
        """Test parsing @deprecated tag without message."""
        comment = """/**
         * @deprecated
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert result.is_deprecated
        assert result.deprecated == ""

    def test_parse_example_tag(self) -> None:
        """Test parsing @example tag."""
        comment = """/**
         * @example
         * const result = add(1, 2);
         * console.log(result); // 3
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert len(result.examples) == 1
        assert "add(1, 2)" in result.examples[0].code

    def test_parse_throws_tag(self) -> None:
        """Test parsing @throws tag."""
        comment = """/**
         * @throws {TypeError} If value is not a string
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert len(result.throws) == 1
        assert result.throws[0][0] == "TypeError"
        assert "not a string" in result.throws[0][1]

    def test_parse_see_tag(self) -> None:
        """Test parsing @see tag."""
        comment = """/**
         * @see {@link https://example.com}
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert len(result.see_also) == 1
        assert "https://example.com" in result.see_also[0]

    def test_parse_type_tag(self) -> None:
        """Test parsing @type tag."""
        comment = """/**
         * @type {Record<string, number>}
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert result.type_annotation == "Record<string, number>"

    def test_parse_typedef_tag(self) -> None:
        """Test parsing @typedef tag."""
        comment = """/**
         * @typedef {Object} User
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert result.typedef is not None
        assert result.typedef.name == "User"
        assert result.typedef.type_annotation == "Object"

    def test_parse_visibility_modifiers(self) -> None:
        """Test parsing visibility modifiers."""
        comment = """/**
         * @private
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert result.private is True

    def test_parse_readonly_tag(self) -> None:
        """Test parsing @readonly tag."""
        comment = """/**
         * @readonly
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert result.readonly is True

    def test_parse_since_tag(self) -> None:
        """Test parsing @since tag."""
        comment = """/**
         * @since 1.0.0
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert result.since == "1.0.0"

    def test_parse_fileoverview_tag(self) -> None:
        """Test parsing @fileoverview tag."""
        comment = """/**
         * @fileoverview Utility functions for data processing.
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert "Utility functions" in (result.fileoverview or "")

    def test_parse_module_tag(self) -> None:
        """Test parsing @module tag."""
        comment = """/**
         * @module utils/data
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert result.module == "utils/data"

    def test_parse_complete_function_doc(self) -> None:
        """Test parsing complete function documentation."""
        comment = """/**
         * Calculates the sum of two numbers.
         *
         * @param {number} a - First number
         * @param {number} b - Second number
         * @returns {number} The sum of a and b
         * @throws {TypeError} If arguments are not numbers
         * @example
         * const result = add(2, 3);
         * console.log(result); // 5
         */"""
        result = self.parser.parse(comment)

        assert result is not None
        assert "Calculates the sum" in (result.description or "")
        assert len(result.params) == 2
        assert result.params[0].name == "a"
        assert result.params[1].name == "b"
        assert result.returns is not None
        assert result.returns.type_annotation == "number"
        assert len(result.throws) == 1
        assert len(result.examples) == 1

    def test_not_jsdoc_returns_none(self) -> None:
        """Test non-JSDoc comment returns None."""
        comment = "// Regular comment"
        result = self.parser.parse(comment)

        assert result is None

    def test_block_comment_returns_none(self) -> None:
        """Test regular block comment returns None."""
        comment = "/* Regular block comment */"
        result = self.parser.parse(comment)

        assert result is None


class TestJSDocExtraction:
    """Test JSDoc extraction from source code."""

    def test_extract_jsdoc_from_source(self) -> None:
        """Test extracting all JSDoc comments from source."""
        source = """/**
 * A user interface.
 */
interface User {
  name: string;
}

/**
 * Creates a user.
 * @param {string} name - User name
 * @returns {User} The new user
 */
function createUser(name: string): User {
  return { name };
}
"""
        results = extract_jsdoc_from_source(source)

        assert len(results) == 2
        assert results[0][1].description == "A user interface."
        assert len(results[1][1].params) == 1

    def test_get_preceding_jsdoc(self) -> None:
        """Test finding JSDoc for a declaration."""
        source = """/**
 * A user interface.
 */
interface User {
  name: string;
}
"""
        comments = extract_jsdoc_from_source(source)

        # Interface is on line 4
        jsdoc = get_preceding_jsdoc(source, 4, comments)

        assert jsdoc is not None
        assert jsdoc.description == "A user interface."

    def test_get_preceding_jsdoc_not_found(self) -> None:
        """Test when no preceding JSDoc exists."""
        source = """interface User {
  name: string;
}
"""
        comments = extract_jsdoc_from_source(source)

        jsdoc = get_preceding_jsdoc(source, 1, comments)

        assert jsdoc is None
