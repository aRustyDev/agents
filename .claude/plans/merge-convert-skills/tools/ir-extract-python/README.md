# ir-extract-python

Python extractor for the IR extraction/synthesis pipeline. This module transforms Python source code into a 5-layer Intermediate Representation (IR) using tree-sitter for parsing and optional semantic enrichment via jedi or pyright.

## Features

- Parse Python 3.8+ source code using tree-sitter
- Extract functions, classes, and type definitions
- Detect Python-specific patterns (comprehensions, decorators, async, pattern matching)
- Optional semantic enrichment via jedi or pyright
- Generate 5-layer IR representation
- CLI for quick extraction

## Installation

```bash
# Basic installation
pip install ir-extract-python

# With semantic enrichment (jedi)
pip install ir-extract-python[semantic]

# With full semantic enrichment (jedi + pyright support)
pip install ir-extract-python[semantic-full]

# For development
pip install ir-extract-python[dev]
```

## Quick Start

### As a Library

```python
from ir_extract_python import PythonExtractor
from ir_core.base import ExtractConfig, SemanticEnrichmentLevel

# Create extractor
extractor = PythonExtractor()

# Extract IR from source code
source = '''
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"
'''

ir = extractor.extract(source, "greeting.py", ExtractConfig())

# Access extracted information
print(f"Module: {ir.module.name}")
print(f"Functions: {[f.name for f in ir.functions]}")
print(f"Types: {[t.name for t in ir.types]}")
```

### With Semantic Enrichment

```python
from ir_core.base import ExtractConfig, SemanticEnrichmentLevel

config = ExtractConfig(
    semantic_level=SemanticEnrichmentLevel.FULL,  # Use pyright
    resolve_imports=True,
    project_root=Path("/path/to/project"),
)

ir = extractor.extract(source, "module.py", config)
```

### CLI Usage

```bash
# Extract to YAML (default)
python -m ir_extract_python module.py

# Extract to JSON
python -m ir_extract_python --format json module.py

# Extract with semantic enrichment
python -m ir_extract_python --enrich module.py

# Extract with full pyright analysis
python -m ir_extract_python --enrich --semantic-level full module.py

# Write to output file
python -m ir_extract_python -o output.yaml module.py

# Validate source without full extraction
python -m ir_extract_python --validate module.py

# Extract signatures only
python -m ir_extract_python --mode signature-only module.py

# Include expression-level details (Layer 0)
python -m ir_extract_python --include-layer0 module.py
```

## Architecture

The extractor follows the hybrid architecture from ADR-009:

```
Source Code
    |
    v
+---------------------------+
|   Tree-sitter Parser      |  Parse Python using tree-sitter-python
+---------------------------+
    |
    v
+---------------------------+
|   Python Parser           |  Extract functions, classes, imports
+---------------------------+
    |
    v
+---------------------------+
|   Semantic Enrichment     |  Add types via jedi/pyright (optional)
+---------------------------+
    |
    v
+---------------------------+
|   Pattern Matcher         |  Detect Python idioms
+---------------------------+
    |
    v
+---------------------------+
|   IR Generator            |  Build 5-layer IR
+---------------------------+
    |
    v
+---------------------------+
|   Gap Detector            |  Mark conversion challenges
+---------------------------+
```

## Python Features Extracted

### Functions
- Synchronous and async functions
- Type annotations (parameters and return)
- Decorators
- Default parameter values
- Variadic parameters (*args, **kwargs)
- Docstrings

### Classes
- Inheritance (single and multiple)
- Methods (instance, class, static)
- Properties
- Class attributes
- Dataclasses
- Protocols
- Generic classes

### Imports
- Simple imports (`import X`)
- From imports (`from X import Y`)
- Aliased imports (`import X as Y`)
- Relative imports
- Wildcard imports (detected as gaps)

### Patterns Detected
- List/dict/set comprehensions
- Generator expressions
- Decorators and decorator factories
- Context managers (with statements)
- Async patterns (async/await, async for, async with)
- Pattern matching (match/case, Python 3.10+)
- Exception handling
- Type annotations

### Gaps Identified
- Wildcard imports
- Dynamic code (exec, eval)
- Metaclasses
- Complex decorators
- Runtime namespace modification

## Semantic Enrichment

### Jedi (Basic)
- Single-file type inference
- Name resolution
- Fast and lightweight
- Default for `--enrich` flag

### Pyright (Full)
- Cross-file type resolution
- Full type system support
- Type stubs (.pyi) support
- Generic type inference

Fallback chain: pyright -> jedi -> Any

## Output Format

The extractor produces IR in the `ir-v1.0` schema format:

```yaml
version: ir-v1.0
module:
  id: "module:greeting.py"
  name: "greeting"
  imports: [...]
  definitions: [...]
  metadata:
    source_file: "greeting.py"
    source_language: "python"
    extraction_version: "ir-v1.0"
types: [...]
functions:
  - id: "func:greeting.py:0"
    name: "greet"
    params:
      - name: "name"
        type:
          kind: "named"
          type_id: "str"
    return_type:
      kind: "named"
      type_id: "str"
    effects:
      - kind: "pure"
        source: "inferred"
gaps: [...]
annotations: [...]
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=ir_extract_python

# Type check
mypy ir_extract_python

# Lint
ruff check ir_extract_python

# Format
black ir_extract_python
```

## License

MIT
