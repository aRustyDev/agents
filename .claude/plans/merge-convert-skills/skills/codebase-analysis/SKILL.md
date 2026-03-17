---
name: Codebase Analysis
version: 1.0.0
description: Extract IR from source code for cross-language conversion
category: conversion
languages: [python, typescript, rust, java, go, scala, roc, kotlin, swift, elixir]
tools: [ir-extract-python, ir-extract-rust, ir-extract-typescript, ir-extract-go, ir-extract-scala, ir-extract-roc]
---

# Codebase Analysis

Extract an Intermediate Representation (IR) from source code to enable cross-language conversion and analysis.

## Usage

```
/codebase-analysis <path> [--language <lang>] [--depth <0-4>] [--output <format>]
```

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `path` | File or directory to analyze | Required |
| `--language` | Source language (auto-detected if omitted) | auto |
| `--depth` | IR extraction depth (0-4) | 4 |
| `--output` | Output format (json, yaml, summary) | json |

## Process

### 1. Language Detection

If `--language` is not specified, detect based on:
- File extension (`.py`, `.rs`, `.ts`, `.go`, `.scala`, `.roc`)
- Shebang line
- Package files (`pyproject.toml`, `Cargo.toml`, `package.json`)

### 2. Module Discovery

Identify all modules and their relationships:
- Import/export statements
- Module boundaries
- Dependency graph

### 3. Type Extraction

Extract type definitions and relationships:
- Struct/class/record definitions
- Enum/ADT/union types
- Type aliases and generics
- Trait/interface definitions

### 4. Function Analysis

Extract function signatures and semantics:
- Parameter types and defaults
- Return types
- Purity annotations (where inferrable)
- Effect annotations (I/O, async, etc.)

### 5. Semantic Annotation

Infer semantic properties:
- Nullability (Option, nullable, undefined)
- Mutability (const, let, var)
- Error handling patterns (Result, exceptions, error returns)
- Concurrency patterns (async, channels, actors)

### 6. Gap Detection

Mark concepts that may not convert cleanly:
- Language-specific patterns (ownership, HKT, macros)
- Family-specific idioms (pattern matching, effects)
- Cross-language semantic gaps

## Output

### IR Layers

The IR is organized into 5 layers of increasing abstraction:

| Layer | Name | Description |
|-------|------|-------------|
| 0 | Expressions | AST-level expression nodes |
| 1 | Data Flow | Value flow through variables |
| 2 | Control Flow | Execution paths and branches |
| 3 | Type System | Type definitions and relationships |
| 4 | Module Structure | Imports, exports, dependencies |

### IR Schema

```yaml
ir:
  version: "1.0"
  source_language: "python"
  source_path: "src/main.py"

  modules:
    - name: "main"
      imports: [...]
      exports: [...]

  types:
    - name: "User"
      kind: "struct"
      properties:
        - name: "id"
          type: "int"
        - name: "name"
          type: "str"

  functions:
    - name: "get_user"
      parameters:
        - name: "id"
          type: "int"
      return_type: "Optional[User]"
      purity: "pure"

  annotations:
    - kind: "PY-003"
      target: "get_user"
      message: "Generator usage detected"
      severity: "medium"
```

### Gap Annotations

Gaps are annotated with:
- `kind`: Gap identifier (e.g., "PY-RS-001")
- `target`: What element has the gap
- `message`: Human-readable description
- `severity`: critical, high, medium, low, info
- `suggestion`: Recommended resolution

## Examples

### Analyze a Python file

```bash
/codebase-analysis src/models.py
```

### Analyze a Rust crate with summary

```bash
/codebase-analysis ./src --language rust --output summary
```

### Analyze specific depth level

```bash
/codebase-analysis lib/ --depth 2  # Control flow only
```

## Reference

- [IR Overview](reference/ir/overview.md)
- [IR Schema](reference/ir/schema.md)
- [Extraction Guide](reference/ir/extraction-guide.md)
- [Tool Usage](reference/ir/tools.md)
- [Language Families](reference/families/overview.md)
- [Python Patterns](reference/languages/python.md)
- [Rust Patterns](reference/languages/rust.md)
- [TypeScript Patterns](reference/languages/typescript.md)

## Related Skills

- [codebase-implement-from-ir](../codebase-implement-from-ir/SKILL.md) - Synthesize code from IR
- [idiomatic-python](../idiomatic-python/SKILL.md) - Python-specific idioms
- [idiomatic-rust](../idiomatic-rust/SKILL.md) - Rust-specific idioms
