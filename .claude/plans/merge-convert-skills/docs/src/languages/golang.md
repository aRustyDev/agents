# Go

> Statically typed, compiled language designed for simplicity, concurrency, and fast compilation.

## Overview

Go (Golang) is a statically typed, compiled programming language designed at Google by Robert Griesemer, Rob Pike, and Ken Thompson, released in 2009. It was created to address criticisms of existing languages while maintaining their positive characteristics, particularly focusing on simplicity, fast compilation, and built-in concurrency.

Go emphasizes readability and simplicity over expressiveness. It has a minimal feature set by design: no classes (composition via structs), no inheritance (interfaces for polymorphism), no exceptions (explicit error returns), and no generics until Go 1.18 (2022).

The language excels in cloud infrastructure, DevOps tooling, network services, and concurrent applications. Major projects like Docker, Kubernetes, and Terraform are written in Go.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | Systems | Compiled, efficient, GC-based |
| Secondary Family | — | Minimal paradigm mixing |
| Subtype | concurrent | Goroutines, channels |

See: [Systems Family](../language-families/systems.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| 1.0 | 2012-03 | Initial stable release |
| 1.11 | 2018-08 | Modules (go mod) |
| 1.13 | 2019-09 | Error wrapping |
| 1.16 | 2021-02 | Embed directive, io/fs |
| 1.18 | 2022-03 | Generics (type parameters) |
| 1.21 | 2023-08 | Built-in slog, min/max/clear |
| 1.22 | 2024-02 | For-range over integers |

## Feature Profile

### Type System

- **Strength:** strong (static, no implicit conversions)
- **Inference:** limited (`:=` declaration, function-local)
- **Generics:** bounded (type parameters with constraints, since 1.18)
- **Nullability:** nullable (nil for pointers, slices, maps, channels)

### Memory Model

- **Management:** gc (concurrent, low-latency)
- **Mutability:** default-mutable (no const for variables)
- **Allocation:** automatic (escape analysis, stack/heap)
- **Pointers:** restricted (no pointer arithmetic)

### Control Flow

- **Structured:** if-else, for, switch, select
- **Effects:** explicit errors (multiple return values)
- **Async:** goroutines + channels (CSP model)

### Data Types

- **Primitives:** bool, int types (int8-int64, uint8-uint64), float32, float64, complex64, complex128, string, rune
- **Composites:** structs, arrays, slices, maps
- **Collections:** slice, map (built-in)
- **Abstraction:** interfaces, packages

### Metaprogramming

- **Macros:** none
- **Reflection:** runtime (reflect package)
- **Code generation:** go generate

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | go mod (built-in) | Module system |
| Build System | go build (built-in) | Fast compilation |
| LSP | gopls | Official, excellent |
| Formatter | gofmt | Standard, opinionated |
| Linter | golangci-lint | Meta-linter |
| REPL | gore | Third-party |
| Test Framework | testing (built-in) | go test |

## Syntax Patterns

```go
// Function definition
func greet(name string, times int) string {
    result := ""
    for i := 0; i < times; i++ {
        result += fmt.Sprintf("Hello, %s! ", name)
    }
    return result
}

// Generic function (Go 1.18+)
func identity[T any](value T) T {
    return value
}

func max[T constraints.Ordered](a, b T) T {
    if a > b {
        return a
    }
    return b
}

// Goroutine and channel (async pattern)
func fetchData(url string) <-chan Result {
    ch := make(chan Result, 1)
    go func() {
        resp, err := http.Get(url)
        if err != nil {
            ch <- Result{Err: err}
            return
        }
        ch <- Result{Value: resp}
    }()
    return ch
}

// Struct definition
type User struct {
    ID    string
    Name  string
    Email *string // nil if not set
}

// Constructor pattern
func NewUser(id, name string) *User {
    return &User{ID: id, Name: name}
}

// Method definition
func (u *User) SetEmail(email string) {
    u.Email = &email
}

// Interface definition
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

// Interface composition
type ReadWriter interface {
    Reader
    Writer
}

// Sum type simulation with interface
type Shape interface {
    Area() float64
}

type Circle struct {
    Radius float64
}

func (c Circle) Area() float64 {
    return math.Pi * c.Radius * c.Radius
}

type Rectangle struct {
    Width, Height float64
}

func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

// Error handling
func divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// Error wrapping (Go 1.13+)
func processFile(path string) error {
    data, err := os.ReadFile(path)
    if err != nil {
        return fmt.Errorf("reading %s: %w", path, err)
    }
    // process data...
    return nil
}

// Deferred cleanup
func readFile(path string) ([]byte, error) {
    f, err := os.Open(path)
    if err != nil {
        return nil, err
    }
    defer f.Close()

    return io.ReadAll(f)
}

// Select for channel operations
func process(ctx context.Context, input <-chan int) {
    for {
        select {
        case <-ctx.Done():
            return
        case v := <-input:
            fmt.Println(v)
        }
    }
}

// Type switch
func describe(i interface{}) string {
    switch v := i.(type) {
    case int:
        return fmt.Sprintf("integer: %d", v)
    case string:
        return fmt.Sprintf("string: %s", v)
    default:
        return "unknown"
    }
}

// Slice operations
numbers := []int{1, 2, 3, 4, 5}
doubled := make([]int, len(numbers))
for i, n := range numbers {
    doubled[i] = n * 2
}

// Map operations
users := make(map[string]*User)
users["1"] = NewUser("1", "Alice")
if user, ok := users["1"]; ok {
    fmt.Println(user.Name)
}
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| No sum types/enums | moderate | Interfaces, const iota, sealed interfaces |
| Nil interface vs nil pointer | moderate | Careful nil checks, typed nils |
| No immutability | minor | Convention, unexported fields |
| Verbose error handling | moderate | Error wrapping, custom error types |
| No generics before 1.18 | (resolved) | Upgrade to 1.18+ |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 1 | golang-rust |
| As Target | 2 | python-golang, typescript-golang |

**Note:** Go's simplicity makes it a good target for straightforward conversions. CSP concurrency requires special handling.

## Idiomatic Patterns

### Interfaces → Traits/Protocols

```go
// Go: interface (structural)
type Stringer interface {
    String() string
}

// IR equivalent: trait
// trait Stringer { fn to_string(&self) -> String }
```

### Error Values → Result Types

```go
// Go: error return
func read() ([]byte, error) {
    // ...
}

// IR equivalent: Result type
// fn read() -> Result<Vec<u8>, Error>
```

### Goroutines → Async/Actors

```go
// Go: goroutine with channel
go func() { ch <- result }()
val := <-ch

// IR equivalent: async task or actor
// spawn(async { result })
// val = await handle
```

### defer → RAII/Finally

```go
// Go: defer
f, _ := os.Open(path)
defer f.Close()

// IR equivalent: RAII or try-finally
// let f = File::open(path)?;  // Dropped automatically
// OR
// try { ... } finally { f.close() }
```

## Related Languages

- **Influenced by:** C, Oberon, Limbo, Newsqueak, CSP
- **Influenced:** Rust (some), Crystal, V
- **Compiles to:** Native machine code
- **FFI compatible:** C (cgo)

## Sources

- [Go Language Specification](https://go.dev/ref/spec)
- [Effective Go](https://go.dev/doc/effective_go)
- [Go Documentation](https://go.dev/doc/)
- [Go by Example](https://gobyexample.com/)

## See Also

- [Systems Family](../language-families/systems.md)
- [Rust](rust.md) - No-GC alternative
- [C](c.md) - FFI target
- [Java](java.md) - GC comparison
