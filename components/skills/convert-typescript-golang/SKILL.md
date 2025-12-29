---
name: convert-typescript-golang
description: Convert TypeScript code to idiomatic Go. Use when migrating TypeScript projects to Go, translating TypeScript patterns to idiomatic Go, or refactoring TypeScript codebases into Go. Extends meta-convert-dev with TypeScript-to-Go specific patterns.
---

# Convert TypeScript to Go

Convert TypeScript code to idiomatic Go. This skill extends `meta-convert-dev` with TypeScript-to-Go specific type mappings, idiom translations, and tooling.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: TypeScript types → Go types
- **Idiom translations**: TypeScript patterns → idiomatic Go
- **Error handling**: Exceptions → error return values
- **Async patterns**: Promise/async → goroutines/channels
- **Interface patterns**: Structural typing → Go interfaces

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- TypeScript language fundamentals - see `lang-typescript-dev`
- Go language fundamentals - see `lang-golang-dev`
- Reverse conversion (Go → TypeScript) - see `convert-golang-typescript`

---

## Quick Reference

| TypeScript | Go | Notes |
|------------|-----|-------|
| `string` | `string` | Direct mapping |
| `number` | `int`, `int64`, `float64` | Specify precision |
| `boolean` | `bool` | Direct mapping |
| `null \| undefined` | `nil` or zero value | Go has nil for pointers/interfaces/slices/maps/channels |
| `T[]` | `[]T` | Slice (dynamic array) |
| `Array<T>` | `[]T` | Slice |
| `[T, U]` | `struct { First T; Second U }` | Named fields preferred over tuples |
| `Record<K, V>` | `map[K]V` | Map type |
| `Map<K, V>` | `map[K]V` | Map type |
| `Set<T>` | `map[T]struct{}` or `map[T]bool` | Set via map with empty struct |
| `T \| U` | `interface{}` or custom type | Use type switch or discriminated union pattern |
| `Promise<T>` | `chan T` or function with error return | Goroutines for async execution |
| `interface X` | `type X interface` | Behavior contracts |
| `class X` | `type X struct` + methods | Methods with receiver syntax |
| `enum` | `const` block with `iota` | Or string constants |
| `any` | `interface{}` or `any` (Go 1.18+) | Avoid when possible |
| `void` | No return value | Function signature omits return |
| `never` | No direct equivalent | Use panic or infinite loop |

## When Converting Code

1. **Analyze source thoroughly** before writing target
2. **Map types first** - create type equivalence table
3. **Preserve semantics** over syntax similarity
4. **Adopt target idioms** - don't write "TypeScript code in Go syntax"
5. **Handle edge cases** - null/nil/undefined, error paths, resource cleanup
6. **Test equivalence** - same inputs → same outputs

---

## Type System Mapping

### Primitive Types

| TypeScript | Go | Notes |
|------------|-----|-------|
| `string` | `string` | UTF-8 encoded in Go |
| `number` | `int` | Default for integers without decimal |
| `number` | `int8`, `int16`, `int32`, `int64` | Sized integers |
| `number` | `uint`, `uint8`, `uint16`, `uint32`, `uint64` | Unsigned integers |
| `number` | `float32`, `float64` | Floating point |
| `bigint` | `*big.Int` | From `math/big` package |
| `boolean` | `bool` | Direct mapping |
| `null` | `nil` | For pointers, interfaces, slices, maps, channels, functions |
| `undefined` | Zero value | Each type has a zero value (0, "", false, nil) |
| `symbol` | No direct equivalent | Use string or int constants |
| `any` | `interface{}` or `any` | `any` alias added in Go 1.18 |
| `unknown` | `interface{}` with type assertion | Requires type checking |
| `void` | (no return) | Function returns nothing |
| `never` | No direct equivalent | Functions that never return use panic |

### Collection Types

| TypeScript | Go | Notes |
|------------|-----|-------|
| `T[]` | `[]T` | Slice (resizable, passed by reference) |
| `Array<T>` | `[]T` | Same as T[] |
| `readonly T[]` | `[]T` | Go doesn't enforce readonly at compile time |
| `[number, number, number]` | `[3]T` | Fixed-size array |
| `[T, U]` | `struct { A T; B U }` | Named struct preferred |
| `[T, U, V]` | `struct { A T; B U; C V }` | Named struct preferred |
| `Map<K, V>` | `map[K]V` | Hash map |
| `Record<K, V>` | `map[K]V` | Hash map |
| `Set<T>` | `map[T]struct{}` | Empty struct uses zero memory |
| `Set<T>` | `map[T]bool` | Alternative using bool (1 byte per entry) |
| `WeakMap` | No direct equivalent | Use map with manual cleanup |
| `WeakSet` | No direct equivalent | Use map with manual cleanup |

### Composite Types

| TypeScript | Go | Notes |
|------------|-----|-------|
| `interface X { ... }` (data) | `type X struct { ... }` | Data structures |
| `interface X { method(): T }` | `type X interface { Method() T }` | Behavior contracts |
| `class X` | `type X struct` + methods | Struct with receiver methods |
| `type X = Y` | `type X = Y` | Type alias (Go 1.9+) |
| `type X = Y \| Z` | Custom type with methods | Discriminated union pattern |
| `T \| null` | `*T` | Pointer can be nil |
| `T \| undefined` | `*T` or zero value check | Pointer or explicit check |
| `Partial<T>` | Struct with pointer fields | Each field can be nil |
| `Required<T>` | Struct with value fields | All fields have values |
| `Pick<T, K>` | New struct type | Select fields manually |
| `Omit<T, K>` | New struct type | Exclude fields manually |
| `enum X` | `const` block with `iota` | Or typed constants |
| `namespace X` | `package X` | Package organization |

### Generic Type Mappings

| TypeScript | Go | Notes |
|------------|-----|-------|
| `<T>` | `[T any]` | Generic type parameter (Go 1.18+) |
| `<T extends U>` | `[T U]` | Type constraint using interface |
| `<T extends keyof U>` | No direct equivalent | Use reflection or code generation |
| `Array<T>` | `[]T` | Built-in generic slice |
| `Promise<T>` | `chan T` or function return | Channels for async communication |
| `Readonly<T>` | No language support | Convention and documentation |
| `Record<K, V>` | `map[K]V` | Built-in generic map |

---

## Idiom Translation

### Pattern: Null/Undefined Handling

**TypeScript:**
```typescript
const name = user?.name ?? "Anonymous";
const age = user?.age || 18;
```

**Go:**
```go
var name string
if user != nil && user.Name != "" {
    name = user.Name
} else {
    name = "Anonymous"
}

age := 18
if user != nil && user.Age > 0 {
    age = user.Age
}
```

**Why this translation:**
- Go doesn't have optional chaining or null coalescing operators
- Explicit nil checks are idiomatic and clear
- Zero values (0, "", false) should be considered in logic
- Pointers are used when nil is a meaningful state

### Pattern: Array/Slice Operations

**TypeScript:**
```typescript
const activeValues = items
  .filter(x => x.active)
  .map(x => x.value)
  .reduce((sum, val) => sum + val, 0);
```

**Go:**
```go
var activeValues int
for _, item := range items {
    if item.Active {
        activeValues += item.Value
    }
}
```

**Why this translation:**
- Go prefers explicit for loops over chaining methods
- More readable and maintainable for Go developers
- Better performance (single pass, no intermediate allocations)
- Can use generics (Go 1.18+) for reusable map/filter if needed

### Pattern: Object Destructuring

**TypeScript:**
```typescript
const { name, age, ...rest } = user;
const [first, second, ...others] = items;
```

**Go:**
```go
name := user.Name
age := user.Age
// rest requires manual field copying or reflection

first := items[0]
second := items[1]
others := items[2:]
```

**Why this translation:**
- Go doesn't support destructuring
- Direct field access is clear and explicit
- Slice operations provide array destructuring
- Manual copying ensures clarity about what's being used

### Pattern: Classes and Methods

**TypeScript:**
```typescript
class Calculator {
  private total: number = 0;

  add(value: number): void {
    this.total += value;
  }

  getTotal(): number {
    return this.total;
  }
}
```

**Go:**
```go
type Calculator struct {
    total int // unexported (lowercase) is private
}

func NewCalculator() *Calculator {
    return &Calculator{total: 0}
}

func (c *Calculator) Add(value int) {
    c.total += value
}

func (c *Calculator) GetTotal() int {
    return c.total
}
```

**Why this translation:**
- Go uses struct types instead of classes
- Methods have receiver syntax (c *Calculator)
- Constructor pattern uses New* functions
- Exported/unexported controlled by capitalization
- Pointer receivers allow mutation

### Pattern: Interfaces and Duck Typing

**TypeScript:**
```typescript
interface Drawable {
  draw(): void;
}

function render(item: Drawable): void {
  item.draw();
}

// Any object with draw() method satisfies interface
const circle = { draw: () => console.log("circle") };
render(circle);
```

**Go:**
```go
type Drawable interface {
    Draw()
}

func Render(item Drawable) {
    item.Draw()
}

// Explicit type must implement interface
type Circle struct{}

func (c Circle) Draw() {
    fmt.Println("circle")
}

// Usage
circle := Circle{}
Render(circle)
```

**Why this translation:**
- Both languages support structural typing for interfaces
- Go requires explicit types, not object literals
- Interface satisfaction is implicit (no implements keyword)
- Method names must match exactly (case-sensitive)

### Pattern: Default Parameters

**TypeScript:**
```typescript
function greet(name: string = "Guest", greeting: string = "Hello"): string {
  return `${greeting}, ${name}!`;
}
```

**Go:**
```go
func Greet(name, greeting string) string {
    if name == "" {
        name = "Guest"
    }
    if greeting == "" {
        greeting = "Hello"
    }
    return fmt.Sprintf("%s, %s!", greeting, name)
}

// Or use options pattern for complex cases
type GreetOptions struct {
    Name     string
    Greeting string
}

func GreetWithOptions(opts GreetOptions) string {
    if opts.Name == "" {
        opts.Name = "Guest"
    }
    if opts.Greeting == "" {
        opts.Greeting = "Hello"
    }
    return fmt.Sprintf("%s, %s!", opts.Greeting, opts.Name)
}
```

**Why this translation:**
- Go doesn't support default parameters
- Check zero values and provide defaults explicitly
- Options pattern for complex parameter sets
- Functional options pattern for even more flexibility

### Pattern: Spread Operator

**TypeScript:**
```typescript
const arr1 = [1, 2, 3];
const arr2 = [...arr1, 4, 5];

const obj1 = { a: 1, b: 2 };
const obj2 = { ...obj1, c: 3 };
```

**Go:**
```go
arr1 := []int{1, 2, 3}
arr2 := append(append([]int{}, arr1...), 4, 5)
// Or clearer:
arr2 := make([]int, len(arr1), len(arr1)+2)
copy(arr2, arr1)
arr2 = append(arr2, 4, 5)

// No built-in object spread; must copy manually
obj2 := struct{ A, B, C int }{
    A: obj1.A,
    B: obj1.B,
    C: 3,
}
```

**Why this translation:**
- Go uses append with ... for variadic slice expansion
- Pre-allocating capacity avoids reallocation
- No object spread; manual field copying required
- Reflection can help for generic copying but adds complexity

### Pattern: Optional Properties

**TypeScript:**
```typescript
interface User {
  name: string;
  email?: string;
  age?: number;
}
```

**Go:**
```go
type User struct {
    Name  string
    Email *string // pointer indicates optional
    Age   *int    // nil means not provided
}

// Helper to create pointer
func StringPtr(s string) *string { return &s }
func IntPtr(i int) *int { return &i }

// Usage
user := User{
    Name:  "Alice",
    Email: StringPtr("alice@example.com"),
}
```

**Why this translation:**
- Pointers distinguish between "not provided" (nil) and "zero value"
- Helper functions make pointer creation cleaner
- Alternative: use zero values and a separate "set" map
- Consider whether nil vs zero value distinction is needed

### Pattern: Union Types

**TypeScript:**
```typescript
type Result = { success: true; data: string } | { success: false; error: string };

function process(): Result {
  if (Math.random() > 0.5) {
    return { success: true, data: "OK" };
  }
  return { success: false, error: "Failed" };
}
```

**Go:**
```go
type Result struct {
    Success bool
    Data    string // only valid if Success == true
    Error   string // only valid if Success == false
}

func Process() Result {
    if rand.Float64() > 0.5 {
        return Result{Success: true, Data: "OK"}
    }
    return Result{Success: false, Error: "Failed"}
}

// Or use interface with type assertion
type ResultSuccess struct{ Data string }
type ResultError struct{ Error string }

func Process() interface{} {
    if rand.Float64() > 0.5 {
        return ResultSuccess{Data: "OK"}
    }
    return ResultError{Error: "Failed"}
}
```

**Why this translation:**
- Go doesn't have union types
- Use struct with discriminator field (Success bool)
- Interface{} with type assertion for true sum types
- Consider if error return pattern is more idiomatic

### Pattern: String Interpolation

**TypeScript:**
```typescript
const name = "Alice";
const age = 30;
const message = `Hello, ${name}! You are ${age} years old.`;
```

**Go:**
```go
name := "Alice"
age := 30
message := fmt.Sprintf("Hello, %s! You are %d years old.", name, age)
```

**Why this translation:**
- Go uses fmt.Sprintf for string formatting
- Printf-style format verbs (%s, %d, %v, etc.)
- Type-safe at runtime, not compile-time
- Alternative: strings.Builder for complex concatenation

---

## Error Handling

### TypeScript Exception Model → Go Error Return Model

**TypeScript:**
```typescript
function parseConfig(path: string): Config {
  if (!fs.existsSync(path)) {
    throw new Error(`Config file not found: ${path}`);
  }

  const content = fs.readFileSync(path, 'utf-8');

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
} catch (err) {
  console.error("Error:", err.message);
}
```

**Go:**
```go
func ParseConfig(path string) (*Config, error) {
    if _, err := os.Stat(path); os.IsNotExist(err) {
        return nil, fmt.Errorf("config file not found: %s", path)
    }

    content, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("failed to read config: %w", err)
    }

    var config Config
    if err := json.Unmarshal(content, &config); err != nil {
        return nil, fmt.Errorf("failed to parse config: %w", err)
    }

    return &config, nil
}

// Usage
config, err := ParseConfig("config.json")
if err != nil {
    log.Printf("Error: %v", err)
    return
}
fmt.Println(config)
```

**Why this translation:**
- Go returns errors as values, not exceptions
- Multiple return values: (result, error)
- fmt.Errorf with %w wraps errors (Go 1.13+)
- errors.Is and errors.As for error checking
- Caller checks err != nil after each call

### Custom Error Types

**TypeScript:**
```typescript
class ValidationError extends Error {
  constructor(public field: string, message: string) {
    super(message);
    this.name = "ValidationError";
  }
}

class NotFoundError extends Error {
  constructor(public resource: string) {
    super(`${resource} not found`);
    this.name = "NotFoundError";
  }
}

function validateUser(user: User): void {
  if (!user.email) {
    throw new ValidationError("email", "Email is required");
  }
}
```

**Go:**
```go
// Custom error types implement error interface
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation error on field %s: %s", e.Field, e.Message)
}

type NotFoundError struct {
    Resource string
}

func (e *NotFoundError) Error() string {
    return fmt.Sprintf("%s not found", e.Resource)
}

func ValidateUser(user *User) error {
    if user.Email == "" {
        return &ValidationError{Field: "email", Message: "Email is required"}
    }
    return nil
}

// Usage with type assertion
err := ValidateUser(user)
if err != nil {
    var validationErr *ValidationError
    if errors.As(err, &validationErr) {
        log.Printf("Validation failed on field: %s", validationErr.Field)
    }
}
```

**Why this translation:**
- Go uses error interface (Error() string method)
- Custom error types are structs with Error() method
- errors.As for type-safe error checking
- errors.Is for sentinel error comparison
- Wrap errors with fmt.Errorf("%w", err) to preserve chain

### Panic vs Error Returns

**TypeScript:**
```typescript
// Exceptions for everything
function divide(a: number, b: number): number {
  if (b === 0) {
    throw new Error("division by zero");
  }
  return a / b;
}
```

**Go:**
```go
// Error returns for expected errors
func Divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// Panic only for programmer errors (bugs)
func DivideMustNotBeZero(a, b float64) float64 {
    if b == 0 {
        panic("division by zero - caller error")
    }
    return a / b
}
```

**Why this translation:**
- Go distinguishes expected errors (return) from bugs (panic)
- Use error returns for conditions caller should handle
- Use panic for programmer errors / assertions
- recover() can catch panics (similar to catch) but rarely used
- Idiomatic Go: errors are values, not exceptions

---

## Concurrency Patterns

### Promise → Goroutines with Channels

**TypeScript:**
```typescript
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/users/${id}`);
  return response.json();
}

// Usage
const user = await fetchUser("123");
console.log(user);
```

**Go:**
```go
func FetchUser(id string) (*User, error) {
    resp, err := http.Get(fmt.Sprintf("/users/%s", id))
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    var user User
    if err := json.NewDecoder(resp.Body).Decode(&user); err != nil {
        return nil, err
    }

    return &user, nil
}

// Usage (synchronous)
user, err := FetchUser("123")
if err != nil {
    log.Fatal(err)
}
fmt.Println(user)

// Or asynchronous with goroutine
func FetchUserAsync(id string) <-chan *User {
    ch := make(chan *User, 1)
    go func() {
        user, err := FetchUser(id)
        if err != nil {
            log.Printf("Error: %v", err)
            close(ch)
            return
        }
        ch <- user
    }()
    return ch
}

// Usage
userChan := FetchUserAsync("123")
user := <-userChan // Wait for result
```

**Why this translation:**
- Go uses goroutines (lightweight threads) for concurrency
- Channels communicate between goroutines
- Synchronous by default; explicit goroutines for async
- defer ensures cleanup (like finally)
- Error handling remains explicit

### Promise.all → WaitGroup or Channels

**TypeScript:**
```typescript
const [users, posts, comments] = await Promise.all([
  fetchUsers(),
  fetchPosts(),
  fetchComments()
]);
```

**Go:**
```go
// Using WaitGroup
var wg sync.WaitGroup
var users []User
var posts []Post
var comments []Comment
var mu sync.Mutex // Protect shared state if needed
var errs []error

wg.Add(3)

go func() {
    defer wg.Done()
    u, err := FetchUsers()
    if err != nil {
        mu.Lock()
        errs = append(errs, err)
        mu.Unlock()
        return
    }
    mu.Lock()
    users = u
    mu.Unlock()
}()

go func() {
    defer wg.Done()
    p, err := FetchPosts()
    if err != nil {
        mu.Lock()
        errs = append(errs, err)
        mu.Unlock()
        return
    }
    mu.Lock()
    posts = p
    mu.Unlock()
}()

go func() {
    defer wg.Done()
    c, err := FetchComments()
    if err != nil {
        mu.Lock()
        errs = append(errs, err)
        mu.Unlock()
        return
    }
    mu.Lock()
    comments = c
    mu.Unlock()
}()

wg.Wait()

if len(errs) > 0 {
    // Handle errors
}

// Or using channels (cleaner)
type Result struct {
    Users    []User
    Posts    []Post
    Comments []Comment
}

func FetchAll() (*Result, error) {
    usersCh := make(chan []User, 1)
    postsCh := make(chan []Post, 1)
    commentsCh := make(chan []Comment, 1)
    errCh := make(chan error, 3)

    go func() {
        users, err := FetchUsers()
        if err != nil {
            errCh <- err
            return
        }
        usersCh <- users
    }()

    go func() {
        posts, err := FetchPosts()
        if err != nil {
            errCh <- err
            return
        }
        postsCh <- posts
    }()

    go func() {
        comments, err := FetchComments()
        if err != nil {
            errCh <- err
            return
        }
        commentsCh <- comments
    }()

    result := &Result{}
    for i := 0; i < 3; i++ {
        select {
        case users := <-usersCh:
            result.Users = users
        case posts := <-postsCh:
            result.Posts = posts
        case comments := <-commentsCh:
            result.Comments = comments
        case err := <-errCh:
            return nil, err
        }
    }

    return result, nil
}
```

**Why this translation:**
- sync.WaitGroup waits for multiple goroutines
- Channels communicate results between goroutines
- select statement waits on multiple channels
- Explicit error handling for each operation
- Consider errgroup package for cleaner error handling

### Async/Await → Goroutines

**TypeScript:**
```typescript
async function processItems(items: string[]): Promise<string[]> {
  const results: string[] = [];

  for (const item of items) {
    const result = await processItem(item);
    results.push(result);
  }

  return results;
}
```

**Go:**
```go
// Sequential (like await)
func ProcessItems(items []string) ([]string, error) {
    results := make([]string, 0, len(items))

    for _, item := range items {
        result, err := ProcessItem(item)
        if err != nil {
            return nil, err
        }
        results = append(results, result)
    }

    return results, nil
}

// Concurrent (parallel processing)
func ProcessItemsConcurrent(items []string) ([]string, error) {
    results := make([]string, len(items))
    errCh := make(chan error, len(items))
    var wg sync.WaitGroup

    for i, item := range items {
        wg.Add(1)
        go func(index int, item string) {
            defer wg.Done()
            result, err := ProcessItem(item)
            if err != nil {
                errCh <- err
                return
            }
            results[index] = result
        }(i, item)
    }

    wg.Wait()
    close(errCh)

    if len(errCh) > 0 {
        return nil, <-errCh
    }

    return results, nil
}
```

**Why this translation:**
- Go doesn't have async/await keywords
- Sequential code is default (like synchronous)
- Use goroutines explicitly for concurrency
- Channels or WaitGroup coordinate goroutines
- More control over concurrency patterns

### Event Emitters → Channels

**TypeScript:**
```typescript
import { EventEmitter } from 'events';

const emitter = new EventEmitter();

emitter.on('data', (value: number) => {
  console.log('Received:', value);
});

emitter.emit('data', 42);
```

**Go:**
```go
// Channel-based pub/sub
type EventBus struct {
    subscribers []chan int
    mu          sync.RWMutex
}

func NewEventBus() *EventBus {
    return &EventBus{
        subscribers: make([]chan int, 0),
    }
}

func (eb *EventBus) Subscribe() <-chan int {
    eb.mu.Lock()
    defer eb.mu.Unlock()

    ch := make(chan int, 10) // buffered
    eb.subscribers = append(eb.subscribers, ch)
    return ch
}

func (eb *EventBus) Publish(value int) {
    eb.mu.RLock()
    defer eb.mu.RUnlock()

    for _, ch := range eb.subscribers {
        ch <- value
    }
}

// Usage
bus := NewEventBus()
dataCh := bus.Subscribe()

go func() {
    for value := range dataCh {
        fmt.Println("Received:", value)
    }
}()

bus.Publish(42)
```

**Why this translation:**
- Go uses channels for message passing
- Explicit subscriber management
- Type-safe channels (type per channel)
- Consider existing packages (e.g., EventBus libraries)
- Goroutines handle async listeners

---

## Common Pitfalls

### 1. Ignoring Error Returns

**Problem:**
```go
// ❌ Ignoring error return
user, _ := FetchUser("123")
fmt.Println(user.Name) // Potential nil pointer dereference!
```

**Solution:**
```go
// ✓ Always check errors
user, err := FetchUser("123")
if err != nil {
    return fmt.Errorf("failed to fetch user: %w", err)
}
fmt.Println(user.Name)
```

**Why:**
- Go conventions require explicit error handling
- Ignoring errors leads to runtime panics
- Use linters (errcheck, golangci-lint) to catch

### 2. Using Pointers When Not Needed

**Problem:**
```go
// ❌ Unnecessary pointer
func Double(n *int) *int {
    result := *n * 2
    return &result
}
```

**Solution:**
```go
// ✓ Pass by value for small types
func Double(n int) int {
    return n * 2
}
```

**Why:**
- Small types (int, bool, small structs) are efficient by value
- Pointers add indirection and nil checks
- Use pointers for: large structs, mutation, or optional values

### 3. Modifying Loop Variables in Goroutines

**Problem:**
```go
// ❌ Loop variable capture bug
for _, item := range items {
    go func() {
        process(item) // All goroutines see last item!
    }()
}
```

**Solution:**
```go
// ✓ Pass variable as parameter or shadow it
for _, item := range items {
    item := item // shadow
    go func() {
        process(item)
    }()
}

// Or pass as parameter
for _, item := range items {
    go func(i string) {
        process(i)
    }(item)
}
```

**Why:**
- Loop variable is reused across iterations
- Goroutines capture variable reference, not value
- Fixed in Go 1.22+ with per-iteration variables

### 4. Not Closing Channels

**Problem:**
```go
// ❌ Channel never closed
ch := make(chan int)
go func() {
    for i := 0; i < 10; i++ {
        ch <- i
    }
    // Never closes!
}()

for val := range ch {
    fmt.Println(val) // Hangs after 10 values
}
```

**Solution:**
```go
// ✓ Close channel when done
ch := make(chan int)
go func() {
    defer close(ch)
    for i := 0; i < 10; i++ {
        ch <- i
    }
}()

for val := range ch {
    fmt.Println(val)
}
```

**Why:**
- range on channel blocks until closed
- close() signals no more values coming
- Only sender should close (not receiver)

### 5. Misunderstanding Zero Values

**Problem:**
```typescript
// TypeScript: undefined check
if (user.age !== undefined) {
  // age was explicitly set
}
```

```go
// ❌ Go: can't distinguish zero value from explicit zero
if user.Age != 0 {
    // Could be unset OR explicitly set to 0!
}
```

**Solution:**
```go
// ✓ Use pointers for optional values
type User struct {
    Name string
    Age  *int // nil means not set, 0 means explicitly zero
}

if user.Age != nil {
    fmt.Println(*user.Age)
}
```

**Why:**
- Go initializes all variables to zero values
- Can't distinguish "not set" from "set to zero"
- Use pointers when distinction matters

### 6. Forgetting defer for Cleanup

**Problem:**
```go
// ❌ Manual cleanup easy to forget
file, err := os.Open("file.txt")
if err != nil {
    return err
}
// ... lots of code ...
if someError {
    return someError // Forgot to close file!
}
file.Close()
```

**Solution:**
```go
// ✓ defer ensures cleanup
file, err := os.Open("file.txt")
if err != nil {
    return err
}
defer file.Close() // Always runs before function returns

// ... code can return anywhere ...
```

**Why:**
- defer guarantees cleanup on all return paths
- Executes in LIFO order
- Common for: files, mutexes, database connections

### 7. Copying Mutexes

**Problem:**
```go
// ❌ Copying struct with mutex
type Counter struct {
    mu    sync.Mutex
    count int
}

func (c Counter) Inc() { // Value receiver copies mutex!
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}
```

**Solution:**
```go
// ✓ Pointer receiver for structs with mutexes
func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}
```

**Why:**
- Copying a locked mutex is undefined behavior
- sync types (Mutex, WaitGroup, etc.) must not be copied
- Use pointer receivers for types with sync primitives

### 8. Interface nil Confusion

**Problem:**
```go
// ❌ Interface containing nil pointer isn't nil!
var p *User = nil
var i interface{} = p
if i != nil {
    fmt.Println("Not nil!") // This prints!
}
```

**Solution:**
```go
// ✓ Check for nil before assigning to interface
var p *User = nil
if p != nil {
    i = p
} else {
    i = nil // Or don't assign
}

// Or use typed nil check
var i interface{} = (*User)(nil)
if i == nil || i.(*User) == nil {
    // Actually nil
}
```

**Why:**
- Interface stores (type, value) pair
- (type=*User, value=nil) != (type=nil, value=nil)
- Common source of bugs in error returns

---

## Tooling

### Conversion Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| **Manual** | TypeScript → Go | No mature automated converter exists |
| AST analysis | Parse TypeScript | Use TypeScript compiler API |
| Code generation | Generate Go | Template-based or custom tooling |

### Go Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `go fmt` | Code formatting | Standardizes formatting |
| `goimports` | Import management | Adds/removes imports automatically |
| `golangci-lint` | Linting | Comprehensive linter aggregator |
| `go vet` | Static analysis | Detects common mistakes |
| `staticcheck` | Advanced static analysis | High-quality checks |
| `errcheck` | Error checking | Ensures errors are checked |
| `go test` | Testing | Built-in test framework |
| `go test -race` | Race detection | Detects race conditions |
| `pprof` | Profiling | CPU and memory profiling |
| `delve` | Debugging | Go debugger |

### Testing Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `testing` package | Unit tests | Built-in framework |
| `testify` | Assertions | Popular testing toolkit |
| `gomock` | Mocking | Interface mocking |
| `httptest` | HTTP testing | Test HTTP handlers |
| `go-cmp` | Deep comparison | Compare complex structures |

### Dependency Management

| TypeScript (npm) | Go Equivalent | Notes |
|------------------|---------------|-------|
| `axios` | `net/http`, `resty` | HTTP clients |
| `lodash` | Built-ins | Go has many built-in utilities |
| `express` | `net/http`, `gin`, `echo` | Web frameworks |
| `jest` | `testing` | Built-in testing |
| `dotenv` | `godotenv`, `viper` | Config management |
| `winston` | `log`, `zap`, `logrus` | Logging |
| `commander` | `flag`, `cobra`, `urfave/cli` | CLI parsing |
| `date-fns` | `time` | Date/time built-in |
| `uuid` | `google/uuid` | UUID generation |
| `zod` | `validator`, `ozzo-validation` | Validation |

---

## Examples

### Example 1: Simple - Type and Function Translation

**Before (TypeScript):**
```typescript
interface User {
  id: string;
  name: string;
  age: number;
  email?: string;
}

function findUserByID(users: User[], id: string): User | undefined {
  return users.find(u => u.id === id);
}

// Usage
const users: User[] = [
  { id: "1", name: "Alice", age: 30, email: "alice@example.com" },
  { id: "2", name: "Bob", age: 25 },
];

const user = findUserByID(users, "1");
if (user) {
  console.log(`Found: ${user.name}`);
}
```

**After (Go):**
```go
package main

import "fmt"

type User struct {
    ID    string
    Name  string
    Age   int
    Email *string // pointer for optional field
}

func FindUserByID(users []User, id string) *User {
    for i := range users {
        if users[i].ID == id {
            return &users[i]
        }
    }
    return nil
}

func main() {
    email := "alice@example.com"
    users := []User{
        {ID: "1", Name: "Alice", Age: 30, Email: &email},
        {ID: "2", Name: "Bob", Age: 25, Email: nil},
    }

    user := FindUserByID(users, "1")
    if user != nil {
        fmt.Printf("Found: %s\n", user.Name)
    }
}
```

### Example 2: Medium - Error Handling and JSON

**Before (TypeScript):**
```typescript
import * as fs from 'fs';

interface Config {
  host: string;
  port: number;
  debug: boolean;
}

class ConfigError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ConfigError";
  }
}

function loadConfig(path: string): Config {
  if (!fs.existsSync(path)) {
    throw new ConfigError(`Config file not found: ${path}`);
  }

  const content = fs.readFileSync(path, 'utf-8');

  try {
    const config = JSON.parse(content);

    if (!config.host || typeof config.port !== 'number') {
      throw new ConfigError("Invalid config format");
    }

    return config as Config;
  } catch (e) {
    if (e instanceof ConfigError) {
      throw e;
    }
    throw new ConfigError(`Failed to parse config: ${(e as Error).message}`);
  }
}

// Usage
try {
  const config = loadConfig("config.json");
  console.log(`Server running on ${config.host}:${config.port}`);
} catch (err) {
  if (err instanceof ConfigError) {
    console.error("Config error:", err.message);
    process.exit(1);
  }
}
```

**After (Go):**
```go
package main

import (
    "encoding/json"
    "fmt"
    "os"
)

type Config struct {
    Host  string `json:"host"`
    Port  int    `json:"port"`
    Debug bool   `json:"debug"`
}

type ConfigError struct {
    Message string
}

func (e *ConfigError) Error() string {
    return e.Message
}

func LoadConfig(path string) (*Config, error) {
    if _, err := os.Stat(path); os.IsNotExist(err) {
        return nil, &ConfigError{
            Message: fmt.Sprintf("config file not found: %s", path),
        }
    }

    content, err := os.ReadFile(path)
    if err != nil {
        return nil, &ConfigError{
            Message: fmt.Sprintf("failed to read config: %v", err),
        }
    }

    var config Config
    if err := json.Unmarshal(content, &config); err != nil {
        return nil, &ConfigError{
            Message: fmt.Sprintf("failed to parse config: %v", err),
        }
    }

    if config.Host == "" || config.Port == 0 {
        return nil, &ConfigError{
            Message: "invalid config format",
        }
    }

    return &config, nil
}

func main() {
    config, err := LoadConfig("config.json")
    if err != nil {
        var configErr *ConfigError
        if errors.As(err, &configErr) {
            fmt.Fprintf(os.Stderr, "Config error: %s\n", configErr.Message)
            os.Exit(1)
        }
    }

    fmt.Printf("Server running on %s:%d\n", config.Host, config.Port)
}
```

### Example 3: Complex - HTTP API with Async Operations

**Before (TypeScript):**
```typescript
import axios from 'axios';
import { EventEmitter } from 'events';

interface User {
  id: string;
  name: string;
  email: string;
}

interface Post {
  id: string;
  userId: string;
  title: string;
  content: string;
}

class APIClient extends EventEmitter {
  private baseURL: string;
  private cache: Map<string, any> = new Map();

  constructor(baseURL: string) {
    super();
    this.baseURL = baseURL;
  }

  async fetchUser(id: string): Promise<User> {
    const cacheKey = `user:${id}`;

    if (this.cache.has(cacheKey)) {
      this.emit('cache-hit', cacheKey);
      return this.cache.get(cacheKey);
    }

    try {
      const response = await axios.get<User>(`${this.baseURL}/users/${id}`);
      this.cache.set(cacheKey, response.data);
      this.emit('user-fetched', response.data);
      return response.data;
    } catch (error) {
      this.emit('error', error);
      throw new Error(`Failed to fetch user ${id}: ${error.message}`);
    }
  }

  async fetchUserPosts(userId: string): Promise<Post[]> {
    try {
      const response = await axios.get<Post[]>(
        `${this.baseURL}/users/${userId}/posts`
      );
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch posts: ${error.message}`);
    }
  }

  async getUserWithPosts(userId: string): Promise<{ user: User; posts: Post[] }> {
    // Fetch in parallel
    const [user, posts] = await Promise.all([
      this.fetchUser(userId),
      this.fetchUserPosts(userId),
    ]);

    return { user, posts };
  }

  clearCache(): void {
    this.cache.clear();
    this.emit('cache-cleared');
  }
}

// Usage
async function main() {
  const client = new APIClient('https://api.example.com');

  client.on('user-fetched', (user: User) => {
    console.log('Fetched user:', user.name);
  });

  client.on('cache-hit', (key: string) => {
    console.log('Cache hit:', key);
  });

  client.on('error', (error: Error) => {
    console.error('API error:', error.message);
  });

  try {
    const result = await client.getUserWithPosts('123');
    console.log(`${result.user.name} has ${result.posts.length} posts`);

    // Second fetch will hit cache
    await client.fetchUser('123');
  } catch (error) {
    console.error('Failed:', error.message);
    process.exit(1);
  }
}

main();
```

**After (Go):**
```go
package main

import (
    "encoding/json"
    "fmt"
    "net/http"
    "sync"
)

type User struct {
    ID    string `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

type Post struct {
    ID      string `json:"id"`
    UserID  string `json:"userId"`
    Title   string `json:"title"`
    Content string `json:"content"`
}

type Event struct {
    Type string
    Data interface{}
}

type APIClient struct {
    baseURL     string
    cache       map[string]interface{}
    cacheMu     sync.RWMutex
    eventCh     chan Event
    httpClient  *http.Client
}

func NewAPIClient(baseURL string) *APIClient {
    return &APIClient{
        baseURL:    baseURL,
        cache:      make(map[string]interface{}),
        eventCh:    make(chan Event, 100),
        httpClient: &http.Client{},
    }
}

func (c *APIClient) Events() <-chan Event {
    return c.eventCh
}

func (c *APIClient) emit(eventType string, data interface{}) {
    select {
    case c.eventCh <- Event{Type: eventType, Data: data}:
    default:
        // Don't block if no listeners
    }
}

func (c *APIClient) FetchUser(id string) (*User, error) {
    cacheKey := fmt.Sprintf("user:%s", id)

    // Check cache
    c.cacheMu.RLock()
    if cached, ok := c.cache[cacheKey]; ok {
        c.cacheMu.RUnlock()
        c.emit("cache-hit", cacheKey)
        return cached.(*User), nil
    }
    c.cacheMu.RUnlock()

    // Fetch from API
    url := fmt.Sprintf("%s/users/%s", c.baseURL, id)
    resp, err := c.httpClient.Get(url)
    if err != nil {
        c.emit("error", err)
        return nil, fmt.Errorf("failed to fetch user %s: %w", id, err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        err := fmt.Errorf("API returned status %d", resp.StatusCode)
        c.emit("error", err)
        return nil, err
    }

    var user User
    if err := json.NewDecoder(resp.Body).Decode(&user); err != nil {
        c.emit("error", err)
        return nil, fmt.Errorf("failed to decode user: %w", err)
    }

    // Update cache
    c.cacheMu.Lock()
    c.cache[cacheKey] = &user
    c.cacheMu.Unlock()

    c.emit("user-fetched", &user)
    return &user, nil
}

func (c *APIClient) FetchUserPosts(userID string) ([]Post, error) {
    url := fmt.Sprintf("%s/users/%s/posts", c.baseURL, userID)
    resp, err := c.httpClient.Get(url)
    if err != nil {
        return nil, fmt.Errorf("failed to fetch posts: %w", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("API returned status %d", resp.StatusCode)
    }

    var posts []Post
    if err := json.NewDecoder(resp.Body).Decode(&posts); err != nil {
        return nil, fmt.Errorf("failed to decode posts: %w", err)
    }

    return posts, nil
}

type UserWithPosts struct {
    User  *User
    Posts []Post
}

func (c *APIClient) GetUserWithPosts(userID string) (*UserWithPosts, error) {
    // Fetch in parallel using goroutines
    type userResult struct {
        user *User
        err  error
    }
    type postsResult struct {
        posts []Post
        err   error
    }

    userCh := make(chan userResult, 1)
    postsCh := make(chan postsResult, 1)

    go func() {
        user, err := c.FetchUser(userID)
        userCh <- userResult{user, err}
    }()

    go func() {
        posts, err := c.FetchUserPosts(userID)
        postsCh <- postsResult{posts, err}
    }()

    // Wait for both
    userRes := <-userCh
    postsRes := <-postsCh

    if userRes.err != nil {
        return nil, userRes.err
    }
    if postsRes.err != nil {
        return nil, postsRes.err
    }

    return &UserWithPosts{
        User:  userRes.user,
        Posts: postsRes.posts,
    }, nil
}

func (c *APIClient) ClearCache() {
    c.cacheMu.Lock()
    defer c.cacheMu.Unlock()

    c.cache = make(map[string]interface{})
    c.emit("cache-cleared", nil)
}

func main() {
    client := NewAPIClient("https://api.example.com")

    // Event listener goroutine
    go func() {
        for event := range client.Events() {
            switch event.Type {
            case "user-fetched":
                user := event.Data.(*User)
                fmt.Println("Fetched user:", user.Name)
            case "cache-hit":
                key := event.Data.(string)
                fmt.Println("Cache hit:", key)
            case "error":
                err := event.Data.(error)
                fmt.Println("API error:", err)
            case "cache-cleared":
                fmt.Println("Cache cleared")
            }
        }
    }()

    result, err := client.GetUserWithPosts("123")
    if err != nil {
        fmt.Fprintf(os.Stderr, "Failed: %v\n", err)
        os.Exit(1)
    }

    fmt.Printf("%s has %d posts\n", result.User.Name, len(result.Posts))

    // Second fetch will hit cache
    _, _ = client.FetchUser("123")
}
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `lang-typescript-dev` - TypeScript development patterns
- `lang-golang-dev` - Go development patterns
