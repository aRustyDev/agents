"""Rust code formatter.

This module provides formatting for generated Rust code,
with support for rustfmt integration.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class FormatConfig:
    """Configuration for Rust formatting.

    Attributes:
        max_width: Maximum line width
        tab_spaces: Spaces per indentation level
        edition: Rust edition (2018, 2021)
        use_rustfmt: Whether to use rustfmt if available
        rustfmt_path: Path to rustfmt binary
    """

    max_width: int = 100
    tab_spaces: int = 4
    edition: str = "2021"
    use_rustfmt: bool = True
    rustfmt_path: str | None = None


class RustFormatter:
    """Format Rust code.

    Supports both built-in simple formatting and rustfmt integration.

    Example:
        formatter = RustFormatter()
        formatted = formatter.format(code)
    """

    def __init__(self, config: FormatConfig | None = None) -> None:
        """Initialize formatter.

        Args:
            config: Formatting configuration
        """
        self.config = config or FormatConfig()
        self._rustfmt_available: bool | None = None

    def format(self, code: str) -> str:
        """Format Rust code.

        Args:
            code: Rust source code

        Returns:
            Formatted code
        """
        if self.config.use_rustfmt and self._check_rustfmt():
            try:
                return self._format_with_rustfmt(code)
            except Exception as e:
                logger.warning("rustfmt failed, using built-in formatter: %s", e)

        return self._format_builtin(code)

    def _check_rustfmt(self) -> bool:
        """Check if rustfmt is available."""
        if self._rustfmt_available is not None:
            return self._rustfmt_available

        rustfmt = self.config.rustfmt_path or "rustfmt"

        # Check if rustfmt exists
        if self.config.rustfmt_path:
            self._rustfmt_available = Path(self.config.rustfmt_path).exists()
        else:
            self._rustfmt_available = shutil.which("rustfmt") is not None

        return self._rustfmt_available

    def _format_with_rustfmt(self, code: str) -> str:
        """Format code using rustfmt.

        Args:
            code: Rust source code

        Returns:
            Formatted code
        """
        rustfmt = self.config.rustfmt_path or "rustfmt"

        # Write to temp file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".rs",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(code)
            temp_path = Path(f.name)

        try:
            # Run rustfmt
            cmd = [
                rustfmt,
                "--edition", self.config.edition,
                "--config", f"max_width={self.config.max_width}",
                "--config", f"tab_spaces={self.config.tab_spaces}",
                str(temp_path),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30, check=False,
            )

            if result.returncode != 0:
                logger.warning("rustfmt returned %d: %s", result.returncode, result.stderr)
                return code

            # Read formatted output
            return temp_path.read_text(encoding="utf-8")

        finally:
            temp_path.unlink(missing_ok=True)

    def _format_builtin(self, code: str) -> str:
        """Format code using built-in formatter.

        This is a simple formatter that handles basic indentation
        and line length. For best results, use rustfmt.

        Args:
            code: Rust source code

        Returns:
            Formatted code
        """
        lines: list[str] = []
        indent_level = 0
        indent_str = " " * self.config.tab_spaces

        for line in code.split("\n"):
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                lines.append("")
                continue

            # Decrease indent for closing braces
            if stripped.startswith("}") or stripped.startswith(")"):
                indent_level = max(0, indent_level - 1)

            # Apply indentation
            if stripped:
                lines.append(indent_str * indent_level + stripped)

            # Increase indent for opening braces
            if stripped.endswith("{") or stripped.endswith("("):
                indent_level += 1

            # Handle single-line closures and blocks
            open_count = stripped.count("{") + stripped.count("(")
            close_count = stripped.count("}") + stripped.count(")")
            if close_count > open_count:
                indent_level = max(0, indent_level - (close_count - open_count))

        return "\n".join(lines)

    def format_line_length(self, code: str) -> str:
        """Break long lines.

        Args:
            code: Rust source code

        Returns:
            Code with long lines broken
        """
        lines: list[str] = []

        for line in code.split("\n"):
            if len(line) <= self.config.max_width:
                lines.append(line)
                continue

            # Try to break at sensible points
            broken = self._break_line(line)
            lines.extend(broken)

        return "\n".join(lines)

    def _break_line(self, line: str) -> list[str]:
        """Break a long line at sensible points.

        Args:
            line: Long line to break

        Returns:
            List of shorter lines
        """
        max_width = self.config.max_width
        indent_str = " " * self.config.tab_spaces

        # Find leading whitespace
        leading = len(line) - len(line.lstrip())
        leading_ws = line[:leading]
        content = line[leading:]

        if len(line) <= max_width:
            return [line]

        result: list[str] = []
        current = leading_ws

        # Break points (in order of preference)
        break_chars = [", ", " + ", " - ", " && ", " || ", " | ", "->"]

        i = 0
        while i < len(content):
            # Check if we need to break
            if len(current + content[i:]) <= max_width:
                result.append(current + content[i:])
                break

            # Find best break point
            best_break = -1
            for bc in break_chars:
                pos = content.rfind(bc, i, i + max_width - len(current))
                if pos > best_break:
                    best_break = pos + len(bc)

            if best_break > i:
                result.append(current + content[i:best_break].rstrip())
                current = leading_ws + indent_str
                i = best_break
            else:
                # Force break at max width
                cut = max_width - len(current)
                result.append(current + content[i:i + cut])
                current = leading_ws + indent_str
                i += cut

        if not result:
            result.append(line)

        return result


def format_rust_code(code: str, config: FormatConfig | None = None) -> str:
    """Convenience function to format Rust code.

    Args:
        code: Rust source code
        config: Optional formatting configuration

    Returns:
        Formatted code
    """
    formatter = RustFormatter(config)
    return formatter.format(code)
