"""Prettier integration for TypeScript formatting.

Provides formatting of generated TypeScript code using prettier.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class PrettierFormatter:
    """Formats TypeScript code using prettier."""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the formatter.

        Args:
            config: Prettier configuration options
        """
        self.config = config or {}
        self._prettier_path = self._find_prettier()
        self._npx_path = shutil.which("npx")

    def _find_prettier(self) -> str | None:
        """Find prettier executable."""
        # Try direct prettier
        prettier = shutil.which("prettier")
        if prettier:
            return prettier

        # Try npx prettier
        npx = shutil.which("npx")
        if npx:
            return None  # Will use npx

        return None

    def is_available(self) -> bool:
        """Check if prettier is available."""
        return self._prettier_path is not None or self._npx_path is not None

    def format(self, code: str) -> str:
        """Format TypeScript code using prettier.

        Args:
            code: TypeScript source code

        Returns:
            Formatted code, or original code if formatting fails
        """
        if not self.is_available():
            logger.warning("prettier not available, returning unformatted code")
            return code

        try:
            return self._run_prettier(code)
        except Exception as e:
            logger.warning(f"prettier formatting failed: {e}")
            return code

    def _run_prettier(self, code: str) -> str:
        """Run prettier on the code."""
        # Write to temp file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".ts",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(code)
            temp_path = f.name

        try:
            # Build command
            if self._prettier_path:
                cmd = [self._prettier_path]
            else:
                cmd = [self._npx_path, "prettier"]

            # Add options
            cmd.extend(["--parser", "typescript"])

            if self.config.get("tab_width"):
                cmd.extend(["--tab-width", str(self.config["tab_width"])])

            if self.config.get("use_tabs"):
                cmd.append("--use-tabs")

            if self.config.get("print_width"):
                cmd.extend(["--print-width", str(self.config["print_width"])])

            if self.config.get("single_quote"):
                cmd.append("--single-quote")

            if self.config.get("trailing_comma"):
                cmd.extend(["--trailing-comma", self.config["trailing_comma"]])

            if self.config.get("semi") is False:
                cmd.append("--no-semi")

            # Write in place
            cmd.extend(["--write", temp_path])

            # Run prettier
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30, check=False,
            )

            if result.returncode != 0:
                logger.warning(f"prettier returned {result.returncode}: {result.stderr}")
                return code

            # Read formatted code
            formatted = Path(temp_path).read_text(encoding="utf-8")
            return formatted

        finally:
            # Clean up
            Path(temp_path).unlink(missing_ok=True)

    def format_check(self, code: str) -> tuple[bool, str]:
        """Check if code is formatted correctly.

        Args:
            code: TypeScript source code

        Returns:
            Tuple of (is_formatted, diff_or_message)
        """
        if not self.is_available():
            return True, "prettier not available"

        formatted = self.format(code)
        if formatted == code:
            return True, "Code is formatted correctly"
        else:
            return False, "Code needs formatting"


class SimpleFormatter:
    """Simple TypeScript formatter without external dependencies."""

    def __init__(
        self,
        indent_size: int = 2,
        use_tabs: bool = False,
        line_length: int = 100,
    ) -> None:
        """Initialize the simple formatter."""
        self.indent_size = indent_size
        self.use_tabs = use_tabs
        self.line_length = line_length
        self._indent_char = "\t" if use_tabs else " " * indent_size

    def format(self, code: str) -> str:
        """Format TypeScript code with basic rules.

        Args:
            code: TypeScript source code

        Returns:
            Formatted code
        """
        lines = code.split("\n")
        formatted_lines = []
        indent_level = 0

        for line in lines:
            stripped = line.strip()

            # Decrease indent for closing braces
            if stripped.startswith("}") or stripped.startswith("]"):
                indent_level = max(0, indent_level - 1)

            # Add proper indentation
            if stripped:
                formatted_lines.append(f"{self._indent_char * indent_level}{stripped}")
            else:
                formatted_lines.append("")

            # Increase indent for opening braces
            if stripped.endswith("{") or stripped.endswith("["):
                indent_level += 1

            # Handle single-line blocks
            if (stripped.endswith("}") and "{" in stripped) or stripped.endswith("];"):
                pass  # Keep same level

        return "\n".join(formatted_lines)

    def normalize_whitespace(self, code: str) -> str:
        """Normalize whitespace in code."""
        lines = code.split("\n")
        normalized = []

        prev_empty = False
        for line in lines:
            is_empty = not line.strip()

            # Collapse multiple empty lines
            if is_empty and prev_empty:
                continue

            normalized.append(line.rstrip())
            prev_empty = is_empty

        # Ensure trailing newline
        result = "\n".join(normalized)
        if not result.endswith("\n"):
            result += "\n"

        return result
