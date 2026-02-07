# ir-synthesize-roc

Roc source code synthesizer for the IR extraction/synthesis pipeline.

## Overview

This package generates idiomatic Roc source code from the 5-layer IR representation:

- **Pure functions**: All functions are pure by default
- **Platform effects**: Effects via Task type
- **Result types**: Explicit error handling
- **Pattern matching**: when...is expressions
- **Tag unions**: Algebraic data types
- **Backslash lambdas**: Roc's unique syntax

## Installation

```bash
pip install ir-synthesize-roc
```

## Usage

### CLI

```bash
# Synthesize from IR file
ir-synthesize-roc ir-output.yaml

# Output to file
ir-synthesize-roc ir-output.yaml -o generated.roc
```

### API

```python
from ir_synthesize_roc import RocSynthesizer
from ir_core.base import SynthConfig
from ir_core.models import IRVersion, TypeDef, TypeKind, FunctionDef, Parameter

# Create IR
ir = IRVersion(
    version="ir-v1.0",
    source_language="python",
    source_path="example.py",
)

# Add a record type
ir.types.append(TypeDef(
    name="User",
    kind=TypeKind.STRUCT,
    properties=[
        {"name": "name", "type": "Str"},
        {"name": "age", "type": "I64"},
    ],
))

# Add a function
ir.functions.append(FunctionDef(
    name="double",
    parameters=[Parameter(name="n", type_annotation="I64")],
    return_type="I64",
))

# Synthesize
synthesizer = RocSynthesizer()
config = SynthConfig()
code = synthesizer.synthesize(ir, config)
print(code)
```

## Type Mapping

### Python → Roc

| Python | Roc |
|--------|-----|
| `int` | `I64` |
| `float` | `F64` |
| `str` | `Str` |
| `bool` | `Bool` |
| `bytes` | `List U8` |
| `list[T]` | `List T` |
| `dict[K, V]` | `Dict K V` |
| `Optional[T]` | `[Just T, Nothing]` |

### Rust → Roc

| Rust | Roc |
|------|-----|
| `i32`, `i64` | `I32`, `I64` |
| `u32`, `u64` | `U32`, `U64` |
| `f32`, `f64` | `F32`, `F64` |
| `String` | `Str` |
| `Vec<T>` | `List T` |
| `HashMap<K, V>` | `Dict K V` |
| `Option<T>` | `[Just T, Nothing]` |
| `Result<T, E>` | `Result T E` |

### Go → Roc

| Go | Roc |
|----|-----|
| `int`, `int64` | `I64` |
| `float64` | `F64` |
| `string` | `Str` |
| `[]T` | `List T` |
| `map[K]V` | `Dict K V` |
| `error` | `[Err Str]` |

## Cross-Language Gap Detection

### Python → Roc (PY-ROC-*)

| Gap | Description |
|-----|-------------|
| PY-ROC-001 | Exceptions → Result type |
| PY-ROC-002 | Mutable state → pure functions |
| PY-ROC-003 | Missing type annotations |

### TypeScript → Roc (TS-ROC-*)

| Gap | Description |
|-----|-------------|
| TS-ROC-001 | Classes → records + functions |
| TS-ROC-002 | null/undefined → tag unions |
| TS-ROC-003 | Async/await → Task |

### Rust → Roc (RS-ROC-*)

| Gap | Description |
|-----|-------------|
| RS-ROC-001 | Ownership → reference counting |
| RS-ROC-002 | Traits → abilities |
| RS-ROC-003 | Macros → manual expansion |

### Go → Roc (GO-ROC-*)

| Gap | Description |
|-----|-------------|
| GO-ROC-001 | Goroutines → platform tasks |
| GO-ROC-002 | Channels → tasks |
| GO-ROC-003 | Interfaces → abilities |
| GO-ROC-004 | Pointers → immutable values |

## Development

```bash
pip install -e ".[dev]"
pytest
mypy ir_synthesize_roc
```

## License

MIT
