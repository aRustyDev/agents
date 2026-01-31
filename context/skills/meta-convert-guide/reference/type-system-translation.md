# Type System Translation Reference

Guide for converting between static/dynamic and strong/weak type systems.

---

## Type System Classification

| Language   | Static/Dynamic | Strong/Weak | Inference Level |
| ---------- | -------------- | ----------- | --------------- |
| Haskell    | Static         | Strong      | Very strong     |
| Rust       | Static         | Strong      | Strong          |
| TypeScript | Static\*       | Strong      | Moderate        |
| Go         | Static         | Strong      | Minimal         |
| Python     | Dynamic        | Strong      | None (runtime)  |
| JavaScript | Dynamic        | Weak        | None            |
| Clojure    | Dynamic        | Strong      | None            |
| Elixir     | Dynamic        | Strong      | None            |

\*TypeScript is optionally typed and compiles to JavaScript

---

## Static → Dynamic Translation

### What Changes

| Static Pattern                  | Dynamic Approach  | Mitigation for Safety          |
| ------------------------------- | ----------------- | ------------------------------ |
| Compile-time type errors        | Runtime errors    | Add runtime validation         |
| Type annotations                | Optional/ignored  | Use type hints (Python), JSDoc |
| Generic constraints             | Duck typing       | Document expected interface    |
| Pattern matching exhaustiveness | Runtime failures  | Add catch-all cases            |
| Nullability tracking            | All refs nullable | Defensive null checks          |

### Translation Example

```typescript
// TypeScript: Static types
interface User {
  id: number;
  name: string;
  email: string;
}

function processUser(user: User): string {
  return `${user.name} <${user.email}>`;
}

// Compile error: Argument of type 'string' is not assignable
// processUser("not a user")
```

```python
# Python: Runtime typing with optional hints
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str

def process_user(user: User) -> str:
    # Type hints help but don't prevent runtime errors
    return f"{user.name} <{user.email}>"

# No compile error - fails at runtime
# process_user("not a user")  # AttributeError

# Add runtime validation for safety
def process_user_safe(user: User) -> str:
    if not isinstance(user, User):
        raise TypeError(f"Expected User, got {type(user)}")
    return f"{user.name} <{user.email}>"
```

---

## Dynamic → Static Translation

### Challenges

| Dynamic Pattern        | Static Challenge       | Solution                |
| ---------------------- | ---------------------- | ----------------------- |
| Dict with mixed types  | Need concrete type     | Define struct/interface |
| Duck typing            | Must declare interface | Create trait/interface  |
| Runtime type switching | Need sum type          | Use enum/union          |
| Optional fields        | All fields required    | Use Option<T>/Maybe     |
| Any/unknown data       | No escape hatch        | Use generics or enums   |

### Translation Example

```python
# Python: Dynamic, flexible structure
def process_event(event):
    event_type = event.get("type")
    if event_type == "click":
        return f"Clicked at {event['x']}, {event['y']}"
    elif event_type == "keypress":
        return f"Pressed key {event['key']}"
    else:
        return f"Unknown event: {event}"
```

```rust
// Rust: Must define all variants explicitly
#[derive(Debug)]
enum Event {
    Click { x: i32, y: i32 },
    Keypress { key: char },
    Unknown { raw: String },
}

fn process_event(event: Event) -> String {
    match event {
        Event::Click { x, y } => format!("Clicked at {}, {}", x, y),
        Event::Keypress { key } => format!("Pressed key {}", key),
        Event::Unknown { raw } => format!("Unknown event: {}", raw),
    }
}
```

---

## Type Inference Comparison

| Language   | Inference Level | Annotation Requirement                  |
| ---------- | --------------- | --------------------------------------- |
| Haskell    | Very strong     | Rarely needed (signatures recommended)  |
| Rust       | Strong          | Type annotations at function boundaries |
| TypeScript | Moderate        | Recommended at boundaries               |
| Go         | Minimal         | Required at function signatures         |
| Python     | None (runtime)  | Optional (mypy uses them)               |

### Inference Examples

```haskell
-- Haskell: Compiler infers everything
map f [] = []
map f (x:xs) = f x : map f xs
-- Inferred: map :: (a -> b) -> [a] -> [b]
```

```rust
// Rust: Local inference, explicit at boundaries
fn transform(items: Vec<i32>) -> Vec<i32> {
    items.iter()           // Inferred: Iter<&i32>
         .map(|x| x * 2)   // Inferred: Map<..., closure>
         .collect()        // Needs turbofish OR return type
}
```

```go
// Go: Minimal inference, mostly explicit
func transform(items []int) []int {
    result := make([]int, len(items))  // := infers type
    for i, v := range items {
        result[i] = v * 2
    }
    return result
}
```

---

## Gradual Typing Strategies

For languages with optional typing (Python, TypeScript):

### Phased Migration

```python
# Phase 1: No types (original)
def fetch_users(filters):
    results = db.query(filters)
    return [transform(r) for r in results]

# Phase 2: Return type only
def fetch_users(filters) -> list[User]:
    results = db.query(filters)
    return [transform(r) for r in results]

# Phase 3: Full typing
def fetch_users(filters: UserFilters) -> list[User]:
    results: list[DbRow] = db.query(filters)
    return [transform(r) for r in results]

# Phase 4: Runtime validation (strict mode)
from pydantic import BaseModel

class UserFilters(BaseModel):
    active: bool = True
    role: str | None = None

def fetch_users(filters: UserFilters) -> list[User]:
    # Pydantic validates at runtime
    ...
```

---

## Handling Dynamic Features

### `any` Type

| Language   | `any` equivalent      | Static alternative   |
| ---------- | --------------------- | -------------------- |
| TypeScript | `any`, `unknown`      | Generics, unions     |
| Python     | No enforcement        | Type hints           |
| Rust       | None                  | Enums, trait objects |
| Go         | `interface{}` / `any` | Generics (1.18+)     |

### Translation

```typescript
// TypeScript: any escape hatch
function process(data: any): any {
  return data.transform();
}
```

```rust
// Rust: Must be explicit
// Option 1: Trait object (runtime dispatch)
fn process(data: &dyn Transformable) -> Box<dyn Output> {
    data.transform()
}

// Option 2: Generic (compile-time dispatch)
fn process<T: Transformable>(data: T) -> T::Output {
    data.transform()
}

// Option 3: Enum (closed set of types)
enum Data {
    String(String),
    Number(i64),
    Object(HashMap<String, Data>),
}
```

---

## Null Safety

| Language   | Null Representation | Static Safety                  |
| ---------- | ------------------- | ------------------------------ |
| TypeScript | `null`, `undefined` | Optional with strictNullChecks |
| Rust       | `Option<T>`         | Required                       |
| Go         | `nil`               | No (runtime check)             |
| Python     | `None`              | Optional with type hints       |
| Kotlin     | `T?`                | Required                       |
| Swift      | `T?`                | Required                       |

### Migration Pattern

```typescript
// TypeScript: Nullable
function getUser(id: string): User | null {
  return db.find(id);
}

const user = getUser("123");
if (user) {
  console.log(user.name); // TypeScript knows user is not null
}
```

```rust
// Rust: Option<T>
fn get_user(id: &str) -> Option<User> {
    db.find(id)
}

if let Some(user) = get_user("123") {
    println!("{}", user.name);
}

// Or with combinators
get_user("123")
    .map(|u| println!("{}", u.name));
```

---

## Pattern Matching Exhaustiveness

### Static Languages

```rust
// Rust: Compiler enforces exhaustiveness
enum Status {
    Active,
    Inactive,
    Pending,
}

fn handle(status: Status) -> &'static str {
    match status {
        Status::Active => "active",
        Status::Inactive => "inactive",
        // Compile error if Pending not handled
    }
}
```

### Dynamic Languages

```python
# Python: Must add catch-all manually
from enum import Enum

class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

def handle(status: Status) -> str:
    match status:
        case Status.ACTIVE:
            return "active"
        case Status.INACTIVE:
            return "inactive"
        case Status.PENDING:
            return "pending"
        case _:  # Must add for safety
            raise ValueError(f"Unknown status: {status}")
```
