# IR Synthesize Python

Python code synthesizer for the IR extraction/synthesis pipeline. Generates idiomatic Python source code from the intermediate representation (IR).

## Overview

This package transforms IR (extracted from source code) back into Python source code. It supports:

- **Multiple preservation levels**: L1 (correct), L2 (idiomatic), L3 (optimized)
- **Type annotations**: Full support for Python 3.11+ type hints
- **Idiomatic patterns**: Comprehensions, context managers, dataclasses, async/await
- **Code formatting**: Optional integration with black and ruff
- **Gap tracking**: Reports synthesis issues that may require attention

## Installation

```bash
# With pip
pip install ir-synthesize-python

# With uv
uv add ir-synthesize-python

# With formatting support
pip install ir-synthesize-python[format]

# With all dependencies (including dev)
pip install ir-synthesize-python[all]
```

## Quick Start

### Python API

```python
from ir_synthesize_python import PythonSynthesizer
from ir_core import SynthConfig, OutputFormat

# Create synthesizer
synthesizer = PythonSynthesizer()

# Configure synthesis
config = SynthConfig(
    output_format=OutputFormat.FORMATTED,
    emit_type_hints=True,
    emit_docstrings=True,
    target_version="3.11",
    custom_options={
        "preservation_mode": "idiomatic",
    },
)

# Synthesize code from IR
code = synthesizer.synthesize(ir, config)

# Check for synthesis gaps
for gap in synthesizer.last_gaps:
    print(f"[{gap.severity.value}] {gap.description}")
```

### Command Line

```bash
# Synthesize from IR file
python -m ir_synthesize_python extracted.yaml

# With formatting
python -m ir_synthesize_python --format extracted.yaml

# Output to file
python -m ir_synthesize_python --output module.py extracted.yaml

# Use idiomatic preservation level
python -m ir_synthesize_python --level idiomatic extracted.yaml

# Show synthesis gaps
python -m ir_synthesize_python --show-gaps extracted.yaml

# Dry run (show what would be generated)
python -m ir_synthesize_python --dry-run extracted.yaml
```

## Preservation Levels

The synthesizer supports three preservation levels:

| Level | Name | Description |
|-------|------|-------------|
| L1 | Correct | Generate valid, compilable Python code |
| L2 | Idiomatic | Use native Python patterns and conventions |
| L3 | Optimized | Apply performance optimizations |

### L1: Correct

Basic code generation that produces valid Python. Minimal transformation, preserves structure from IR.

### L2: Idiomatic

Generates idiomatic Python code:
- List/dict/set comprehensions instead of loops
- Dataclasses instead of plain classes
- Context managers for resource handling
- F-strings for formatting
- Pattern matching (Python 3.10+)

### L3: Optimized

Applies performance optimizations:
- Generator expressions for memory efficiency
- `__slots__` for memory-efficient classes
- Inline simple functions
- Use built-in functions where appropriate

## Features

### Type Annotations

Full support for Python type hints:

```python
# Generic types
def process(items: list[str]) -> dict[str, int]: ...

# Union types (Python 3.10+ syntax)
def handle(value: str | int | None) -> bool: ...

# Callable types
def apply(func: Callable[[int], str]) -> str: ...

# Tuple types
def unpack(data: tuple[str, int, float]) -> None: ...
```

### Idiomatic Patterns

The synthesizer generates idiomatic Python patterns:

```python
# List comprehension
squares = [x ** 2 for x in range(10) if x > 0]

# Dict comprehension
name_lengths = {name: len(name) for name in names}

# Context manager
with open(path) as f:
    data = f.read()

# Dataclass
@dataclass
class Point:
    x: float
    y: float

# Async/await
async def fetch(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async for chunk in response.content.iter_any():
            yield chunk
```

### Code Formatting

Optional integration with formatting tools:

```python
# Using black (library)
from ir_synthesize_python import PythonFormatter

formatter = PythonFormatter(use_black=True, line_length=88)
formatted = formatter.format(code)

# Using ruff (subprocess)
formatter = PythonFormatter(use_ruff=True)
formatted = formatter.format(code)
```

## Architecture

```
ir-synthesize-python/
+-- __init__.py          # Public API exports
+-- synthesizer.py       # Main PythonSynthesizer class
+-- generator.py         # Code construct generation
+-- formatter.py         # Code formatting utilities
+-- idioms.py            # Idiomatic pattern generation
+-- __main__.py          # CLI entry point
+-- tests/
    +-- test_synthesizer.py
    +-- test_generator.py
    +-- test_idioms.py
    +-- test_roundtrip.py  # Round-trip tests with extractor
```

### Key Classes

- **PythonSynthesizer**: Main synthesizer class extending `ir_core.Synthesizer`
- **PythonCodeGenerator**: Generates Python code constructs from IR
- **PythonFormatter**: Formats code using black/ruff
- **PythonIdiomGenerator**: Generates idiomatic Python patterns

## Round-Trip Testing

The package includes round-trip tests with `ir-extract-python` to verify L3 (semantic) equivalence:

```python
# Extract Python to IR
extractor = PythonExtractor()
ir = extractor.extract(source_code, "module.py", extract_config)

# Synthesize back to Python
synthesizer = PythonSynthesizer()
generated = synthesizer.synthesize(ir, synth_config)

# Verify behavior matches
assert exec_function(source_code, "func", args) == exec_function(generated, "func", args)
```

Run round-trip tests:

```bash
pytest tests/test_roundtrip.py -m roundtrip
```

## Gap Handling

The synthesizer tracks and reports synthesis gaps:

```python
synthesizer.synthesize(ir, config)

for gap in synthesizer.last_gaps:
    print(f"Gap: {gap.id}")
    print(f"  Type: {gap.gap_type.value}")
    print(f"  Severity: {gap.severity.value}")
    print(f"  Description: {gap.description}")
    print(f"  Source concept: {gap.source_concept}")
    print(f"  Target concept: {gap.target_concept}")
```

## Configuration Options

### SynthConfig Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `output_format` | OutputFormat | SOURCE | Format for output |
| `line_length` | int | 88 | Maximum line length |
| `emit_type_hints` | bool | True | Include type annotations |
| `emit_docstrings` | bool | True | Include docstrings |
| `target_version` | str | None | Target Python version |

### Custom Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `preservation_mode` | str | "idiomatic" | Preservation level |

## Requirements

- Python 3.11+
- ir-core >= 0.1.0
- PyYAML >= 6.0

Optional:
- black >= 24.0.0 (for formatting)
- ruff >= 0.2.0 (for formatting)
- ir-extract-python >= 0.1.0 (for round-trip tests)

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=ir_synthesize_python

# Type checking
mypy ir_synthesize_python

# Linting
ruff check ir_synthesize_python
```

## See Also

- [ir-core](../ir-core/): Core IR models and base classes
- [ir-extract-python](../ir-extract-python/): Python extractor
- [Equivalence Levels](../../docs/src/validation/equivalence-levels.md): Semantic equivalence specification

## License

MIT
