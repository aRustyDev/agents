# Layer 2: Control Flow IR

The Control Flow IR represents function signatures, effect annotations, and the structural flow of execution within code.

**Version:** 1.0
**Generated:** 2026-02-04
**Task:** ai-f33.4

---

## 1. Overview

Layer 2 sits at the center of the IR architecture, bridging type definitions (Layer 3) with data flow analysis (Layer 1). It captures:

- **Function signatures** - Parameters, return types, receivers, generic constraints
- **Effect annotations** - Purity, exceptions, async, unsafe, and other computational effects
- **Control flow graphs** - Basic blocks, terminators, branching structure
- **Concurrency patterns** - Spawn, await, channels, and synchronization points

```
Layer 3: Type IR
     |
     v
Layer 2: Control Flow IR  <-- This document
     |
     v
Layer 1: Data Flow IR
```

### 1.1 Design Principles

1. **Effect-explicit**: Every function tracks its effects, enabling accurate conversion between effect systems
2. **CFG-based bodies**: Function bodies use control flow graphs for language-agnostic representation
3. **Receiver-aware**: Methods and free functions have uniform representation with optional receivers
4. **Mutability-tracked**: Parameter mutability is explicit for ownership conversion

### 1.2 Key Constructs

| Construct | Purpose | Reference |
|-----------|---------|-----------|
| `function` | Complete function/method definition | Section 2 |
| `param` | Parameter with type and mutability | Section 3 |
| `effect` | Computational effect annotation | Section 4 |
| `control_flow_graph` | Function body structure | Section 5 |
| `terminator` | Block ending instruction | Section 6 |

---

## 2. Function Schema

The `function` schema captures complete function definitions, including methods with receivers.

### 2.1 Complete Schema

```yaml
function:
  id: FunctionId
  name: string
  params: Param[]
  return_type: TypeRef
  type_params: TypeParam[]
  effects: Effect[]
  body: ControlFlowGraph?
  visibility: Visibility
  receiver: Receiver?

  # Metadata
  source_span: SourceSpan?
  annotations: SemanticAnnotation[]
  doc_comment: string?
```

### 2.2 Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | FunctionId | Yes | Unique identifier within the IR |
| `name` | string | Yes | Function name (may be empty for lambdas) |
| `params` | Param[] | Yes | Ordered list of parameters (may be empty) |
| `return_type` | TypeRef | Yes | Return type (use `unit` or `void` for no return) |
| `type_params` | TypeParam[] | No | Generic type parameters |
| `effects` | Effect[] | Yes | List of effects (empty means pure by default) |
| `body` | ControlFlowGraph | No | Function body (None for declarations/extern) |
| `visibility` | Visibility | Yes | Access level |
| `receiver` | Receiver | No | Self/this parameter for methods |

### 2.3 Visibility Values

```yaml
visibility:
  kind: public | private | protected | internal | package
  scope: ModuleId?  # For internal/package visibility
```

### 2.4 Example: Simple Function

**Source (TypeScript):**
```typescript
export function greet(name: string): string {
    return `Hello, ${name}!`;
}
```

**IR Representation:**
```yaml
function:
  id: "fn:greet"
  name: "greet"
  params:
    - name: "name"
      type: { kind: "named", type_id: "type:string" }
      mutability: "immutable"
  return_type: { kind: "named", type_id: "type:string" }
  type_params: []
  effects: []  # Pure function
  visibility: { kind: "public" }
  body:
    entry: "block:0"
    blocks:
      - id: "block:0"
        statements: []
        terminator:
          kind: "return"
          value: { kind: "string_interpolation", parts: ["Hello, ", { ref: "name" }, "!"] }
    exit: "block:0"
```

---

## 3. Parameters

Parameters capture argument definitions with mutability modes and optional defaults.

### 3.1 Parameter Schema

```yaml
param:
  name: string
  type: TypeRef
  default: Expression?
  mutability: mutable | immutable | move

  # Optional metadata
  variadic: boolean?
  annotations: SemanticAnnotation[]
```

### 3.2 Mutability Modes

| Mode | Semantics | Source Examples |
|------|-----------|-----------------|
| `immutable` | Read-only access, no modification allowed | Rust `&T`, Java `final`, Go default |
| `mutable` | Can be modified in place | Rust `&mut T`, C `*`, Python default |
| `move` | Ownership transferred, no further access | Rust by-value, C++ `std::move` |

### 3.3 Default Values

Default values are optional expressions evaluated when argument is omitted.

```yaml
param:
  name: "timeout"
  type: { kind: "named", type_id: "type:i32" }
  default:
    kind: "literal"
    value: 30
  mutability: "immutable"
```

### 3.4 Receiver for Methods

Methods have an implicit `receiver` parameter representing `self`/`this`.

```yaml
receiver:
  type: TypeRef
  mutability: mutable | immutable | move
  name: string?  # Usually "self", "this", or omitted
```

**Example: Method with Mutable Receiver (Rust)**

```rust
impl Counter {
    fn increment(&mut self) -> u32 {
        self.count += 1;
        self.count
    }
}
```

```yaml
function:
  id: "fn:Counter::increment"
  name: "increment"
  params: []
  return_type: { kind: "named", type_id: "type:u32" }
  receiver:
    type: { kind: "named", type_id: "type:Counter" }
    mutability: "mutable"
    name: "self"
  effects: []
  visibility: { kind: "public" }
```

**Example: Method with Immutable Receiver (Go)**

```go
func (c Counter) Get() uint32 {
    return c.count
}
```

```yaml
function:
  id: "fn:Counter::Get"
  name: "Get"
  params: []
  return_type: { kind: "named", type_id: "type:uint32" }
  receiver:
    type: { kind: "named", type_id: "type:Counter" }
    mutability: "immutable"
    name: "c"
  effects: []
  visibility: { kind: "public" }
```

---

## 4. Effect System

Effects annotate the computational side effects a function may produce.

### 4.1 Effect Schema

```yaml
effect:
  kind: pure | throws | async | unsafe | io | suspends | allocates | captures
  type: TypeRef?  # For effects with associated types (e.g., throws(ErrorType))

  # Optional metadata
  source: explicit | inferred | default
  confidence: float?  # For inferred effects
```

### 4.2 Effect Kinds

#### 4.2.1 `pure`

Function has no observable side effects. Output depends only on inputs.

**Languages with explicit purity:** Haskell (default), PureScript, Elm

**IR Example:**
```yaml
effects: []  # Empty effects list implies pure
```

Note: An empty `effects` array indicates a pure function. The `pure` effect kind is used when explicitly marking purity is needed for clarity or when converting from languages where purity is marked.

#### 4.2.2 `throws`

Function may raise exceptions or return error values.

**Languages:** Java (checked exceptions), Python, TypeScript, Kotlin

```yaml
effect:
  kind: "throws"
  type: { kind: "named", type_id: "type:IOException" }
```

**Multiple Exception Types:**
```yaml
effects:
  - kind: "throws"
    type: { kind: "named", type_id: "type:FileNotFoundException" }
  - kind: "throws"
    type: { kind: "named", type_id: "type:PermissionDeniedException" }
```

#### 4.2.3 `async`

Function performs asynchronous operations, returns Future/Promise.

**Languages:** TypeScript/JavaScript (async), Rust (async fn), Python (async def)

```yaml
effect:
  kind: "async"
  type: { kind: "generic", type_id: "type:Future", args: [{ kind: "named", type_id: "type:Response" }] }
```

#### 4.2.4 `unsafe`

Function performs operations that bypass safety guarantees.

**Languages:** Rust (unsafe fn), C (default), Zig

```yaml
effect:
  kind: "unsafe"
```

#### 4.2.5 `io`

Function performs input/output operations.

**Languages:** Haskell (IO monad), Koka, Clean

```yaml
effect:
  kind: "io"
  type: { kind: "generic", type_id: "type:IO", args: [{ kind: "named", type_id: "type:String" }] }
```

#### 4.2.6 `suspends`

Function may suspend execution (coroutines, generators).

**Languages:** Kotlin (suspend), Python (yield)

```yaml
effect:
  kind: "suspends"
```

#### 4.2.7 `allocates`

Function performs heap allocation.

**Languages:** Zig (explicit allocators), Rust (with global allocator)

```yaml
effect:
  kind: "allocates"
  type: { kind: "named", type_id: "type:Allocator" }
```

#### 4.2.8 `captures`

Function captures variables from enclosing scope (closures).

**Languages:** All languages with closures

```yaml
effect:
  kind: "captures"
  type: null  # Captured variables tracked in closure metadata
```

### 4.3 Effect Combinations

Functions may have multiple effects:

```yaml
# Async function that may throw
effects:
  - kind: "async"
  - kind: "throws"
    type: { kind: "named", type_id: "type:NetworkError" }
```

### 4.4 Effect Inference

For languages without explicit effect annotations, effects are inferred:

```yaml
effect:
  kind: "io"
  source: "inferred"
  confidence: 0.95
  evidence:
    - "line 42: print() call detected"
    - "line 58: file.write() call detected"
```

---

## 5. Control Flow Graph

Function bodies are represented as control flow graphs (CFGs) for language-agnostic analysis.

### 5.1 CFG Schema

```yaml
control_flow_graph:
  entry: BlockId
  blocks: Block[]
  exit: BlockId
```

### 5.2 Block Schema

```yaml
block:
  id: BlockId
  statements: Statement[]
  terminator: Terminator

  # Optional metadata
  loop_depth: int?
  exception_handler: BlockId?
```

### 5.3 Statement Types

Statements are non-branching instructions within a block.

```yaml
statement:
  kind: assign | call | alloc | dealloc | noop

  # For assign
  target: BindingId
  value: Expression

  # For call (non-returning or result discarded)
  callee: Expression
  arguments: Expression[]
```

### 5.4 CFG Example

**Source (Python):**
```python
def abs_value(x: int) -> int:
    if x < 0:
        return -x
    else:
        return x
```

**CFG Representation:**
```yaml
control_flow_graph:
  entry: "block:entry"
  blocks:
    - id: "block:entry"
      statements: []
      terminator:
        kind: "branch"
        condition: { kind: "binary_op", op: "<", left: { ref: "x" }, right: { literal: 0 } }
        then_block: "block:negative"
        else_block: "block:positive"

    - id: "block:negative"
      statements: []
      terminator:
        kind: "return"
        value: { kind: "unary_op", op: "-", operand: { ref: "x" } }

    - id: "block:positive"
      statements: []
      terminator:
        kind: "return"
        value: { ref: "x" }

  exit: null  # Both paths return, no single exit block
```

---

## 6. Terminators

Terminators define how control exits a block.

### 6.1 Terminator Schema

```yaml
terminator:
  kind: return | branch | switch | loop | try | unreachable

  # Kind-specific fields below
```

### 6.2 Return Terminator

Exits the function with an optional value.

```yaml
terminator:
  kind: "return"
  value: Expression?  # None for void/unit returns
```

**Example:**
```yaml
terminator:
  kind: "return"
  value:
    kind: "call"
    callee: { ref: "compute_result" }
    arguments: [{ ref: "input" }]
```

### 6.3 Branch Terminator

Conditional branch to one of two blocks.

```yaml
terminator:
  kind: "branch"
  condition: Expression  # Must evaluate to boolean
  then_block: BlockId
  else_block: BlockId?   # None for unconditional jumps to then_block
```

**Example (if-else):**
```yaml
terminator:
  kind: "branch"
  condition: { kind: "call", callee: { ref: "is_valid" }, arguments: [{ ref: "data" }] }
  then_block: "block:process"
  else_block: "block:error"
```

**Example (unconditional jump):**
```yaml
terminator:
  kind: "branch"
  condition: { kind: "literal", value: true }
  then_block: "block:next"
  else_block: null
```

### 6.4 Switch/Match Terminator

Multi-way branch based on pattern matching or value comparison.

```yaml
terminator:
  kind: "switch"
  scrutinee: Expression
  arms: SwitchArm[]
  default_block: BlockId?

switch_arm:
  pattern: Pattern
  guard: Expression?
  target: BlockId
```

**Example (Rust match):**

```rust
match status {
    Status::Ok(value) => process(value),
    Status::Error(e) => handle_error(e),
    Status::Pending => wait(),
}
```

```yaml
terminator:
  kind: "switch"
  scrutinee: { ref: "status" }
  arms:
    - pattern: { kind: "variant", type: "Status", variant: "Ok", bindings: ["value"] }
      target: "block:process"
    - pattern: { kind: "variant", type: "Status", variant: "Error", bindings: ["e"] }
      target: "block:handle_error"
    - pattern: { kind: "variant", type: "Status", variant: "Pending", bindings: [] }
      target: "block:wait"
  default_block: null  # Exhaustive match
```

**Example (TypeScript switch):**

```typescript
switch (code) {
    case 200: return "OK";
    case 404: return "Not Found";
    default: return "Unknown";
}
```

```yaml
terminator:
  kind: "switch"
  scrutinee: { ref: "code" }
  arms:
    - pattern: { kind: "literal", value: 200 }
      target: "block:ok"
    - pattern: { kind: "literal", value: 404 }
      target: "block:not_found"
  default_block: "block:unknown"
```

### 6.5 Loop Terminator

Represents loop constructs with explicit continue/break targets.

```yaml
terminator:
  kind: "loop"
  body: BlockId
  continue_target: BlockId  # Where 'continue' jumps to
  break_target: BlockId     # Where 'break' jumps to

  # Optional loop metadata
  loop_kind: while | for | loop  # Hint for code generation
```

**Example (while loop):**

```python
while x > 0:
    x = x - 1
    if x == 5:
        break
```

```yaml
blocks:
  - id: "block:loop_header"
    statements: []
    terminator:
      kind: "branch"
      condition: { kind: "binary_op", op: ">", left: { ref: "x" }, right: { literal: 0 } }
      then_block: "block:loop_body"
      else_block: "block:after_loop"

  - id: "block:loop_body"
    statements:
      - kind: "assign"
        target: "x"
        value: { kind: "binary_op", op: "-", left: { ref: "x" }, right: { literal: 1 } }
    terminator:
      kind: "branch"
      condition: { kind: "binary_op", op: "==", left: { ref: "x" }, right: { literal: 5 } }
      then_block: "block:after_loop"  # break
      else_block: "block:loop_header"  # continue

  - id: "block:after_loop"
    statements: []
    terminator:
      kind: "return"
      value: null
```

### 6.6 Try Terminator

Structured exception handling with catch and finally blocks.

```yaml
terminator:
  kind: "try"
  try_block: BlockId
  catch_blocks: CatchBlock[]
  finally_block: BlockId?

catch_block:
  exception_type: TypeRef
  binding: BindingId?  # Variable to bind caught exception
  handler_block: BlockId
```

**Example (Java try-catch-finally):**

```java
try {
    data = readFile(path);
} catch (FileNotFoundException e) {
    data = getDefault();
} catch (IOException e) {
    throw new RuntimeException(e);
} finally {
    cleanup();
}
```

```yaml
terminator:
  kind: "try"
  try_block: "block:try_body"
  catch_blocks:
    - exception_type: { kind: "named", type_id: "type:FileNotFoundException" }
      binding: "e"
      handler_block: "block:catch_fnf"
    - exception_type: { kind: "named", type_id: "type:IOException" }
      binding: "e"
      handler_block: "block:catch_io"
  finally_block: "block:finally"
```

### 6.7 Unreachable Terminator

Marks code paths that should never execute.

```yaml
terminator:
  kind: "unreachable"
  reason: string?  # Optional explanation
```

**Example (after exhaustive match or panic):**
```yaml
terminator:
  kind: "unreachable"
  reason: "All enum variants handled above"
```

---

## 7. Language Examples

### 7.1 Async Function (TypeScript)

**Source:**
```typescript
async function fetchUser(id: string): Promise<User> {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) {
        throw new HttpError(response.status);
    }
    return await response.json();
}
```

**IR Representation:**
```yaml
function:
  id: "fn:fetchUser"
  name: "fetchUser"
  params:
    - name: "id"
      type: { kind: "named", type_id: "type:string" }
      mutability: "immutable"
  return_type:
    kind: "generic"
    type_id: "type:Promise"
    args: [{ kind: "named", type_id: "type:User" }]
  effects:
    - kind: "async"
    - kind: "throws"
      type: { kind: "named", type_id: "type:HttpError" }
  body:
    entry: "block:0"
    blocks:
      - id: "block:0"
        statements:
          - kind: "assign"
            target: "response"
            value:
              kind: "await"
              expr:
                kind: "call"
                callee: { ref: "fetch" }
                arguments: [{ kind: "string_interpolation", parts: ["/api/users/", { ref: "id" }] }]
        terminator:
          kind: "branch"
          condition: { kind: "unary_op", op: "!", operand: { kind: "field_access", object: { ref: "response" }, field: "ok" } }
          then_block: "block:error"
          else_block: "block:success"

      - id: "block:error"
        statements: []
        terminator:
          kind: "return"
          value:
            kind: "throw"
            expr:
              kind: "construct"
              type: "HttpError"
              arguments: [{ kind: "field_access", object: { ref: "response" }, field: "status" }]

      - id: "block:success"
        statements: []
        terminator:
          kind: "return"
          value:
            kind: "await"
            expr:
              kind: "call"
              callee: { kind: "method", object: { ref: "response" }, method: "json" }
              arguments: []
    exit: null
```

### 7.2 Function with Exceptions (Java)

**Source:**
```java
public User findUser(String id) throws UserNotFoundException, DatabaseException {
    Connection conn = database.getConnection();
    try {
        ResultSet rs = conn.query("SELECT * FROM users WHERE id = ?", id);
        if (!rs.next()) {
            throw new UserNotFoundException(id);
        }
        return User.fromResultSet(rs);
    } finally {
        conn.close();
    }
}
```

**IR Representation:**
```yaml
function:
  id: "fn:findUser"
  name: "findUser"
  params:
    - name: "id"
      type: { kind: "named", type_id: "type:String" }
      mutability: "immutable"
  return_type: { kind: "named", type_id: "type:User" }
  receiver:
    type: { kind: "named", type_id: "type:UserRepository" }
    mutability: "immutable"
    name: "this"
  effects:
    - kind: "throws"
      type: { kind: "named", type_id: "type:UserNotFoundException" }
    - kind: "throws"
      type: { kind: "named", type_id: "type:DatabaseException" }
  visibility: { kind: "public" }
  body:
    entry: "block:0"
    blocks:
      - id: "block:0"
        statements:
          - kind: "assign"
            target: "conn"
            value:
              kind: "call"
              callee: { kind: "method", object: { ref: "database" }, method: "getConnection" }
              arguments: []
        terminator:
          kind: "try"
          try_block: "block:try"
          catch_blocks: []
          finally_block: "block:finally"

      - id: "block:try"
        statements:
          - kind: "assign"
            target: "rs"
            value:
              kind: "call"
              callee: { kind: "method", object: { ref: "conn" }, method: "query" }
              arguments:
                - { literal: "SELECT * FROM users WHERE id = ?" }
                - { ref: "id" }
        terminator:
          kind: "branch"
          condition:
            kind: "unary_op"
            op: "!"
            operand: { kind: "call", callee: { kind: "method", object: { ref: "rs" }, method: "next" }, arguments: [] }
          then_block: "block:not_found"
          else_block: "block:found"

      - id: "block:not_found"
        statements: []
        terminator:
          kind: "return"
          value:
            kind: "throw"
            expr:
              kind: "construct"
              type: "UserNotFoundException"
              arguments: [{ ref: "id" }]

      - id: "block:found"
        statements: []
        terminator:
          kind: "return"
          value:
            kind: "call"
            callee: { ref: "User.fromResultSet" }
            arguments: [{ ref: "rs" }]

      - id: "block:finally"
        statements:
          - kind: "call"
            callee: { kind: "method", object: { ref: "conn" }, method: "close" }
            arguments: []
        terminator:
          kind: "branch"
          condition: { literal: true }
          then_block: "block:exit"
          else_block: null
    exit: "block:exit"
```

### 7.3 Pure Function (Haskell)

**Source:**
```haskell
quicksort :: Ord a => [a] -> [a]
quicksort []     = []
quicksort (x:xs) = quicksort smaller ++ [x] ++ quicksort larger
  where
    smaller = [y | y <- xs, y <= x]
    larger  = [y | y <- xs, y > x]
```

**IR Representation:**
```yaml
function:
  id: "fn:quicksort"
  name: "quicksort"
  params:
    - name: "list"
      type:
        kind: "generic"
        type_id: "type:List"
        args: [{ kind: "type_param", name: "a" }]
      mutability: "immutable"
  return_type:
    kind: "generic"
    type_id: "type:List"
    args: [{ kind: "type_param", name: "a" }]
  type_params:
    - name: "a"
      bounds: [{ kind: "named", type_id: "type:Ord" }]
  effects: []  # Pure function - no effects
  body:
    entry: "block:0"
    blocks:
      - id: "block:0"
        statements: []
        terminator:
          kind: "switch"
          scrutinee: { ref: "list" }
          arms:
            - pattern: { kind: "constructor", name: "Nil", bindings: [] }
              target: "block:empty"
            - pattern: { kind: "constructor", name: "Cons", bindings: ["x", "xs"] }
              target: "block:cons"
          default_block: null

      - id: "block:empty"
        statements: []
        terminator:
          kind: "return"
          value: { kind: "construct", type: "List", variant: "Nil" }

      - id: "block:cons"
        statements:
          - kind: "assign"
            target: "smaller"
            value:
              kind: "list_comprehension"
              element: { ref: "y" }
              source: { ref: "xs" }
              binding: "y"
              filter: { kind: "binary_op", op: "<=", left: { ref: "y" }, right: { ref: "x" } }
          - kind: "assign"
            target: "larger"
            value:
              kind: "list_comprehension"
              element: { ref: "y" }
              source: { ref: "xs" }
              binding: "y"
              filter: { kind: "binary_op", op: ">", left: { ref: "y" }, right: { ref: "x" } }
        terminator:
          kind: "return"
          value:
            kind: "binary_op"
            op: "++"
            left:
              kind: "call"
              callee: { ref: "quicksort" }
              arguments: [{ ref: "smaller" }]
            right:
              kind: "binary_op"
              op: "++"
              left: { kind: "list", elements: [{ ref: "x" }] }
              right:
                kind: "call"
                callee: { ref: "quicksort" }
                arguments: [{ ref: "larger" }]
    exit: null
```

### 7.4 Method with Receiver (Rust)

**Source:**
```rust
impl Cache<K, V> {
    pub fn get_or_insert<F>(&mut self, key: K, default: F) -> &V
    where
        F: FnOnce() -> V,
    {
        if !self.data.contains_key(&key) {
            let value = default();
            self.data.insert(key.clone(), value);
        }
        self.data.get(&key).unwrap()
    }
}
```

**IR Representation:**
```yaml
function:
  id: "fn:Cache::get_or_insert"
  name: "get_or_insert"
  receiver:
    type:
      kind: "generic"
      type_id: "type:Cache"
      args:
        - { kind: "type_param", name: "K" }
        - { kind: "type_param", name: "V" }
    mutability: "mutable"
    name: "self"
  params:
    - name: "key"
      type: { kind: "type_param", name: "K" }
      mutability: "move"
    - name: "default"
      type: { kind: "type_param", name: "F" }
      mutability: "move"
  return_type:
    kind: "reference"
    inner: { kind: "type_param", name: "V" }
    mutability: "immutable"
  type_params:
    - name: "K"
      bounds: []
    - name: "V"
      bounds: []
    - name: "F"
      bounds:
        - kind: "function"
          params: []
          return_type: { kind: "type_param", name: "V" }
  effects: []
  visibility: { kind: "public" }
  body:
    entry: "block:0"
    blocks:
      - id: "block:0"
        statements: []
        terminator:
          kind: "branch"
          condition:
            kind: "unary_op"
            op: "!"
            operand:
              kind: "call"
              callee: { kind: "method", object: { ref: "self.data" }, method: "contains_key" }
              arguments: [{ kind: "borrow", expr: { ref: "key" }, mutability: "immutable" }]
          then_block: "block:insert"
          else_block: "block:get"

      - id: "block:insert"
        statements:
          - kind: "assign"
            target: "value"
            value:
              kind: "call"
              callee: { ref: "default" }
              arguments: []
          - kind: "call"
            callee: { kind: "method", object: { ref: "self.data" }, method: "insert" }
            arguments:
              - { kind: "call", callee: { kind: "method", object: { ref: "key" }, method: "clone" }, arguments: [] }
              - { ref: "value" }
        terminator:
          kind: "branch"
          condition: { literal: true }
          then_block: "block:get"
          else_block: null

      - id: "block:get"
        statements: []
        terminator:
          kind: "return"
          value:
            kind: "call"
            callee: { ref: "unwrap" }
            arguments:
              - kind: "call"
                callee: { kind: "method", object: { ref: "self.data" }, method: "get" }
                arguments: [{ kind: "borrow", expr: { ref: "key" }, mutability: "immutable" }]
    exit: null
```

---

## 8. Concurrency Patterns

Layer 2 represents concurrency primitives in a language-agnostic way.

### 8.1 Spawn

Creating concurrent tasks or threads.

```yaml
spawn:
  kind: goroutine | thread | task | actor | process
  target: Expression  # Function or closure to execute
  arguments: Expression[]
  result_binding: BindingId?  # Handle to the spawned task
```

**Example (Go goroutine):**
```go
go process(item)
```

```yaml
statement:
  kind: "spawn"
  spawn:
    kind: "goroutine"
    target: { ref: "process" }
    arguments: [{ ref: "item" }]
    result_binding: null  # Fire and forget
```

### 8.2 Await

Waiting for async operations to complete.

```yaml
await:
  expr: Expression  # Future/Promise/Task to await
  timeout: Expression?  # Optional timeout duration
```

**Example (Rust async):**
```rust
let result = future.await;
```

```yaml
statement:
  kind: "assign"
  target: "result"
  value:
    kind: "await"
    expr: { ref: "future" }
    timeout: null
```

### 8.3 Channel Operations

CSP-style channel communication.

```yaml
channel_send:
  channel: Expression
  value: Expression
  blocking: boolean

channel_recv:
  channel: Expression
  blocking: boolean
  result_binding: BindingId
```

**Example (Go channel):**
```go
ch <- value  // send
x := <-ch    // receive
```

```yaml
# Send
statement:
  kind: "channel_send"
  channel: { ref: "ch" }
  value: { ref: "value" }
  blocking: true

# Receive
statement:
  kind: "assign"
  target: "x"
  value:
    kind: "channel_recv"
    channel: { ref: "ch" }
    blocking: true
```

### 8.4 Select/Race

Waiting on multiple concurrent operations.

```yaml
select:
  arms: SelectArm[]
  default_block: BlockId?  # Non-blocking fallback

select_arm:
  kind: recv | send | timeout
  channel: Expression?
  value: Expression?
  timeout_duration: Expression?
  target_block: BlockId
```

**Example (Go select):**
```go
select {
case msg := <-msgCh:
    process(msg)
case <-done:
    return
case <-time.After(timeout):
    handleTimeout()
}
```

```yaml
terminator:
  kind: "select"
  arms:
    - kind: "recv"
      channel: { ref: "msgCh" }
      binding: "msg"
      target_block: "block:process"
    - kind: "recv"
      channel: { ref: "done" }
      target_block: "block:return"
    - kind: "timeout"
      timeout_duration: { ref: "timeout" }
      target_block: "block:timeout"
  default_block: null
```

---

## 9. Semantic Annotations

Layer 2 functions can carry semantic annotations from the gap pattern system.

### 9.1 Effect-Related Annotations

| Annotation | Pattern | Purpose |
|------------|---------|---------|
| `@error_handling_conversion` | EF-001 | Track exception to Result conversion |
| `@monad_flattening` | EF-004 | Track monadic effect unwrapping |
| `@evaluation_strategy` | EF-009 | Track lazy to strict conversion |
| `@sync_to_async` | EF-011 | Track synchronous to async conversion |

### 9.2 Concurrency Annotations

| Annotation | Pattern | Purpose |
|------------|---------|---------|
| `@concurrency_model_conversion` | CC-001 | Track actor to thread conversion |
| `@csp_to_async` | CC-004 | Track channel to async conversion |
| `@supervision_conversion` | CC-009 | Track supervision tree handling |

### 9.3 Example with Annotations

```yaml
function:
  id: "fn:process_data"
  name: "process_data"
  annotations:
    - kind: "@error_handling_conversion"
      value:
        source_pattern: "throws"
        target_pattern: "Result<T, E>"
        exceptions:
          - type: "IOException"
            maps_to: "IoError"
        propagation: "? operator"
      confidence: 1.0
      source: "explicit"
    - kind: "@sync_to_async"
      value:
        original: "blocking_read()"
        converted: "async_read().await"
        concurrency_impact: "non-blocking"
      confidence: 0.9
      source: "inferred"
```

---

## 10. Cross-References

### Related Documents

| Document | Relationship |
|----------|--------------|
| `overview.md` | Layer 2 position in architecture |
| `layer-1.md` | Data flow within function bodies |
| `layer-3.md` | Type definitions used by functions |
| `gap-patterns.md` | Effect and concurrency patterns (EF-*, CC-*) |
| `ir-implications.md` | Annotation requirements |

### Schema Dependencies

```
TypeRef      <- Used in return_type, param.type, effect.type
TypeParam    <- Used in type_params
SourceSpan   <- Used for source location tracking
Expression   <- Used in CFG statements and terminators
BindingId    <- References to Layer 1 bindings
```

---

*Generated for Phase 4: IR Schema Design (ai-f33.4)*
