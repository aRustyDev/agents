# Gotchas by Language Pair

Specific pitfalls when converting between common language pairs.

---

## Python → Rust

### None Handling

```python
# Python: None is everywhere
def find(items, key):
    for item in items:
        if item.key == key:
            return item
    return None  # Implicit possibility
```

```rust
// Rust: Must be explicit
fn find(items: &[Item], key: &str) -> Option<&Item> {
    items.iter().find(|i| i.key == key)
}
// Caller MUST handle None case
```

### List Comprehensions

```python
# Python: Compact
squares = [x**2 for x in range(10) if x % 2 == 0]
```

```rust
// Rust: Iterator chain
let squares: Vec<_> = (0..10)
    .filter(|x| x % 2 == 0)
    .map(|x| x * x)
    .collect();
```

### Dynamic Attributes

```python
# Python: Add attributes anytime
obj.new_field = "value"
```

```rust
// Rust: Use HashMap for dynamic fields
struct Dynamic {
    known: String,
    extra: HashMap<String, Value>,
}
```

### Default Arguments

```python
# Python
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")
```

```rust
// Rust: Builder pattern or Option
fn greet(name: &str, greeting: Option<&str>) {
    let greeting = greeting.unwrap_or("Hello");
    println!("{}, {}!", greeting, name);
}

// Or builder
Greeting::new(name).greeting("Hi").send();
```

---

## TypeScript → Rust

### Null Coalescing

```typescript
// TypeScript
const value = input ?? defaultValue;
const nested = obj?.prop?.deep ?? "default";
```

```rust
// Rust
let value = input.unwrap_or(default_value);
let nested = obj
    .and_then(|o| o.prop.as_ref())
    .and_then(|p| p.deep.as_ref())
    .unwrap_or(&"default".to_string());

// Or with if-let chains (nightly/future)
```

### Object Spread

```typescript
// TypeScript
const updated = { ...original, name: "new" };
```

```rust
// Rust: Struct update syntax
let updated = User { name: "new".into(), ..original };
// Note: moves non-Copy fields from original!
```

### Union Types

```typescript
// TypeScript
type Result = string | number | null;
```

```rust
// Rust: Enum
enum Result {
    Text(String),
    Number(i64),
    None,
}
```

### Async/Await Differences

```typescript
// TypeScript: Promises auto-start
const promise = fetchData();  // Already running!
await promise;
```

```rust
// Rust: Futures are lazy
let future = fetch_data();  // Nothing happens yet
future.await;  // Now it runs
```

---

## Go → Rust

### Error Returns

```go
// Go: Multiple returns
func process() (Result, error) {
    if err != nil {
        return Result{}, err
    }
    return result, nil
}
```

```rust
// Rust: Result type
fn process() -> Result<ProcessResult, Error> {
    // Use ? for propagation
    let data = get_data()?;
    Ok(ProcessResult::from(data))
}
```

### Goroutines → Tokio

```go
// Go: Simple goroutine
go func() {
    doWork()
}()
```

```rust
// Rust: Spawn task
tokio::spawn(async {
    do_work().await
});
```

### Interface Satisfaction

```go
// Go: Implicit interface satisfaction
type Reader interface { Read([]byte) (int, error) }
// Any type with Read method satisfies Reader
```

```rust
// Rust: Explicit impl
trait Reader {
    fn read(&mut self, buf: &mut [u8]) -> io::Result<usize>;
}
impl Reader for MyType {
    fn read(&mut self, buf: &mut [u8]) -> io::Result<usize> { ... }
}
```

### Zero Values

```go
// Go: Zero values for everything
var s string  // ""
var n int     // 0
var b bool    // false
```

```rust
// Rust: Must initialize or use Default
let s: String = String::new();  // or Default::default()
let n: i32 = 0;
let b: bool = false;
// Or derive Default for structs
```

---

## JavaScript → Rust

### Truthy/Falsy

```javascript
// JavaScript: Truthy coercion
if (value) { /* value is truthy */ }
if (!array.length) { /* empty */ }
```

```rust
// Rust: Explicit checks
if value.is_some() { ... }
if array.is_empty() { ... }
if !string.is_empty() { ... }
```

### Array Methods

| JavaScript | Rust Equivalent |
|------------|-----------------|
| `.map()` | `.iter().map()` |
| `.filter()` | `.iter().filter()` |
| `.reduce()` | `.iter().fold()` |
| `.find()` | `.iter().find()` |
| `.some()` | `.iter().any()` |
| `.every()` | `.iter().all()` |
| `.includes()` | `.contains()` |
| `.flat()` | `.flatten()` |

### Object Destructuring

```javascript
// JavaScript
const { name, age = 0 } = user;
```

```rust
// Rust: Pattern matching
let User { name, age } = user;
// For defaults, use Option fields
let age = user.age.unwrap_or(0);
```

### Prototypes → Traits

```javascript
// JavaScript: Prototype extension
Array.prototype.first = function() {
    return this[0];
};
```

```rust
// Rust: Extension trait
trait First<T> {
    fn first(&self) -> Option<&T>;
}
impl<T> First<T> for Vec<T> {
    fn first(&self) -> Option<&T> {
        self.get(0)
    }
}
```

---

## Java → Rust

### Null Safety

```java
// Java: Nullable everywhere
String name = user.getName();  // Could be null
if (name != null) { ... }
```

```rust
// Rust: Option is explicit
let name: Option<String> = user.name();
if let Some(name) = name { ... }
// Or
let name = user.name().unwrap_or_default();
```

### Checked Exceptions

```java
// Java: Checked exceptions
public void read() throws IOException {
    // ...
}
```

```rust
// Rust: Result types
fn read() -> io::Result<()> {
    // Use ? to propagate
}
```

### Inheritance Hierarchies

```java
// Java: Deep inheritance
class Dog extends Animal implements Pet, Trainable { }
```

```rust
// Rust: Composition + traits
struct Dog {
    animal: AnimalData,
}
impl Pet for Dog { ... }
impl Trainable for Dog { ... }
```

### Generics Differences

```java
// Java: Type erasure
List<String> list = new ArrayList<>();
// At runtime, just List
```

```rust
// Rust: Monomorphization
Vec<String>  // Distinct compiled type
Vec<i32>     // Different compiled type
```

---

## Haskell/Scala → Rust

### Higher-Kinded Types

```haskell
-- Haskell: Abstract over container
class Functor f where
  fmap :: (a -> b) -> f a -> f b
```

```rust
// Rust: No HKTs, use concrete implementations
// Each container has its own map
vec.iter().map(f).collect()
option.map(f)
result.map(f)
```

### Type Classes → Traits

```scala
// Scala: Type class with implicit
implicit val intShow: Show[Int] = _.toString
def print[A: Show](a: A) = println(implicitly[Show[A]].show(a))
```

```rust
// Rust: Traits
impl Display for MyType {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result { ... }
}
fn print<T: Display>(a: T) { println!("{}", a); }
```

### Monadic Composition

```haskell
-- Haskell: Do notation
do
  x <- getLine
  y <- getLine
  return (x ++ y)
```

```rust
// Rust: ? operator for Result/Option
fn concat_lines() -> io::Result<String> {
    let x = read_line()?;
    let y = read_line()?;
    Ok(format!("{}{}", x, y))
}
```

---

## Elixir → Rust

### Pattern Matching in Functions

```elixir
# Elixir: Pattern match in function head
def process({:ok, value}), do: handle_value(value)
def process({:error, msg}), do: handle_error(msg)
```

```rust
// Rust: Match in function body
fn process(result: Result<Value, Error>) {
    match result {
        Ok(value) => handle_value(value),
        Err(msg) => handle_error(msg),
    }
}
```

### Pipe Operator

```elixir
# Elixir: Pipe
data
|> parse()
|> validate()
|> transform()
```

```rust
// Rust: Method chains or intermediate bindings
let result = transform(validate(parse(data)?)?)?;

// Or with methods
data.parse()?.validate()?.transform()
```

### Processes → Tasks

```elixir
# Elixir: Spawn process
spawn(fn -> do_work() end)
```

```rust
// Rust: Spawn task
tokio::spawn(async { do_work().await });
```

### Hot Code Reload

```elixir
# Elixir: Hot reload in production
# Just works with releases
```

```rust
// Rust: No equivalent
// Recompile and redeploy
// Use feature flags for runtime behavior changes
```

---

## Quick Reference: Common Traps

| From | To | Trap | Solution |
|------|-----|------|----------|
| Python | Rust | Implicit None | Always return Option |
| TypeScript | Rust | Object spread moves | Clone if needed |
| Go | Rust | Zero values | Default trait |
| JavaScript | Rust | Truthy checks | Explicit bool methods |
| Java | Rust | null everywhere | Option<T> |
| Haskell | Rust | HKTs | Per-type implementations |
| Elixir | Rust | Pipes | Method chains |
