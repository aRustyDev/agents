---
name: lang-fsharp-dev
description: Foundational F# patterns covering functional-first programming, type providers, computation expressions, and domain modeling. Use when writing F# code, understanding functional patterns, working with type providers, or building .NET applications with F#. This is the entry point for F# development.
---

# F# Fundamentals

Foundational F# patterns and core language features. This skill serves as both a reference for common patterns and guidance for functional-first .NET development.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      F# Skill Hierarchy                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ┌───────────────────┐                        │
│                    │  lang-fsharp-dev  │ ◄── You are here       │
│                    │   (foundation)    │                        │
│                    └─────────┬─────────┘                        │
│                              │                                  │
│     ┌────────────┬───────────┼───────────┬────────────┐        │
│     │            │           │           │            │        │
│     ▼            ▼           ▼           ▼            ▼        │
│ ┌────────┐ ┌──────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐   │
│ │ type   │ │ domain   │ │ async  │ │ testing │ │ web-api  │   │
│ │providers│ │ modeling │ │ -dev   │ │  -dev   │ │   -dev   │   │
│ └────────┘ └──────────┘ └────────┘ └─────────┘ └──────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**This skill covers:**
- Functional-first programming patterns
- Type system (records, discriminated unions, options)
- Pattern matching and active patterns
- Computation expressions basics
- Type providers fundamentals
- Domain modeling with types
- Interop with C# and .NET

**This skill does NOT cover (see specialized skills):**
- Advanced type providers usage
- Domain-driven design patterns
- Async/Task programming deep dive
- Testing frameworks (Expecto, xUnit, FsUnit)
- Web development (Giraffe, Saturn, Falco)

---

## Quick Reference

| Task | Pattern |
|------|---------|
| Define record | `type Person = { Name: string; Age: int }` |
| Define union | `type Result<'T,'E> = Ok of 'T \| Error of 'E` |
| Pattern match | `match value with \| Some x -> x \| None -> 0` |
| Define function | `let add x y = x + y` |
| Pipe operator | `value \|> function1 \|> function2` |
| Composition | `let f = function1 >> function2` |
| List comprehension | `[ for i in 1..10 -> i * i ]` |
| Async computation | `async { let! result = fetchData() return result }` |

---

## Core Types

### Records

```fsharp
// Basic record
type Person = {
    FirstName: string
    LastName: string
    Age: int
}

// Creating instances
let person = {
    FirstName = "John"
    LastName = "Doe"
    Age = 30
}

// Copy-and-update
let olderPerson = { person with Age = 31 }

// Pattern matching on records
let getFullName person =
    match person with
    | { FirstName = f; LastName = l } -> $"{f} {l}"

// Shorter: destructuring
let getFullName' { FirstName = f; LastName = l } = $"{f} {l}"
```

### Discriminated Unions

```fsharp
// Simple union
type PaymentMethod =
    | Cash
    | CreditCard of cardNumber: string
    | DebitCard of cardNumber: string * pin: int

// Using unions
let processPayment method =
    match method with
    | Cash -> "Processing cash payment"
    | CreditCard cardNumber -> $"Processing credit card {cardNumber}"
    | DebitCard (cardNumber, _) -> $"Processing debit card {cardNumber}"

// Option type (built-in union)
type Option<'T> =
    | Some of 'T
    | None

// Result type (built-in union)
type Result<'T,'E> =
    | Ok of 'T
    | Error of 'E

// Using Option
let findPerson id =
    if id = 1 then
        Some { FirstName = "John"; LastName = "Doe"; Age = 30 }
    else
        None

// Using Result
let divide x y =
    if y = 0 then
        Error "Division by zero"
    else
        Ok (x / y)
```

### Single-Case Unions (Type Safety)

```fsharp
// Wrap primitives for type safety
type EmailAddress = EmailAddress of string
type CustomerId = CustomerId of int

let sendEmail (EmailAddress email) message =
    printfn $"Sending to {email}: {message}"

let getCustomer (CustomerId id) =
    // Can't accidentally pass wrong ID type
    printfn $"Fetching customer {id}"

// Usage prevents type confusion
let email = EmailAddress "test@example.com"
let customerId = CustomerId 123
sendEmail email "Hello"
// sendEmail customerId "Hello"  // Compile error!
```

---

## Pattern Matching

### Basic Matching

```fsharp
// Match on values
let describe x =
    match x with
    | 0 -> "zero"
    | 1 -> "one"
    | 2 -> "two"
    | n when n > 0 -> "positive"
    | _ -> "negative"

// Match on types
let processValue (value: obj) =
    match value with
    | :? string as s -> $"String: {s}"
    | :? int as i -> $"Int: {i}"
    | _ -> "Unknown type"

// Match on tuples
let point = (3, 4)
match point with
| (0, 0) -> "origin"
| (x, 0) -> $"on x-axis at {x}"
| (0, y) -> $"on y-axis at {y}"
| (x, y) -> $"at ({x}, {y})"
```

### Active Patterns

```fsharp
// Single-case active pattern
let (|Even|Odd|) n =
    if n % 2 = 0 then Even else Odd

match 42 with
| Even -> "even number"
| Odd -> "odd number"

// Partial active pattern
let (|Integer|_|) (str: string) =
    match System.Int32.TryParse(str) with
    | true, value -> Some value
    | false, _ -> None

match "123" with
| Integer n -> $"Number: {n}"
| _ -> "Not a number"

// Multi-case active pattern
let (|Small|Medium|Large|) n =
    if n < 10 then Small
    elif n < 100 then Medium
    else Large

match 42 with
| Small -> "small"
| Medium -> "medium"
| Large -> "large"
```

---

## Functions

### Function Basics

```fsharp
// Simple function
let add x y = x + y

// Type annotations (optional but recommended for public APIs)
let add' (x: int) (y: int) : int = x + y

// Anonymous function (lambda)
let doubled = List.map (fun x -> x * 2) [1; 2; 3]

// Recursive function
let rec factorial n =
    if n <= 1 then 1
    else n * factorial (n - 1)

// Tail-recursive function (optimized)
let factorial' n =
    let rec loop acc n =
        if n <= 1 then acc
        else loop (acc * n) (n - 1)
    loop 1 n
```

### Partial Application and Currying

```fsharp
// All F# functions are curried by default
let add x y = x + y
let add5 = add 5  // Partial application
add5 10  // Returns 15

// Use partial application for configurable functions
let greet greeting name = $"{greeting}, {name}!"
let sayHello = greet "Hello"
let sayHi = greet "Hi"

sayHello "Alice"  // "Hello, Alice!"
sayHi "Bob"       // "Hi, Bob!"
```

### Function Composition

```fsharp
// Forward composition (>>)
let add1 x = x + 1
let double x = x * 2
let add1ThenDouble = add1 >> double

add1ThenDouble 5  // Returns 12

// Backward composition (<<)
let doubleThenAdd1 = add1 << double
doubleThenAdd1 5  // Returns 11

// Pipe operator (|>)
let result =
    5
    |> add1
    |> double
    |> fun x -> x + 10

// Pipe backward (<|)
let sum = (+) <| 1 + 2  // Equivalent to (+) (1 + 2)
```

---

## Collections

### Lists

```fsharp
// List literals
let numbers = [1; 2; 3; 4; 5]
let moreNumbers = [1..10]
let evenNumbers = [2..2..10]

// Cons operator (::)
let newList = 0 :: numbers  // [0; 1; 2; 3; 4; 5]

// List comprehensions
let squares = [ for i in 1..10 -> i * i ]
let evens = [ for i in 1..20 do if i % 2 = 0 then yield i ]

// Common list functions
let doubled = List.map (fun x -> x * 2) numbers
let evens' = List.filter (fun x -> x % 2 = 0) numbers
let sum = List.fold (+) 0 numbers
let sum' = List.sum numbers
let product = List.reduce (*) numbers
```

### Arrays

```fsharp
// Array literals
let arr = [| 1; 2; 3; 4; 5 |]

// Array comprehension
let squares = [| for i in 1..10 -> i * i |]

// Mutable updates (in-place)
arr.[0] <- 10

// Array functions (similar to List)
let doubled = Array.map (fun x -> x * 2) arr
let evens = Array.filter (fun x -> x % 2 = 0) arr
```

### Sequences (Lazy)

```fsharp
// Infinite sequence
let naturals = Seq.initInfinite id  // 0, 1, 2, 3, ...

// Lazy evaluation
let expensiveSeq = seq {
    printfn "Computing..."
    for i in 1..5 do
        printfn $"Yielding {i}"
        yield i * i
}

// Only computed when enumerated
expensiveSeq |> Seq.take 3 |> Seq.toList
```

### Map and Set

```fsharp
// Map (immutable dictionary)
let ages = Map [ ("Alice", 30); ("Bob", 25) ]
let aliceAge = ages.["Alice"]  // 30
let aliceAge' = Map.tryFind "Alice" ages  // Some 30
let updatedAges = Map.add "Charlie" 35 ages

// Set (immutable)
let set1 = Set [1; 2; 3]
let set2 = Set [3; 4; 5]
let union = Set.union set1 set2  // {1, 2, 3, 4, 5}
let intersection = Set.intersect set1 set2  // {3}
```

---

## Computation Expressions

### Option Computation Expression

```fsharp
// Option workflow
type OptionBuilder() =
    member _.Bind(x, f) = Option.bind f x
    member _.Return(x) = Some x
    member _.ReturnFrom(x) = x

let option = OptionBuilder()

let validateAge age =
    option {
        let! validAge =
            if age >= 0 && age <= 120 then Some age
            else None
        return validAge
    }
```

### Result Computation Expression

```fsharp
// Result workflow
type ResultBuilder() =
    member _.Bind(x, f) = Result.bind f x
    member _.Return(x) = Ok x
    member _.ReturnFrom(x) = x

let result = ResultBuilder()

let divideBy x y =
    if y = 0 then Error "Division by zero"
    else Ok (x / y)

let calculate =
    result {
        let! a = divideBy 10 2   // Ok 5
        let! b = divideBy 20 4   // Ok 5
        let! c = divideBy a b    // Ok 1
        return c
    }
```

### Async Computation Expression

```fsharp
// Async workflow (built-in)
let fetchData url = async {
    printfn $"Fetching {url}..."
    do! Async.Sleep 1000
    return $"Data from {url}"
}

let processUrls urls = async {
    let! results =
        urls
        |> List.map fetchData
        |> Async.Parallel

    return results |> Array.toList
}

// Run async computation
let urls = ["url1"; "url2"; "url3"]
processUrls urls |> Async.RunSynchronously
```

---

## Type Providers

### CSV Type Provider

```fsharp
open FSharp.Data

// Type provider infers schema from sample
type StockData = CsvProvider<"stocks.csv">

let data = StockData.Load("stocks.csv")
for row in data.Rows do
    printfn $"{row.Date}: {row.Close}"
```

### JSON Type Provider

```fsharp
open FSharp.Data

// Infer from sample JSON
type Weather = JsonProvider<"""
{
    "temperature": 72,
    "condition": "sunny",
    "humidity": 65
}
""">

let weather = Weather.Load("weather.json")
printfn $"Temperature: {weather.Temperature}°F"
```

### SQL Type Provider

```fsharp
open FSharp.Data.Sql

type Sql = SqlDataProvider<
    ConnectionString = "Server=localhost;Database=mydb",
    DatabaseVendor = Common.DatabaseProviderTypes.MSSQLSERVER>

let ctx = Sql.GetDataContext()
let customers =
    query {
        for customer in ctx.Dbo.Customers do
        where (customer.Age > 18)
        select customer
    }
```

---

## Domain Modeling

### Making Illegal States Unrepresentable

```fsharp
// Bad: Can represent invalid states
type EmailContactBad = {
    EmailAddress: string option
    IsVerified: bool
}
// Problem: IsVerified can be true when EmailAddress is None

// Good: Invalid states impossible
type VerifiedEmail = VerifiedEmail of string
type UnverifiedEmail = UnverifiedEmail of string

type EmailContact =
    | Verified of VerifiedEmail
    | Unverified of UnverifiedEmail

// Can only verify an unverified email
let verify (UnverifiedEmail email) =
    // Verification logic...
    VerifiedEmail email
```

### Smart Constructors

```fsharp
// Constrained types with validation
type EmailAddress = private EmailAddress of string

module EmailAddress =
    let create (email: string) =
        if email.Contains("@") then
            Ok (EmailAddress email)
        else
            Error "Invalid email format"

    let value (EmailAddress email) = email

// Usage
match EmailAddress.create "test@example.com" with
| Ok email -> printfn $"Valid: {EmailAddress.value email}"
| Error msg -> printfn $"Error: {msg}"
```

### Units of Measure

```fsharp
// Define units
[<Measure>] type kg
[<Measure>] type m
[<Measure>] type s

// Type-safe calculations
let distance = 100.0<m>
let time = 10.0<s>
let speed = distance / time  // Type: float<m/s>

// Prevents mixing units
let mass = 50.0<kg>
// let invalid = distance + mass  // Compile error!

// Converting units
let metersToKilometers (x: float<m>) : float =
    float x / 1000.0
```

---

## Interop with C#

### Calling C# from F#

```fsharp
// Use C# classes naturally
open System.Collections.Generic

let dict = Dictionary<string, int>()
dict.Add("one", 1)
dict.Add("two", 2)

// LINQ extension methods
open System.Linq

let numbers = [1..10]
let evens = numbers.Where(fun x -> x % 2 = 0).ToList()
```

### Calling F# from C#

```fsharp
// Design F# types for C# consumption
namespace MyLibrary

// Use [<CLIMutable>] for record types
[<CLIMutable>]
type Person = {
    FirstName: string
    LastName: string
    Age: int
}

// Use classes for OO APIs
type PersonService() =
    member _.GetPerson(id: int) : Person option =
        Some { FirstName = "John"; LastName = "Doe"; Age = 30 }

    // Convert Option to nullable for C#
    member this.TryGetPerson(id: int) : Person =
        match this.GetPerson(id) with
        | Some p -> p
        | None -> Unchecked.defaultof<Person>
```

---

## Common Idioms

### Railway-Oriented Programming

```fsharp
// Chain operations that can fail
let validateName name =
    if String.IsNullOrWhiteSpace(name) then
        Error "Name cannot be empty"
    else
        Ok name

let validateAge age =
    if age >= 0 && age <= 120 then
        Ok age
    else
        Error "Invalid age"

let createPerson name age =
    result {
        let! validName = validateName name
        let! validAge = validateAge age
        return { FirstName = validName; LastName = ""; Age = validAge }
    }
```

### Dependency Injection (Reader Pattern)

```fsharp
// Pass dependencies explicitly
type Dependencies = {
    GetTime: unit -> System.DateTime
    Logger: string -> unit
}

let processOrder deps orderId =
    deps.Logger $"Processing order {orderId}"
    let timestamp = deps.GetTime()
    // ... rest of logic

// Usage
let deps = {
    GetTime = fun () -> System.DateTime.Now
    Logger = printfn "%s"
}

processOrder deps 123
```

### Event Sourcing Pattern

```fsharp
// Define events
type AccountEvent =
    | AccountOpened of customerId: string * initialBalance: decimal
    | MoneyDeposited of amount: decimal
    | MoneyWithdrawn of amount: decimal

// Apply events to state
type Account = { Balance: decimal }

let apply state event =
    match event with
    | AccountOpened (_, initialBalance) ->
        { Balance = initialBalance }
    | MoneyDeposited amount ->
        { state with Balance = state.Balance + amount }
    | MoneyWithdrawn amount ->
        { state with Balance = state.Balance - amount }

// Rebuild state from events
let buildState events =
    events |> List.fold apply { Balance = 0m }
```

---

## Troubleshooting

### Type Inference Issues

**Problem:** Compiler can't infer types

```fsharp
// Error: type inference failure
let processItems items =
    items |> List.map (fun x -> x.ToString())
```

**Fix:** Add type annotations
```fsharp
let processItems (items: int list) =
    items |> List.map (fun x -> x.ToString())
```

### Option/Result Unwrapping

**Problem:** Nested Option/Result types

```fsharp
// Bad: nested Some
let findAndProcess id =
    match find id with
    | Some person ->
        match process person with
        | Some result -> Some result
        | None -> None
    | None -> None
```

**Fix:** Use computation expressions or bind
```fsharp
let findAndProcess id =
    find id
    |> Option.bind process
```

### Mutable vs Immutable

**Problem:** Need to update values

```fsharp
// Doesn't work - records are immutable
let person = { FirstName = "John"; LastName = "Doe"; Age = 30 }
person.Age <- 31  // Error!
```

**Fix:** Use copy-and-update or mutable
```fsharp
// Functional: create new record
let olderPerson = { person with Age = 31 }

// Or use mutable if really needed
type MutablePerson = {
    FirstName: string
    LastName: string
    mutable Age: int
}
```

### Recursive Type Definitions

**Problem:** Types reference each other

```fsharp
// Error: types not defined yet
type Folder = { Name: string; Items: Item list }
type Item = File of string | Folder of Folder
```

**Fix:** Use `and` keyword
```fsharp
type Folder = { Name: string; Items: Item list }
and Item = File of string | Folder of Folder
```

---

## References

- [F# Language Reference](https://docs.microsoft.com/en-us/dotnet/fsharp/language-reference/)
- [F# for Fun and Profit](https://fsharpforfunandprofit.com/)
- [F# Style Guide](https://docs.microsoft.com/en-us/dotnet/fsharp/style-guide/)
- [Domain Modeling Made Functional](https://pragprog.com/titles/swdddf/domain-modeling-made-functional/)
