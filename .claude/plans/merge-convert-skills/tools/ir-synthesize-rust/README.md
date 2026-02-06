# ir-synthesize-rust

Rust source code synthesizer for the IR conversion pipeline.

## Overview

This package synthesizes Rust source code from the 5-layer IR representation,
generating borrow-checker-valid output with proper:

- **Ownership**: Chooses between owned, borrowed, and mutable borrows
- **Lifetimes**: Infers or generates explicit lifetime annotations
- **Idioms**: Uses Result, Option, iterators, and other Rust patterns
- **Formatting**: Integrates with rustfmt for clean output

## Installation

```bash
pip install ir-synthesize-rust
```

## Usage

### CLI

```bash
# Synthesize from IR JSON
python -m ir_synthesize_rust input.json

# Output to file
python -m ir_synthesize_rust input.json -o output.rs

# With options
python -m ir_synthesize_rust input.json --edition 2021 --format formatted
```

### Python API

```python
from ir_synthesize_rust import RustSynthesizer
from ir_core.base import SynthConfig, OutputFormat

synthesizer = RustSynthesizer()
code = synthesizer.synthesize(ir, SynthConfig(
    output_format=OutputFormat.FORMATTED,
    target_version="2021",
))

print(code)

# Check for synthesis gaps
for gap in synthesizer.last_gaps:
    print(f"Gap: {gap.description}")
```

## Features

### Ownership Planning

The synthesizer automatically chooses ownership modes:

```python
# IR with parameter type
param:
  name: data
  type: Vec<i32>

# Synthesizer decides:
# - &Vec<i32> if only read
# - &mut Vec<i32> if modified
# - Vec<i32> if consumed
```

### Lifetime Inference

Applies Rust lifetime elision rules:

```rust
// Single input reference → elide output lifetime
fn first(&self) -> &str { ... }

// Multiple references → may need explicit lifetimes
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str { ... }
```

### Type Mapping

Maps IR types to idiomatic Rust:

| IR Type | Rust Type |
|---------|-----------|
| `builtins.int` | `i64` |
| `builtins.float` | `f64` |
| `builtins.str` | `String` |
| `builtins.list` | `Vec<T>` |
| `builtins.dict` | `HashMap<K, V>` |
| `typing.Optional` | `Option<T>` |

### Format Integration

Supports rustfmt for consistent formatting:

```python
config = SynthConfig(
    output_format=OutputFormat.FORMATTED,
    line_length=100,
    indent_size=4,
)
```

## Gap Handling

The synthesizer reports gaps for constructs that:

- Require ownership decisions
- Need explicit lifetimes
- Use patterns without Rust equivalent
- Contain unsafe operations

```python
for gap in synthesizer.last_gaps:
    if gap.severity == Severity.CRITICAL:
        print(f"Cannot convert: {gap.description}")
    elif gap.severity == Severity.HIGH:
        print(f"Manual review needed: {gap.description}")
```

## Rust Edition Support

Supports Rust editions:
- 2015 (legacy)
- 2018
- 2021 (default)

```python
config = SynthConfig(target_version="2021")
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy ir_synthesize_rust

# Linting
ruff check .
```

## Architecture

```
ir_synthesize_rust/
├── __init__.py       # Package exports
├── __main__.py       # CLI entry point
├── synthesizer.py    # Main synthesizer implementation
├── generator.py      # Code generation
├── ownership.py      # Ownership planning
├── formatter.py      # rustfmt integration
└── tests/
    └── test_generator.py
```
