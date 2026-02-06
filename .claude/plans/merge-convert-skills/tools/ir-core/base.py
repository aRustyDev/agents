"""Abstract base classes for language-specific extractors and synthesizers.

This module defines the core abstractions that all language implementations
must follow. The architecture is designed to support the hybrid approach
described in ADR-009: tree-sitter for parsing + semantic enrichment.

Example:
    class PythonExtractor(Extractor):
        def extract(self, source: str, path: str, config: ExtractConfig) -> IRVersion:
            # 1. Parse with tree-sitter
            # 2. Normalize to GAST
            # 3. Enrich with jedi/pyright
            # 4. Generate IR layers
            ...

        def supported_version(self) -> str:
            return "ir-v1.0"
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    from ir_core.models import IRVersion, GapMarker, SemanticAnnotation


class ExtractionMode(str, Enum):
    """Mode of extraction determining what layers are populated.

    Attributes:
        FULL_MODULE: Complete codebase conversion (layers 0-4)
        SINGLE_FUNCTION: Function-level extraction (layers 0-2)
        TYPE_ONLY: Interface/type extraction (layers 3-4)
        SIGNATURE_ONLY: API surface extraction (layers 2-4)
    """

    FULL_MODULE = "full_module"
    SINGLE_FUNCTION = "single_function"
    TYPE_ONLY = "type_only"
    SIGNATURE_ONLY = "signature_only"


class SemanticEnrichmentLevel(str, Enum):
    """Level of semantic analysis to perform.

    Attributes:
        NONE: No semantic analysis (syntax only)
        BASIC: Basic type inference (jedi-level)
        FULL: Full type analysis (pyright-level)
    """

    NONE = "none"
    BASIC = "basic"
    FULL = "full"


@dataclass
class ExtractConfig:
    """Configuration for extraction operations.

    Attributes:
        mode: Extraction mode determining layer population
        include_layer0: Whether to include expression-level details (Layer 0)
        semantic_level: Level of semantic enrichment
        resolve_imports: Whether to resolve cross-file imports
        project_root: Root directory for import resolution
        type_stubs_paths: Additional paths for type stubs (.pyi files)
        preserve_spans: Whether to preserve source location spans
        max_depth: Maximum depth for recursive extraction
        timeout_seconds: Timeout for extraction operations
        custom_options: Language-specific options

    Example:
        config = ExtractConfig(
            mode=ExtractionMode.FULL_MODULE,
            semantic_level=SemanticEnrichmentLevel.FULL,
            resolve_imports=True,
            project_root=Path("/path/to/project"),
        )
    """

    mode: ExtractionMode = ExtractionMode.FULL_MODULE
    include_layer0: bool = False
    semantic_level: SemanticEnrichmentLevel = SemanticEnrichmentLevel.BASIC
    resolve_imports: bool = False
    project_root: Path | None = None
    type_stubs_paths: list[Path] = field(default_factory=list)
    preserve_spans: bool = True
    max_depth: int = 10
    timeout_seconds: float = 30.0
    custom_options: dict[str, Any] = field(default_factory=dict)

    def with_mode(self, mode: ExtractionMode) -> ExtractConfig:
        """Create a copy with a different extraction mode."""
        return ExtractConfig(
            mode=mode,
            include_layer0=self.include_layer0,
            semantic_level=self.semantic_level,
            resolve_imports=self.resolve_imports,
            project_root=self.project_root,
            type_stubs_paths=self.type_stubs_paths.copy(),
            preserve_spans=self.preserve_spans,
            max_depth=self.max_depth,
            timeout_seconds=self.timeout_seconds,
            custom_options=self.custom_options.copy(),
        )


class OutputFormat(str, Enum):
    """Format for synthesized output.

    Attributes:
        SOURCE: Plain source code
        FORMATTED: Formatted with language formatter (black, rustfmt)
        PRESERVED: Attempt to preserve original formatting (libcst)
    """

    SOURCE = "source"
    FORMATTED = "formatted"
    PRESERVED = "preserved"


@dataclass
class SynthConfig:
    """Configuration for synthesis operations.

    Attributes:
        output_format: Format for the synthesized output
        line_length: Maximum line length for formatted output
        indent_size: Indentation size in spaces
        use_tabs: Whether to use tabs instead of spaces
        preserve_comments: Whether to preserve comments from IR
        emit_type_hints: Whether to emit type annotations
        emit_docstrings: Whether to emit docstrings
        target_version: Target language version (e.g., "3.11" for Python)
        custom_options: Language-specific options

    Example:
        config = SynthConfig(
            output_format=OutputFormat.FORMATTED,
            line_length=88,
            emit_type_hints=True,
            target_version="3.11",
        )
    """

    output_format: OutputFormat = OutputFormat.FORMATTED
    line_length: int = 88
    indent_size: int = 4
    use_tabs: bool = False
    preserve_comments: bool = True
    emit_type_hints: bool = True
    emit_docstrings: bool = True
    target_version: str | None = None
    custom_options: dict[str, Any] = field(default_factory=dict)


class Extractor(ABC):
    """Base class for language-specific extractors.

    Extractors transform source code into the 5-layer IR representation.
    They follow the hybrid architecture: tree-sitter for parsing,
    language-specific tools for semantic enrichment.

    Subclasses must implement:
        - extract(): Main extraction logic
        - supported_version(): IR version this extractor produces

    The extraction pipeline typically follows these steps:
        1. Parse source with tree-sitter
        2. Normalize CST to Generic AST (GAST)
        3. Enrich with semantic information (types, bindings)
        4. Generate 5-layer IR
        5. Validate against schema
        6. Detect and mark semantic gaps

    Example:
        class PythonExtractor(Extractor):
            def __init__(self):
                self._parser = TreeSitterAdapter("python")
                self._enricher = JediEnricher()

            def extract(self, source: str, path: str, config: ExtractConfig) -> IRVersion:
                tree = self._parser.parse(source)
                gast = self._normalize(tree)
                typed_gast = self._enricher.enrich(gast, source)
                return self._generate_ir(typed_gast, config)

            def supported_version(self) -> str:
                return "ir-v1.0"
    """

    @abstractmethod
    def extract(
        self, source: str, path: str, config: ExtractConfig
    ) -> "IRVersion":
        """Extract IR from source code.

        Args:
            source: Source code as a string
            path: File path (used for error reporting and import resolution)
            config: Extraction configuration

        Returns:
            IRVersion containing all extracted layers

        Raises:
            ExtractionError: If extraction fails with E001-E005 error codes
        """
        ...

    @abstractmethod
    def supported_version(self) -> str:
        """Return the IR schema version this extractor produces.

        Returns:
            Version string (e.g., "ir-v1.0")
        """
        ...

    def extract_file(self, path: Path, config: ExtractConfig) -> "IRVersion":
        """Convenience method to extract from a file path.

        Args:
            path: Path to the source file
            config: Extraction configuration

        Returns:
            IRVersion containing all extracted layers
        """
        source = path.read_text(encoding="utf-8")
        return self.extract(source, str(path), config)

    def validate_source(self, source: str, path: str) -> list["GapMarker"]:
        """Validate source code and return potential issues.

        This is a quick validation pass that doesn't perform full extraction.
        Useful for identifying problems before attempting extraction.

        Args:
            source: Source code as a string
            path: File path for error reporting

        Returns:
            List of gap markers for detected issues
        """
        # Default implementation - subclasses can override
        return []


class Synthesizer(ABC):
    """Base class for language-specific synthesizers.

    Synthesizers transform IR back into source code in the target language.
    They aim to produce idiomatic, compilable output while preserving
    semantic equivalence (L3 level).

    Subclasses must implement:
        - synthesize(): Main synthesis logic
        - target_language(): The language this synthesizer produces

    The synthesis pipeline typically follows these steps:
        1. Validate IR against schema
        2. Map IR constructs to target language patterns
        3. Generate source code
        4. Format output (if configured)
        5. Emit gap markers for unconvertible constructs

    Example:
        class PythonSynthesizer(Synthesizer):
            def synthesize(self, ir: IRVersion, config: SynthConfig) -> str:
                code = self._generate_code(ir)
                if config.output_format == OutputFormat.FORMATTED:
                    code = black.format_str(code)
                return code

            def target_language(self) -> str:
                return "python"
    """

    @abstractmethod
    def synthesize(self, ir: "IRVersion", config: SynthConfig) -> str:
        """Synthesize source code from IR.

        Args:
            ir: IRVersion containing the layers to synthesize
            config: Synthesis configuration

        Returns:
            Generated source code as a string

        Raises:
            SynthesisError: If synthesis fails with S001-S005 error codes
        """
        ...

    @abstractmethod
    def target_language(self) -> str:
        """Return the target language identifier.

        Returns:
            Language identifier (e.g., "python", "rust", "typescript")
        """
        ...

    def synthesize_to_file(
        self, ir: "IRVersion", path: Path, config: SynthConfig
    ) -> None:
        """Convenience method to synthesize directly to a file.

        Args:
            ir: IRVersion containing the layers to synthesize
            path: Output file path
            config: Synthesis configuration
        """
        code = self.synthesize(ir, config)
        path.write_text(code, encoding="utf-8")

    def estimate_output(self, ir: "IRVersion") -> dict[str, Any]:
        """Estimate properties of the synthesized output.

        Useful for planning and progress reporting.

        Args:
            ir: IRVersion to estimate for

        Returns:
            Dictionary with estimates (e.g., line_count, complexity)
        """
        # Default implementation - subclasses can override
        return {
            "estimated_lines": 0,
            "estimated_complexity": "unknown",
        }


# Type variable for extractor/synthesizer registration
E = TypeVar("E", bound=Extractor)
S = TypeVar("S", bound=Synthesizer)


class ExtractorRegistry:
    """Registry for language-specific extractors.

    Allows dynamic registration and lookup of extractors by language.

    Example:
        registry = ExtractorRegistry()
        registry.register("python", PythonExtractor)
        extractor = registry.get("python")
    """

    def __init__(self) -> None:
        self._extractors: dict[str, type[Extractor]] = {}

    def register(self, language: str, extractor_class: type[E]) -> None:
        """Register an extractor for a language.

        Args:
            language: Language identifier (e.g., "python", "rust")
            extractor_class: Extractor class to register
        """
        self._extractors[language.lower()] = extractor_class

    def get(self, language: str) -> Extractor:
        """Get an extractor instance for a language.

        Args:
            language: Language identifier

        Returns:
            Extractor instance

        Raises:
            KeyError: If no extractor is registered for the language
        """
        extractor_class = self._extractors.get(language.lower())
        if extractor_class is None:
            available = ", ".join(sorted(self._extractors.keys()))
            raise KeyError(
                f"No extractor registered for '{language}'. "
                f"Available: {available or 'none'}"
            )
        return extractor_class()

    def languages(self) -> list[str]:
        """Return list of registered languages."""
        return sorted(self._extractors.keys())


class SynthesizerRegistry:
    """Registry for language-specific synthesizers.

    Allows dynamic registration and lookup of synthesizers by language.

    Example:
        registry = SynthesizerRegistry()
        registry.register("python", PythonSynthesizer)
        synthesizer = registry.get("python")
    """

    def __init__(self) -> None:
        self._synthesizers: dict[str, type[Synthesizer]] = {}

    def register(self, language: str, synthesizer_class: type[S]) -> None:
        """Register a synthesizer for a language.

        Args:
            language: Language identifier
            synthesizer_class: Synthesizer class to register
        """
        self._synthesizers[language.lower()] = synthesizer_class

    def get(self, language: str) -> Synthesizer:
        """Get a synthesizer instance for a language.

        Args:
            language: Language identifier

        Returns:
            Synthesizer instance

        Raises:
            KeyError: If no synthesizer is registered for the language
        """
        synthesizer_class = self._synthesizers.get(language.lower())
        if synthesizer_class is None:
            available = ", ".join(sorted(self._synthesizers.keys()))
            raise KeyError(
                f"No synthesizer registered for '{language}'. "
                f"Available: {available or 'none'}"
            )
        return synthesizer_class()

    def languages(self) -> list[str]:
        """Return list of registered languages."""
        return sorted(self._synthesizers.keys())


# Global registries for convenience
_extractor_registry = ExtractorRegistry()
_synthesizer_registry = SynthesizerRegistry()


def register_extractor(language: str) -> Callable[[type[E]], type[E]]:
    """Decorator to register an extractor class.

    Example:
        @register_extractor("python")
        class PythonExtractor(Extractor):
            ...
    """

    def decorator(cls: type[E]) -> type[E]:
        _extractor_registry.register(language, cls)
        return cls

    return decorator


def register_synthesizer(language: str) -> Callable[[type[S]], type[S]]:
    """Decorator to register a synthesizer class.

    Example:
        @register_synthesizer("python")
        class PythonSynthesizer(Synthesizer):
            ...
    """

    def decorator(cls: type[S]) -> type[S]:
        _synthesizer_registry.register(language, cls)
        return cls

    return decorator


def get_extractor(language: str) -> Extractor:
    """Get a registered extractor for a language."""
    return _extractor_registry.get(language)


def get_synthesizer(language: str) -> Synthesizer:
    """Get a registered synthesizer for a language."""
    return _synthesizer_registry.get(language)
