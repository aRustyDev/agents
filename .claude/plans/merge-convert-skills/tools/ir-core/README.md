# IR Core

Core infrastructure for the IR extraction/synthesis pipeline (Phase 5).

## Overview

This package provides the foundational abstractions and utilities for the intermediate representation (IR) pipeline, enabling language-to-language code conversion with semantic preservation tracking.

## Architecture

The architecture follows ADR-009 (Hybrid Extractor Architecture):

```
Source Code
    |
    v
[Tree-sitter Parser]     -- Universal syntax parsing
    |
    v
[AST Normalizer]         -- Convert CST to Generic AST
    |
    v
[Semantic Enricher]      -- Language-specific type analysis
    |
    v
[IR Generator]           -- Produce 5-layer IR
    |
    v
[Schema Validator]       -- Validate against ir-v1.json
    |
    v
[Gap Detector]           -- Identify semantic gaps
```

## Installation

```bash
# Install with core dependencies
pip install -e .

# Install with tree-sitter support
pip install -e ".[treesitter]"

# Install with all optional dependencies
pip install -e ".[all]"
```

## Usage

### Basic Extraction

```python
from ir_core import Extractor, ExtractConfig, ExtractionMode
from ir_core.models import IRVersion

# Create custom extractor (or use language-specific implementation)
class MyExtractor(Extractor):
    def extract(self, source: str, path: str, config: ExtractConfig) -> IRVersion:
        # Implementation...
        pass

    def supported_version(self) -> str:
        return "ir-v1.0"

# Configure extraction
config = ExtractConfig(
    mode=ExtractionMode.FULL_MODULE,
    include_layer0=False,  # Skip expression layer for faster extraction
)

# Extract IR
extractor = MyExtractor()
ir = extractor.extract(source_code, "module.py", config)
```

### Validation

```python
from ir_core.validation import SchemaValidator, validate_ir

# Validate IR instance
result = validate_ir(ir)
if not result.is_valid:
    for error in result.errors:
        print(f"{error.code}: {error.message} at {error.path}")
```

### Gap Detection

```python
from ir_core.gaps import GapDetector, detect_gaps

# Detect gaps for Python -> Rust conversion
gaps = detect_gaps(ir, source_language="python", target_language="rust")

for gap in gaps:
    print(f"[{gap.severity}] {gap.gap_pattern_id}: {gap.description}")
    print(f"  Mitigations: {gap.suggested_mitigations}")
```

### Tree-sitter Parsing

```python
from ir_core.treesitter import TreeSitterAdapter

# Parse Python source
adapter = TreeSitterAdapter("python")
tree = adapter.parse("def hello(): pass")

# Query for functions
functions = tree.root.find_all("function_definition")
for func in functions:
    name = func.child_by_field("name")
    print(f"Found function: {name.text}")
```

## IR Schema Layers

| Layer | Name | Contents |
|-------|------|----------|
| 4 | Structural | Modules, imports, exports |
| 3 | Type | Type definitions, relationships |
| 2 | Control Flow | Functions, effects, CFG |
| 1 | Data Flow | Bindings, lifetimes, transformations |
| 0 | Expression | AST details (optional) |

## Error Codes

### Extraction Errors (E001-E005)

| Code | Description |
|------|-------------|
| E001 | Parse error - syntax error in source |
| E002 | Unsupported syntax - valid but not supported |
| E003 | Type inference failed - cannot determine type |
| E004 | Cross-file reference - unresolved import |
| E005 | Metaprogramming - dynamic code generation |

### Synthesis Errors (S001-S005)

| Code | Description |
|------|-------------|
| S001 | Invalid IR - schema validation failed |
| S002 | Unsupported construct - IR not supported in target |
| S003 | Type mapping failed - cannot map type |
| S004 | Missing dependency - required import unavailable |
| S005 | Code generation failed - synthesis error |

### Validation Errors (V001-V004)

| Code | Description |
|------|-------------|
| V001 | Schema mismatch - IR doesn't match schema |
| V002 | Cross-reference error - invalid reference |
| V003 | Consistency error - layers inconsistent |
| V004 | Preservation violation - level not met |

## Gap Patterns

The gap detector implements 54 patterns from Phase 3:

- **Type System (TS-001 to TS-016)**: Dynamic typing, HKT, nullability
- **Memory Model (MM-001 to MM-012)**: GC to ownership, lifetimes
- **Effect System (EF-001 to EF-012)**: Exceptions, error handling
- **Concurrency (CC-001 to CC-014)**: Actors, channels, thread safety

## Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=ir_core --cov-report=term-missing
```

## Related Documents

- ADR-009: Extractor Architecture
- IR Schema: `docs/src/ir-schema/`
- Equivalence Levels: `docs/src/validation/equivalence-levels.md`
- Phase 5 Plan: `phase/5-validation-tooling.md`

## License

MIT
