---
name: lang-roc-library-dev
description: Roc-specific library and platform development patterns. Use when creating reusable Roc packages, developing custom platforms, organizing package modules, exposing public APIs, managing platform interfaces, or publishing packages. Extends meta-library-dev with Roc's unique platform system and module patterns.
created: 2025-12-28T22:00
updated: 2025-12-28T22:00
tags: [lang, roc, library, dev]
source: arustydev/agents
---

# Roc Library Development

Roc-specific patterns for library package and platform development. This skill extends `meta-library-dev` with Roc's unique platform architecture, package system, and module organization.

## This Skill Extends

- `meta-library-dev` - Foundational library patterns (API design, versioning, testing strategies)

For general concepts like semantic versioning, module organization principles, and testing pyramids, see the meta-skill first.

## This Skill Adds

- **Roc platform system**: Platform development, app/platform separation, I/O interfaces
- **Package organization**: Module structure, package declarations, visibility patterns
- **Roc idioms**: Pure functional patterns, platform interfaces, type inference
- **Roc ecosystem**: Standard library modules, builtin modules, platform conventions

## This Skill Does NOT Cover

- General library patterns - see `meta-library-dev`
- Roc application development - focus is on reusable packages/platforms
- Roc-specific syntax basics - see language documentation
- CLI application development - see CLI-specific skills

---

## Overview

Roc has a unique architecture that separates applications from platforms:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Roc Package Architecture                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────┐                                              │
│  │  Application  │  (your code)                                 │
│  │    (.roc)     │                                              │
│  └───────┬───────┘                                              │
│          │                                                      │
│          │ imports                                              │
│          ▼                                                      │
│  ┌───────────────┐                                              │
│  │    Package    │  (reusable modules)                          │
│  │  package {}   │                                              │
│  └───────┬───────┘                                              │
│          │                                                      │
│          │ depends on                                           │
│          ▼                                                      │
│  ┌───────────────┐         ┌──────────────┐                    │
│  │   Platform    │────────▶│  Runtime     │                    │
│  │  platform {}  │         │  (Rust, C)   │                    │
│  └───────────────┘         └──────────────┘                    │
│          │                                                      │
│          └─ Provides I/O primitives (no I/O in stdlib)         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Key Concepts:**

| Concept | Purpose | I/O Allowed |
|---------|---------|-------------|
| **Package** | Reusable modules (pure functions/types) | No |
| **Platform** | Runtime + I/O primitives | Yes |
| **App** | Executable application | Yes (via platform) |
| **Module** | Single .roc file with exports | No (unless platform) |

**This skill focuses on creating Packages and Platforms for reuse.**

---

## Quick Reference

### File Types

| Type | Declaration | Purpose |
|------|-------------|---------|
| `app` | `app [main] { ... }` | Executable application |
| `package` | `package [Module1, Module2] { ... }` | Reusable package |
| `platform` | `platform "name" requires {} exposes {} packages {} ...` | Platform for apps |
| `module` | `module [export1, export2]` | Single module file |

### Common Commands

| Command | Description |
|---------|-------------|
| `roc check` | Type-check without building |
| `roc build` | Build executable |
| `roc test` | Run tests |
| `roc format` | Format code |
| `roc docs` | Generate documentation |

---

## Package Development

### Package Structure

```
my-package/
├── package/
│   ├── main.roc           # Package entry point
│   ├── Parser.roc         # Module files
│   ├── Types.roc
│   └── Internal.roc
├── examples/
│   └── basic.roc          # Example apps
├── platform/              # Optional: custom platform
│   └── main.roc
└── README.md
```

### Package Declaration

**package/main.roc:**
```roc
package [
    # Public modules (exposed to users)
    Parser,
    Types,
    # Can also expose specific values
    parseConfig,
    defaultConfig,
]
```

**Key Principles:**
1. Only expose what users need (minimal public API)
2. Keep implementation modules private
3. Re-export common types/functions at package level
4. Use descriptive module names

### Module Structure

**package/Parser.roc:**
```roc
module [
    # Public API
    parse,
    parseWithConfig,
    Config,
    ParseError,
]

import Types exposing [Document, Metadata]
import Internal  # Private import, not exposed

## Parse a document string.
##
## ```roc
## result = parse "# Title\nContent"
## expect result == Ok { title: "Title", content: "Content" }
## ```
parse : Str -> Result Document ParseError
parse = \input ->
    parseWithConfig input defaultConfig

## Configuration for parsing.
Config : {
    strict : Bool,
    preserveWhitespace : Bool,
}

defaultConfig : Config
defaultConfig = {
    strict: Bool.false,
    preserveWhitespace: Bool.false,
}

## Parse with custom configuration.
parseWithConfig : Str, Config -> Result Document ParseError
parseWithConfig = \input, config ->
    # Implementation
    # ...
```

### Visibility Patterns

**Module-level visibility:**
```roc
module [
    # Public: Anyone importing this module can use these
    publicFunction,
    PublicType,
]

# Private: Only visible within this module
privateHelper : Str -> Str
privateHelper = \x -> x

# Public functions can call private helpers
publicFunction : Str -> Str
publicFunction = \input ->
    privateHelper input
```

**Package-level visibility:**
```roc
# main.roc
package [
    # These modules are visible to package users
    Parser,
    Types,
]

# Internal is NOT in package exports = private to package
import Internal
```

---

## Platform Development

### Platform Structure

```
my-platform/
├── platform/
│   └── main.roc           # Platform declaration
├── host/
│   ├── Cargo.toml         # Rust host implementation
│   └── src/
│       ├── lib.rs
│       └── main.rs
└── examples/
    └── hello.roc
```

### Platform Declaration

**platform/main.roc:**
```roc
platform "cli"
    requires { Model } { main : Task Model [] }
    exposes [
        Task,
        Stdout,
        Stdin,
        File,
        Path,
        Env,
    ]
    packages {}
    imports []
    provides [mainForHost]

import Task
import Internal.Task

mainForHost : Task.Task Model [] as Fx
mainForHost = main
```

**Key Components:**

| Section | Purpose |
|---------|---------|
| `requires` | What apps must provide (e.g., `main` function) |
| `exposes` | Modules the platform provides to apps |
| `packages` | Dependencies |
| `imports` | Internal platform imports |
| `provides` | Entry point for host |

### Platform Interface Design

**Good platform design:**

1. **Clear separation of concerns:**
```roc
# Platform exposes pure types and Task-based I/O
module [
    # Pure types
    Request,
    Response,
    # Effectful operations
    serveHttp : Config, (Request -> Task Response []) -> Task {} []
]
```

2. **Type-safe I/O:**
```roc
# File module
read : Path -> Task Str [FileNotFound, PermissionDenied]
write : Path, Str -> Task {} [PermissionDenied, DiskFull]

# Stdin module
line : Task Str [EndOfInput]
```

3. **Composable effects:**
```roc
# Tasks can be chained
program : Task {} []
program =
    path <- Task.await (Env.var "CONFIG_PATH")
    contents <- Task.await (File.read path)
    config <- Task.await (parseConfig contents)
    runServer config
```

---

## Module Organization Patterns

### Single Responsibility Modules

```roc
# Types.roc - Just type definitions
module [Config, Document, Metadata]

Config : {
    timeout : U64,
    retries : U8,
}

Document : {
    title : Str,
    content : Str,
    metadata : Metadata,
}

Metadata : {
    author : Str,
    created : U64,
}
```

### Extension Modules

```roc
# ConfigExt.roc - Operations on Config
module [default, withTimeout, validate]

import Types exposing [Config]

default : Config
default = {
    timeout: 30_000,
    retries: 3,
}

withTimeout : Config, U64 -> Config
withTimeout = \config, ms -> { config & timeout: ms }

validate : Config -> Result Config [InvalidTimeout, InvalidRetries]
validate = \config ->
    if config.timeout == 0 then
        Err InvalidTimeout
    else if config.retries > 10 then
        Err InvalidRetries
    else
        Ok config
```

### Re-export Pattern

**package/main.roc:**
```roc
package [
    # Re-export commonly used types from multiple modules
    Config,
    Document,
    # Re-export main functions
    parse,
    parseWithConfig,
    # Expose modules for advanced usage
    Parser,
    Types,
]

# Import everything needed for re-exports
import Parser exposing [parse, parseWithConfig]
import Types exposing [Config, Document]
```

---

## Type Design Patterns

### Opaque Types

```roc
module [UserId, fromU64, toU64]

# Opaque: internals hidden from users
UserId := U64

## Create a UserId from a U64.
fromU64 : U64 -> UserId
fromU64 = @UserId

## Extract the U64 from a UserId.
toU64 : UserId -> U64
toU64 = \@UserId id -> id
```

### Tagged Unions for Errors

```roc
module [ParseError, toStr]

ParseError : [
    InvalidSyntax Str,
    UnexpectedEnd,
    UnknownTag Str,
]

toStr : ParseError -> Str
toStr = \err ->
    when err is
        InvalidSyntax msg -> "Invalid syntax: $(msg)"
        UnexpectedEnd -> "Unexpected end of input"
        UnknownTag tag -> "Unknown tag: $(tag)"
```

### Builder Pattern (Records with Defaults)

```roc
module [Config, default, build, withTimeout, withRetries]

Config : {
    timeout : U64,
    retries : U8,
    strict : Bool,
}

default : Config
default = {
    timeout: 30_000,
    retries: 3,
    strict: Bool.false,
}

build : {} -> Config
build = \{} -> default

withTimeout : Config, U64 -> Config
withTimeout = \config, ms -> { config & timeout: ms }

withRetries : Config, U8 -> Config
withRetries = \config, n -> { config & retries: n }

# Usage:
# config = build {} |> withTimeout 60_000 |> withRetries 5
```

---

## Testing Patterns

### Expect Blocks

```roc
## Parse a valid document.
parse : Str -> Result Document ParseError
parse = \input ->
    # Implementation
    # ...

# Test cases using expect
expect
    result = parse "# Title\nContent"
    result == Ok { title: "Title", content: "Content" }

expect
    result = parse ""
    result == Err UnexpectedEnd

expect
    result = parse "# Title\nContent"
    Result.isOk result
```

### Test Modules

**tests/ParserTests.roc:**
```roc
module []

import Parser exposing [parse, ParseError]

expect
    # Happy path
    input = "# Hello\nWorld"
    result = parse input
    result == Ok { title: "Hello", content: "World" }

expect
    # Error case
    result = parse ""
    result == Err UnexpectedEnd

expect
    # Edge case
    input = Str.repeat "a" 10_000
    result = parse input
    Result.isOk result
```

### Property-Based Testing Pattern

```roc
# Generate test cases
expectAll = \cases ->
    List.all cases \case ->
        expected = case.expected
        actual = parse case.input
        actual == expected

expect
    cases = [
        { input: "# A\nB", expected: Ok { title: "A", content: "B" } },
        { input: "", expected: Err UnexpectedEnd },
        { input: "###", expected: Err (InvalidSyntax "Too many #") },
    ]
    expectAll cases
```

---

## Builtin Modules

Roc provides several builtin modules auto-imported into every file:

| Module | Purpose | Common Functions |
|--------|---------|------------------|
| `Str` | String operations | `concat`, `split`, `trim`, `to_utf8` |
| `Num` | Numeric operations | `add`, `sub`, `is_even`, `abs` |
| `List` | List operations | `map`, `filter`, `fold_left`, `len` |
| `Dict` | Dictionary/Map | `insert`, `get`, `keys`, `values` |
| `Set` | Set operations | `insert`, `contains`, `union` |
| `Bool` | Boolean operations | `true`, `false`, `not` |
| `Result` | Result type | `Ok`, `Err`, `map`, `try` |

**Note:** The standard library provides NO I/O operations. All I/O comes from platforms.

---

## Breaking Changes (2025)

### Snake Case Migration

Builtins are migrating from `camelCase` to `snake_case`:

```roc
# Old (deprecated)
Str.joinWith
List.keepIf

# New (current)
Str.join_with
List.keep_if
```

**Action:** Use new snake_case names in all new packages.

### Task Deprecation (Purity Inference)

`Task` is deprecated in favor of purity inference:

```roc
# Old pattern
readConfig : Task Config [FileNotFound]
readConfig =
    path <- Task.await (Env.var "CONFIG")
    contents <- Task.await (File.read path)
    Task.ok (parse contents)

# New pattern (purity inferred)
readConfig : Config ![FileNotFound, EnvVarNotSet]
readConfig =
    path = Env.var! "CONFIG"
    contents = File.read! path
    parse contents
```

**Action:** For new platforms, use purity inference. For compatibility, check platform docs.

---

## Publishing Packages

### Pre-publish Checklist

- [ ] `roc check` passes on all modules
- [ ] `roc test` passes
- [ ] `roc format` applied to all files
- [ ] Documentation comments on all public functions
- [ ] Examples in `examples/` directory
- [ ] README.md with usage examples
- [ ] Version follows semantic versioning
- [ ] No dependencies on unreleased packages
- [ ] License file included

### Package Metadata

**Include in README.md:**

```markdown
# My Package

Brief description of what this package does.

## Installation

How to include this package in a Roc project.

## Quick Start

\```roc
import MyPackage exposing [parse]

main =
    result = parse "input"
    # ...
\```

## Modules

- `Parser` - Main parsing logic
- `Types` - Type definitions
- `Config` - Configuration utilities

## Examples

See `examples/` directory.

## License

MIT
```

---

## Common Patterns

### Error Handling

```roc
# Return Result for operations that can fail
parse : Str -> Result Document [InvalidSyntax Str, UnexpectedEnd]
parse = \input ->
    if Str.is_empty input then
        Err UnexpectedEnd
    else
        # Parse logic
        Ok document

# Chain Results
processDocument : Str -> Result ProcessedDoc [ParseError, ValidationError]
processDocument = \input ->
    parsed <- Result.try (parse input |> Result.map_err ParseError)
    validated <- Result.try (validate parsed |> Result.map_err ValidationError)
    Ok (process validated)
```

### Polymorphic Functions

```roc
# Generic over any type
identity : a -> a
identity = \x -> x

# Constrained generics (via abilities - future feature)
compare : a, a -> [LT, EQ, GT] where a implements Ord
```

### Pipeline Pattern

```roc
# Use |> for readable data transformations
processData : List Str -> List Str
processData = \items ->
    items
    |> List.map Str.trim
    |> List.keep_if (\s -> !(Str.is_empty s))
    |> List.map Str.to_lowercase
    |> List.sort_with Str.compare
```

---

## Anti-Patterns

### 1. Leaking Implementation Details

```roc
# Bad: Exposing internal structure
module [Config, InternalState]

# Good: Only expose what's needed
module [Config, fromStr, toStr]
```

### 2. Overly Large Modules

```roc
# Bad: Single module with 1000+ lines

# Good: Split into focused modules
# - Types.roc (types)
# - Parser.roc (parsing)
# - Validator.roc (validation)
# - main.roc (re-exports)
```

### 3. Missing Documentation

```roc
# Bad: No docs
parse : Str -> Result Document ParseError

# Good: Documented
## Parse a document from a string.
##
## Returns a Document on success, or ParseError if the input is invalid.
##
## ```roc
## result = parse "# Title"
## expect result == Ok { title: "Title", ... }
## ```
parse : Str -> Result Document ParseError
```

### 4. Platform Doing Too Much

```roc
# Bad: Platform provides complex business logic
module [
    readUserFromDb,
    validateUser,
    sendEmail,
]

# Good: Platform provides primitives
module [
    dbQuery,
    httpRequest,
    # Let apps compose these into business logic
]
```

---

## Troubleshooting

### Module Not Found

**Symptom:** `Module 'MyModule' not found`

**Causes & Fixes:**

| Cause | Fix |
|-------|-----|
| Module not in package exports | Add to `package [...]` list |
| File name doesn't match module | Rename file to match (e.g., `MyModule.roc`) |
| Import path incorrect | Use correct relative/absolute path |

### Type Inference Failures

**Symptom:** `Cannot infer type for this expression`

**Fixes:**
1. Add explicit type annotation
2. Provide more context (often happens in empty lists)
3. Check for ambiguous number types (add `U64`, `I32`, etc.)

```roc
# Problem: Ambiguous type
nums = []

# Fix: Provide type context
nums : List U64
nums = []

# Or use in context
nums = List.range { start: At 1, end: At 10 }
```

### Circular Dependencies

**Symptom:** `Circular dependency detected`

**Fix:** Restructure modules

```roc
# Before (circular):
# A.roc imports B.roc
# B.roc imports A.roc

# After: Extract shared types
# Types.roc (shared types)
# A.roc imports Types
# B.roc imports Types
```

---

## Platform Examples

### Basic CLI Platform

```roc
platform "basic-cli"
    requires { Model } { main : Task Model [] }
    exposes [
        Task,
        Stdout,
        Stdin,
        File,
        Path,
        Env,
        Arg,
    ]
    packages {}
    imports []
    provides [mainForHost]

mainForHost : Task Model [] as Fx
mainForHost = main
```

### Web Platform

```roc
platform "basic-webserver"
    requires {} { main : Request -> Task Response [] }
    exposes [
        Request,
        Response,
        Task,
        Stdout,
    ]
    packages {}
    imports []
    provides [mainForHost]

Request : {
    method : [GET, POST, PUT, DELETE],
    url : Str,
    headers : Dict Str Str,
    body : List U8,
}

Response : {
    status : U16,
    headers : Dict Str Str,
    body : List U8,
}
```

---

## References

- `meta-library-dev` - Foundational library patterns
- [Roc Tutorial](https://www.roc-lang.org/tutorial)
- [Roc Platforms](https://www.roc-lang.org/platforms)
- [GitHub - roc-lang/roc](https://github.com/roc-lang/roc)
- [basic-cli Platform](https://github.com/roc-lang/basic-cli)
- [basic-webserver Platform](https://github.com/roc-lang/basic-webserver)

---

## Sources

- [The Roc Programming Language](https://www.roc-lang.org/)
- [GitHub - roc-lang/roc](https://github.com/roc-lang/roc)
- [Tutorial | Roc](https://www.roc-lang.org/tutorial)
- [Platforms and Apps | Roc](https://www.roc-lang.org/platforms)
- [Understanding Roc: Functional and separate from the runtime | TechTarget](https://www.techtarget.com/searchapparchitecture/tip/Understanding-Roc-Functional-and-separate-from-the-runtime)
