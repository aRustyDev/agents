# ir-extract-rust

Rust source code extractor for the IR conversion pipeline.

## Overview

This package extracts Rust source code into the 5-layer IR representation,
with special handling for Rust-specific concepts:

- **Ownership semantics**: Tracks owned values, borrows, and moves
- **Lifetime annotations**: Extracts explicit and elided lifetimes
- **Borrow checker constraints**: Records borrow relationships
- **Trait bounds**: Captures generic constraints and where clauses

## Installation

```bash
pip install ir-extract-rust
# or with tree-sitter
pip install ir-extract-rust[dev]
```

## Usage

### CLI

```bash
# Extract to stdout
python -m ir_extract_rust path/to/file.rs

# Extract to file
python -m ir_extract_rust path/to/file.rs -o output.json

# With options
python -m ir_extract_rust file.rs --pretty --spans --semantic full
```

### Python API

```python
from ir_extract_rust import RustExtractor
from ir_core.base import ExtractConfig

extractor = RustExtractor()
ir = extractor.extract(rust_source, "example.rs", ExtractConfig())

# Access extracted data
for func in ir.functions:
    print(f"Function: {func.name}")

for type_def in ir.types:
    print(f"Type: {type_def.name} ({type_def.kind})")

# Check for extraction gaps
for gap in ir.gaps:
    print(f"Gap: {gap.description}")
```

## Layers Extracted

### Layer 4: Module Structure
- `mod` declarations and visibility
- `use` statements and re-exports
- Public API surface

### Layer 3: Type System
- Structs (regular, tuple, unit)
- Enums (unit, tuple, struct variants)
- Traits and impl blocks
- Generic type parameters with bounds

### Layer 2: Control Flow
- Functions and methods
- Async functions
- Unsafe blocks
- Pattern matching

### Layer 1: Data Flow
- Ownership tracking (owned, borrowed, moved)
- Lifetime annotations
- Move vs copy semantics
- Borrow relationships

### Layer 0: Expressions (Optional)
- Full AST for detailed analysis
- Enabled with `include_layer0=True`

## Ownership Annotations

The extractor adds semantic annotations for ownership:

```yaml
annotations:
  - kind: "MM-002"  # Ownership
    target: "func:1:param:data"
    value:
      ownership: "borrowed"
      lifetime: "a"

  - kind: "MM-009"  # Move vs Copy
    target: "func:2"
    value:
      semantics: "move"

  - kind: "MM-010"  # Lifetimes
    target: "func:3"
    value:
      params: ["a", "b"]
      constraints:
        - short: "b"
          long: "a"
```

## Gap Detection

The extractor identifies potential issues:

- Use-after-move errors
- Borrow conflicts
- Lifetime elision ambiguity
- Unsafe code blocks

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy ir_extract_rust

# Linting
ruff check .
```

## Architecture

```
ir_extract_rust/
├── __init__.py       # Package exports
├── __main__.py       # CLI entry point
├── extractor.py      # Main extractor implementation
├── parser.py         # Tree-sitter based parser
├── ownership.py      # Ownership analysis
├── lifetimes.py      # Lifetime extraction
└── tests/
    ├── test_parser.py
    └── test_ownership.py
```
