# Layer 1: Data Flow IR

Layer 1 represents data dependencies, variable bindings, lifetimes, and transformations. Unlike Layer 2 (Control Flow), which describes execution order, Layer 1 captures how data moves through a program.

**Version:** 1.0
**Generated:** 2026-02-04
**Task:** ai-f33.5

---

## 1. Overview

### 1.1 Purpose

Layer 1 serves as the foundation for understanding data relationships in converted code:

- **Binding Semantics**: How variables are bound to values
- **Lifetime Tracking**: When data is created, used, and destroyed
- **Ownership Model**: Who is responsible for data (critical for Rust conversions)
- **Transformation Chains**: How data flows through map/filter/fold operations
- **Side Effect Propagation**: How effects travel through data dependencies

### 1.2 Layer Position

```
Layer 2: Control Flow IR
         ↓ contains
Layer 1: Data Flow IR    ← This document
         ↓ references
Layer 0: Expression IR (optional)
```

Layer 1 sits between control flow (Layer 2) and expressions (Layer 0). Function bodies from Layer 2 are represented as data flow graphs in Layer 1.

### 1.3 Key Constructs

| Construct | Purpose | Primary Use |
|-----------|---------|-------------|
| `binding` | Variable binding with mutability and lifetime | All variables |
| `lifetime` | Ownership and borrowing semantics | Memory safety |
| `data_flow_node` | Node in the data dependency graph | Transformation tracking |
| `transformation` | Functional operation on data | map/filter/fold chains |

---

## 2. Binding Schema

A binding represents a variable bound to a value within a specific scope.

### 2.1 Schema Definition

```yaml
binding:
  id: BindingId
  name: string
  type: TypeRef            # Reference to Layer 3 type
  mutability: Mutability
  lifetime: Lifetime
  value: Expression?       # Optional initial value (Layer 0)
  scope: ScopeId
  captures: Capture[]?     # For closure bindings
  annotations: SemanticAnnotation[]
```

### 2.2 Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier for cross-references |
| `name` | Yes | Variable name in source code |
| `type` | Yes | Type reference (may be inferred) |
| `mutability` | Yes | mutable, immutable, or linear |
| `lifetime` | Yes | Ownership/borrowing information |
| `value` | No | Initial value expression |
| `scope` | Yes | Enclosing scope identifier |
| `captures` | No | Variables captured from outer scopes |
| `annotations` | No | Semantic annotations (e.g., @inferred_type) |

### 2.3 Binding Examples

**Python binding with inferred type:**

```yaml
binding:
  id: "b_001"
  name: "items"
  type:
    kind: named
    type_id: "list_str"
  mutability: mutable
  lifetime:
    kind: scoped
    scope: "fn_process"
  value:
    kind: literal
    value: []
  scope: "fn_process"
  annotations:
    - kind: inferred_type
      value:
        original: "dynamic"
        inferred: "list[str]"
        confidence: 0.92
      source: usage
```

**Rust binding with explicit ownership:**

```yaml
binding:
  id: "b_002"
  name: "data"
  type:
    kind: named
    type_id: "Vec_u8"
  mutability: mutable
  lifetime:
    kind: owned
  value:
    kind: call
    callee: "Vec::new"
  scope: "fn_read_file"
```

---

## 3. Mutability Model

The IR supports three mutability levels to capture semantics across all language families.

### 3.1 Mutability Kinds

```yaml
Mutability:
  mutable     # Can be reassigned
  immutable   # Cannot be reassigned
  linear      # Must be used exactly once
```

### 3.2 Mutability Semantics

| Kind | Reassignment | Multiple Reads | Language Examples |
|------|--------------|----------------|-------------------|
| `mutable` | Allowed | Allowed | Python, Java, JavaScript (let) |
| `immutable` | Forbidden | Allowed | Rust (let), Haskell, JavaScript (const) |
| `linear` | Forbidden | Forbidden | Rust (move), Clean, Linear Haskell |

### 3.3 Language Mappings

**Mutable-by-default languages:**

| Language | Mutable Keyword | Immutable Keyword |
|----------|-----------------|-------------------|
| Python | (default) | N/A (convention) |
| Java | (default) | `final` |
| JavaScript | `let` | `const` |
| C++ | (default) | `const` |

**Immutable-by-default languages:**

| Language | Immutable Keyword | Mutable Keyword |
|----------|-------------------|-----------------|
| Rust | `let` | `let mut` |
| Haskell | (default) | `IORef`, `STRef` |
| Elixir | (default) | N/A (rebinding) |
| Scala | `val` | `var` |

### 3.4 Mutability Conversion Patterns

Converting mutable to immutable (Pattern MM-004):

```yaml
# Source (Python)
binding:
  name: "total"
  mutability: mutable
  annotations:
    - kind: mutability_analysis
      value:
        mutation_sites: [15, 22, 31]
        can_be_immutable: false
        transformation_strategy: "persistent_ds"

# Target (Haskell) - converted to fold
transformation:
  kind: fold
  input_type: "list_int"
  output_type: "int"
  function: "+"
```

---

## 4. Lifetime System

Lifetimes track when data is valid and who owns it. This is critical for memory-safe language conversions.

### 4.1 Lifetime Schema

```yaml
lifetime:
  kind: LifetimeKind
  scope: ScopeId?          # For scoped lifetimes
  borrow_kind: BorrowKind? # For borrowed lifetimes
  name: string?            # Named lifetime (e.g., 'a)

LifetimeKind:
  static    # Lives for program duration ('static)
  scoped    # Lives for a lexical scope
  owned     # Ownership can be transferred
  borrowed  # Temporary reference

BorrowKind:
  shared    # &T - multiple readers, no writers
  mutable   # &mut T - single reader/writer
  move      # Ownership transfer (not a borrow)
```

### 4.2 Lifetime Semantics

| Kind | Duration | Aliasing | Transfer |
|------|----------|----------|----------|
| `static` | Entire program | Allowed | No |
| `scoped` | Until scope ends | Allowed | No |
| `owned` | Until dropped | No | Yes (move) |
| `borrowed` | Until borrow ends | Depends on borrow_kind | No |

### 4.3 Rust Ownership Examples

**Owned value:**

```yaml
binding:
  id: "b_string"
  name: "s"
  type: { kind: named, type_id: "String" }
  mutability: immutable
  lifetime:
    kind: owned
  scope: "fn_main"
```

**Shared borrow:**

```yaml
binding:
  id: "b_ref"
  name: "r"
  type:
    kind: reference
    referent: { kind: named, type_id: "String" }
    lifetime_name: "'a"
  mutability: immutable
  lifetime:
    kind: borrowed
    borrow_kind: shared
    scope: "fn_process"
```

**Mutable borrow:**

```yaml
binding:
  id: "b_mut_ref"
  name: "m"
  type:
    kind: reference
    referent: { kind: named, type_id: "Vec_i32" }
    mutable: true
  mutability: mutable
  lifetime:
    kind: borrowed
    borrow_kind: mutable
    scope: "loop_body"
```

### 4.4 GC Language Mappings

Languages with garbage collection map to simplified lifetime models:

| Source Language | Lifetime Mapping | Notes |
|-----------------|------------------|-------|
| Python | All `scoped` | GC handles deallocation |
| Java | All `scoped` | References counted |
| JavaScript | All `scoped` | GC handles cycles |
| Go | `scoped` + escape analysis | Stack vs heap |

**Python to Rust conversion (Pattern MM-002):**

```yaml
# Python source - all values GC-managed
binding:
  name: "items"
  lifetime:
    kind: scoped
    scope: "fn_process"
  annotations:
    - kind: ownership_hint
      value:
        source: "passed by reference (Python)"
        analysis:
          mutated: false
          returned: false
          stored: false
        recommendation:
          primary: "&[T]"
          rationale: "no mutation, iteration only"
        lifetime: "'a (tied to input)"
```

---

## 5. Data Flow Nodes

Data flow nodes represent points in the data dependency graph where values are created, transformed, or consumed.

### 5.1 Node Schema

```yaml
data_flow_node:
  id: NodeId
  kind: NodeKind
  expression: Expression
  inputs: NodeId[]
  outputs: NodeId[]
  effects: Effect[]

NodeKind:
  source     # Data originates here (literals, parameters)
  transform  # Data is transformed (operations, calls)
  sink       # Data is consumed here (returns, assignments)
```

### 5.2 Node Kinds

**Source nodes** create new data:
- Literal values
- Function parameters
- External inputs (I/O)

**Transform nodes** modify data:
- Function calls
- Operators
- Method invocations

**Sink nodes** consume data:
- Return statements
- Assignments to external state
- Output operations

### 5.3 Data Flow Graph Example

For the expression `result = items.filter(pred).map(fn).collect()`:

```yaml
nodes:
  - id: "n_items"
    kind: source
    expression: { kind: identifier, binding_ref: "b_items" }
    outputs: ["n_filter"]

  - id: "n_filter"
    kind: transform
    expression:
      kind: method_call
      receiver: "n_items"
      method: "filter"
      args: ["pred"]
    inputs: ["n_items"]
    outputs: ["n_map"]
    effects: []

  - id: "n_map"
    kind: transform
    expression:
      kind: method_call
      receiver: "n_filter"
      method: "map"
      args: ["fn"]
    inputs: ["n_filter"]
    outputs: ["n_collect"]
    effects: []

  - id: "n_collect"
    kind: transform
    expression:
      kind: method_call
      receiver: "n_map"
      method: "collect"
    inputs: ["n_map"]
    outputs: ["n_result"]
    effects: [{ kind: allocates }]

  - id: "n_result"
    kind: sink
    expression:
      kind: assignment
      target: "result"
    inputs: ["n_collect"]
    outputs: []
```

### 5.4 Effect Tracking in Data Flow

Effects propagate through data flow edges:

```yaml
# Effect propagation example
data_flow_node:
  id: "n_read"
  kind: transform
  expression:
    kind: call
    callee: "read_file"
    args: ["path"]
  inputs: ["n_path"]
  outputs: ["n_content"]
  effects:
    - kind: io
    - kind: throws
      type: { kind: named, type_id: "IOError" }
```

---

## 6. Transformations

Transformations represent functional patterns that operate on data collections.

### 6.1 Transformation Schema

```yaml
transformation:
  kind: TransformKind
  input_type: TypeRef
  output_type: TypeRef
  function: FunctionRef | Lambda

TransformKind:
  map       # Apply function to each element
  filter    # Keep elements matching predicate
  fold      # Reduce to single value
  flat_map  # Map then flatten
  collect   # Materialize lazy sequence
```

### 6.2 Transformation Semantics

| Kind | Input | Output | Function Signature |
|------|-------|--------|-------------------|
| `map` | `[A]` | `[B]` | `A -> B` |
| `filter` | `[A]` | `[A]` | `A -> Bool` |
| `fold` | `[A]` | `B` | `(B, A) -> B` |
| `flat_map` | `[A]` | `[B]` | `A -> [B]` |
| `collect` | `Iterator<A>` | `[A]` | N/A |

### 6.3 Transformation Examples

**Map transformation:**

```yaml
transformation:
  kind: map
  input_type:
    kind: generic
    type_id: "Vec"
    args: [{ kind: named, type_id: "String" }]
  output_type:
    kind: generic
    type_id: "Vec"
    args: [{ kind: named, type_id: "i32" }]
  function:
    kind: lambda
    params: [{ name: "s", type: "String" }]
    body: { kind: method_call, receiver: "s", method: "len" }
```

**Fold transformation:**

```yaml
transformation:
  kind: fold
  input_type:
    kind: generic
    type_id: "Vec"
    args: [{ kind: named, type_id: "i32" }]
  output_type: { kind: named, type_id: "i32" }
  function:
    kind: function_ref
    id: "fn_add"
    # Represents: |acc, x| acc + x
```

---

## 7. Linear Types

Linear types enforce that values are used exactly once. This is essential for resource management without GC.

### 7.1 Linear Type Semantics

```yaml
binding:
  id: "b_file"
  name: "file"
  type: { kind: named, type_id: "File" }
  mutability: linear
  lifetime:
    kind: owned
  annotations:
    - kind: linear_type_conversion
      value:
        source_pattern: "shared_mutable"
        target_pattern: "linear"
        usage_count: 1
        must_consume: true
```

### 7.2 Linear Type Rules

1. **Single use**: A linear value must be used exactly once
2. **No aliasing**: Cannot create multiple references
3. **Explicit consumption**: Must be explicitly passed or dropped

### 7.3 Linear Type Conversion (Pattern MM-003)

**Java source (shared mutable):**

```java
void transfer(Account from, Account to, int amount) {
    from.balance -= amount;
    to.balance += amount;
}
```

**Rust target (linear ownership):**

```rust
fn transfer(mut from: Account, mut to: Account, amount: i32) -> (Account, Account) {
    from.balance -= amount;
    to.balance += amount;
    (from, to)  // Return ownership
}
```

**IR representation:**

```yaml
function:
  id: "fn_transfer"
  params:
    - name: "from"
      type: "Account"
      mutability: linear
    - name: "to"
      type: "Account"
      mutability: linear
  return_type:
    kind: tuple
    elements: ["Account", "Account"]
  body:
    nodes:
      - id: "n_withdraw"
        kind: transform
        expression: { kind: assignment, target: "from.balance", op: "-=", value: "amount" }
        inputs: ["from", "amount"]
        outputs: ["from_new"]

      - id: "n_deposit"
        kind: transform
        expression: { kind: assignment, target: "to.balance", op: "+=", value: "amount" }
        inputs: ["to", "amount"]
        outputs: ["to_new"]

      - id: "n_return"
        kind: sink
        expression: { kind: tuple, elements: ["from_new", "to_new"] }
        inputs: ["from_new", "to_new"]
```

---

## 8. Closure Captures

Closures capture variables from enclosing scopes. The IR tracks how each variable is captured.

### 8.1 Capture Schema

```yaml
capture:
  binding_id: BindingId     # Original binding
  capture_kind: CaptureKind
  captured_type: TypeRef?   # May differ from original

CaptureKind:
  by_value      # Copy/clone the value
  by_reference  # Borrow the value
  by_mut_ref    # Mutably borrow
  by_move       # Take ownership
```

### 8.2 Capture Examples

**JavaScript closure (by reference):**

```javascript
function counter() {
    let count = 0;
    return () => count++;  // Captures count by reference
}
```

```yaml
binding:
  id: "b_closure"
  name: "increment"
  type: { kind: function, params: [], return_type: "i32" }
  captures:
    - binding_id: "b_count"
      capture_kind: by_mut_ref
      captured_type: "i32"
```

**Rust closure (move semantics):**

```rust
let data = vec![1, 2, 3];
let closure = move || data.len();  // Takes ownership
```

```yaml
binding:
  id: "b_closure"
  name: "closure"
  type: { kind: function, params: [], return_type: "usize" }
  captures:
    - binding_id: "b_data"
      capture_kind: by_move
      captured_type: "Vec<i32>"
  annotations:
    - kind: ownership_transfer
      value:
        from: "b_data"
        to: "b_closure"
        reason: "move keyword in closure"
```

### 8.3 Capture Conversion Challenges

**Python to Rust (Pattern MM-002):**

Python closures capture by reference with late binding. Rust requires explicit capture mode.

```yaml
# Python source
binding:
  id: "b_lambda"
  captures:
    - binding_id: "b_x"
      capture_kind: by_reference  # Python default
  annotations:
    - kind: ownership_hint
      value:
        recommendation:
          capture_mode: "by_move"
          rationale: "x not used after closure creation"
        alternative:
          capture_mode: "by_reference"
          requires: "lifetime annotation 'a"
```

---

## 9. Haskell Immutability Example

Haskell represents pure immutable bindings with no mutation sites.

### 9.1 Haskell Binding

```haskell
let items = [1, 2, 3]
    doubled = map (*2) items
in sum doubled
```

```yaml
bindings:
  - id: "b_items"
    name: "items"
    type:
      kind: generic
      type_id: "List"
      args: [{ kind: named, type_id: "Int" }]
    mutability: immutable
    lifetime:
      kind: static  # Haskell values are effectively static
    value:
      kind: literal
      value: [1, 2, 3]

  - id: "b_doubled"
    name: "doubled"
    type:
      kind: generic
      type_id: "List"
      args: [{ kind: named, type_id: "Int" }]
    mutability: immutable
    lifetime:
      kind: static
    value:
      kind: call
      callee: "map"
      args:
        - kind: lambda
          body: { kind: operator, op: "*", operands: ["$1", 2] }
        - kind: identifier
          binding_ref: "b_items"
```

### 9.2 Laziness Annotation

Haskell's lazy evaluation affects data flow:

```yaml
binding:
  id: "b_naturals"
  name: "naturals"
  type: { kind: generic, type_id: "List", args: ["Int"] }
  mutability: immutable
  annotations:
    - kind: evaluation_strategy
      value:
        source: "lazy"
        pattern: "infinite_list"
        analysis:
          is_infinite: true
          consumption_pattern: "take_first_n"
        transformation:
          strategy: "iterator"
          target_type: "impl Iterator<Item = i32>"
```

---

## 10. Side Effect Tracking

Side effects propagate through the data flow graph, enabling effect analysis.

### 10.1 Effect Types

```yaml
Effect:
  kind: EffectKind
  type: TypeRef?       # For typed effects (e.g., throws(E))
  scope: ScopeId?      # Where effect is contained

EffectKind:
  pure       # No side effects
  io         # Input/output operations
  throws     # May raise exception
  async      # Asynchronous operation
  allocates  # Memory allocation
  mutates    # Mutates external state
  captures   # Captures environment
```

### 10.2 Effect Propagation Rules

1. **Pure nodes**: No effects propagate through
2. **IO nodes**: IO effect propagates to all dependents
3. **Throws nodes**: Exception effect propagates until caught
4. **Allocates nodes**: Allocation tracked for lifetime analysis

### 10.3 Effect Boundary Example

```yaml
data_flow_node:
  id: "n_fetch"
  kind: transform
  expression:
    kind: call
    callee: "fetch_data"
    args: ["url"]
  effects:
    - kind: io
    - kind: async
    - kind: throws
      type: { kind: named, type_id: "NetworkError" }
  annotations:
    - kind: effect_boundary
      value:
        source_style: "implicit"
        target_style: "explicit_result"
        transformation: "wrap in Result<T, NetworkError>"
```

---

## 11. Cross-Layer References

### 11.1 References to Layer 0

Layer 1 optionally references Layer 0 for expression details:

```yaml
binding:
  id: "b_expr"
  value:
    # Reference to Layer 0 expression
    expression_id: "expr_0042"
    # Or inline expression
    kind: operator
    op: "+"
    operands:
      - { kind: identifier, name: "a" }
      - { kind: literal, value: 1 }
```

### 11.2 References to Layer 2

Layer 1 is contained within Layer 2 function bodies:

```yaml
# Layer 2 function
function:
  id: "fn_process"
  body:
    # Layer 1 data flow graph
    entry_bindings: ["b_input"]
    nodes: [...]
    exit_binding: "b_result"
```

### 11.3 References to Layer 3

Layer 1 references Layer 3 types:

```yaml
binding:
  type:
    kind: named
    type_id: "t_user"  # References Layer 3 type_def
```

---

## 12. Gap Patterns Affecting Layer 1

The following Phase 3 gap patterns primarily affect Layer 1:

| Pattern ID | Name | Severity | Layer 1 Impact |
|------------|------|----------|----------------|
| MM-002 | GC to Ownership | high | Lifetime inference |
| MM-003 | Shared to Linear | high | Mutability conversion |
| MM-004 | Mutable to Immutable | medium | Mutation tracking |
| TS-001 | Dynamic to Static | high | Type inference on bindings |
| EF-009 | Lazy to Strict | high | Transformation strategy |

### 12.1 Annotation Integration

Layer 1 nodes carry semantic annotations from Phase 3 patterns:

```yaml
binding:
  id: "b_data"
  annotations:
    # Type inference (TS-001)
    - kind: inferred_type
      value:
        original: "dynamic"
        inferred: "Vec<String>"
        confidence: 0.88
      source: usage

    # Ownership hint (MM-002)
    - kind: ownership_hint
      value:
        source: "passed by reference (Python)"
        recommendation:
          primary: "&[String]"
          lifetime: "'a"

    # Mutability analysis (MM-004)
    - kind: mutability_analysis
      value:
        source_mutability: "mutable"
        mutation_sites: []
        can_eliminate: true
```

---

## 13. Summary

Layer 1 provides the foundation for understanding data semantics in code conversion:

| Concept | Schema | Purpose |
|---------|--------|---------|
| Bindings | `binding` | Variable definitions with types and lifetimes |
| Mutability | `mutable \| immutable \| linear` | Change semantics |
| Lifetimes | `static \| scoped \| owned \| borrowed` | Memory safety |
| Data Flow | `data_flow_node` | Dependency graph |
| Transformations | `map \| filter \| fold \| flat_map \| collect` | Functional patterns |
| Effects | `pure \| io \| throws \| async \| allocates` | Side effect tracking |
| Captures | `by_value \| by_reference \| by_move` | Closure semantics |

### 13.1 Key Design Decisions

1. **Unified ownership model**: Single representation works for GC, ARC, and ownership-based languages
2. **Effect propagation**: Side effects tracked through data dependencies, not just control flow
3. **Linear type support**: First-class support for exactly-once semantics
4. **Capture tracking**: Explicit representation of closure capture modes

### 13.2 Related Documents

| Document | Content |
|----------|---------|
| `overview.md` | IR architecture and layers |
| `layer-0.md` | Expression IR details |
| `layer-2.md` | Control flow and functions |
| `layer-3.md` | Type system representation |
| `preservation-levels.md` | Semantic preservation tracking |

---

*Generated for Phase 4: IR Schema Design (ai-f33.5)*
