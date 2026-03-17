# Synthesis Guide

Step-by-step guide for synthesizing target language code from IR.

## Overview

Synthesis transforms a language-agnostic IR into idiomatic code for a target language while resolving semantic gaps and applying language conventions.

## Synthesis Process

### Phase 1: IR Validation

Validate input IR before synthesis:

```python
from ir_core.validation import validate_ir

errors = validate_ir(ir)
if any(e.severity == 'critical' for e in errors):
    raise ValidationError("IR has critical issues")
```

Check for:
- Schema compliance
- Required fields
- Reference resolution
- Internal consistency

### Phase 2: Gap Analysis

Review all annotations for semantic gaps:

```python
from ir_synthesize_python import PythonSynthesizer

synthesizer = PythonSynthesizer()
gaps = synthesizer.detect_cross_language_gaps(ir, "python")

for gap in gaps:
    if gap.severity == "critical":
        print(f"REQUIRES DECISION: {gap.message}")
        print(f"  Options: {gap.suggestion}")
```

### Phase 3: Gap Resolution

For each gap severity:

| Severity | Action |
|----------|--------|
| Critical | Halt, present options to user |
| High | Generate with TODO comment |
| Medium | Auto-convert with inline comment |
| Low | Auto-convert silently |
| Info | Log for reference |

Example resolution:

```python
# CRITICAL: Rust ownership pattern detected
# Original: fn consume(self) -> Result
# Options:
#   1. Clone before use (performance impact)
#   2. Use reference (behavior change)
#   3. Restructure to builder pattern

# CHOSEN: Clone before use
def consume(self) -> Result:
    # NOTE: Cloned from Rust ownership pattern
    copy = self._deep_copy()
    return self._process(copy)
```

### Phase 4: Type Translation

Map IR types to target language types:

```python
TYPE_MAP = {
    # Primitives
    "Int": "int",
    "Float": "float",
    "String": "str",
    "Bool": "bool",

    # Composites
    "Option[T]": "Optional[T]",
    "Result[T,E]": "Result[T, E]",  # or custom Result type
    "List[T]": "list[T]",
    "Dict[K,V]": "dict[K, V]",

    # Functions
    "Fn(A,B)->C": "Callable[[A, B], C]",
}
```

### Phase 5: Pattern Translation

Map IR patterns to target idioms:

| IR Pattern | Python Target |
|------------|---------------|
| `MatchExpression` | `match` statement (3.10+) or if/elif chain |
| `ADTDef` | `@dataclass` with union type |
| `OptionType` | `Optional[T]` or `T \| None` |
| `ResultType` | Custom Result class or exceptions |
| `AsyncAnnotation` | `async def` |

### Phase 6: Code Generation

Generate syntactically correct code:

```python
def generate_function(func: FunctionDef) -> str:
    # Parameters
    params = [f"{p.name}: {translate_type(p.type)}"
              for p in func.parameters]

    # Return type
    ret = f" -> {translate_type(func.return_type)}" if func.return_type else ""

    # Async prefix
    prefix = "async " if func.async else ""

    # Body
    body = generate_body(func.body)

    return f"{prefix}def {func.name}({', '.join(params)}){ret}:\n{body}"
```

### Phase 7: Idiom Application

Apply target-language conventions:

| Convention | Application |
|------------|-------------|
| Naming | snake_case for functions, PascalCase for classes |
| Docstrings | Google-style or NumPy-style |
| Imports | Group stdlib, third-party, local |
| Type hints | Use modern syntax (3.10+) |
| Error handling | Exceptions or Result pattern |

### Phase 8: Formatting

Apply standard formatting:

```python
import subprocess

def format_code(code: str, language: str) -> str:
    if language == "python":
        return subprocess.run(
            ["black", "-"],
            input=code,
            capture_output=True,
            text=True
        ).stdout
```

## Target-Specific Strategies

### Python Target

**Type Mapping**:
```python
"Int" → "int"
"Option[T]" → "T | None"
"Result[T,E]" → "T"  # with exception for error
"List[T]" → "list[T]"
```

**Pattern Mapping**:
- ADT → `@dataclass` with `__match_args__`
- Pattern match → `match` statement
- Type class → Protocol + runtime check

**Idioms**:
- Use type hints everywhere
- Prefer `dataclass` over plain class
- Use `contextlib` for resource management

### Rust Target

**Type Mapping**:
```rust
"Int" → "i64"
"Option[T]" → "Option<T>"
"Result[T,E]" → "Result<T, E>"
"List[T]" → "Vec<T>"
```

**Pattern Mapping**:
- Class → `struct` + `impl`
- Interface → `trait`
- Nullable → `Option<T>`

**Idioms**:
- Ownership by default
- `?` for error propagation
- `impl Trait` for generic returns

### TypeScript Target

**Type Mapping**:
```typescript
"Int" → "number"
"Option[T]" → "T | undefined"
"Result[T,E]" → "Result<T, E>"
"List[T]" → "T[]"
```

**Pattern Mapping**:
- ADT → `type` union with discriminator
- Pattern match → `switch` with type guards
- Interface → `interface`

**Idioms**:
- Strict mode
- Immutable by default (`readonly`)
- Use discriminated unions

### Go Target

**Type Mapping**:
```go
"Int" → "int64"
"Option[T]" → "*T"
"Result[T,E]" → "(T, error)"
"List[T]" → "[]T"
```

**Pattern Mapping**:
- Class → `struct` + methods
- Interface → `interface`
- Error → explicit return

**Idioms**:
- Error handling: `if err != nil`
- Short variable names
- Composition over inheritance

### Scala Target

**Type Mapping**:
```scala
"Int" → "Int"
"Option[T]" → "Option[T]"
"Result[T,E]" → "Either[E, T]"
"List[T]" → "List[T]"
```

**Pattern Mapping**:
- Class → `case class`
- Interface → `trait`
- ADT → `sealed trait` + `case class`

**Idioms**:
- Immutability default
- For comprehensions for monadic operations
- Type classes via implicits/givens

## Output Structure

### Single File

```python
# Generated by ir-synthesize-python
# Source: auth.rs

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    name: str
    email: str

def authenticate(username: str, password: str) -> Optional[User]:
    """Authenticate user and return User if successful."""
    # TODO: Implement authentication logic
    ...
```

### Multi-File Project

```
output/
├── src/
│   ├── __init__.py
│   ├── models.py      # Type definitions
│   ├── services.py    # Business logic
│   └── utils.py       # Helpers
├── tests/
│   ├── __init__.py
│   └── test_models.py # Test stubs
├── pyproject.toml     # Package config
└── GAPS.md           # Gap resolution notes
```

## Quality Checklist

Before finalizing output:

- [ ] All types have valid mappings
- [ ] All functions have proper signatures
- [ ] Gap resolutions are documented
- [ ] Code passes syntax check
- [ ] Formatting applied
- [ ] Imports are complete
- [ ] Tests are generated (if requested)
