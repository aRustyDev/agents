# Layer 0: Expression IR

The lowest layer of the IR architecture, providing full AST representation with source location tracking.

**Version:** 1.0
**Generated:** 2026-02-04
**Task:** ai-f33.6

---

## 1. Overview

Layer 0 captures the fine-grained details of expressions: literals, identifiers, operators, function calls, and lambdas. It preserves source locations (spans) for every syntactic element, enabling precise error reporting and round-trip fidelity.

### 1.1 Important: Layer 0 is OPTIONAL

**Most conversions should NOT use Layer 0.** Layers 1-4 provide sufficient semantic information for the vast majority of language-to-language conversions. Layer 0 adds significant complexity and storage overhead.

Use Layer 0 only when:
- Expression-level fidelity is explicitly required
- You need to preserve or analyze formatting and comments
- Debugging conversion issues at the AST level
- Building refactoring or code analysis tools

### 1.2 Position in Layer Architecture

```
Layer 4: Structural IR       <- Modules, imports, exports
Layer 3: Type IR             <- Type definitions, relationships
Layer 2: Control Flow IR     <- Functions, control patterns
Layer 1: Data Flow IR        <- Bindings, transformations
Layer 0: Expression IR       <- AST details (OPTIONAL)
```

Layer 0 sits beneath Layer 1 (Data Flow IR). When present, Layer 1 bindings reference Layer 0 expressions for their values. When absent, Layer 1 operates with abstract data flow nodes.

---

## 2. When to Use Layer 0

### 2.1 Use Cases Where Layer 0 Adds Value

| Use Case | Why Layer 0 Helps | Example |
|----------|-------------------|---------|
| **Preserving formatting/comments** | Source spans map back to original text | Code review tools showing before/after |
| **Complex expression transformations** | Full AST enables pattern matching | Transforming `x?.y?.z` to `match` chains |
| **Debugging conversion issues** | Trace exactly which expression caused problems | "Error at line 42, column 15" |
| **Round-trip fidelity testing** | Verify source reconstructs correctly | Testing IR serialization/deserialization |
| **IDE integration** | Source locations for hover, go-to-definition | Language server protocol support |
| **Code metrics/analysis** | Count operators, nesting depth, complexity | Cyclomatic complexity calculation |

### 2.2 Use Cases Where Layer 0 is Overhead

| Use Case | Why Skip Layer 0 | Better Alternative |
|----------|------------------|-------------------|
| **Standard conversion** | Semantic level sufficient | Layers 1-4 capture logic |
| **API extraction** | Only signatures matter | Layers 2-4 (signature_only mode) |
| **Type migration** | Only types matter | Layers 3-4 (type_only mode) |
| **Batch processing** | Storage/performance concern | Layers 1-4 are more compact |
| **Semantic diffing** | Expression details noise | Layer 1 data flow comparison |

### 2.3 Decision Flowchart

```
Do you need exact source locations?
├── No -> Skip Layer 0
└── Yes
    └── Do you need expression-level pattern matching?
        ├── No -> Skip Layer 0, use span metadata on Layer 1
        └── Yes -> Use Layer 0
```

---

## 3. Expression Schema

### 3.1 Core Expression Structure

```yaml
expression:
  id: ExpressionId            # Unique identifier
  kind: ExpressionKind        # Discriminator for expression type
  type: TypeRef               # Resolved type (if known)
  span: SourceSpan            # Location in source file

  # Kind-specific fields follow...
```

### 3.2 Expression Kinds

Layer 0 supports the following expression kinds:

| Kind | Description | Key Fields |
|------|-------------|------------|
| `literal` | Constant values | `literal_kind`, `literal_value` |
| `identifier` | Variable references | `binding_ref` |
| `call` | Function/method invocation | `callee`, `arguments` |
| `operator` | Binary, unary, ternary operations | `operator`, `operands` |
| `lambda` | Anonymous functions | `params`, `body`, `captures` |
| `member_access` | Field/property access | `object`, `member` |
| `index` | Array/map indexing | `collection`, `index` |
| `cast` | Type conversions | `target_type`, `operand` |
| `conditional` | Ternary expressions | `condition`, `then_expr`, `else_expr` |
| `tuple` | Tuple construction | `elements` |
| `array` | Array/list literals | `elements` |
| `object` | Object/struct literals | `fields` |
| `await` | Async await expressions | `operand` |
| `throw` | Throw/raise expressions | `exception` |

### 3.3 Literal Expressions

```yaml
literal:
  kind: literal
  literal_kind: LiteralKind
  literal_value: any

LiteralKind:
  - int          # Integer: 42, 0xFF, 0b1010
  - float        # Floating-point: 3.14, 1e-10
  - string       # String: "hello", 'world'
  - char         # Character: 'a', '\n'
  - bool         # Boolean: true, false
  - null         # Null/nil/None
  - regex        # Regular expression: /pattern/flags
  - bigint       # Arbitrary precision: 999999999999999999999n
  - symbol       # Symbols (Ruby, JS): :foo, Symbol("bar")
  - bytes        # Byte strings: b"data"
  - template     # Template literals: `hello ${name}`
```

**Example: Integer literal**

```yaml
expression:
  id: "expr:lit:1"
  kind: literal
  literal_kind: int
  literal_value: 42
  type:
    kind: named
    type_id: "type:i32"
  span:
    file: "src/main.rs"
    start_line: 10
    start_col: 15
    end_line: 10
    end_col: 17
```

### 3.4 Identifier Expressions

```yaml
identifier:
  kind: identifier
  binding_ref: BindingId    # Reference to Layer 1 binding
  name: string              # Original identifier name (for display)
```

**Example: Variable reference**

```yaml
expression:
  id: "expr:id:1"
  kind: identifier
  binding_ref: "binding:x:1"
  name: "x"
  type:
    kind: named
    type_id: "type:i32"
  span:
    file: "src/main.rs"
    start_line: 12
    start_col: 8
    end_line: 12
    end_col: 9
```

### 3.5 Call Expressions

```yaml
call:
  kind: call
  callee: Expression          # Function/method being called
  arguments: Argument[]       # Positional and named arguments
  type_arguments: TypeRef[]?  # Generic type arguments

argument:
  name: string?               # Named argument (if applicable)
  value: Expression
  spread: bool                # Is this a spread/splat argument?
```

**Example: Method call**

```yaml
expression:
  id: "expr:call:1"
  kind: call
  callee:
    id: "expr:member:1"
    kind: member_access
    object:
      id: "expr:id:2"
      kind: identifier
      binding_ref: "binding:list:1"
      name: "list"
    member: "iter"
  arguments: []
  type:
    kind: named
    type_id: "type:Iterator<i32>"
  span:
    file: "src/main.rs"
    start_line: 15
    start_col: 4
    end_line: 15
    end_col: 15
```

### 3.6 Operator Expressions

```yaml
operator:
  kind: operator
  operator: string            # Operator symbol or name
  operator_kind: OperatorKind
  operands: Expression[]      # 1 for unary, 2 for binary, 3 for ternary

OperatorKind:
  - unary_prefix    # -x, !x, ++x
  - unary_postfix   # x++, x?
  - binary          # x + y, x && y
  - comparison      # x < y, x == y
  - assignment      # x = y, x += y
  - ternary         # x ? y : z
```

**Operator mapping table:**

| Category | Operators |
|----------|-----------|
| Arithmetic | `+`, `-`, `*`, `/`, `%`, `**` |
| Comparison | `==`, `!=`, `<`, `>`, `<=`, `>=`, `<=>` |
| Logical | `&&`, `\|\|`, `!`, `and`, `or`, `not` |
| Bitwise | `&`, `\|`, `^`, `~`, `<<`, `>>`, `>>>` |
| Assignment | `=`, `+=`, `-=`, `*=`, `/=`, etc. |
| Access | `.`, `?.`, `::`, `->` |
| Range | `..`, `..=`, `...` |
| Other | `??`, `?:`, `as`, `is`, `in` |

**Example: Binary operation**

```yaml
expression:
  id: "expr:op:1"
  kind: operator
  operator: "+"
  operator_kind: binary
  operands:
    - id: "expr:id:3"
      kind: identifier
      binding_ref: "binding:a:1"
      name: "a"
    - id: "expr:lit:2"
      kind: literal
      literal_kind: int
      literal_value: 1
  type:
    kind: named
    type_id: "type:i32"
  span:
    file: "src/main.rs"
    start_line: 20
    start_col: 10
    end_line: 20
    end_col: 15
```

### 3.7 Lambda Expressions

```yaml
lambda:
  kind: lambda
  params: Param[]                  # Parameter list
  body: Expression | ControlFlowGraph  # Single expression or block
  captures: Capture[]              # Captured variables from enclosing scope
  is_async: bool                   # Async lambda?
  is_generator: bool               # Generator function?

capture:
  binding_ref: BindingId          # Reference to captured binding
  capture_kind: CaptureKind

CaptureKind:
  - by_value      # Copy/move the value
  - by_ref        # Borrow/reference
  - by_mut_ref    # Mutable borrow
```

**Example: Lambda with captures**

```yaml
expression:
  id: "expr:lambda:1"
  kind: lambda
  params:
    - name: "x"
      type:
        kind: named
        type_id: "type:i32"
  body:
    id: "expr:op:2"
    kind: operator
    operator: "+"
    operator_kind: binary
    operands:
      - id: "expr:id:4"
        kind: identifier
        binding_ref: "binding:x:param"
        name: "x"
      - id: "expr:id:5"
        kind: identifier
        binding_ref: "binding:offset:1"
        name: "offset"
  captures:
    - binding_ref: "binding:offset:1"
      capture_kind: by_value
  is_async: false
  is_generator: false
  type:
    kind: function
    params:
      - kind: named
        type_id: "type:i32"
    return_type:
      kind: named
      type_id: "type:i32"
  span:
    file: "src/main.rs"
    start_line: 25
    start_col: 12
    end_line: 25
    end_col: 30
```

---

## 4. Source Spans

Source spans track the precise location of every expression in the original source file.

### 4.1 SourceSpan Structure

```yaml
source_span:
  file: string      # File path (relative to project root)
  start_line: int   # 1-indexed starting line
  start_col: int    # 0-indexed starting column (bytes or chars)
  end_line: int     # 1-indexed ending line
  end_col: int      # 0-indexed ending column (exclusive)
```

### 4.2 Column Encoding

Different languages and tools use different column encodings:

| Encoding | Description | Common In |
|----------|-------------|-----------|
| Byte offset | UTF-8 byte position | Rust, LSP (UTF-8 mode) |
| Character offset | Unicode codepoint | Python, JavaScript |
| UTF-16 code unit | For BMP + surrogate pairs | LSP (default), VS Code |

The IR normalizes to **byte offset** (UTF-8). Converters should document when source languages use different encodings.

### 4.3 Span Examples

**Single-line expression:**

```
let result = x + y * 2;
             ^^^^^^^^^
             start: (1, 13)
             end: (1, 22)
```

```yaml
span:
  file: "src/math.rs"
  start_line: 1
  start_col: 13
  end_line: 1
  end_col: 22
```

**Multi-line expression:**

```
let query = users
    .filter(|u| u.active)
    .map(|u| u.name)
    .collect();
```

```yaml
span:
  file: "src/db.rs"
  start_line: 1
  start_col: 12
  end_line: 4
  end_col: 14
```

### 4.4 Nested Spans

Every subexpression has its own span. Parent spans fully contain child spans.

```
        total / numbers.len()
        ^^^^^^^^^^^^^^^^^^^^^   outer: operator "/"
        ^^^^^                   left: identifier "total"
                ^^^^^^^^^^^^^^  right: call
                ^^^^^^^         object: identifier "numbers"
                        ^^^^^   method: "len"
```

---

## 5. Comprehensive Examples

### 5.1 Simple Arithmetic Expression

**Source (Rust):**

```rust
let area = width * height;
```

**Layer 0 IR:**

```yaml
expression:
  id: "expr:op:area"
  kind: operator
  operator: "*"
  operator_kind: binary
  operands:
    - id: "expr:id:width"
      kind: identifier
      binding_ref: "binding:width:1"
      name: "width"
      type:
        kind: named
        type_id: "type:f64"
      span:
        file: "src/geometry.rs"
        start_line: 5
        start_col: 11
        end_line: 5
        end_col: 16
    - id: "expr:id:height"
      kind: identifier
      binding_ref: "binding:height:1"
      name: "height"
      type:
        kind: named
        type_id: "type:f64"
      span:
        file: "src/geometry.rs"
        start_line: 5
        start_col: 19
        end_line: 5
        end_col: 25
  type:
    kind: named
    type_id: "type:f64"
  span:
    file: "src/geometry.rs"
    start_line: 5
    start_col: 11
    end_line: 5
    end_col: 25
```

### 5.2 Method Chain

**Source (Rust):**

```rust
numbers.iter().filter(|x| *x > 0).map(|x| x * 2).collect()
```

**Layer 0 IR (abbreviated):**

```yaml
expression:
  id: "expr:call:collect"
  kind: call
  callee:
    id: "expr:member:collect"
    kind: member_access
    object:
      id: "expr:call:map"
      kind: call
      callee:
        id: "expr:member:map"
        kind: member_access
        object:
          id: "expr:call:filter"
          kind: call
          callee:
            id: "expr:member:filter"
            kind: member_access
            object:
              id: "expr:call:iter"
              kind: call
              callee:
                id: "expr:member:iter"
                kind: member_access
                object:
                  id: "expr:id:numbers"
                  kind: identifier
                  binding_ref: "binding:numbers:1"
                member: "iter"
              arguments: []
            member: "filter"
          arguments:
            - value:
                id: "expr:lambda:filter"
                kind: lambda
                params:
                  - name: "x"
                body:
                  # *x > 0 expression...
                captures: []
        member: "map"
      arguments:
        - value:
            id: "expr:lambda:map"
            kind: lambda
            params:
              - name: "x"
            body:
              # x * 2 expression...
            captures: []
    member: "collect"
  arguments: []
  span:
    file: "src/transform.rs"
    start_line: 10
    start_col: 4
    end_line: 10
    end_col: 60
```

### 5.3 Conditional Expression (Ternary)

**Source (JavaScript):**

```javascript
const status = age >= 18 ? "adult" : "minor";
```

**Layer 0 IR:**

```yaml
expression:
  id: "expr:cond:1"
  kind: conditional
  condition:
    id: "expr:op:cmp"
    kind: operator
    operator: ">="
    operator_kind: comparison
    operands:
      - id: "expr:id:age"
        kind: identifier
        binding_ref: "binding:age:1"
        name: "age"
      - id: "expr:lit:18"
        kind: literal
        literal_kind: int
        literal_value: 18
  then_expr:
    id: "expr:lit:adult"
    kind: literal
    literal_kind: string
    literal_value: "adult"
  else_expr:
    id: "expr:lit:minor"
    kind: literal
    literal_kind: string
    literal_value: "minor"
  type:
    kind: named
    type_id: "type:string"
  span:
    file: "src/user.js"
    start_line: 3
    start_col: 15
    end_line: 3
    end_col: 46
```

---

## 6. Relationship to Higher Layers

### 6.1 Layer 0 to Layer 1 Connection

Layer 1 (Data Flow IR) represents bindings and transformations. When Layer 0 is present, Layer 1 bindings reference Layer 0 expressions for their initializer values.

```yaml
# Layer 1 binding
binding:
  id: "binding:area:1"
  name: "area"
  type:
    kind: named
    type_id: "type:f64"
  value: "expr:op:area"    # Reference to Layer 0 expression
  mutability: immutable
  scope: "scope:main:1"
```

### 6.2 When Layer 0 is Absent

Without Layer 0, Layer 1 uses abstract representations:

```yaml
# Layer 1 binding (no Layer 0)
binding:
  id: "binding:area:1"
  name: "area"
  type:
    kind: named
    type_id: "type:f64"
  value_description: "width * height"  # Human-readable, not structural
  mutability: immutable
  scope: "scope:main:1"
```

### 6.3 Data Flow Graphs

Layer 1 data flow nodes can reference Layer 0 expressions when detailed analysis is needed:

```yaml
data_flow_node:
  id: "node:transform:1"
  kind: transform
  expression: "expr:call:map"      # Optional Layer 0 reference
  inputs: ["node:source:iter"]
  outputs: ["node:sink:collect"]
```

---

## 7. When NOT to Use Layer 0

### 7.1 Standard Conversion Workflow

For most language conversions, Layer 0 is unnecessary overhead:

```
Source Code
    |
    v
[Parser] --> Skip Layer 0
    |
    v
Layer 1: Data Flow IR   <-- Start here
    |
    v
Layer 2: Control Flow IR
    |
    v
Layer 3: Type IR
    |
    v
Layer 4: Structural IR
    |
    v
Target Code
```

### 7.2 Storage Cost Analysis

| Layer | Typical Size per Function | Notes |
|-------|---------------------------|-------|
| Layer 4 | ~100 bytes | Module metadata |
| Layer 3 | ~500 bytes | Type definitions |
| Layer 2 | ~1 KB | Control flow graph |
| Layer 1 | ~2 KB | Data flow nodes |
| **Layer 0** | **~10-50 KB** | Full AST with spans |

Layer 0 can be 5-25x larger than Layers 1-4 combined.

### 7.3 Recommended Approach

1. **Start without Layer 0** - Use Layers 1-4 for initial conversion
2. **Add Layer 0 selectively** - Only for functions with conversion issues
3. **Use Layer 0 for tooling** - IDEs, linters, and refactoring tools benefit
4. **Strip Layer 0 for storage** - Archive without expression details

---

## 8. Schema Summary

### 8.1 Complete Expression Schema

```yaml
expression:
  id: ExpressionId
  kind: literal | identifier | call | operator | lambda |
        member_access | index | cast | conditional |
        tuple | array | object | await | throw
  type: TypeRef
  span: SourceSpan

  # literal
  literal_kind: int | float | string | char | bool | null |
                regex | bigint | symbol | bytes | template
  literal_value: any

  # identifier
  binding_ref: BindingId
  name: string

  # call
  callee: Expression
  arguments: Argument[]
  type_arguments: TypeRef[]?

  # operator
  operator: string
  operator_kind: unary_prefix | unary_postfix | binary |
                 comparison | assignment | ternary
  operands: Expression[]

  # lambda
  params: Param[]
  body: Expression | ControlFlowGraph
  captures: Capture[]
  is_async: bool
  is_generator: bool

  # member_access
  object: Expression
  member: string

  # index
  collection: Expression
  index: Expression

  # cast
  target_type: TypeRef
  operand: Expression

  # conditional
  condition: Expression
  then_expr: Expression
  else_expr: Expression

  # tuple, array
  elements: Expression[]

  # object
  fields: ObjectField[]

  # await, throw
  operand: Expression

source_span:
  file: string
  start_line: int
  start_col: int
  end_line: int
  end_col: int

argument:
  name: string?
  value: Expression
  spread: bool

capture:
  binding_ref: BindingId
  capture_kind: by_value | by_ref | by_mut_ref

object_field:
  name: string
  value: Expression
  shorthand: bool
```

---

## 9. Cross-References

| Document | Relevance |
|----------|-----------|
| `overview.md` | Layer architecture context |
| `layer-1.md` | Data Flow IR (references Layer 0 expressions) |
| `layer-2.md` | Control Flow IR (function bodies) |
| `preservation-levels.md` | When expression fidelity matters |
| `binary-formats.md` | Serialization considerations |

---

*Generated for Phase 4: IR Schema Design (ai-f33.6)*
