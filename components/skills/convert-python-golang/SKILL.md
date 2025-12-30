---
name: convert-python-golang
description: Convert Python code to idiomatic Go. Use when migrating Python projects to Go, translating Python patterns to idiomatic Go, or refactoring Python codebases for performance and concurrency. Extends meta-convert-dev with Python-to-Go specific patterns.
---

# Convert Python to Go

Convert Python code to idiomatic Go. This skill extends `meta-convert-dev` with Python-to-Go specific type mappings, idiom translations, and tooling for transforming dynamic, interpreted Python code into static, compiled Go.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Python types → Go types (dynamic → static)
- **Idiom translations**: Python patterns → idiomatic Go
- **Error handling**: Exceptions → multiple return values with error
- **Async patterns**: asyncio → goroutines and channels
- **Memory model**: Python GC → Go GC (both garbage collected, different idioms)
- **Type system**: Duck typing → interfaces and struct embedding
- **Build system**: pip/uv → go modules

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Python language fundamentals - see `lang-python-dev`
- Go language fundamentals - see `lang-go-dev`
- Reverse conversion (Go → Python) - see `convert-golang-python`

---

## Quick Reference

| Python | Go | Notes |
|--------|-----|-------|
| `int` | `int`, `int64`, `big.Int` | Python has arbitrary precision |
| `float` | `float64` | IEEE 754 double precision |
| `bool` | `bool` | Direct mapping |
| `str` | `string` | Immutable UTF-8 strings |
| `bytes` | `[]byte` | Byte slices |
| `list[T]` | `[]T` | Slices (dynamic arrays) |
| `tuple` | `struct{}` or array | Use struct for heterogeneous |
| `dict[K, V]` | `map[K]V` | Hash maps |
| `set[T]` | `map[T]bool` or `map[T]struct{}` | No built-in set type |
| `None` | `nil` (for pointers) or zero value | Context-dependent |
| `Optional[T]` | `*T` (pointer) | Pointer = nullable |
| `Union[T, U]` | `interface{}` or custom type | Use type assertions |
| `def func():` | `func name() {}` | Functions |
| `async def` | `func` + goroutines | No async/await syntax |
| `with` | `defer` | Resource cleanup |
| `@decorator` | Function wrappers | No decorator syntax |
| `class` | `type` + struct | Composition over inheritance |
| Exception | `error` return value | Multiple return values |

## When Converting Code

1. **Analyze source thoroughly** before writing target
2. **Map types first** - create type equivalence table
3. **Handle arbitrary-precision integers** - decide if `int64` is enough or need `big.Int`
4. **Preserve semantics** over syntax similarity
5. **Adopt Go idioms** - don't write "Python code in Go syntax"
6. **Handle edge cases** - None, exceptions, dynamic typing assumptions
7. **Test equivalence** - same inputs → same outputs

---

## Type System Mapping

### Primitive Types

| Python | Go | Notes |
|--------|-----|-------|
| `int` | `int` | Platform-dependent (32 or 64-bit) |
| `int` | `int64` | Explicit 64-bit for large numbers |
| `int` | `math/big.Int` | **Python default** - arbitrary precision |
| `float` | `float64` | IEEE 754 double precision |
| `bool` | `bool` | Direct mapping |
| `str` | `string` | Immutable UTF-8 strings |
| `bytes` | `[]byte` | Byte slice |
| `bytearray` | `[]byte` | Mutable byte slice |
| `None` | `nil` | For pointers, slices, maps, channels |
| `None` | Zero value | For value types (0, false, "") |

**Critical Note on Integers**: Python's `int` type has **arbitrary precision** and never overflows. Go integers are fixed-size and **can overflow**. Always validate range or use `math/big.Int` for Python-like behavior.

### Collection Types

| Python | Go | Notes |
|--------|-----|-------|
| `list[T]` | `[]T` | Slice (dynamic array) |
| `tuple[T, U]` | `struct{X T; Y U}` | Heterogeneous tuple → struct |
| `tuple[T, ...]` | `[]T` | Homogeneous tuple → slice |
| `dict[K, V]` | `map[K]V` | Hash map |
| `set[T]` | `map[T]bool` | Set as map keys |
| `set[T]` | `map[T]struct{}` | Memory-efficient set |
| `frozenset[T]` | `map[T]struct{}` | Go maps are mutable |
| `collections.deque` | `container/list.List` | Doubly-linked list |
| `collections.OrderedDict` | Map iteration (Go 1.12+) | Maps preserve insertion order in Go 1.12+ |
| `collections.defaultdict` | Map with check | Use map access pattern |
| `collections.Counter` | `map[T]int` | Count occurrences |

### Composite Types

| Python | Go | Notes |
|--------|-----|-------|
| `class` (data) | `struct` | Data containers |
| `class` (behavior) | `interface` | Behavior contracts |
| `@dataclass` | `struct` with literal | Simple data structures |
| `typing.Protocol` | `interface` | Duck typing → interfaces |
| `typing.TypedDict` | `struct` | Named fields |
| `typing.NamedTuple` | `struct` | Prefer struct |
| `enum.Enum` | `const` with iota | Enumerated constants |
| `typing.Literal["a", "b"]` | `const` or custom type | Literal types |
| `typing.Union[T, U]` | `interface{}` + type assertion | Or custom type |
| `typing.Optional[T]` | `*T` (pointer) | Pointer = nullable |
| `typing.Callable[[Args], Ret]` | `func(Args) Ret` | Function types |
| `typing.Generic[T]` | Interfaces | Go 1.18+ generics limited |

### Type Annotations → Interfaces

| Python | Go | Notes |
|--------|-----|-------|
| `def f(x: Iterable[T])` | `func f(x []T)` | Slice for most cases |
| `def f(x: Sequence[T])` | `func f(x []T)` | Slice for sequences |
| `def f(x: Mapping[K, V])` | `func f(x map[K]V)` | Map for mappings |
| `x: Any` | `interface{}` (or `any`) | Use sparingly |

---

## Idiom Translation

### Pattern 1: None Handling (Optional Values)

**Python:**
```python
# Optional chaining
user = get_user(user_id)
if user is not None:
    name = user.name
else:
    name = "Anonymous"

# Or with walrus operator
if user := get_user(user_id):
    name = user.name
```

**Go:**
```go
// Pointer nil check
user := getUser(userID)
var name string
if user != nil {
    name = user.Name
} else {
    name = "Anonymous"
}

// Or with early return
user := getUser(userID)
if user == nil {
    name = "Anonymous"
} else {
    name = user.Name
}
```

**Why this translation:**
- Python uses `None` with truthiness; Go uses `nil` with explicit pointer checks
- Go's zero values provide defaults without needing `None` for primitives
- Go pointers are explicit about nullability

### Pattern 2: List Comprehensions → Slice Loops

**Python:**
```python
# List comprehension
squared_evens = [x * x for x in numbers if x % 2 == 0]

# Generator expression
total = sum(x * x for x in numbers if x % 2 == 0)
```

**Go:**
```go
// Slice with filtering and mapping
var squaredEvens []int
for _, x := range numbers {
    if x % 2 == 0 {
        squaredEvens = append(squaredEvens, x*x)
    }
}

// Manual aggregation
total := 0
for _, x := range numbers {
    if x % 2 == 0 {
        total += x * x
    }
}
```

**Why this translation:**
- Go doesn't have list comprehensions; use explicit loops
- `range` loops are idiomatic for iteration
- `append` grows slices dynamically (similar to Python lists)

### Pattern 3: Dictionary Operations

**Python:**
```python
# Get with default
value = config.get("timeout", 30)

# Setdefault pattern
cache.setdefault(key, expensive_compute())

# Dictionary comprehension
squared = {k: v * v for k, v in items.items()}
```

**Go:**
```go
// Get with default
value, ok := config["timeout"]
if !ok {
    value = 30
}

// Check and set pattern
if _, ok := cache[key]; !ok {
    cache[key] = expensiveCompute()
}

// Manual map building
squared := make(map[string]int)
for k, v := range items {
    squared[k] = v * v
}
```

**Why this translation:**
- Go's two-value map access (`value, ok := map[key]`) checks existence
- No built-in `get` method; use existence check pattern
- Explicit loops replace comprehensions

### Pattern 4: String Formatting

**Python:**
```python
# f-strings
message = f"User {user.name} has {count} items"

# format method
message = "User {} has {} items".format(user.name, count)
```

**Go:**
```go
// fmt.Sprintf (returns string)
message := fmt.Sprintf("User %s has %d items", user.Name, count)

// fmt.Printf (prints directly)
fmt.Printf("User %s has %d items\n", user.Name, count)
```

**Why this translation:**
- Go uses `fmt` package with C-style format specifiers
- `%s` for strings, `%d` for integers, `%v` for default format
- Type-safe at runtime (not compile-time like some languages)

### Pattern 5: Duck Typing → Interfaces

**Python:**
```python
# Duck typing - if it has .read(), it's file-like
def process_data(file_like):
    data = file_like.read()
    return parse(data)

# Works with files, StringIO, BytesIO, etc.
```

**Go:**
```go
// Interface definition
type Reader interface {
    Read(p []byte) (n int, err error)
}

// Function accepts interface
func processData(r Reader) (Data, error) {
    data, err := io.ReadAll(r)
    if err != nil {
        return Data{}, err
    }
    return parse(data)
}

// Works with *os.File, bytes.Buffer, strings.Reader, etc.
```

**Why this translation:**
- Python relies on runtime duck typing; Go uses compile-time interfaces
- Go interfaces are implicit (no "implements" keyword)
- More type-safe but requires upfront interface definition

### Pattern 6: Context Managers → Defer

**Python:**
```python
# Context manager for resource cleanup
with open("file.txt") as f:
    data = f.read()
# File automatically closed
```

**Go:**
```go
// Defer for cleanup
f, err := os.Open("file.txt")
if err != nil {
    return err
}
defer f.Close() // Guaranteed to run when function returns

data, err := io.ReadAll(f)
if err != nil {
    return err
}
```

**Why this translation:**
- Python's `with` guarantees cleanup via `__exit__`
- Go's `defer` schedules function calls for later (LIFO order)
- Both ensure cleanup even with errors/returns

### Pattern 7: Decorators → Function Wrappers

**Python:**
```python
from functools import wraps

def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    return wrapper

@log_calls
def process_data(data):
    return len(data)
```

**Go:**
```go
// Function wrapper pattern
func logCalls(name string, fn func([]byte) int) func([]byte) int {
    return func(data []byte) int {
        fmt.Printf("Calling %s\n", name)
        result := fn(data)
        fmt.Printf("Finished %s\n", name)
        return result
    }
}

// Manual wrapping
processData := logCalls("processData", func(data []byte) int {
    return len(data)
})
```

**Why this translation:**
- Go doesn't have decorator syntax; use function wrappers
- Requires explicit wrapping instead of `@` syntax
- Type signatures must match exactly (less flexible than Python)

### Pattern 8: Class Methods and Properties

**Python:**
```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def area(self):
        return 3.14159 * self._radius ** 2

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value
```

**Go:**
```go
type Circle struct {
    radius float64
}

// Constructor
func NewCircle(radius float64) *Circle {
    return &Circle{radius: radius}
}

// Getter (no "Get" prefix in Go)
func (c *Circle) Area() float64 {
    return 3.14159 * c.radius * c.radius
}

func (c *Circle) Radius() float64 {
    return c.radius
}

// Setter
func (c *Circle) SetRadius(value float64) error {
    if value < 0 {
        return errors.New("radius cannot be negative")
    }
    c.radius = value
    return nil
}
```

**Why this translation:**
- Go doesn't have properties; use methods
- No automatic getter/setter generation
- Explicit error returns instead of exceptions

---

## Error Handling

### Python Exceptions → Go Multiple Returns

**Python:**
```python
def divide(a, b):
    if b == 0:
        raise ValueError("division by zero")
    return a / b

# Caller
try:
    result = divide(10, 2)
    print(f"Result: {result}")
except ValueError as e:
    print(f"Error: {e}")
```

**Go:**
```go
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// Caller
result, err := divide(10, 2)
if err != nil {
    fmt.Printf("Error: %v\n", err)
    return
}
fmt.Printf("Result: %f\n", result)
```

**Translation rules:**
- Python raises exceptions; Go returns `(result, error)`
- Check `err != nil` immediately after function call
- Return early on error (guard clauses)
- `nil` error means success

### Custom Exceptions → Custom Error Types

**Python:**
```python
class ValidationError(Exception):
    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

raise ValidationError("email", "invalid format")
```

**Go:**
```go
type ValidationError struct {
    Field   string
    Message string
}

func (e ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Message)
}

// Return custom error
return ValidationError{Field: "email", Message: "invalid format"}
```

**Translation rules:**
- Implement `Error() string` method to satisfy `error` interface
- Add fields for error context
- Use `errors.Is()` and `errors.As()` for error type checking

### Exception Hierarchies → Error Wrapping

**Python:**
```python
try:
    process_data()
except ValueError as e:
    raise ConfigError(f"Invalid config: {e}") from e
```

**Go:**
```go
err := processData()
if err != nil {
    return fmt.Errorf("invalid config: %w", err)
}

// Check wrapped error
if errors.Is(err, os.ErrNotExist) {
    // Handle specific error
}
```

**Translation rules:**
- Use `%w` in `fmt.Errorf` to wrap errors
- `errors.Is()` checks error identity (unwraps chain)
- `errors.As()` extracts specific error types

---

## Concurrency Patterns

### Asyncio → Goroutines and Channels

**Python:**
```python
import asyncio

async def fetch_user(user_id):
    await asyncio.sleep(0.1)  # Simulate I/O
    return {"id": user_id, "name": f"User {user_id}"}

async def main():
    # Sequential
    user1 = await fetch_user(1)
    user2 = await fetch_user(2)

    # Concurrent
    users = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3)
    )
    print(users)

asyncio.run(main())
```

**Go:**
```go
import "time"

func fetchUser(userID int) User {
    time.Sleep(100 * time.Millisecond) // Simulate I/O
    return User{ID: userID, Name: fmt.Sprintf("User %d", userID)}
}

func main() {
    // Sequential
    user1 := fetchUser(1)
    user2 := fetchUser(2)

    // Concurrent with goroutines and channels
    ch := make(chan User, 3)
    for _, id := range []int{1, 2, 3} {
        id := id // Capture loop variable
        go func() {
            ch <- fetchUser(id)
        }()
    }

    // Collect results
    var users []User
    for i := 0; i < 3; i++ {
        users = append(users, <-ch)
    }
    fmt.Println(users)
}
```

**Why this translation:**
- Python uses `async/await` syntax; Go uses goroutines (lightweight threads)
- Go channels replace asyncio coordination
- No event loop - goroutines are managed by runtime

### Threading → Goroutines with Sync

**Python:**
```python
from concurrent.futures import ThreadPoolExecutor

def fetch_url(url):
    # I/O-bound operation
    return f"Content from {url}"

urls = ["http://example.com", "http://example.org"]

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(fetch_url, urls))
```

**Go:**
```go
import "sync"

func fetchURL(url string) string {
    // I/O-bound operation
    return fmt.Sprintf("Content from %s", url)
}

func main() {
    urls := []string{"http://example.com", "http://example.org"}

    var wg sync.WaitGroup
    results := make([]string, len(urls))

    for i, url := range urls {
        wg.Add(1)
        go func(i int, url string) {
            defer wg.Done()
            results[i] = fetchURL(url)
        }(i, url)
    }

    wg.Wait()
    fmt.Println(results)
}
```

**Why this translation:**
- Python ThreadPoolExecutor → Go goroutines + WaitGroup
- Go's goroutines are cheaper than OS threads
- `sync.WaitGroup` waits for goroutines to complete

### Multiprocessing → Goroutines (Usually)

**Python:**
```python
from multiprocessing import Pool

def cpu_bound_task(n):
    return sum(i * i for i in range(n))

with Pool(4) as pool:
    results = pool.map(cpu_bound_task, [1000000] * 4)
```

**Go:**
```go
func cpuBoundTask(n int) int {
    sum := 0
    for i := 0; i < n; i++ {
        sum += i * i
    }
    return sum
}

func main() {
    runtime.GOMAXPROCS(4) // Optional: limit CPU cores

    var wg sync.WaitGroup
    results := make([]int, 4)

    for i := 0; i < 4; i++ {
        wg.Add(1)
        go func(i int) {
            defer wg.Done()
            results[i] = cpuBoundTask(1000000)
        }(i)
    }

    wg.Wait()
    fmt.Println(results)
}
```

**Why this translation:**
- Python uses multiprocessing to bypass GIL for CPU-bound tasks
- Go's goroutines can run in parallel on multiple cores (no GIL)
- Same pattern (goroutines) works for both I/O and CPU-bound tasks

---

## Paradigm Translation

### Mental Model Shift: Dynamic → Static Typing

| Python Concept | Go Approach | Key Insight |
|----------------|-------------|-------------|
| Duck typing | Interfaces | Type contracts defined upfront |
| Dynamic attributes | Struct fields | Fixed structure |
| `**kwargs` flexibility | Options pattern | Functional options for flexibility |
| Multiple inheritance | Composition + embedding | Favor composition |
| Monkey patching | Avoid | Build-time dependency injection |

### Object-Oriented → Struct-Based

**Python:**
```python
class Animal:
    def speak(self):
        raise NotImplementedError

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"
```

**Go:**
```go
// Interface defines behavior
type Animal interface {
    Speak() string
}

// Structs implement interface implicitly
type Dog struct{}

func (d Dog) Speak() string {
    return "Woof!"
}

type Cat struct{}

func (c Cat) Speak() string {
    return "Meow!"
}

// Use interface for polymorphism
func makeSound(a Animal) {
    fmt.Println(a.Speak())
}
```

**Key differences:**
- Go has no classes or inheritance
- Interfaces are implicit (no "implements" keyword)
- Composition via struct embedding

---

## Module and Import System

### Python Imports → Go Packages

**Python:**
```python
# myproject/utils/strings.py
def capitalize(s):
    return s.upper()

# myproject/main.py
from utils.strings import capitalize
# Or
from utils import strings
```

**Go:**
```go
// myproject/utils/strings.go
package utils

func Capitalize(s string) string {
    return strings.ToUpper(s)
}

// myproject/main.go
package main

import "myproject/utils"

func main() {
    result := utils.Capitalize("hello")
}
```

**Translation rules:**
- Python modules are files; Go packages are directories
- Uppercase names are exported (public) in Go
- Import path is directory path, not file path

### Python __init__.py → Go Package Organization

**Python:**
```python
# mypackage/__init__.py
from .module_a import ClassA
from .module_b import ClassB

__all__ = ["ClassA", "ClassB"]
```

**Go:**
```go
// All .go files in same directory are same package
// No __init__.go equivalent

// mypackage/module_a.go
package mypackage

type ClassA struct {}

// mypackage/module_b.go
package mypackage

type ClassB struct {}

// Exported names (uppercase) are automatically public
```

**Translation rules:**
- Go has no `__init__` file
- All `.go` files in a directory must have same `package` declaration
- Visibility controlled by capitalization

---

## Build and Dependencies

### pip/uv → go modules

**Python:**
```bash
# requirements.txt
requests==2.31.0
pytest>=7.4.0

# Install
pip install -r requirements.txt
```

**Go:**
```bash
# go.mod (generated)
module github.com/user/myproject

go 1.21

require (
    github.com/gorilla/mux v1.8.0
)

# Add dependency
go get github.com/gorilla/mux@v1.8.0

# Update all
go get -u ./...

# Cleanup
go mod tidy
```

**Translation rules:**
- `go.mod` is like `pyproject.toml` (declarative)
- `go.sum` is like lock file (checksums)
- No virtual environments needed (per-project modules)

### Project Structure

**Python:**
```
myproject/
├── pyproject.toml
├── src/
│   └── myproject/
│       ├── __init__.py
│       └── core.py
└── tests/
    └── test_core.py
```

**Go:**
```
myproject/
├── go.mod
├── go.sum
├── main.go
├── internal/        # Private packages
│   └── core/
│       └── core.go
└── core_test.go     # Tests alongside code
```

**Translation rules:**
- Go tests live next to source (`*_test.go`)
- `internal/` packages can't be imported by external projects
- Flat structure preferred over deep nesting

---

## Testing

### pytest → testing package

**Python:**
```python
# test_math.py
import pytest

def test_add():
    assert add(1, 2) == 3

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (-1, 1, 0),
])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected

@pytest.fixture
def sample_data():
    return [1, 2, 3]

def test_with_fixture(sample_data):
    assert len(sample_data) == 3
```

**Go:**
```go
// math_test.go
package math

import "testing"

func TestAdd(t *testing.T) {
    result := Add(1, 2)
    if result != 3 {
        t.Errorf("Add(1, 2) = %d; want 3", result)
    }
}

// Table-driven test (idiomatic Go)
func TestAddTable(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 1, 2, 3},
        {"negative", -1, 1, 0},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Add(tt.a, tt.b)
            if result != tt.expected {
                t.Errorf("Add(%d, %d) = %d; want %d",
                    tt.a, tt.b, result, tt.expected)
            }
        })
    }
}

// Test helper (like fixture)
func setupData(t *testing.T) []int {
    t.Helper()
    data := []int{1, 2, 3}
    t.Cleanup(func() {
        // Cleanup if needed
    })
    return data
}

func TestWithHelper(t *testing.T) {
    data := setupData(t)
    if len(data) != 3 {
        t.Errorf("len(data) = %d; want 3", len(data))
    }
}
```

**Translation rules:**
- `pytest` → `go test` (built-in)
- Parametrize → table-driven tests (idiomatic)
- Fixtures → helper functions with `t.Helper()`

---

## Common Pitfalls

1. **Forgetting to Check Errors**

Python exceptions are automatic; Go errors must be checked explicitly.

```go
// Bad
result, _ := doSomething() // Ignoring error

// Good
result, err := doSomething()
if err != nil {
    return err
}
```

2. **Treating nil Like None**

Python `None` can be used for any type; Go `nil` only works with pointers, slices, maps, channels, functions, and interfaces.

```go
// Bad
var name string = nil  // Compile error

// Good
var name *string = nil  // OK - pointer
var name string         // OK - zero value ""
```

3. **Modifying Loop Variables in Goroutines**

```go
// Bad
for _, item := range items {
    go func() {
        process(item) // All goroutines see last item!
    }()
}

// Good
for _, item := range items {
    item := item // Capture loop variable
    go func() {
        process(item)
    }()
}
```

4. **Expecting Reference Semantics for Structs**

Python objects are references; Go structs are values (copy on assignment).

```go
// Bad
func updateUser(u User) {
    u.Name = "Updated" // Modifies copy, not original
}

// Good
func updateUser(u *User) {
    u.Name = "Updated" // Modifies original via pointer
}
```

5. **Integer Overflow**

Python integers never overflow; Go integers wrap or panic.

```go
var x int64 = 9223372036854775807 // Max int64
x = x + 1 // Overflows to negative in production

// Use math/big for arbitrary precision
import "math/big"
x := big.NewInt(9223372036854775807)
x.Add(x, big.NewInt(1)) // No overflow
```

6. **Map Iteration Order**

Python dicts maintain insertion order (3.7+); Go maps have random iteration order.

```go
// Order is not guaranteed
for key, value := range myMap {
    // Don't rely on order
}

// Use slice of keys for consistent order
keys := make([]string, 0, len(myMap))
for key := range myMap {
    keys = append(keys, key)
}
sort.Strings(keys)
for _, key := range keys {
    // Ordered iteration
}
```

7. **Shadowing Variables with :=**

```go
// Bad
user, err := getUser(1)
if err != nil {
    user, err := getUser(2) // Shadows outer user!
    // ...
}
// user is still from getUser(1)

// Good
user, err := getUser(1)
if err != nil {
    user, err = getUser(2) // Reuses outer user
    // ...
}
```

---

## Serialization

### JSON: Python json → Go encoding/json

**Python:**
```python
import json
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str
    age: int

user = User(name="Alice", email="alice@example.com", age=30)

# Serialize
json_str = json.dumps(user.__dict__)

# Deserialize
data = json.loads(json_str)
user = User(**data)
```

**Go:**
```go
import "encoding/json"

type User struct {
    Name  string `json:"name"`
    Email string `json:"email"`
    Age   int    `json:"age"`
}

user := User{Name: "Alice", Email: "alice@example.com", Age: 30}

// Serialize
data, err := json.Marshal(user)
if err != nil {
    return err
}

// Deserialize
var user User
err = json.Unmarshal(data, &user)
if err != nil {
    return err
}
```

**Translation rules:**
- Use struct tags for field names: `json:"field_name"`
- `json:",omitempty"` for optional fields
- Pointers for nullable fields

**See also:** `patterns-serialization-dev` for cross-language comparison

---

## Zero Values and Defaults

### Python None → Go Zero Values

**Python:**
```python
# None represents absence
value = None

# Check for None
if value is None:
    value = "default"
```

**Go:**
```go
// Zero values for each type
var i int       // 0
var f float64   // 0.0
var s string    // ""
var p *int      // nil
var slice []int // nil
var m map[K]V   // nil

// Check for nil (pointers, slices, maps)
if slice == nil {
    slice = []int{1, 2, 3}
}

// Check for zero value (strings, numbers)
if s == "" {
    s = "default"
}
```

**Translation rules:**
- Pointers, slices, maps, channels, functions → `nil`
- Numbers → `0` or `0.0`
- Strings → `""`
- Bools → `false`
- Structs → all fields zero-valued

---

## Metaprogramming

### Python Decorators → Go Code Generation

Python has runtime metaprogramming; Go uses compile-time code generation.

**Python:**
```python
# Runtime decorator
def memoize(func):
    cache = {}
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper

@memoize
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)
```

**Go:**
```go
// Manual memoization (no decorator syntax)
var fibCache = make(map[int]int)

func fib(n int) int {
    if result, ok := fibCache[n]; ok {
        return result
    }

    if n < 2 {
        return n
    }

    result := fib(n-1) + fib(n-2)
    fibCache[n] = result
    return result
}

// Or use code generation for repetitive patterns
//go:generate mockgen -source=interface.go -destination=mock.go
```

**Translation rules:**
- No decorator syntax in Go
- Use function wrappers or code generation
- `go generate` for compile-time metaprogramming

**See also:** `patterns-metaprogramming-dev` for cross-language comparison

---

## Examples

### Example 1: Simple - HTTP Client

**Before (Python):**
```python
import requests

def fetch_user(user_id: int) -> dict:
    response = requests.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()
    return response.json()

try:
    user = fetch_user(1)
    print(f"User: {user['name']}")
except requests.HTTPError as e:
    print(f"HTTP error: {e}")
except Exception as e:
    print(f"Error: {e}")
```

**After (Go):**
```go
import (
    "encoding/json"
    "fmt"
    "io"
    "net/http"
)

type User struct {
    Name string `json:"name"`
}

func fetchUser(userID int) (User, error) {
    url := fmt.Sprintf("https://api.example.com/users/%d", userID)
    resp, err := http.Get(url)
    if err != nil {
        return User{}, err
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return User{}, fmt.Errorf("HTTP error: %d", resp.StatusCode)
    }

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return User{}, err
    }

    var user User
    if err := json.Unmarshal(body, &user); err != nil {
        return User{}, err
    }

    return user, nil
}

func main() {
    user, err := fetchUser(1)
    if err != nil {
        fmt.Printf("Error: %v\n", err)
        return
    }
    fmt.Printf("User: %s\n", user.Name)
}
```

### Example 2: Medium - Concurrent Workers

**Before (Python):**
```python
import asyncio
from typing import List

async def process_item(item: int) -> int:
    await asyncio.sleep(0.1)  # Simulate work
    return item * 2

async def process_batch(items: List[int]) -> List[int]:
    tasks = [process_item(item) for item in items]
    return await asyncio.gather(*tasks)

async def main():
    items = list(range(10))
    results = await process_batch(items)
    print(f"Processed {len(results)} items")

asyncio.run(main())
```

**After (Go):**
```go
import (
    "fmt"
    "sync"
    "time"
)

func processItem(item int) int {
    time.Sleep(100 * time.Millisecond) // Simulate work
    return item * 2
}

func processBatch(items []int) []int {
    results := make([]int, len(items))
    var wg sync.WaitGroup

    for i, item := range items {
        wg.Add(1)
        go func(i, item int) {
            defer wg.Done()
            results[i] = processItem(item)
        }(i, item)
    }

    wg.Wait()
    return results
}

func main() {
    items := make([]int, 10)
    for i := range items {
        items[i] = i
    }

    results := processBatch(items)
    fmt.Printf("Processed %d items\n", len(results))
}
```

### Example 3: Complex - REST API Server

**Before (Python):**
```python
from flask import Flask, jsonify, request
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class User:
    id: int
    name: str
    email: str

app = Flask(__name__)
users: Dict[int, User] = {}
next_id = 1

@app.route('/users', methods=['GET'])
def list_users():
    return jsonify([user.__dict__ for user in users.values()])

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id: int):
    user = users.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.__dict__)

@app.route('/users', methods=['POST'])
def create_user():
    global next_id
    data = request.get_json()

    if not data.get('name') or not data.get('email'):
        return jsonify({"error": "Missing required fields"}), 400

    user = User(id=next_id, name=data['name'], email=data['email'])
    users[next_id] = user
    next_id += 1

    return jsonify(user.__dict__), 201

if __name__ == '__main__':
    app.run(debug=True)
```

**After (Go):**
```go
import (
    "encoding/json"
    "fmt"
    "net/http"
    "strconv"
    "sync"
)

type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

type Server struct {
    mu     sync.RWMutex
    users  map[int]User
    nextID int
}

func NewServer() *Server {
    return &Server{
        users:  make(map[int]User),
        nextID: 1,
    }
}

func (s *Server) handleListUsers(w http.ResponseWriter, r *http.Request) {
    s.mu.RLock()
    defer s.mu.RUnlock()

    users := make([]User, 0, len(s.users))
    for _, user := range s.users {
        users = append(users, user)
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(users)
}

func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
    idStr := r.URL.Query().Get("id")
    id, err := strconv.Atoi(idStr)
    if err != nil {
        http.Error(w, "Invalid user ID", http.StatusBadRequest)
        return
    }

    s.mu.RLock()
    user, ok := s.users[id]
    s.mu.RUnlock()

    if !ok {
        http.Error(w, "User not found", http.StatusNotFound)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(user)
}

func (s *Server) handleCreateUser(w http.ResponseWriter, r *http.Request) {
    var data struct {
        Name  string `json:"name"`
        Email string `json:"email"`
    }

    if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
        http.Error(w, "Invalid JSON", http.StatusBadRequest)
        return
    }

    if data.Name == "" || data.Email == "" {
        http.Error(w, "Missing required fields", http.StatusBadRequest)
        return
    }

    s.mu.Lock()
    user := User{
        ID:    s.nextID,
        Name:  data.Name,
        Email: data.Email,
    }
    s.users[s.nextID] = user
    s.nextID++
    s.mu.Unlock()

    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusCreated)
    json.NewEncoder(w).Encode(user)
}

func main() {
    server := NewServer()

    http.HandleFunc("/users", func(w http.ResponseWriter, r *http.Request) {
        switch r.Method {
        case http.MethodGet:
            server.handleListUsers(w, r)
        case http.MethodPost:
            server.handleCreateUser(w, r)
        default:
            http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        }
    })

    fmt.Println("Server starting on :8080")
    http.ListenAndServe(":8080", nil)
}
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-golang-python` - Reverse conversion (Go → Python)
- `lang-python-dev` - Python development patterns
- `lang-go-dev` - Go development patterns

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - Async patterns, threading, goroutines across languages
- `patterns-serialization-dev` - JSON, validation, struct tags across languages
- `patterns-metaprogramming-dev` - Decorators, code generation across languages
