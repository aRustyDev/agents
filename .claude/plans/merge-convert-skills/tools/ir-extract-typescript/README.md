# ir-extract-typescript

TypeScript source code extractor for the IR conversion pipeline.

## Overview

This package extracts TypeScript source code into the 5-layer IR representation,
with special handling for TypeScript-specific concepts:

- **Structural typing**: Captures interface and type alias definitions
- **Union and intersection types**: Preserves complex type compositions
- **Generic constraints**: Extracts type parameters with bounds and defaults
- **Interface extensions**: Tracks inheritance relationships
- **Decorators**: Records decorator usage for classes and methods

## Installation

```bash
pip install ir-extract-typescript
# or with tree-sitter
pip install ir-extract-typescript[dev]
```

## Usage

### CLI

```bash
# Extract to stdout
python -m ir_extract_typescript path/to/file.ts

# Extract to file
python -m ir_extract_typescript path/to/file.ts -o output.json

# With options
python -m ir_extract_typescript file.ts --pretty --spans --semantic full
```

### Python API

```python
from ir_extract_typescript import TypeScriptExtractor
from ir_core.base import ExtractConfig

extractor = TypeScriptExtractor()
ir = extractor.extract(typescript_source, "example.ts", ExtractConfig())

# Access extracted data
for type_def in ir.types:
    print(f"Type: {type_def.name} ({type_def.kind})")

for func in ir.functions:
    print(f"Function: {func.name}")

# Check for extraction gaps
for gap in ir.gaps:
    print(f"Gap: {gap.description}")
```

## Layers Extracted

### Layer 4: Module Structure
- Import statements (default, named, namespace, type-only)
- Export statements
- Module declarations

### Layer 3: Type System
- Interfaces with properties, methods, index signatures
- Type aliases (including union, intersection, conditional)
- Enums (regular and const)
- Classes with inheritance and decorators
- Generic type parameters with constraints

### Layer 2: Control Flow
- Functions and arrow functions
- Async functions and generators
- Method definitions

### Layer 1: Data Flow (Future)
- Variable declarations
- Assignment tracking

### Layer 0: Expressions (Optional)
- Full AST for detailed analysis
- Enabled with `include_layer0=True`

## TypeScript-Specific Annotations

The extractor adds semantic annotations for TypeScript concepts:

```yaml
annotations:
  - kind: "TS-004"  # Structural typing
    target: "type:0"
    value:
      typing: structural

  - kind: "TS-006"  # Type inference
    target: "var:config"
    value:
      inferred: true

  - kind: "TS-009"  # Union types
    target: "type:1"
    value:
      union_members: ["string", "number"]
```

## Gap Detection

The extractor identifies potential conversion issues:

| Gap Code | Description |
|----------|-------------|
| TS-010 | Conditional types |
| TS-011 | Mapped types |
| TS-012 | Template literal types |
| TS-013 | Decorators |
| TS-014 | Function overloads |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy ir_extract_typescript

# Linting
ruff check .
```

## Architecture

```
ir_extract_typescript/
├── __init__.py       # Package exports
├── __main__.py       # CLI entry point
├── extractor.py      # Main extractor implementation
├── parser.py         # Tree-sitter based parser
├── types.py          # Type system analysis
└── tests/
    ├── test_parser.py
    └── test_types.py
```
