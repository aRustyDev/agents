# Error Handling Examples

Code examples showing error handling translation between languages.

---

## Exception → Result Type

### TypeScript → Rust

```typescript
// TypeScript: throws exception
function parseConfig(path: string): Config {
  const content = fs.readFileSync(path, "utf-8");
  try {
    return JSON.parse(content);
  } catch (e) {
    throw new Error(`Failed to parse config: ${e.message}`);
  }
}

// Usage
try {
  const config = parseConfig("config.json");
  console.log(config);
} catch (e) {
  console.error("Config error:", e);
}
```

```rust
// Rust: returns Result
fn parse_config(path: &Path) -> Result<Config, ConfigError> {
    let content = fs::read_to_string(path)
        .map_err(|e| ConfigError::ReadFailed(e))?;
    serde_json::from_str(&content)
        .map_err(|e| ConfigError::ParseFailed(e))
}

// Usage
match parse_config(Path::new("config.json")) {
    Ok(config) => println!("{:?}", config),
    Err(e) => eprintln!("Config error: {}", e),
}

// Or with ? in caller
let config = parse_config(Path::new("config.json"))?;
```

---

## Exception → Error Return

### TypeScript → Go

```typescript
// TypeScript: throws
function divide(a: number, b: number): number {
  if (b === 0) throw new Error("division by zero");
  return a / b;
}

// Usage
try {
  const result = divide(10, 0);
} catch (e) {
  console.error(e.message);
}
```

```go
// Go: error return
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// Usage
result, err := divide(10, 0)
if err != nil {
    log.Printf("Error: %v", err)
    return
}
fmt.Println(result)
```

---

## Error Hierarchy Translation

### TypeScript Class Hierarchy → Rust Enum

```typescript
// TypeScript: class hierarchy
class AppError extends Error {
  constructor(
    message: string,
    public code: string,
  ) {
    super(message);
    this.name = "AppError";
  }
}

class NotFoundError extends AppError {
  constructor(resource: string) {
    super(`${resource} not found`, "NOT_FOUND");
  }
}

class ValidationError extends AppError {
  constructor(
    message: string,
    public field: string,
  ) {
    super(message, "VALIDATION");
  }
}

// Usage
function findUser(id: string): User {
  const user = db.get(id);
  if (!user) throw new NotFoundError("User");
  return user;
}
```

```rust
// Rust: enum variants with thiserror
use thiserror::Error;

#[derive(Debug, Error)]
enum AppError {
    #[error("{resource} not found")]
    NotFound { resource: String },

    #[error("validation failed on {field}: {message}")]
    Validation { field: String, message: String },

    #[error(transparent)]
    Io(#[from] std::io::Error),

    #[error(transparent)]
    Database(#[from] sqlx::Error),
}

// Usage
fn find_user(id: &str) -> Result<User, AppError> {
    db.get(id).ok_or_else(|| AppError::NotFound {
        resource: "User".into()
    })
}
```

---

## Python Exception → Rust Result

```python
# Python: exceptions with context
class UserError(Exception):
    pass

class NotFoundError(UserError):
    def __init__(self, resource: str, id: str):
        self.resource = resource
        self.id = id
        super().__init__(f"{resource} with id {id} not found")

def get_user(user_id: str) -> User:
    try:
        return db.query(User).get(user_id)
    except DatabaseError as e:
        raise UserError(f"Database failed: {e}") from e
    if user is None:
        raise NotFoundError("User", user_id)
    return user
```

```rust
// Rust: error types with context
use thiserror::Error;

#[derive(Debug, Error)]
enum UserError {
    #[error("{resource} with id {id} not found")]
    NotFound { resource: String, id: String },

    #[error("database failed")]
    Database(#[from] sqlx::Error),
}

fn get_user(user_id: &str) -> Result<User, UserError> {
    let user = db.query::<User>()
        .get(user_id)?;  // Database errors auto-convert

    user.ok_or_else(|| UserError::NotFound {
        resource: "User".into(),
        id: user_id.into(),
    })
}
```

---

## Go Error → Rust Result

```go
// Go: error wrapping
import (
    "errors"
    "fmt"
)

var ErrNotFound = errors.New("not found")
var ErrValidation = errors.New("validation failed")

func GetUser(id string) (*User, error) {
    user, err := db.Query(id)
    if err != nil {
        return nil, fmt.Errorf("database query: %w", err)
    }
    if user == nil {
        return nil, fmt.Errorf("user %s: %w", id, ErrNotFound)
    }
    return user, nil
}

// Checking error type
if errors.Is(err, ErrNotFound) {
    // handle not found
}
```

```rust
// Rust: equivalent pattern
use thiserror::Error;

#[derive(Debug, Error)]
enum UserError {
    #[error("user {0} not found")]
    NotFound(String),

    #[error("database query failed")]
    Database(#[from] sqlx::Error),
}

fn get_user(id: &str) -> Result<User, UserError> {
    let user = db.query(id)?;  // auto-wraps database errors

    user.ok_or_else(|| UserError::NotFound(id.into()))
}

// Checking error type
match result {
    Err(UserError::NotFound(id)) => { /* handle */ }
    Err(UserError::Database(e)) => { /* handle */ }
    Ok(user) => { /* success */ }
}
```

---

## Elixir Pattern Matching → Other Languages

```elixir
# Elixir: tuple-based errors with pattern matching
def get_user(id) do
  case Repo.get(User, id) do
    nil -> {:error, :not_found}
    user -> {:ok, user}
  end
end

def create_order(user_id, items) do
  with {:ok, user} <- get_user(user_id),
       {:ok, validated} <- validate_items(items),
       {:ok, order} <- Repo.insert(%Order{user: user, items: validated}) do
    {:ok, order}
  else
    {:error, :not_found} -> {:error, "User not found"}
    {:error, :invalid_items} -> {:error, "Invalid items"}
    {:error, changeset} -> {:error, format_errors(changeset)}
  end
end
```

```rust
// Rust: Result chaining
fn get_user(id: i64) -> Result<User, UserError> {
    repo.get::<User>(id)
        .ok_or(UserError::NotFound)
}

fn create_order(user_id: i64, items: Vec<Item>) -> Result<Order, OrderError> {
    let user = get_user(user_id)
        .map_err(|_| OrderError::UserNotFound)?;

    let validated = validate_items(&items)
        .map_err(|_| OrderError::InvalidItems)?;

    repo.insert(Order::new(user, validated))
        .map_err(OrderError::Database)
}
```

```typescript
// TypeScript: Result type pattern (neverthrow library)
import { ok, err, Result } from "neverthrow";

function getUser(id: string): Result<User, "not_found"> {
  const user = repo.get(id);
  return user ? ok(user) : err("not_found");
}

function createOrder(
  userId: string,
  items: Item[],
): Result<Order, OrderError> {
  return getUser(userId)
    .mapErr(() => ({ type: "user_not_found" as const }))
    .andThen((user) =>
      validateItems(items)
        .mapErr(() => ({ type: "invalid_items" as const }))
        .map((validated) => ({ user, validated })),
    )
    .andThen(({ user, validated }) => repo.insert(new Order(user, validated)));
}
```

---

## Error Context / Wrapping

### Adding Context to Errors

```typescript
// TypeScript: error cause (ES2022)
try {
  await fetchData();
} catch (e) {
  throw new Error("Failed to load user data", { cause: e });
}
```

```rust
// Rust: anyhow for context
use anyhow::{Context, Result};

fn load_user_data() -> Result<UserData> {
    let response = fetch_data()
        .context("Failed to fetch from API")?;

    parse_response(response)
        .context("Failed to parse user data")
}
```

```go
// Go: fmt.Errorf with %w
func loadUserData() (*UserData, error) {
    response, err := fetchData()
    if err != nil {
        return nil, fmt.Errorf("failed to fetch from API: %w", err)
    }

    data, err := parseResponse(response)
    if err != nil {
        return nil, fmt.Errorf("failed to parse user data: %w", err)
    }

    return data, nil
}
```

```python
# Python: exception chaining
try:
    response = fetch_data()
except RequestError as e:
    raise UserDataError("Failed to fetch from API") from e

try:
    data = parse_response(response)
except ParseError as e:
    raise UserDataError("Failed to parse user data") from e
```

---

## Panic vs Error

### When to Panic/Crash

| Scenario | Rust | Go | Elixir |
|----------|------|-----|--------|
| Invalid args (programmer error) | `panic!` | `panic()` | `raise` |
| Recoverable failure | `Result<T, E>` | `error` return | `{:error, reason}` |
| Unrecoverable state | `panic!` | `panic()` | Supervisor restart |
| Out of memory | `panic!` (implicit) | `panic()` | VM handles |

```rust
// Rust: panic for invariant violations
fn get_index(items: &[Item], index: usize) -> &Item {
    // Panic if index out of bounds - programmer error
    &items[index]
}

// Result for expected failures
fn find_by_id(items: &[Item], id: &str) -> Option<&Item> {
    items.iter().find(|i| i.id == id)
}
```

```go
// Go: panic for unrecoverable, error for expected
func mustParseConfig(path string) Config {
    config, err := parseConfig(path)
    if err != nil {
        panic(fmt.Sprintf("invalid config: %v", err))
    }
    return config
}

func parseConfig(path string) (Config, error) {
    // Returns error for handling
    data, err := os.ReadFile(path)
    if err != nil {
        return Config{}, err
    }
    // ...
}
```
