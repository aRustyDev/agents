# Idiom Translation Examples

Code examples showing idiomatic translations between languages.

> **Philosophy**: Adopt target idioms, don't write "Source code in Target syntax"

---

## Translation Approaches

| Approach | When to Use | Example |
|----------|-------------|---------|
| **Literal** | Simple operations, primitives | `x + y` → `x + y` |
| **Semantic** | Same concept, different syntax | `arr.map()` → `.iter().map()` |
| **Idiomatic** | Different paradigm | Class hierarchy → Trait + Structs |
| **Redesign** | No equivalent | Prototype chain → Explicit composition |

---

## Null Handling

### TypeScript → Multiple Languages

```typescript
// TypeScript: null coalescing
const name = user?.name ?? "Anonymous";
```

```rust
// Rust: Option combinators
let name = user.as_ref()
    .map(|u| u.name.as_str())
    .unwrap_or("Anonymous");
```

```go
// Go: explicit nil check
var name string
if user != nil && user.Name != "" {
    name = user.Name
} else {
    name = "Anonymous"
}
```

```python
# Python: or operator (careful with falsy values)
name = (user and user.name) or "Anonymous"

# Safer Python
name = user.name if user and user.name else "Anonymous"
```

```elixir
# Elixir: pattern matching with default
name = case user do
  %{name: name} when name != nil -> name
  _ -> "Anonymous"
end

# Or with || operator
name = (user && user.name) || "Anonymous"
```

```clojure
;; Clojure: or with get
(def name (or (:name user) "Anonymous"))

;; With some->
(def name (or (some-> user :name) "Anonymous"))
```

---

## Collection Operations

### Filter + Map + Reduce

```typescript
// TypeScript: chained methods
const result = items
  .filter((x) => x.active)
  .map((x) => x.value)
  .reduce((a, b) => a + b, 0);
```

```rust
// Rust: iterator adaptors
let result: i32 = items.iter()
    .filter(|x| x.active)
    .map(|x| x.value)
    .sum();
```

```go
// Go: explicit loops (pre-generics style)
var result int
for _, x := range items {
    if x.Active {
        result += x.Value
    }
}
```

```python
# Python: generator expressions
result = sum(x.value for x in items if x.active)
```

```elixir
# Elixir: pipe operator
result = items
  |> Enum.filter(& &1.active)
  |> Enum.map(& &1.value)
  |> Enum.sum()
```

```clojure
;; Clojure: threading macro
(def result
  (->> items
       (filter :active)
       (map :value)
       (reduce + 0)))
```

```haskell
-- Haskell: function composition
result = sum $ map value $ filter active items

-- Or with & operator (left-to-right)
result = items & filter active & map value & sum
```

---

## Finding Elements

### Find First Match

```typescript
// TypeScript
const user = users.find((u) => u.id === id);
if (user) {
  process(user);
}
```

```rust
// Rust
if let Some(user) = users.iter().find(|u| u.id == id) {
    process(user);
}
```

```go
// Go
var found *User
for _, u := range users {
    if u.ID == id {
        found = &u
        break
    }
}
if found != nil {
    process(found)
}
```

```python
# Python
user = next((u for u in users if u.id == id), None)
if user:
    process(user)
```

```elixir
# Elixir
case Enum.find(users, fn u -> u.id == id end) do
  nil -> :not_found
  user -> process(user)
end
```

---

## Grouping Data

### Group By Key

```typescript
// TypeScript
const grouped = items.reduce(
  (acc, item) => {
    const key = item.category;
    acc[key] = acc[key] || [];
    acc[key].push(item);
    return acc;
  },
  {} as Record<string, Item[]>,
);
```

```rust
// Rust: use itertools or fold
use itertools::Itertools;

let grouped: HashMap<String, Vec<&Item>> = items
    .iter()
    .into_group_map_by(|item| item.category.clone());

// Or with fold
let grouped = items.iter().fold(
    HashMap::new(),
    |mut acc, item| {
        acc.entry(item.category.clone())
           .or_insert_with(Vec::new)
           .push(item);
        acc
    }
);
```

```python
# Python: defaultdict
from collections import defaultdict

grouped = defaultdict(list)
for item in items:
    grouped[item.category].append(item)

# Or with itertools
from itertools import groupby
grouped = {k: list(v) for k, v in groupby(sorted(items, key=lambda x: x.category), key=lambda x: x.category)}
```

```elixir
# Elixir
grouped = Enum.group_by(items, & &1.category)
```

```clojure
;; Clojure
(def grouped (group-by :category items))
```

---

## String Building

### Concatenation Patterns

```typescript
// TypeScript: template literals
const message = `Hello, ${user.name}! You have ${count} items.`;
```

```rust
// Rust: format! macro
let message = format!("Hello, {}! You have {} items.", user.name, count);
```

```go
// Go: fmt.Sprintf
message := fmt.Sprintf("Hello, %s! You have %d items.", user.Name, count)
```

```python
# Python: f-strings
message = f"Hello, {user.name}! You have {count} items."
```

```elixir
# Elixir: string interpolation
message = "Hello, #{user.name}! You have #{count} items."
```

### Building Large Strings

```typescript
// TypeScript: array join
const parts: string[] = [];
for (const item of items) {
  parts.push(item.name);
}
const result = parts.join(", ");
```

```rust
// Rust: collect with join (preferred)
let result: String = items
    .iter()
    .map(|item| item.name.as_str())
    .collect::<Vec<_>>()
    .join(", ");

// Or itertools
use itertools::Itertools;
let result = items.iter().map(|i| &i.name).join(", ");
```

```go
// Go: strings.Builder
var builder strings.Builder
for i, item := range items {
    if i > 0 {
        builder.WriteString(", ")
    }
    builder.WriteString(item.Name)
}
result := builder.String()
```

```python
# Python: join
result = ", ".join(item.name for item in items)
```

---

## Early Return Patterns

### Guard Clauses

```typescript
// TypeScript
function process(user: User | null): Result {
  if (!user) return { error: "No user" };
  if (!user.active) return { error: "Inactive" };
  if (!user.verified) return { error: "Not verified" };

  return { data: doWork(user) };
}
```

```rust
// Rust: ? operator with Result
fn process(user: Option<&User>) -> Result<Data, Error> {
    let user = user.ok_or(Error::NoUser)?;
    if !user.active { return Err(Error::Inactive); }
    if !user.verified { return Err(Error::NotVerified); }

    Ok(do_work(user))
}
```

```go
// Go: early returns
func process(user *User) (Result, error) {
    if user == nil {
        return Result{}, errors.New("no user")
    }
    if !user.Active {
        return Result{}, errors.New("inactive")
    }
    if !user.Verified {
        return Result{}, errors.New("not verified")
    }

    return doWork(user), nil
}
```

```elixir
# Elixir: with statement
def process(user) do
  with {:ok, user} <- validate_exists(user),
       {:ok, user} <- validate_active(user),
       {:ok, user} <- validate_verified(user) do
    {:ok, do_work(user)}
  end
end
```

---

## Pattern Matching

### Destructuring

```typescript
// TypeScript
const { name, age, email } = user;
const [first, second, ...rest] = items;
```

```rust
// Rust
let User { name, age, email, .. } = user;
let [first, second, rest @ ..] = items[..] else { panic!() };

// Or with slice patterns
if let [first, second, rest @ ..] = &items[..] {
    // use first, second, rest
}
```

```python
# Python
name, age, email = user.name, user.age, user.email
first, second, *rest = items
```

```elixir
# Elixir
%{name: name, age: age, email: email} = user
[first, second | rest] = items
```

```clojure
;; Clojure
(let [{:keys [name age email]} user
      [first second & rest] items]
  ...)
```

---

## Default Values

### With Fallbacks

```typescript
// TypeScript
function greet(name?: string, greeting = "Hello") {
  return `${greeting}, ${name ?? "World"}!`;
}
```

```rust
// Rust: Option with unwrap_or
fn greet(name: Option<&str>, greeting: Option<&str>) -> String {
    let name = name.unwrap_or("World");
    let greeting = greeting.unwrap_or("Hello");
    format!("{}, {}!", greeting, name)
}

// Or with Default trait for structs
#[derive(Default)]
struct Config {
    timeout: u32,  // defaults to 0
    retries: u32,  // defaults to 0
}

impl Config {
    fn new() -> Self {
        Self {
            timeout: 30,
            retries: 3,
            ..Default::default()
        }
    }
}
```

```go
// Go: explicit checks
func greet(name, greeting string) string {
    if name == "" {
        name = "World"
    }
    if greeting == "" {
        greeting = "Hello"
    }
    return fmt.Sprintf("%s, %s!", greeting, name)
}
```

```python
# Python
def greet(name: str = "World", greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"
```

```elixir
# Elixir: default arguments
def greet(name \\ "World", greeting \\ "Hello") do
  "#{greeting}, #{name}!"
end
```
