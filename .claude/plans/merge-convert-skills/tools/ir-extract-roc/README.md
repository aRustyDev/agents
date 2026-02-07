# ir-extract-roc

Roc source code extractor for the IR extraction/synthesis pipeline.

## Overview

This package extracts Roc source code into the 5-layer IR representation, with special handling for Roc's unique functional approach:

- **Pure functions**: No side effects in the language core
- **Platform effects**: Effects via Task type from platforms
- **No exceptions**: Result type everywhere
- **Pattern matching**: when...is expressions
- **Tag unions**: Algebraic data types with variants
- **Abilities**: Type classes for polymorphism

## Installation

```bash
pip install ir-extract-roc
```

## Usage

### CLI

```bash
# Extract to YAML (default)
ir-extract-roc path/to/file.roc

# Extract to JSON
ir-extract-roc path/to/file.roc -f json

# Output to file
ir-extract-roc path/to/file.roc -o output.yaml
```

### API

```python
from ir_extract_roc import RocExtractor
from ir_core.base import ExtractConfig

extractor = RocExtractor()
config = ExtractConfig()

source = '''
app [main] { pf: platform "..." }

import pf.Stdout
import pf.Task exposing [Task]

main : Task {} *
main =
    Stdout.line "Hello, World!"

double : I64 -> I64
double = \\n -> n * 2
'''

ir = extractor.extract(source, "main.roc", config)
```

## Semantic Annotations

The extractor generates Roc-specific semantic annotations:

| Kind | Description |
|------|-------------|
| ROC-001 | Pure function (no side effects) |
| ROC-002 | Platform Task effect |
| ROC-003 | Result type (no exceptions) |
| ROC-004 | Pattern matching expression |
| ROC-005 | Tag union with variant data |

## Gap Detection

The extractor detects patterns that may require manual attention during conversion:

| Kind | Severity | Description |
|------|----------|-------------|
| ROC-010 | Medium | Platform-specific code |
| ROC-011 | Medium | Ability constraints |
| ROC-012 | Low | Complex pattern matching |
| ROC-013 | Low | Opaque types |
| ROC-014 | Low | Heavy backslash lambda usage |

## Cross-Language Conversion

When converting Roc to other languages, consider:

### Roc → Python
- Pure functions → Regular functions with @pure decorator (optional)
- Task → async/await
- Result → try/except or Result class
- Pattern matching → match statement (Python 3.10+)
- Tag unions → dataclasses with Union

### Roc → TypeScript
- Pure functions → Regular functions
- Task → Promise
- Result → Result type or union
- Pattern matching → switch/if-else
- Tag unions → discriminated unions

### Roc → Rust
- Pure functions → Functions without side effects
- Task → async fn returning Result
- Result → std::result::Result
- Pattern matching → match expressions
- Tag unions → enum with variants

### Roc → Go
- Pure functions → Regular functions
- Task → goroutine with channels
- Result → multiple returns with error
- Pattern matching → switch/type switch
- Tag unions → interface with implementations

## Roc Syntax Notes

Roc has unique syntax that differs from other languages:

### Backslash Lambdas
```roc
double = \n -> n * 2
add = \a, b -> a + b
```

### when...is Pattern Matching
```roc
describe = \animal ->
    when animal is
        Dog name -> "Dog named $(name)"
        Cat -> "A cat"
        _ -> "Unknown"
```

### Record Syntax
```roc
User : { name : Str, age : I64 }
user = { name: "Alice", age: 30 }
```

### Tag Unions
```roc
Result a e : [Ok a, Err e]
Maybe a : [Just a, Nothing]
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type check
mypy ir_extract_roc

# Lint
ruff check ir_extract_roc
```

## Known Limitations

1. **Parser maturity**: Uses regex-based parsing as tree-sitter-roc may not be available
2. **Roc pre-1.0**: Syntax may change in future Roc versions
3. **Platform specifics**: Platform-specific features not fully captured
4. **Abilities**: Complex ability bounds may not be fully parsed

## License

MIT
