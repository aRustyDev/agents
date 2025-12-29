---
name: patterns-metaprogramming-dev
description: Cross-cutting patterns for metaprogramming mechanisms across languages. Use when translating decorators between languages, converting annotations to macros, understanding metaprogramming equivalents, or designing code generation strategies for language conversions.
---

# Metaprogramming Patterns

Cross-language reference for metaprogramming mechanisms including decorators, macros, annotations, and code generation. This skill helps translate metaprogramming patterns between languages during code conversion.

## Overview

**This skill covers:**
- Decorator/annotation/attribute comparison across languages
- Macro systems (compile-time vs runtime)
- Code generation patterns
- Translation strategies between paradigms

**This skill does NOT cover:**
- Language-specific metaprogramming tutorials (see `lang-*-dev` skills)
- Building specific decorators/macros for applications
- Runtime reflection for debugging (see language-specific skills)

---

## Metaprogramming Mechanism Comparison

| Language | Primary Mechanism | Execution Time | Power Level |
|----------|-------------------|----------------|-------------|
| TypeScript | Decorators | Runtime | Medium |
| Python | Decorators | Runtime | High |
| Rust | Proc macros, derive | Compile-time | Very High |
| Java/Kotlin | Annotations | Compile + Runtime | Medium |
| Go | `//go:generate` | Build-time | Low |
| C# | Attributes | Runtime (reflection) | Medium |
| Ruby | Metaprogramming APIs | Runtime | Very High |
| Elixir | Macros | Compile-time | Very High |

### Execution Time Impact

```
Compile-time (Rust, Elixir)
├── Zero runtime overhead
├── Full type information available
├── Complex transformations possible
└── Errors caught at compile time

Runtime (Python, TypeScript, Ruby)
├── Runtime overhead (usually minimal)
├── Dynamic behavior possible
├── Can inspect runtime values
└── Errors may occur at runtime

Build-time (Go generate)
├── Separate build step
├── Generates source files
├── No runtime mechanism
└── Manual regeneration needed
```

---

## Decorator/Annotation Comparison

### TypeScript Decorators

```typescript
// Class decorator
@Controller('/users')
class UserController {
  // Method decorator
  @Get('/:id')
  @Authorized(['admin'])
  getUser(@Param('id') id: string): User {
    return this.userService.find(id);
  }
}

// Decorator factory (returns decorator)
function Log(prefix: string) {
  return function (target: any, key: string, descriptor: PropertyDescriptor) {
    const original = descriptor.value;
    descriptor.value = function (...args: any[]) {
      console.log(`${prefix}: ${key} called`);
      return original.apply(this, args);
    };
  };
}
```

**Capabilities:**
- Class, method, property, parameter decorators
- Decorator factories for configuration
- Metadata reflection (`reflect-metadata`)
- Runtime execution (after class definition)

### Python Decorators

```python
from functools import wraps

# Function decorator
def log(prefix: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"{prefix}: {func.__name__} called")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Class decorator
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class Database:
    pass

# Method with multiple decorators (applied bottom-up)
@app.route('/users/<id>')
@requires_auth
@log("API")
def get_user(id: str) -> User:
    return user_service.find(id)
```

**Capabilities:**
- Function, method, class decorators
- Stacking multiple decorators
- Access to wrapped function's attributes
- Full runtime introspection
- Arbitrary Python code in decorators

### Rust Derive Macros and Attributes

```rust
// Derive macro (generates trait implementations)
#[derive(Debug, Clone, Serialize, Deserialize)]
struct User {
    #[serde(rename = "user_id")]
    id: String,

    #[serde(skip_serializing_if = "Option::is_none")]
    email: Option<String>,
}

// Attribute macro (transforms the item)
#[tokio::main]
async fn main() {
    // ...
}

// Proc macro (custom compile-time code generation)
#[route(GET, "/users/:id")]
async fn get_user(id: Path<String>) -> impl Responder {
    // Handler implementation
}
```

**Capabilities:**
- Derive macros for trait implementation
- Attribute macros for code transformation
- Function-like macros (`macro_rules!`, proc macros)
- Full AST access at compile time
- Zero runtime overhead

### Java/Kotlin Annotations

```java
// Runtime annotation
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Cached {
    int ttlSeconds() default 300;
}

// Usage
@RestController
@RequestMapping("/users")
public class UserController {

    @GetMapping("/{id}")
    @Cached(ttlSeconds = 60)
    public User getUser(@PathVariable String id) {
        return userService.find(id);
    }
}
```

**Capabilities:**
- Compile-time (`SOURCE`), class-file (`CLASS`), runtime (`RUNTIME`) retention
- Annotation processors for compile-time code generation
- Runtime reflection for reading annotations
- Limited to metadata (no code transformation)

### Go Generate Directives

```go
//go:generate stringer -type=Status
type Status int

const (
    Pending Status = iota
    Active
    Completed
)

//go:generate mockgen -source=service.go -destination=mock_service.go
type UserService interface {
    Find(id string) (*User, error)
}
```

**Capabilities:**
- Build-time code generation
- Executes external tools
- Generates new source files
- No runtime mechanism (just comments)
- Manual `go generate` step required

### C# Attributes

```csharp
[ApiController]
[Route("[controller]")]
public class UserController : ControllerBase
{
    [HttpGet("{id}")]
    [Authorize(Roles = "Admin")]
    [ResponseCache(Duration = 60)]
    public ActionResult<User> GetUser(string id)
    {
        return userService.Find(id);
    }
}

// Custom attribute
[AttributeUsage(AttributeTargets.Method)]
public class LogAttribute : Attribute
{
    public string Prefix { get; set; }
}
```

**Capabilities:**
- Runtime reflection to read attributes
- Compile-time analysis with Roslyn
- Source generators for code generation
- Metadata only (no direct code transformation)

---

## Translation Patterns

### Decorator → Derive Macro (TS/Python → Rust)

| Source Pattern | Rust Equivalent | Notes |
|----------------|-----------------|-------|
| `@Serialize` | `#[derive(Serialize)]` | Derive macro |
| `@validate` | Validator crate derives | `#[derive(Validate)]` |
| `@log` method decorator | Tracing + custom wrapper | No direct equivalent |
| `@cache` | Memoization crate or manual | `cached` crate |
| `@singleton` | `lazy_static!` or `OnceCell` | Different pattern |

**Example Translation:**

```typescript
// TypeScript
@Entity()
class User {
  @Column()
  @Length(1, 100)
  name: string;

  @Column()
  @IsEmail()
  email: string;
}
```

```rust
// Rust equivalent
#[derive(Debug, Serialize, Deserialize, Validate)]
struct User {
    #[validate(length(min = 1, max = 100))]
    name: String,

    #[validate(email)]
    email: String,
}
```

### Decorator → Annotation (Python/TS → Java)

```python
# Python
@app.route('/users/<id>', methods=['GET'])
@requires_auth
def get_user(id: str) -> User:
    return user_service.find(id)
```

```java
// Java equivalent
@GetMapping("/users/{id}")
@PreAuthorize("isAuthenticated()")
public User getUser(@PathVariable String id) {
    return userService.find(id);
}
```

### Method Decorator → Manual Wrapper (Any → Go)

Go lacks decorators. Use wrapper functions or middleware:

```typescript
// TypeScript
@Log("API")
@Timed()
async getUser(id: string): Promise<User> {
    return this.service.find(id);
}
```

```go
// Go equivalent - middleware pattern
func LogMiddleware(prefix string, next http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        log.Printf("%s: %s %s", prefix, r.Method, r.URL.Path)
        next(w, r)
    }
}

func TimedMiddleware(next http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next(w, r)
        log.Printf("Duration: %v", time.Since(start))
    }
}

// Usage
http.HandleFunc("/users/", LogMiddleware("API", TimedMiddleware(getUser)))
```

### Class Decorator → Trait Implementation (Python → Rust)

```python
# Python
@dataclass
@total_ordering
class User:
    name: str
    age: int
```

```rust
// Rust equivalent
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord)]
struct User {
    name: String,
    age: i32,
}
```

---

## Common Use Cases

### 1. Serialization/Validation

| Use Case | TypeScript | Python | Rust | Go |
|----------|------------|--------|------|-----|
| JSON serialization | `class-transformer` | `@dataclass` + `json` | `#[derive(Serialize)]` | struct tags |
| Validation | `class-validator` | `pydantic` | `#[derive(Validate)]` | `validator` pkg |
| ORM mapping | TypeORM decorators | SQLAlchemy | Diesel derives | GORM tags |

### 2. Web Frameworks

| Framework Pattern | TypeScript | Python | Rust | Java |
|-------------------|------------|--------|------|------|
| Route definition | `@Get('/path')` | `@app.route()` | `#[get("/path")]` | `@GetMapping` |
| Dependency injection | `@Injectable()` | `@inject` | Constructor | `@Autowired` |
| Middleware | `@UseGuards()` | `@requires_auth` | Tower layers | `@PreAuthorize` |

### 3. Logging/Tracing

| Pattern | TypeScript | Python | Rust | Go |
|---------|------------|--------|------|-----|
| Method logging | `@Log()` | `@log` | `#[instrument]` | Middleware |
| Timing | `@Timed()` | `@timer` | `#[instrument]` | Middleware |
| Tracing | OpenTelemetry decorators | `@trace` | `tracing` macros | Context |

---

## Anti-Patterns

### 1. Over-decoration

```typescript
// ❌ Too many decorators obscure the logic
@Controller()
@UseGuards(AuthGuard)
@UseInterceptors(LoggingInterceptor)
@UsePipes(ValidationPipe)
@UseFilters(HttpExceptionFilter)
class UserController {
  @Get()
  @UseGuards(RoleGuard)
  @Serialize(UserDto)
  @Cache(60)
  @Throttle(10, 60)
  @ApiOperation({ summary: 'Get users' })
  @ApiResponse({ status: 200 })
  getUsers() { }
}

// ✓ Group related concerns
@Controller()
@UseGuards(AuthGuard, RoleGuard)
class UserController {
  @Get()
  @Cache(60)
  getUsers() { }
}
```

### 2. Side Effects in Decorators

```python
# ❌ Decorator with hidden side effects
def register(func):
    global_registry.append(func)  # Hidden mutation!
    return func

# ✓ Explicit registration
def register(func):
    func._registered = True
    return func

def collect_registered(module):
    return [f for f in dir(module) if getattr(f, '_registered', False)]
```

### 3. Decorator Order Confusion

```python
# Decorators apply bottom-up!
@decorator_a  # Applied SECOND
@decorator_b  # Applied FIRST
def func():
    pass

# Equivalent to:
func = decorator_a(decorator_b(func))
```

### 4. Losing Function Metadata

```python
# ❌ Loses original function name, docstring
def bad_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

# ✓ Preserve metadata
from functools import wraps

def good_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

---

## When No Direct Equivalent Exists

### Strategy 1: Manual Implementation

When target language lacks metaprogramming for a pattern, implement manually:

```typescript
// TypeScript: Memoization decorator
@Memoize()
function expensiveComputation(n: number): number {
    // ...
}
```

```go
// Go: Manual memoization
var cache = make(map[int]int)
var mu sync.RWMutex

func expensiveComputation(n int) int {
    mu.RLock()
    if val, ok := cache[n]; ok {
        mu.RUnlock()
        return val
    }
    mu.RUnlock()

    result := // ... compute
    mu.Lock()
    cache[n] = result
    mu.Unlock()
    return result
}
```

### Strategy 2: Code Generation

Use build-time generation when runtime metaprogramming isn't available:

```go
//go:generate go run gen_memoize.go -type=expensiveComputation
```

### Strategy 3: Interface/Trait Abstraction

Replace decorator behavior with explicit interfaces:

```typescript
// TypeScript: Decorator-based
@Injectable()
class UserService {
    @Transactional()
    async createUser(data: UserData): Promise<User> { }
}
```

```rust
// Rust: Trait-based
trait Transactional {
    async fn in_transaction<F, T>(&self, f: F) -> Result<T>
    where
        F: FnOnce() -> Result<T>;
}

impl UserService {
    async fn create_user(&self, data: UserData) -> Result<User> {
        self.in_transaction(|| {
            // ... implementation
        }).await
    }
}
```

---

## Best Practices

1. **Prefer compile-time over runtime** when possible for performance
2. **Keep decorators focused** - one responsibility per decorator
3. **Document decorator behavior** - especially execution order
4. **Preserve function metadata** - use `@wraps` in Python, etc.
5. **Consider testability** - decorated code should remain testable
6. **Avoid magic** - decorator behavior should be predictable
7. **Match target language idioms** - don't force patterns that don't fit

---

## Related Skills

- `meta-convert-dev` - Code conversion patterns
- `convert-*` skills - Language-specific conversions
- `lang-*-dev` skills - Language-specific metaprogramming details
- `patterns-serialization-dev` - Serialization patterns (often uses metaprogramming)
