# Paradigm Translation Reference

Guide for converting between programming paradigms (OOP → FP, FP → FP, etc.).

---

## OOP → Functional Translation

### Core Concept Mapping

| OOP Concept           | Functional Approach                       | Key Insight                                      |
|-----------------------|-------------------------------------------|--------------------------------------------------|
| Class with fields     | Record/struct + module functions          | Data and behavior separated                      |
| Inheritance hierarchy | Composition / Type classes / Protocols    | Favor capabilities over hierarchies              |
| Mutable object state  | Immutable data + transformation functions | New version instead of mutation                  |
| Method chaining       | Function pipelines                        | `obj.a().b()` → `b(a(obj))` or `obj \|> a \|> b` |
| Interface             | Protocol / Type class / Trait             | Behavior contract                                |
| Private methods       | Module-private functions                  | Visibility at module level                       |

### Class → Data + Functions

```typescript
// OOP: Class with methods
class User {
  private name: string;
  private email: string;

  constructor(name: string, email: string) {
    this.name = name;
    this.email = email;
  }

  greet(): string {
    return `Hello, ${this.name}!`;
  }

  updateEmail(email: string): void {
    this.email = email;
  }
}
```

```elixir
# Functional: Data + functions
defmodule User do
  defstruct [:name, :email]

  def new(name, email) do
    %User{name: name, email: email}
  end

  def greet(%User{name: name}) do
    "Hello, #{name}!"
  end

  def update_email(%User{} = user, email) do
    %{user | email: email}  # Returns new user, doesn't mutate
  end
end
```

### Inheritance → Composition

```typescript
// OOP: Inheritance hierarchy
abstract class Shape {
  abstract area(): number;
}

class Circle extends Shape {
  constructor(private radius: number) {
    super();
  }
  area(): number {
    return Math.PI * this.radius ** 2;
  }
}

class Rectangle extends Shape {
  constructor(
    private width: number,
    private height: number,
  ) {
    super();
  }
  area(): number {
    return this.width * this.height;
  }
}
```

```rust
// Functional: Enum + pattern matching
enum Shape {
    Circle { radius: f64 },
    Rectangle { width: f64, height: f64 },
}

impl Shape {
    fn area(&self) -> f64 {
        match self {
            Shape::Circle { radius } => std::f64::consts::PI * radius.powi(2),
            Shape::Rectangle { width, height } => width * height,
        }
    }
}
```

---

## Immutability Patterns

### Mutable → Immutable

| Mutable Pattern       | Immutable Pattern                  | Example Languages       |
|-----------------------|------------------------------------|-------------------------|
| `obj.field = value`   | `{...obj, field: value}`           | JS, Clojure, Elixir     |
| `list.push(x)`        | `[x \| list]` or `cons(x, list)`   | Erlang, Elixir, Haskell |
| `dict[key] = value`   | `Map.put(dict, key, value)`        | Elixir, Clojure         |
| Accumulator variables | `fold`/`reduce` with initial value | All functional          |
| In-place sort         | Return sorted copy                 | All functional          |

### Example: Mutable to Immutable

```python
# Mutable (imperative)
def process_users(users):
    result = []
    for user in users:
        if user.active:
            user.score += 10  # Mutation!
            result.append(user)
    return result
```

```elixir
# Immutable (functional)
def process_users(users) do
  users
  |> Enum.filter(& &1.active)
  |> Enum.map(& %{&1 | score: &1.score + 10})  # New map, not mutation
end
```

---

## State Management

| OOP Approach     | Functional Equivalent                |
|------------------|--------------------------------------|
| Singleton        | Module with state (GenServer, Agent) |
| Observer pattern | Event streams, pub/sub               |
| Factory pattern  | Constructor functions, protocols     |
| Repository       | Pure functions + effect boundary     |
| State machine    | Enum + transition functions          |

### Stateful Service Translation

```typescript
// OOP: Stateful service
class Counter {
  private count = 0;

  increment(): void {
    this.count++;
  }

  get(): number {
    return this.count;
  }
}
```

```elixir
# Functional: GenServer for state
defmodule Counter do
  use GenServer

  def start_link(_), do: GenServer.start_link(__MODULE__, 0, name: __MODULE__)
  def increment, do: GenServer.cast(__MODULE__, :increment)
  def get, do: GenServer.call(__MODULE__, :get)

  @impl true
  def init(_), do: {:ok, 0}

  @impl true
  def handle_cast(:increment, count), do: {:noreply, count + 1}

  @impl true
  def handle_call(:get, _from, count), do: {:reply, count, count}
end
```

---

## Functional → Functional Translation

Different functional languages have different idioms.

### Key Differences

| Aspect            | Clojure          | Elixir        | Haskell          | Scala           |
|-------------------|------------------|---------------|------------------|-----------------|
| **Typing**        | Dynamic          | Dynamic       | Static (HM)      | Static (hybrid) |
| **Laziness**      | Lazy seqs        | Strict        | Lazy default     | Strict          |
| **Purity**        | Practical        | Practical     | Pure (IO)        | Hybrid          |
| **Macros**        | Yes              | Yes           | Template Haskell | Limited         |
| **Concurrency**   | STM + core.async | Actors (BEAM) | STM, async       | Akka            |
| **Pattern match** | Limited          | Full          | Full             | Full            |

### Laziness Translation

```haskell
-- Haskell: Lazy by default
naturals = [0..]  -- Infinite list, evaluated on demand
take 5 naturals   -- [0,1,2,3,4]
```

```clojure
;; Clojure: Explicit lazy sequences
(def naturals (range))  ; Lazy sequence
(take 5 naturals)  ; (0 1 2 3 4)
```

```elixir
# Elixir: Strict, use Stream for laziness
naturals = Stream.iterate(0, &(&1 + 1))
Enum.take(naturals, 5)  # [0, 1, 2, 3, 4]
```

### Purity Translation

```haskell
-- Haskell: Effects in IO monad
readConfig :: FilePath -> IO Config
readConfig path = do
  content <- readFile path
  pure (parseConfig content)
```

```clojure
;; Clojure: Effects are implicit
(defn read-config [path]
  (-> path slurp parse-config))
```

```elixir
# Elixir: Effects are implicit
def read_config(path) do
  path |> File.read!() |> parse_config()
end
```

---

## Concurrency Model Translation (FP)

| From               | To                 | Translation Strategy                         |
|--------------------|--------------------|----------------------------------------------|
| Clojure STM        | Elixir Agent       | `ref` → `Agent`, `alter` → `Agent.update`    |
| Clojure core.async | Elixir GenServer   | Channels → GenServer calls, go blocks → Task |
| Haskell STM        | Clojure STM        | Similar concepts, different syntax           |
| Elixir GenServer   | Clojure component  | GenServer → Stuart Sierra's component        |
| Erlang processes   | Clojure core.async | Mailbox → channel, receive → alts!           |

### Example: Clojure STM → Elixir Agent

```clojure
;; Clojure: STM
(def account (ref {:balance 100}))

(dosync
  (alter account update :balance + 50))
```

```elixir
# Elixir: Agent
{:ok, account} = Agent.start_link(fn -> %{balance: 100} end)

Agent.update(account, fn state ->
  %{state | balance: state.balance + 50}
end)
```

---

## Pipeline Styles

| Language | Pipeline Syntax | Direction |
|----------|-----------------|-----------|
| Elixir | `\|>` | Left to right |
| F# | `\|>` | Left to right |
| Haskell | `&` (lens) | Left to right |
| Haskell | `.` (compose) | Right to left |
| Clojure | `->` / `->>` | Left to right |
| OCaml | `\|>` | Left to right |

### Pipeline Example

```elixir
# Elixir
users
|> Enum.filter(&(&1.active))
|> Enum.map(&(&1.name))
|> Enum.sort()
```

```clojure
;; Clojure
(->> users
     (filter :active)
     (map :name)
     (sort))
```

```haskell
-- Haskell (with &)
users
  & filter active
  & map name
  & sort
```

```fsharp
// F#
users
|> List.filter (fun u -> u.Active)
|> List.map (fun u -> u.Name)
|> List.sort
```
