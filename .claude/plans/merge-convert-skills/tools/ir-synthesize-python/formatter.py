"""Python code formatting utilities.

This module provides the PythonFormatter class for formatting generated Python code
using black/ruff and adding docstrings from IR metadata.

Example:
    formatter = PythonFormatter()
    formatted_code = formatter.format(code)
    code_with_docs = formatter.add_docstrings(code, ir)
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ir_core.models import IRVersion


@dataclass
class FormatResult:
    """Result of a formatting operation.

    Attributes:
        code: Formatted code
        success: Whether formatting succeeded
        error: Error message if failed
        tool: Tool used for formatting
    """

    code: str
    success: bool
    error: str | None = None
    tool: str | None = None


class PythonFormatter:
    """Format generated Python code.

    This class handles code formatting using external tools (black, ruff) and
    provides utilities for adding docstrings and other formatting adjustments.

    Attributes:
        line_length: Maximum line length (default: 88)
        use_black: Whether to use black for formatting (default: True)
        use_ruff: Whether to use ruff for formatting (default: False)
        target_version: Python version target (default: "py311")
    """

    def __init__(
        self,
        line_length: int = 88,
        use_black: bool = True,
        use_ruff: bool = False,
        target_version: str = "py311",
    ) -> None:
        """Initialize the formatter.

        Args:
            line_length: Maximum line length
            use_black: Whether to use black
            use_ruff: Whether to use ruff
            target_version: Python version target
        """
        self.line_length = line_length
        self.use_black = use_black
        self.use_ruff = use_ruff
        self.target_version = target_version

        # Check tool availability
        self._black_available = self._check_tool("black")
        self._ruff_available = self._check_tool("ruff")

    def format(self, code: str) -> str:
        """Format Python code.

        Attempts to format using the configured tools (black/ruff).
        Falls back to basic formatting if external tools are unavailable.

        Args:
            code: Python code to format

        Returns:
            Formatted code
        """
        result = self.format_with_result(code)
        return result.code

    def format_with_result(self, code: str) -> FormatResult:
        """Format Python code and return detailed result.

        Args:
            code: Python code to format

        Returns:
            FormatResult with formatting details
        """
        # Try black first
        if self.use_black and self._black_available:
            result = self._format_with_black(code)
            if result.success:
                return result

        # Try ruff
        if self.use_ruff and self._ruff_available:
            result = self._format_with_ruff(code)
            if result.success:
                return result

        # Fall back to basic formatting
        return self._basic_format(code)

    def add_docstrings(self, code: str, ir: IRVersion) -> str:
        """Add docstrings from IR metadata to code.

        This method parses the code and inserts docstrings from the IR where
        appropriate. It's useful when the initial synthesis didn't include
        docstrings.

        Args:
            code: Python code
            ir: IR containing documentation metadata

        Returns:
            Code with docstrings added
        """
        # Build a map of entity names to their docstrings
        docstring_map: dict[str, str] = {}

        # Module docstring
        if ir.module.metadata.documentation:
            docstring_map["__module__"] = ir.module.metadata.documentation

        # Function docstrings
        for func in ir.functions:
            if func.doc_comment:
                docstring_map[func.name] = func.doc_comment

        # Class docstrings (from annotations)
        for type_def in ir.types:
            for annotation in type_def.annotations:
                if annotation.kind == "docstring":
                    doc = annotation.value.get("text", "")
                    if doc:
                        docstring_map[type_def.name] = doc

        # Simple insertion - could be made more robust with AST parsing
        lines = code.split("\n")
        result_lines: list[str] = []
        i = 0

        while i < len(lines):
            line = lines[i]
            result_lines.append(line)

            # Check for function definitions
            stripped = line.strip()
            if stripped.startswith("def ") or stripped.startswith("async def "):
                # Extract function name
                func_name = self._extract_def_name(stripped)
                if func_name and func_name in docstring_map:
                    # Check if next line already has docstring
                    if i + 1 < len(lines) and not self._is_docstring(lines[i + 1]):
                        indent = self._get_indent(line) + "    "
                        docstring = self._format_docstring(
                            docstring_map[func_name], indent
                        )
                        result_lines.append(docstring)

            # Check for class definitions
            elif stripped.startswith("class "):
                class_name = self._extract_class_name(stripped)
                if class_name and class_name in docstring_map:
                    if i + 1 < len(lines) and not self._is_docstring(lines[i + 1]):
                        indent = self._get_indent(line) + "    "
                        docstring = self._format_docstring(
                            docstring_map[class_name], indent
                        )
                        result_lines.append(docstring)

            i += 1

        return "\n".join(result_lines)

    def fix_imports(self, code: str) -> str:
        """Sort and organize imports in the code.

        Uses isort (via ruff or standalone) to organize imports.

        Args:
            code: Python code

        Returns:
            Code with organized imports
        """
        if self._ruff_available:
            return self._organize_imports_ruff(code)

        # Try isort directly
        if self._check_tool("isort"):
            return self._organize_imports_isort(code)

        return code

    def _format_with_black(self, code: str) -> FormatResult:
        """Format code using black.

        Args:
            code: Python code

        Returns:
            FormatResult
        """
        try:
            # Try using black as a library first
            import black

            mode = black.Mode(
                line_length=self.line_length,
                target_versions={black.TargetVersion[self.target_version.upper()]},
            )
            formatted = black.format_str(code, mode=mode)
            return FormatResult(
                code=formatted,
                success=True,
                tool="black",
            )
        except ImportError:
            pass
        except Exception as e:
            return FormatResult(
                code=code,
                success=False,
                error=f"black library error: {e}",
                tool="black",
            )

        # Fall back to subprocess
        return self._run_formatter_subprocess(
            code,
            ["black", "-", f"--line-length={self.line_length}"],
            "black",
        )

    def _format_with_ruff(self, code: str) -> FormatResult:
        """Format code using ruff.

        Args:
            code: Python code

        Returns:
            FormatResult
        """
        return self._run_formatter_subprocess(
            code,
            ["ruff", "format", "-", f"--line-length={self.line_length}"],
            "ruff",
        )

    def _run_formatter_subprocess(
        self, code: str, cmd: list[str], tool: str
    ) -> FormatResult:
        """Run a formatter as a subprocess.

        Args:
            code: Code to format
            cmd: Command and arguments
            tool: Tool name for reporting

        Returns:
            FormatResult
        """
        try:
            result = subprocess.run(
                cmd,
                input=code,
                capture_output=True,
                text=True,
                timeout=30, check=False,
            )
            if result.returncode == 0:
                return FormatResult(
                    code=result.stdout,
                    success=True,
                    tool=tool,
                )
            else:
                return FormatResult(
                    code=code,
                    success=False,
                    error=result.stderr,
                    tool=tool,
                )
        except subprocess.TimeoutExpired:
            return FormatResult(
                code=code,
                success=False,
                error="Formatting timed out",
                tool=tool,
            )
        except FileNotFoundError:
            return FormatResult(
                code=code,
                success=False,
                error=f"{tool} not found",
                tool=tool,
            )
        except Exception as e:
            return FormatResult(
                code=code,
                success=False,
                error=str(e),
                tool=tool,
            )

    def _basic_format(self, code: str) -> FormatResult:
        """Apply basic formatting without external tools.

        Args:
            code: Python code

        Returns:
            FormatResult
        """
        # Basic formatting:
        # - Ensure consistent line endings
        # - Remove trailing whitespace
        # - Ensure file ends with newline
        # - Normalize blank lines

        lines = code.split("\n")
        result_lines: list[str] = []
        prev_blank = False

        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()

            # Normalize multiple blank lines
            is_blank = not line.strip()
            if is_blank:
                if not prev_blank:
                    result_lines.append(line)
                prev_blank = True
            else:
                result_lines.append(line)
                prev_blank = False

        # Ensure ends with newline
        code = "\n".join(result_lines)
        if code and not code.endswith("\n"):
            code += "\n"

        return FormatResult(
            code=code,
            success=True,
            tool="basic",
        )

    def _organize_imports_ruff(self, code: str) -> str:
        """Organize imports using ruff.

        Args:
            code: Python code

        Returns:
            Code with organized imports
        """
        try:
            result = subprocess.run(
                ["ruff", "check", "--fix", "--select=I", "-"],
                input=code,
                capture_output=True,
                text=True,
                timeout=30, check=False,
            )
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass
        return code

    def _organize_imports_isort(self, code: str) -> str:
        """Organize imports using isort.

        Args:
            code: Python code

        Returns:
            Code with organized imports
        """
        try:
            result = subprocess.run(
                ["isort", "-"],
                input=code,
                capture_output=True,
                text=True,
                timeout=30, check=False,
            )
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass
        return code

    def _check_tool(self, tool: str) -> bool:
        """Check if an external tool is available.

        Args:
            tool: Tool name

        Returns:
            True if available
        """
        try:
            result = subprocess.run(
                [tool, "--version"],
                capture_output=True,
                timeout=5, check=False,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _extract_def_name(self, line: str) -> str | None:
        """Extract function name from a def line.

        Args:
            line: Line starting with 'def ' or 'async def '

        Returns:
            Function name or None
        """
        if line.startswith("async def "):
            rest = line[10:]
        elif line.startswith("def "):
            rest = line[4:]
        else:
            return None

        # Find the opening parenthesis
        paren_idx = rest.find("(")
        if paren_idx > 0:
            return rest[:paren_idx].strip()
        return None

    def _extract_class_name(self, line: str) -> str | None:
        """Extract class name from a class line.

        Args:
            line: Line starting with 'class '

        Returns:
            Class name or None
        """
        if not line.startswith("class "):
            return None

        rest = line[6:]

        # Find the colon or parenthesis
        for char in ("(", ":"):
            idx = rest.find(char)
            if idx > 0:
                return rest[:idx].strip()

        return rest.strip().rstrip(":")

    def _is_docstring(self, line: str) -> bool:
        """Check if a line is or starts a docstring.

        Args:
            line: Code line

        Returns:
            True if docstring
        """
        stripped = line.strip()
        return stripped.startswith('"""') or stripped.startswith("'''")

    def _get_indent(self, line: str) -> str:
        """Get the indentation of a line.

        Args:
            line: Code line

        Returns:
            Indentation string
        """
        return line[: len(line) - len(line.lstrip())]

    def _format_docstring(self, doc: str, indent: str) -> str:
        """Format a docstring with proper indentation.

        Args:
            doc: Docstring content
            indent: Indentation to use

        Returns:
            Formatted docstring
        """
        if "\n" in doc:
            lines = doc.split("\n")
            formatted_lines = [f'{indent}"""']
            for line in lines:
                formatted_lines.append(f"{indent}{line}")
            formatted_lines.append(f'{indent}"""')
            return "\n".join(formatted_lines)
        else:
            return f'{indent}"""{doc}"""'


class FormatterConfig:
    """Configuration for the Python formatter.

    Attributes:
        line_length: Maximum line length
        indent_size: Number of spaces per indentation level
        use_tabs: Whether to use tabs instead of spaces
        quote_style: Preferred quote style ('single' or 'double')
        trailing_comma: Whether to add trailing commas
        target_version: Python version target
    """

    def __init__(
        self,
        line_length: int = 88,
        indent_size: int = 4,
        use_tabs: bool = False,
        quote_style: str = "double",
        trailing_comma: bool = True,
        target_version: str = "py311",
    ) -> None:
        """Initialize formatter configuration."""
        self.line_length = line_length
        self.indent_size = indent_size
        self.use_tabs = use_tabs
        self.quote_style = quote_style
        self.trailing_comma = trailing_comma
        self.target_version = target_version

    @classmethod
    def from_pyproject(cls, path: Path) -> FormatterConfig:
        """Load configuration from pyproject.toml.

        Args:
            path: Path to pyproject.toml

        Returns:
            FormatterConfig
        """
        config = cls()

        try:
            import tomllib

            with open(path, "rb") as f:
                data = tomllib.load(f)

            # Try black settings
            black_config = data.get("tool", {}).get("black", {})
            if "line-length" in black_config:
                config.line_length = black_config["line-length"]
            if "target-version" in black_config:
                versions = black_config["target-version"]
                if versions:
                    config.target_version = versions[0]

            # Try ruff settings
            ruff_config = data.get("tool", {}).get("ruff", {})
            if "line-length" in ruff_config:
                config.line_length = ruff_config["line-length"]
            if "target-version" in ruff_config:
                config.target_version = ruff_config["target-version"]

        except Exception:
            pass

        return config
