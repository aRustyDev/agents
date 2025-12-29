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

## Serialization

F# works seamlessly with .NET serialization libraries while maintaining functional idioms. For cross-language serialization patterns, see `patterns-serialization-dev`.

### System.Text.Json

```fsharp
open System.Text.Json
open System.Text.Json.Serialization

// Simple record serialization
type Person = {
    FirstName: string
    LastName: string
    Age: int
}

let person = { FirstName = "Alice"; LastName = "Smith"; Age = 30 }
let json = JsonSerializer.Serialize(person)
// {"FirstName":"Alice","LastName":"Smith","Age":30}

let parsed = JsonSerializer.Deserialize<Person>(json)

// Custom options
let options = JsonSerializerOptions()
options.PropertyNamingPolicy <- JsonNamingPolicy.CamelCase
options.WriteIndented <- true

let camelCaseJson = JsonSerializer.Serialize(person, options)
// {
//   "firstName": "alice",
//   "lastName": "smith",
//   "age": 30
// }
```

### JsonFSharpConverter for F# Types

```fsharp
open System.Text.Json
open System.Text.Json.Serialization

// Configure for F# discriminated unions and options
let options = JsonSerializerOptions()
options.Converters.Add(JsonFSharpConverter())

// Discriminated union serialization
type PaymentMethod =
    | Cash
    | CreditCard of cardNumber: string
    | DebitCard of cardNumber: string * pin: int

let payment = CreditCard "1234-5678-9012-3456"
let json = JsonSerializer.Serialize(payment, options)
// {"Case":"CreditCard","Fields":["1234-5678-9012-3456"]}

// Option type handling
type User = {
    Name: string
    Email: string option
}

let user = { Name = "Bob"; Email = Some "bob@example.com" }
let userJson = JsonSerializer.Serialize(user, options)
```

### Custom Converters

```fsharp
open System
open System.Text.Json
open System.Text.Json.Serialization

// Custom converter for EmailAddress
type EmailAddress = EmailAddress of string

type EmailAddressConverter() =
    inherit JsonConverter<EmailAddress>()

    override _.Read(reader, typeToConvert, options) =
        EmailAddress (reader.GetString())

    override _.Write(writer, value, options) =
        let (EmailAddress email) = value
        writer.WriteStringValue(email)

// Register converter
let options = JsonSerializerOptions()
options.Converters.Add(EmailAddressConverter())

let email = EmailAddress "test@example.com"
let json = JsonSerializer.Serialize(email, options)
// "test@example.com"
```

### FSharp.Json

```fsharp
open FSharp.Json

// Simple serialization
type Config = {
    Port: int
    Host: string
    Debug: bool
}

let config = { Port = 8080; Host = "localhost"; Debug = true }
let json = Json.serialize config
let parsed = Json.deserialize<Config> json

// Custom field names
type ApiResponse = {
    [<JsonField("response_code")>]
    ResponseCode: int

    [<JsonField("response_data")>]
    Data: string
}

// Transform during serialization
type Settings = {
    [<JsonField(Transform=typeof<Transforms.CamelCase>)>]
    DatabaseUrl: string

    [<JsonField(Transform=typeof<Transforms.SnakeCase>)>]
    MaxConnections: int
}
```

### Type Providers for JSON

```fsharp
open FSharp.Data

// Infer schema from sample JSON
type Weather = JsonProvider<"""
{
    "temperature": 72.5,
    "condition": "sunny",
    "humidity": 65,
    "forecast": [
        {"day": "Monday", "high": 75, "low": 60},
        {"day": "Tuesday", "high": 78, "low": 62}
    ]
}
""">

// Use with type safety
let weather = Weather.Load("weather.json")
printfn $"Temperature: {weather.Temperature}°F"
printfn $"Condition: {weather.Condition}"

weather.Forecast
|> Array.iter (fun day ->
    printfn $"{day.Day}: {day.High}°F / {day.Low}°F")

// From URL
let liveWeather = Weather.Load("https://api.weather.com/current")

// Parse from string
let jsonString = """{"temperature":68,"condition":"cloudy","humidity":70}"""
let parsed = Weather.Parse(jsonString)
```

### Validation Patterns

```fsharp
// Validation with Result
type ValidationError = string

let validateEmail (email: string) : Result<string, ValidationError> =
    if email.Contains("@") then
        Ok email
    else
        Error "Invalid email format"

let validateAge (age: int) : Result<int, ValidationError> =
    if age >= 0 && age <= 120 then
        Ok age
    else
        Error "Age must be between 0 and 120"

// Combine validations
type PersonData = {
    Name: string
    Email: string
    Age: int
}

let validatePerson data =
    result {
        let! validEmail = validateEmail data.Email
        let! validAge = validateAge data.Age
        return { data with Email = validEmail; Age = validAge }
    }

// Applicative validation (collect all errors)
type Validation<'T> = Result<'T, ValidationError list>

let validatePersonApplicative data : Validation<PersonData> =
    let validateName name =
        if String.IsNullOrWhiteSpace(name) then
            Error ["Name cannot be empty"]
        else
            Ok name

    match (validateName data.Name, validateEmail data.Email, validateAge data.Age) with
    | Ok n, Ok e, Ok a -> Ok { Name = n; Email = e; Age = a }
    | errors ->
        errors
        |> fun (n, e, a) ->
            [n; e; a]
            |> List.collect (function Error errs -> errs | Ok _ -> [])
        |> Error
```

---

## Build and Dependencies

F# uses the standard .NET build ecosystem with project files, NuGet packages, and the dotnet CLI.

### Project File (.fsproj)

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <OutputType>Exe</OutputType>
    <RootNamespace>MyApp</RootNamespace>
  </PropertyGroup>

  <ItemGroup>
    <!-- Order matters in F#! Files are compiled top-to-bottom -->
    <Compile Include="Types.fs" />
    <Compile Include="Helpers.fs" />
    <Compile Include="Domain.fs" />
    <Compile Include="Program.fs" />
  </ItemGroup>

  <ItemGroup>
    <PackageReference Include="FSharp.Data" Version="6.3.0" />
    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
  </ItemGroup>

</Project>
```

### dotnet CLI Commands

```bash
# Create new project
dotnet new console -lang F# -o MyApp
dotnet new classlib -lang F# -o MyLib
dotnet new webapi -lang F# -o MyApi

# Build and run
dotnet build
dotnet run
dotnet run -- arg1 arg2  # Pass arguments

# Watch mode (rebuild on file changes)
dotnet watch run

# Clean build artifacts
dotnet clean

# Restore packages
dotnet restore

# Create solution
dotnet new sln -n MySolution
dotnet sln add MyApp/MyApp.fsproj
dotnet sln add MyLib/MyLib.fsproj
```

### NuGet Package Management

```bash
# Add package
dotnet add package FSharp.Data
dotnet add package Newtonsoft.Json --version 13.0.3

# Remove package
dotnet remove package FSharp.Data

# Update package
dotnet add package FSharp.Data  # Gets latest

# List packages
dotnet list package

# List outdated packages
dotnet list package --outdated
```

### Package References in .fsproj

```xml
<ItemGroup>
  <!-- Exact version -->
  <PackageReference Include="FSharp.Core" Version="8.0.0" />

  <!-- Version range -->
  <PackageReference Include="FSharp.Data" Version="[6.0,7.0)" />

  <!-- Latest stable -->
  <PackageReference Include="Newtonsoft.Json" Version="*" />

  <!-- Development only -->
  <PackageReference Include="FsCheck" Version="2.16.5">
    <PrivateAssets>all</PrivateAssets>
  </PackageReference>
</ItemGroup>
```

### Project References

```xml
<!-- Reference another project -->
<ItemGroup>
  <ProjectReference Include="..\MyLib\MyLib.fsproj" />
</ItemGroup>
```

```bash
# Add project reference via CLI
dotnet add reference ../MyLib/MyLib.fsproj
```

### Paket (Alternative Package Manager)

```bash
# Install Paket
dotnet tool install paket

# Initialize Paket
dotnet paket init

# Add package
dotnet paket add FSharp.Data

# Install dependencies
dotnet paket install

# Update all packages
dotnet paket update
```

**paket.dependencies:**
```
source https://api.nuget.org/v3/index.json

nuget FSharp.Core >= 8.0
nuget FSharp.Data ~> 6.3
nuget Newtonsoft.Json

group Test
  nuget Expecto
  nuget FsCheck
```

**paket.references:**
```
FSharp.Data
Newtonsoft.Json

group Test
  Expecto
  FsCheck
```

### FAKE Build Script

```fsharp
// build.fsx
#r "paket:
nuget Fake.Core.Target
nuget Fake.DotNet.Cli //"
#load ".fake/build.fsx/intellisense.fsx"

open Fake.Core
open Fake.DotNet

let clean _ =
    !! "**/bin"
    ++ "**/obj"
    |> Shell.cleanDirs

let build _ =
    DotNet.build id ""

let test _ =
    DotNet.test id ""

let publish _ =
    DotNet.publish (fun opts ->
        { opts with
            Configuration = DotNet.BuildConfiguration.Release
            OutputPath = Some "./publish" }) ""

// Define targets
Target.create "Clean" clean
Target.create "Build" build
Target.create "Test" test
Target.create "Publish" publish

// Dependencies
open Fake.Core.TargetOperators

"Clean"
  ==> "Build"
  ==> "Test"
  ==> "Publish"

Target.runOrDefault "Build"
```

Run with:
```bash
dotnet fake build
dotnet fake build -t Publish
```

### Multi-Project Structure

```
MySolution/
├── MySolution.sln
├── src/
│   ├── MyApp/
│   │   ├── MyApp.fsproj
│   │   ├── Program.fs
│   │   └── Domain.fs
│   └── MyLib/
│       ├── MyLib.fsproj
│       ├── Types.fs
│       └── Utils.fs
├── tests/
│   └── MyApp.Tests/
│       ├── MyApp.Tests.fsproj
│       └── Tests.fs
├── paket.dependencies
└── build.fsx
```

### Publishing

```bash
# Publish for specific runtime
dotnet publish -r win-x64 -c Release
dotnet publish -r linux-x64 -c Release
dotnet publish -r osx-arm64 -c Release

# Self-contained (includes runtime)
dotnet publish -r linux-x64 -c Release --self-contained

# Framework-dependent (requires .NET runtime installed)
dotnet publish -c Release --no-self-contained

# Single file
dotnet publish -r linux-x64 -c Release /p:PublishSingleFile=true
```

### NuGet Package Creation

```xml
<!-- Add to .fsproj -->
<PropertyGroup>
  <PackageId>MyAwesomeLibrary</PackageId>
  <Version>1.0.0</Version>
  <Authors>Your Name</Authors>
  <Description>An awesome F# library</Description>
  <PackageLicenseExpression>MIT</PackageLicenseExpression>
  <RepositoryUrl>https://github.com/username/repo</RepositoryUrl>
</PropertyGroup>
```

```bash
# Create package
dotnet pack -c Release

# Publish to NuGet
dotnet nuget push bin/Release/MyAwesomeLibrary.1.0.0.nupkg --api-key YOUR_KEY --source https://api.nuget.org/v3/index.json
```

---

## Testing

F# has excellent testing support with Expecto, FsUnit, and FsCheck for property-based testing.

### Expecto

```fsharp
// Tests.fs
module Tests

open Expecto

// Simple test
let simpleTest =
    testCase "addition works" <| fun () ->
        let result = 1 + 1
        Expect.equal result 2 "1 + 1 should equal 2"

// Test list
let mathTests =
    testList "Math operations" [
        testCase "addition" <| fun () ->
            Expect.equal (2 + 2) 4 "2 + 2 = 4"

        testCase "subtraction" <| fun () ->
            Expect.equal (5 - 3) 2 "5 - 3 = 2"

        testCase "multiplication" <| fun () ->
            Expect.equal (3 * 4) 12 "3 * 4 = 12"
    ]

// Run all tests
[<EntryPoint>]
let main args =
    runTestsWithCLIArgs [] args mathTests
```

### Expecto Matchers

```fsharp
open Expecto

let expectTests =
    testList "Expecto expectations" [
        testCase "equal" <| fun () ->
            Expect.equal (1 + 1) 2 "should be equal"

        testCase "not equal" <| fun () ->
            Expect.notEqual 1 2 "should not be equal"

        testCase "is true" <| fun () ->
            Expect.isTrue (5 > 3) "5 should be greater than 3"

        testCase "is false" <| fun () ->
            Expect.isFalse (3 > 5) "3 should not be greater than 5"

        testCase "contains" <| fun () ->
            Expect.contains [1; 2; 3] 2 "list should contain 2"

        testCase "sequence equal" <| fun () ->
            Expect.sequenceEqual [1; 2; 3] [1; 2; 3] "sequences should match"

        testCase "throws" <| fun () ->
            Expect.throws (fun () -> failwith "boom") "should throw"

        testCase "is some" <| fun () ->
            Expect.isSome (Some 5) "should be Some"

        testCase "is none" <| fun () ->
            Expect.isNone None "should be None"
    ]
```

### Async and Task Testing

```fsharp
open Expecto

let asyncTests =
    testList "Async tests" [
        testCaseAsync "async computation" <| async {
            let! result = async { return 42 }
            Expect.equal result 42 "async result"
        }

        testTask "task computation" {
            let! result = task { return 42 }
            Expect.equal result 42 "task result"
        }
    ]
```

### Test Organization

```fsharp
// Nested test groups
let allTests =
    testList "All tests" [
        testList "Domain" [
            testList "User" [
                testCase "create user" <| fun () ->
                    let user = createUser "Alice" "alice@example.com"
                    Expect.equal user.Name "Alice" "name matches"
            ]
            testList "Order" [
                testCase "calculate total" <| fun () ->
                    let total = calculateTotal [10m; 20m; 30m]
                    Expect.equal total 60m "total is sum"
            ]
        ]
        testList "API" [
            // API tests
        ]
    ]

// Run with filters
[<EntryPoint>]
let main args =
    runTestsWithCLIArgs [] args allTests

// Run specific tests:
// dotnet run -- --filter "User"
```

### FsUnit with xUnit

```fsharp
module Tests

open Xunit
open FsUnit.Xunit

[<Fact>]
let ``2 + 2 should equal 4`` () =
    2 + 2 |> should equal 4

[<Fact>]
let ``list should contain element`` () =
    [1; 2; 3] |> should contain 2

[<Fact>]
let ``string should start with`` () =
    "hello world" |> should startWith "hello"

[<Fact>]
let ``option should be Some`` () =
    Some 5 |> should be (ofCase <@ Some @>)

[<Theory>]
[<InlineData(1, 2, 3)>]
[<InlineData(5, 5, 10)>]
[<InlineData(-1, 1, 0)>]
let ``addition works for multiple inputs`` a b expected =
    a + b |> should equal expected
```

### FsCheck Property-Based Testing

```fsharp
open Expecto
open FsCheck

// Property test with Expecto
let propertyTests =
    testList "Property tests" [
        testProperty "reverse twice equals original" <| fun (xs: int list) ->
            List.rev (List.rev xs) = xs

        testProperty "length of reverse equals length" <| fun (xs: int list) ->
            List.length (List.rev xs) = List.length xs

        testProperty "addition is commutative" <| fun (a: int) (b: int) ->
            a + b = b + a

        testProperty "list append length" <| fun (xs: int list) (ys: int list) ->
            List.length (xs @ ys) = List.length xs + List.length ys
    ]

// Custom generator
let positiveInt = Arb.generate<int> |> Gen.map abs

let customGeneratorTest =
    testProperty "square of positive is positive" <| fun () ->
        Prop.forAll (Arb.fromGen positiveInt) (fun n ->
            n * n >= 0)

// Conditional properties
let conditionalTest =
    testProperty "division by non-zero" <| fun (a: float) (b: float) ->
        b <> 0.0 ==> lazy (a / b * b = a)
```

### FsCheck with xUnit

```fsharp
open Xunit
open FsCheck
open FsCheck.Xunit

[<Property>]
let ``reverse twice gives original`` (xs: int list) =
    List.rev (List.rev xs) = xs

[<Property>]
let ``sort is idempotent`` (xs: int list) =
    List.sort (List.sort xs) = List.sort xs

[<Property(Arbitrary = [| typeof<CustomGenerators> |])>]
let ``custom generator property`` (email: string) =
    email.Contains("@")

// Custom generators
type CustomGenerators =
    static member Email() =
        let genEmail =
            gen {
                let! user = Gen.elements ["alice"; "bob"; "charlie"]
                let! domain = Gen.elements ["example.com"; "test.com"]
                return $"{user}@{domain}"
            }
        Arb.fromGen genEmail
```

### Test Setup and Teardown

```fsharp
open Expecto

// Setup/teardown pattern
let withDatabase test =
    let db = setupDatabase()  // Setup
    try
        test db
    finally
        cleanupDatabase db  // Teardown

let databaseTests =
    testList "Database tests" [
        testCase "insert user" <| fun () ->
            withDatabase (fun db ->
                insertUser db "Alice"
                let users = getUsers db
                Expect.contains users "Alice" "user should exist"
            )
    ]

// Shared fixture
type DatabaseFixture() =
    let db = setupDatabase()
    member _.Database = db
    interface System.IDisposable with
        member _.Dispose() = cleanupDatabase db

let fixtureTests =
    testSequenced <| testList "Sequenced tests" [
        let fixture = new DatabaseFixture()
        yield testCase "test 1" <| fun () ->
            // use fixture.Database
            ()
        yield testCase "test 2" <| fun () ->
            // use fixture.Database
            ()
    ]
```

### Mocking and Stubs

```fsharp
// Interface-based mocking
type IUserRepository =
    abstract member GetUser: int -> User option
    abstract member SaveUser: User -> unit

// Create stub for testing
let createStubRepository users =
    { new IUserRepository with
        member _.GetUser(id) =
            users |> List.tryFind (fun u -> u.Id = id)
        member _.SaveUser(user) =
            () // No-op for testing
    }

let testWithStub =
    testCase "get user from stub" <| fun () ->
        let users = [
            { Id = 1; Name = "Alice"; Email = "alice@example.com"; Age = 30 }
            { Id = 2; Name = "Bob"; Email = "bob@example.com"; Age = 25 }
        ]
        let repo = createStubRepository users
        let user = repo.GetUser(1)
        Expect.isSome user "should find user"
        Expect.equal user.Value.Name "Alice" "name should match"
```

### Running Tests

```bash
# Run with dotnet
dotnet run  # If entry point is defined
dotnet test  # If using xUnit/NUnit

# Expecto options
dotnet run -- --help
dotnet run -- --filter "User"
dotnet run -- --sequenced
dotnet run -- --debug
dotnet run -- --fail-on-focused-tests

# Watch mode
dotnet watch run
```

---

## Cross-Cutting Patterns

For cross-language comparison and translation patterns, see:

- `patterns-serialization-dev` - JSON/YAML handling, validation patterns
- `patterns-concurrency-dev` - Async workflows, parallel processing, Mailbox processors
- `patterns-metaprogramming-dev` - Type providers, computation expressions, quotations

---

## References

- [F# Language Reference](https://docs.microsoft.com/en-us/dotnet/fsharp/language-reference/)
- [F# for Fun and Profit](https://fsharpforfunandprofit.com/)
- [F# Style Guide](https://docs.microsoft.com/en-us/dotnet/fsharp/style-guide/)
- [Domain Modeling Made Functional](https://pragprog.com/titles/swdddf/domain-modeling-made-functional/)
