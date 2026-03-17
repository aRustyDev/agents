# IR Extraction Guide

Step-by-step guide for extracting IR from source code.

## Overview

IR extraction transforms source code into a language-agnostic representation while preserving semantic meaning and annotating patterns that may not convert cleanly.

## Extraction Process

### Phase 1: Parse Source

Use language-specific parser to create AST:

```python
from ir_extract_python import PythonExtractor

extractor = PythonExtractor()
config = ExtractConfig(depth=4)
ir = extractor.extract(source_code, file_path, config)
```

### Phase 2: Module Discovery

1. Identify module boundaries (files, packages)
2. Parse import statements
3. Resolve dependencies
4. Build dependency graph

```yaml
modules:
  - name: "auth"
    path: "src/auth/__init__.py"
    imports:
      - module: "models"
        items: ["User", "Session"]
    exports:
      - "authenticate"
      - "logout"
      - "AuthService"
```

### Phase 3: Type Extraction

Extract all type definitions:

1. **Classes/Structs**
   - Properties and their types
   - Methods and signatures
   - Inheritance relationships

2. **Enums/ADTs**
   - Variants
   - Associated data

3. **Interfaces/Traits**
   - Required methods
   - Default implementations

4. **Type Aliases**
   - Target types
   - Generic parameters

### Phase 4: Function Analysis

For each function:

1. **Signature**
   - Parameters and types
   - Return type
   - Generic constraints

2. **Semantics**
   - Purity (pure, impure, io)
   - Async status
   - Error handling pattern

3. **Body** (optional, depth-dependent)
   - Control flow
   - Data flow
   - Expression tree

### Phase 5: Semantic Inference

Infer properties not explicitly stated:

| Property | Inference Method |
|----------|------------------|
| Purity | Check for I/O calls, mutations |
| Nullability | Analyze assignments, returns |
| Mutability | Track variable reassignments |
| Error Handling | Detect try/catch, Result usage |

### Phase 6: Gap Detection

Identify patterns that may not convert:

1. **Language-Specific Patterns**
   - Ownership (Rust)
   - Decorators (Python)
   - Macros (Rust, Scala)

2. **Family-Specific Patterns**
   - Higher-kinded types (ML/FP)
   - Actors (BEAM)
   - Pattern matching depth

3. **Cross-Language Gaps**
   - Type system differences
   - Error handling mismatch
   - Concurrency model mismatch

## Extraction Depth Levels

### Level 0: Expressions

Most detailed, captures full AST:

```yaml
expressions:
  - kind: binary_op
    operator: "+"
    left:
      kind: variable
      name: "a"
    right:
      kind: literal
      value: 1
      type: Int
```

Use for: Precise code transformation, refactoring

### Level 1: Data Flow

Value propagation and dependencies:

```yaml
data_flow:
  - binding: "result"
    depends_on: ["x", "y"]
    operation: "multiply_then_add"
```

Use for: Dependency analysis, dead code detection

### Level 2: Control Flow

Execution paths and branches:

```yaml
control_flow:
  - kind: "conditional"
    branches:
      - condition: "is_valid(x)"
        leads_to: ["validate", "process"]
      - condition: "else"
        leads_to: ["error"]
```

Use for: Path analysis, complexity metrics

### Level 3: Type System

Type definitions and relationships:

```yaml
types:
  - name: "UserService"
    kind: "class"
    implements: ["Service"]
    methods:
      - name: "get_user"
        return_type: "Option[User]"
```

Use for: API extraction, interface comparison

### Level 4: Module Structure

High-level organization:

```yaml
modules:
  - name: "auth"
    exports: ["authenticate", "AuthService"]
    depends_on: ["database", "crypto"]
```

Use for: Architecture analysis, dependency mapping

## Language-Specific Extraction

### Python

Special handling for:
- Decorators → `DecoratorAnnotation`
- Type hints → Explicit types
- `*args, **kwargs` → Variadic parameters
- Context managers → `ResourceBlock`
- Generators → `GeneratorFunction`

### Rust

Special handling for:
- Ownership → `OwnershipAnnotation`
- Lifetimes → `LifetimeAnnotation`
- Pattern guards → `MatchGuard`
- `?` operator → `ErrorPropagation`
- Macros → Expansion or annotation

### TypeScript

Special handling for:
- Union types → `UnionType`
- Type guards → `TypeNarrowing`
- Generics → Standard generic params
- `undefined` vs `null` → `Nullable` with distinction
- `as const` → `LiteralType`

### Go

Special handling for:
- Multiple returns → `TupleReturn`
- Error returns → `ResultPattern`
- Goroutines → `AsyncAnnotation`
- Channels → `ChannelType`
- Defer → `DeferredExecution`

### Scala

Special handling for:
- Higher-kinded types → `HKTAnnotation`
- Implicits/given → `ContextParameter`
- Variance → `VarianceAnnotation`
- For comprehensions → `MonadicChain`
- Pattern matching → `MatchExpression`

### Roc

Special handling for:
- Task effects → `EffectAnnotation`
- Backpassing → `BackpassSyntax`
- Tag unions → `ADTDef`
- Abilities → `TypeClassDef`
- Opaque types → `NewtypeDef`

## Output Validation

After extraction, validate:

1. **Schema Compliance**: All fields match expected types
2. **Reference Resolution**: All type/function references exist
3. **Scope Validity**: Variables referenced within scope
4. **Gap Coverage**: Known patterns are annotated

```python
from ir_core.validation import validate_ir

errors = validate_ir(ir)
if errors:
    for error in errors:
        print(f"{error.severity}: {error.message}")
```

## Best Practices

1. **Start at Level 4** for understanding structure
2. **Drop to Level 0** only for detailed transformation
3. **Always validate** output IR
4. **Review critical gaps** before synthesis
5. **Preserve source location** for debugging
