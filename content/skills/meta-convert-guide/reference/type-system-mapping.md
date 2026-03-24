# Type System Mapping Strategies

Comprehensive strategies for mapping types between languages.

---

## Primitive Type Mappings

Create a complete primitive mapping table for each language pair.

### Example: TypeScript → Rust

| TypeScript  | Rust     | Notes                          |
|-------------|----------|--------------------------------|
| `string`    | `String` | Owned, heap-allocated          |
| `string`    | `&str`   | Borrowed, for parameters       |
| `number`    | `i32`    | Default integer                |
| `number`    | `i64`    | Large integers                 |
| `number`    | `f64`    | Floating point                 |
| `boolean`   | `bool`   | Direct mapping                 |
| `null`      | -        | Use Option<T>                  |
| `undefined` | -        | Use Option<T>                  |
| `any`       | -        | Avoid; use generics or enums   |
| `unknown`   | -        | Use generics with trait bounds |
| `never`     | `!`      | Never type (unstable)          |
| `void`      | `()`     | Unit type                      |

### Example: Python → Rust

| Python      | Rust            | Notes                    |
|-------------|-----------------|--------------------------|
| `str`       | `String`        | Owned string             |
| `str`       | `&str`          | Borrowed string          |
| `int`       | `i64`           | Python ints are unbounded|
| `int`       | `BigInt`        | For truly large ints     |
| `float`     | `f64`           | 64-bit float             |
| `bool`      | `bool`          | Direct mapping           |
| `None`      | `Option::None`  | Explicit optionality     |
| `Any`       | -               | Use generics             |
| `bytes`     | `Vec<u8>`       | Byte vector              |
| `bytes`     | `&[u8]`         | Borrowed bytes           |

### Example: Go → Rust

| Go          | Rust            | Notes                    |
|-------------|-----------------|--------------------------|
| `string`    | `String`        | Owned                    |
| `string`    | `&str`          | Borrowed                 |
| `int`       | `isize`         | Platform-dependent       |
| `int32`     | `i32`           | Direct mapping           |
| `int64`     | `i64`           | Direct mapping           |
| `float64`   | `f64`           | Direct mapping           |
| `bool`      | `bool`          | Direct mapping           |
| `nil`       | `Option::None`  | Explicit optionality     |
| `[]byte`    | `Vec<u8>`       | Byte vector              |
| `error`     | `Result<T, E>`  | Error as return value    |

---

## Composite Type Mappings

### Collections

| TypeScript     | Rust                    | Python           | Go               |
|----------------|-------------------------|------------------|------------------|
| `T[]`          | `Vec<T>`                | `list[T]`        | `[]T`            |
| `readonly T[]` | `&[T]`                  | `tuple[T, ...]`  | -                |
| `[T, U]`       | `(T, U)`                | `tuple[T, U]`    | struct           |
| `Record<K, V>` | `HashMap<K, V>`         | `dict[K, V]`     | `map[K]V`        |
| `Map<K, V>`    | `HashMap<K, V>`         | `dict[K, V]`     | `map[K]V`        |
| `Set<T>`       | `HashSet<T>`            | `set[T]`         | `map[T]struct{}` |

### Union Types

| TypeScript     | Rust                    | Python           | Go               |
|----------------|-------------------------|------------------|------------------|
| `T \| U`       | `enum { A(T), B(U) }`   | `Union[T, U]`    | interface        |
| `T \| null`    | `Option<T>`             | `Optional[T]`    | `*T` (pointer)   |
| `T & U`        | `struct { ...T, ...U }` | Multiple inherit | Embedding        |

---

## Interface/Class to Struct/Trait

### Structural Mappings

| TypeScript Pattern            | Rust Pattern                        | When to Use             |
|-------------------------------|-------------------------------------|-------------------------|
| `interface X { ... }`         | `struct X { ... }`                  | Data-only types         |
| `interface X { method(): T }` | `trait X { fn method(&self) -> T }` | Behavior contracts      |
| `class X implements Y`        | `struct X` + `impl Y for X`         | Implementation          |
| `class X extends Y`           | Composition over inheritance        | Rust avoids inheritance |
| `abstract class X`            | `trait X`                           | Abstract contracts      |

### Data Types

```typescript
// TypeScript: Data interface
interface User {
  id: string;
  name: string;
  email: string;
}
```

```rust
// Rust: Struct
struct User {
    id: String,
    name: String,
    email: String,
}
```

### Behavior Contracts

```typescript
// TypeScript: Interface with methods
interface Repository<T> {
  find(id: string): Promise<T | null>;
  save(item: T): Promise<void>;
}
```

```rust
// Rust: Trait
trait Repository<T> {
    async fn find(&self, id: &str) -> Option<T>;
    async fn save(&self, item: &T) -> Result<(), Error>;
}
```

---

## Generic Type Mappings

| TypeScript            | Rust            | Notes                 |
|-----------------------|-----------------|-----------------------|
| `<T>`                 | `<T>`           | Unconstrained generic |
| `<T extends U>`       | `<T: U>`        | Trait bound           |
| `<T extends A & B>`   | `<T: A + B>`    | Multiple bounds       |
| `<T = Default>`       | `<T = Default>` | Default type          |
| `<T extends keyof U>` | Custom trait    | No direct equivalent  |

### Generic Functions

```typescript
// TypeScript: Generic function
function identity<T>(value: T): T {
  return value;
}
```

```rust
// Rust: Generic function
fn identity<T>(value: T) -> T {
    value
}
```

### Bounded Generics

```typescript
// TypeScript: Bounded generic
function process<T extends Serializable>(item: T): string {
  return item.serialize();
}
```

```rust
// Rust: Trait bound
fn process<T: Serialize>(item: &T) -> String {
    serde_json::to_string(item).unwrap()
}
```

---

## Nullable / Optional Handling

### Mapping Strategies

| Source              | Target (Rust)   | Target (Go)     | Target (Python)   |
|---------------------|-----------------|-----------------|-------------------|
| `T \| null`         | `Option<T>`     | `*T`            | `Optional[T]`     |
| `T \| undefined`    | `Option<T>`     | zero value      | `Optional[T]`     |
| `T?` (optional)     | `Option<T>`     | `*T`            | `Optional[T]`     |
| `Required<T>`       | `T` (all fields)| `T` (all fields)| Required fields   |
| `Partial<T>`        | All `Option<>`  | All pointers    | All Optional      |

### Null Propagation

```typescript
// TypeScript: Optional chaining
const name = user?.profile?.name ?? "Unknown";
```

```rust
// Rust: Option combinators
let name = user
    .as_ref()
    .and_then(|u| u.profile.as_ref())
    .map(|p| p.name.as_str())
    .unwrap_or("Unknown");
```

```go
// Go: Explicit checks
var name string
if user != nil && user.Profile != nil {
    name = user.Profile.Name
} else {
    name = "Unknown"
}
```

---

## Type Alias Strategies

| Source Pattern       | Rust             | Go               | Python           |
|----------------------|------------------|------------------|------------------|
| Simple alias         | `type X = Y`     | `type X = Y`     | `X = Y`          |
| Newtype (branded)    | `struct X(Y)`    | `type X Y`       | `NewType('X', Y)`|
| Generic alias        | `type X<T> = Y<T>`| Not supported   | `X = Y[T]`       |

### Newtype Pattern (Type Safety)

```typescript
// TypeScript: Branded type
type UserId = string & { readonly __brand: unique symbol };
type OrderId = string & { readonly __brand: unique symbol };
```

```rust
// Rust: Newtype wrapper
struct UserId(String);
struct OrderId(String);

// Can't mix them up!
fn get_user(id: UserId) -> User { ... }
fn get_order(id: OrderId) -> Order { ... }
```

```go
// Go: Type definition
type UserId string
type OrderId string

func getUser(id UserId) *User { ... }
func getOrder(id OrderId) *Order { ... }
```
