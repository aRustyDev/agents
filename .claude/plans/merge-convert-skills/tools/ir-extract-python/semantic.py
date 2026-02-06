"""Semantic enrichment for Python source code.

This module provides the SemanticEnricher class that adds type information
and name resolution to the extracted IR using jedi or pyright.

The enrichment follows a fallback chain:
1. pyright (if configured and available) - Full type analysis
2. jedi - Basic type inference
3. Graceful degradation to typing.Any

Example:
    enricher = SemanticEnricher()

    # Basic enrichment with jedi
    enriched = enricher.enrich_with_jedi(source, "module.py")

    # Full enrichment with pyright
    enriched = enricher.enrich_with_pyright(source, "module.py", project_root)
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ir_core.models import (
    IRVersion,
    TypeRef,
    TypeRefKind,
    SemanticAnnotation,
    AnnotationSource,
)


@dataclass
class TypeInfo:
    """Type information from semantic analysis.

    Attributes:
        type_string: String representation of the type
        is_inferred: Whether the type was inferred vs. explicit
        confidence: Confidence level (0.0-1.0)
        source_line: Line number in source
        source_col: Column number in source
    """

    type_string: str
    is_inferred: bool = True
    confidence: float = 0.8
    source_line: int = 0
    source_col: int = 0


@dataclass
class NameResolution:
    """Name resolution information.

    Attributes:
        name: The resolved name
        definition_file: File where the name is defined
        definition_line: Line where the name is defined
        definition_col: Column where the name is defined
        kind: Kind of definition (function, class, variable, etc.)
    """

    name: str
    definition_file: str | None = None
    definition_line: int | None = None
    definition_col: int | None = None
    kind: str = "variable"


@dataclass
class EnrichedData:
    """Container for all enrichment data.

    Attributes:
        types: Mapping from (line, col) to TypeInfo
        names: Mapping from (line, col) to NameResolution
        errors: List of error messages during enrichment
    """

    types: dict[str, TypeInfo] = field(default_factory=dict)
    names: dict[str, NameResolution] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def get_type(self, line: int, col: int) -> TypeInfo | None:
        """Get type info at a specific location."""
        key = f"{line}:{col}"
        return self.types.get(key)

    def get_name(self, line: int, col: int) -> NameResolution | None:
        """Get name resolution at a specific location."""
        key = f"{line}:{col}"
        return self.names.get(key)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by extractor."""
        result: dict[str, Any] = {}

        for key, type_info in self.types.items():
            if key not in result:
                result[key] = {}
            result[key]["return_type"] = type_info.type_string
            result[key]["is_inferred"] = type_info.is_inferred
            result[key]["confidence"] = type_info.confidence

        for key, name_info in self.names.items():
            if key not in result:
                result[key] = {}
            result[key]["definition"] = {
                "file": name_info.definition_file,
                "line": name_info.definition_line,
                "col": name_info.definition_col,
                "kind": name_info.kind,
            }

        return result


class SemanticEnricher:
    """Enrich AST with type information using pyright or jedi.

    This class provides semantic analysis capabilities for Python source code,
    adding type information and name resolution to support the IR extraction.

    The enricher follows a tiered approach:
    - Basic (jedi): Single-file analysis, quick type inference
    - Full (pyright): Cross-file analysis, full type system support

    Attributes:
        jedi_available: Whether jedi is installed
        pyright_available: Whether pyright is available

    Example:
        enricher = SemanticEnricher()

        # Check availability
        if enricher.pyright_available:
            data = enricher.enrich_with_pyright(source, path, project_root)
        else:
            data = enricher.enrich_with_jedi(source, path)
    """

    def __init__(self) -> None:
        """Initialize the semantic enricher."""
        self._jedi: Any | None = None
        self._jedi_available: bool | None = None
        self._pyright_available: bool | None = None

    @property
    def jedi_available(self) -> bool:
        """Check if jedi is available."""
        if self._jedi_available is None:
            try:
                import jedi
                self._jedi = jedi
                self._jedi_available = True
            except ImportError:
                self._jedi_available = False
        return self._jedi_available

    @property
    def pyright_available(self) -> bool:
        """Check if pyright is available."""
        if self._pyright_available is None:
            try:
                result = subprocess.run(
                    ["pyright", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                self._pyright_available = result.returncode == 0
            except (subprocess.SubprocessError, FileNotFoundError):
                self._pyright_available = False
        return self._pyright_available

    def enrich_with_jedi(
        self,
        source: str,
        path: str,
        environment: str | None = None,
    ) -> dict[str, Any]:
        """Enrich source with type information using jedi.

        Jedi provides basic type inference and name resolution for
        single-file analysis. It's fast and doesn't require project setup.

        Args:
            source: Python source code
            path: File path for context
            environment: Optional Python environment path

        Returns:
            Dictionary mapping locations to semantic information
        """
        if not self.jedi_available:
            return {}

        enriched = EnrichedData()

        try:
            # Create jedi Script
            script = self._jedi.Script(source, path=path)

            # Get all names in the file
            names = script.get_names(all_scopes=True, definitions=True, references=True)

            for name in names:
                key = f"{name.line}:{name.column}"

                # Get inferred types
                try:
                    type_inferences = name.infer()
                    if type_inferences:
                        type_strs = [inf.name for inf in type_inferences]
                        type_string = " | ".join(set(type_strs)) if type_strs else "Any"

                        enriched.types[key] = TypeInfo(
                            type_string=type_string,
                            is_inferred=True,
                            confidence=0.7 if len(type_inferences) == 1 else 0.5,
                            source_line=name.line,
                            source_col=name.column,
                        )
                except Exception:
                    pass

                # Get definition location
                try:
                    definitions = name.goto()
                    if definitions:
                        defn = definitions[0]
                        enriched.names[key] = NameResolution(
                            name=name.name,
                            definition_file=str(defn.module_path) if defn.module_path else None,
                            definition_line=defn.line,
                            definition_col=defn.column,
                            kind=defn.type,
                        )
                except Exception:
                    pass

            # Get function signatures
            for line_num, line in enumerate(source.split("\n"), start=1):
                # Find function definitions and get their signatures
                if "def " in line:
                    try:
                        # Position cursor after 'def '
                        col = line.find("def ") + 4
                        sigs = script.get_signatures(line_num, col)
                        for sig in sigs:
                            key = f"{line_num}:{col}"
                            if key not in enriched.types:
                                # Build return type string from signature
                                return_type = self._extract_jedi_return_type(sig)
                                enriched.types[key] = TypeInfo(
                                    type_string=return_type,
                                    is_inferred=True,
                                    confidence=0.6,
                                    source_line=line_num,
                                    source_col=col,
                                )
                    except Exception:
                        pass

        except Exception as e:
            enriched.errors.append(f"jedi error: {e}")

        return enriched.to_dict()

    def enrich_with_pyright(
        self,
        source: str,
        path: str,
        project_root: Path | None = None,
    ) -> dict[str, Any]:
        """Enrich source with type information using pyright.

        Pyright provides full type analysis including:
        - Cross-file type resolution
        - Type stubs (.pyi) support
        - Generic type inference
        - Protocol and structural typing

        Args:
            source: Python source code
            path: File path
            project_root: Project root for import resolution

        Returns:
            Dictionary mapping locations to semantic information
        """
        if not self.pyright_available:
            return self.enrich_with_jedi(source, path)

        enriched = EnrichedData()

        try:
            # Write source to temp file if needed
            if project_root:
                target_path = project_root / path
            else:
                # Use temp directory
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    suffix=".py",
                    delete=False
                ) as f:
                    f.write(source)
                    target_path = Path(f.name)

            # Run pyright in JSON output mode
            cmd = [
                "pyright",
                "--outputjson",
                str(target_path),
            ]

            if project_root:
                cmd.extend(["--project", str(project_root)])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(project_root) if project_root else None,
            )

            # Parse pyright output
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    self._process_pyright_output(data, enriched, path)
                except json.JSONDecodeError:
                    enriched.errors.append("Failed to parse pyright output")

            # Also try to get hover information for richer types
            # This would require pyright's language server protocol
            # For now, fall back to jedi for detailed type info
            jedi_data = self.enrich_with_jedi(source, path)

            # Merge jedi data with pyright data (pyright takes precedence)
            for key, value in jedi_data.items():
                if key not in enriched.to_dict():
                    if "return_type" in value:
                        enriched.types[key] = TypeInfo(
                            type_string=value["return_type"],
                            is_inferred=value.get("is_inferred", True),
                            confidence=value.get("confidence", 0.7),
                        )

        except subprocess.TimeoutExpired:
            enriched.errors.append("pyright timed out")
            # Fall back to jedi
            return self.enrich_with_jedi(source, path)
        except Exception as e:
            enriched.errors.append(f"pyright error: {e}")
            # Fall back to jedi
            return self.enrich_with_jedi(source, path)

        return enriched.to_dict()

    def enrich_types(self, ir: IRVersion, source: str) -> IRVersion:
        """Add inferred types to IR elements.

        This method enriches an existing IR with type information from
        semantic analysis. It updates TypeRefs that were initially set
        to Any with more specific types when available.

        Args:
            ir: IRVersion to enrich
            source: Original source code

        Returns:
            Enriched IRVersion (modified in place)
        """
        # Get enrichment data
        path = ir.module.metadata.source_file
        enriched = self.enrich_with_jedi(source, path)

        # Update function return types
        for func in ir.functions:
            if func.span:
                key = f"{func.span.start_line}:{func.span.start_col}"
                if key in enriched:
                    type_info = enriched[key]
                    if "return_type" in type_info:
                        func.return_type = self._string_to_type_ref(
                            type_info["return_type"]
                        )

                        # Add annotation about inference
                        ir.annotations.append(SemanticAnnotation(
                            id=f"annotation:{func.id}:return_type",
                            target=func.id,
                            kind="inferred_type",
                            value={"type": type_info["return_type"]},
                            confidence=type_info.get("confidence", 0.7),
                            source=AnnotationSource.INFERRED,
                        ))

        return ir

    def resolve_imports(self, ir: IRVersion) -> IRVersion:
        """Resolve import targets.

        This method attempts to resolve import statements to their
        actual definitions, categorizing them as stdlib, third-party,
        or local.

        Args:
            ir: IRVersion with imports to resolve

        Returns:
            IRVersion with resolved imports (modified in place)
        """
        for imp in ir.module.imports:
            # Determine import category
            module_path = ".".join(imp.module_path)

            if self._is_stdlib_module(module_path):
                # Add annotation for stdlib
                ir.annotations.append(SemanticAnnotation(
                    id=f"annotation:{imp.id}:category",
                    target=imp.id,
                    kind="import_category",
                    value={"category": "stdlib", "module": module_path},
                    confidence=1.0,
                    source=AnnotationSource.INFERRED,
                ))
            elif self._is_typing_module(module_path):
                # Typing imports are special
                ir.annotations.append(SemanticAnnotation(
                    id=f"annotation:{imp.id}:category",
                    target=imp.id,
                    kind="import_category",
                    value={"category": "typing", "module": module_path},
                    confidence=1.0,
                    source=AnnotationSource.INFERRED,
                ))
            else:
                # Could be local or third-party
                ir.annotations.append(SemanticAnnotation(
                    id=f"annotation:{imp.id}:category",
                    target=imp.id,
                    kind="import_category",
                    value={"category": "unknown", "module": module_path},
                    confidence=0.5,
                    source=AnnotationSource.INFERRED,
                ))

        return ir

    def _process_pyright_output(
        self,
        data: dict[str, Any],
        enriched: EnrichedData,
        path: str,
    ) -> None:
        """Process pyright JSON output into EnrichedData.

        Args:
            data: Parsed pyright JSON output
            enriched: EnrichedData to populate
            path: Source file path
        """
        # Pyright outputs diagnostics which include type errors
        # We can extract type information from these
        diagnostics = data.get("generalDiagnostics", [])

        for diag in diagnostics:
            if diag.get("file", "").endswith(path):
                line = diag.get("range", {}).get("start", {}).get("line", 0) + 1
                col = diag.get("range", {}).get("start", {}).get("character", 0)
                key = f"{line}:{col}"

                message = diag.get("message", "")

                # Try to extract type from error message
                # e.g., 'Type of "x" is "int"' or 'Expression of type "str"'
                if 'Type of' in message or 'type "' in message:
                    # Extract type from quotes
                    import re
                    type_match = re.search(r'type "([^"]+)"', message.lower())
                    if type_match:
                        type_string = type_match.group(1)
                        enriched.types[key] = TypeInfo(
                            type_string=type_string,
                            is_inferred=True,
                            confidence=0.9,  # High confidence from pyright
                            source_line=line,
                            source_col=col,
                        )

    def _extract_jedi_return_type(self, signature: Any) -> str:
        """Extract return type from a jedi signature.

        Args:
            signature: jedi Signature object

        Returns:
            Return type as string
        """
        # Jedi signature has annotation attribute
        if hasattr(signature, "annotation") and signature.annotation:
            return signature.annotation

        # Try to get from bracket_start
        try:
            if hasattr(signature, "return_annotation"):
                return signature.return_annotation or "Any"
        except Exception:
            pass

        return "Any"

    def _string_to_type_ref(self, type_str: str) -> TypeRef:
        """Convert a type string to a TypeRef.

        Args:
            type_str: Type as a string

        Returns:
            TypeRef representation
        """
        type_str = type_str.strip()

        if not type_str or type_str == "None":
            return TypeRef(kind=TypeRefKind.NAMED, type_id="None")

        # Union types
        if "|" in type_str:
            members = [
                self._string_to_type_ref(m.strip())
                for m in type_str.split("|")
            ]
            return TypeRef(kind=TypeRefKind.UNION, members=members)

        # Generic types
        if "[" in type_str:
            bracket_pos = type_str.find("[")
            base = type_str[:bracket_pos]
            return TypeRef(kind=TypeRefKind.NAMED, type_id=base)

        return TypeRef(kind=TypeRefKind.NAMED, type_id=type_str)

    def _is_stdlib_module(self, module: str) -> bool:
        """Check if a module is part of the standard library."""
        stdlib_modules = {
            "abc", "aifc", "argparse", "array", "ast", "asynchat", "asyncio",
            "asyncore", "atexit", "audioop", "base64", "bdb", "binascii",
            "binhex", "bisect", "builtins", "bz2", "calendar", "cgi",
            "cgitb", "chunk", "cmath", "cmd", "code", "codecs", "codeop",
            "collections", "colorsys", "compileall", "concurrent",
            "configparser", "contextlib", "contextvars", "copy", "copyreg",
            "cProfile", "crypt", "csv", "ctypes", "curses", "dataclasses",
            "datetime", "dbm", "decimal", "difflib", "dis", "distutils",
            "doctest", "email", "encodings", "enum", "errno", "faulthandler",
            "fcntl", "filecmp", "fileinput", "fnmatch", "formatter",
            "fractions", "ftplib", "functools", "gc", "getopt", "getpass",
            "gettext", "glob", "graphlib", "grp", "gzip", "hashlib",
            "heapq", "hmac", "html", "http", "idlelib", "imaplib",
            "imghdr", "imp", "importlib", "inspect", "io", "ipaddress",
            "itertools", "json", "keyword", "lib2to3", "linecache",
            "locale", "logging", "lzma", "mailbox", "mailcap", "marshal",
            "math", "mimetypes", "mmap", "modulefinder", "multiprocessing",
            "netrc", "nis", "nntplib", "numbers", "operator", "optparse",
            "os", "ossaudiodev", "parser", "pathlib", "pdb", "pickle",
            "pickletools", "pipes", "pkgutil", "platform", "plistlib",
            "poplib", "posix", "posixpath", "pprint", "profile", "pstats",
            "pty", "pwd", "py_compile", "pyclbr", "pydoc", "queue",
            "quopri", "random", "re", "readline", "reprlib", "resource",
            "rlcompleter", "runpy", "sched", "secrets", "select",
            "selectors", "shelve", "shlex", "shutil", "signal", "site",
            "smtpd", "smtplib", "sndhdr", "socket", "socketserver",
            "spwd", "sqlite3", "ssl", "stat", "statistics", "string",
            "stringprep", "struct", "subprocess", "sunau", "symtable",
            "sys", "sysconfig", "syslog", "tabnanny", "tarfile", "telnetlib",
            "tempfile", "termios", "test", "textwrap", "threading", "time",
            "timeit", "tkinter", "token", "tokenize", "tomllib", "trace",
            "traceback", "tracemalloc", "tty", "turtle", "turtledemo",
            "types", "typing", "typing_extensions", "unicodedata",
            "unittest", "urllib", "uu", "uuid", "venv", "warnings",
            "wave", "weakref", "webbrowser", "winreg", "winsound",
            "wsgiref", "xdrlib", "xml", "xmlrpc", "zipapp", "zipfile",
            "zipimport", "zlib", "zoneinfo",
        }

        # Check base module
        base = module.split(".")[0]
        return base in stdlib_modules

    def _is_typing_module(self, module: str) -> bool:
        """Check if a module is typing-related."""
        typing_modules = {
            "typing", "typing_extensions", "types",
        }
        base = module.split(".")[0]
        return base in typing_modules
