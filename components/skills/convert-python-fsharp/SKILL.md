---
name: convert-python-fsharp
description: Convert Python code to idiomatic F#. Use when migrating Python projects to F#, translating Python patterns to idiomatic F#, or refactoring Python codebases for type safety, functional programming, and .NET integration. Extends meta-convert-dev with Python-to-F# specific patterns.
---

# Convert Python to F#

Convert Python code to idiomatic F#. This skill extends `meta-convert-dev` with Python-to-F# specific type mappings, idiom translations, and tooling for transforming dynamic, garbage-collected Python code into functional-first, statically-typed F# on the .NET platform.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Python types → F# types (dynamic → static)
- **Idiom translations**: Imperative/OOP Python → functional-first F#
- **Error handling**: Exceptions → Result/Option types
- **Async patterns**: asyncio → Async workflows
- **Type system**: Duck typing → discriminated unions + type inference
- **Collection patterns**: List comprehensions → List/Seq expressions + pipe operator

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Python language fundamentals - see `lang-python-dev`
- F# language fundamentals - see `lang-fsharp-dev`
- Reverse conversion (F# → Python) - see `convert-fsharp-python` or Fable.Python transpiler

---

## Quick Reference

| Python | F# | Notes |
|--------|------|-------|
| `int` | `int`, `int64`, `bigint` | F# int is 32-bit, Python has arbitrary precision |
| `float` | `float` | IEEE 754 double precision |
| `bool` | `bool` | Direct mapping |
| `str` | `string` | Immutable by default in both |
| `bytes` | `byte[]` | Byte array |
| `list[T]` | `List<'T>` | F# lists are immutable, linked |
| `list[T]` (mutable) | `ResizeArray<'T>` | .NET List<T> |
| `tuple` | `'T * 'U` | Tuple syntax |
| `dict[K, V]` | `Map<'K, 'V>` | Immutable map |
| `dict[K, V]` (mutable) | `Dictionary<'K, 'V>` | .NET Dictionary |
| `set[T]` | `Set<'T>` | Immutable set |
| `None` | `None` (in `Option<'T>`) | Explicit nullable |
| `Union[T, U]` | Discriminated union | Tagged union |
| `Callable[[Args], Ret]` | `'Args -> 'Ret` | Function type |
| `async def` | `async { }` | Async computation expression |
| `@dataclass` | `type Record = { }` | F# records |
| `try/except` | `Result<'T, 'E>` or `try/with` | Railway-oriented programming preferred |

## When Converting Code

1. **Analyze source thoroughly** before writing target
2. **Map types first** - create type equivalence table
3. **Embrace immutability** - F# defaults to immutable; use mutable sparingly
4. **Adopt functional patterns** - don't write "Python code in F# syntax"
5. **Use type inference** - F# infers most types; annotate only when needed
6. **Railway-oriented programming** - prefer Result/Option over exceptions
7. **Leverage pipe operator** - chain operations with `|>`
8. **Test equivalence** - same inputs → same outputs

---

## Type System Mapping

### Primitive Types

| Python | F# | Notes |
|--------|------|-------|
| `int` | `int` | 32-bit signed integer |
| `int` (large) | `int64` | 64-bit signed integer |
| `int` (arbitrary) | `bigint` | Arbitrary precision (like Python) |
| `float` | `float` | 64-bit floating point (F# `float` = .NET `Double`) |
| `bool` | `bool` | Direct mapping |
| `str` | `string` | UTF-16 immutable string (.NET) |
| `bytes` | `byte[]` | Byte array |
| `bytearray` | `ResizeArray<byte>` | Mutable byte array |
| `None` | `Option.None` | Must be wrapped in `Option<'T>` |
| `...` (Ellipsis) | - | No direct equivalent |

**Critical Note on Integers**: Python's `int` type has **arbitrary precision** and never overflows. F# `int` is 32-bit (like C#). Use `bigint` for Python-like arbitrary precision, or `int64` for most cases.

### Collection Types

| Python | F# | Notes |
|--------|------|-------|
| `list[T]` | `List<'T>` | F# list is immutable, singly-linked |
| `list[T]` (mutable) | `ResizeArray<'T>` | .NET `List<T>` (mutable, growable) |
| `tuple` | `'T * 'U * ...` | Fixed-size, immutable |
| `dict[K, V]` | `Map<'K, 'V>` | Immutable map (tree-based) |
| `dict[K, V]` (mutable) | `Dictionary<'K, 'V>` | .NET `Dictionary` (hash-based) |
| `set[T]` | `Set<'T>` | Immutable set |
| `set[T]` (mutable) | `HashSet<'T>` | .NET `HashSet` |
| `frozenset[T]` | `Set<'T>` | Immutable by default in F# |
| `collections.deque` | `Queue<'T>` | .NET `Queue` |
| `collections.OrderedDict` | Use `List<'K * 'V>` | Preserve insertion order |
| `collections.defaultdict` | `Map` + `Map.tryFind` | Use `defaultArg` pattern |
| `collections.Counter` | `Map<'T, int>` | Count occurrences |

### Composite Types

| Python | F# | Notes |
|--------|------|-------|
| `class` (data) | `type Record = { }` | F# records are immutable by default |
| `class` (behavior) | `type` + member methods | OOP supported but not idiomatic |
| `@dataclass` | `type Record = { }` | Records with structural equality |
| `typing.Protocol` | Interface | Structural typing → nominal in F# |
| `typing.TypedDict` | `type Record = { }` | Named fields |
| `typing.NamedTuple` | `type Record = { }` | Prefer records over tuples |
| `enum.Enum` | Discriminated union | `type Color = Red | Green | Blue` |
| `typing.Literal["a", "b"]` | Discriminated union | `type Status = Active | Inactive` |
| `typing.Union[T, U]` | `type Result = A of 'T | B of 'U` | Tagged union |
| `typing.Optional[T]` | `Option<'T>` | Explicit nullable |
| `typing.Callable[[Args], Ret]` | `'Args -> 'Ret` | Function type |
| `typing.Generic[T]` | `'T` | Generic type parameter |

### Type Annotations → Generics

| Python | F# | Notes |
|--------|------|-------|
| `def f(x: T) -> T` | `let f (x: 'T) : 'T = x` | Unconstrained generic (usually inferred) |
| `def f(x: Iterable[T])` | `let f (x: seq<'T>) = ...` | F# `seq<'T>` is lazy |
| `def f(x: Sequence[T])` | `let f (x: 'T list) = ...` | Or `'T[]` for arrays |
| `x: Any` | **Avoid** - use generics | `obj` exists but discouraged |
| `x: object` | `obj` | Root type, but use generics instead |

---

## Idiom Translation

### Pattern 1: None Handling (Optional Chaining)

**Python:**
```python
# Optional chaining with walrus operator
if user := get_user(user_id):
    name = user.name
else:
    name = "Anonymous"

# Or simpler
name = user.name if user else "Anonymous"
```

**F#:**
```fsharp
// Option pattern matching
let name =
    match get_user user_id with
    | Some user -> user.Name
    | None -> "Anonymous"

// Or with defaultArg
let name =
    get_user user_id
    |> Option.map (fun u -> u.Name)
    |> Option.defaultValue "Anonymous"
```

**Why this translation:**
- Python uses truthiness while F# uses explicit `Option<'T>`
- F# pattern matching is exhaustive (compiler ensures all cases handled)
- Pipe operator `|>` chains operations left-to-right (like UNIX pipes)

### Pattern 2: List Comprehensions → List/Seq Expressions

**Python:**
```python
# List comprehension
squared_evens = [x * x for x in numbers if x % 2 == 0]

# Generator expression
total = sum(x * x for x in numbers if x % 2 == 0)
```

**F#:**
```fsharp
// List expression
let squaredEvens =
    [ for x in numbers do
        if x % 2 = 0 then
          x * x ]

// Or with pipe operator (more idiomatic)
let squaredEvens =
    numbers
    |> List.filter (fun x -> x % 2 = 0)
    |> List.map (fun x -> x * x)

// Seq for lazy evaluation (like generator)
let total =
    numbers
    |> Seq.filter (fun x -> x % 2 = 0)
    |> Seq.map (fun x -> x * x)
    |> Seq.sum
```

**Why this translation:**
- F# has both list expressions (like comprehensions) and pipe chains
- Pipe operator style is more composable and idiomatic
- `Seq<'T>` is lazy (like Python generators), `List<'T>` is eager

### Pattern 3: Dictionary/Map Operations

**Python:**
```python
# Create dictionary
counts = {"apple": 5, "banana": 3}

# Add/update
counts["orange"] = 2
counts["apple"] += 1

# Safe get with default
count = counts.get("grape", 0)
```

**F#:**
```fsharp
// Create immutable map
let counts =
    Map.ofList [
        "apple", 5
        "banana", 3
    ]

// Add/update (returns new map)
let counts2 = counts |> Map.add "orange" 2
let counts3 = counts2 |> Map.add "apple" 6

// Safe get with default
let count = counts |> Map.tryFind "grape" |> Option.defaultValue 0

// Or for mutable dictionary (.NET)
let mutableCounts = System.Collections.Generic.Dictionary<string, int>()
mutableCounts.["apple"] <- 5
mutableCounts.["apple"] <- mutableCounts.["apple"] + 1
```

**Why this translation:**
- F# defaults to immutable `Map<'K, 'V>` (functional style)
- Operations return new maps rather than mutating in-place
- Can use .NET `Dictionary` for mutable operations when needed

### Pattern 4: Class → Record + Functions

**Python:**
```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

    def distance_from_origin(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5
```

**F#:**
```fsharp
// F# record type
type Point = {
    X: float
    Y: float
}

// Standalone function (idiomatic F#)
let distanceFromOrigin point =
    sqrt (point.X ** 2.0 + point.Y ** 2.0)

// Or as member method if needed
type Point with
    member this.DistanceFromOrigin() =
        sqrt (this.X ** 2.0 + this.Y ** 2.0)

// Usage
let p = { X = 3.0; Y = 4.0 }
let dist = distanceFromOrigin p  // Functional style
let dist2 = p.DistanceFromOrigin()  // OOP style
```

**Why this translation:**
- F# records provide structural equality automatically
- Separating data (record) from functions is more functional
- Member methods available but less idiomatic than standalone functions

### Pattern 5: Iteration and Loops → Recursion/Higher-Order Functions

**Python:**
```python
# Imperative loop
def factorial(n: int) -> int:
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
```

**F#:**
```fsharp
// Recursive function (idiomatic F#)
let rec factorial n =
    match n with
    | 0 | 1 -> 1
    | _ -> n * factorial (n - 1)

// Or tail-recursive (better for large n)
let factorial n =
    let rec loop acc n =
        match n with
        | 0 | 1 -> acc
        | _ -> loop (acc * n) (n - 1)
    loop 1 n

// Or using fold (most functional)
let factorial n =
    [1..n] |> List.fold (*) 1
```

**Why this translation:**
- F# favors recursion and higher-order functions over loops
- Tail recursion is optimized by F# compiler
- `fold`, `map`, `filter` express intent more clearly than loops

### Pattern 6: Context Managers → use Binding

**Python:**
```python
# Context manager
with open("file.txt", "r") as f:
    content = f.read()
# f is automatically closed
```

**F#:**
```fsharp
// use binding (implements IDisposable)
use file = System.IO.File.OpenText("file.txt")
let content = file.ReadToEnd()
// file is automatically disposed at end of scope

// Or with explicit scope
let content =
    use file = System.IO.File.OpenText("file.txt")
    file.ReadToEnd()
```

**Why this translation:**
- F# `use` binding calls `Dispose()` automatically
- Both Python and F# ensure resource cleanup
- F# leverages .NET's `IDisposable` pattern

---

## Error Handling

### Python Exceptions → F# Result Type

**Python's exception model:**
```python
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

try:
    result = divide(10, 0)
except ValueError as e:
    print(f"Error: {e}")
    result = 0
```

**F# Result type (idiomatic):**
```fsharp
// Define error type
type MathError =
    | DivideByZero
    | InvalidInput of string

// Function returns Result<'T, 'E>
let divide a b =
    if b = 0.0 then
        Error DivideByZero
    else
        Ok (a / b)

// Pattern match on result
let result =
    match divide 10.0 0.0 with
    | Ok value -> value
    | Error DivideByZero ->
        printfn "Error: Cannot divide by zero"
        0.0
    | Error (InvalidInput msg) ->
        printfn "Error: %s" msg
        0.0
```

**F# with try/with (when needed):**
```fsharp
// F# also supports exceptions for interop
let result =
    try
        divide 10.0 0.0
    with
    | :? System.DivideByZeroException as ex ->
        printfn "Error: %s" ex.Message
        0.0
```

**Railway-Oriented Programming:**
```fsharp
// Chaining operations that might fail
let validateAge age =
    if age >= 0 && age <= 150 then
        Ok age
    else
        Error "Age out of range"

let validateName name =
    if String.IsNullOrWhiteSpace(name) then
        Error "Name cannot be empty"
    else
        Ok name

// Compose validations
type Person = { Name: string; Age: int }

let createPerson name age =
    match validateName name, validateAge age with
    | Ok n, Ok a -> Ok { Name = n; Age = a }
    | Error e, _ -> Error e
    | _, Error e -> Error e

// Or with Result.bind
let createPerson2 name age =
    validateName name
    |> Result.bind (fun n ->
        validateAge age
        |> Result.map (fun a -> { Name = n; Age = a }))
```

**Why this approach:**
- `Result<'T, 'E>` makes errors explicit in the type system
- Errors are values, not control flow
- Railway-oriented programming chains operations cleanly
- Compiler enforces error handling

---

## Concurrency Patterns

### Python asyncio → F# Async Workflows

**Python:**
```python
import asyncio

async def fetch_data(url: str) -> str:
    await asyncio.sleep(1)  # Simulate I/O
    return f"Data from {url}"

async def process_urls(urls: list[str]) -> list[str]:
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

# Run
urls = ["url1", "url2", "url3"]
results = asyncio.run(process_urls(urls))
```

**F#:**
```fsharp
open System

// Async workflow
let fetchData url = async {
    do! Async.Sleep 1000  // Simulate I/O
    return sprintf "Data from %s" url
}

let processUrls urls = async {
    let! results =
        urls
        |> List.map fetchData
        |> Async.Parallel
    return results
}

// Run
let urls = ["url1"; "url2"; "url3"]
let results = processUrls urls |> Async.RunSynchronously
```

**Why this translation:**
- F# `async { }` is a computation expression (similar to async/await)
- `do!` is like `await` without a return value
- `let!` is like `await` with a return value
- `Async.Parallel` is like `asyncio.gather`

### Threading Models

| Python | F# | Notes |
|--------|------|-------|
| `threading.Thread` | `System.Threading.Thread` | Direct .NET interop |
| `asyncio` | `async { }` | Async workflows |
| `multiprocessing` | - | F# uses .NET Task Parallel Library |
| `concurrent.futures` | `Task<'T>` | .NET Tasks |

**F# Task vs Async:**
```fsharp
// F# Async (native)
let fetchAsync url = async {
    do! Async.Sleep 1000
    return "data"
}

// .NET Task (for interop)
open System.Threading.Tasks

let fetchTask url = task {
    do! Task.Delay 1000
    return "data"
}

// Convert between them
let asyncToTask = fetchAsync "url" |> Async.StartAsTask
let taskToAsync = fetchTask "url" |> Async.AwaitTask
```

---

## Memory & Garbage Collection

Both Python and F# use garbage collection, making this conversion simpler than Python → Rust.

| Aspect | Python | F# |
|--------|--------|-----|
| Memory management | Reference counting + GC | .NET GC (generational) |
| Mutability | Mutable by default | Immutable by default |
| String interning | Yes | Yes (.NET) |
| Object lifetime | GC managed | GC managed |

**Key difference**: F# defaults to **immutability**, which reduces bugs and makes concurrency safer.

---

## Common Pitfalls

1. **Mutability assumptions**: Python is mutable by default; F# is immutable by default
   - Use `mutable` keyword or `ResizeArray`/`Dictionary` for mutable state

2. **List performance**: F# `List<'T>` is a linked list, not an array
   - Use `ResizeArray<'T>` (.NET `List<T>`) for random access
   - Use `Array` for fixed-size collections

3. **Integer overflow**: Python `int` never overflows; F# `int` is 32-bit
   - Use `bigint` for arbitrary precision
   - Use `Checked` context for overflow detection

4. **String indexing**: Python uses 0-based indexing; F# strings are .NET strings
   - F# strings are UTF-16 (not UTF-8 like Python 3)
   - Indexing: `s.[0]` gets a `char`, not a string

5. **Null values**: Python has `None`; F# discourages `null`
   - Use `Option<'T>` instead of nullable references
   - Only .NET interop types can be `null`

6. **Whitespace significance**: Python uses indentation; F# uses indentation but less strictly
   - F# requires proper indentation in computation expressions
   - Use `#light "off"` to disable (not recommended)

7. **Function application**: Python uses `f(x, y)`; F# uses `f x y`
   - Parentheses only needed for grouping: `f (x + 1) y`
   - Tupled arguments: `f(x, y)` is a single tuple argument

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| **dotnet CLI** | Build, run, test F# projects | `dotnet new console -lang F#` |
| **Ionide** | F# support for VS Code | Syntax, IntelliSense, debugging |
| **JetBrains Rider** | Full-featured F# IDE | Commercial, cross-platform |
| **FSI (F# Interactive)** | REPL for F# | Interactive development like Python REPL |
| **Paket** | Alternative package manager | More control than NuGet |
| **FAKE** | F# build automation | Like Make/Rake but in F# |
| **FsCheck** | Property-based testing | Like Python's Hypothesis |
| **Expecto** | F# test framework | Lightweight, functional |
| **Fable.Python** | F# → Python transpiler | Compile F# to Python |
| **FSharp.Data** | Type providers for CSV/JSON/XML | Strongly-typed data access |

---

## Examples

### Example 1: Simple - List Processing

**Before (Python):**
```python
def filter_and_square(numbers: list[int]) -> list[int]:
    """Filter even numbers and square them."""
    return [x * x for x in numbers if x % 2 == 0]

result = filter_and_square([1, 2, 3, 4, 5, 6])
print(result)  # [4, 16, 36]
```

**After (F#):**
```fsharp
// Type-inferred function
let filterAndSquare numbers =
    numbers
    |> List.filter (fun x -> x % 2 = 0)
    |> List.map (fun x -> x * x)

let result = filterAndSquare [1; 2; 3; 4; 5; 6]
printfn "%A" result  // [4; 16; 36]
```

### Example 2: Medium - Error Handling + Options

**Before (Python):**
```python
from typing import Optional

def find_user(user_id: int, users: list[dict]) -> Optional[dict]:
    """Find user by ID."""
    for user in users:
        if user["id"] == user_id:
            return user
    return None

def get_user_name(user_id: int, users: list[dict]) -> str:
    """Get user name, or 'Unknown' if not found."""
    user = find_user(user_id, users)
    if user:
        return user["name"]
    else:
        return "Unknown"

users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
]

print(get_user_name(1, users))  # Alice
print(get_user_name(99, users))  # Unknown
```

**After (F#):**
```fsharp
// Define types
type User = { Id: int; Name: string }

// Find user (returns Option)
let findUser userId users =
    users
    |> List.tryFind (fun user -> user.Id = userId)

// Get user name with default
let getUserName userId users =
    findUser userId users
    |> Option.map (fun user -> user.Name)
    |> Option.defaultValue "Unknown"

// Data
let users = [
    { Id = 1; Name = "Alice" }
    { Id = 2; Name = "Bob" }
]

printfn "%s" (getUserName 1 users)   // Alice
printfn "%s" (getUserName 99 users)  // Unknown
```

### Example 3: Complex - Async Processing with Error Handling

**Before (Python):**
```python
import asyncio
from typing import Union, List
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str

async def fetch_user(user_id: int) -> Union[User, str]:
    """Fetch user asynchronously. Returns User or error message."""
    await asyncio.sleep(0.1)  # Simulate network delay

    if user_id < 0:
        return "Invalid user ID"
    elif user_id > 1000:
        return "User not found"
    else:
        return User(
            id=user_id,
            name=f"User{user_id}",
            email=f"user{user_id}@example.com"
        )

async def process_users(user_ids: List[int]) -> tuple[List[User], List[str]]:
    """Process multiple users, separating successes and errors."""
    tasks = [fetch_user(uid) for uid in user_ids]
    results = await asyncio.gather(*tasks)

    users = []
    errors = []

    for result in results:
        if isinstance(result, User):
            users.append(result)
        else:
            errors.append(result)

    return users, errors

# Run
user_ids = [1, -5, 42, 9999]
users, errors = asyncio.run(process_users(user_ids))

print(f"Fetched {len(users)} users")
for user in users:
    print(f"  - {user.name}: {user.email}")

print(f"Encountered {len(errors)} errors")
for error in errors:
    print(f"  - {error}")
```

**After (F#):**
```fsharp
open System

// Define types
type User = {
    Id: int
    Name: string
    Email: string
}

type FetchError =
    | InvalidUserId
    | UserNotFound

// Async function returning Result
let fetchUser userId = async {
    do! Async.Sleep 100  // Simulate network delay

    if userId < 0 then
        return Error InvalidUserId
    elif userId > 1000 then
        return Error UserNotFound
    else
        return Ok {
            Id = userId
            Name = sprintf "User%d" userId
            Email = sprintf "user%d@example.com" userId
        }
}

// Process multiple users
let processUsers userIds = async {
    let! results =
        userIds
        |> List.map fetchUser
        |> Async.Parallel

    let users, errors =
        results
        |> Array.partition (function Ok _ -> true | Error _ -> false)
        |> fun (oks, errs) ->
            let users = oks |> Array.choose (function Ok u -> Some u | _ -> None)
            let errors = errs |> Array.choose (function Error e -> Some e | _ -> None)
            (users, errors)

    return (users, errors)
}

// Run
let userIds = [1; -5; 42; 9999]
let users, errors = processUsers userIds |> Async.RunSynchronously

printfn "Fetched %d users" (Array.length users)
for user in users do
    printfn "  - %s: %s" user.Name user.Email

printfn "Encountered %d errors" (Array.length errors)
for error in errors do
    let msg =
        match error with
        | InvalidUserId -> "Invalid user ID"
        | UserNotFound -> "User not found"
    printfn "  - %s" msg
```

**Key differences:**
- F# uses `Result<'T, 'E>` instead of `Union[T, str]` for error handling
- Discriminated unions for error types (not string messages)
- Pattern matching with `match` for exhaustive handling
- `Async.Parallel` for concurrent operations
- Pipe operator chains for data transformations
- Type inference removes most type annotations

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-python-rust` - Python → Rust conversion (similar dynamic → static transition)
- `convert-typescript-python` - TypeScript → Python (reverse static → dynamic)
- `lang-python-dev` - Python development patterns
- `lang-fsharp-dev` - F# development patterns

Cross-cutting pattern skills (for areas not fully covered by lang-*-dev):
- `patterns-concurrency-dev` - Async, channels, threads across languages
- `patterns-serialization-dev` - JSON, validation, struct tags across languages
- `patterns-metaprogramming-dev` - Decorators, macros, annotations across languages

External resources:
- [F# for Python programmers](https://fsharp.org/) - Official F# learning resources
- [Fable.Python](https://fable.io/Fable.Python/) - F# to Python transpiler (reverse direction)
- [F# Language Reference](https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/) - Comprehensive F# documentation
