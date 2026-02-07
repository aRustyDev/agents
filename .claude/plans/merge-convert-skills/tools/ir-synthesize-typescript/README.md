# ir-synthesize-typescript

TypeScript source code synthesizer for the IR conversion pipeline.

## Overview

This package synthesizes TypeScript source code from the 5-layer IR representation,
generating borrow-checker-valid output with proper:

- **Type annotations**: Full type safety with generics
- **Interfaces and types**: Proper structural typing
- **Classes**: With decorators and access modifiers
- **Formatting**: Integrates with prettier for clean output

## Installation

```bash
pip install ir-synthesize-typescript
```

## Usage

### CLI

```bash
# Synthesize from IR JSON
python -m ir_synthesize_typescript input.json

# Output to file
python -m ir_synthesize_typescript input.json -o output.ts

# With options
python -m ir_synthesize_typescript input.json --format formatted --line-length 80
```

### Python API

```python
from ir_synthesize_typescript import TypeScriptSynthesizer
from ir_core.base import SynthConfig, OutputFormat

synthesizer = TypeScriptSynthesizer()
code = synthesizer.synthesize(ir, SynthConfig(
    output_format=OutputFormat.FORMATTED,
    target_version="ES2022",
))

print(code)

# Check for synthesis gaps
for gap in synthesizer.last_gaps:
    print(f"Gap: {gap.description}")
```

## Features

### Type Generation

Maps IR types to idiomatic TypeScript:

| IR Type | TypeScript Type |
|---------|--------------------|
| `int` | `number` |
| `float` | `number` |
| `str` | `string` |
| `bool` | `boolean` |
| `list` | `Array<T>` |
| `dict` | `Record<K, V>` |
| `Optional` | `T \| null` |

### Interface Generation

```typescript
// From IR interface definition
export interface User<T extends object = {}> {
  readonly id: number;
  name: string;
  email?: string;
  metadata: T;
}
```

### Class Generation

```typescript
// From IR class definition
export class UserService {
  private api: ApiClient;

  constructor(api: ApiClient) {
    this.api = api;
  }

  async getUser(id: number): Promise<User> {
    // Method implementation
  }
}
```

### Format Integration

Supports prettier for consistent formatting:

```python
config = SynthConfig(
    output_format=OutputFormat.FORMATTED,
    line_length=100,
    indent_size=2,
)
```

## Gap Handling

The synthesizer reports gaps for constructs that:

- Have no direct TypeScript equivalent
- Require type annotations
- Lose semantic information

```python
for gap in synthesizer.last_gaps:
    if gap.severity == Severity.CRITICAL:
        print(f"Cannot convert: {gap.description}")
    elif gap.severity == Severity.HIGH:
        print(f"Manual review needed: {gap.description}")
```

### Cross-Language Gaps

| From | Gap Code | Description |
|------|----------|-------------|
| Python | PY-TS-001 | Missing type annotation |
| Python | PY-TS-002 | Missing return type |
| Python | PY-TS-003 | *args/**kwargs conversion |
| Rust | RS-TS-001 | Ownership semantics lost |
| Rust | RS-TS-002 | Lifetime annotation lost |
| Rust | RS-TS-003 | Result type conversion |
| Rust | RS-TS-004 | Option type conversion |

## ES Version Support

Supports ECMAScript versions:
- ES2015 (ES6)
- ES2016-ES2021
- ES2022 (default)
- ESNext

```python
config = SynthConfig(target_version="ES2022")
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy ir_synthesize_typescript

# Linting
ruff check .
```

## Architecture

```
ir_synthesize_typescript/
├── __init__.py       # Package exports
├── __main__.py       # CLI entry point
├── synthesizer.py    # Main synthesizer implementation
├── generator.py      # Code generation
├── formatter.py      # Prettier integration
└── tests/
    └── test_generator.py
```
