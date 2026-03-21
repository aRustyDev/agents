"""IR Validation Tool.

Validates IR (Intermediate Representation) documents against the ir-v1 schema
and performs semantic validation including reference integrity, cross-layer
consistency, and gap marker validity.

This module provides:
- Schema validation against ir-v1.json
- Reference integrity checking (dangling refs, circular refs)
- Cross-layer consistency validation
- Gap marker validity verification
- Comprehensive error reporting

Example usage:
    from ir_validate import IRValidator

    validator = IRValidator()
    result = validator.validate(ir_data)

    if not result.is_valid:
        for error in result.errors:
            print(f"{error.code}: {error.message} at {error.location}")
"""

__version__ = "1.0.0"

from .errors import ValidationError, ValidationErrorCode
from .validator import IRValidator, ValidationResult

__all__ = [
    "IRValidator",
    "ValidationError",
    "ValidationErrorCode",
    "ValidationResult",
]
