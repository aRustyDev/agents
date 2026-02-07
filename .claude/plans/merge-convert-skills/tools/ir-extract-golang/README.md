# ir-extract-golang

Go source code extractor for the IR extraction/synthesis pipeline.

## Overview

This package extracts Go source code into the 5-layer IR representation, with special handling for Go-specific concepts:

- **Error handling**: Multiple return values with error as the last value
- **Concurrency**: Goroutines and channels (CSP model)
- **Defer statements**: Resource cleanup patterns
- **Interfaces**: Structural typing (implicit satisfaction)
- **Generics**: Go 1.18+ type parameters

## Installation

```bash
pip install ir-extract-golang
```

## Usage

### CLI

```bash
# Extract to YAML (default)
ir-extract-golang path/to/file.go

# Extract to JSON
ir-extract-golang path/to/file.go -f json

# Output to file
ir-extract-golang path/to/file.go -o output.yaml
```

### API

```python
from ir_extract_golang import GolangExtractor
from ir_core.base import ExtractConfig

extractor = GolangExtractor()
config = ExtractConfig()

source = """
package main

import "fmt"

type Greeter interface {
    Greet() string
}

type Person struct {
    Name string
}

func (p Person) Greet() string {
    return fmt.Sprintf("Hello, %s!", p.Name)
}

func main() {
    var g Greeter = Person{Name: "World"}
    fmt.Println(g.Greet())
}
"""

ir = extractor.extract(source, "main.go", config)
```

## Semantic Annotations

The extractor generates Go-specific semantic annotations:

| Kind | Description |
|------|-------------|
| GO-001 | Structural typing for interfaces |
| GO-002 | Error handling pattern (returns error) |
| GO-003 | Goroutine usage |
| GO-004 | Channel operations |
| GO-005 | Defer statement usage |

## Gap Detection

The extractor detects patterns that may require manual attention during conversion:

| Kind | Severity | Description |
|------|----------|-------------|
| GO-010 | Medium | Multiple goroutines (synchronization complexity) |
| GO-011 | Medium | Complex channel usage |
| GO-012 | Low | Multiple return values (>2) |
| GO-013 | Medium | Custom generic constraints |
| GO-014 | Low | Embedded types |
| GO-015 | Low | Struct field tags |

## Cross-Language Conversion

When converting Go to other languages, consider:

### Go → Python
- Multiple returns → tuples or dataclasses
- Channels → asyncio.Queue
- Goroutines → asyncio.create_task
- Defer → context managers / try-finally
- Interfaces → Protocol classes (structural)

### Go → TypeScript
- Multiple returns → tuples or objects
- Channels → async iterators or observables
- Goroutines → Promise.all
- Defer → try-finally
- Interfaces → interfaces (structural match)

### Go → Rust
- Multiple returns → Result<(T, U), E> or custom types
- Channels → std::sync::mpsc or tokio::sync
- Goroutines → std::thread or tokio::spawn
- Defer → Drop trait or scopeguard
- Interfaces → traits (explicit implementation required)

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type check
mypy ir_extract_golang

# Lint
ruff check ir_extract_golang
```

## License

MIT
