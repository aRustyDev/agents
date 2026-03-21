"""Tests for base classes and registries."""

from __future__ import annotations

import pytest
from ir_core.base import (
    ExtractConfig,
    ExtractionMode,
    Extractor,
    ExtractorRegistry,
    OutputFormat,
    SemanticEnrichmentLevel,
    SynthConfig,
    Synthesizer,
    SynthesizerRegistry,
    get_extractor,
    get_synthesizer,
    register_extractor,
    register_synthesizer,
)
from ir_core.models import IRVersion, Module, ModuleMetadata


class TestExtractConfig:
    """Tests for ExtractConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = ExtractConfig()
        assert config.mode == ExtractionMode.FULL_MODULE
        assert config.include_layer0 is False
        assert config.semantic_level == SemanticEnrichmentLevel.BASIC
        assert config.resolve_imports is False
        assert config.preserve_spans is True
        assert config.timeout_seconds == 30.0

    def test_with_mode(self) -> None:
        """Test with_mode creates a copy."""
        config = ExtractConfig(
            mode=ExtractionMode.FULL_MODULE,
            include_layer0=True,
        )
        new_config = config.with_mode(ExtractionMode.SINGLE_FUNCTION)

        # New config has different mode
        assert new_config.mode == ExtractionMode.SINGLE_FUNCTION

        # Original unchanged
        assert config.mode == ExtractionMode.FULL_MODULE

        # Other fields preserved
        assert new_config.include_layer0 is True


class TestSynthConfig:
    """Tests for SynthConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = SynthConfig()
        assert config.output_format == OutputFormat.FORMATTED
        assert config.line_length == 88
        assert config.indent_size == 4
        assert config.use_tabs is False
        assert config.emit_type_hints is True

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = SynthConfig(
            output_format=OutputFormat.PRESERVED,
            line_length=120,
            target_version="3.11",
        )
        assert config.output_format == OutputFormat.PRESERVED
        assert config.line_length == 120
        assert config.target_version == "3.11"


class MockExtractor(Extractor):
    """Mock extractor for testing."""

    def extract(self, source: str, path: str, config: ExtractConfig) -> IRVersion:
        return IRVersion(
            module=Module(
                id="mod:mock",
                name="mock",
                metadata=ModuleMetadata(
                    source_file=path,
                    source_language="mock",
                ),
            ),
        )

    def supported_version(self) -> str:
        return "ir-v1.0"


class MockSynthesizer(Synthesizer):
    """Mock synthesizer for testing."""

    def synthesize(self, ir: IRVersion, config: SynthConfig) -> str:
        return f"# Mock output for {ir.module.name}"

    def target_language(self) -> str:
        return "mock"


class TestExtractor:
    """Tests for Extractor base class."""

    def test_extract_method(self) -> None:
        """Test extract method."""
        extractor = MockExtractor()
        config = ExtractConfig()

        ir = extractor.extract("print('hello')", "test.py", config)

        assert ir.module.name == "mock"
        assert ir.module.metadata.source_file == "test.py"

    def test_supported_version(self) -> None:
        """Test supported_version method."""
        extractor = MockExtractor()
        assert extractor.supported_version() == "ir-v1.0"

    def test_validate_source(self) -> None:
        """Test validate_source method."""
        extractor = MockExtractor()
        gaps = extractor.validate_source("print('hello')", "test.py")

        # Default implementation returns empty list
        assert gaps == []


class TestSynthesizer:
    """Tests for Synthesizer base class."""

    def test_synthesize_method(self) -> None:
        """Test synthesize method."""
        synthesizer = MockSynthesizer()
        ir = IRVersion(
            module=Module(
                id="mod:test",
                name="test",
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                ),
            ),
        )
        config = SynthConfig()

        output = synthesizer.synthesize(ir, config)

        assert "test" in output

    def test_target_language(self) -> None:
        """Test target_language method."""
        synthesizer = MockSynthesizer()
        assert synthesizer.target_language() == "mock"

    def test_estimate_output(self) -> None:
        """Test estimate_output method."""
        synthesizer = MockSynthesizer()
        ir = IRVersion(
            module=Module(
                id="mod:test",
                name="test",
                metadata=ModuleMetadata(
                    source_file="test.py",
                    source_language="python",
                ),
            ),
        )

        estimate = synthesizer.estimate_output(ir)

        assert "estimated_lines" in estimate
        assert "estimated_complexity" in estimate


class TestExtractorRegistry:
    """Tests for ExtractorRegistry."""

    def test_register_and_get(self) -> None:
        """Test registering and getting an extractor."""
        registry = ExtractorRegistry()
        registry.register("mock", MockExtractor)

        extractor = registry.get("mock")

        assert isinstance(extractor, MockExtractor)

    def test_get_unknown_raises(self) -> None:
        """Test getting unknown extractor raises KeyError."""
        registry = ExtractorRegistry()

        with pytest.raises(KeyError) as exc_info:
            registry.get("unknown")

        assert "unknown" in str(exc_info.value).lower()

    def test_languages(self) -> None:
        """Test languages method."""
        registry = ExtractorRegistry()
        registry.register("python", MockExtractor)
        registry.register("rust", MockExtractor)

        languages = registry.languages()

        assert "python" in languages
        assert "rust" in languages
        assert languages == sorted(languages)  # Alphabetically sorted

    def test_case_insensitive(self) -> None:
        """Test that language lookup is case-insensitive."""
        registry = ExtractorRegistry()
        registry.register("Python", MockExtractor)

        extractor = registry.get("python")
        assert isinstance(extractor, MockExtractor)

        extractor = registry.get("PYTHON")
        assert isinstance(extractor, MockExtractor)


class TestSynthesizerRegistry:
    """Tests for SynthesizerRegistry."""

    def test_register_and_get(self) -> None:
        """Test registering and getting a synthesizer."""
        registry = SynthesizerRegistry()
        registry.register("mock", MockSynthesizer)

        synthesizer = registry.get("mock")

        assert isinstance(synthesizer, MockSynthesizer)

    def test_get_unknown_raises(self) -> None:
        """Test getting unknown synthesizer raises KeyError."""
        registry = SynthesizerRegistry()

        with pytest.raises(KeyError):
            registry.get("unknown")


class TestDecorators:
    """Tests for registration decorators."""

    def test_register_extractor_decorator(self) -> None:
        """Test @register_extractor decorator."""
        # Note: This modifies global state, so we test it carefully

        @register_extractor("test_lang")
        class TestExtractor(Extractor):
            def extract(self, source: str, path: str, config: ExtractConfig) -> IRVersion:
                return IRVersion(
                    module=Module(
                        id="mod:test",
                        name="test",
                        metadata=ModuleMetadata(
                            source_file=path,
                            source_language="test_lang",
                        ),
                    ),
                )

            def supported_version(self) -> str:
                return "ir-v1.0"

        # Should be retrievable via global function
        extractor = get_extractor("test_lang")
        assert isinstance(extractor, TestExtractor)

    def test_register_synthesizer_decorator(self) -> None:
        """Test @register_synthesizer decorator."""

        @register_synthesizer("test_lang_synth")
        class TestSynthesizer(Synthesizer):
            def synthesize(self, ir: IRVersion, config: SynthConfig) -> str:
                return "test output"

            def target_language(self) -> str:
                return "test_lang_synth"

        synthesizer = get_synthesizer("test_lang_synth")
        assert isinstance(synthesizer, TestSynthesizer)
