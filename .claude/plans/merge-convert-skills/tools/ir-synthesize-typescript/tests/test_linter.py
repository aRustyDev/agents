"""Tests for ESLint integration."""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path for direct import
sys.path.insert(0, str(Path(__file__).parent.parent / "ir_synthesize_typescript"))

import pytest
from linter import (
    ESLintConfig,
    ESLinter,
    LintResult,
    LintSeverity,
    lint_typescript,
)


class TestESLintConfig:
    """Test ESLint configuration."""

    def test_default_rules(self) -> None:
        """Test default rules are set."""
        assert "@typescript-eslint/no-unused-vars" in ESLintConfig.DEFAULT_RULES
        assert "@typescript-eslint/no-explicit-any" in ESLintConfig.DEFAULT_RULES

    def test_strict_rules_include_defaults(self) -> None:
        """Test strict rules extend defaults."""
        for rule in ["no-var", "prefer-const"]:
            assert rule in ESLintConfig.STRICT_RULES

    def test_create_config(self) -> None:
        """Test creating ESLint config."""
        config = ESLintConfig.create_config()

        assert config["parser"] == "@typescript-eslint/parser"
        assert "@typescript-eslint" in config["plugins"]
        assert config["parserOptions"]["ecmaVersion"] == 2022

    def test_create_config_with_custom_rules(self) -> None:
        """Test creating config with custom rules."""
        custom_rules = {"no-console": "off"}
        config = ESLintConfig.create_config(rules=custom_rules)

        assert config["rules"]["no-console"] == "off"

    def test_create_config_with_parser_options(self) -> None:
        """Test creating config with parser options."""
        options = {"project": "./tsconfig.json"}
        config = ESLintConfig.create_config(parser_options=options)

        assert config["parserOptions"]["project"] == "./tsconfig.json"


class TestLintResult:
    """Test LintResult dataclass."""

    def test_empty_result_is_success(self) -> None:
        """Test empty result indicates success."""
        result = LintResult(success=True)

        assert result.success
        assert result.error_count == 0
        assert result.warning_count == 0
        assert len(result.issues) == 0

    def test_result_with_errors(self) -> None:
        """Test result with errors."""
        from linter import LintIssue

        issue = LintIssue(
            rule="no-unused-vars",
            message="'x' is declared but never used",
            severity=LintSeverity.ERROR,
            line=1,
            column=5,
        )

        result = LintResult(
            success=False,
            issues=[issue],
            error_count=1,
            warning_count=0,
        )

        assert not result.success
        assert result.error_count == 1
        assert len(result.issues) == 1
        assert result.issues[0].rule == "no-unused-vars"


class TestESLinter:
    """Test ESLinter functionality."""

    def test_linter_initialization(self) -> None:
        """Test linter can be initialized."""
        linter = ESLinter()
        assert linter.rules == ESLintConfig.DEFAULT_RULES

    def test_linter_with_strict_mode(self) -> None:
        """Test linter with strict mode."""
        linter = ESLinter(strict=True)
        assert linter.rules == ESLintConfig.STRICT_RULES

    def test_linter_with_custom_rules(self) -> None:
        """Test linter with custom rules."""
        custom_rules = {"no-console": "error"}
        linter = ESLinter(rules=custom_rules)
        assert linter.rules == custom_rules


class TestESLinterWithoutESLint:
    """Test ESLinter behavior when ESLint is not available."""

    def test_lint_without_eslint(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test linting returns success when ESLint not available."""
        # Simulate ESLint not being available
        monkeypatch.setattr("shutil.which", lambda _x: None)

        linter = ESLinter()
        result = linter.lint("const x: number = 1;")

        assert result.success
        assert "not available" in result.output

    def test_fix_without_eslint(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test fixing returns original code when ESLint not available."""
        monkeypatch.setattr("shutil.which", lambda _x: None)

        linter = ESLinter()
        original_code = "const x: number = 1;"
        fixed_code, result = linter.fix(original_code)

        assert fixed_code == original_code
        assert result.success


class TestLintTypescriptFunction:
    """Test the convenience lint_typescript function."""

    def test_lint_typescript_basic(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test basic linting via convenience function."""
        monkeypatch.setattr("shutil.which", lambda _x: None)

        result = lint_typescript("const x: number = 1;")

        assert isinstance(result, LintResult)
        assert result.success

    def test_lint_typescript_with_fix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test linting with fix via convenience function."""
        monkeypatch.setattr("shutil.which", lambda _x: None)

        result = lint_typescript("const x: number = 1;", fix=True)

        assert isinstance(result, tuple)
        code, lint_result = result
        assert isinstance(code, str)
        assert isinstance(lint_result, LintResult)


class TestLintSeverity:
    """Test LintSeverity enum."""

    def test_severity_values(self) -> None:
        """Test severity enum values."""
        assert LintSeverity.ERROR.value == "error"
        assert LintSeverity.WARNING.value == "warning"
        assert LintSeverity.INFO.value == "info"

    def test_severity_comparison(self) -> None:
        """Test severity can be compared."""
        assert LintSeverity.ERROR == "error"
        assert LintSeverity.WARNING == "warning"
