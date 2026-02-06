"""IR Round-Trip Validation Tool.

Validates Python -> IR -> Python round-trip preservation at multiple
equivalence levels (L1-L3) as defined in the equivalence-levels specification.

This module provides:
- RoundTripValidator: Main validator for round-trip testing
- CodeComparator: Compare source and target at different preservation levels
- SafeExecutor: Safe code execution with sandboxing
- RoundTripReport: Generate validation reports

Preservation Levels:
    L1 (Syntactic): AST isomorphism after normalization
    L2 (Operational): Lock-step execution traces match
    L3 (Semantic): Same I/O behavior for all inputs (Phase 5 target)

Example usage:
    from ir_roundtrip import RoundTripValidator, PreservationLevel

    validator = RoundTripValidator()
    result = validator.validate(source_code, PreservationLevel.L3_SEMANTIC)

    if result.passed:
        print("Round-trip validation passed!")
    else:
        print(f"Validation failed: {result.failure_reason}")
        for diff in result.differences:
            print(f"  - {diff}")

CLI usage:
    python -m ir_roundtrip validate file.py
    python -m ir_roundtrip validate --level l3 file.py
    python -m ir_roundtrip batch dir/ --report report.json
    python -m ir_roundtrip benchmark --samples 100

See Also:
    - docs/src/validation/equivalence-levels.md: Preservation level definitions
    - ir-extract-python: Python extractor
    - ir-synthesize-python: Python synthesizer
"""

from __future__ import annotations

from .validator import (
    RoundTripValidator,
    RoundTripResult,
    PreservationLevel,
    ValidationStatus,
)
from .comparison import (
    CodeComparator,
    CompareResult,
    ASTDifference,
    SemanticDifference,
)
from .executor import (
    SafeExecutor,
    ExecutionResult,
    ExecutionError,
)
from .report import (
    RoundTripReport,
    ReportFormat,
)

__version__ = "0.1.0"
__all__ = [
    # Main validator
    "RoundTripValidator",
    "RoundTripResult",
    "PreservationLevel",
    "ValidationStatus",
    # Comparison
    "CodeComparator",
    "CompareResult",
    "ASTDifference",
    "SemanticDifference",
    # Execution
    "SafeExecutor",
    "ExecutionResult",
    "ExecutionError",
    # Reporting
    "RoundTripReport",
    "ReportFormat",
]
