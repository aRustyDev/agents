---
name: convert-python-typescript
description: Bidirectional conversion between Python and Typescript. Use when migrating projects between these languages in either direction. Extends meta-convert-dev with Python↔Typescript specific patterns. Use when migrating Python projects to TypeScript, translating Pythonic patterns to TypeScript idioms, or refactoring Python codebases into TypeScript. Extends meta-convert-dev with Python-to-TypeScript specific patterns.
---

# Python ↔ Typescript Conversion

Bidirectional conversion between Python and Typescript. This skill extends `meta-convert-dev` with Python↔Typescript specific type mappings, idiom translations, and tooling.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Python types → TypeScript types (with runtime to static typing)
- **Idiom translations**: Pythonic patterns → TypeScript idioms
- **Error handling**: Python exceptions → TypeScript error patterns
- **Async patterns**: asyncio/async-await → Promise/async-await
- **Type system differences**: Dynamic duck typing → static structural typing

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Python language fundamentals - see `lang-python-dev`
- TypeScript language fundamentals - see `lang-typescript-patterns-dev`

---

## Quick Reference

| Python | TypeScript | Notes |
|--------|------------|-------|
| `str` | `string` | Unicode strings |
| `int` | `number` / `bigint` | Regular numbers or large integers |
| `float` | `number` | Floating point |
| `bool` | `boolean` | Same concept |
| `list[T]` | `T[]` / `Array<T>` | Mutable array |
| `tuple[T, U]` | `[T, U]` / `readonly [T, U]` | Fixed-size tuple |
| `dict[K, V]` | `Record<K, V>` / `Map<K, V>` | Key-value mapping |
| `T \| None` / `Optional[T]` | `T \| null` / `T \| undefined` | Nullable types |
| `Coroutine[Any, Any, T]` | `Promise<T>` | Async operations |
| `class X` / `Protocol` | `interface X` / `type X` | Structure definition |
| `Enum` / `Literal` | `enum X` / `const` object | Enumerated values |

## When Converting Code

1. **Analyze source thoroughly** before writing TypeScript
2. **Map types first** - Python type hints → TypeScript types
3. **Preserve semantics** over syntax similarity
4. **Adopt TypeScript idioms** - don't write "Python code in TypeScript syntax"
5. **Handle edge cases** - None → null/undefined, falsy values
6. **Test equivalence** - same inputs → same outputs

---

## Type System Mapping

### Primitive Types

| Python | TypeScript | Notes |
|--------|------------|-------|
| `str` | `string` | UTF-16 in TS, but similar usage |
| `int` | `number` | For safe integers (-2^53 to 2^53) |
| `int` | `bigint` | For arbitrary precision (use when needed) |
| `float` | `number` | IEEE 754 double precision |
| `bool` | `boolean` | Lowercase (true/false) in TS |
| `None` | `null` | Explicit null |
| `None` | `undefined` | Implicit absence (default) |
| - | `void` | Function return type (no value) |
| `Any` | `any` | Escape hatch (avoid when possible) |
| `object` | `unknown` | Type-safe any |
| `NoReturn` | `never` | Function never returns |

### Collection Types

| Python | TypeScript | Notes |
|--------|------------|-------|
| `list[T]` | `T[]` / `Array<T>` | Mutable, ordered |
| `tuple[T, ...]` | `readonly T[]` | Immutable sequence |
| `tuple[T, U]` | `[T, U]` | Fixed-size tuple |
| `set[T]` | `Set<T>` | Unique values, unordered |
| `dict[K, V]` | `Map<K, V>` | Key-value with object keys |
| `dict[str, V]` | `Record<string, V>` | String-keyed object |
| `dict[str, V]` | `{ [key: string]: V }` | Index signature |
| `frozenset[T]` | `ReadonlySet<T>` | Immutable set |
| `Mapping[K, V]` | `ReadonlyMap<K, V>` | Immutable map view |

### Composite Types

| Python | TypeScript | Notes |
|--------|------------|-------|
| `class X:` | `interface X { ... }` | Data structure |
| `class X:` | `class X { ... }` | With methods/behavior |
| `Protocol` | `interface X { ... }` | Structural typing |
| `dataclass` | `interface X { ... }` | Data-only classes |
| `TypedDict` | `interface X { ... }` | Typed dict structure |
| `T \| U` | `T \| U` | Union types (3.10+) |
| `Union[T, U]` | `T \| U` | Union types (pre-3.10) |
| - | `T & U` | Intersection (combine fields) |
| `Optional[T]` | `T \| null` / `T \| undefined` | Nullable |
| `Literal["a", "b"]` | `"a" \| "b"` | String literal union |

### Generic Types

| Python | TypeScript | Notes |
|--------|------------|-------|
| `[T]` (3.12+) / `TypeVar('T')` | `<T>` | Generic type parameter |
| `TypeVar('T', bound=U)` | `<T extends U>` | Bounded type variable |
| `TypeVar('T', A, B)` | `T extends A \| B` | Constrained type |
| `Callable[[A, B], R]` | `(a: A, b: B) => R` | Function signature |
| `Callable[..., R]` | `(...args: any[]) => R` | Variadic function |
| `Type[T]` | `typeof T` | Type of class |
| - | `keyof T` | Union of property keys |
| - | `T[K]` | Index access type |

---

## Module System Translation

Python uses a straightforward import system, while TypeScript has ES modules with explicit imports/exports.

### Import and Export Patterns

**Python:**
```python
# math_utils.py - Python module
def add(a: float, b: float) -> float:
    return a + b

def multiply(a: float, b: float) -> float:
    return a * b

# Explicit public API (optional)
__all__ = ['add', 'multiply']

# Private function (convention)
def _internal_helper():
    pass
```

**TypeScript:**
```typescript
// mathUtils.ts - TypeScript module
export function add(a: number, b: number): number {
  return a + b;
}

export function multiply(a: number, b: number): number {
  return a * b;
}

// Private function (not exported)
function internalHelper() {
  // ...
}

// Default export (Python has no equivalent)
export default class Calculator {
  // ...
}
```

### Import Patterns

**Python:**
```python
# Named imports
from math_utils import add, multiply

# Module import
import math_utils

# Import everything (not recommended)
from math_utils import *

# Import with alias
from math_utils import add as addition

# Relative imports
from . import sibling_module
from .. import parent_module
from ..utils import helper
```

**TypeScript:**
```typescript
// Named imports
import { add, multiply } from './mathUtils';

// Default import
import Calculator from './mathUtils';

// Import with alias
import { add as addition } from './mathUtils';

// Namespace import
import * as MathUtils from './mathUtils';

// Side-effect only import
import './polyfills';

// Type-only imports (erased at runtime)
import type { User, Config } from './types';
```

### Package Structure

**Python:**
```python
# mypackage/
# ├── __init__.py           # Package initialization
# ├── core.py
# └── utils.py

# mypackage/__init__.py
"""Package docstring."""

__version__ = "1.0.0"
__all__ = ["CoreClass", "utility_function"]

from .core import CoreClass
from .utils import utility_function
```

**TypeScript:**
```typescript
// mypackage/
// ├── index.ts              // Barrel export (like __init__.py)
// ├── core.ts
// └── utils.ts

// mypackage/index.ts
export { CoreClass } from './core';
export { utilityFunction } from './utils';
export type { Config } from './types';

// Or re-export all
export * from './core';
export * from './utils';
```

### Dynamic Imports

**Python:**
```python
# Dynamic import
import importlib

module_name = "json"
json_module = importlib.import_module(module_name)

# Lazy imports
def expensive_operation():
    import heavy_module  # Only loaded when function called
    return heavy_module.process()

# Conditional imports (type checking)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from expensive_module import ExpensiveClass
```

**TypeScript:**
```typescript
// Dynamic import (returns Promise)
async function loadModule() {
  const module = await import('./heavyModule');
  return module.process();
}

// Conditional type import
import type { ExpensiveClass } from './expensiveModule';

// Dynamic import with type
type MathUtils = typeof import('./mathUtils');
```

---

## Error Handling Translation

### Python Exception Model → TypeScript Error Patterns

Both languages use exception-based error handling, but TypeScript also supports Result-like patterns.

| Aspect | Python | TypeScript |
|--------|--------|------------|
| Base class | `Exception` | `Error` |
| Try-catch | `try/except/else/finally` | `try/catch/finally` |
| Throwing | `raise Exception()` | `throw new Error()` |
| Re-throwing | `raise` (without args) | `throw` (without args) |
| Type checking | `isinstance()` or specific except | `instanceof` |

### Exception Translation

**Python:**
```python
class AppError(Exception):
    """Base exception for application errors."""
    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.code = code

class NotFoundError(AppError):
    """Raised when a resource is not found."""
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", "NOT_FOUND")
        self.resource = resource

class ValidationError(AppError):
    """Raised when validation fails."""
    def __init__(self, message: str, errors: list[str]):
        super().__init__(message, "VALIDATION_ERROR")
        self.errors = errors
```

**TypeScript:**
```typescript
class AppError extends Error {
  constructor(message: string, public code: string) {
    super(message);
    this.name = this.constructor.name;
    // Maintain proper prototype chain
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

class NotFoundError extends AppError {
  constructor(public resource: string) {
    super(`${resource} not found`, "NOT_FOUND");
  }
}

class ValidationError extends AppError {
  constructor(message: string, public errors: string[]) {
    super(message, "VALIDATION_ERROR");
  }
}
```

### Error Handling Patterns

**Python:**
```python
def load_config(path: str) -> Config:
    try:
        with open(path) as f:
            content = f.read()
        data = json.loads(content)
        return Config(**data)
    except FileNotFoundError:
        raise NotFoundError(path) from None
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in {path}") from e
    except Exception:
        # Re-raise unexpected errors
        raise

# Usage
try:
    config = load_config("config.json")
except NotFoundError as e:
    print(f"Config not found: {e.resource}")
except ValidationError as e:
    print(f"Invalid config: {e.errors}")
```

**TypeScript:**
```typescript
function loadConfig(path: string): Config {
  try {
    const content = fs.readFileSync(path, 'utf-8');
    const data = JSON.parse(content);
    return data as Config;
  } catch (error) {
    if (error.code === 'ENOENT') {
      throw new NotFoundError(path);
    } else if (error instanceof SyntaxError) {
      throw new ValidationError(`Invalid JSON in ${path}`, [error.message]);
    } else {
      // Re-throw unexpected errors
      throw error;
    }
  }
}

// Usage
try {
  const config = loadConfig('config.json');
} catch (error) {
  if (error instanceof NotFoundError) {
    console.error(`Config not found: ${error.resource}`);
  } else if (error instanceof ValidationError) {
    console.error(`Invalid config: ${error.errors}`);
  } else {
    throw error;
  }
}
```

### Result Pattern (Alternative to Exceptions)

**Python:**
```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar('T')
E = TypeVar('E')

@dataclass
class Ok(Generic[T]):
    value: T

@dataclass
class Err(Generic[E]):
    error: E

Result = Ok[T] | Err[E]

def divide(a: float, b: float) -> Result[float, str]:
    if b == 0:
        return Err("Division by zero")
    return Ok(a / b)

# Usage
result = divide(10, 2)
match result:
    case Ok(value):
        print(f"Result: {value}")
    case Err(error):
        print(f"Error: {error}")
```

**TypeScript:**
```typescript
// Result type pattern
type Result<T, E> =
  | { success: true; data: T }
  | { success: false; error: E };

function divide(a: number, b: number): Result<number, string> {
  if (b === 0) {
    return { success: false, error: "Division by zero" };
  }
  return { success: true, data: a / b };
}

// Usage
const result = divide(10, 2);
if (result.success) {
  console.log(`Result: ${result.data}`);
} else {
  console.error(`Error: ${result.error}`);
}
```

---

## Concurrency Patterns

### Python Async/Await → TypeScript Promise/Async-Await

Both languages support async/await, but with different runtimes and patterns.

| Aspect | Python | TypeScript |
|--------|--------|------------|
| Runtime | asyncio event loop (explicit) | V8 event loop (built-in) |
| Promise/Future | `Coroutine[Any, Any, T]` | `Promise<T>` |
| Concurrent | `asyncio.gather()` | `Promise.all()` |
| Race | `asyncio.wait(..., FIRST_COMPLETED)` | `Promise.race()` |
| Timeout | `asyncio.wait_for()` | `Promise.race()` + timeout |

### Basic Async Functions

**Python:**
```python
import asyncio
import aiohttp

async def fetch_user(id: str) -> User:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'/api/users/{id}') as response:
            if not response.ok:
                raise Exception(f"Failed to fetch user {id}")
            data = await response.json()
            return User(**data)

# Entry point requires event loop
async def main():
    user = await fetch_user('123')
    print(user.name)

if __name__ == '__main__':
    asyncio.run(main())
```

**TypeScript:**
```typescript
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch user ${id}`);
  }

  return await response.json();
}

// Can await at top level (in modules)
const user = await fetchUser('123');
console.log(user.name);

// Or in async function
async function main() {
  const user = await fetchUser('123');
  console.log(user.name);
}

main();
```

### Concurrent Execution

**Python:**
```python
# Sequential (slow)
user1 = await fetch_user('1')
user2 = await fetch_user('2')

# Concurrent with gather
users = await asyncio.gather(
    fetch_user('1'),
    fetch_user('2'),
    fetch_user('3')
)

# With TaskGroup (Python 3.11+)
async with asyncio.TaskGroup() as tg:
    task1 = tg.create_task(fetch_user('1'))
    task2 = tg.create_task(fetch_user('2'))
    task3 = tg.create_task(fetch_user('3'))

users = [task1.result(), task2.result(), task3.result()]

# Handle errors separately
results = await asyncio.gather(
    fetch_user('1'),
    fetch_user('2'),
    return_exceptions=True
)
for result in results:
    if isinstance(result, Exception):
        print(f"Error: {result}")
```

**TypeScript:**
```typescript
// Sequential (slow)
const user1 = await fetchUser('1');
const user2 = await fetchUser('2');

// Concurrent with Promise.all
const users = await Promise.all([
  fetchUser('1'),
  fetchUser('2'),
  fetchUser('3')
]);

// Handle errors separately with allSettled
const results = await Promise.allSettled([
  fetchUser('1'),
  fetchUser('2'),
  fetchUser('3')
]);

for (const result of results) {
  if (result.status === 'fulfilled') {
    console.log('User:', result.value);
  } else {
    console.error('Error:', result.reason);
  }
}
```

### Async Iteration

**Python:**
```python
from typing import AsyncIterator

async def generate_pages(start: int, end: int) -> AsyncIterator[Page]:
    for i in range(start, end + 1):
        yield await fetch_page(i)

# Async iteration
async for page in generate_pages(1, 10):
    process(page)

# Async comprehension
pages = [page async for page in generate_pages(1, 10)]
```

**TypeScript:**
```typescript
async function* generatePages(start: number, end: number): AsyncIterable<Page> {
  for (let i = start; i <= end; i++) {
    yield await fetchPage(i);
  }
}

// Async iteration
for await (const page of generatePages(1, 10)) {
  process(page);
}

// Convert to array
const pages: Page[] = [];
for await (const page of generatePages(1, 10)) {
  pages.push(page);
}
```

### Timeout and Cancellation

**Python:**
```python
# Timeout with wait_for
try:
    user = await asyncio.wait_for(fetch_user('1'), timeout=5.0)
except asyncio.TimeoutError:
    print("Request timed out")

# Timeout with timeout context manager (3.11+)
try:
    async with asyncio.timeout(5.0):
        user = await fetch_user('1')
except asyncio.TimeoutError:
    print("Request timed out")

# Cancellation
task = asyncio.create_task(fetch_user('1'))
# Later...
task.cancel()
try:
    await task
except asyncio.CancelledError:
    print("Task was cancelled")
```

**TypeScript:**
```typescript
// Timeout with Promise.race
async function fetchWithTimeout<T>(
  promise: Promise<T>,
  ms: number
): Promise<T> {
  const timeout = new Promise<never>((_, reject) =>
    setTimeout(() => reject(new Error('Timeout')), ms)
  );
  return Promise.race([promise, timeout]);
}

try {
  const user = await fetchWithTimeout(fetchUser('1'), 5000);
} catch (error) {
  if (error.message === 'Timeout') {
    console.error('Request timed out');
  }
}

// Cancellation with AbortController
const controller = new AbortController();
const signal = controller.signal;

// Later...
controller.abort();

// Use with fetch
const response = await fetch(url, { signal });
```

---

## Metaprogramming Translation

### Decorators

**Python:**
```python
from functools import wraps
from typing import Callable, TypeVar, ParamSpec

P = ParamSpec('P')
T = TypeVar('T')

# Function decorator
def log_calls(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    return wrapper

@log_calls
def process_data(data: list) -> int:
    return len(data)

# Class decorator
def singleton(cls):
    instances = {}
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class Database:
    pass
```

**TypeScript:**
```typescript
// Function decorator (experimental)
function logCalls(
  target: any,
  propertyKey: string,
  descriptor: PropertyDescriptor
) {
  const original = descriptor.value;
  descriptor.value = function(...args: any[]) {
    console.log(`Calling ${propertyKey}`);
    const result = original.apply(this, args);
    console.log(`Finished ${propertyKey}`);
    return result;
  };
}

class Service {
  @logCalls
  processData(data: any[]): number {
    return data.length;
  }
}

// Class decorator
function singleton<T extends { new(...args: any[]): {} }>(constructor: T) {
  let instance: T;
  return class extends constructor {
    constructor(...args: any[]) {
      if (instance) {
        return instance;
      }
      super(...args);
      instance = this as any;
    }
  };
}

@singleton
class Database {
  // ...
}

// Higher-order function (alternative to decorators)
function logCalls<T extends (...args: any[]) => any>(fn: T): T {
  return ((...args: any[]) => {
    console.log(`Calling ${fn.name}`);
    const result = fn(...args);
    console.log(`Finished ${fn.name}`);
    return result;
  }) as T;
}

const processData = logCalls((data: any[]) => data.length);
```

### Property Access

**Python:**
```python
class Circle:
    def __init__(self, radius: float):
        self._radius = radius

    @property
    def area(self) -> float:
        return 3.14159 * self._radius ** 2

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

# Usage
circle = Circle(5)
print(circle.area)  # Computed property
circle.radius = 10  # Setter validation
```

**TypeScript:**
```typescript
class Circle {
  private _radius: number;

  constructor(radius: number) {
    this._radius = radius;
  }

  get area(): number {
    return Math.PI * this._radius ** 2;
  }

  get radius(): number {
    return this._radius;
  }

  set radius(value: number) {
    if (value < 0) {
      throw new Error("Radius cannot be negative");
    }
    this._radius = value;
  }
}

// Usage
const circle = new Circle(5);
console.log(circle.area);  // Computed property
circle.radius = 10;        // Setter validation
```

### Dynamic Attribute Access

**Python:**
```python
class DynamicObject:
    def __getattr__(self, name: str):
        return f"Dynamic: {name}"

    def __setattr__(self, name: str, value):
        super().__setattr__(name, value)

    def __delattr__(self, name: str):
        super().__delattr__(name)

# Usage
obj = DynamicObject()
print(obj.anything)  # "Dynamic: anything"
```

**TypeScript:**
```typescript
// Using Proxy for dynamic properties
function createDynamicObject() {
  return new Proxy({}, {
    get(target, prop) {
      if (prop in target) {
        return target[prop];
      }
      return `Dynamic: ${String(prop)}`;
    },
    set(target, prop, value) {
      target[prop] = value;
      return true;
    },
    deleteProperty(target, prop) {
      delete target[prop];
      return true;
    }
  });
}

// Usage
const obj = createDynamicObject();
console.log(obj.anything);  // "Dynamic: anything"
```

---

## Zero and Default Values

### Null/None Handling

| Python | TypeScript | Notes |
|--------|------------|-------|
| `None` | `null` | Explicit null |
| `None` | `undefined` | Default absence |
| `Optional[T]` | `T \| null` | Nullable value |
| `T \| None` | `T \| undefined` | Optional value |
| `Union[T, None]` | `T \| null \| undefined` | Fully optional |

**Python:**
```python
from typing import Optional

def find_user(id: str) -> Optional[User]:
    user = database.get(id)
    return user  # Can be None

# Usage - explicit None check
user = find_user('123')
if user is not None:
    print(user.name)
else:
    print("User not found")

# Or with walrus operator
if (user := find_user('123')) is not None:
    print(user.name)
```

**TypeScript:**
```typescript
function findUser(id: string): User | null {
  const user = database.get(id);
  return user ?? null;  // Convert undefined to null
}

// Usage - explicit null check
const user = findUser('123');
if (user !== null) {
  console.log(user.name);
} else {
  console.log('User not found');
}

// Optional chaining
const name = findUser('123')?.name ?? 'Unknown';

// Nullish coalescing
const user = findUser('123') ?? defaultUser;
```

### Default Values

**Python:**
```python
# Default parameter values
def greet(name: str = "World") -> str:
    return f"Hello, {name}!"

# Mutable defaults (AVOID)
def bad_append(item: str, items: list[str] = []) -> list[str]:
    items.append(item)  # Same list reused!
    return items

# Correct mutable defaults
def good_append(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items

# Dataclass defaults
from dataclasses import dataclass, field

@dataclass
class Config:
    host: str = "localhost"
    port: int = 8080
    tags: list[str] = field(default_factory=list)  # Mutable default
```

**TypeScript:**
```typescript
// Default parameter values
function greet(name: string = "World"): string {
  return `Hello, ${name}!`;
}

// Default object/array parameters (creates new instance each time)
function append(item: string, items: string[] = []): string[] {
  items.push(item);
  return items;
}

// Interface with optional properties
interface Config {
  host?: string;
  port?: number;
  tags?: string[];
}

// Default values when destructuring
function createConfig({
  host = "localhost",
  port = 8080,
  tags = []
}: Partial<Config> = {}): Config {
  return { host, port, tags };
}

// Class with defaults
class Config {
  host: string = "localhost";
  port: number = 8080;
  tags: string[] = [];  // Creates new array per instance
}
```

---

## Serialization

### JSON Serialization

**Python:**
```python
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

@dataclass
class User:
    id: str
    name: str
    email: str
    created_at: datetime

# Custom encoder for non-JSON types
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)

# Serialization
user = User("1", "Alice", "alice@example.com", datetime.now())
json_str = json.dumps(asdict(user), cls=CustomEncoder)

# Deserialization with validation
data = json.loads(json_str)
user = User(
    id=data['id'],
    name=data['name'],
    email=data['email'],
    created_at=datetime.fromisoformat(data['created_at'])
)
```

**TypeScript:**
```typescript
interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
}

// Serialization (custom replacer for Date)
const user: User = {
  id: "1",
  name: "Alice",
  email: "alice@example.com",
  createdAt: new Date()
};

const jsonStr = JSON.stringify(user, (key, value) => {
  if (value instanceof Date) {
    return value.toISOString();
  }
  return value;
});

// Deserialization (custom reviver for Date)
const data = JSON.parse(jsonStr, (key, value) => {
  if (key === 'createdAt' && typeof value === 'string') {
    return new Date(value);
  }
  return value;
}) as User;

// Better: Use a library like zod for validation
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
  createdAt: z.coerce.date()
});

const user = UserSchema.parse(data);  // Validates and transforms
```

### Pydantic → Zod

**Python (Pydantic):**
```python
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime

class User(BaseModel):
    id: str
    name: str
    email: EmailStr
    age: int
    created_at: datetime

    @validator('age')
    def validate_age(cls, v):
        if v < 0:
            raise ValueError('Age must be positive')
        return v

# Validation and serialization
user = User(
    id="1",
    name="Alice",
    email="alice@example.com",
    age=30,
    created_at=datetime.now()
)

json_str = user.model_dump_json()  # Serialize
user2 = User.model_validate_json(json_str)  # Deserialize with validation
```

**TypeScript (Zod):**
```typescript
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
  age: z.number().int().positive(),
  createdAt: z.coerce.date()
});

type User = z.infer<typeof UserSchema>;

// Validation and serialization
const user: User = {
  id: "1",
  name: "Alice",
  email: "alice@example.com",
  age: 30,
  createdAt: new Date()
};

// Validate
const validated = UserSchema.parse(user);

// Safe parse (doesn't throw)
const result = UserSchema.safeParse(user);
if (result.success) {
  console.log(result.data);
} else {
  console.error(result.error);
}

// JSON round-trip
const jsonStr = JSON.stringify(user);
const parsed = UserSchema.parse(JSON.parse(jsonStr));
```

---

## Build and Dependencies

### Package Manager Comparison

| Aspect | Python | TypeScript |
|--------|--------|------------|
| Package manager | pip, uv, poetry | npm, yarn, pnpm |
| Manifest file | `pyproject.toml`, `requirements.txt` | `package.json` |
| Lock file | `uv.lock`, `poetry.lock` | `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` |
| Virtual environment | `venv`, `virtualenv` | `node_modules` (per-project) |
| Global packages | Discouraged | Allowed with `-g` flag |

### Project Configuration

**Python (pyproject.toml):**
```toml
[project]
name = "myproject"
version = "1.0.0"
description = "A sample Python project"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
dependencies = [
    "requests>=2.31.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "ruff>=0.1.0",
    "mypy>=1.6.0",
]

[project.scripts]
mytool = "myproject.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true
```

**TypeScript (package.json + tsconfig.json):**
```json
// package.json
{
  "name": "myproject",
  "version": "1.0.0",
  "description": "A sample TypeScript project",
  "type": "module",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "test": "vitest",
    "lint": "eslint .",
    "format": "prettier --write ."
  },
  "dependencies": {
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "vitest": "^1.0.0",
    "eslint": "^8.54.0",
    "@typescript-eslint/eslint-plugin": "^6.13.0",
    "@typescript-eslint/parser": "^6.13.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2022"],
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### Dependency Installation

**Python:**
```bash
# Using pip
pip install requests pytest

# Using uv (faster)
uv add requests pytest
uv add --dev ruff mypy

# Install from requirements.txt
pip install -r requirements.txt

# Install project in editable mode
pip install -e .
```

**TypeScript:**
```bash
# Using npm
npm install axios
npm install --save-dev vitest

# Using pnpm (faster)
pnpm add axios
pnpm add -D vitest

# Install from package.json
npm install

# Global install (for CLI tools)
npm install -g typescript
```

---

## Testing

### Testing Framework Comparison

| Aspect | Python (pytest) | TypeScript (vitest/jest) |
|--------|----------------|-------------------------|
| Runner | pytest | vitest / jest |
| Assertion | assert statement | expect().toBe() |
| Fixtures | @pytest.fixture | beforeEach / fixtures |
| Mocking | unittest.mock | vi.mock() / jest.mock() |
| Coverage | pytest-cov | vitest --coverage |
| Parametrize | @pytest.mark.parametrize | test.each() |

### Basic Tests

**Python (pytest):**
```python
# test_calculator.py
import pytest

def test_addition():
    assert 1 + 1 == 2

def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        1 / 0

# Parametrized tests
@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (2, 3, 5),
    (10, 5, 15),
])
def test_addition_parametrized(a, b, expected):
    assert a + b == expected

# Fixtures
@pytest.fixture
def sample_user():
    return {"name": "Alice", "age": 30}

def test_user_data(sample_user):
    assert sample_user["name"] == "Alice"
    assert sample_user["age"] == 30
```

**TypeScript (vitest):**
```typescript
// calculator.test.ts
import { describe, it, expect, beforeEach } from 'vitest';

describe('Calculator', () => {
  it('should add numbers', () => {
    expect(1 + 1).toBe(2);
  });

  it('should throw on division by zero', () => {
    expect(() => 1 / 0).toThrow();
  });

  // Parametrized tests
  it.each([
    [1, 1, 2],
    [2, 3, 5],
    [10, 5, 15],
  ])('should add %i + %i = %i', (a, b, expected) => {
    expect(a + b).toBe(expected);
  });

  // Fixtures with beforeEach
  let sampleUser: { name: string; age: number };

  beforeEach(() => {
    sampleUser = { name: "Alice", age: 30 };
  });

  it('should have user data', () => {
    expect(sampleUser.name).toBe("Alice");
    expect(sampleUser.age).toBe(30);
  });
});
```

### Async Tests

**Python:**
```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_fetch():
    result = await fetch_user('123')
    assert result.name == "Alice"

# With timeout
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_slow_operation():
    result = await slow_operation()
    assert result is not None
```

**TypeScript:**
```typescript
import { describe, it, expect } from 'vitest';

describe('Async operations', () => {
  it('should fetch user', async () => {
    const result = await fetchUser('123');
    expect(result.name).toBe("Alice");
  });

  // With timeout
  it('should handle slow operation', async () => {
    const result = await slowOperation();
    expect(result).not.toBeNull();
  }, { timeout: 5000 });
});
```

---

## Idiom Translation

### Pattern 1: List Comprehensions → Array Methods

**Python:**
```python
# List comprehension
squares = [x**2 for x in range(10)]

# With filter
evens = [x for x in range(10) if x % 2 == 0]

# Nested
matrix = [[i+j for j in range(3)] for i in range(3)]

# Dict comprehension
word_lengths = {word: len(word) for word in ["hello", "world"]}

# Set comprehension
unique_lengths = {len(word) for word in ["hello", "world", "hi"]}
```

**TypeScript:**
```typescript
// Array map
const squares = Array.from({ length: 10 }, (_, i) => i ** 2);
// Or
const squares = [...Array(10).keys()].map(x => x ** 2);

// With filter
const evens = [...Array(10).keys()].filter(x => x % 2 === 0);

// Nested
const matrix = Array.from({ length: 3 }, (_, i) =>
  Array.from({ length: 3 }, (_, j) => i + j)
);

// Object from entries
const wordLengths = Object.fromEntries(
  ["hello", "world"].map(word => [word, word.length])
);

// Set
const uniqueLengths = new Set(["hello", "world", "hi"].map(w => w.length));
```

### Pattern 2: With Statement → Try-Finally / Using

**Python:**
```python
# Context manager
with open("file.txt") as f:
    content = f.read()
# File automatically closed

# Custom context manager
from contextlib import contextmanager

@contextmanager
def timer():
    start = time.time()
    yield
    end = time.time()
    print(f"Elapsed: {end - start:.2f}s")

with timer():
    # Code to time
    time.sleep(1)
```

**TypeScript:**
```typescript
// Try-finally pattern
let file: fs.FileHandle | null = null;
try {
  file = await fs.open("file.txt");
  const content = await file.readFile('utf-8');
} finally {
  await file?.close();
}

// Using Disposable pattern (TypeScript 5.2+)
class Timer implements Disposable {
  private start = Date.now();

  [Symbol.dispose]() {
    const end = Date.now();
    console.log(`Elapsed: ${(end - this.start) / 1000}s`);
  }
}

{
  using timer = new Timer();
  // Code to time
  await sleep(1000);
}  // Timer automatically disposed

// Async disposable
class FileHandle implements AsyncDisposable {
  async [Symbol.asyncDispose]() {
    await this.close();
  }
}

{
  await using file = await fs.open("file.txt");
  // Use file
}  // Automatically closed
```

### Pattern 3: Multiple Return Values → Tuples/Objects

**Python:**
```python
# Tuple unpacking
def get_user_stats(user_id: str) -> tuple[str, int, float]:
    name = "Alice"
    count = 42
    average = 3.14
    return name, count, average

name, count, average = get_user_stats("123")

# Named tuple
from typing import NamedTuple

class UserStats(NamedTuple):
    name: str
    count: int
    average: float

def get_user_stats(user_id: str) -> UserStats:
    return UserStats("Alice", 42, 3.14)

stats = get_user_stats("123")
print(stats.name, stats.count)
```

**TypeScript:**
```typescript
// Tuple return
function getUserStats(userId: string): [string, number, number] {
  const name = "Alice";
  const count = 42;
  const average = 3.14;
  return [name, count, average];
}

const [name, count, average] = getUserStats("123");

// Object return (preferred)
interface UserStats {
  name: string;
  count: number;
  average: number;
}

function getUserStats(userId: string): UserStats {
  return {
    name: "Alice",
    count: 42,
    average: 3.14
  };
}

const stats = getUserStats("123");
console.log(stats.name, stats.count);

// With destructuring
const { name, count } = getUserStats("123");
```

### Pattern 4: Dataclass → Interface/Type

**Python:**
```python
from dataclasses import dataclass, field

@dataclass
class User:
    id: str
    name: str
    email: str
    age: int = 0
    tags: list[str] = field(default_factory=list)

    def greet(self) -> str:
        return f"Hello, {self.name}!"

# Usage
user = User(id="1", name="Alice", email="alice@example.com")
print(user.greet())
```

**TypeScript:**
```typescript
// Interface (data only)
interface User {
  id: string;
  name: string;
  email: string;
  age?: number;
  tags?: string[];
}

// Class (with methods)
class User {
  id: string;
  name: string;
  email: string;
  age: number = 0;
  tags: string[] = [];

  constructor(data: Omit<User, 'age' | 'tags'>) {
    this.id = data.id;
    this.name = data.name;
    this.email = data.email;
  }

  greet(): string {
    return `Hello, ${this.name}!`;
  }
}

// Usage
const user = new User({
  id: "1",
  name: "Alice",
  email: "alice@example.com"
});
console.log(user.greet());

// Factory function (alternative)
function createUser(data: Omit<User, 'age' | 'tags'>): User {
  return {
    age: 0,
    tags: [],
    ...data,
    greet() {
      return `Hello, ${this.name}!`;
    }
  };
}
```

### Pattern 5: Protocol → Interface

**Python:**
```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Closeable(Protocol):
    def close(self) -> None: ...

# Structural typing - no explicit inheritance needed
class Window:
    def draw(self) -> None:
        print("Drawing window")

    def close(self) -> None:
        print("Closing window")

def render(obj: Drawable) -> None:
    obj.draw()

window = Window()
render(window)  # Works without explicit inheritance
```

**TypeScript:**
```typescript
// Interface (structural typing built-in)
interface Drawable {
  draw(): void;
}

interface Closeable {
  close(): void;
}

// Structural typing - no explicit implements needed (but recommended)
class Window implements Drawable, Closeable {
  draw(): void {
    console.log("Drawing window");
  }

  close(): void {
    console.log("Closing window");
  }
}

function render(obj: Drawable): void {
  obj.draw();
}

const window = new Window();
render(window);  // Works due to structural typing
```

### Pattern 6: Enum → Const Object or String Literal Union

**Python:**
```python
from enum import Enum, StrEnum

# Enum class
class Status(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"

# Or StrEnum (Python 3.11+)
class Status(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"

# Usage
def process(status: Status) -> None:
    if status == Status.PENDING:
        print("Pending...")
    elif status is Status.ACTIVE:
        print("Active!")

# With Literal
from typing import Literal

StatusType = Literal["pending", "active", "completed"]

def handle(status: StatusType) -> None:
    if status == "pending":
        print("Pending...")
```

**TypeScript:**
```typescript
// String enum
enum Status {
  Pending = "pending",
  Active = "active",
  Completed = "completed"
}

function process(status: Status): void {
  if (status === Status.Pending) {
    console.log("Pending...");
  } else if (status === Status.Active) {
    console.log("Active!");
  }
}

// Const object (preferred - no runtime overhead)
const Status = {
  Pending: "pending",
  Active: "active",
  Completed: "completed"
} as const;

type Status = typeof Status[keyof typeof Status];

function handle(status: Status): void {
  if (status === Status.Pending) {
    console.log("Pending...");
  }
}

// String literal union (most TypeScript-like)
type Status = "pending" | "active" | "completed";

function handleSimple(status: Status): void {
  switch (status) {
    case "pending":
      console.log("Pending...");
      break;
    case "active":
      console.log("Active!");
      break;
    case "completed":
      console.log("Completed!");
      break;
  }
}
```

### Pattern 7: Generators → Generator Functions

**Python:**
```python
def fibonacci(n: int):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# Usage
for num in fibonacci(10):
    print(num)

# Generator expression
squares = (x**2 for x in range(10))
```

**TypeScript:**
```typescript
function* fibonacci(n: number): Generator<number> {
  let [a, b] = [0, 1];
  for (let i = 0; i < n; i++) {
    yield a;
    [a, b] = [b, a + b];
  }
}

// Usage
for (const num of fibonacci(10)) {
  console.log(num);
}

// No generator expression equivalent - use Array methods
const squares = Array.from({ length: 10 }, (_, i) => i ** 2);
```

---

## Common Pitfalls

### 1. Python `None` → TypeScript `null` vs `undefined`

**Problem:** Python has one "null" value (`None`), TypeScript has two (`null` and `undefined`).

**Python:**
```python
def find_user(id: str) -> User | None:
    # ...
    return None  # Only one way to represent "no value"
```

**TypeScript:**
```typescript
// Need to decide: null or undefined?
function findUser(id: string): User | null {
  return null;  // Explicit absence
}

// Or
function findUser(id: string): User | undefined {
  return undefined;  // Implicit absence (default)
}

// Often both are possible
function findUser(id: string): User | null | undefined {
  // ...
}
```

**Solution:** Choose a convention:
- Use `null` for explicit "not found" cases
- Use `undefined` for optional/uninitialized values
- Or stick to one consistently (prefer `undefined` for simplicity)

### 2. Mutable vs Immutable Collections

**Problem:** Python's mutable defaults vs TypeScript's const behavior.

**Python:**
```python
# Mutable list
items = [1, 2, 3]
items.append(4)  # Modifies in place

# To make immutable, use tuple
items = (1, 2, 3)  # Cannot be modified
```

**TypeScript:**
```typescript
// const reference, but mutable content
const items = [1, 2, 3];
items.push(4);  // Works! const doesn't freeze content

// To make immutable
const items: readonly number[] = [1, 2, 3];
items.push(4);  // Error: push doesn't exist on readonly array

// Or use as const
const items = [1, 2, 3] as const;
items.push(4);  // Error
```

**Solution:** Use `readonly` for truly immutable arrays in TypeScript.

### 3. Truthy/Falsy Values

**Problem:** Different falsy values between languages.

**Python:**
```python
# Python falsy values: None, False, 0, "", [], {}, ()
if user:  # False for None or empty dict
    print(user.name)

# Be explicit
if user is not None:  # Only checks None
    print(user.name)
```

**TypeScript:**
```typescript
// TypeScript falsy: null, undefined, false, 0, "", NaN
if (user) {  // False for null, undefined, or empty object
  console.log(user.name);
}

// Be explicit
if (user !== null && user !== undefined) {
  console.log(user.name);
}

// Or use nullish coalescing
const name = user?.name ?? "Unknown";
```

**Solution:** Use explicit comparisons when the distinction matters.

### 4. Integer Division

**Problem:** Python has floor division (`//`), TypeScript only has float division.

**Python:**
```python
result = 5 / 2   # 2.5 (float division)
result = 5 // 2  # 2 (floor division)
```

**TypeScript:**
```typescript
const result = 5 / 2;           // 2.5 (always float)
const floored = Math.floor(5 / 2);  // 2 (explicit floor)
const truncated = Math.trunc(5 / 2); // 2 (toward zero)
```

**Solution:** Use `Math.floor()` or `Math.trunc()` in TypeScript for integer division.

### 5. Class Properties Initialization

**Problem:** Python requires `__init__`, TypeScript allows class-level initialization.

**Python:**
```python
class Counter:
    # Class variable (shared across instances!)
    count = 0

    def __init__(self, initial: int = 0):
        # Instance variable (per-instance)
        self.count = initial
```

**TypeScript:**
```typescript
class Counter {
  // Instance property (per-instance by default)
  count: number = 0;

  // Static property (shared across instances)
  static globalCount: number = 0;

  constructor(initial: number = 0) {
    this.count = initial;
  }
}
```

**Solution:** Understand that TypeScript class properties are instance variables by default, unlike Python.

### 6. String Formatting

**Problem:** Python f-strings vs TypeScript template literals.

**Python:**
```python
name = "Alice"
age = 30
message = f"Hello, {name}! You are {age} years old."

# Multi-line
message = f"""
Hello, {name}!
You are {age} years old.
"""
```

**TypeScript:**
```typescript
const name = "Alice";
const age = 30;
const message = `Hello, ${name}! You are ${age} years old.`;

// Multi-line (indentation matters!)
const message = `
Hello, ${name}!
You are ${age} years old.
`;
```

**Solution:** Both support similar template syntax, but TypeScript preserves all whitespace.

### 7. Dictionary/Object Property Access

**Problem:** Python raises KeyError, TypeScript returns undefined.

**Python:**
```python
user = {"name": "Alice"}
email = user["email"]  # KeyError!

# Safe access
email = user.get("email")  # None
email = user.get("email", "default@example.com")  # Default value
```

**TypeScript:**
```typescript
const user = { name: "Alice" };
const email = user["email"];  // undefined (no error)
const email2 = user.email;     // undefined (no error)

// With strict types
interface User {
  name: string;
  email?: string;  // Explicitly optional
}

const user: User = { name: "Alice" };
const email = user.email;  // string | undefined

// Nullish coalescing for default
const email = user.email ?? "default@example.com";
```

**Solution:** TypeScript's optional properties provide type safety, but always returns `undefined` for missing keys.

### 8. Import Side Effects

**Problem:** Python executes module on first import, TypeScript has clearer side-effect semantics.

**Python:**
```python
# config.py
print("Loading config...")  # Executes on first import
DATABASE_URL = "..."

# main.py
import config  # Prints "Loading config..."
import config  # Does NOT print again (cached)
```

**TypeScript:**
```typescript
// config.ts
console.log("Loading config...");  // Executes on first import
export const DATABASE_URL = "...";

// main.ts
import { DATABASE_URL } from './config';  // Prints "Loading config..."
import './config';  // Side-effect import (explicit)
```

**Solution:** Both cache modules, but TypeScript makes side-effect imports more explicit.

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| **TypeScript Compiler (tsc)** | Type checking and transpilation | Core TypeScript tool |
| **ts-node** | Run TypeScript directly | Development convenience |
| **vitest** | Testing framework | Modern, fast test runner |
| **zod** | Runtime validation | Like pydantic for TypeScript |
| **prettier** | Code formatting | Opinionated formatter |
| **eslint** | Linting | Code quality checks |
| **type-fest** | Utility types | Extended type utilities |
| **axios** | HTTP client | Like requests for Python |
| **date-fns** | Date manipulation | Alternative to Python datetime |
| **lodash** | Utility functions | Functional programming helpers |

### Type Checking Setup

**tsconfig.json:**
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

### Linting Setup

**.eslintrc.json:**
```json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/recommended-requiring-type-checking"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "project": "./tsconfig.json"
  },
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }]
  }
}
```

---

## Examples

### Example 1: Simple - HTTP Request Function

**Before (Python):**
```python
import httpx
from dataclasses import dataclass

@dataclass
class User:
    id: str
    name: str
    email: str

async def fetch_user(id: str) -> User:
    async with httpx.AsyncClient() as client:
        response = await client.get(f'https://api.example.com/users/{id}')

        if not response.is_success:
            raise Exception(f"HTTP {response.status_code}")

        data = response.json()
        return User(**data)

# Usage
async def main():
    try:
        user = await fetch_user('123')
        print(user.name)
    except Exception as error:
        print(f'Failed: {error}')

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
```

**After (TypeScript):**
```typescript
interface User {
  id: string;
  name: string;
  email: string;
}

async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`https://api.example.com/users/${id}`);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  return await response.json();
}

// Usage (top-level await in modules)
try {
  const user = await fetchUser('123');
  console.log(user.name);
} catch (error) {
  console.error('Failed:', error);
}
```

### Example 2: Medium - Data Processing Pipeline

**Before (Python):**
```python
from dataclasses import dataclass
from typing import NamedTuple

@dataclass
class Product:
    id: str
    name: str
    price: float
    category: str
    in_stock: bool

class CategoryStats(NamedTuple):
    category: str
    count: int
    average_price: float
    total_value: float

def analyze_products(products: list[Product]) -> list[CategoryStats]:
    from collections import defaultdict
    from operator import attrgetter

    # Group by category
    grouped: dict[str, list[Product]] = defaultdict(list)
    for product in products:
        if product.in_stock:
            grouped[product.category].append(product)

    # Calculate statistics
    stats = []
    for category, items in grouped.items():
        total_price = sum(item.price for item in items)
        count = len(items)
        stats.append(CategoryStats(
            category=category,
            count=count,
            average_price=total_price / count,
            total_value=total_price
        ))

    return sorted(stats, key=attrgetter('total_value'), reverse=True)

# Usage
stats = analyze_products(products)
for s in stats:
    print(f"{s.category}: {s.count} items, avg ${s.average_price:.2f}")
```

**After (TypeScript):**
```typescript
interface Product {
  id: string;
  name: string;
  price: number;
  category: string;
  inStock: boolean;
}

interface CategoryStats {
  category: string;
  count: number;
  averagePrice: number;
  totalValue: number;
}

function analyzeProducts(products: Product[]): CategoryStats[] {
  // Group by category
  const grouped = new Map<string, Product[]>();
  for (const product of products) {
    if (product.inStock) {
      const items = grouped.get(product.category) ?? [];
      items.push(product);
      grouped.set(product.category, items);
    }
  }

  // Calculate statistics
  const stats: CategoryStats[] = [];
  for (const [category, items] of grouped.entries()) {
    const totalPrice = items.reduce((sum, item) => sum + item.price, 0);
    const count = items.length;
    stats.push({
      category,
      count,
      averagePrice: totalPrice / count,
      totalValue: totalPrice
    });
  }

  // Sort by total value descending
  return stats.sort((a, b) => b.totalValue - a.totalValue);
}

// Usage
const stats = analyzeProducts(products);
for (const s of stats) {
  console.log(`${s.category}: ${s.count} items, avg $${s.averagePrice.toFixed(2)}`);
}
```

### Example 3: Complex - Generic Repository with Caching

**Before (Python):**
```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Generic, TypeVar, Protocol, Callable, Awaitable
from collections import OrderedDict
import asyncio

class Entity(Protocol):
    id: str
    created_at: datetime
    updated_at: datetime

@dataclass
class User:
    id: str
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

T = TypeVar('T', bound=Entity)

@dataclass
class CacheOptions:
    ttl_seconds: int = 300
    max_size: int = 100

@dataclass
class CacheEntry(Generic[T]):
    value: T
    expires_at: datetime

class CachedRepository(Generic[T]):
    def __init__(
        self,
        fetch_fn: Callable[[str], Awaitable[T]],
        options: CacheOptions | None = None
    ):
        self._fetch_fn = fetch_fn
        self._options = options or CacheOptions()
        self._cache: OrderedDict[str, CacheEntry[T]] = OrderedDict()
        self._ttl = timedelta(seconds=self._options.ttl_seconds)
        self._max_size = self._options.max_size

    async def get(self, id: str) -> T | None:
        # Check cache
        cached = self._cache.get(id)
        if cached and cached.expires_at > datetime.now():
            self._cache.move_to_end(id)
            return cached.value

        # Fetch from source
        try:
            value = await self._fetch_fn(id)
            self._set(id, value)
            return value
        except Exception as error:
            if hasattr(error, 'status') and error.status == 404:
                return None
            raise

    async def get_many(self, ids: list[str]) -> dict[str, T]:
        results = await asyncio.gather(
            *[self._fetch_with_id(id) for id in ids],
            return_exceptions=False
        )
        return {
            id: value
            for id, value in results
            if value is not None
        }

    async def _fetch_with_id(self, id: str) -> tuple[str, T | None]:
        value = await self.get(id)
        return (id, value)

    def _set(self, id: str, value: T) -> None:
        if len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)

        self._cache[id] = CacheEntry(
            value=value,
            expires_at=datetime.now() + self._ttl
        )

    def invalidate(self, id: str) -> None:
        self._cache.pop(id, None)

    def clear(self) -> None:
        self._cache.clear()
```

**After (TypeScript):**
```typescript
interface Entity {
  id: string;
  createdAt: Date;
  updatedAt: Date;
}

interface User extends Entity {
  name: string;
  email: string;
}

interface CacheOptions {
  ttlSeconds: number;
  maxSize: number;
}

interface CacheEntry<T> {
  value: T;
  expiresAt: number;
}

class CachedRepository<T extends Entity> {
  private cache: Map<string, CacheEntry<T>> = new Map();
  private readonly ttl: number;
  private readonly maxSize: number;

  constructor(
    private readonly fetchFn: (id: string) => Promise<T>,
    options: CacheOptions = { ttlSeconds: 300, maxSize: 100 }
  ) {
    this.ttl = options.ttlSeconds * 1000;
    this.maxSize = options.maxSize;
  }

  async get(id: string): Promise<T | null> {
    // Check cache
    const cached = this.cache.get(id);
    if (cached && cached.expiresAt > Date.now()) {
      // Move to end (LRU)
      this.cache.delete(id);
      this.cache.set(id, cached);
      return cached.value;
    }

    // Fetch from source
    try {
      const value = await this.fetchFn(id);
      this.set(id, value);
      return value;
    } catch (error) {
      if (error.status === 404) {
        return null;
      }
      throw error;
    }
  }

  async getMany(ids: string[]): Promise<Map<string, T>> {
    const results = await Promise.all(
      ids.map(async id => ({ id, value: await this.get(id) }))
    );

    return new Map(
      results
        .filter(r => r.value !== null)
        .map(r => [r.id, r.value!])
    );
  }

  private set(id: string, value: T): void {
    // Evict oldest if at capacity
    if (this.cache.size >= this.maxSize) {
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }

    this.cache.set(id, {
      value,
      expiresAt: Date.now() + this.ttl
    });
  }

  invalidate(id: string): void {
    this.cache.delete(id);
  }

  clear(): void {
    this.cache.clear();
  }
}

// Usage
async function fetchUserFromApi(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) {
    throw Object.assign(new Error(`HTTP ${response.status}`), {
      status: response.status
    });
  }
  return await response.json();
}

const userRepo = new CachedRepository(fetchUserFromApi, {
  ttlSeconds: 600,
  maxSize: 50
});

// Fetch single user
const user = await userRepo.get('123');
if (user) {
  console.log(`Found user: ${user.name}`);
}

// Fetch multiple users
const users = await userRepo.getMany(['1', '2', '3']);
for (const [id, user] of users) {
  console.log(`${id}: ${user.name}`);
}
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `lang-python-dev` - Python development patterns
- `lang-typescript-patterns-dev` - TypeScript development patterns

Cross-cutting pattern skills (for areas not fully covered by lang-*-dev):
- `patterns-concurrency-dev` - Async, channels, threads across languages
- `patterns-serialization-dev` - JSON, validation, struct tags across languages
- `patterns-metaprogramming-dev` - Decorators, macros, annotations across languages
