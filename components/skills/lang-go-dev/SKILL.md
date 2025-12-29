---
name: lang-go-dev
description: Foundational Go patterns covering types, interfaces, goroutines, channels, and common idioms. Use when writing Go code, understanding Go's concurrency model, or needing guidance on which specialized Go skill to use. This is the entry point for Go development.
---

# Go Fundamentals

Foundational Go patterns and core language features. This skill serves as both a reference for common patterns and an index to specialized Go skills.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       Go Skill Hierarchy                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ┌─────────────────┐                          │
│                    │   lang-go-dev   │ ◄── You are here         │
│                    │  (foundation)   │                          │
│                    └────────┬────────┘                          │
│                             │                                   │
│         ┌───────────────────┼───────────────────┐               │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ concurrency │    │   testing   │    │   modules   │         │
│  │  patterns   │    │  patterns   │    │  packages   │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**This skill covers:**
- Basic types and zero values
- Structs, interfaces, and embedding
- Slices, maps, and iteration
- Error handling patterns
- Goroutines and channels basics
- Common idioms and conventions

**This skill does NOT cover (see specialized skills):**
- Advanced concurrency patterns → `go-concurrency-patterns`
- Module management and versioning → future skill
- Testing strategies → future skill
- Performance optimization → future skill

---

## Quick Reference

| Task | Syntax |
|------|--------|
| Variable declaration | `var x int` or `x := 0` |
| Constant | `const Pi = 3.14` |
| Function | `func name(x int) int { return x }` |
| Multiple return | `func f() (int, error)` |
| Struct | `type User struct { Name string }` |
| Interface | `type Reader interface { Read() }` |
| Slice | `[]int{1, 2, 3}` |
| Map | `map[string]int{"a": 1}` |
| Goroutine | `go func() { ... }()` |
| Channel | `ch := make(chan int)` |
| Defer | `defer file.Close()` |

---

## Skill Routing

Use this table to find the right specialized skill:

| When you need to... | Use this skill |
|---------------------|----------------|
| Complex concurrency (worker pools, fan-out) | `go-concurrency-patterns` |
| Module versioning, go.mod management | future: `lang-go-modules-dev` |
| Testing strategies, mocking | future: `lang-go-testing-dev` |
| HTTP servers, middleware | future: `lang-go-http-dev` |

---

## Types and Variables

### Basic Types

```go
// Boolean
var active bool = true

// Numeric types
var i int = 42           // Platform-dependent size
var i64 int64 = 42       // Explicit 64-bit
var f float64 = 3.14     // Default float type
var c complex128 = 1+2i  // Complex numbers

// String (immutable UTF-8)
var s string = "hello"

// Byte and rune
var b byte = 'A'         // Alias for uint8
var r rune = '世'        // Alias for int32 (Unicode code point)
```

### Zero Values

Every type has a zero value - no uninitialized variables in Go:

| Type | Zero Value |
|------|------------|
| `bool` | `false` |
| `int`, `float64` | `0` |
| `string` | `""` (empty string) |
| `pointer`, `slice`, `map`, `chan`, `func` | `nil` |
| `struct` | All fields zero-valued |

### Variable Declaration

```go
// Explicit type
var name string = "Alice"

// Type inference
var name = "Alice"

// Short declaration (inside functions only)
name := "Alice"

// Multiple variables
var x, y int = 1, 2
a, b := 1, "hello"

// Block declaration
var (
    name   string = "Alice"
    age    int    = 30
    active bool   = true
)
```

### Constants

```go
// Typed constant
const Pi float64 = 3.14159

// Untyped constant (more flexible)
const MaxSize = 1024

// Constant block with iota
const (
    Sunday = iota  // 0
    Monday         // 1
    Tuesday        // 2
)

// Iota patterns
const (
    _  = iota             // Skip 0
    KB = 1 << (10 * iota) // 1024
    MB                    // 1048576
    GB                    // 1073741824
)
```

---

## Functions

### Basic Functions

```go
// Simple function
func greet(name string) string {
    return "Hello, " + name
}

// Multiple parameters of same type
func add(x, y int) int {
    return x + y
}

// Multiple return values
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// Named return values
func split(sum int) (x, y int) {
    x = sum * 4 / 9
    y = sum - x
    return // Naked return
}
```

### Variadic Functions

```go
// Accept any number of arguments
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}

// Usage
sum(1, 2, 3)
sum([]int{1, 2, 3}...) // Spread slice
```

### Function Values and Closures

```go
// Functions are first-class values
var fn func(int) int
fn = func(x int) int { return x * 2 }

// Closure (captures outer variable)
func counter() func() int {
    count := 0
    return func() int {
        count++
        return count
    }
}

c := counter()
c() // 1
c() // 2
```

### Defer

```go
// Deferred calls execute in LIFO order when function returns
func process(filename string) error {
    f, err := os.Open(filename)
    if err != nil {
        return err
    }
    defer f.Close() // Guaranteed to run

    // Process file...
    return nil
}

// Arguments evaluated immediately, call deferred
func demo() {
    for i := 0; i < 3; i++ {
        defer fmt.Println(i) // Prints 2, 1, 0
    }
}
```

---

## Structs

### Definition and Instantiation

```go
// Define struct type
type User struct {
    ID        int
    Name      string
    Email     string
    CreatedAt time.Time
}

// Create instances
u1 := User{ID: 1, Name: "Alice", Email: "alice@example.com"}
u2 := User{1, "Alice", "alice@example.com", time.Now()} // Positional (fragile)
u3 := User{Name: "Bob"} // Other fields get zero values

// Pointer to struct
u4 := &User{Name: "Charlie"}

// Anonymous struct (one-off use)
point := struct {
    X, Y int
}{10, 20}
```

### Methods

```go
// Value receiver (copy)
func (u User) FullName() string {
    return u.Name
}

// Pointer receiver (can modify, avoids copy)
func (u *User) UpdateEmail(email string) {
    u.Email = email
}

// Usage
user := User{Name: "Alice"}
user.UpdateEmail("new@example.com") // Automatic &user
```

### When to Use Pointer vs Value Receiver

| Use Pointer Receiver | Use Value Receiver |
|---------------------|-------------------|
| Method modifies the receiver | Method only reads |
| Struct is large | Struct is small |
| Consistency with other methods | Immutability desired |

### Embedding (Composition)

```go
type Person struct {
    Name string
    Age  int
}

func (p Person) Greet() string {
    return "Hello, " + p.Name
}

type Employee struct {
    Person              // Embedded (not named)
    EmployeeID string
    Department string
}

// Employee "inherits" Person's fields and methods
emp := Employee{
    Person:     Person{Name: "Alice", Age: 30},
    EmployeeID: "E001",
    Department: "Engineering",
}

emp.Name        // Promoted field
emp.Greet()     // Promoted method
emp.Person.Name // Explicit access
```

---

## Interfaces

### Definition and Implementation

```go
// Define interface
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

// Compose interfaces
type ReadWriter interface {
    Reader
    Writer
}

// Implement implicitly (no "implements" keyword)
type FileReader struct {
    data []byte
    pos  int
}

func (f *FileReader) Read(p []byte) (int, error) {
    n := copy(p, f.data[f.pos:])
    f.pos += n
    return n, nil
}

// FileReader now implements Reader
```

### Empty Interface

```go
// interface{} accepts any type (like any in TS)
func printAnything(v interface{}) {
    fmt.Println(v)
}

// Go 1.18+: 'any' is alias for interface{}
func printAnything(v any) {
    fmt.Println(v)
}
```

### Type Assertions

```go
// Assert specific type
var i interface{} = "hello"

s := i.(string)        // Panics if wrong type
s, ok := i.(string)    // Safe: ok is false if wrong type

if s, ok := i.(string); ok {
    fmt.Println(s)
}
```

### Type Switch

```go
func describe(i interface{}) {
    switch v := i.(type) {
    case int:
        fmt.Printf("Integer: %d\n", v)
    case string:
        fmt.Printf("String: %s\n", v)
    case bool:
        fmt.Printf("Boolean: %t\n", v)
    default:
        fmt.Printf("Unknown type: %T\n", v)
    }
}
```

### Common Interfaces

| Interface | Methods | Use |
|-----------|---------|-----|
| `io.Reader` | `Read([]byte) (int, error)` | Read data |
| `io.Writer` | `Write([]byte) (int, error)` | Write data |
| `io.Closer` | `Close() error` | Clean up resources |
| `fmt.Stringer` | `String() string` | Custom string representation |
| `error` | `Error() string` | Error type |

---

## Collections

### Arrays

```go
// Fixed size, rarely used directly
var arr [5]int              // Zero-valued
arr := [5]int{1, 2, 3, 4, 5}
arr := [...]int{1, 2, 3}    // Size inferred (3)

// Arrays are values, not references
arr2 := arr // Full copy
```

### Slices

```go
// Dynamic, reference type (view into array)
var s []int                 // nil slice
s := []int{1, 2, 3}         // Literal
s := make([]int, 5)         // Length 5, capacity 5
s := make([]int, 0, 10)     // Length 0, capacity 10

// Slice operations
len(s)                      // Length
cap(s)                      // Capacity
s[1:3]                      // Sub-slice [1, 3)
s[:3]                       // [0, 3)
s[1:]                       // [1, len)

// Append (may reallocate)
s = append(s, 4)            // Single element
s = append(s, 4, 5, 6)      // Multiple elements
s = append(s, other...)     // Another slice

// Copy
dst := make([]int, len(src))
copy(dst, src)
```

### Slice Gotchas

```go
// Slices share underlying array
original := []int{1, 2, 3, 4, 5}
slice := original[1:3] // [2, 3]
slice[0] = 99          // Modifies original!

// Safe copy
safeCopy := make([]int, len(original[1:3]))
copy(safeCopy, original[1:3])
```

### Maps

```go
// Create maps
var m map[string]int        // nil map (read ok, write panics)
m := map[string]int{}       // Empty map
m := make(map[string]int)   // Empty map
m := map[string]int{        // With values
    "alice": 30,
    "bob":   25,
}

// Operations
m["key"] = 42               // Set
val := m["key"]             // Get (zero value if missing)
val, ok := m["key"]         // Check existence
delete(m, "key")            // Delete
len(m)                      // Size

// Iterate (order is random!)
for key, value := range m {
    fmt.Println(key, value)
}
```

### Iteration

```go
// Range over slice
for i, v := range slice {
    fmt.Println(i, v)
}

// Index only
for i := range slice {
    fmt.Println(i)
}

// Value only
for _, v := range slice {
    fmt.Println(v)
}

// Range over map
for k, v := range m {
    fmt.Println(k, v)
}

// Range over string (runes)
for i, r := range "hello" {
    fmt.Printf("%d: %c\n", i, r)
}

// Range over channel
for msg := range ch {
    fmt.Println(msg)
}
```

---

## Error Handling

### The error Interface

```go
// error is a built-in interface
type error interface {
    Error() string
}

// Create errors
err := errors.New("something went wrong")
err := fmt.Errorf("failed to process %s: %w", name, originalErr)
```

### Error Handling Pattern

```go
// Check errors immediately
result, err := doSomething()
if err != nil {
    return err // Or handle appropriately
}
// Use result...

// Multiple operations
f, err := os.Open(filename)
if err != nil {
    return fmt.Errorf("open file: %w", err)
}
defer f.Close()

data, err := io.ReadAll(f)
if err != nil {
    return fmt.Errorf("read file: %w", err)
}
```

### Custom Errors

```go
// Simple custom error
type ValidationError struct {
    Field   string
    Message string
}

func (e ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Message)
}

// Usage
return ValidationError{Field: "email", Message: "invalid format"}
```

### Error Wrapping (Go 1.13+)

```go
// Wrap error with context
if err != nil {
    return fmt.Errorf("failed to connect: %w", err)
}

// Check error type
if errors.Is(err, os.ErrNotExist) {
    // Handle file not found
}

// Extract wrapped error
var pathErr *os.PathError
if errors.As(err, &pathErr) {
    fmt.Println("Path:", pathErr.Path)
}
```

### Panic and Recover

```go
// Panic for unrecoverable errors (avoid in library code)
func mustParse(s string) int {
    n, err := strconv.Atoi(s)
    if err != nil {
        panic(err)
    }
    return n
}

// Recover from panic
func safeCall(fn func()) (err error) {
    defer func() {
        if r := recover(); r != nil {
            err = fmt.Errorf("panic: %v", r)
        }
    }()
    fn()
    return nil
}
```

---

## Concurrency Basics

### Goroutines

```go
// Start goroutine
go doWork()

// Anonymous goroutine
go func() {
    fmt.Println("In goroutine")
}()

// With arguments (captured by value)
for i := 0; i < 5; i++ {
    go func(n int) {
        fmt.Println(n)
    }(i)
}
```

### Channels

```go
// Create channel
ch := make(chan int)        // Unbuffered
ch := make(chan int, 10)    // Buffered (capacity 10)

// Send and receive
ch <- 42        // Send (blocks if full/unbuffered)
val := <-ch     // Receive (blocks if empty)

// Close channel
close(ch)

// Check if closed
val, ok := <-ch
if !ok {
    fmt.Println("Channel closed")
}

// Range over channel (until closed)
for val := range ch {
    fmt.Println(val)
}
```

### Channel Directions

```go
// Send-only channel
func producer(ch chan<- int) {
    ch <- 42
}

// Receive-only channel
func consumer(ch <-chan int) {
    val := <-ch
}
```

### Select

```go
// Wait on multiple channels
select {
case msg := <-ch1:
    fmt.Println("From ch1:", msg)
case msg := <-ch2:
    fmt.Println("From ch2:", msg)
case ch3 <- 42:
    fmt.Println("Sent to ch3")
default:
    fmt.Println("No communication ready")
}

// Timeout pattern
select {
case result := <-ch:
    fmt.Println(result)
case <-time.After(time.Second):
    fmt.Println("Timeout")
}
```

### WaitGroup

```go
import "sync"

var wg sync.WaitGroup

for i := 0; i < 5; i++ {
    wg.Add(1)
    go func(n int) {
        defer wg.Done()
        fmt.Println(n)
    }(i)
}

wg.Wait() // Block until all done
```

### Mutex

```go
import "sync"

type SafeCounter struct {
    mu    sync.Mutex
    count int
}

func (c *SafeCounter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}

func (c *SafeCounter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.count
}

// RWMutex for read-heavy workloads
type Cache struct {
    mu   sync.RWMutex
    data map[string]string
}

func (c *Cache) Get(key string) string {
    c.mu.RLock()
    defer c.mu.RUnlock()
    return c.data[key]
}
```

---

## Common Patterns

### Options Pattern (Functional Options)

```go
type Server struct {
    host    string
    port    int
    timeout time.Duration
}

type Option func(*Server)

func WithPort(port int) Option {
    return func(s *Server) {
        s.port = port
    }
}

func WithTimeout(d time.Duration) Option {
    return func(s *Server) {
        s.timeout = d
    }
}

func NewServer(host string, opts ...Option) *Server {
    s := &Server{
        host:    host,
        port:    8080,           // Default
        timeout: time.Minute,    // Default
    }
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// Usage
server := NewServer("localhost",
    WithPort(9000),
    WithTimeout(30*time.Second),
)
```

### Constructor Pattern

```go
type User struct {
    id   int
    name string
}

// Constructor function (New prefix convention)
func NewUser(id int, name string) *User {
    return &User{
        id:   id,
        name: name,
    }
}

// MustX for constructors that can fail
func MustCompile(pattern string) *regexp.Regexp {
    re, err := regexp.Compile(pattern)
    if err != nil {
        panic(err)
    }
    return re
}
```

### Table-Driven Tests

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 1, 2, 3},
        {"negative", -1, -2, -3},
        {"zero", 0, 0, 0},
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
```

### Context for Cancellation

```go
import "context"

func doWork(ctx context.Context) error {
    select {
    case <-time.After(time.Hour):
        return nil
    case <-ctx.Done():
        return ctx.Err()
    }
}

// Usage with timeout
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

if err := doWork(ctx); err != nil {
    log.Println("Work cancelled:", err)
}

// Usage with cancellation
ctx, cancel := context.WithCancel(context.Background())
go func() {
    time.Sleep(time.Second)
    cancel() // Signal cancellation
}()
```

---

## Go Conventions

### Naming

| Type | Convention | Example |
|------|------------|---------|
| Exported (public) | PascalCase | `UserService` |
| Unexported (private) | camelCase | `userCache` |
| Acronyms | All caps | `HTTPClient`, `xmlParser` |
| Interfaces | -er suffix | `Reader`, `Stringer` |
| Getters | No Get prefix | `Name()` not `GetName()` |
| Package names | lowercase, single word | `http`, `strconv` |

### Code Organization

```go
// Standard file structure
package main

import (
    "fmt"           // Standard library
    "net/http"

    "github.com/pkg/errors"  // Third-party

    "myproject/internal/user"  // Internal packages
)

// Constants
const MaxRetries = 3

// Package-level variables (minimize these)
var defaultClient = &http.Client{}

// Types
type Server struct { ... }

// Functions
func NewServer() *Server { ... }

// Methods
func (s *Server) Start() error { ... }
```

### Error Strings

```go
// Lowercase, no punctuation
errors.New("connection refused")  // Good
errors.New("Connection refused.") // Bad

// With context
fmt.Errorf("open %s: %w", filename, err)
```

---

## Troubleshooting

### "declared and not used"

```go
// Go requires all variables to be used
x := 5  // Error if x is never used

// Use blank identifier to ignore
x, _ := someFuncReturningTwo()
```

### "cannot use X as type Y"

```go
// Types must match exactly
var x int64 = 5
var y int = x    // Error: int64 != int

// Explicit conversion required
var y int = int(x)
```

### "nil pointer dereference"

```go
// Check for nil before dereferencing
var u *User
fmt.Println(u.Name)  // Panic!

if u != nil {
    fmt.Println(u.Name)
}
```

### "all goroutines are asleep - deadlock!"

```go
// Common cause: unbuffered channel with no receiver
ch := make(chan int)
ch <- 1  // Blocks forever, no receiver

// Fix: use buffered channel or ensure receiver exists
ch := make(chan int, 1)
ch <- 1  // OK
```

### "race condition detected"

```go
// Run with race detector
// go run -race main.go

// Fix: use sync primitives
var mu sync.Mutex
mu.Lock()
shared++
mu.Unlock()
```

---

## References

- [Go Documentation](https://go.dev/doc/)
- [Effective Go](https://go.dev/doc/effective_go)
- [Go by Example](https://gobyexample.com/)
- Specialized skills: `go-concurrency-patterns` (external)
