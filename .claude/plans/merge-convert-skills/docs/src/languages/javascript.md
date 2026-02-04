# JavaScript

> Dynamic, prototype-based language that powers the web and increasingly server-side applications.

## Overview

JavaScript is a dynamic, prototype-based programming language created by Brendan Eich at Netscape in 1995. Originally designed for client-side web scripting, it has become one of the most widely used programming languages, running in browsers, servers (Node.js, Deno, Bun), and embedded systems.

JavaScript's event-driven, single-threaded nature with an event loop makes it well-suited for I/O-heavy applications. The language has evolved significantly through ECMAScript standards, adding features like classes, modules, async/await, and optional chaining.

As the compile target for TypeScript and the runtime for web applications, JavaScript remains foundational to modern software development.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | Dynamic | Prototype-based, duck typing |
| Secondary Family | — | Multi-paradigm |
| Subtype | web | Browser and server |

See: [Dynamic Family](../language-families/dynamic.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| ES5 | 2009-12 | Strict mode, JSON, Array methods |
| ES6/ES2015 | 2015-06 | Classes, modules, arrow functions, let/const, Promises |
| ES2017 | 2017-06 | async/await, Object.entries/values |
| ES2020 | 2020-06 | Optional chaining (?.), nullish coalescing (??) |
| ES2022 | 2022-06 | Top-level await, class fields, .at() |
| ES2023 | 2023-06 | Array findLast, Hashbang support |

## Feature Profile

### Type System

- **Strength:** weak (dynamic, implicit coercion)
- **Inference:** none (runtime typing)
- **Generics:** none (duck typing)
- **Nullability:** nullable (null and undefined)

### Memory Model

- **Management:** gc (engine GC - V8, SpiderMonkey, JavaScriptCore)
- **Mutability:** default-mutable (const for bindings, not values)
- **Allocation:** heap (automatic)

### Control Flow

- **Structured:** if-else, for, while, switch, try-catch
- **Effects:** exceptions (throw/try/catch)
- **Async:** Promises, async/await, callbacks

### Data Types

- **Primitives:** number, string, boolean, bigint, symbol, null, undefined
- **Composites:** objects, arrays, functions, classes
- **Collections:** Array, Map, Set, WeakMap, WeakSet
- **Abstraction:** prototypes, classes, modules

### Metaprogramming

- **Macros:** none
- **Reflection:** runtime (Reflect, Object methods)
- **Code generation:** eval, Function constructor, Proxy

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | npm, pnpm, yarn, bun | npm is default |
| Build System | webpack, vite, esbuild, rollup | vite is modern |
| LSP | typescript-language-server | Works for JS too |
| Formatter | prettier, biome | prettier standard |
| Linter | eslint, biome | biome is faster |
| REPL | node, deno, bun, browser console | Multiple runtimes |
| Test Framework | jest, vitest, mocha | vitest modern |

## Syntax Patterns

```javascript
// Function definition
function greet(name, times = 1) {
  return "Hello, " + name + "! ".repeat(times);
}

// Arrow function
const greet = (name, times = 1) => `Hello, ${name}! `.repeat(times);

// Async function
async function fetchData(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

// Class definition
class User {
  #email; // private field

  constructor(id, name) {
    this.id = id;
    this.name = name;
    this.#email = null;
  }

  get email() {
    return this.#email;
  }

  set email(value) {
    this.#email = value;
  }

  toString() {
    return `User(${this.name})`;
  }
}

// Object literal
const user = {
  id: "1",
  name: "Alice",
  email: null,
  greet() {
    return `Hello, ${this.name}!`;
  }
};

// Destructuring
const { name, email = "default@example.com" } = user;
const [first, second, ...rest] = array;

// Spread operator
const newUser = { ...user, name: "Bob" };
const combined = [...array1, ...array2];

// Optional chaining and nullish coalescing
const email = user?.profile?.email ?? "no-email@example.com";

// Promise handling
fetchData(url)
  .then(data => process(data))
  .catch(error => console.error(error))
  .finally(() => cleanup());

// Array methods (functional style)
const numbers = [1, 2, 3, 4, 5];
const result = numbers
  .filter(n => n % 2 === 0)
  .map(n => n * 2)
  .reduce((sum, n) => sum + n, 0);

// Module export/import
// utils.js
export function helper() { }
export default class Main { }

// main.js
import Main, { helper } from './utils.js';

// Error handling
try {
  const result = riskyOperation();
} catch (error) {
  if (error instanceof NetworkError) {
    console.error("Network failed:", error.message);
  } else {
    throw error;
  }
} finally {
  cleanup();
}

// Generator
function* fibonacci() {
  let [a, b] = [0, 1];
  while (true) {
    yield a;
    [a, b] = [b, a + b];
  }
}

// Proxy (metaprogramming)
const proxy = new Proxy(target, {
  get(obj, prop) {
    console.log(`Accessing ${prop}`);
    return obj[prop];
  }
});
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| No static types | high | Use TypeScript |
| Type coercion surprises | moderate | Use === instead of ==, TypeScript |
| this binding confusion | moderate | Arrow functions, explicit binding |
| null vs undefined | minor | Use ?? operator, consistent conventions |
| No integer type | minor | Use BigInt for large integers, Math.trunc() |
| Prototype complexity | minor | Use class syntax, avoid prototype manipulation |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 0 | — |
| As Target | 0 | — |

**Note:** Not in current convert-* skills despite ubiquity. TypeScript serves as typed alternative.

## Idiomatic Patterns

### Promises → Async/Effect

```javascript
// JavaScript: Promise chain
fetch(url).then(r => r.json()).then(process);

// IR equivalent: async/await or effect
// let data = await fetch(url).json();
```

### Prototypes → Classes/Traits

```javascript
// JavaScript: prototype
Object.prototype.toString = function() { };

// IR equivalent: trait/interface implementation
// impl Display for Object { }
```

### Optional Chaining → Maybe/Option

```javascript
// JavaScript: optional chaining
const name = user?.profile?.name ?? "Anonymous";

// IR equivalent: Option combinators
// user.and_then(|u| u.profile).map(|p| p.name).unwrap_or("Anonymous")
```

## Related Languages

- **Influenced by:** Java (syntax), Scheme (functions), Self (prototypes)
- **Influenced:** TypeScript, CoffeeScript, Dart, many others
- **Compiles to:** Bytecode (V8, etc.)
- **FFI compatible:** WebAssembly, Node.js native addons

## Sources

- [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [ECMAScript Specification](https://tc39.es/ecma262/)
- [TC39 Proposals](https://github.com/tc39/proposals)
- [Node.js Documentation](https://nodejs.org/docs/)

## See Also

- [Dynamic Family](../language-families/dynamic.md)
- [TypeScript](typescript.md) - Typed superset
- [Python](python.md) - Dynamic comparison
