---
name: lang-fsharp-library-dev
description: F#-specific library development patterns. Use when creating F# libraries, designing functional APIs, configuring .fsproj and NuGet packages, writing XML documentation, ensuring C# interop, or publishing to NuGet. Extends meta-library-dev with F# tooling and functional idioms.
---

# F# Library Development

F#-specific patterns for library development. This skill extends `meta-library-dev` with F# tooling, functional API design, and .NET ecosystem practices.

## This Skill Extends

- `meta-library-dev` - Foundational library patterns (API design, versioning, testing strategies)
- `lang-fsharp-dev` - F# fundamentals (types, functions, computation expressions)

For general concepts like semantic versioning and testing pyramids, see `meta-library-dev`. For F# language basics, see `lang-fsharp-dev`.

## This Skill Adds

- **F# library tooling**: .fsproj configuration, NuGet packaging, .NET CLI
- **Functional API design**: Pure functions, immutability, type-driven design
- **F# ecosystem**: NuGet.org, FsDoc, C# interop, common dependencies
- **Documentation**: XML docs for IntelliSense, FsDoc for documentation sites

## This Skill Does NOT Cover

- General library patterns - see `meta-library-dev`
- F# language fundamentals - see `lang-fsharp-dev`
- Domain modeling details - see `lang-fsharp-domain-modeling-dev`
- Testing frameworks - see `lang-fsharp-testing-dev`
- Web API development - see `lang-fsharp-web-api-dev`

---

## Quick Reference

| Task | Command/Pattern |
|------|-----------------|
| New library project | `dotnet new classlib -lang F# -n MyLib` |
| Build | `dotnet build` |
| Test | `dotnet test` |
| Pack | `dotnet pack` |
| Publish (dry run) | `dotnet pack --no-build -o ./nupkg` |
| Publish to NuGet | `dotnet nuget push ./nupkg/*.nupkg` |
| Generate docs | `dotnet fsdocs build` |
| Watch mode | `dotnet watch build` |
| Clean | `dotnet clean` |

---

## Project File Structure (.fsproj)

### Required Fields for NuGet Publishing

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <!-- Target framework -->
    <TargetFramework>net8.0</TargetFramework>

    <!-- Package metadata -->
    <PackageId>MyCompany.MyLibrary</PackageId>
    <Version>1.0.0</Version>
    <Authors>Your Name</Authors>
    <Company>Your Company</Company>

    <!-- Required for NuGet.org -->
    <Description>A brief description of what this library does</Description>
    <PackageLicenseExpression>MIT</PackageLicenseExpression>
    <PackageProjectUrl>https://github.com/username/repo</PackageProjectUrl>
    <RepositoryUrl>https://github.com/username/repo</RepositoryUrl>
    <RepositoryType>git</RepositoryType>

    <!-- Recommended -->
    <PackageReadmeFile>README.md</PackageReadmeFile>
    <PackageTags>fsharp;functional;library</PackageTags>
    <PackageReleaseNotes>Initial release</PackageReleaseNotes>

    <!-- F# specific -->
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
    <WarnOn>3390;$(WarnOn)</WarnOn> <!-- Warn on missing XML docs -->
  </PropertyGroup>

  <!-- Include README in package -->
  <ItemGroup>
    <None Include="README.md" Pack="true" PackagePath="/" />
    <None Include="CHANGELOG.md" Pack="true" PackagePath="/" />
  </ItemGroup>
</Project>
```

### Multi-Targeting

```xml
<PropertyGroup>
  <!-- Support multiple frameworks -->
  <TargetFrameworks>net6.0;net7.0;net8.0</TargetFrameworks>
</PropertyGroup>

<!-- Conditional package references -->
<ItemGroup Condition="'$(TargetFramework)' == 'net6.0'">
  <PackageReference Include="SomePolyfill" Version="1.0.0" />
</ItemGroup>
```

### Source Files Order

```xml
<!-- Files must be in dependency order (F# requirement) -->
<ItemGroup>
  <Compile Include="Types.fs" />
  <Compile Include="Validation.fs" />
  <Compile Include="Core.fs" />
  <Compile Include="Api.fs" />
</ItemGroup>
```

---

## Standard Library Structure

```
MyLibrary/
├── src/
│   └── MyLibrary/
│       ├── MyLibrary.fsproj
│       ├── Types.fs           # Core types
│       ├── Validation.fs      # Validation logic
│       ├── Core.fs            # Core implementation
│       ├── Api.fs             # Public API
│       └── AssemblyInfo.fs    # Assembly metadata
├── tests/
│   └── MyLibrary.Tests/
│       ├── MyLibrary.Tests.fsproj
│       └── Tests.fs
├── docs/
│   └── index.md
├── README.md
├── CHANGELOG.md
├── LICENSE
└── .gitignore
```

### Module Organization Pattern

```fsharp
// Types.fs - Define core types first
namespace MyLibrary

/// Customer identifier
type CustomerId = CustomerId of int

/// Customer data
type Customer = {
    Id: CustomerId
    Name: string
    Email: string
}

/// Validation error
type ValidationError =
    | InvalidName of string
    | InvalidEmail of string


// Validation.fs - Validation logic
namespace MyLibrary

module Validation =

    /// Validate customer name
    let validateName name =
        if String.IsNullOrWhiteSpace(name) then
            Error (InvalidName "Name cannot be empty")
        else
            Ok name

    /// Validate email format
    let validateEmail email =
        if email.Contains("@") then
            Ok email
        else
            Error (InvalidEmail "Invalid email format")


// Core.fs - Core implementation
namespace MyLibrary

module Core =

    /// Create a customer with validation
    let createCustomer id name email =
        result {
            let! validName = Validation.validateName name
            let! validEmail = Validation.validateEmail email
            return {
                Id = CustomerId id
                Name = validName
                Email = validEmail
            }
        }


// Api.fs - Public API surface
namespace MyLibrary

/// Public API for customer operations
[<RequireQualifiedAccess>]
module Customer =

    /// Create a new customer
    let create id name email =
        Core.createCustomer id name email

    /// Get customer ID
    let getId (customer: Customer) =
        let (CustomerId id) = customer.Id
        id
```

---

## Functional API Design Patterns

### 1. Use Discriminated Unions for State

```fsharp
/// Explicit states prevent invalid combinations
type EmailAddress =
    | Unverified of string
    | Verified of string * verifiedAt: System.DateTime

/// API clearly shows state transitions
module Email =

    /// Send verification email
    let sendVerification (Unverified email) =
        // Send email logic
        email

    /// Verify email with token
    let verify token (Unverified email) =
        // Verify logic
        Verified (email, System.DateTime.UtcNow)

    /// Can only send to verified emails
    let sendTo message (Verified (email, _)) =
        // Send message
        ()
```

### 2. Smart Constructors with Validation

```fsharp
/// Email address with private constructor
type EmailAddress = private EmailAddress of string

/// Public module for creating emails
module EmailAddress =

    /// Create email with validation
    let create (email: string) : Result<EmailAddress, string> =
        if email.Contains("@") && email.Contains(".") then
            Ok (EmailAddress email)
        else
            Error "Invalid email format"

    /// Get string value
    let value (EmailAddress email) = email

    /// Try parse from string
    let tryParse str =
        match create str with
        | Ok email -> Some email
        | Error _ -> None

// Usage prevents invalid emails
let result = EmailAddress.create "user@example.com"
```

### 3. Builder Pattern (F# Style)

```fsharp
/// Configuration with defaults
type HttpConfig = {
    BaseUrl: string
    Timeout: System.TimeSpan
    RetryCount: int
    Headers: Map<string, string>
}

/// Builder module
module HttpConfig =

    /// Default configuration
    let defaults = {
        BaseUrl = "https://api.example.com"
        Timeout = System.TimeSpan.FromSeconds(30.0)
        RetryCount = 3
        Headers = Map.empty
    }

    /// Set base URL
    let withBaseUrl url config =
        { config with BaseUrl = url }

    /// Set timeout
    let withTimeout timeout config =
        { config with Timeout = timeout }

    /// Add header
    let withHeader key value config =
        { config with Headers = Map.add key value config.Headers }

// Usage with pipe operator
let config =
    HttpConfig.defaults
    |> HttpConfig.withBaseUrl "https://myapi.com"
    |> HttpConfig.withTimeout (System.TimeSpan.FromSeconds(60.0))
    |> HttpConfig.withHeader "Authorization" "Bearer token"
```

### 4. Result-Oriented Error Handling

```fsharp
/// Domain-specific errors
type LibraryError =
    | ValidationFailed of field: string * message: string
    | NotFound of entity: string * id: string
    | NetworkError of exn
    | Unauthorized

/// Return Result types from public APIs
module Api =

    /// Fetch user by ID
    let getUser (userId: string) : Result<User, LibraryError> =
        try
            match Database.tryFind userId with
            | Some user -> Ok user
            | None -> Error (NotFound ("User", userId))
        with
        | :? System.Net.WebException as ex ->
            Error (NetworkError ex)

    /// Chain operations with result computation expression
    let getUserEmail userId =
        result {
            let! user = getUser userId
            let! email = validateEmail user.Email
            return email
        }
```

### 5. Extension Methods for C# Interop

```fsharp
namespace MyLibrary

open System.Runtime.CompilerServices

/// Extension methods for C# consumption
[<Extension>]
type CustomerExtensions =

    /// Convert Option to nullable for C#
    [<Extension>]
    static member ToNullable(option: Option<'T>) =
        match option with
        | Some value -> System.Nullable(value)
        | None -> System.Nullable()

    /// Convert Result to exception-based for C#
    [<Extension>]
    static member GetOrThrow(result: Result<'T, 'E>) =
        match result with
        | Ok value -> value
        | Error error -> failwith (error.ToString())

// C# can now use: var result = GetUser(id).ToNullable()
```

---

## C# Interop Best Practices

### Making F# Types C#-Friendly

```fsharp
namespace MyLibrary

// 1. Use [<CLIMutable>] for records used in C#
[<CLIMutable>]
type Customer = {
    Id: int
    Name: string
    Email: string
}

// 2. Hide F# Option from C# APIs
type CustomerService() =

    /// F#-friendly API
    member _.TryGetCustomer(id: int) : Customer option =
        // Implementation
        None

    /// C#-friendly API (returns null instead of None)
    member this.GetCustomer(id: int) : Customer =
        match this.TryGetCustomer(id) with
        | Some customer -> customer
        | None -> null

// 3. Provide tuple-based tryParse pattern for C#
module CustomerId =

    /// F# API
    let tryParse (str: string) : CustomerId option =
        match System.Int32.TryParse(str) with
        | true, id -> Some (CustomerId id)
        | false, _ -> None

    /// C# API (out parameter pattern)
    let TryParse(str: string, [<System.Runtime.InteropServices.Out>] result: byref<CustomerId>) =
        match tryParse str with
        | Some id ->
            result <- id
            true
        | None -> false
```

### Async/Task Interop

```fsharp
open System.Threading.Tasks

/// Provide both Async and Task APIs
type DataService() =

    /// F#-friendly Async
    member _.FetchDataAsync(url: string) : Async<string> =
        async {
            // Implementation
            return "data"
        }

    /// C#-friendly Task
    member this.FetchDataTask(url: string) : Task<string> =
        this.FetchDataAsync(url)
        |> Async.StartAsTask
```

### Nullability Annotations for C# 8.0+

```fsharp
// Enable nullable reference types
#nowarn "3391" // Suppress nullable warnings if needed

open System.Diagnostics.CodeAnalysis

type Api() =

    /// Mark return as never null
    [<return: NotNull>]
    member _.GetRequiredValue() : string =
        "always returns a value"

    /// Mark return as maybe null
    [<return: MaybeNull>]
    member _.GetOptionalValue() : string =
        null
```

---

## XML Documentation

### Documentation Comments

```fsharp
/// <summary>
/// Represents a customer in the system.
/// </summary>
/// <remarks>
/// Customers must have a unique ID and valid email address.
/// </remarks>
type Customer = {
    /// <summary>The unique customer identifier</summary>
    Id: CustomerId

    /// <summary>The customer's full name</summary>
    Name: string

    /// <summary>The customer's email address</summary>
    Email: string
}

/// <summary>
/// Creates a new customer with validation.
/// </summary>
/// <param name="id">The customer ID</param>
/// <param name="name">The customer name</param>
/// <param name="email">The customer email</param>
/// <returns>
/// Ok with Customer if validation succeeds, Error with ValidationError otherwise
/// </returns>
/// <example>
/// <code>
/// match Customer.create 1 "John Doe" "john@example.com" with
/// | Ok customer -> printfn "Created: %s" customer.Name
/// | Error error -> printfn "Error: %A" error
/// </code>
/// </example>
let create id name email =
    Core.createCustomer id name email

/// <summary>
/// Gets the customer ID as an integer.
/// </summary>
/// <param name="customer">The customer</param>
/// <returns>The customer ID as int</returns>
/// <exception cref="System.ArgumentNullException">
/// Thrown when customer is null
/// </exception>
let getId (customer: Customer) =
    let (CustomerId id) = customer.Id
    id
```

### FsDoc Documentation

```fsharp
// Install FsDoc: dotnet tool install -g fsdocs-tool

// Create docs/index.md
(**
# My Library

This library provides functional APIs for customer management.

## Quick Start

    open MyLibrary

    let result = Customer.create 1 "John" "john@example.com"

## Features

- Type-safe customer validation
- Immutable data structures
- C# interop support
*)

// Generate docs
// dotnet fsdocs build --input docs --output docs/_site
```

---

## Package Configuration

### NuGet Package Best Practices

```xml
<PropertyGroup>
  <!-- Symbols package for debugging -->
  <IncludeSymbols>true</IncludeSymbols>
  <SymbolPackageFormat>snupkg</SymbolPackageFormat>

  <!-- Source link for GitHub -->
  <PublishRepositoryUrl>true</PublishRepositoryUrl>
  <EmbedUntrackedSources>true</EmbedUntrackedSources>

  <!-- Deterministic builds -->
  <ContinuousIntegrationBuild Condition="'$(CI)' == 'true'">true</ContinuousIntegrationBuild>

  <!-- Nullable reference types -->
  <Nullable>enable</Nullable>
</PropertyGroup>

<ItemGroup>
  <PackageReference Include="Microsoft.SourceLink.GitHub" Version="8.0.0" PrivateAssets="All" />
</ItemGroup>
```

### Icon and README

```xml
<PropertyGroup>
  <!-- Package icon -->
  <PackageIcon>icon.png</PackageIcon>
  <PackageIconUrl>https://example.com/icon.png</PackageIconUrl>

  <!-- README -->
  <PackageReadmeFile>README.md</PackageReadmeFile>
</PropertyGroup>

<ItemGroup>
  <None Include="../../icon.png" Pack="true" PackagePath="/" />
  <None Include="../../README.md" Pack="true" PackagePath="/" />
</ItemGroup>
```

---

## Testing Patterns

### Unit Tests with Expecto

```fsharp
// Install: dotnet add package Expecto

module Tests

open Expecto
open MyLibrary

[<Tests>]
let customerTests =
    testList "Customer" [
        test "create with valid data succeeds" {
            let result = Customer.create 1 "John Doe" "john@example.com"
            Expect.isOk result "Should succeed with valid data"
        }

        test "create with invalid email fails" {
            let result = Customer.create 1 "John Doe" "invalid"
            Expect.isError result "Should fail with invalid email"
        }

        testProperty "getId returns original id" <| fun id ->
            match Customer.create id "Name" "email@test.com" with
            | Ok customer ->
                let retrievedId = Customer.getId customer
                Expect.equal retrievedId id "IDs should match"
            | Error _ -> ()
    ]

[<EntryPoint>]
let main args =
    runTestsWithArgs defaultConfig args customerTests
```

### Property-Based Testing with FsCheck

```fsharp
// Install: dotnet add package FsCheck

open FsCheck
open Expecto

let validEmailGen =
    gen {
        let! name = Arb.generate<string>
        let! domain = Arb.generate<string>
        return $"{name}@{domain}.com"
    }

[<Tests>]
let propertyTests =
    testList "Properties" [
        testProperty "email validation roundtrip" <| fun () ->
            Prop.forAll (Arb.fromGen validEmailGen) (fun email ->
                match EmailAddress.create email with
                | Ok addr ->
                    EmailAddress.value addr = email
                | Error _ ->
                    not (email.Contains("@"))
            )
    ]
```

---

## Publishing Workflow

### Pre-Publish Checklist

- [ ] `dotnet build` succeeds without warnings
- [ ] `dotnet test` all tests pass
- [ ] `dotnet pack` creates package successfully
- [ ] Version bumped in .fsproj
- [ ] CHANGELOG.md updated
- [ ] README.md is current
- [ ] XML documentation complete (no 3390 warnings)
- [ ] All required NuGet metadata present
- [ ] LICENSE file included
- [ ] Icon and README included in package
- [ ] Tested on all target frameworks

### Publishing Commands

```bash
# Build in release mode
dotnet build -c Release

# Run tests
dotnet test -c Release

# Create NuGet package
dotnet pack -c Release -o ./nupkg

# Publish to NuGet.org (requires API key)
dotnet nuget push ./nupkg/*.nupkg --api-key $NUGET_API_KEY --source https://api.nuget.org/v3/index.json

# Or use local NuGet.config
dotnet nuget push ./nupkg/*.nupkg --source nuget.org
```

### Versioning Strategy

```xml
<!-- Use semantic versioning -->
<PropertyGroup>
  <Version>1.2.3</Version>
  <!-- Or separate parts -->
  <VersionPrefix>1.2.3</VersionPrefix>
  <VersionSuffix>beta1</VersionSuffix>
  <!-- Results in: 1.2.3-beta1 -->
</PropertyGroup>
```

---

## Common Dependencies

### Core Libraries

```xml
<ItemGroup>
  <!-- Result computation expressions -->
  <PackageReference Include="FSharp.Core" Version="8.0.0" />

  <!-- Functional data structures -->
  <PackageReference Include="FSharpPlus" Version="1.5.0" />
</ItemGroup>
```

### Serialization

```xml
<ItemGroup>
  <!-- JSON serialization -->
  <PackageReference Include="System.Text.Json" Version="8.0.0" />
  <!-- Or Newtonsoft.Json for F# types -->
  <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
  <PackageReference Include="FSharp.SystemTextJson" Version="1.3.13" />
</ItemGroup>
```

### Validation

```xml
<ItemGroup>
  <!-- Railway-oriented programming -->
  <PackageReference Include="FsToolkit.ErrorHandling" Version="4.15.1" />
</ItemGroup>
```

### Documentation

```xml
<ItemGroup>
  <!-- Generate documentation site -->
  <PackageReference Include="FSharp.Formatting" Version="14.0.1" />
</ItemGroup>
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Build and Publish

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'

      - name: Restore
        run: dotnet restore

      - name: Build
        run: dotnet build -c Release --no-restore

      - name: Test
        run: dotnet test -c Release --no-build

      - name: Pack
        run: dotnet pack -c Release --no-build -o ./nupkg

      - name: Publish to NuGet
        if: startsWith(github.ref, 'refs/tags/v')
        run: dotnet nuget push ./nupkg/*.nupkg --api-key ${{ secrets.NUGET_API_KEY }} --source https://api.nuget.org/v3/index.json
```

---

## Anti-Patterns

### 1. Exposing Mutable State

```fsharp
// Bad: Mutable field in public API
type BadConfig() =
    let mutable timeout = 30
    member _.Timeout
        with get() = timeout
        and set(value) = timeout <- value

// Good: Immutable with copy-and-update
type GoodConfig = {
    Timeout: int
}

module GoodConfig =
    let defaults = { Timeout = 30 }
    let withTimeout timeout config = { config with Timeout = timeout }
```

### 2. Exception-Based Error Handling

```fsharp
// Bad: Exceptions in library code
let parseCustomer data =
    if data.Name = "" then
        failwith "Invalid name"
    // ...

// Good: Result type
let parseCustomer data =
    if data.Name = "" then
        Error (ValidationError "Invalid name")
    else
        Ok { Id = data.Id; Name = data.Name }
```

### 3. Stringly-Typed APIs

```fsharp
// Bad: String-based state
type Status = string
let pending: Status = "pending"
let completed: Status = "completed"

// Good: Discriminated union
type Status =
    | Pending
    | InProgress of startTime: System.DateTime
    | Completed of result: string
```

### 4. Mixing F# and C# Idioms

```fsharp
// Bad: Using C# patterns in F# library
type CustomerRepository() =
    member _.GetAsync(id: int) : Task<Customer option> =
        task {
            // Implementation
            return None
        }

// Good: Provide both F# and C# APIs
type CustomerRepository() =

    // F# API
    member _.tryGetAsync(id: int) : Async<Customer option> =
        async {
            // Implementation
            return None
        }

    // C# API
    member this.GetAsync(id: int) : Task<Customer> =
        async {
            match! this.tryGetAsync(id) with
            | Some customer -> return customer
            | None -> return null
        }
        |> Async.StartAsTask
```

---

## Performance Considerations

### Tail Recursion

```fsharp
// Bad: Stack overflow for large lists
let rec sum list =
    match list with
    | [] -> 0
    | head :: tail -> head + sum tail

// Good: Tail-recursive
let sum list =
    let rec loop acc remaining =
        match remaining with
        | [] -> acc
        | head :: tail -> loop (acc + head) tail
    loop 0 list
```

### Struct Records for Performance

```fsharp
// Use structs for small, frequently-allocated types
[<Struct>]
type Point = {
    X: float
    Y: float
}

// Avoids heap allocation
let distance p1 p2 =
    let dx = p2.X - p1.X
    let dy = p2.Y - p1.Y
    sqrt (dx * dx + dy * dy)
```

### Sequence Laziness

```fsharp
// Prefer lazy sequences for large data
let processLargeDataset () =
    File.ReadLines("large-file.txt")
    |> Seq.filter isValid
    |> Seq.map transform
    |> Seq.take 100
    |> Seq.toList
// Only reads first 100 valid items
```

---

## References

- `meta-library-dev` - Foundational library patterns
- `lang-fsharp-dev` - F# language fundamentals
- [F# Component Design Guidelines](https://docs.microsoft.com/en-us/dotnet/fsharp/style-guide/component-design-guidelines)
- [NuGet Package Publishing](https://docs.microsoft.com/en-us/nuget/create-packages/publish-a-package)
- [FsDoc Documentation](https://fsprojects.github.io/FSharp.Formatting/)
- [FsToolkit.ErrorHandling](https://github.com/demystifyfp/FsToolkit.ErrorHandling)
