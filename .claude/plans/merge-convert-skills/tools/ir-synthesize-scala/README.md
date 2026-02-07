# ir-synthesize-scala

Scala source code synthesizer for the IR extraction/synthesis pipeline.

## Overview

This package generates idiomatic Scala source code from the 5-layer IR representation:

- **Case classes**: Product types with automatic methods
- **Sealed traits**: Sum types for exhaustive matching
- **Higher-kinded types**: F[_] and type constructors
- **Variance**: Covariant (+T) and contravariant (-T)
- **Given instances**: Type class instances (Scala 3)
- **For comprehensions**: Monadic composition
- **Pattern matching**: Exhaustive matching

## Installation

```bash
pip install ir-synthesize-scala
```

## Usage

### CLI

```bash
# Synthesize from IR file
ir-synthesize-scala ir-output.yaml

# Output to file
ir-synthesize-scala ir-output.yaml -o generated.scala
```

### API

```python
from ir_synthesize_scala import ScalaSynthesizer
from ir_core.base import SynthConfig
from ir_core.models import IRVersion, TypeDef, TypeKind, FunctionDef, Parameter

# Create IR
ir = IRVersion(
    version="ir-v1.0",
    source_language="python",
    source_path="example.py",
)

# Add a case class
ir.types.append(TypeDef(
    name="User",
    kind=TypeKind.STRUCT,
    properties=[
        {"name": "name", "type": "String"},
        {"name": "age", "type": "Int"},
    ],
))

# Add a function
ir.functions.append(FunctionDef(
    name="double",
    parameters=[Parameter(name="n", type_annotation="Int")],
    return_type="Int",
))

# Synthesize
synthesizer = ScalaSynthesizer()
config = SynthConfig()
code = synthesizer.synthesize(ir, config)
print(code)
```

## Type Mapping

### Python → Scala

| Python | Scala |
|--------|-------|
| `int` | `Int` |
| `float` | `Double` |
| `str` | `String` |
| `bool` | `Boolean` |
| `bytes` | `Array[Byte]` |
| `list[T]` | `List[T]` |
| `dict[K, V]` | `Map[K, V]` |
| `Optional[T]` | `Option[T]` |

### Rust → Scala

| Rust | Scala |
|------|-------|
| `i32`, `i64` | `Int`, `Long` |
| `f32`, `f64` | `Float`, `Double` |
| `String` | `String` |
| `Vec<T>` | `List[T]` |
| `HashMap<K, V>` | `Map[K, V]` |
| `Option<T>` | `Option[T]` |
| `Result<T, E>` | `Either[E, T]` |

### TypeScript → Scala

| TypeScript | Scala |
|------------|-------|
| `number` | `Double` |
| `string` | `String` |
| `boolean` | `Boolean` |
| `Array<T>` | `List[T]` |
| `Promise<T>` | `Future[T]` |

### Go → Scala

| Go | Scala |
|----|-------|
| `int64` | `Long` |
| `float64` | `Double` |
| `string` | `String` |
| `[]T` | `List[T]` |
| `map[K]V` | `Map[K, V]` |
| `error` | `Throwable` |

### Roc → Scala

| Roc | Scala |
|-----|-------|
| `I64` | `Long` |
| `F64` | `Double` |
| `Str` | `String` |
| `Bool` | `Boolean` |
| `List T` | `List[T]` |
| `Task T E` | `IO[T]` (cats-effect) |

## Cross-Language Gap Detection

### Python → Scala (PY-SC-*)

| Gap | Description |
|-----|-------------|
| PY-SC-001 | Dynamic typing → explicit types |
| PY-SC-002 | Duck typing → traits |
| PY-SC-003 | Exceptions → Either/Try |

### TypeScript → Scala (TS-SC-*)

| Gap | Description |
|-----|-------------|
| TS-SC-001 | Union types → sealed traits |
| TS-SC-002 | null/undefined → Option |
| TS-SC-003 | Structural typing → nominal |

### Rust → Scala (RS-SC-*)

| Gap | Description |
|-----|-------------|
| RS-SC-001 | Ownership → GC |
| RS-SC-002 | Lifetimes → N/A |
| RS-SC-003 | Trait objects → HKT |

### Go → Scala (GO-SC-*)

| Gap | Description |
|-----|-------------|
| GO-SC-001 | Multiple returns → tuples |
| GO-SC-002 | Error return → Either/Try |
| GO-SC-003 | Goroutines → Future/Actors |
| GO-SC-004 | Interfaces → traits |

### Roc → Scala (ROC-SC-*)

| Gap | Description |
|-----|-------------|
| ROC-SC-001 | Task effects → IO monad |
| ROC-SC-002 | Tag unions → sealed traits |
| ROC-SC-003 | Abilities → type classes |

## Development

```bash
pip install -e ".[dev]"
pytest
mypy ir_synthesize_scala
```

## License

MIT
