"""Go code formatter using gofmt/goimports."""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class GofmtFormatter:
    """Format Go code using gofmt."""

    def __init__(self) -> None:
        """Initialize the formatter."""
        self._gofmt_path = shutil.which("gofmt")
        self._goimports_path = shutil.which("goimports")

    def format(self, code: str, use_goimports: bool = False) -> str:
        """Format Go code.

        Args:
            code: Go source code
            use_goimports: If True, use goimports for import management

        Returns:
            Formatted code
        """
        formatter_path = self._goimports_path if use_goimports else self._gofmt_path

        if not formatter_path:
            logger.warning("gofmt not found, returning unformatted code")
            return code

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".go",
                delete=False,
                encoding="utf-8",
            ) as f:
                f.write(code)
                temp_path = Path(f.name)

            try:
                result = subprocess.run(
                    [formatter_path, str(temp_path)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    return result.stdout
                else:
                    logger.warning(f"gofmt failed: {result.stderr}")
                    return code

            finally:
                temp_path.unlink(missing_ok=True)

        except subprocess.TimeoutExpired:
            logger.warning("gofmt timed out")
            return code
        except Exception as e:
            logger.warning(f"gofmt error: {e}")
            return code


class SimpleFormatter:
    """Simple Go code formatter for when gofmt is not available."""

    def format(self, code: str) -> str:
        """Apply basic formatting to Go code.

        This is a fallback when gofmt is not available.
        It provides minimal formatting but may not match
        the official Go style perfectly.
        """
        lines = code.split("\n")
        formatted_lines = []
        indent_level = 0

        for line in lines:
            stripped = line.strip()

            # Decrease indent for closing braces
            if stripped.startswith("}") or stripped.startswith(")"):
                indent_level = max(0, indent_level - 1)

            # Apply indent
            if stripped:
                formatted_lines.append("\t" * indent_level + stripped)
            else:
                formatted_lines.append("")

            # Increase indent for opening braces
            if stripped.endswith("{") or stripped.endswith("("):
                indent_level += 1

        return "\n".join(formatted_lines)


def get_formatter(prefer_goimports: bool = False) -> GofmtFormatter | SimpleFormatter:
    """Get the best available formatter.

    Args:
        prefer_goimports: If True, prefer goimports over gofmt

    Returns:
        Formatter instance
    """
    gofmt = GofmtFormatter()

    if prefer_goimports and gofmt._goimports_path:
        return gofmt
    if gofmt._gofmt_path:
        return gofmt

    logger.info("gofmt not available, using simple formatter")
    return SimpleFormatter()
