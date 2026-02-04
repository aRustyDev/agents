# TypeScript

> Typed superset of JavaScript that compiles to plain JavaScript.

## Overview

TypeScript is a strongly-typed programming language developed by Microsoft, first released in 2012. It builds on JavaScript by adding optional static type checking, interfaces, enums, and other features that help catch errors at compile time rather than runtime.

TypeScript code compiles to JavaScript, making it compatible with any JavaScript runtime (browsers, Node.js, Deno, Bun). The type system is structural (duck typing) rather than nominal, and uses type inference to reduce annotation burden while maintaining type safety.

The language has become the standard for large-scale JavaScript applications, offering better tooling, refactoring support, and documentation through types while maintaining full JavaScript interoperability.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | Dynamic | Compiles to JavaScript |
| Secondary Family | Gradual-Typing | Optional static types |
| Subtype | web | Web/Node.js ecosystem |

See: [Dynamic Family](../language-families/dynamic.md), [Gradual-Typing Family](../language-families/gradual-typing.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| 4.0 | 2020-08 | Variadic tuple types, labeled tuple elements |
| 4.9 | 2022-11 | satisfies operator, auto-accessors |
| 5.0 | 2023-03 | const type parameters, decorators (stage 3) |
| 5.3 | 2023-11 | Import attributes, narrowing improvements |

## Feature Profile

### Type System

- **Strength:** gradual (static types optional, `any` escape hatch)
- **Inference:** bidirectional (strong local inference)
- **Generics:** bounded (constraints via `extends`)
- **Nullability:** optional (`strictNullChecks`, `T | null | undefined`)

### Memory Model

- **Management:** gc (JavaScript engine GC)
- **Mutability:** default-mutable (`readonly` modifier available)
- **Allocation:** heap (automatic, JavaScript semantics)

### Control Flow

- **Structured:** if-else, for, while, switch, try-catch
- **Effects:** exceptions (try/catch/finally)
- **Async:** async-await, Promises

### Data Types

- **Primitives:** number, string, boolean, bigint, symbol, null, undefined
- **Composites:** arrays, tuples, objects, classes, interfaces
- **Collections:** Array, Map, Set, WeakMap, WeakSet
- **Abstraction:** interfaces, type aliases, classes, modules

### Metaprogramming

- **Macros:** none (but type-level computation)
- **Reflection:** runtime (JavaScript reflection), type guards
- **Code generation:** decorators (experimental → stage 3)

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | npm, pnpm, yarn, bun | npm is default |
| Build System | tsc, esbuild, swc, vite | tsc for type checking |
| LSP | typescript-language-server | Built into tsc |
| Formatter | prettier, biome | prettier is standard |
| Linter | eslint, biome | biome is faster |
| REPL | ts-node, tsx, bun | tsx for quick scripts |
| Test Framework | jest, vitest, mocha | vitest is modern |

## Syntax Patterns

```typescript
// Function definition
function greet(name: string, times: number = 1): string {
  return `Hello, ${name}! `.repeat(times);
}

// Arrow function with generics
const identity = <T>(value: T): T => value;

// Async function
async function fetchData(url: string): Promise<Response> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response;
}

// Type definition (interface)
interface User {
  readonly id: string;
  name: string;
  email?: string;  // optional
}

// Type definition (type alias with union)
type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };

// Discriminated union
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "rectangle"; width: number; height: number };

function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.radius ** 2;
    case "rectangle":
      return shape.width * shape.height;
  }
}

// Class with decorators
class ApiClient {
  constructor(private baseUrl: string) {}

  async get<T>(path: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`);
    return response.json();
  }
}

// Error handling
try {
  const data = await fetchData(url);
} catch (error) {
  if (error instanceof NetworkError) {
    console.error("Network failed:", error.message);
  } else {
    throw error;
  }
} finally {
  cleanup();
}

// Type guard
function isUser(value: unknown): value is User {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    "name" in value
  );
}

// Mapped type
type Readonly<T> = {
  readonly [K in keyof T]: T[K];
};

// Conditional type
type Flatten<T> = T extends Array<infer U> ? U : T;
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| Types erased at runtime | moderate | Use type guards, zod/io-ts for runtime validation |
| `any` bypasses type checking | minor | Use `unknown` instead, enable `noImplicitAny` |
| No pattern matching | moderate | Use discriminated unions + switch |
| Null vs undefined distinction | minor | Use `strictNullChecks`, prefer `undefined` |
| No true immutability | minor | Use `readonly` modifier, `as const` |
| Structural typing can be surprising | minor | Use branded types for nominal-like behavior |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 2 | typescript-golang, typescript-rust |
| As Target | 1 | python-typescript |

**Missing high-value pairs:** typescript→python, typescript→java, javascript→typescript

## Idiomatic Patterns

### Discriminated Unions → ADTs

```typescript
// TypeScript: discriminated union
type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };

// IR equivalent: ADT/enum
// enum Result<T, E> { Ok(T), Err(E) }
```

### Type Guards → Pattern Matching

```typescript
// TypeScript: type guard
function processShape(shape: Shape) {
  if (shape.kind === "circle") {
    return Math.PI * shape.radius ** 2;
  }
  // TypeScript narrows type here
}

// IR equivalent: pattern match
// match shape { Circle { radius } => ... }
```

### Optional Chaining → Maybe/Option

```typescript
// TypeScript: optional chaining
const name = user?.profile?.name ?? "Anonymous";

// IR equivalent: Option combinators
// user.and_then(|u| u.profile).map(|p| p.name).unwrap_or("Anonymous")
```

## Related Languages

- **Influenced by:** JavaScript, C#, Java
- **Influenced:** Flow, Dart (partially)
- **Compiles to:** JavaScript (ES3-ESNext)
- **FFI compatible:** JavaScript (native), WebAssembly (via wasm-bindgen)

## Sources

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [TypeScript Language Specification](https://github.com/microsoft/TypeScript/blob/main/doc/spec-ARCHIVED.md)
- [TypeScript Playground](https://www.typescriptlang.org/play)
- [Type Challenges](https://github.com/type-challenges/type-challenges)

## See Also

- [Dynamic Family](../language-families/dynamic.md)
- [Gradual-Typing Family](../language-families/gradual-typing.md)
- [Python](python.md) - Gradual typing comparison
- [JavaScript](javascript.md) - Compile target
