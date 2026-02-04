# F#

> Functional-first programming language for .NET with strong typing and succinct syntax.

## Overview

F# is a functional-first, general-purpose programming language developed by Microsoft Research, first released in 2005. It runs on .NET and combines functional programming with object-oriented and imperative features, emphasizing immutability, type inference, and concise syntax.

F# pioneered several features later adopted by C#, including async/await, pattern matching, and discriminated unions. It offers excellent interoperability with the entire .NET ecosystem while maintaining a functional programming style.

The language is particularly strong in data science, finance, web development (via Fable for JavaScript), and domain modeling with its powerful type system.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | ML-FP | OCaml-derived, ML heritage |
| Secondary Family | OOP | .NET object system |
| Subtype | hybrid | Functional-first, multi-paradigm |

See: [ML-FP Family](../language-families/ml-fp.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| 4.0 | 2015-07 | Provided methods, extended members |
| 5.0 | 2020-11 | String interpolation, nameof |
| 6.0 | 2021-11 | Task expressions, implicit conversions |
| 7.0 | 2022-11 | Static abstract interface members |
| 8.0 | 2023-11 | Nested record patterns, copy/update improvements |

## Feature Profile

### Type System

- **Strength:** strong (static, sound type system)
- **Inference:** bidirectional (Hindley-Milner)
- **Generics:** bounded (constraints, statically resolved type parameters)
- **Nullability:** explicit (Option<'a>, reference types nullable with .NET 8)

### Memory Model

- **Management:** gc (.NET garbage collection)
- **Mutability:** default-immutable (let, mutable keyword required)
- **Allocation:** heap (.NET managed heap)

### Control Flow

- **Structured:** if-else, match, for, while, try-with
- **Effects:** exceptions (Result for functional), Computation Expressions
- **Async:** async/task computation expressions

### Data Types

- **Primitives:** int, float, bool, char, string, unit
- **Composites:** records, discriminated unions, tuples, structs
- **Collections:** list, array, seq, Map, Set
- **Abstraction:** modules, classes, interfaces, type providers

### Metaprogramming

- **Macros:** none (type providers for code gen)
- **Reflection:** runtime (.NET reflection)
- **Code generation:** Type Providers (compile-time), quotations

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | NuGet, Paket | NuGet is standard |
| Build System | dotnet CLI, FAKE | MSBuild-based |
| LSP | Ionide, FsAutoComplete | Ionide for VS Code |
| Formatter | Fantomas | Opinionated |
| Linter | FSharpLint | Community maintained |
| REPL | F# Interactive (fsi) | Built-in |
| Test Framework | Expecto, xUnit, NUnit | Expecto is FP-friendly |

## Syntax Patterns

```fsharp
// Function definition
let greet name times =
    String.replicate times $"Hello, {name}! "

// Generic function
let identity (x: 'a) : 'a = x

// Async function (task expression)
let fetchData (url: string) : Task<Response> = task {
    let! response = httpClient.GetAsync(url)
    if response.StatusCode <> HttpStatusCode.OK then
        raise (HttpException response.StatusCode)
    return response
}

// Record type
type User = {
    Id: string
    Name: string
    Email: string option
}

// Discriminated union (ADT)
type Result<'T, 'E> =
    | Ok of 'T
    | Error of 'E

type Shape =
    | Circle of radius: float
    | Rectangle of width: float * height: float

// Pattern matching
let area shape =
    match shape with
    | Circle r -> Math.PI * r * r
    | Rectangle (w, h) -> w * h

// Active patterns
let (|Even|Odd|) n =
    if n % 2 = 0 then Even else Odd

let describe n =
    match n with
    | Even -> "even"
    | Odd -> "odd"

// Computation expression (result builder)
let divide a b = result {
    if b = 0 then
        return! Error "Division by zero"
    else
        return a / b
}

// Pipeline operator
let processNumbers numbers =
    numbers
    |> List.filter (fun x -> x > 0)
    |> List.map (fun x -> x * 2)
    |> List.sum

// Composition operator
let processAll = List.filter isValid >> List.map transform >> List.sum

// List comprehension (sequence expression)
let evenSquares xs = [
    for x in xs do
        if x % 2 = 0 then
            yield x * x
]

// Error handling
let tryDivide a b =
    try
        Ok (a / b)
    with
    | :? DivideByZeroException -> Error "Division by zero"

// Module definition
module UserService =
    let create name email =
        { Id = Guid.NewGuid().ToString()
          Name = name
          Email = Some email }

    let validate user =
        if String.IsNullOrEmpty user.Name then
            Error "Name required"
        else
            Ok user

// Type extension
type String with
    member this.Words = this.Split(' ') |> Array.toList
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| .NET null leaks into F# | moderate | Use Option, enable nullable reference types |
| Mutable by default in .NET interop | minor | Wrap in F# types, use immutable interfaces |
| Limited higher-kinded types | moderate | Use computation expressions, type classes via SRTP |
| No pattern matching in lambdas | minor | Use match expression, function keyword |
| Type providers require VS/Windows (some) | minor | Use cross-platform providers |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 3 | fsharp-haskell, fsharp-roc, fsharp-scala |
| As Target | 5 | python-fsharp, elixir-fsharp, clojure-fsharp, elm-fsharp, erlang-fsharp |

**Note:** Bridge between FP and .NET worlds.

## Idiomatic Patterns

### Discriminated Unions → ADTs

```fsharp
// F#: discriminated union
type Option<'a> =
    | Some of 'a
    | None

// IR equivalent: enum/ADT
// enum Option<T> { Some(T), None }
```

### Pipeline Operator → Method Chaining

```fsharp
// F#: pipeline
x |> f |> g |> h

// IR equivalent: method chain or composition
// h(g(f(x))) or x.f().g().h()
```

### Computation Expressions → Monadic Operations

```fsharp
// F#: async computation expression
async {
    let! x = getX()
    let! y = getY(x)
    return combine x y
}

// IR equivalent: monadic bind
// getX().flatMap(x => getY(x).map(y => combine(x, y)))
```

### Active Patterns → Custom Extractors

```fsharp
// F#: active pattern
let (|ParseInt|_|) s =
    match Int32.TryParse s with
    | true, n -> Some n
    | _ -> None

// IR equivalent: extractor/unapply
// object ParseInt { def unapply(s: String): Option[Int] }
```

## Related Languages

- **Influenced by:** OCaml, ML, Haskell, C#
- **Influenced:** C# (many features), Scala
- **Compiles to:** .NET IL, JavaScript (Fable)
- **FFI compatible:** C# (native), .NET ecosystem

## Sources

- [F# Language Reference](https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/)
- [F# Core Library](https://fsharp.github.io/fsharp-core-docs/)
- [F# for Fun and Profit](https://fsharpforfunandprofit.com/)
- [F# Software Foundation](https://fsharp.org/)

## See Also

- [ML-FP Family](../language-families/ml-fp.md)
- [Haskell](haskell.md) - Pure FP comparison
- [Scala](scala.md) - Hybrid FP alternative
- [OCaml](ocaml.md) - Direct ancestor
