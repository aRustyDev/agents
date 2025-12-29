---
name: lang-roc-dev
description: Foundational Roc patterns covering platform/application architecture, records, tags, pattern matching, abilities, and functional idioms. Use when writing Roc code, understanding the platform model, or needing guidance on which specialized Roc skill to use. This is the entry point for Roc development.
---

# Roc Fundamentals

Foundational Roc patterns and core language features. This skill serves as both a reference for common patterns and an index to specialized Roc skills.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Roc Skill Hierarchy                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ┌───────────────────┐                        │
│                    │   lang-roc-dev    │ ◄── You are here       │
│                    │   (foundation)    │                        │
│                    └─────────┬─────────┘                        │
│                              │                                  │
│              ┌───────────────┴───────────────┐                  │
│              │                               │                  │
│              ▼                               ▼                  │
│     ┌─────────────────┐            ┌─────────────────┐          │
│     │    patterns     │            │     platform    │          │
│     │      -dev       │            │       -dev      │          │
│     └─────────────────┘            └─────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**This skill covers:**
- Platform vs application architecture
- Records and their operations
- Tags and tag unions
- Pattern matching with when expressions
- Abilities (Roc's trait system)
- Result type and error handling
- Functional patterns and idioms
- Type inference fundamentals

**This skill does NOT cover (see specialized skills):**
- Platform development → `lang-roc-platform-dev`
- Best practices and advanced patterns → `lang-roc-patterns-dev`
- Testing strategies → `lang-roc-patterns-dev`

---

## Quick Reference

| Task | Syntax |
|------|--------|
| Define record | `{ name: "Alice", age: 30 }` |
| Record type | `{ name : Str, age : U32 }` |
| Update record | `{ user & age: 31 }` |
| Define tag | `Red` or `Custom(40, 60, 80)` |
| Tag union type | `[Red, Yellow, Green]` |
| Pattern match | `when x is ... -> ...` |
| Function type | `add : I64, I64 -> I64` |
| Error handling | `Result a err` |
| Ability constraint | `a -> Str where a implements Inspect` |
| Inline test | `expect 1 + 1 == 2` |

---

## Skill Routing

Use this table to find the right specialized skill:

| When you need to... | Use this skill |
|---------------------|----------------|
| Build custom platforms | `lang-roc-platform-dev` |
| Advanced testing strategies | `lang-roc-patterns-dev` |
| Performance optimization | `lang-roc-patterns-dev` |
| Library design patterns | `lang-roc-patterns-dev` |

---

## Platform vs Application Model

### Architecture Overview

Roc uses a unique separation between platforms and applications:

```
┌─────────────────────────────────────────────────┐
│                  Application                    │
│         (Pure functional Roc code)              │
│                                                 │
│  • Business logic                               │
│  • Data transformations                         │
│  • No direct I/O                                │
└────────────┬────────────────────────────────────┘
             │ Pure interface
             ▼
┌─────────────────────────────────────────────────┐
│                  Platform                       │
│         (Roc API + Host implementation)         │
│                                                 │
│  Roc API:    Pure functions applications use    │
│  Host:       Actual I/O implementation          │
│              (written in Rust, C, Zig, etc.)    │
└─────────────────────────────────────────────────┘
```

### Application Structure

```roc
app [main] {
    pf: platform "https://github.com/roc-lang/basic-cli/releases/download/0.10.0/vNe6s9hWzoTZtFmNkvEICPErI9ptji_ySjicO6CkucY.tar.br"
}

import pf.Stdout
import pf.Task exposing [Task]

main : Task {} []
main =
    Stdout.line! "Hello, World!"
```

**Key concepts:**
- `app` header declares entry point and platform
- Platform provides I/O capabilities (Stdout, File, Http, etc.)
- Application code remains pure
- Platform handles all effects

### Platform Responsibilities

Platforms provide:
- **I/O primitives**: File system, network, console
- **Memory management**: Allocation and deallocation
- **Program lifecycle**: Startup, shutdown, event loops
- **Host integration**: FFI to system libraries

### Common Platforms

| Platform | Purpose | Use Case |
|----------|---------|----------|
| `basic-cli` | CLI applications | Scripts, command-line tools |
| `basic-webserver` | Web servers | HTTP services, APIs |
| `static-site-gen` | Static sites | Documentation, blogs |

---

## Records

### Record Basics

```roc
# Record literal
user = { name: "Alice", age: 30, active: Bool.true }

# Record type annotation
user : { name : Str, age : U32, active : Bool }

# Accessing fields
userName = user.name
userAge = user.age

# Field access with destructuring
{ name, age } = user
```

### Record Updates

```roc
# Update single field
olderUser = { user & age: 31 }

# Update multiple fields
updatedUser = { user &
    age: 31,
    active: Bool.false
}

# Nested updates
person = {
    name: "Alice",
    address: { city: "NYC", zip: "10001" }
}

movedPerson = { person &
    address: { person.address & city: "SF" }
}
```

### Optional Fields

Roc uses tag unions for optional values, not special record syntax:

```roc
# Type with optional email
User : {
    name : Str,
    age : U32,
    email : [Some Str, None],
}

# Creating users
userWithEmail = {
    name: "Alice",
    age: 30,
    email: Some("alice@example.com")
}

userWithoutEmail = {
    name: "Bob",
    age: 25,
    email: None
}

# Handling optional values
emailText = when user.email is
    Some(addr) -> addr
    None -> "no email"
```

### Record Functions

```roc
# Function taking a record
greet : { name : Str, age : U32 } -> Str
greet = \user ->
    "Hello, \(user.name)! You are \(Num.toStr(user.age))"

# Destructuring in parameters
greetShort : { name : Str, age : U32 } -> Str
greetShort = \{ name, age } ->
    "Hello, \(name)! You are \(Num.toStr(age))"

# Partial destructuring
getName : { name : Str, age : U32 } -> Str
getName = \{ name } ->  # age is ignored
    name
```

---

## Tags and Tag Unions

### Tag Basics

```roc
# Simple tags (like enums)
color = Red
direction = North

# Tags with payloads
color = Custom(40, 60, 80)
result = Ok(42)
error = Err("Something went wrong")

# Tags with named payloads (records)
point = Point({ x: 10, y: 20 })
# Or more commonly
point = Point({ x: 10, y: 20 })
```

### Tag Union Types

```roc
# Type definition
Color : [Red, Yellow, Green, Custom(U8, U8, U8)]

# Union of different tag shapes
Result a e : [Ok a, Err e]

# Nested unions
Expression : [
    Num(I64),
    Add(Expression, Expression),
    Multiply(Expression, Expression),
]
```

### Pattern Matching on Tags

```roc
# Basic matching
colorName = when color is
    Red -> "red"
    Yellow -> "yellow"
    Green -> "green"
    Custom(r, g, b) -> "rgb(\(Num.toStr(r)), \(Num.toStr(g)), \(Num.toStr(b)))"

# Matching with guards
describe = when age is
    n if n < 13 -> "child"
    n if n < 20 -> "teenager"
    _ -> "adult"

# Nested pattern matching
eval : Expression -> I64
eval = \expr ->
    when expr is
        Num(n) -> n
        Add(left, right) -> eval(left) + eval(right)
        Multiply(left, right) -> eval(left) * eval(right)
```

### Structural Tag Unions

Roc uses structural (not nominal) types:

```roc
# No need to declare the type separately
handleStatus : [Pending, Approved, Rejected] -> Str
handleStatus = \status ->
    when status is
        Pending -> "Waiting..."
        Approved -> "Done!"
        Rejected -> "Failed"

# Type is inferred from patterns
# This is equivalent to:
# Status : [Pending, Approved, Rejected]
# handleStatus : Status -> Str
```

### Open vs Closed Tag Unions

```roc
# Closed tag union (exact set)
Color : [Red, Green, Blue]

# Open tag union (can accept more)
# Used for extensibility
handleColor : [Red, Green, Blue]* -> Str
handleColor = \color ->
    when color is
        Red -> "red"
        Green -> "green"
        Blue -> "blue"
        _ -> "unknown color"

# The * makes it open to additional tags
```

---

## Pattern Matching

### When Expressions

```roc
# Basic when
result = when value is
    1 -> "one"
    2 -> "two"
    _ -> "other"

# With destructuring
when point is
    { x: 0, y: 0 } -> "origin"
    { x, y: 0 } -> "on x-axis at \(Num.toStr(x))"
    { x: 0, y } -> "on y-axis at \(Num.toStr(y))"
    { x, y } -> "at (\(Num.toStr(x)), \(Num.toStr(y)))"

# Multiple values
when (x, y) is
    (0, 0) -> "origin"
    (0, _) -> "on y-axis"
    (_, 0) -> "on x-axis"
    _ -> "elsewhere"
```

### Pattern Types

```roc
# Literal patterns
when n is
    0 -> "zero"
    1 -> "one"
    _ -> "other"

# Variable binding
when result is
    Ok(value) -> value
    Err(msg) -> "Error: \(msg)"

# List patterns
when list is
    [] -> "empty"
    [first] -> "single: \(first)"
    [first, second] -> "pair: \(first), \(second)"
    [first, ..] -> "starts with: \(first)"

# Record patterns
when user is
    { name: "Alice", .. } -> "Hello Alice!"
    { name, .. } -> "Hello \(name)!"

# Guard clauses
when n is
    x if x < 0 -> "negative"
    x if x > 0 -> "positive"
    _ -> "zero"
```

### Exhaustiveness Checking

```roc
# Compiler enforces exhaustive matching
handleColor : [Red, Green, Blue] -> Str
handleColor = \color ->
    when color is
        Red -> "red"
        Green -> "green"
        # Missing Blue - compiler error!

# Must handle all cases or use wildcard
handleColorComplete : [Red, Green, Blue] -> Str
handleColorComplete = \color ->
    when color is
        Red -> "red"
        Green -> "green"
        Blue -> "blue"  # Now complete

# Or use wildcard for remaining cases
handleColorDefault : [Red, Green, Blue] -> Str
handleColorDefault = \color ->
    when color is
        Red -> "red"
        _ -> "not red"
```

---

## Abilities

### What are Abilities?

Abilities are Roc's version of traits/typeclasses:

```roc
# Using the Eq ability
areEqual : a, a -> Bool where a implements Eq
areEqual = \x, y ->
    x == y

# Using the Inspect ability (like Debug in Rust)
debug : a -> Str where a implements Inspect
debug = \value ->
    Inspect.toStr(value)
```

### Built-in Abilities

| Ability | Purpose | Example |
|---------|---------|---------|
| `Eq` | Structural equality | `x == y` |
| `Hash` | Hashing for dictionaries | `Dict.insert(dict, key, value)` |
| `Inspect` | Debug representation | `Inspect.toStr(value)` |
| `Decode` | Deserialize from bytes | `Decode.fromBytes(bytes)` |
| `Encode` | Serialize to bytes | `Encode.toBytes(value)` |

### Automatic Derivation

Records and tags automatically implement abilities:

```roc
# This type automatically has Eq, Hash, Inspect
User : {
    name : Str,
    age : U32,
    role : [Admin, User, Guest],
}

user1 = { name: "Alice", age: 30, role: Admin }
user2 = { name: "Alice", age: 30, role: Admin }

# Eq works automatically
expect user1 == user2  # true

# Inspect works automatically
dbg(user1)  # Shows: { name: "Alice", age: 30, role: Admin }
```

### Custom Ability Implementations

```roc
# Define a custom ability
Hash implements
    hash : a -> U64 where a implements Hash

# Implement for custom type
CustomType implements [Hash]
    hash = \val ->
        # Custom hashing logic
        computeHash(val)
```

### Ability Constraints in Functions

```roc
# Single constraint
toString : a -> Str where a implements Inspect
toString = \value ->
    Inspect.toStr(value)

# Multiple constraints
compare : a, a -> [Less, Equal, Greater]
    where a implements Eq & Ord
compare = \x, y ->
    if x < y then
        Less
    else if x > y then
        Greater
    else
        Equal

# Constraints on type parameters
Map k v : ... where k implements Hash & Eq
```

---

## Result Type and Error Handling

### Result Basics

```roc
# Result type definition
Result a e : [Ok a, Err e]

# Returning Results
divide : I64, I64 -> Result I64 [DivByZero]
divide = \a, b ->
    if b == 0 then
        Err(DivByZero)
    else
        Ok(a // b)

# Using Results
when divide(10, 2) is
    Ok(result) -> Num.toStr(result)
    Err(DivByZero) -> "Cannot divide by zero"
```

### Error Propagation with Try

```roc
# Using try (!) for error propagation
calculate : I64, I64, I64 -> Result I64 [DivByZero]
calculate = \a, b, c ->
    x = divide!(a, b)  # Returns early on Err
    y = divide!(x, c)  # Returns early on Err
    Ok(y)

# Equivalent to:
calculateVerbose : I64, I64, I64 -> Result I64 [DivByZero]
calculateVerbose = \a, b, c ->
    when divide(a, b) is
        Err(e) -> Err(e)
        Ok(x) ->
            when divide(x, c) is
                Err(e) -> Err(e)
                Ok(y) -> Ok(y)
```

### Multiple Error Types

```roc
# Tag union for different errors
parseAndDivide : Str, Str -> Result I64 [ParseError Str, DivByZero]
parseAndDivide = \aStr, bStr ->
    a = Str.toI64!(aStr) |> Result.mapErr(\_ -> ParseError("Invalid a"))
    b = Str.toI64!(bStr) |> Result.mapErr(\_ -> ParseError("Invalid b"))
    divide!(a, b)

# Handling all error cases
when parseAndDivide("10", "2") is
    Ok(result) -> "Result: \(Num.toStr(result))"
    Err(ParseError(msg)) -> "Parse error: \(msg)"
    Err(DivByZero) -> "Division by zero"
```

### Result Helpers

```roc
# Map over Ok value
result = divide(10, 2)
    |> Result.map(\x -> x * 2)  # Ok(10)

# Map over Err value
result = divide(10, 0)
    |> Result.mapErr(\DivByZero -> "Error: division by zero")

# Provide default on error
value = divide(10, 0)
    |> Result.withDefault(0)  # Returns 0

# Chain Results
chain : Result a e, (a -> Result b e) -> Result b e
result = divide(10, 2)
    |> Result.try(\x -> divide(x, 2))
```

---

## Type System Fundamentals

### Type Inference

```roc
# Types are inferred
double = \x -> x * 2
# Inferred type: Num a -> Num a

# Can add explicit annotations
double : I64 -> I64
double = \x -> x * 2

# Type parameters
identity : a -> a
identity = \x -> x

# Type parameters with constraints
show : a -> Str where a implements Inspect
show = \x -> Inspect.toStr(x)
```

### Number Types

```roc
# Integer types
i8, i16, i32, i64, i128  # Signed integers
u8, u16, u32, u64, u128  # Unsigned integers

# Flexible numbers (type inferred from usage)
x = 42       # Num *
y = x + 1    # Still Num *, becomes concrete when needed

# Explicit typing
x : I64
x = 42

# Floating point
f32, f64     # 32-bit and 64-bit floats
pi : F64
pi = 3.14159
```

### Function Types

```roc
# Function with single parameter
increment : I64 -> I64

# Multiple parameters (curried)
add : I64, I64 -> I64

# Function taking a function
map : List a, (a -> b) -> List b

# Function with abilities constraint
sort : List a -> List a where a implements Ord
```

### Type Aliases

```roc
# Create type aliases for clarity
UserId : U64
UserName : Str

User : {
    id : UserId,
    name : UserName,
    email : Str,
}

# Opaque types (hide implementation)
Age := U32

createAge : U32 -> Age
createAge = \n -> @Age(n)

getAge : Age -> U32
getAge = \@Age(n) -> n
```

---

## Functional Patterns

### List Operations

```roc
# Map
numbers = [1, 2, 3, 4, 5]
doubled = List.map(numbers, \n -> n * 2)
# [2, 4, 6, 8, 10]

# Filter
evens = List.keepIf(numbers, \n -> n % 2 == 0)
# [2, 4]

# Fold (reduce)
sum = List.walk(numbers, 0, \acc, n -> acc + n)
# 15

# Find
maybeFirst = List.findFirst(numbers, \n -> n > 3)
# Ok(4)

# Chain operations with pipeline
result = numbers
    |> List.map(\n -> n * 2)
    |> List.keepIf(\n -> n > 5)
    |> List.walk(0, Num.add)
```

### Pipeline Operator

```roc
# Without pipeline
result = add(multiply(2, 3), 4)

# With pipeline (left to right)
result = 2
    |> multiply(3)
    |> add(4)

# Common with list operations
users
    |> List.map(\u -> u.name)
    |> List.sortAsc
    |> Str.joinWith(", ")
```

### Dict (Dictionary/Map)

```roc
# Create dictionary
scores = Dict.empty({})
    |> Dict.insert("Alice", 100)
    |> Dict.insert("Bob", 85)
    |> Dict.insert("Charlie", 92)

# Get value
aliceScore = Dict.get(scores, "Alice")
# Ok(100)

# Update value
newScores = Dict.update(scores, "Alice", \maybeScore ->
    when maybeScore is
        Some(score) -> Some(score + 10)
        None -> None
)

# Keys and values
allNames = Dict.keys(scores)
allScores = Dict.values(scores)
```

### Set Operations

```roc
# Create sets
set1 = Set.fromList([1, 2, 3, 4])
set2 = Set.fromList([3, 4, 5, 6])

# Union
union = Set.union(set1, set2)
# {1, 2, 3, 4, 5, 6}

# Intersection
intersection = Set.intersection(set1, set2)
# {3, 4}

# Difference
diff = Set.difference(set1, set2)
# {1, 2}

# Contains
hasThree = Set.contains(set1, 3)
# Bool.true
```

---

## Testing with Expect

### Basic Expects

```roc
# Simple test
expect 1 + 1 == 2

# Test with variables
add = \a, b -> a + b
expect add(2, 3) == 5

# Multiple expects
expect
    result = divide(10, 2)
    result == Ok(5)

expect
    result = divide(10, 0)
    result == Err(DivByZero)
```

### Inline Expects

```roc
# Verify assumptions in functions
factorial : U64 -> U64
factorial = \n ->
    # Verify our assumption
    expect n <= 20  # Factorial grows quickly!

    when n is
        0 -> 1
        _ -> n * factorial(n - 1)
```

### Testing with roc test

```roc
# Top-level expects run with `roc test`
expect List.map([1, 2, 3], \x -> x * 2) == [2, 4, 6]

expect
    users = [
        { name: "Alice", age: 30 },
        { name: "Bob", age: 25 },
    ]
    oldest = List.sortWith(users, \a, b ->
        Num.compare(b.age, a.age)
    )
    List.first(oldest) == Ok({ name: "Alice", age: 30 })
```

---

## Common Idioms

### Option Pattern (Maybe)

```roc
# Roc doesn't have a built-in Maybe/Option
# Use tag unions instead
MaybeUser : [Some User, None]

findUser : U64 -> [Some User, None]
findUser = \id ->
    # ... search logic
    if found then
        Some(user)
    else
        None

# Using the result
when findUser(1) is
    Some(user) -> "Found: \(user.name)"
    None -> "Not found"
```

### Parsing Pattern

```roc
# Parser combinator style
Parser a : Str -> Result { value : a, rest : Str } [ParseError Str]

parseInt : Parser I64
parseInt = \input ->
    when Str.toI64(input) is
        Ok(n) -> Ok({ value: n, rest: "" })
        Err(_) -> Err(ParseError("Not a number"))

# Chain parsers
parsePoint : Parser { x : I64, y : I64 }
parsePoint = \input ->
    { value: x, rest: afterX } = parseInt!(input)
    { value: y, rest: afterY } = parseInt!(afterX)
    Ok({ value: { x, y }, rest: afterY })
```

### Task Pattern (Effects)

```roc
# Platform-provided Task type for effects
Task a err : [Task a err]

# Chaining tasks
main : Task {} []
main =
    # Read file
    content = File.readUtf8!("input.txt")

    # Process content
    processed = String.toUpper(content)

    # Write result
    File.writeUtf8!("output.txt", processed)

    # Log completion
    Stdout.line!("Done!")
```

### Builder Pattern

```roc
# Use records with update syntax
RequestBuilder : {
    url : Str,
    method : [Get, Post, Put, Delete],
    headers : Dict Str Str,
    body : [Some Str, None],
}

defaultRequest : Str -> RequestBuilder
defaultRequest = \url -> {
    url,
    method: Get,
    headers: Dict.empty({}),
    body: None,
}

# Build requests
request = defaultRequest("https://api.example.com")
    |> \r -> { r & method: Post }
    |> \r -> { r & headers: Dict.insert(r.headers, "Content-Type", "application/json") }
    |> \r -> { r & body: Some("{\"key\": \"value\"}") }
```

---

## Troubleshooting

### Type Mismatch Errors

**Problem:** "Type mismatch in when branch"

```roc
# Wrong - branches return different types
value = when condition is
    Bool.true -> 42
    Bool.false -> "false"  # Error!
```

**Fix:** Ensure all branches return the same type:
```roc
value = when condition is
    Bool.true -> "true"
    Bool.false -> "false"
```

### Non-Exhaustive Pattern Match

**Problem:** "Pattern match is not exhaustive"

```roc
# Wrong - missing Blue case
colorName = when color is
    Red -> "red"
    Green -> "green"
    # Missing Blue!
```

**Fix:** Add all cases or use wildcard:
```roc
# Option 1: Add missing case
colorName = when color is
    Red -> "red"
    Green -> "green"
    Blue -> "blue"

# Option 2: Use wildcard
colorName = when color is
    Red -> "red"
    _ -> "other"
```

### Circular Type Definitions

**Problem:** Type depends on itself incorrectly

```roc
# Correct recursive type
List a : [Nil, Cons a (List a)]

# Wrong - missing tag wrapper
BadList a : [a, BadList a]  # Error!
```

**Fix:** Wrap recursive references in tags:
```roc
List a : [Nil, Cons a (List a)]
```

### Ability Constraint Errors

**Problem:** "Type doesn't implement required ability"

```roc
# Wrong - function has no Eq
compare : a, a -> Bool where a implements Eq
compare = \x, y -> x == y

# Trying to use with function
fn = \x -> x + 1
result = compare(fn, fn)  # Error: function doesn't implement Eq
```

**Fix:** Only use types that implement the required ability:
```roc
result = compare(42, 42)  # OK: I64 implements Eq
```

### Task Error Propagation

**Problem:** Not handling task errors properly

```roc
# Wrong - ignoring potential errors
main =
    content = File.readUtf8!("missing.txt")  # Might fail!
    Stdout.line!(content)
```

**Fix:** Handle errors explicitly:
```roc
main =
    when File.readUtf8("missing.txt") is
        Ok(content) -> Stdout.line!(content)
        Err(err) -> Stderr.line!("Error: \(Inspect.toStr(err))")
```

---

## References

- [Roc Tutorial](https://www.roc-lang.org/tutorial)
- [Roc Examples](https://www.roc-lang.org/examples/)
- [Roc Abilities Documentation](https://www.roc-lang.org/abilities)
- [Platforms and Apps](https://www.roc-lang.org/platforms)
- [Roc FAQ](https://github.com/Ivo-Balbaert/roc-lang/blob/main/FAQ.md)
- Specialized skills: `lang-roc-patterns-dev`, `lang-roc-platform-dev`
