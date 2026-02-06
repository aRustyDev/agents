"""Round-trip validation engine.

This module provides the core RoundTripValidator class that validates
Python -> IR -> Python round-trip preservation at specified levels.

The validation process:
1. Extract source code to IR using ir-extract-python
2. Validate the IR using ir-validate
3. Synthesize IR back to target code using ir-synthesize-python
4. Compare source and target at the specified preservation level

Example:
    validator = RoundTripValidator()
    result = validator.validate(source, PreservationLevel.L3_SEMANTIC)

    if not result.passed:
        print(f"Failed: {result.failure_reason}")
"""

from __future__ import annotations

import hashlib
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable

# Add sibling tools to path
TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR / "ir-core"))
sys.path.insert(0, str(TOOLS_DIR / "ir-extract-python"))
sys.path.insert(0, str(TOOLS_DIR / "ir-synthesize-python"))
sys.path.insert(0, str(TOOLS_DIR / "ir-validate"))

from ir_core.base import ExtractConfig, SynthConfig, OutputFormat, ExtractionMode
from ir_core.models import IRVersion, GapMarker

from .comparison import CodeComparator, CompareResult
from .executor import SafeExecutor, ExecutionResult


class PreservationLevel(str, Enum):
    """Preservation levels for round-trip validation.

    These correspond to the L1-L3 levels defined in equivalence-levels.md.
    Phase 5 targets L3 (Semantic) equivalence.

    Attributes:
        L1_SYNTACTIC: AST structure matches after normalization
        L2_OPERATIONAL: Execution traces match (same intermediate states)
        L3_SEMANTIC: Same I/O behavior for all inputs (black-box equivalence)
    """

    L1_SYNTACTIC = "l1"
    L2_OPERATIONAL = "l2"
    L3_SEMANTIC = "l3"


class ValidationStatus(str, Enum):
    """Status of a round-trip validation.

    Attributes:
        PASSED: Validation passed at the specified level
        FAILED: Validation failed (differences found)
        ERROR: Validation could not complete (extraction/synthesis error)
        SKIPPED: Validation was skipped (unsupported construct)
    """

    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class RoundTripResult:
    """Result of a round-trip validation.

    Attributes:
        status: Validation status
        level: Preservation level tested
        source: Original source code
        target: Synthesized target code (if successful)
        ir: Intermediate representation (if extraction succeeded)
        comparison: Detailed comparison result
        execution_results: L3 execution comparison results
        duration_ms: Validation duration in milliseconds
        timestamp: When validation was performed
        failure_reason: Human-readable failure explanation
        gaps: Gap markers from extraction/synthesis
        metadata: Additional validation metadata
    """

    status: ValidationStatus
    level: PreservationLevel
    source: str
    target: str | None = None
    ir: IRVersion | None = None
    comparison: CompareResult | None = None
    execution_results: list[tuple[ExecutionResult, ExecutionResult]] = field(
        default_factory=list
    )
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    failure_reason: str | None = None
    gaps: list[GapMarker] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        """Check if validation passed."""
        return self.status == ValidationStatus.PASSED

    @property
    def source_hash(self) -> str:
        """SHA-256 hash of source code."""
        return hashlib.sha256(self.source.encode("utf-8")).hexdigest()

    @property
    def target_hash(self) -> str | None:
        """SHA-256 hash of target code, if available."""
        if self.target is None:
            return None
        return hashlib.sha256(self.target.encode("utf-8")).hexdigest()

    def summary(self) -> str:
        """Generate a one-line summary."""
        status_icon = {
            ValidationStatus.PASSED: "[PASS]",
            ValidationStatus.FAILED: "[FAIL]",
            ValidationStatus.ERROR: "[ERROR]",
            ValidationStatus.SKIPPED: "[SKIP]",
        }[self.status]

        level_str = self.level.value.upper()
        duration_str = f"{self.duration_ms:.1f}ms"

        if self.failure_reason:
            return f"{status_icon} {level_str} {duration_str} - {self.failure_reason}"
        return f"{status_icon} {level_str} {duration_str}"


@dataclass
class SemanticResult:
    """Result of L3 semantic equivalence verification.

    Attributes:
        equivalent: Whether semantic equivalence holds
        test_count: Number of test inputs executed
        pass_count: Number of tests that passed
        fail_count: Number of tests that failed
        counterexamples: Inputs that produced different outputs
        confidence: Statistical confidence (0.0-1.0)
    """

    equivalent: bool
    test_count: int = 0
    pass_count: int = 0
    fail_count: int = 0
    counterexamples: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 1.0

    @property
    def pass_rate(self) -> float:
        """Percentage of tests that passed."""
        if self.test_count == 0:
            return 0.0
        return self.pass_count / self.test_count


class RoundTripValidator:
    """Validate Python -> IR -> Python round-trip preservation.

    This validator performs the complete round-trip pipeline and compares
    the source and synthesized code at the specified preservation level.

    Attributes:
        extractor: Python extractor instance
        synthesizer: Python synthesizer instance
        comparator: Code comparator instance
        executor: Safe code executor instance

    Example:
        validator = RoundTripValidator()

        # Basic validation at L3
        result = validator.validate(source, PreservationLevel.L3_SEMANTIC)

        # Validation with custom test inputs
        result = validator.validate_l3_semantic(
            source,
            target,
            test_inputs=[{"x": 1}, {"x": 2}, {"x": -1}]
        )
    """

    def __init__(
        self,
        extract_config: ExtractConfig | None = None,
        synth_config: SynthConfig | None = None,
    ) -> None:
        """Initialize the round-trip validator.

        Args:
            extract_config: Configuration for extraction (default: full module)
            synth_config: Configuration for synthesis (default: formatted output)
        """
        self.extract_config = extract_config or ExtractConfig(
            mode=ExtractionMode.FULL_MODULE,
            include_layer0=False,
            preserve_spans=True,
        )
        self.synth_config = synth_config or SynthConfig(
            output_format=OutputFormat.FORMATTED,
            emit_type_hints=True,
            emit_docstrings=True,
        )

        self.comparator = CodeComparator()
        self.executor = SafeExecutor()

        # Lazy-loaded extractors/synthesizers
        self._extractor: Any = None
        self._synthesizer: Any = None
        self._ir_validator: Any = None

    @property
    def extractor(self) -> Any:
        """Get the Python extractor (lazy loaded)."""
        if self._extractor is None:
            try:
                from ir_extract_python import PythonExtractor
                self._extractor = PythonExtractor()
            except ImportError as e:
                raise ImportError(
                    "ir-extract-python not available. "
                    "Ensure it is in the Python path."
                ) from e
        return self._extractor

    @property
    def synthesizer(self) -> Any:
        """Get the Python synthesizer (lazy loaded)."""
        if self._synthesizer is None:
            try:
                from ir_synthesize_python import PythonSynthesizer
                self._synthesizer = PythonSynthesizer()
            except ImportError as e:
                raise ImportError(
                    "ir-synthesize-python not available. "
                    "Ensure it is in the Python path."
                ) from e
        return self._synthesizer

    @property
    def ir_validator(self) -> Any:
        """Get the IR validator (lazy loaded)."""
        if self._ir_validator is None:
            try:
                from ir_validate import IRValidator
                self._ir_validator = IRValidator()
            except ImportError as e:
                raise ImportError(
                    "ir-validate not available. "
                    "Ensure it is in the Python path."
                ) from e
        return self._ir_validator

    def validate(
        self,
        source: str,
        level: PreservationLevel = PreservationLevel.L3_SEMANTIC,
        filename: str = "test.py",
        test_inputs: list[dict[str, Any]] | None = None,
    ) -> RoundTripResult:
        """Validate round-trip at the specified preservation level.

        Args:
            source: Python source code to validate
            level: Preservation level to test
            filename: Filename for error reporting
            test_inputs: Custom test inputs for L3 validation

        Returns:
            RoundTripResult with validation details
        """
        start_time = time.perf_counter()

        try:
            # Step 1: Extract source to IR
            ir = self._extract(source, filename)

            # Step 2: Validate IR
            ir_valid = self._validate_ir(ir)
            if not ir_valid:
                return self._make_result(
                    status=ValidationStatus.ERROR,
                    level=level,
                    source=source,
                    ir=ir,
                    failure_reason="IR validation failed",
                    duration_ms=self._elapsed_ms(start_time),
                )

            # Step 3: Synthesize IR to target
            target = self._synthesize(ir)

            # Step 4: Compare at the specified level
            if level == PreservationLevel.L1_SYNTACTIC:
                comparison = self.comparator.compare_l1_syntactic(source, target)
            elif level == PreservationLevel.L2_OPERATIONAL:
                comparison = self.comparator.compare_l2_operational(source, target)
            else:  # L3_SEMANTIC
                comparison = self.comparator.compare_l3_semantic(
                    source, target, test_inputs or []
                )

            # Step 5: Run L3 semantic tests if at that level
            execution_results: list[tuple[ExecutionResult, ExecutionResult]] = []
            if level == PreservationLevel.L3_SEMANTIC and test_inputs:
                execution_results = self._run_semantic_tests(
                    source, target, test_inputs
                )

            # Determine status
            status = (
                ValidationStatus.PASSED if comparison.equivalent
                else ValidationStatus.FAILED
            )

            return self._make_result(
                status=status,
                level=level,
                source=source,
                target=target,
                ir=ir,
                comparison=comparison,
                execution_results=execution_results,
                failure_reason=comparison.summary if not comparison.equivalent else None,
                gaps=list(ir.gaps) if ir else [],
                duration_ms=self._elapsed_ms(start_time),
            )

        except Exception as e:
            return self._make_result(
                status=ValidationStatus.ERROR,
                level=level,
                source=source,
                failure_reason=f"Validation error: {e}",
                duration_ms=self._elapsed_ms(start_time),
            )

    def validate_l3_semantic(
        self,
        source: str,
        target: str,
        test_inputs: list[dict[str, Any]],
        func_name: str | None = None,
    ) -> SemanticResult:
        """Verify L3 semantic equivalence with test inputs.

        Executes both source and target code with the given test inputs
        and compares outputs for equivalence.

        Args:
            source: Original source code
            target: Synthesized target code
            test_inputs: List of input dictionaries
            func_name: Function name to test (auto-detected if None)

        Returns:
            SemanticResult with equivalence details
        """
        if not test_inputs:
            return SemanticResult(equivalent=True, test_count=0, confidence=0.0)

        # Auto-detect function name if not provided
        if func_name is None:
            func_name = self._detect_function_name(source)
            if func_name is None:
                return SemanticResult(
                    equivalent=False,
                    test_count=0,
                    counterexamples=[{"error": "Could not detect function name"}],
                    confidence=0.0,
                )

        pass_count = 0
        fail_count = 0
        counterexamples: list[dict[str, Any]] = []

        for inputs in test_inputs:
            source_result = self.executor.execute(source, inputs, func_name=func_name)
            target_result = self.executor.execute(target, inputs, func_name=func_name)

            if self.executor.compare_outputs(source_result, target_result):
                pass_count += 1
            else:
                fail_count += 1
                counterexamples.append({
                    "inputs": inputs,
                    "source_output": source_result.to_dict(),
                    "target_output": target_result.to_dict(),
                })

        total = pass_count + fail_count
        equivalent = fail_count == 0

        # Statistical confidence based on sample size
        # Using a simple heuristic: more tests = higher confidence
        confidence = min(1.0, total / 100)  # 100 tests = 100% confidence

        return SemanticResult(
            equivalent=equivalent,
            test_count=total,
            pass_count=pass_count,
            fail_count=fail_count,
            counterexamples=counterexamples,
            confidence=confidence,
        )

    def validate_batch(
        self,
        sources: list[tuple[str, str]],
        level: PreservationLevel = PreservationLevel.L3_SEMANTIC,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> list[RoundTripResult]:
        """Validate multiple source files.

        Args:
            sources: List of (filename, source_code) tuples
            level: Preservation level to test
            progress_callback: Optional callback(current, total) for progress

        Returns:
            List of RoundTripResult for each source
        """
        results: list[RoundTripResult] = []
        total = len(sources)

        for i, (filename, source) in enumerate(sources):
            if progress_callback:
                progress_callback(i, total)

            result = self.validate(source, level, filename)
            results.append(result)

        if progress_callback:
            progress_callback(total, total)

        return results

    def _extract(self, source: str, filename: str) -> IRVersion:
        """Extract source code to IR."""
        return self.extractor.extract(source, filename, self.extract_config)

    def _validate_ir(self, ir: IRVersion) -> bool:
        """Validate IR against schema and semantic rules."""
        try:
            ir_dict = ir.model_dump(mode="json")
            result = self.ir_validator.validate(ir_dict)
            return result.is_valid
        except Exception:
            return False

    def _synthesize(self, ir: IRVersion) -> str:
        """Synthesize IR back to Python code."""
        return self.synthesizer.synthesize(ir, self.synth_config)

    def _run_semantic_tests(
        self,
        source: str,
        target: str,
        test_inputs: list[dict[str, Any]],
    ) -> list[tuple[ExecutionResult, ExecutionResult]]:
        """Run semantic equivalence tests."""
        results: list[tuple[ExecutionResult, ExecutionResult]] = []

        func_name = self._detect_function_name(source)
        if func_name is None:
            return results

        for inputs in test_inputs:
            source_result = self.executor.execute(source, inputs, func_name=func_name)
            target_result = self.executor.execute(target, inputs, func_name=func_name)
            results.append((source_result, target_result))

        return results

    def _detect_function_name(self, source: str) -> str | None:
        """Auto-detect the first function name in source code."""
        import ast

        try:
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Skip private functions
                    if not node.name.startswith("_"):
                        return node.name
        except SyntaxError:
            pass

        return None

    def _make_result(
        self,
        status: ValidationStatus,
        level: PreservationLevel,
        source: str,
        target: str | None = None,
        ir: IRVersion | None = None,
        comparison: CompareResult | None = None,
        execution_results: list[tuple[ExecutionResult, ExecutionResult]] | None = None,
        failure_reason: str | None = None,
        gaps: list[GapMarker] | None = None,
        duration_ms: float = 0.0,
    ) -> RoundTripResult:
        """Create a RoundTripResult with defaults."""
        return RoundTripResult(
            status=status,
            level=level,
            source=source,
            target=target,
            ir=ir,
            comparison=comparison,
            execution_results=execution_results or [],
            duration_ms=duration_ms,
            failure_reason=failure_reason,
            gaps=gaps or [],
        )

    def _elapsed_ms(self, start_time: float) -> float:
        """Calculate elapsed time in milliseconds."""
        return (time.perf_counter() - start_time) * 1000
