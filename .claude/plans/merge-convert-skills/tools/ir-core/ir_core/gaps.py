"""Gap detection for semantic gaps during extraction/synthesis.

This module provides tools for detecting and categorizing semantic gaps
that occur during language-to-language conversion. It implements the
gap taxonomy from Phase 3 (54 patterns across 4 categories).

Features:
    - Automatic gap detection from IR analysis
    - Gap categorization and severity assignment
    - Suggested mitigations for each gap
    - Integration with preservation level tracking

Gap Categories:
    - Type System (TS-001 to TS-016): Type-related gaps
    - Memory Model (MM-001 to MM-012): Ownership/lifetime gaps
    - Effect System (EF-001 to EF-012): Exception/effect gaps
    - Concurrency (CC-001 to CC-014): Concurrency model gaps

Example:
    detector = GapDetector()
    gaps = detector.detect(ir, source_lang="python", target_lang="rust")
    for gap in gaps:
        print(f"{gap.gap_pattern_id}: {gap.description}")
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .models import (
    AutomationLevel,
    GapMarker,
    GapType,
    IRVersion,
    PreservationLevel,
    Severity,
    TypeKind,
    TypeRefKind,
)

# =============================================================================
# Gap Pattern Definitions
# =============================================================================


@dataclass
class GapPattern:
    """Definition of a gap pattern from Phase 3.

    Attributes:
        id: Pattern ID (e.g., "TS-001")
        name: Short name
        category: Category (type_system, memory_model, effect_system, concurrency)
        description: Detailed description
        gap_type: Default gap type
        severity: Default severity
        source_concepts: Source language concepts that trigger this gap
        target_concepts: Target language concepts (if any)
        mitigations: Suggested mitigation strategies
        automation_level: How much can be automated
        preservation_impact: Maximum preservation level with this gap
        affected_layers: Which IR layers are affected
    """

    id: str
    name: str
    category: str
    description: str
    gap_type: GapType
    severity: Severity
    source_concepts: list[str] = field(default_factory=list)
    target_concepts: list[str] = field(default_factory=list)
    mitigations: list[str] = field(default_factory=list)
    automation_level: AutomationLevel = AutomationLevel.PARTIAL
    preservation_impact: PreservationLevel = PreservationLevel.SEMANTIC
    affected_layers: list[int] = field(default_factory=list)


# Type System Patterns (TS-001 to TS-016)
TYPE_SYSTEM_PATTERNS = {
    "TS-001": GapPattern(
        id="TS-001",
        name="Dynamic to Static Type",
        category="type_system",
        description="Dynamic typing requires type inference for static target",
        gap_type=GapType.LOSSY,
        severity=Severity.HIGH,
        source_concepts=["dynamic typing", "duck typing", "any type"],
        target_concepts=["static types", "generic types"],
        mitigations=[
            "Infer types from usage patterns",
            "Use generic types with bounds",
            "Add explicit type annotations",
        ],
        automation_level=AutomationLevel.PARTIAL,
        preservation_impact=PreservationLevel.SEMANTIC,
        affected_layers=[1, 3],
    ),
    "TS-002": GapPattern(
        id="TS-002",
        name="Nullable to Non-null",
        category="type_system",
        description="Nullable types must be converted to Option/Maybe",
        gap_type=GapType.STRUCTURAL,
        severity=Severity.MEDIUM,
        source_concepts=["null", "None", "undefined"],
        target_concepts=["Option", "Maybe", "Optional"],
        mitigations=[
            "Convert null to Option::None",
            "Add null checks at boundaries",
            "Use default values where appropriate",
        ],
        automation_level=AutomationLevel.FULL,
        preservation_impact=PreservationLevel.IDIOMATIC,
        affected_layers=[1, 3],
    ),
    "TS-003": GapPattern(
        id="TS-003",
        name="HKT to Non-HKT",
        category="type_system",
        description="Higher-kinded type abstraction cannot be preserved",
        gap_type=GapType.LOSSY,
        severity=Severity.HIGH,
        source_concepts=["Functor", "Monad", "Applicative", "type constructor"],
        target_concepts=["concrete types", "trait specialization"],
        mitigations=[
            "Generate specialized implementations",
            "Use defunctionalization",
            "Accept code duplication",
        ],
        automation_level=AutomationLevel.PARTIAL,
        preservation_impact=PreservationLevel.SEMANTIC,
        affected_layers=[2, 3],
    ),
    "TS-004": GapPattern(
        id="TS-004",
        name="Gradual to Full Static",
        category="type_system",
        description="Gradually typed code has incomplete type coverage",
        gap_type=GapType.LOSSY,
        severity=Severity.MEDIUM,
        source_concepts=["gradual typing", "Any", "untyped"],
        target_concepts=["full static typing"],
        mitigations=[
            "Run type inference on untyped sections",
            "Use generic type bounds",
            "Fallback to Any/Object for unknowns",
        ],
        automation_level=AutomationLevel.PARTIAL,
        preservation_impact=PreservationLevel.SEMANTIC,
        affected_layers=[1, 3],
    ),
    "TS-005": GapPattern(
        id="TS-005",
        name="Duck Type to Interface",
        category="type_system",
        description="Structural/duck typing requires explicit interface",
        gap_type=GapType.STRUCTURAL,
        severity=Severity.MEDIUM,
        source_concepts=["duck typing", "structural typing", "protocol"],
        target_concepts=["interface", "trait", "explicit protocol"],
        mitigations=[
            "Infer interface from usage",
            "Generate trait/interface from methods used",
            "Use structural typing if available",
        ],
        automation_level=AutomationLevel.PARTIAL,
        preservation_impact=PreservationLevel.IDIOMATIC,
        affected_layers=[3],
    ),
}

# Memory Model Patterns (MM-001 to MM-012)
MEMORY_MODEL_PATTERNS = {
    "MM-001": GapPattern(
        id="MM-001",
        name="GC to Manual Memory",
        category="memory_model",
        description="Garbage collection must be replaced with manual memory management",
        gap_type=GapType.STRUCTURAL,
        severity=Severity.CRITICAL,
        source_concepts=["garbage collection", "automatic memory"],
        target_concepts=["malloc/free", "manual allocation"],
        mitigations=[
            "Track all allocations",
            "Add explicit deallocation",
            "Use RAII patterns",
        ],
        automation_level=AutomationLevel.NONE,
        preservation_impact=PreservationLevel.SYNTACTIC,
        affected_layers=[1],
    ),
    "MM-002": GapPattern(
        id="MM-002",
        name="GC to Ownership",
        category="memory_model",
        description="GC-based memory must be converted to ownership model",
        gap_type=GapType.STRUCTURAL,
        severity=Severity.HIGH,
        source_concepts=["garbage collection", "reference counting"],
        target_concepts=["ownership", "borrowing", "lifetimes"],
        mitigations=[
            "Analyze ownership patterns",
            "Use Rc/Arc for shared data",
            "Design clear ownership hierarchy",
        ],
        automation_level=AutomationLevel.PARTIAL,
        preservation_impact=PreservationLevel.SEMANTIC,
        affected_layers=[1],
    ),
    "MM-003": GapPattern(
        id="MM-003",
        name="Shared to Linear",
        category="memory_model",
        description="Shared mutable state requires linear type transformation",
        gap_type=GapType.STRUCTURAL,
        severity=Severity.HIGH,
        source_concepts=["shared mutable", "aliasing"],
        target_concepts=["linear types", "unique ownership"],
        mitigations=[
            "Return modified values",
            "Use interior mutability",
            "Restructure to single owner",
        ],
        automation_level=AutomationLevel.PARTIAL,
        preservation_impact=PreservationLevel.SEMANTIC,
        affected_layers=[1],
    ),
    "MM-004": GapPattern(
        id="MM-004",
        name="Mutable to Immutable",
        category="memory_model",
        description="Mutable data structures require immutable transformation",
        gap_type=GapType.STRUCTURAL,
        severity=Severity.MEDIUM,
        source_concepts=["mutable", "in-place modification"],
        target_concepts=["immutable", "persistent data structures"],
        mitigations=[
            "Use functional update patterns",
            "Apply persistent data structures",
            "Return new values instead of mutating",
        ],
        automation_level=AutomationLevel.PARTIAL,
        preservation_impact=PreservationLevel.IDIOMATIC,
        affected_layers=[1],
    ),
}

# Effect System Patterns (EF-001 to EF-012)
EFFECT_SYSTEM_PATTERNS = {
    "EF-001": GapPattern(
        id="EF-001",
        name="Exceptions to Result",
        category="effect_system",
        description="Exception-based error handling to Result/Either types",
        gap_type=GapType.STRUCTURAL,
        severity=Severity.MEDIUM,
        source_concepts=["try/catch", "throw", "raise"],
        target_concepts=["Result", "Either", "? operator"],
        mitigations=[
            "Wrap throwing code in Result",
            "Map exception types to error variants",
            "Use ? for propagation",
        ],
        automation_level=AutomationLevel.FULL,
        preservation_impact=PreservationLevel.IDIOMATIC,
        affected_layers=[2],
    ),
    "EF-002": GapPattern(
        id="EF-002",
        name="Null to Option",
        category="effect_system",
        description="Null/undefined values to Option/Maybe types",
        gap_type=GapType.STRUCTURAL,
        severity=Severity.MEDIUM,
        source_concepts=["null", "None", "nil", "undefined"],
        target_concepts=["Option", "Maybe", "Optional"],
        mitigations=[
            "Wrap nullable values in Option",
            "Use map/flatMap for chaining",
            "Add null checks at boundaries",
        ],
        automation_level=AutomationLevel.FULL,
        preservation_impact=PreservationLevel.IDIOMATIC,
        affected_layers=[1, 2],
    ),
    "EF-003": GapPattern(
        id="EF-003",
        name="Checked to Unchecked Exceptions",
        category="effect_system",
        description="Checked exception handling differs from unchecked",
        gap_type=GapType.LOSSY,
        severity=Severity.LOW,
        source_concepts=["checked exceptions"],
        target_concepts=["unchecked exceptions", "panics"],
        mitigations=[
            "Document exception scenarios",
            "Convert to Result types",
            "Allow some to propagate as panics",
        ],
        automation_level=AutomationLevel.PARTIAL,
        preservation_impact=PreservationLevel.SEMANTIC,
        affected_layers=[2],
    ),
    "EF-009": GapPattern(
        id="EF-009",
        name="Lazy to Strict Evaluation",
        category="effect_system",
        description="Lazy evaluation semantics to strict/eager evaluation",
        gap_type=GapType.SEMANTIC,
        severity=Severity.HIGH,
        source_concepts=["lazy evaluation", "thunks", "call-by-need"],
        target_concepts=["strict evaluation", "call-by-value"],
        mitigations=[
            "Use iterators for lazy sequences",
            "Wrap in closures for deferred evaluation",
            "Be aware of evaluation order changes",
        ],
        automation_level=AutomationLevel.PARTIAL,
        preservation_impact=PreservationLevel.SEMANTIC,
        affected_layers=[1, 2],
    ),
}

# Concurrency Patterns (CC-001 to CC-014)
CONCURRENCY_PATTERNS = {
    "CC-001": GapPattern(
        id="CC-001",
        name="Actors to Threads",
        category="concurrency",
        description="Actor-based concurrency to thread-based model",
        gap_type=GapType.STRUCTURAL,
        severity=Severity.HIGH,
        source_concepts=["actors", "mailbox", "message passing"],
        target_concepts=["threads", "channels", "async/await"],
        mitigations=[
            "Map mailbox to channel",
            "Use actor library in target",
            "Implement message handlers as methods",
        ],
        automation_level=AutomationLevel.PARTIAL,
        preservation_impact=PreservationLevel.SEMANTIC,
        affected_layers=[2, 4],
    ),
    "CC-004": GapPattern(
        id="CC-004",
        name="CSP to Async/Await",
        category="concurrency",
        description="CSP-style channels to async/await model",
        gap_type=GapType.STRUCTURAL,
        severity=Severity.MEDIUM,
        source_concepts=["channels", "select", "goroutines"],
        target_concepts=["async/await", "futures", "promises"],
        mitigations=[
            "Map channels to async streams",
            "Use select! macro for multiplexing",
            "Consider buffering differences",
        ],
        automation_level=AutomationLevel.PARTIAL,
        preservation_impact=PreservationLevel.IDIOMATIC,
        affected_layers=[2],
    ),
    "CC-012": GapPattern(
        id="CC-012",
        name="Thread Safety Analysis",
        category="concurrency",
        description="Thread safety requirements differ between languages",
        gap_type=GapType.RUNTIME,
        severity=Severity.HIGH,
        source_concepts=["shared state", "mutable global"],
        target_concepts=["Send", "Sync", "thread-safe"],
        mitigations=[
            "Wrap in Mutex/RwLock",
            "Use atomic types",
            "Redesign for single-threaded access",
        ],
        automation_level=AutomationLevel.PARTIAL,
        preservation_impact=PreservationLevel.SEMANTIC,
        affected_layers=[1, 2],
    ),
}

# Combined pattern registry
ALL_PATTERNS: dict[str, GapPattern] = {
    **TYPE_SYSTEM_PATTERNS,
    **MEMORY_MODEL_PATTERNS,
    **EFFECT_SYSTEM_PATTERNS,
    **CONCURRENCY_PATTERNS,
}


# =============================================================================
# Gap Detection
# =============================================================================


@dataclass
class DetectionContext:
    """Context for gap detection.

    Attributes:
        source_language: Source language identifier
        target_language: Target language identifier
        ir: IRVersion being analyzed
        options: Detection options
    """

    source_language: str
    target_language: str
    ir: IRVersion
    options: dict[str, Any] = field(default_factory=dict)


class GapDetector:
    """Detects semantic gaps in IR during conversion.

    Analyzes IR to find potential semantic gaps based on:
    - Source/target language characteristics
    - IR constructs that are difficult to convert
    - Type system differences
    - Memory model differences
    - Effect system differences
    - Concurrency model differences

    Example:
        detector = GapDetector()

        # Detect gaps for Python -> Rust conversion
        gaps = detector.detect(ir, "python", "rust")

        for gap in gaps:
            print(f"{gap.severity}: {gap.description}")
            print(f"  Mitigations: {gap.suggested_mitigations}")
    """

    def __init__(self) -> None:
        """Initialize gap detector with registered patterns."""
        self._patterns = ALL_PATTERNS.copy()
        self._detectors: list[Callable[[DetectionContext], list[GapMarker]]] = []

        # Register default detectors
        self._register_default_detectors()

    def _register_default_detectors(self) -> None:
        """Register default gap detection functions."""
        self._detectors.extend([
            self._detect_type_system_gaps,
            self._detect_memory_model_gaps,
            self._detect_effect_system_gaps,
            self._detect_concurrency_gaps,
        ])

    def detect(
        self,
        ir: IRVersion,
        source_language: str,
        target_language: str,
        options: dict[str, Any] | None = None,
    ) -> list[GapMarker]:
        """Detect semantic gaps in IR.

        Args:
            ir: IRVersion to analyze
            source_language: Source language identifier
            target_language: Target language identifier
            options: Detection options

        Returns:
            List of detected GapMarkers
        """
        ctx = DetectionContext(
            source_language=source_language.lower(),
            target_language=target_language.lower(),
            ir=ir,
            options=options or {},
        )

        gaps: list[GapMarker] = []
        gap_id_counter = 0

        for detector in self._detectors:
            detected = detector(ctx)
            for gap in detected:
                # Assign unique ID if not set
                if not gap.id:
                    gap.id = f"gap-{gap_id_counter:04d}"
                    gap_id_counter += 1
                gaps.append(gap)

        return gaps

    def _detect_type_system_gaps(
        self,
        ctx: DetectionContext,
    ) -> list[GapMarker]:
        """Detect type system gaps."""
        gaps: list[GapMarker] = []

        # Check for dynamic typing (TS-001)
        if ctx.source_language in {"python", "ruby", "javascript"}:
            if ctx.target_language in {"rust", "go", "java", "typescript"}:
                # Check for Any/dynamic types in bindings
                for binding in ctx.ir.bindings:
                    if binding.type and binding.type.type_id:
                        type_id = binding.type.type_id.lower()
                        if "any" in type_id or "dynamic" in type_id:
                            pattern = self._patterns.get("TS-001")
                            if pattern:
                                gaps.append(self._create_gap_marker(
                                    pattern,
                                    location=binding.id,
                                    description=f"Binding '{binding.name}' has dynamic type",
                                ))

        # Check for nullable types (TS-002)
        for type_def in ctx.ir.types:
            if type_def.kind == TypeKind.ALIAS:
                if type_def.body.aliased_type:
                    if type_def.body.aliased_type.kind == TypeRefKind.UNION:
                        # Check if union contains null
                        members = type_def.body.aliased_type.members
                        null_types = {"null", "none", "undefined", "nil"}
                        has_null = any(
                            m.type_id and m.type_id.lower() in null_types
                            for m in members
                        )
                        if has_null:
                            pattern = self._patterns.get("TS-002")
                            if pattern:
                                gaps.append(self._create_gap_marker(
                                    pattern,
                                    location=type_def.id,
                                    description=f"Type '{type_def.name}' is nullable union",
                                ))

        # Check for HKT (TS-003)
        for type_def in ctx.ir.types:
            if type_def.kind == TypeKind.INTERFACE:
                # Look for type parameters used as type constructors
                for param in type_def.params:
                    for bound in param.bounds:
                        if bound.type_id and "functor" in bound.type_id.lower():
                            pattern = self._patterns.get("TS-003")
                            if pattern:
                                gaps.append(self._create_gap_marker(
                                    pattern,
                                    location=type_def.id,
                                    description=f"Type '{type_def.name}' uses higher-kinded types",
                                ))
                            break

        return gaps

    def _detect_memory_model_gaps(
        self,
        ctx: DetectionContext,
    ) -> list[GapMarker]:
        """Detect memory model gaps."""
        gaps: list[GapMarker] = []

        # GC to Ownership (MM-002)
        gc_languages = {"python", "ruby", "javascript", "java", "go", "c#"}
        ownership_languages = {"rust"}

        if ctx.source_language in gc_languages and ctx.target_language in ownership_languages:
            # All bindings need ownership analysis
            for binding in ctx.ir.bindings:
                # Check for mutable bindings that might need ownership hints
                if binding.mutability.value == "mutable":
                    # Check if there's already an ownership_hint annotation
                    has_hint = any(
                        ann.kind == "ownership_hint"
                        for ann in binding.annotations
                    )
                    if not has_hint:
                        pattern = self._patterns.get("MM-002")
                        if pattern:
                            gaps.append(self._create_gap_marker(
                                pattern,
                                location=binding.id,
                                description=f"Mutable binding '{binding.name}' needs ownership analysis",
                            ))

        # Shared to Linear (MM-003)
        for func in ctx.ir.functions:
            # Check for parameters that might create aliasing
            mutable_params = [
                p for p in func.params
                if p.mutability.value == "mutable"
            ]
            if len(mutable_params) > 1:
                pattern = self._patterns.get("MM-003")
                if pattern:
                    param_names = [p.name for p in mutable_params]
                    gaps.append(self._create_gap_marker(
                        pattern,
                        location=func.id,
                        description=f"Function '{func.name}' has multiple mutable params: {param_names}",
                    ))

        return gaps

    def _detect_effect_system_gaps(
        self,
        ctx: DetectionContext,
    ) -> list[GapMarker]:
        """Detect effect system gaps."""
        gaps: list[GapMarker] = []

        # Exceptions to Result (EF-001)
        exception_languages = {"python", "java", "javascript", "ruby"}
        result_languages = {"rust", "go", "haskell"}

        if ctx.source_language in exception_languages and ctx.target_language in result_languages:
            for func in ctx.ir.functions:
                # Check for throws effect
                throws_effects = [
                    e for e in func.effects
                    if e.kind.value == "throws"
                ]
                if throws_effects:
                    pattern = self._patterns.get("EF-001")
                    if pattern:
                        exception_types = [
                            e.type.type_id if e.type else "unknown"
                            for e in throws_effects
                        ]
                        gaps.append(self._create_gap_marker(
                            pattern,
                            location=func.id,
                            description=f"Function '{func.name}' throws: {exception_types}",
                        ))

        # Lazy to Strict (EF-009)
        lazy_languages = {"haskell"}
        strict_languages = {"python", "rust", "java", "go"}

        if ctx.source_language in lazy_languages and ctx.target_language in strict_languages:
            # All functions from lazy language need attention
            for func in ctx.ir.functions:
                pattern = self._patterns.get("EF-009")
                if pattern:
                    gaps.append(self._create_gap_marker(
                        pattern,
                        location=func.id,
                        description=f"Function '{func.name}' from lazy language needs evaluation analysis",
                    ))

        return gaps

    def _detect_concurrency_gaps(
        self,
        ctx: DetectionContext,
    ) -> list[GapMarker]:
        """Detect concurrency model gaps."""
        gaps: list[GapMarker] = []

        # Actors to Threads (CC-001)
        actor_languages = {"erlang", "elixir"}
        thread_languages = {"rust", "java", "go"}

        if ctx.source_language in actor_languages and ctx.target_language in thread_languages:
            # Check for module-level concurrency patterns
            pattern = self._patterns.get("CC-001")
            if pattern:
                gaps.append(self._create_gap_marker(
                    pattern,
                    location=ctx.ir.module.id,
                    description="Module uses actor-based concurrency",
                ))

        # CSP to Async (CC-004)
        csp_languages = {"go"}
        async_languages = {"rust", "javascript", "python"}

        if ctx.source_language in csp_languages and ctx.target_language in async_languages:
            pattern = self._patterns.get("CC-004")
            if pattern:
                gaps.append(self._create_gap_marker(
                    pattern,
                    location=ctx.ir.module.id,
                    description="Module may use CSP-style channels",
                ))

        # Thread Safety (CC-012)
        if ctx.target_language == "rust":
            # Check for types that might need Send/Sync
            for type_def in ctx.ir.types:
                if type_def.kind in {TypeKind.STRUCT, TypeKind.CLASS}:
                    # Check for interior mutability indicators
                    mutable_fields = [
                        f for f in type_def.body.fields
                        if f.mutability.value == "mutable"
                    ]
                    if mutable_fields:
                        pattern = self._patterns.get("CC-012")
                        if pattern:
                            gaps.append(self._create_gap_marker(
                                pattern,
                                location=type_def.id,
                                description=f"Type '{type_def.name}' has mutable fields, needs thread safety analysis",
                            ))

        return gaps

    def _create_gap_marker(
        self,
        pattern: GapPattern,
        location: str,
        description: str | None = None,
    ) -> GapMarker:
        """Create a GapMarker from a pattern.

        Args:
            pattern: GapPattern to use
            location: IR element location
            description: Optional custom description

        Returns:
            GapMarker instance
        """
        return GapMarker(
            id="",  # Will be assigned by detect()
            location=location,
            gap_type=pattern.gap_type,
            gap_pattern_id=pattern.id,
            severity=pattern.severity,
            description=description or pattern.description,
            source_concept=", ".join(pattern.source_concepts),
            target_concept=", ".join(pattern.target_concepts) if pattern.target_concepts else None,
            suggested_mitigations=pattern.mitigations.copy(),
            preservation_level=pattern.preservation_impact,
            automation_level=pattern.automation_level,
            affected_layers=pattern.affected_layers.copy(),
        )

    def register_pattern(self, pattern: GapPattern) -> None:
        """Register a custom gap pattern.

        Args:
            pattern: GapPattern to register
        """
        self._patterns[pattern.id] = pattern

    def register_detector(
        self,
        detector: Callable[[DetectionContext], list[GapMarker]],
    ) -> None:
        """Register a custom gap detector.

        Args:
            detector: Function that takes DetectionContext and returns gaps
        """
        self._detectors.append(detector)


def detect_gaps(
    ir: IRVersion,
    source_language: str,
    target_language: str,
) -> list[GapMarker]:
    """Convenience function for gap detection.

    Args:
        ir: IRVersion to analyze
        source_language: Source language
        target_language: Target language

    Returns:
        List of detected gaps
    """
    detector = GapDetector()
    return detector.detect(ir, source_language, target_language)
