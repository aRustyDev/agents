# TypeScript Advanced Patterns Reference

TypeScript-specific patterns that require careful translation to other languages.

---

## Type Guards

### User-Defined Type Guards

```typescript
// TypeScript: Type guard function
interface Dog {
  bark(): void;
}
interface Cat {
  meow(): void;
}
type Pet = Dog | Cat;

function isDog(pet: Pet): pet is Dog {
  return "bark" in pet;
}

function speak(pet: Pet) {
  if (isDog(pet)) {
    pet.bark(); // TypeScript knows pet is Dog
  } else {
    pet.meow(); // TypeScript knows pet is Cat
  }
}
```

### Translation to Other Languages

```rust
// Rust: Enum with pattern matching
enum Pet {
    Dog(Dog),
    Cat(Cat),
}

fn speak(pet: &Pet) {
    match pet {
        Pet::Dog(dog) => dog.bark(),
        Pet::Cat(cat) => cat.meow(),
    }
}
```

```python
# Python: isinstance checks (runtime)
from typing import Union

def speak(pet: Union[Dog, Cat]) -> None:
    if isinstance(pet, Dog):
        pet.bark()
    else:
        pet.meow()
```

```go
// Go: Type switch
func speak(pet interface{}) {
    switch p := pet.(type) {
    case Dog:
        p.Bark()
    case Cat:
        p.Meow()
    }
}
```

---

## Conditional Types

```typescript
// TypeScript: Conditional type
type Flatten<T> = T extends Array<infer U> ? U : T;

type A = Flatten<string[]>; // string
type B = Flatten<number>; // number
```

### Translation Strategies

```rust
// Rust: Trait with associated type
trait Flatten {
    type Output;
}

impl<T> Flatten for Vec<T> {
    type Output = T;
}

impl Flatten for i32 {
    type Output = i32;
}
```

```haskell
-- Haskell: Type families
type family Flatten a where
  Flatten [a] = a
  Flatten a = a
```

**Note:** Most languages don't have direct equivalents. Use:

- Separate types/functions for each case
- Traits with associated types
- Code generation

---

## Mapped Types

```typescript
// TypeScript: Mapped types
type Partial<T> = { [K in keyof T]?: T[K] };
type Readonly<T> = { readonly [K in keyof T]: T[K] };
type Pick<T, K extends keyof T> = { [P in K]: T[P] };

interface User {
  name: string;
  age: number;
}

type PartialUser = Partial<User>; // { name?: string; age?: number; }
```

### Translation

```rust
// Rust: No mapped types - use derive macros or manual
#[derive(Default)]
struct UserBuilder {
    name: Option<String>,
    age: Option<u32>,
}

// Readonly is default in Rust (use &mut for mutation)
struct User {
    name: String,
    age: u32,
}
```

```python
# Python: TypedDict with total=False
from typing import TypedDict

class PartialUser(TypedDict, total=False):
    name: str
    age: int

# Or dataclass with Optional
@dataclass
class PartialUser:
    name: Optional[str] = None
    age: Optional[int] = None
```

---

## Template Literal Types

```typescript
// TypeScript: Template literal type
type EventName = `on${Capitalize<string>}`;
type ValidEvent = `on${"Click" | "Hover" | "Focus"}`;

function on(event: ValidEvent, handler: () => void) {}
on("onClick", () => {}); // OK
// on("onClack", () => {});  // Error
```

### Translation

Most languages don't have this. Use:

```rust
// Rust: Enum instead
#[derive(Debug, Clone, Copy)]
enum Event {
    Click,
    Hover,
    Focus,
}

fn on(event: Event, handler: impl Fn()) {}
```

```go
// Go: Const enum pattern
type Event string

const (
    EventClick Event = "onClick"
    EventHover Event = "onHover"
    EventFocus Event = "onFocus"
)

func on(event Event, handler func()) {}
```

---

## Branded / Opaque Types

```typescript
// TypeScript: Branded type for type safety
type UserId = string & { readonly __brand: unique symbol };
type OrderId = string & { readonly __brand: unique symbol };

function createUserId(id: string): UserId {
  return id as UserId;
}

function getUser(id: UserId) {} // Won't accept OrderId
```

### Translation

```rust
// Rust: Newtype pattern
struct UserId(String);
struct OrderId(String);

impl UserId {
    fn new(id: String) -> Self { Self(id) }
    fn as_str(&self) -> &str { &self.0 }
}

fn get_user(id: &UserId) {}  // Won't accept OrderId
```

```python
# Python: NewType (type-checker only)
from typing import NewType

UserId = NewType('UserId', str)
OrderId = NewType('OrderId', str)

def get_user(id: UserId) -> User: ...
```

```go
// Go: Type definition
type UserId string
type OrderId string

func getUser(id UserId) *User { ... }
```

---

## Index Signatures

```typescript
// TypeScript: Index signature
interface StringMap {
  [key: string]: string;
}

interface NumberMap {
  [key: string]: number;
}

// With known keys too
interface Config {
  name: string;
  [key: string]: string | number; // Additional dynamic keys
}
```

### Translation

```rust
// Rust: HashMap
use std::collections::HashMap;

type StringMap = HashMap<String, String>;
type NumberMap = HashMap<String, i64>;

// Mixed: Use struct + HashMap
struct Config {
    name: String,
    extra: HashMap<String, serde_json::Value>,
}
```

```python
# Python: TypedDict or dict
from typing import Dict

StringMap = Dict[str, str]
NumberMap = Dict[str, int]
```

---

## Utility Types

| TypeScript       | Rust             | Python                   | Go             |
| ---------------- | ---------------- | ------------------------ | -------------- |
| `Partial<T>`     | All `Option<>`   | `TypedDict(total=False)` | Pointer fields |
| `Required<T>`    | No `Option<>`    | Required fields          | Non-pointer    |
| `Readonly<T>`    | Default          | `frozen=True`            | -              |
| `Pick<T, K>`     | New struct       | New TypedDict            | New struct     |
| `Omit<T, K>`     | New struct       | New TypedDict            | New struct     |
| `Record<K, V>`   | `HashMap<K, V>`  | `Dict[K, V]`             | `map[K]V`      |
| `NonNullable<T>` | `T` (not Option) | Remove None              | Non-nil        |
| `ReturnType<T>`  | Associated type  | -                        | -              |
| `Parameters<T>`  | -                | -                        | -              |

---

## Discriminated Unions

```typescript
// TypeScript: Discriminated union
type Result<T, E> = { success: true; value: T } | { success: false; error: E };

function handle<T, E>(result: Result<T, E>) {
  if (result.success) {
    console.log(result.value); // TypeScript knows value exists
  } else {
    console.error(result.error); // TypeScript knows error exists
  }
}
```

### Translation

```rust
// Rust: Native enum
enum Result<T, E> {
    Ok(T),
    Err(E),
}

fn handle<T, E>(result: Result<T, E>) {
    match result {
        Ok(value) => println!("{:?}", value),
        Err(error) => eprintln!("{:?}", error),
    }
}
```

```python
# Python: Union with Literal discriminator
from typing import Union, Literal
from dataclasses import dataclass

@dataclass
class Success[T]:
    success: Literal[True]
    value: T

@dataclass
class Failure[E]:
    success: Literal[False]
    error: E

Result = Union[Success[T], Failure[E]]
```

---

## Generics with Defaults

```typescript
// TypeScript: Generic with default
interface Container<T = string> {
  value: T;
}

const stringContainer: Container = { value: "hello" };
const numberContainer: Container<number> = { value: 42 };
```

### Translation

```rust
// Rust: Default generic
struct Container<T = String> {
    value: T,
}

let string_container: Container = Container { value: "hello".into() };
let number_container: Container<i32> = Container { value: 42 };
```

```go
// Go: No default generics (1.18+)
// Must always specify type parameter
type Container[T any] struct {
    Value T
}
```
