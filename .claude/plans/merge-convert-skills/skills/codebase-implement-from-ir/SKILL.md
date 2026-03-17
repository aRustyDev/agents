---
name: Implement from IR
version: 1.0.0
description: Synthesize target language code from IR
category: conversion
languages: [python, typescript, rust, java, go, scala, roc, kotlin, swift, elixir]
tools: [ir-synthesize-python, ir-synthesize-rust, ir-synthesize-typescript, ir-synthesize-go, ir-synthesize-scala, ir-synthesize-roc]
---

# Implement from IR

Generate idiomatic code in a target language from an Intermediate Representation (IR).

## Usage

```
/codebase-implement-from-ir <ir-path> --target <language> [--style <mode>] [--gaps <handling>]
```

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ir-path` | Path to IR file (JSON/YAML) | Required |
| `--target` | Target language | Required |
| `--style` | Generation style (minimal, idiomatic, verbose) | idiomatic |
| `--gaps` | Gap handling (warn, error, annotate, ignore) | warn |

## Process

### 1. IR Validation

Validate the input IR:
- Schema compliance
- Required fields present
- Internal consistency (referenced types exist)

### 2. Gap Resolution

Review detected gaps and apply mitigations:

| Gap Severity | Default Action |
|--------------|----------------|
| Critical | Halt, require human decision |
| High | Warn, suggest alternatives |
| Medium | Auto-convert with TODO comment |
| Low | Auto-convert silently |
| Info | Log for reference |

### 3. Pattern Translation

Map IR patterns to target idioms:

#### Type Mappings

| Source | Python | Rust | TypeScript | Go | Scala |
|--------|--------|------|------------|-----|-------|
| `int` | `int` | `i64` | `number` | `int64` | `Long` |
| `str` | `str` | `String` | `string` | `string` | `String` |
| `bool` | `bool` | `bool` | `boolean` | `bool` | `Boolean` |
| `Option[T]` | `Optional[T]` | `Option<T>` | `T \| undefined` | `*T` | `Option[T]` |
| `Result[T,E]` | `Result[T,E]` | `Result<T,E>` | `Result<T,E>` | `(T, error)` | `Either[E,T]` |
| `List[T]` | `list[T]` | `Vec<T>` | `T[]` | `[]T` | `List[T]` |
| `Dict[K,V]` | `dict[K,V]` | `HashMap<K,V>` | `Map<K,V>` | `map[K]V` | `Map[K,V]` |

#### Pattern Mappings

| Pattern | Source IR | Target Transformation |
|---------|-----------|----------------------|
| Pattern Match | `MatchExpression` | switch/if-else chain (if needed) |
| ADT | `TypeDef.adt` | sealed class/enum |
| Type Class | `TypeClassDef` | trait/interface + instances |
| Async | `AsyncAnnotation` | async/await, Future, goroutine |
| Error Handling | `ResultType` | Result, Either, (T, error) |

### 4. Code Generation

Generate syntactically correct code:
- Proper indentation and formatting
- Valid identifier names
- Correct import statements
- Appropriate module structure

### 5. Idiom Application

Apply target-language conventions:
- Naming conventions (snake_case, camelCase, PascalCase)
- Documentation style (docstrings, JSDoc, rustdoc)
- Error handling idioms
- Common patterns (builder, factory, etc.)

### 6. Formatting

Format code with target's standard tools:
- Python: `black`, `ruff`
- Rust: `rustfmt`
- TypeScript: `prettier`
- Go: `gofmt`
- Scala: `scalafmt`

## Output

### Generated Code Structure

```
output/
├── src/
│   ├── models.{ext}      # Type definitions
│   ├── services.{ext}    # Functions and methods
│   └── utils.{ext}       # Helper functions
├── tests/
│   └── test_models.{ext} # Generated test stubs
├── Cargo.toml            # (Rust) Package manifest
├── pyproject.toml        # (Python) Package manifest
└── GAPS.md               # Gap resolution notes
```

### Gap Resolution Report

```markdown
# Gap Resolution Report

## Critical Gaps (Require Human Decision)

### 1. Higher-Kinded Types (SC-001)
- **Source**: `Functor[F[_]]` in `types.scala`
- **Target**: TypeScript
- **Issue**: TypeScript cannot express HKT
- **Options**:
  1. Monomorphize to specific types (List, Option, etc.)
  2. Use type-level programming with conditional types
  3. Simplify to concrete implementation

## High Severity Gaps (Auto-Converted with Warning)

### 1. Ownership Transfer (RS-001)
- **Source**: `fn take(self)` in `entity.rs`
- **Target**: Python
- **Resolution**: Converted to normal method, added runtime validation
```

## Semantic Preservation Levels

Target these levels in order of priority:

### 1. Semantically Equivalent
Same observable behavior in all cases:
- Pure functions map directly
- Immutable data structures preserve semantics
- Error handling maintains all cases

### 2. Idiomatically Correct
Follows target conventions even if slightly different:
- Use target-native collections
- Apply target naming conventions
- Use target error handling patterns

### 3. Optimized
Efficient for target platform:
- Use target-specific optimizations
- Leverage platform features
- Minimize overhead from conversion

## Examples

### Synthesize Rust from Python IR

```bash
/codebase-implement-from-ir analysis.ir.json --target rust
```

### Synthesize with verbose style

```bash
/codebase-implement-from-ir analysis.ir.json --target python --style verbose
```

### Strict gap handling

```bash
/codebase-implement-from-ir analysis.ir.json --target go --gaps error
```

## Reference

- [Synthesis Guide](reference/synthesis-guide.md)
- [Pattern Translations](reference/patterns/)
- [Target Languages](reference/targets/)

### Target-Specific Guides

- [Rust Target](reference/targets/rust/idioms.md)
- [Python Target](reference/targets/python/idioms.md)
- [TypeScript Target](reference/targets/typescript/idioms.md)
- [Go Target](reference/targets/go/idioms.md)
- [Scala Target](reference/targets/scala/idioms.md)
- [Roc Target](reference/targets/roc/idioms.md)

## Related Skills

- [codebase-analysis](../codebase-analysis/SKILL.md) - Extract IR from source
- [idiomatic-rust](../idiomatic-rust/SKILL.md) - Rust-specific idioms
- [idiomatic-python](../idiomatic-python/SKILL.md) - Python-specific idioms
