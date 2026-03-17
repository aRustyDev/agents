# IR Overview

The Intermediate Representation (IR) is a language-agnostic data structure that captures the semantic meaning of source code, enabling conversion between programming languages.

## Design Principles

### 1. Semantic Preservation

The IR captures what code *means*, not just what it *looks like*:
- Function purity and effects
- Nullability and optionality
- Error handling patterns
- Mutability constraints

### 2. Language Agnosticism

The IR is not biased toward any specific language:
- Uses universal type vocabulary
- Represents patterns abstractly
- Annotates language-specific features

### 3. Layered Architecture

Information is organized by abstraction level:
- Low-level expressions (Layer 0)
- Data and control flow (Layers 1-2)
- Type system (Layer 3)
- Module structure (Layer 4)

### 4. Lossless Annotation

When conversion isn't straightforward, gaps are annotated:
- Source pattern captured
- Target limitation noted
- Suggested resolutions provided

## IR Layers

### Layer 0: Expressions

AST-level expression nodes:

```yaml
expressions:
  - kind: "binary_op"
    operator: "+"
    left: {kind: "variable", name: "a"}
    right: {kind: "literal", value: 1, type: "int"}
```

### Layer 1: Data Flow

Value flow through variables:

```yaml
data_flow:
  bindings:
    - name: "total"
      value_from: ["item.price", "tax"]
      operation: "sum"
  mutations:
    - variable: "counter"
      operations: ["increment"]
```

### Layer 2: Control Flow

Execution paths and branches:

```yaml
control_flow:
  - kind: "conditional"
    condition: "user.is_active"
    true_branch: [...]
    false_branch: [...]

  - kind: "loop"
    variable: "item"
    iterable: "items"
    body: [...]
```

### Layer 3: Type System

Type definitions and relationships:

```yaml
types:
  - name: "User"
    kind: "struct"
    properties:
      - name: "id"
        type: "Int"
        nullable: false
      - name: "email"
        type: "String"
        nullable: false
    methods:
      - name: "display_name"
        return_type: "String"
        purity: "pure"
```

### Layer 4: Module Structure

Imports, exports, dependencies:

```yaml
modules:
  - name: "auth"
    path: "src/auth.py"
    imports:
      - module: "models"
        items: ["User", "Session"]
    exports:
      - "authenticate"
      - "logout"
    dependencies:
      - "models"
      - "database"
```

## Type Vocabulary

### Primitive Types

| IR Type | Description |
|---------|-------------|
| `Int` | Integer (platform-sized) |
| `I8`, `I16`, `I32`, `I64` | Sized integers |
| `U8`, `U16`, `U32`, `U64` | Unsigned integers |
| `Float` | Floating point (platform-sized) |
| `F32`, `F64` | Sized floats |
| `Bool` | Boolean |
| `Char` | Unicode character |
| `String` | Text string |
| `Unit` | No value (void) |

### Composite Types

| IR Type | Description |
|---------|-------------|
| `Option[T]` | Optional value |
| `Result[T,E]` | Success or error |
| `List[T]` | Ordered collection |
| `Set[T]` | Unique collection |
| `Dict[K,V]` | Key-value mapping |
| `Tuple[T...]` | Fixed heterogeneous |
| `Array[T,N]` | Fixed-size array |

### Function Types

| IR Type | Description |
|---------|-------------|
| `Fn(A,B) -> C` | Function type |
| `Async[T]` | Async result |
| `Effect[E,T]` | Effectful computation |

## Semantic Annotations

### Purity

```yaml
purity:
  - pure       # No side effects
  - impure     # Has side effects
  - io         # Performs I/O
  - async      # Asynchronous
```

### Nullability

```yaml
nullability:
  - non_null   # Never null
  - nullable   # May be null
  - optional   # Explicitly optional
```

### Mutability

```yaml
mutability:
  - immutable  # Cannot change
  - mutable    # Can change
  - once       # Set once
```

### Error Handling

```yaml
error_handling:
  - throws     # May throw exception
  - returns    # Returns error value
  - panics     # May terminate
  - never      # Cannot fail
```

## Gap Annotations

When a source pattern doesn't map directly to the IR:

```yaml
annotations:
  - kind: "RS-001"        # Rust ownership
    target: "transfer"
    severity: "high"
    message: "Ownership transfer detected"
    source_pattern: "fn consume(self)"
    suggestion: "Use clone or borrow pattern"
```

### Severity Levels

| Level | Description |
|-------|-------------|
| `critical` | Cannot convert without human decision |
| `high` | Significant semantic change |
| `medium` | Pattern translation needed |
| `low` | Minor syntax adaptation |
| `info` | Documentation only |

## Example IR

```yaml
ir:
  version: "1.0"
  source_language: "python"
  source_path: "src/user_service.py"

  modules:
    - name: "user_service"
      imports:
        - module: "models"
          items: ["User"]
        - module: "database"
          items: ["get_connection"]
      exports:
        - "UserService"

  types:
    - name: "UserService"
      kind: "class"
      properties:
        - name: "db"
          type: "Connection"
          visibility: "private"
      methods:
        - name: "get_user"
          parameters:
            - name: "id"
              type: "Int"
          return_type: "Option[User]"
          purity: "io"
          async: true

  functions:
    - name: "create_service"
      parameters: []
      return_type: "UserService"
      purity: "io"
      body:
        - kind: "binding"
          name: "conn"
          value:
            kind: "call"
            function: "get_connection"
            arguments: []
        - kind: "return"
          value:
            kind: "construct"
            type: "UserService"
            arguments:
              db: {kind: "variable", name: "conn"}

  annotations:
    - kind: "PY-001"
      target: "UserService"
      severity: "medium"
      message: "Class with mutable state"
      suggestion: "Consider immutable pattern for functional targets"
```
