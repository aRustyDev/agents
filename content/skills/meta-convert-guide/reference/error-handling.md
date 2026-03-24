# Error Handling Reference

Comprehensive reference for error handling translation between languages.

---

## Error Model Comparison

| Language   | Primary Model    | Error Type                          | Propagation            |
|------------|------------------|-------------------------------------|------------------------|
| TypeScript | Exceptions       | `Error` class                       | `throw` / `try-catch`  |
| Python     | Exceptions       | `Exception` hierarchy               | `raise` / `try-except` |
| Go         | Error returns    | `error` interface                   | Multiple return values |
| Rust       | Result type      | `Result<T, E>`                      | `?` operator           |
| Erlang     | Pattern matching | `{ok, Value}` / `{error, Reason}`   | Return tuples          |
| Elixir     | Pattern matching | `{:ok, value}` / `{:error, reason}` | Return tuples, `with`  |
| Haskell    | Maybe/Either     | `Maybe a`, `Either e a`             | Monadic bind (`>>=`)   |
| Scala      | Try/Either       | `Try[T]`, `Either[E, T]`            | `for` comprehensions   |
| F#         | Result           | `Result<'T, 'E>`                    | `result { }` CE        |

---

## Translation Patterns

### Exception → Result Type

| Exception Pattern | Result Pattern |
|-------------------|----------------|
| `throw new Error(msg)` | `Err(Error::new(msg))` |
| `try { ... } catch (e) { ... }` | `match result { Ok(v) => ..., Err(e) => ... }` |
| `throw` (rethrow) | `?` operator |
| `finally { ... }` | RAII / Drop / defer |
| Exception hierarchy | Enum variants |

### Exception → Error Return (Go)

| Exception Pattern | Go Pattern |
|-------------------|------------|
| `throw new Error(msg)` | `return ..., errors.New(msg)` |
| `try { ... }` | `result, err := ...` |
| `catch (e) { ... }` | `if err != nil { ... }` |
| `throw` (rethrow) | `return ..., err` |
| `finally { ... }` | `defer func() { ... }()` |

---

## Error Hierarchy Translation

### Class Hierarchy → Enum

```
TypeScript Class Hierarchy:
    Error
    ├── AppError (code: string)
    │   ├── NotFoundError
    │   ├── ValidationError (field: string)
    │   └── AuthError
    └── NetworkError

Rust Enum:
    enum AppError {
        NotFound { resource: String },
        Validation { field: String, message: String },
        Auth { reason: String },
        Network(reqwest::Error),
        Io(std::io::Error),
    }
```

### Creating Error Types

**Rust (with thiserror):**
```rust
use thiserror::Error;

#[derive(Debug, Error)]
enum AppError {
    #[error("{resource} not found")]
    NotFound { resource: String },

    #[error("validation failed on {field}: {message}")]
    Validation { field: String, message: String },

    #[error("authentication failed: {reason}")]
    Auth { reason: String },

    #[error(transparent)]
    Network(#[from] reqwest::Error),

    #[error(transparent)]
    Io(#[from] std::io::Error),
}
```

**Go (with error types):**
```go
var (
    ErrNotFound   = errors.New("not found")
    ErrValidation = errors.New("validation failed")
    ErrAuth       = errors.New("authentication failed")
)

type NotFoundError struct {
    Resource string
}

func (e NotFoundError) Error() string {
    return fmt.Sprintf("%s not found", e.Resource)
}

func (e NotFoundError) Is(target error) bool {
    return target == ErrNotFound
}
```

---

## "Let It Crash" Philosophy (BEAM)

Erlang/Elixir use a fundamentally different error philosophy.

### Comparison

| Traditional Approach         | "Let It Crash" Approach                           |
|------------------------------|---------------------------------------------------|
| Catch and handle every error | Handle expected errors, let unexpected ones crash |
| Error recovery in-process    | Supervisor restarts clean process                 |
| Complex error handling code  | Simple code, complex supervision tree             |
| State corruption possible    | Fresh state on restart                            |

### When to Use Each

**Handle explicitly:**
- Expected conditions (user not found, validation failed)
- Business logic errors
- Recoverable states

**Let crash:**
- Programmer errors (nil dereference)
- Unrecoverable state corruption
- Configuration errors at startup
- Network partitions (let supervisor handle)

### Supervision Strategies

| Strategy | Behavior |
|----------|----------|
| `:one_for_one` | Restart only crashed child |
| `:one_for_all` | Restart all children if one crashes |
| `:rest_for_one` | Restart crashed child and all after it |
| `:simple_one_for_one` | Dynamic children, same spec |

---

## Error Context / Wrapping

### Adding Context

| Language | Pattern |
|----------|---------|
| Rust | `anyhow::Context` or manual |
| Go | `fmt.Errorf("context: %w", err)` |
| Python | `raise NewError("context") from err` |
| TypeScript | `new Error("msg", { cause: err })` |

### Rust Context Example

```rust
use anyhow::{Context, Result};

fn load_config() -> Result<Config> {
    let path = get_config_path()
        .context("failed to determine config path")?;

    let content = fs::read_to_string(&path)
        .with_context(|| format!("failed to read {}", path.display()))?;

    parse_config(&content)
        .context("failed to parse config")
}
```

---

## Error Propagation Patterns

### Rust ? Operator

```rust
fn process() -> Result<Output, Error> {
    let a = step_a()?;  // Returns early if Err
    let b = step_b(a)?;
    let c = step_c(b)?;
    Ok(c)
}
```

### Go Error Checking

```go
func process() (Output, error) {
    a, err := stepA()
    if err != nil {
        return Output{}, fmt.Errorf("step a: %w", err)
    }

    b, err := stepB(a)
    if err != nil {
        return Output{}, fmt.Errorf("step b: %w", err)
    }

    c, err := stepC(b)
    if err != nil {
        return Output{}, fmt.Errorf("step c: %w", err)
    }

    return c, nil
}
```

### Elixir with Statement

```elixir
def process() do
  with {:ok, a} <- step_a(),
       {:ok, b} <- step_b(a),
       {:ok, c} <- step_c(b) do
    {:ok, c}
  else
    {:error, reason} -> {:error, reason}
  end
end
```

---

## Panic vs Error Decision

### When to Panic/Crash

| Scenario | Action |
|----------|--------|
| Invalid function arguments (programmer error) | Panic |
| Recoverable failure (file not found) | Return error |
| Unrecoverable state corruption | Panic |
| Out of memory | Panic (implicit) |
| Configuration error at startup | Panic |
| Network timeout | Return error |
| Division by zero (user input) | Return error |
| Division by zero (hardcoded) | Panic |

### Language-Specific

| Language | Panic | Error |
|----------|-------|-------|
| Rust | `panic!`, `unwrap()` | `Result<T, E>` |
| Go | `panic()` | `error` return |
| Python | Unhandled exception | Caught exception |
| Elixir | Supervisor restart | `{:error, reason}` |
