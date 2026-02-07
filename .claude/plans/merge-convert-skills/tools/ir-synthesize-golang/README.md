# ir-synthesize-golang

Go source code synthesizer for the IR extraction/synthesis pipeline.

## Overview

This package generates idiomatic Go source code from the 5-layer IR representation, with proper handling of Go-specific patterns:

- **Error handling**: Converts to multiple return values with error
- **Concurrency**: Generates goroutines and channels from async patterns
- **Defer statements**: Resource cleanup patterns
- **Interfaces**: Structural typing (implicit satisfaction)
- **Generics**: Go 1.18+ type parameters

## Installation

```bash
pip install ir-synthesize-golang
```

## Usage

### CLI

```bash
# Synthesize from IR file (formatted by gofmt)
ir-synthesize-golang ir-output.yaml

# Output to file
ir-synthesize-golang ir-output.yaml -o generated.go

# Skip formatting
ir-synthesize-golang ir-output.yaml --no-format
```

### API

```python
from ir_synthesize_golang import GolangSynthesizer
from ir_core.base import SynthConfig
from ir_core.models import IRVersion, TypeDef, TypeKind, FunctionDef, Parameter

# Create IR
ir = IRVersion(
    version="ir-v1.0",
    source_language="python",
    source_path="example.py",
)

# Add a struct (from Python dataclass)
ir.types.append(TypeDef(
    name="User",
    kind=TypeKind.STRUCT,
    properties=[
        {"name": "Name", "type": "string"},
        {"name": "Email", "type": "string"},
        {"name": "Age", "type": "int"},
    ],
))

# Add a function
ir.functions.append(FunctionDef(
    name="NewUser",
    parameters=[
        Parameter(name="name", type_annotation="string"),
        Parameter(name="email", type_annotation="string"),
    ],
    return_type="*User",
))

# Synthesize
synthesizer = GolangSynthesizer()
config = SynthConfig(format=True)
code = synthesizer.synthesize(ir, config)
print(code)
```

## Type Mapping

The synthesizer converts types from source languages to Go:

### Python → Go

| Python | Go |
|--------|-----|
| `int` | `int` |
| `float` | `float64` |
| `str` | `string` |
| `bool` | `bool` |
| `bytes` | `[]byte` |
| `list[T]` | `[]T` |
| `dict[K, V]` | `map[K]V` |
| `Optional[T]` | `*T` |
| `Any` | `any` |

### TypeScript → Go

| TypeScript | Go |
|------------|-----|
| `number` | `float64` |
| `string` | `string` |
| `boolean` | `bool` |
| `Array<T>` | `[]T` |
| `Map<K, V>` | `map[K]V` |
| `Promise<T>` | `chan T` |
| `unknown` | `any` |

### Rust → Go

| Rust | Go |
|------|-----|
| `i32`, `i64` | `int32`, `int64` |
| `u32`, `u64` | `uint32`, `uint64` |
| `f32`, `f64` | `float32`, `float64` |
| `String`, `&str` | `string` |
| `Vec<T>` | `[]T` |
| `HashMap<K, V>` | `map[K]V` |
| `Option<T>` | `*T` |
| `Result<T, E>` | `(T, error)` |

## Cross-Language Gap Detection

The synthesizer detects patterns that may require manual attention:

### Python → Go (PY-GO-*)

| Gap | Description |
|-----|-------------|
| PY-GO-001 | Dynamic typing converted to explicit types |
| PY-GO-002 | Exception handling converted to error returns |
| PY-GO-003 | Generators need channel conversion |
| PY-GO-004 | Protocol/ABC converted to interface |

### TypeScript → Go (TS-GO-*)

| Gap | Description |
|-----|-------------|
| TS-GO-001 | Union types have no direct equivalent |
| TS-GO-002 | Optional properties use pointers or zero values |
| TS-GO-003 | Async/await needs goroutine/channel conversion |
| TS-GO-004 | Decorators have no equivalent |

### Rust → Go (RS-GO-*)

| Gap | Description |
|-----|-------------|
| RS-GO-001 | Ownership semantics not applicable |
| RS-GO-002 | Result type converted to multiple returns |
| RS-GO-003 | Traits converted to interfaces |
| RS-GO-004 | Macros require manual expansion |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type check
mypy ir_synthesize_golang

# Lint
ruff check ir_synthesize_golang
```

## License

MIT
