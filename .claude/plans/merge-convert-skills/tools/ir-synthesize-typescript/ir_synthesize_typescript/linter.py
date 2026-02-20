"""ESLint integration for TypeScript validation.

Provides linting of generated TypeScript code using ESLint.
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar

logger = logging.getLogger(__name__)


class LintSeverity(str, Enum):
    """Lint issue severity."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class LintIssue:
    """A linting issue found in code."""

    rule: str
    message: str
    severity: LintSeverity
    line: int
    column: int
    end_line: int | None = None
    end_column: int | None = None
    fix: str | None = None


@dataclass
class LintResult:
    """Result of linting code."""

    success: bool
    issues: list[LintIssue] = field(default_factory=list)
    error_count: int = 0
    warning_count: int = 0
    fixable_count: int = 0
    output: str = ""


class ESLintConfig:
    """ESLint configuration for TypeScript."""

    # Recommended rules for generated TypeScript
    DEFAULT_RULES: ClassVar[dict[str, Any]] = {
        # TypeScript-specific rules
        "@typescript-eslint/explicit-function-return-type": "warn",
        "@typescript-eslint/no-explicit-any": "warn",
        "@typescript-eslint/no-unused-vars": "error",
        "@typescript-eslint/no-non-null-assertion": "warn",
        "@typescript-eslint/prefer-readonly": "warn",
        "@typescript-eslint/prefer-nullish-coalescing": "warn",
        "@typescript-eslint/prefer-optional-chain": "warn",
        # General rules
        "no-console": "warn",
        "no-debugger": "error",
        "eqeqeq": ["error", "always"],
        "prefer-const": "error",
        "no-var": "error",
    }

    # Strict rules for generated code
    STRICT_RULES: ClassVar[dict[str, Any]] = {
        **DEFAULT_RULES,
        "@typescript-eslint/explicit-function-return-type": "error",
        "@typescript-eslint/no-explicit-any": "error",
        "@typescript-eslint/strict-boolean-expressions": "error",
    }

    # Relaxed rules for less strict checking
    RELAXED_RULES: ClassVar[dict[str, Any]] = {
        "@typescript-eslint/no-unused-vars": "warn",
        "@typescript-eslint/no-explicit-any": "off",
        "no-console": "off",
    }

    @classmethod
    def create_config(
        cls,
        rules: dict[str, Any] | None = None,
        parser_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create an ESLint configuration object.

        Args:
            rules: Custom rules to apply
            parser_options: Parser options for TypeScript

        Returns:
            ESLint configuration dictionary
        """
        config = {
            "parser": "@typescript-eslint/parser",
            "parserOptions": {
                "ecmaVersion": 2022,
                "sourceType": "module",
                **(parser_options or {}),
            },
            "plugins": ["@typescript-eslint"],
            "extends": [
                "eslint:recommended",
                "plugin:@typescript-eslint/recommended",
            ],
            "rules": rules or cls.DEFAULT_RULES,
            "env": {
                "browser": True,
                "node": True,
                "es2022": True,
            },
        }

        return config


class ESLinter:
    """Lints TypeScript code using ESLint."""

    def __init__(
        self,
        rules: dict[str, Any] | None = None,
        strict: bool = False,
    ) -> None:
        """Initialize the linter.

        Args:
            rules: Custom ESLint rules
            strict: Use strict rule set
        """
        if rules:
            self.rules = rules
        elif strict:
            self.rules = ESLintConfig.STRICT_RULES
        else:
            self.rules = ESLintConfig.DEFAULT_RULES

        self._eslint_path = self._find_eslint()
        self._npx_path = shutil.which("npx")

    def _find_eslint(self) -> str | None:
        """Find ESLint executable."""
        # Try direct eslint
        eslint = shutil.which("eslint")
        if eslint:
            return eslint

        return None

    def is_available(self) -> bool:
        """Check if ESLint is available."""
        return self._eslint_path is not None or self._npx_path is not None

    def lint(self, code: str, fix: bool = False) -> LintResult:
        """Lint TypeScript code.

        Args:
            code: TypeScript source code
            fix: Whether to apply automatic fixes

        Returns:
            LintResult with issues found
        """
        if not self.is_available():
            logger.warning("ESLint not available")
            return LintResult(
                success=True,
                output="ESLint not available, skipping lint",
            )

        try:
            return self._run_eslint(code, fix)
        except Exception as e:
            logger.warning(f"ESLint failed: {e}")
            return LintResult(
                success=False,
                output=str(e),
            )

    def _run_eslint(self, code: str, fix: bool = False) -> LintResult:
        """Run ESLint on the code."""
        # Create temp directory with config and code
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Write code file
            code_file = temp_path / "test.ts"
            code_file.write_text(code, encoding="utf-8")

            # Write ESLint config
            config = ESLintConfig.create_config(rules=self.rules)
            config_file = temp_path / ".eslintrc.json"
            config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")

            # Build command
            cmd = (
                [self._eslint_path]
                if self._eslint_path
                else [str(self._npx_path), "eslint"]
            )

            cmd.extend(
                [
                    "--format",
                    "json",
                    "--no-eslintrc",
                    "--config",
                    str(config_file),
                ]
            )

            if fix:
                cmd.append("--fix")

            cmd.append(str(code_file))

            # Run ESLint
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=temp_dir,
                check=False,
            )

            # Parse JSON output
            return self._parse_eslint_output(result.stdout, result.stderr)

    def _parse_eslint_output(self, stdout: str, stderr: str) -> LintResult:
        """Parse ESLint JSON output."""
        if not stdout.strip():
            return LintResult(
                success=True,
                output=stderr or "No output from ESLint",
            )

        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            return LintResult(
                success=False,
                output=f"Failed to parse ESLint output: {stdout}",
            )

        if not data:
            return LintResult(success=True)

        # ESLint returns array of file results
        file_result = data[0] if data else {}
        messages = file_result.get("messages", [])

        issues = []
        error_count = 0
        warning_count = 0
        fixable_count = 0

        for msg in messages:
            severity = (
                LintSeverity.ERROR if msg.get("severity") == 2 else LintSeverity.WARNING
            )

            issue = LintIssue(
                rule=msg.get("ruleId", "unknown"),
                message=msg.get("message", ""),
                severity=severity,
                line=msg.get("line", 0),
                column=msg.get("column", 0),
                end_line=msg.get("endLine"),
                end_column=msg.get("endColumn"),
                fix=msg.get("fix", {}).get("text") if msg.get("fix") else None,
            )
            issues.append(issue)

            if severity == LintSeverity.ERROR:
                error_count += 1
            else:
                warning_count += 1

            if msg.get("fix"):
                fixable_count += 1

        return LintResult(
            success=error_count == 0,
            issues=issues,
            error_count=error_count,
            warning_count=warning_count,
            fixable_count=fixable_count,
        )

    def fix(self, code: str) -> tuple[str, LintResult]:
        """Lint and fix TypeScript code.

        Args:
            code: TypeScript source code

        Returns:
            Tuple of (fixed_code, lint_result)
        """
        if not self.is_available():
            return code, LintResult(
                success=True,
                output="ESLint not available, returning original code",
            )

        # Create temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Write code file
            code_file = temp_path / "test.ts"
            code_file.write_text(code, encoding="utf-8")

            # Write ESLint config
            config = ESLintConfig.create_config(rules=self.rules)
            config_file = temp_path / ".eslintrc.json"
            config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")

            # Build command with --fix
            cmd = (
                [self._eslint_path]
                if self._eslint_path
                else [str(self._npx_path), "eslint"]
            )

            cmd.extend(
                [
                    "--format",
                    "json",
                    "--no-eslintrc",
                    "--config",
                    str(config_file),
                    "--fix",
                    str(code_file),
                ]
            )

            # Run ESLint with fix
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=temp_dir,
                check=False,
            )

            # Read fixed code
            fixed_code = code_file.read_text(encoding="utf-8")

            # Parse result
            lint_result = self._parse_eslint_output(result.stdout, result.stderr)

            return fixed_code, lint_result


def lint_typescript(
    code: str,
    strict: bool = False,
    fix: bool = False,
) -> LintResult | tuple[str, LintResult]:
    """Convenience function to lint TypeScript code.

    Args:
        code: TypeScript source code
        strict: Use strict rule set
        fix: Apply automatic fixes

    Returns:
        LintResult, or tuple of (fixed_code, LintResult) if fix=True
    """
    linter = ESLinter(strict=strict)

    if fix:
        return linter.fix(code)
    else:
        return linter.lint(code)
