# Paradigm Translation Reference

When converting code between languages with different programming paradigms, the translation goes beyond syntax - it requires a mental model shift. This reference covers common paradigm translations.

## Paradigm Matrix

| Source Paradigm | Target Paradigm | Difficulty | Key Challenge |
|-----------------|-----------------|------------|---------------|
| OOP → FP | Medium-Hard | Replacing classes with data + functions |
| FP → OOP | Medium | Adding classes around pure functions |
| Imperative → Declarative | Medium | Expressing "what" instead of "how" |
| Declarative → Imperative | Easy | Making implicit steps explicit |
| Dynamic → Static | Medium-Hard | Adding types everywhere |
| Static → Dynamic | Easy | Removing/simplifying types |
| Statement-oriented → Expression-oriented | Medium | Everything returns a value |
| Mutable-first → Immutable-first | Hard | Redesigning state management |

## OOP → FP Translation Patterns

### Classes → Data + Functions

**OOP (Java):**
```java
public class BankAccount {
    private double balance;
    private String accountId;

    public BankAccount(String accountId, double initialBalance) {
        this.accountId = accountId;
        this.balance = initialBalance;
    }

    public void deposit(double amount) {
        if (amount > 0) {
            this.balance += amount;
        }
    }

    public boolean withdraw(double amount) {
        if (amount > 0 && amount <= balance) {
            this.balance -= amount;
            return true;
        }
        return false;
    }

    public double getBalance() { return balance; }
}

// Usage
BankAccount account = new BankAccount("123", 1000.0);
account.deposit(500.0);
account.withdraw(200.0);
```

**FP (F#):**
```fsharp
// Data
type BankAccount = {
    AccountId: string
    Balance: decimal
}

// Functions (pure, operate on data)
module BankAccount =
    let create accountId initialBalance =
        { AccountId = accountId; Balance = initialBalance }

    let deposit amount account =
        if amount > 0m
        then { account with Balance = account.Balance + amount }
        else account

    let withdraw amount account =
        if amount > 0m && amount <= account.Balance
        then Some { account with Balance = account.Balance - amount }
        else None

    let getBalance account = account.Balance

// Usage (threading state through)
let account =
    BankAccount.create "123" 1000m
    |> BankAccount.deposit 500m
    |> BankAccount.withdraw 200m
    |> Option.defaultValue (BankAccount.create "123" 0m)
```

**Translation Strategy:**
1. **Extract data** - Fields become record/struct fields
2. **Extract behavior** - Methods become module functions
3. **Remove mutation** - Return new instances instead of modifying
4. **Explicit state** - State threading via function composition
5. **Option for failure** - Replace boolean returns with Option/Result

### Inheritance → Composition + Polymorphism via Types

**OOP (Java):**
```java
abstract class Shape {
    abstract double area();
    abstract double perimeter();
}

class Circle extends Shape {
    private double radius;
    Circle(double radius) { this.radius = radius; }
    double area() { return Math.PI * radius * radius; }
    double perimeter() { return 2 * Math.PI * radius; }
}

class Rectangle extends Shape {
    private double width, height;
    Rectangle(double w, double h) { this.width = w; this.height = h; }
    double area() { return width * height; }
    double perimeter() { return 2 * (width + height); }
}
```

**FP (Haskell):**
```haskell
-- Algebraic Data Type (sum type)
data Shape
    = Circle Double           -- radius
    | Rectangle Double Double -- width, height

-- Pattern matching replaces virtual dispatch
area :: Shape -> Double
area (Circle r) = pi * r * r
area (Rectangle w h) = w * h

perimeter :: Shape -> Double
perimeter (Circle r) = 2 * pi * r
perimeter (Rectangle w h) = 2 * (w + h)
```

**Translation Strategy:**
1. **Class hierarchy → Sum type** - Subclasses become type constructors
2. **Virtual methods → Pattern match functions** - Dispatch is explicit
3. **Open for extension** - Consider type classes if extensibility needed
4. **Closed set** - Sum types are closed (can add exhaustiveness checking)

### Mutable State → Immutable Transformations

**Imperative (Python):**
```python
def process_orders(orders):
    results = []
    for order in orders:
        if order['status'] == 'pending':
            order['status'] = 'processed'  # mutation!
            order['processed_at'] = datetime.now()
            results.append(order)
    return results
```

**FP (Elixir):**
```elixir
def process_orders(orders) do
  orders
  |> Enum.filter(&(&1.status == :pending))
  |> Enum.map(fn order ->
    %{order |
      status: :processed,
      processed_at: DateTime.utc_now()
    }
  end)
end
```

**Translation Strategy:**
1. **Loop → Pipeline** - for/while → filter/map/reduce
2. **Mutation → New value** - Modify → Create new with changes
3. **Side effects → Pure functions** - Move I/O to boundaries
4. **Intermediate variables → Pipeline operators** - |> in Elixir, >> in Haskell

## Imperative → Declarative Patterns

### Control Flow → Expressions

**Imperative (Go):**
```go
func classify(score int) string {
    var grade string
    if score >= 90 {
        grade = "A"
    } else if score >= 80 {
        grade = "B"
    } else if score >= 70 {
        grade = "C"
    } else {
        grade = "F"
    }
    return grade
}
```

**Declarative (Elixir):**
```elixir
def classify(score) do
  cond do
    score >= 90 -> "A"
    score >= 80 -> "B"
    score >= 70 -> "C"
    true -> "F"
  end
end

# Or with guards:
def classify(score) when score >= 90, do: "A"
def classify(score) when score >= 80, do: "B"
def classify(score) when score >= 70, do: "C"
def classify(_score), do: "F"
```

### Loops → Comprehensions/Recursion

**Imperative (Python):**
```python
def find_adults(people):
    adults = []
    for person in people:
        if person['age'] >= 18:
            adults.append(person['name'])
    return adults
```

**Declarative (Elixir):**
```elixir
# Comprehension
def find_adults(people) do
  for %{age: age, name: name} <- people, age >= 18, do: name
end

# Or pipeline
def find_adults(people) do
  people
  |> Enum.filter(&(&1.age >= 18))
  |> Enum.map(&(&1.name))
end
```

## Dynamic → Static Type System Patterns

### Adding Types to Dynamic Code

**Dynamic (Python):**
```python
def process_user(user):
    return {
        'id': user['id'],
        'display_name': f"{user['first_name']} {user['last_name']}",
        'is_adult': user['age'] >= 18
    }
```

**Static (Rust):**
```rust
#[derive(Debug)]
struct User {
    id: u64,
    first_name: String,
    last_name: String,
    age: u8,
}

#[derive(Debug)]
struct ProcessedUser {
    id: u64,
    display_name: String,
    is_adult: bool,
}

fn process_user(user: &User) -> ProcessedUser {
    ProcessedUser {
        id: user.id,
        display_name: format!("{} {}", user.first_name, user.last_name),
        is_adult: user.age >= 18,
    }
}
```

**Translation Strategy:**
1. **Dict → Struct** - Define explicit types for data
2. **Implicit types → Explicit signatures** - Add parameter and return types
3. **Runtime checks → Compile-time checks** - Leverage type system
4. **Duck typing → Trait bounds** - Explicit interface requirements

### Handling "Any" Types

| Dynamic Pattern | Static Equivalent |
|-----------------|-------------------|
| Accept any type | Generics with trait bounds |
| Optional field | `Option<T>` |
| Nullable | `Option<T>` (never null) |
| Mixed collection | Sum types or trait objects |
| Runtime type check | Pattern matching on enums |

## Expression-Oriented Translation

### Statement-Oriented → Expression-Oriented

**Statement-oriented (JavaScript):**
```javascript
function processValue(value) {
    let result;
    if (value > 0) {
        result = value * 2;
    } else {
        result = 0;
    }
    return result;
}
```

**Expression-oriented (Rust):**
```rust
fn process_value(value: i32) -> i32 {
    if value > 0 {
        value * 2
    } else {
        0
    }
    // No explicit return - last expression is the value
}
```

**Key Differences:**
- No semicolon on last expression (returns that value)
- `if`/`match` are expressions, not statements
- Blocks `{}` return their last expression
- Early returns with `return` keyword when needed

## Common Paradigm Gotchas

### OOP → FP

| OOP Habit | FP Approach |
|-----------|-------------|
| Mutate object state | Return new object |
| Null checks | Option types |
| Exceptions | Result types |
| Inheritance | Composition + type classes |
| Side effects anywhere | Side effects at boundaries |

### Imperative → Declarative

| Imperative Habit | Declarative Approach |
|------------------|---------------------|
| Explicit loops | Higher-order functions |
| Mutable accumulators | Fold/reduce |
| Multiple statements | Expression chains |
| Early return | Pattern matching |
| Index-based iteration | Iterator adapters |

### Dynamic → Static

| Dynamic Habit | Static Approach |
|---------------|----------------|
| Dict for everything | Typed structs |
| Duck typing | Trait bounds |
| Runtime type checks | Exhaustive pattern matching |
| Implicit conversions | Explicit From/Into |
| Optional fields | Option<T> |

## Language Family Patterns

### Lisp Family (Clojure, Common Lisp, Scheme)
- Everything is an expression
- Homoiconic (code is data)
- Macros for metaprogramming
- Dynamic by default (Clojure has optional types)

### ML Family (Haskell, F#, OCaml, Elm, Roc)
- Strong static types with inference
- Pattern matching central
- ADTs (sum types) for data modeling
- Expression-oriented
- Pure by default (Haskell) or mostly pure

### C Family (C, C++, Go, Rust)
- Statement-oriented (Go, C) or mixed (Rust)
- Explicit memory management (Rust) or GC (Go)
- Imperative core with FP features
- Systems programming focus

### BEAM Family (Erlang, Elixir, Gleam)
- Actor model concurrency
- Pattern matching
- Immutable data
- Let-it-crash philosophy
- Hot code reload

---

## Cross-References

- [Platform Ecosystem](platform-ecosystem.md) - Platform-specific patterns
- [Concurrency Patterns](../SKILL.md#concurrency-pattern-translation) - Concurrency paradigm shifts
- [Error Handling](../SKILL.md#conversion-skill-structure) - Error handling paradigms
