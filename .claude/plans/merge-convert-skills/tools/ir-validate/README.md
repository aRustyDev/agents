# IR Validate

Validation tool for IR (Intermediate Representation) documents used in the multi-layer code conversion system.

## Features

- **Schema Validation (V001)**: Validates IR documents against the ir-v1.json schema
- **Reference Integrity (V002)**: Detects dangling references and circular dependencies
- **Cross-Layer Consistency (V003)**: Ensures layers are internally consistent
- **Gap Marker Validity (V004)**: Validates gap markers and preservation levels

## Installation

```bash
# From the tools directory
cd tools/ir-validate
pip install -e .

# With full dependencies (includes jsonschema)
pip install -e ".[full]"

# With dev dependencies
pip install -e ".[dev]"
```

## Usage

### Validate a Single File

```bash
# Basic validation
python -m ir_validate check file.ir.yaml

# Specify schema version
python -m ir_validate check --schema v1 file.ir.yaml

# JSON output for CI
python -m ir_validate check --format json file.ir.yaml

# Compact output (one line per error)
python -m ir_validate check --format compact file.ir.yaml

# Strict mode (treat warnings as errors)
python -m ir_validate check --strict file.ir.yaml
```

### Batch Validation

```bash
# Validate all IR files in a directory
python -m ir_validate batch dir/

# Custom file pattern
python -m ir_validate batch --pattern "*.ir.json" dir/

# Stop on first failure
python -m ir_validate batch --fail-fast dir/
```

### Programmatic Usage

```python
from ir_validate import IRValidator, ValidationResult

# Create validator
validator = IRValidator(schema_version="v1")

# Validate dict
ir_data = {
    "version": "ir-v1.0",
    "metadata": {"created_at": "2026-02-05T10:00:00Z"},
    "modules": [...]
}
result = validator.validate(ir_data)

# Check result
if not result.is_valid:
    print(f"Found {result.error_count} errors")
    for error in result.errors:
        print(f"  {error.code}: {error.message}")

# Format output
print(result.format(output_format="human"))
```

## Error Categories

### V001: Schema Validation Errors

Structural issues with the IR document.

| Code | Description |
|------|-------------|
| V001-001 | Missing required field |
| V001-002 | Invalid type |
| V001-003 | Invalid enum value |
| V001-004 | Pattern mismatch |
| V001-005 | Invalid format |
| V001-008 | Invalid version format |

### V002: Reference Integrity Errors

Issues with references between IR elements.

| Code | Description |
|------|-------------|
| V002-001 | Dangling reference |
| V002-002 | Circular reference |
| V002-003 | Invalid reference format |

### V003: Cross-Layer Consistency Errors

Inconsistencies between IR layers.

| Code | Description |
|------|-------------|
| V003-001 | Layer mismatch |
| V003-002 | Parent/child inconsistent |
| V003-003 | Type definition missing |
| V003-006 | Effect propagation violation |
| V003-008 | Visibility inconsistent |

### V004: Gap Marker Validity Errors

Issues with gap markers and preservation tracking.

| Code | Description |
|------|-------------|
| V004-001 | Invalid gap type |
| V004-002 | Invalid preservation level |
| V004-003 | Gap location not found |
| V004-006 | Annotation target not found |

## Output Formats

### Human (default)

```
============================================================
IR Validation Report
============================================================

File: example.ir.yaml
Schema: v1
Timestamp: 2026-02-05T10:30:00Z

Status: FAILED
Errors: 2, Warnings: 1, Info: 0

------------------------------------------------------------
Issues Found:
------------------------------------------------------------

[V002-001] ERROR
  Reference 'mod_nonexistent' not found
  Location: $.modules[0].submodules[0]
  Suggestion: Either define the referenced item 'mod_nonexistent' or remove the reference.
```

### JSON

```json
{
  "file_path": "example.ir.yaml",
  "schema_version": "v1",
  "timestamp": "2026-02-05T10:30:00Z",
  "summary": {
    "passed": false,
    "total_errors": 2,
    "total_warnings": 1,
    "total_info": 0,
    "errors_by_category": {"V002": 2, "V003": 1}
  },
  "errors": [...]
}
```

### Compact

```
example.ir.yaml:$.modules[0].submodules[0]:error:V002-001:Reference 'mod_nonexistent' not found
# FAIL: 2 errors, 1 warnings, 0 info
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html
```

### Type Checking

```bash
mypy .
```

### Linting

```bash
ruff check .
ruff format .
```

## Architecture

```
ir-validate/
├── __init__.py      # Package exports
├── __main__.py      # CLI entry point
├── validator.py     # Main IRValidator class
├── errors.py        # Error taxonomy (V001-V004)
├── schema.py        # JSON Schema validation
├── references.py    # Reference integrity checking
├── consistency.py   # Cross-layer consistency
├── report.py        # Output formatting
├── tests/
│   ├── conftest.py  # Test fixtures
│   ├── test_validator.py
│   ├── test_errors.py
│   ├── test_references.py
│   ├── test_consistency.py
│   └── test_report.py
└── pyproject.toml
```

## Related Documents

- [IR Schema Overview](../../docs/src/ir-schema/overview.md)
- [Equivalence Levels](../../docs/src/validation/equivalence-levels.md)
- [IR v1 Schema](../../schemas/ir-v1.json)
