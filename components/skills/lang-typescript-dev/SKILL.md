---
name: lang-typescript-dev
description: Foundational TypeScript patterns covering types, interfaces, generics, utility types, and common idioms. Use when writing TypeScript code, understanding the type system, or needing guidance on which specialized TypeScript skill to use. This is the entry point for TypeScript development.
---

# TypeScript Fundamentals

Foundational TypeScript patterns and core type system features. This skill serves as both a reference for common patterns and an index to specialized TypeScript skills.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   TypeScript Skill Hierarchy                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                 ┌─────────────────────┐                         │
│                 │ lang-typescript-dev │ ◄── You are here        │
│                 │    (foundation)     │                         │
│                 └──────────┬──────────┘                         │
│                            │                                    │
│            ┌───────────────┴───────────────┐                    │
│            │                               │                    │
│            ▼                               ▼                    │
│   ┌─────────────────┐            ┌─────────────────┐           │
│   │    patterns     │            │     library     │           │
│   │      -dev       │            │       -dev      │           │
│   └─────────────────┘            └─────────────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**This skill covers:**
- Basic and advanced types
- Interfaces and type aliases
- Unions, intersections, and type guards
- Generics fundamentals
- Utility types
- Common patterns and idioms

**This skill does NOT cover (see specialized skills):**
- tsconfig.json configuration → `lang-typescript-patterns-dev`
- Best practices and code patterns → `lang-typescript-patterns-dev`
- Library/package publishing → `lang-typescript-library-dev`
- React component typing → frontend skills
- Node.js typing → backend skills

---

## Quick Reference

| Task | Syntax |
|------|--------|
| Type alias | `type Name = string \| number` |
| Interface | `interface User { name: string }` |
| Generic function | `function fn<T>(x: T): T` |
| Optional property | `{ name?: string }` |
| Readonly property | `{ readonly id: number }` |
| Union type | `string \| number` |
| Intersection | `TypeA & TypeB` |
| Type assertion | `value as Type` or `<Type>value` |
| Non-null assertion | `value!` |
| Type guard | `if (typeof x === 'string')` |

---

## Skill Routing

Use this table to find the right specialized skill:

| When you need to... | Use this skill |
|---------------------|----------------|
| Configure tsconfig.json | `lang-typescript-patterns-dev` |
| Set up strict mode, path aliases | `lang-typescript-patterns-dev` |
| Publish npm packages | `lang-typescript-library-dev` |
| Configure ESM/CJS dual packages | `lang-typescript-library-dev` |
| Generate declaration files | `lang-typescript-library-dev` |

---

## Basic Types

### Primitive Types

```typescript
// String, number, boolean
let name: string = "Alice";
let age: number = 30;
let active: boolean = true;

// Arrays
let numbers: number[] = [1, 2, 3];
let names: Array<string> = ["Alice", "Bob"];

// Tuple (fixed-length array with specific types)
let pair: [string, number] = ["age", 30];

// Any (escape hatch - avoid when possible)
let data: any = "could be anything";

// Unknown (safer than any - requires type checking)
let input: unknown = getUserInput();
if (typeof input === "string") {
  console.log(input.toUpperCase()); // OK after check
}

// Void (function returns nothing)
function log(msg: string): void {
  console.log(msg);
}

// Never (function never returns)
function fail(msg: string): never {
  throw new Error(msg);
}

// Null and undefined
let nullable: string | null = null;
let optional: string | undefined = undefined;
```

### Object Types

```typescript
// Inline object type
function greet(user: { name: string; age: number }): string {
  return `Hello, ${user.name}`;
}

// Optional properties
function greet(user: { name: string; age?: number }): string {
  return user.age ? `${user.name} is ${user.age}` : user.name;
}

// Index signatures
interface StringMap {
  [key: string]: string;
}

const headers: StringMap = {
  "Content-Type": "application/json",
  "Authorization": "Bearer token",
};
```

---

## Interfaces vs Type Aliases

### Interface

```typescript
// Declaration
interface User {
  id: number;
  name: string;
  email?: string;
}

// Extension
interface Admin extends User {
  permissions: string[];
}

// Declaration merging (interfaces can be extended across files)
interface User {
  createdAt: Date;  // Adds to existing User interface
}

// Implementing interfaces
class UserImpl implements User {
  id = 1;
  name = "Alice";
  createdAt = new Date();
}
```

### Type Alias

```typescript
// Declaration
type User = {
  id: number;
  name: string;
  email?: string;
};

// Intersection (like extends)
type Admin = User & {
  permissions: string[];
};

// Types can represent primitives, unions, tuples
type ID = string | number;
type Point = [number, number];
type Callback = (data: string) => void;

// Cannot be merged (redeclaration is an error)
```

### When to Use Which

| Use Case | Prefer |
|----------|--------|
| Object shapes | Either (interface slightly better for extension) |
| Unions, intersections | Type alias (only option) |
| Primitives, tuples | Type alias (only option) |
| Class implementation | Interface |
| Library public API | Interface (allows consumer extension) |
| Complex computed types | Type alias |

---

## Unions and Intersections

### Union Types

```typescript
// Value can be one of several types
type Status = "pending" | "approved" | "rejected";
type ID = string | number;

function process(id: ID): void {
  // Must handle both cases
  if (typeof id === "string") {
    console.log(id.toUpperCase());
  } else {
    console.log(id.toFixed(2));
  }
}

// Discriminated unions (tagged unions)
type Success = { status: "success"; data: string };
type Failure = { status: "failure"; error: Error };
type Result = Success | Failure;

function handle(result: Result): void {
  switch (result.status) {
    case "success":
      console.log(result.data);  // TypeScript knows this is Success
      break;
    case "failure":
      console.error(result.error);  // TypeScript knows this is Failure
      break;
  }
}
```

### Intersection Types

```typescript
// Combine multiple types
type Named = { name: string };
type Aged = { age: number };
type Person = Named & Aged;  // { name: string; age: number }

// Useful for mixins
type Timestamped = { createdAt: Date; updatedAt: Date };
type User = { id: number; name: string };
type TimestampedUser = User & Timestamped;
```

---

## Type Guards

### Built-in Type Guards

```typescript
// typeof (primitives)
function process(value: string | number): void {
  if (typeof value === "string") {
    console.log(value.toUpperCase());
  } else {
    console.log(value.toFixed(2));
  }
}

// instanceof (classes)
function handle(error: Error | string): void {
  if (error instanceof Error) {
    console.log(error.message);
  } else {
    console.log(error);
  }
}

// in operator (property check)
type Cat = { meow: () => void };
type Dog = { bark: () => void };

function speak(animal: Cat | Dog): void {
  if ("meow" in animal) {
    animal.meow();
  } else {
    animal.bark();
  }
}

// Array.isArray
function process(value: string | string[]): void {
  if (Array.isArray(value)) {
    console.log(value.join(", "));
  } else {
    console.log(value);
  }
}
```

### Custom Type Guards

```typescript
// Type predicate function
function isString(value: unknown): value is string {
  return typeof value === "string";
}

function process(value: unknown): void {
  if (isString(value)) {
    console.log(value.toUpperCase());  // TypeScript knows it's string
  }
}

// Discriminated union guard
function isSuccess(result: Result): result is Success {
  return result.status === "success";
}
```

---

## Generics

### Generic Functions

```typescript
// Basic generic function
function identity<T>(value: T): T {
  return value;
}

const str = identity("hello");  // Type: string
const num = identity(42);       // Type: number

// Multiple type parameters
function pair<T, U>(first: T, second: U): [T, U] {
  return [first, second];
}

// With constraints
function getLength<T extends { length: number }>(item: T): number {
  return item.length;
}

getLength("hello");    // OK
getLength([1, 2, 3]);  // OK
getLength(123);        // Error: number has no length
```

### Generic Interfaces and Types

```typescript
// Generic interface
interface Container<T> {
  value: T;
  getValue(): T;
}

// Generic type alias
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

// Usage
const success: Result<string> = { ok: true, value: "data" };
const failure: Result<string> = { ok: false, error: new Error("fail") };
```

### Generic Constraints

```typescript
// Extends constraint
function merge<T extends object, U extends object>(a: T, b: U): T & U {
  return { ...a, ...b };
}

// keyof constraint
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { name: "Alice", age: 30 };
const name = getProperty(user, "name");  // Type: string
const age = getProperty(user, "age");    // Type: number
// getProperty(user, "foo");  // Error: "foo" not in keyof typeof user
```

---

## Utility Types

### Transformation Types

```typescript
interface User {
  id: number;
  name: string;
  email: string;
}

// Partial<T> - All properties optional
type PartialUser = Partial<User>;
// { id?: number; name?: string; email?: string }

// Required<T> - All properties required
type RequiredUser = Required<PartialUser>;

// Readonly<T> - All properties readonly
type ReadonlyUser = Readonly<User>;
// { readonly id: number; readonly name: string; readonly email: string }

// Pick<T, K> - Select properties
type UserName = Pick<User, "name">;
// { name: string }

// Omit<T, K> - Exclude properties
type UserWithoutEmail = Omit<User, "email">;
// { id: number; name: string }
```

### Record and Mapped Types

```typescript
// Record<K, V> - Object with specific key/value types
type UserRoles = Record<string, string[]>;
const roles: UserRoles = {
  alice: ["admin", "user"],
  bob: ["user"],
};

// Index signature equivalent
type SameAsRecord = { [key: string]: string[] };
```

### Conditional Types

```typescript
// Extract<T, U> - Extract types assignable to U
type Numbers = Extract<string | number | boolean, number>;
// number

// Exclude<T, U> - Exclude types assignable to U
type NotNumbers = Exclude<string | number | boolean, number>;
// string | boolean

// NonNullable<T> - Exclude null and undefined
type Defined = NonNullable<string | null | undefined>;
// string
```

### Function Types

```typescript
function greet(name: string, age: number): string {
  return `Hello ${name}, you are ${age}`;
}

// ReturnType<T> - Extract return type
type GreetReturn = ReturnType<typeof greet>;
// string

// Parameters<T> - Extract parameter types as tuple
type GreetParams = Parameters<typeof greet>;
// [string, number]
```

---

## Common Patterns

### Exhaustive Switch

```typescript
type Status = "pending" | "approved" | "rejected";

function handleStatus(status: Status): string {
  switch (status) {
    case "pending":
      return "Waiting...";
    case "approved":
      return "Done!";
    case "rejected":
      return "Failed";
    default:
      // This ensures all cases are handled
      const _exhaustive: never = status;
      return _exhaustive;
  }
}
```

### Branded Types

```typescript
// Create distinct types from primitives
type UserId = string & { readonly brand: unique symbol };
type OrderId = string & { readonly brand: unique symbol };

function createUserId(id: string): UserId {
  return id as UserId;
}

function createOrderId(id: string): OrderId {
  return id as OrderId;
}

function getUser(id: UserId): User { /* ... */ }
function getOrder(id: OrderId): Order { /* ... */ }

const userId = createUserId("user-123");
const orderId = createOrderId("order-456");

getUser(userId);   // OK
// getUser(orderId);  // Error: OrderId not assignable to UserId
```

### Builder Pattern with Types

```typescript
interface RequestConfig {
  url: string;
  method?: "GET" | "POST" | "PUT" | "DELETE";
  headers?: Record<string, string>;
  body?: unknown;
}

class RequestBuilder {
  private config: RequestConfig;

  constructor(url: string) {
    this.config = { url };
  }

  method(m: RequestConfig["method"]): this {
    this.config.method = m;
    return this;
  }

  header(key: string, value: string): this {
    this.config.headers = { ...this.config.headers, [key]: value };
    return this;
  }

  body<T>(data: T): this {
    this.config.body = data;
    return this;
  }

  build(): RequestConfig {
    return this.config;
  }
}

const request = new RequestBuilder("/api/users")
  .method("POST")
  .header("Content-Type", "application/json")
  .body({ name: "Alice" })
  .build();
```

### Assertion Functions

```typescript
function assertDefined<T>(
  value: T | null | undefined,
  message?: string
): asserts value is T {
  if (value === null || value === undefined) {
    throw new Error(message ?? "Value is not defined");
  }
}

function process(value: string | null): void {
  assertDefined(value, "Value required");
  // TypeScript knows value is string here
  console.log(value.toUpperCase());
}
```

---

## Troubleshooting

### "Object is possibly undefined"

```typescript
// Problem
const user = users.find(u => u.id === 1);
console.log(user.name);  // Error: user might be undefined

// Fix 1: Optional chaining
console.log(user?.name);

// Fix 2: Type guard
if (user) {
  console.log(user.name);
}

// Fix 3: Non-null assertion (use carefully)
console.log(user!.name);
```

### "Type 'X' is not assignable to type 'Y'"

```typescript
// Problem
const status: "active" | "inactive" = "active";
const str: string = "active";
// const status2: "active" | "inactive" = str;  // Error

// Fix: Use const assertion or explicit typing
const status2: "active" | "inactive" = str as "active" | "inactive";
// Or
const literal = "active" as const;
```

### "Property 'X' does not exist on type"

```typescript
// Problem with union types
type Cat = { meow: () => void };
type Dog = { bark: () => void };
type Animal = Cat | Dog;

function speak(animal: Animal): void {
  // animal.meow();  // Error: Dog doesn't have meow

  // Fix: Type guard
  if ("meow" in animal) {
    animal.meow();
  }
}
```

### Index Signature Errors

```typescript
// Problem
interface User {
  name: string;
  age: number;
}

const key = "name";
// const value = user[key];  // Error with noPropertyAccessFromIndexSignature

// Fix 1: Use known key
const value = user.name;

// Fix 2: Type assertion
const value2 = user[key as keyof User];

// Fix 3: Add index signature (if dynamic access needed)
interface FlexibleUser {
  name: string;
  age: number;
  [key: string]: string | number;
}
```

---

## References

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [TypeScript Playground](https://www.typescriptlang.org/play)
- Specialized skills: `lang-typescript-patterns-dev`, `lang-typescript-library-dev`
