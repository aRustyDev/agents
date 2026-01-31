---
name: convert-typescript-python
description: Convert TypeScript code to idiomatic Python. Use when migrating TypeScript projects to Python, translating TypeScript patterns to Pythonic idioms, or refactoring TypeScript codebases into Python. Extends meta-convert-dev with TypeScript-to-Python specific patterns.
---

# Convert TypeScript to Python

Convert TypeScript code to idiomatic Python. This skill extends `meta-convert-dev` with TypeScript-to-Python specific type mappings, idiom translations, and tooling.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: TypeScript types → Python types (with type hints)
- **Idiom translations**: TypeScript patterns → Pythonic idioms
- **Error handling**: TypeScript exceptions → Python exceptions (different patterns)
- **Async patterns**: Promise/async-await → asyncio
- **Type system differences**: Static structural typing → dynamic duck typing

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- TypeScript language fundamentals - see `lang-typescript-dev`
- Python language fundamentals - see `lang-python-dev`
- Reverse conversion (Python → TypeScript) - see `convert-python-typescript`

---

## Quick Reference

| TypeScript | Python | Notes |
|------------|--------|-------|
| `string` | `str` | Unicode strings |
| `number` | `int` / `float` | Specify precision |
| `boolean` | `bool` | Same concept |
| `Array<T>` / `T[]` | `list[T]` | Mutable sequence |
| `readonly T[]` | `tuple[T, ...]` | Immutable sequence |
| `Record<K, V>` | `dict[K, V]` | Key-value mapping |
| `T \| null` | `T \| None` / `Optional[T]` | Nullable types |
| `Promise<T>` | `Coroutine[Any, Any, T]` | Async operations |
| `interface X` | `class X` / `Protocol` | Structure definition |
| `enum X` | `Enum` / `Literal` | Enumerated values |

## When Converting Code

1. **Analyze source thoroughly** before writing Python
2. **Map types first** - TypeScript types → Python type hints
3. **Preserve semantics** over syntax similarity
4. **Adopt Python idioms** - don't write "TypeScript code in Python syntax"
5. **Handle edge cases** - undefined/null → None, falsy values
6. **Test equivalence** - same inputs → same outputs

---

## Type System Mapping

### Primitive Types

| TypeScript | Python | Notes |
|------------|--------|-------|
| `string` | `str` | Unicode by default in both |
| `number` | `int` | For integers |
| `number` | `float` | For floating-point |
| `bigint` | `int` | Python has arbitrary-precision integers |
| `boolean` | `bool` | Capitalized (True/False) in Python |
| `null` | `None` | Singleton null value |
| `undefined` | `None` | Both map to None in Python |
| `void` | `None` | Function return type |
| `any` | `Any` | Escape hatch (avoid when possible) |
| `unknown` | `Any` / `object` | Prefer object for constraints |
| `never` | `NoReturn` | Function never returns |
| `symbol` | - | No direct equivalent (use strings) |

### Collection Types

| TypeScript | Python | Notes |
|------------|--------|-------|
| `T[]` / `Array<T>` | `list[T]` | Mutable, ordered |
| `readonly T[]` | `tuple[T, ...]` / `Sequence[T]` | Immutable sequence |
| `[T, U]` | `tuple[T, U]` | Fixed-size tuple |
| `Set<T>` | `set[T]` | Unique values, unordered |
| `Map<K, V>` | `dict[K, V]` | Key-value mapping |
| `Record<K, V>` | `dict[K, V]` | Type-safe object |
| `WeakMap<K, V>` | `weakref.WeakValueDictionary` | Weak references |
| `ReadonlyMap<K, V>` | `Mapping[K, V]` | Immutable view |
| `ReadonlySet<T>` | `frozenset[T]` / `AbstractSet[T]` | Immutable set |

### Composite Types

| TypeScript | Python | Notes |
|------------|--------|-------|
| `interface X { ... }` | `class X:` / `TypedDict` | Data class or typed dict |
| `type X = Y \| Z` | `X = Y \| Z` | Union types (3.10+) |
| `type X = Y & Z` | Multiple inheritance / Protocol | Intersection via inheritance |
| `T \| null` | `T \| None` / `Optional[T]` | Nullable types |
| `Partial<T>` | TypedDict with `total=False` | All fields optional |
| `Required<T>` | TypedDict with `total=True` | All fields required |
| `Pick<T, K>` | TypedDict subset | Manual definition |
| `Omit<T, K>` | TypedDict subset | Manual definition |
| `ReturnType<T>` | Function annotations | Infer from function signature |

### Generic Types

| TypeScript | Python | Notes |
|------------|--------|-------|
| `<T>` | `[T]` (3.12+) / `TypeVar('T')` | Generic type parameter |
| `<T extends U>` | `TypeVar('T', bound=U)` | Bounded type variable |
| `<T extends A \| B>` | `TypeVar('T', A, B)` | Constrained type variable |
| `<T = Default>` | `[T = Default]` (3.13+) | Default type parameter |
| `keyof T` | `Literal[...]` | String literal union |
| `T[K]` | `@overload` / `__getitem__` | Index access type |

---

## Idiom Translation

### Pattern 1: Optional Chaining & Nullish Coalescing

**TypeScript:**
```typescript
const name = user?.profile?.name ?? "Anonymous";
const age = user?.age ?? 0;
```

**Python:**
```python
name = (user.profile.name if user and user.profile else None) or "Anonymous"
# Better with walrus operator (3.8+)
name = (profile.name if (profile := getattr(user, 'profile', None)) else None) or "Anonymous"

# Or using helper
from operator import attrgetter
name = attrgetter('profile.name')(user) if user else "Anonymous"

# Most Pythonic: use get() for dicts, getattr() for objects
name = getattr(getattr(user, 'profile', None), 'name', None) or "Anonymous"
```

**Why this translation:**
- Python doesn't have built-in optional chaining
- `or` operator works for default values but watch for falsy values (0, "", [], etc.)
- Explicit None checks are more Pythonic than chaining
- Consider using `getattr()` with defaults for cleaner code

### Pattern 2: Array/List Methods

**TypeScript:**
```typescript
const result = items
  .filter(x => x.active)
  .map(x => x.value)
  .reduce((sum, val) => sum + val, 0);
```

**Python:**
```python
# List comprehension (most Pythonic)
result = sum(x.value for x in items if x.active)

# Or step by step
result = sum(
    x.value
    for x in items
    if x.active
)

# Functional style (less Pythonic)
from functools import reduce
result = reduce(
    lambda sum, val: sum + val,
    map(lambda x: x.value, filter(lambda x: x.active, items)),
    0
)
```

**Why this translation:**
- List comprehensions and generator expressions are the Pythonic way
- More readable and often faster than map/filter chains
- Built-in functions like `sum()`, `any()`, `all()` are preferred
- Avoid `reduce()` unless necessary (explicit loops are clearer)

### Pattern 3: Object Destructuring

**TypeScript:**
```typescript
const { name, age, ...rest } = user;
const [first, second, ...others] = items;
```

**Python:**
```python
# Dictionary unpacking
name = user['name']
age = user['age']
rest = {k: v for k, v in user.items() if k not in ('name', 'age')}

# Or with destructuring (dataclasses)
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    extra: dict

# List unpacking
first, second, *others = items

# Named tuple unpacking
from typing import NamedTuple

class Point(NamedTuple):
    x: int
    y: int

p = Point(1, 2)
x, y = p  # Unpacking
```

**Why this translation:**
- Python has tuple unpacking with `*` (PEP 3132)
- Dict comprehension for "rest" pattern
- Dataclasses/NamedTuples provide structure with unpacking
- No built-in object rest spread like TypeScript

### Pattern 4: Async/Await

**TypeScript:**
```typescript
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  const data = await response.json();
  return data;
}

const users = await Promise.all(ids.map(id => fetchUser(id)));
```

**Python:**
```python
import asyncio
import aiohttp

async def fetch_user(id: str) -> User:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'/api/users/{id}') as response:
            data = await response.json()
            return User(**data)

# Concurrent execution
users = await asyncio.gather(*[fetch_user(id) for id in ids])

# Or with TaskGroup (3.11+)
async with asyncio.TaskGroup() as tg:
    tasks = [tg.create_task(fetch_user(id)) for id in ids]
users = [task.result() for task in tasks]
```

**Why this translation:**
- Python's `async/await` is similar but requires explicit event loop
- `asyncio.gather()` is equivalent to `Promise.all()`
- Context managers (`async with`) for resource management
- TaskGroup provides structured concurrency (Python 3.11+)

### Pattern 5: Class & Interface

**TypeScript:**
```typescript
interface Repository {
  save(item: Item): Promise<void>;
  findById(id: string): Promise<Item | null>;
}

class ItemRepository implements Repository {
  async save(item: Item): Promise<void> {
    // implementation
  }

  async findById(id: string): Promise<Item | null> {
    // implementation
  }
}
```

**Python:**
```python
from abc import ABC, abstractmethod
from typing import Protocol, Optional

# Option 1: Protocol (structural typing, like TS interface)
class Repository(Protocol):
    async def save(self, item: Item) -> None: ...
    async def findById(self, id: str) -> Optional[Item]: ...

# Option 2: ABC (nominal typing, explicit inheritance)
class RepositoryBase(ABC):
    @abstractmethod
    async def save(self, item: Item) -> None:
        pass

    @abstractmethod
    async def findById(self, id: str) -> Optional[Item]:
        pass

# Implementation
class ItemRepository:  # Protocol doesn't require inheritance
    async def save(self, item: Item) -> None:
        # implementation
        pass

    async def findById(self, id: str) -> Optional[Item]:
        # implementation
        return None

# Or with ABC
class ItemRepository(RepositoryBase):
    async def save(self, item: Item) -> None:
        pass

    async def findById(self, id: str) -> Optional[Item]:
        return None
```

**Why this translation:**
- `Protocol` provides structural typing (like TypeScript interfaces)
- `ABC` provides nominal typing (explicit inheritance required)
- Use `Protocol` for duck typing, `ABC` for strict contracts
- Python 3.8+ supports `Protocol` from `typing`

### Pattern 6: Enum Types

**TypeScript:**
```typescript
enum Status {
  Pending = "pending",
  Active = "active",
  Completed = "completed"
}

type StatusType = Status.Pending | Status.Active;
```

**Python:**
```python
from enum import Enum, auto
from typing import Literal

# Option 1: Enum class
class Status(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"

# Option 2: StrEnum (3.11+)
from enum import StrEnum

class Status(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"

# Option 3: Literal types
StatusType = Literal["pending", "active", "completed"]

# Subset type
ActiveStatus = Literal["pending", "active"]

# Usage
def process(status: Status) -> None:
    if status == Status.PENDING:
        ...
    elif status is Status.ACTIVE:  # Use 'is' for enum comparison
        ...

# With Literal
def handle(status: StatusType) -> None:
    if status == "pending":
        ...
```

**Why this translation:**
- `Enum` provides type-safe enumerations with methods
- `Literal` types for simple string/int unions
- `StrEnum` (Python 3.11+) for string enums that compare as strings
- Use `is` for enum comparisons (identity), `==` for Literal

### Pattern 7: Error Handling

**TypeScript:**
```typescript
class ValidationError extends Error {
  constructor(message: string, public field: string) {
    super(message);
    this.name = "ValidationError";
  }
}

function validateUser(user: User): void {
  if (!user.email) {
    throw new ValidationError("Email required", "email");
  }
}

try {
  validateUser(user);
} catch (error) {
  if (error instanceof ValidationError) {
    console.error(`Field ${error.field}: ${error.message}`);
  } else {
    throw error;
  }
}
```

**Python:**
```python
class ValidationError(ValueError):
    """Raised when validation fails"""
    def __init__(self, message: str, field: str):
        super().__init__(message)
        self.field = field

def validate_user(user: User) -> None:
    if not user.email:
        raise ValidationError("Email required", field="email")

# Exception handling
try:
    validate_user(user)
except ValidationError as error:
    print(f"Field {error.field}: {error}")
except Exception:
    raise  # Re-raise if not ValidationError

# Context manager for cleanup
from contextlib import contextmanager

@contextmanager
def transaction():
    try:
        yield
    except Exception:
        rollback()
        raise
    else:
        commit()

with transaction():
    validate_user(user)
```

**Why this translation:**
- Both use exception-based error handling
- Python exceptions inherit from `Exception` (or specific types)
- Type checking with `isinstance()` or specific `except` clause
- Context managers (`with` statement) for resource cleanup
- Python has no `finally` equivalent to TS but uses `finally` block

### Pattern 8: Type Guards & Narrowing

**TypeScript:**
```typescript
function isString(value: unknown): value is string {
  return typeof value === "string";
}

function process(value: string | number) {
  if (typeof value === "string") {
    console.log(value.toUpperCase());
  } else {
    console.log(value.toFixed(2));
  }
}
```

**Python:**
```python
from typing import TypeGuard, Union

def is_string(value: object) -> TypeGuard[str]:
    return isinstance(value, str)

def process(value: Union[str, float]) -> None:
    if isinstance(value, str):
        print(value.upper())
    else:
        print(f"{value:.2f}")

# Pattern matching (3.10+)
match value:
    case str():
        print(value.upper())
    case float() | int():
        print(f"{value:.2f}")
    case _:
        raise TypeError(f"Unexpected type: {type(value)}")

# Type narrowing with assert
from typing import assert_never

def handle(value: str | int | None) -> None:
    if value is None:
        return
    elif isinstance(value, str):
        print(value.upper())
    elif isinstance(value, int):
        print(value * 2)
    else:
        assert_never(value)  # Exhaustiveness check
```

**Why this translation:**
- `TypeGuard` (Python 3.10+) for type guard functions
- `isinstance()` for runtime type checking with narrowing
- Pattern matching (3.10+) for structural matching
- `assert_never()` for exhaustiveness checking

### Pattern 9: Decorators & Metadata

**TypeScript:**
```typescript
function logged(target: any, key: string, descriptor: PropertyDescriptor) {
  const original = descriptor.value;
  descriptor.value = function(...args: any[]) {
    console.log(`Calling ${key} with`, args);
    return original.apply(this, args);
  };
}

class Service {
  @logged
  process(data: string) {
    return data.toUpperCase();
  }
}
```

**Python:**
```python
from functools import wraps
from typing import Callable, TypeVar, ParamSpec

P = ParamSpec('P')
T = TypeVar('T')

def logged(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        print(f"Calling {func.__name__} with {args}, {kwargs}")
        return func(*args, **kwargs)
    return wrapper

class Service:
    @logged
    def process(self, data: str) -> str:
        return data.upper()

# Property decorator
class Config:
    def __init__(self, value: int):
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, val: int) -> None:
        if val < 0:
            raise ValueError("Must be positive")
        self._value = val

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

**Why this translation:**
- Python decorators use `@` syntax like TypeScript
- `@wraps` preserves function metadata
- `ParamSpec` and `TypeVar` for type-safe decorators
- Property decorators for getters/setters
- Class decorators for metaprogramming

### Pattern 10: Modules & Imports

**TypeScript:**
```typescript
// math.ts
export function add(a: number, b: number): number {
  return a + b;
}

export default class Calculator {
  // ...
}

// main.ts
import Calculator, { add } from './math';
import * as math from './math';
```

**Python:**
```python
# math.py
def add(a: float, b: float) -> float:
    return a + b

class Calculator:
    pass

# Explicit public API
__all__ = ['add', 'Calculator']

# main.py
from math import add, Calculator  # Named imports
import math  # Module import
from math import *  # Import all (not recommended)

# Conditional imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from expensive_module import HeavyClass  # Type-only import

# Lazy import
def process():
    import heavy_module  # Imported only when function called
    return heavy_module.process()
```

**Why this translation:**
- Python has no "default export" - all exports are named
- `__all__` defines public API (like explicit exports)
- `TYPE_CHECKING` for type-only imports (avoid circular deps)
- Python imports are executed once and cached
- Lazy imports for optional dependencies

---

## Error Handling

### TypeScript Error Model → Python Error Model

Both TypeScript and Python use exception-based error handling, but with different patterns and conventions.

| Aspect | TypeScript | Python |
|--------|-----------|---------|
| Base class | `Error` | `Exception` |
| Try-catch | `try/catch/finally` | `try/except/else/finally` |
| Throwing | `throw new Error()` | `raise Exception()` |
| Re-throwing | `throw` | `raise` (without args) |
| Type checking | `instanceof` | `isinstance()` or specific except |

### Exception Hierarchy Translation

**TypeScript:**
```typescript
class AppError extends Error {
  constructor(message: string) {
    super(message);
    this.name = this.constructor.name;
  }
}

class NotFoundError extends AppError {
  constructor(resource: string) {
    super(`${resource} not found`);
  }
}

class ValidationError extends AppError {
  constructor(message: string, public errors: string[]) {
    super(message);
  }
}
```

**Python:**
```python
class AppError(Exception):
    """Base exception for application errors"""
    pass

class NotFoundError(AppError):
    """Raised when a resource is not found"""
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found")
        self.resource = resource

class ValidationError(AppError):
    """Raised when validation fails"""
    def __init__(self, message: str, errors: list[str]):
        super().__init__(message)
        self.errors = errors

# Using standard library base classes
class ConfigError(ValueError):
    """Inherit from ValueError for invalid values"""
    pass

class NetworkError(IOError):
    """Inherit from IOError for I/O failures"""
    pass
```

### Error Handling Patterns

**TypeScript:**
```typescript
async function loadConfig(path: string): Promise<Config> {
  try {
    const content = await fs.promises.readFile(path, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    if (error instanceof SyntaxError) {
      throw new ConfigError(`Invalid JSON in ${path}`, error);
    } else if (error.code === 'ENOENT') {
      throw new NotFoundError(path);
    } else {
      throw error;
    }
  }
}
```

**Python:**
```python
import json
from pathlib import Path

async def load_config(path: str) -> Config:
    try:
        content = await asyncio.to_thread(Path(path).read_text)
        data = json.loads(content)
        return Config(**data)
    except json.JSONDecodeError as error:
        raise ConfigError(f"Invalid JSON in {path}") from error
    except FileNotFoundError:
        raise NotFoundError(path) from None
    except Exception:
        raise  # Re-raise unexpected errors

# Exception chaining with 'from'
try:
    result = parse_data(raw)
except ValueError as error:
    raise ValidationError("Invalid data") from error  # Chain exception

# Suppress original exception with 'from None'
try:
    result = fetch_data()
except RequestError:
    raise ServiceUnavailable() from None  # Hide implementation detail
```

### Context Managers for Cleanup

**TypeScript:**
```typescript
class Connection {
  async connect(): Promise<void> { /* ... */ }
  async disconnect(): Promise<void> { /* ... */ }

  async withConnection<T>(fn: () => Promise<T>): Promise<T> {
    await this.connect();
    try {
      return await fn();
    } finally {
      await this.disconnect();
    }
  }
}

await connection.withConnection(async () => {
  // use connection
});
```

**Python:**
```python
from contextlib import asynccontextmanager

class Connection:
    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    # Context manager protocol
    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
        return False  # Don't suppress exceptions

# Usage
async with Connection() as conn:
    # use connection
    pass

# Function-based context manager
@asynccontextmanager
async def get_connection():
    conn = Connection()
    await conn.connect()
    try:
        yield conn
    finally:
        await conn.disconnect()

async with get_connection() as conn:
    # use connection
    pass
```

---

## Concurrency Patterns

### TypeScript Async → Python Asyncio

Both languages support `async/await`, but Python requires explicit event loop management and has different primitives.

| Aspect | TypeScript | Python |
|--------|-----------|---------|
| Runtime | V8 event loop (built-in) | asyncio event loop (explicit) |
| Promise | `Promise<T>` | `Coroutine[Any, Any, T]` |
| Concurrent | `Promise.all()` | `asyncio.gather()` |
| Race | `Promise.race()` | `asyncio.wait(..., FIRST_COMPLETED)` |
| Sequential | `await` each | `await` each |
| Timeout | `Promise.race()` + timeout | `asyncio.wait_for()` |

### Basic Async Functions

**TypeScript:**
```typescript
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch user ${id}`);
  }
  return await response.json();
}

// Sequential
const user1 = await fetchUser('1');
const user2 = await fetchUser('2');

// Concurrent
const [user1, user2] = await Promise.all([
  fetchUser('1'),
  fetchUser('2')
]);
```

**Python:**
```python
import aiohttp
import asyncio

async def fetch_user(id: str) -> User:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'/api/users/{id}') as response:
            if not response.ok:
                raise Exception(f"Failed to fetch user {id}")
            data = await response.json()
            return User(**data)

# Sequential
user1 = await fetch_user('1')
user2 = await fetch_user('2')

# Concurrent
user1, user2 = await asyncio.gather(
    fetch_user('1'),
    fetch_user('2')
)

# With TaskGroup (3.11+) - preferred for structured concurrency
async with asyncio.TaskGroup() as tg:
    task1 = tg.create_task(fetch_user('1'))
    task2 = tg.create_task(fetch_user('2'))
user1 = task1.result()
user2 = task2.result()
```

### Async Iteration & Streams

**TypeScript:**
```typescript
async function* generatePages(start: number, end: number) {
  for (let i = start; i <= end; i++) {
    yield await fetchPage(i);
  }
}

for await (const page of generatePages(1, 10)) {
  process(page);
}
```

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

# Async generator expression
total = sum(page.size async for page in generate_pages(1, 10))
```

### Timeout & Cancellation

**TypeScript:**
```typescript
async function fetchWithTimeout<T>(
  promise: Promise<T>,
  ms: number
): Promise<T> {
  const timeout = new Promise<never>((_, reject) =>
    setTimeout(() => reject(new Error('Timeout')), ms)
  );
  return Promise.race([promise, timeout]);
}

const user = await fetchWithTimeout(fetchUser('1'), 5000);
```

**Python:**
```python
async def fetch_with_timeout(coro, seconds: float):
    try:
        return await asyncio.wait_for(coro, timeout=seconds)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {seconds}s")

user = await fetch_with_timeout(fetch_user('1'), 5.0)

# Manual timeout with select
async def fetch_user_timeout(id: str, timeout: float) -> User:
    try:
        async with asyncio.timeout(timeout):  # 3.11+
            return await fetch_user(id)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Fetch timed out for user {id}")
```

### Background Tasks

**TypeScript:**
```typescript
// Fire and forget (not awaited)
fetchUser('1').catch(error => console.error(error));

// With proper cleanup
const tasks: Promise<void>[] = [];
tasks.push(processItem('1'));
tasks.push(processItem('2'));

await Promise.allSettled(tasks);
```

**Python:**
```python
# Fire and forget - create task but don't await
task = asyncio.create_task(fetch_user('1'))

# Add done callback
def handle_error(task: asyncio.Task):
    if task.exception():
        print(f"Error: {task.exception()}")

task.add_done_callback(handle_error)

# Background tasks with tracking
tasks = [
    asyncio.create_task(process_item('1')),
    asyncio.create_task(process_item('2'))
]

# Wait for all, handle errors
results = await asyncio.gather(*tasks, return_exceptions=True)
for result in results:
    if isinstance(result, Exception):
        print(f"Error: {result}")

# Proper cleanup on shutdown
async def shutdown(tasks: list[asyncio.Task]):
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
```

---

## Common Pitfalls

### 1. TypeScript `undefined` vs `null` → Python `None`

**Problem:** TypeScript distinguishes `undefined` and `null`, Python only has `None`.

```typescript
// TypeScript
interface User {
  name: string;
  age?: number;  // undefined if not provided
  email: string | null;  // explicitly nullable
}
```

```python
# Python - both map to None
from typing import Optional

class User:
    name: str
    age: Optional[int] = None  # undefined → None
    email: Optional[str] = None  # null → None
```

**Solution:** Document the semantic difference in comments or use sentinel values if distinction is critical.

### 2. Falsy Values in Conditionals

**Problem:** Python treats more values as falsy than TypeScript.

```typescript
// TypeScript - only null/undefined are falsy for objects
if (user) { /* user is not null/undefined */ }
if (count) { /* count is not 0 */ }
```

```python
# Python - many values are falsy: None, False, 0, "", [], {}, etc.
if user:  # False if None or any "empty" value
    pass

# Be explicit
if user is not None:  # Only checks None
    pass

if count != 0:  # Explicit zero check
    pass
```

**Solution:** Use explicit comparisons (`is not None`, `!= 0`, `len(items) > 0`) rather than truthy checks when the distinction matters.

### 3. Mutable Default Arguments

**Problem:** Python mutable defaults are shared across calls.

```typescript
// TypeScript - new array each time
function addItem(item: string, list: string[] = []): string[] {
  list.push(item);
  return list;
}
```

```python
# Python - WRONG: shared across calls
def add_item(item: str, list: list[str] = []) -> list[str]:
    list.append(item)
    return list

# Correct: use None and create new list
def add_item(item: str, list: list[str] | None = None) -> list[str]:
    if list is None:
        list = []
    list.append(item)
    return list
```

**Solution:** Never use mutable objects as default arguments. Use `None` and create the object inside the function.

### 4. Dictionary Key Errors

**Problem:** TypeScript objects allow undefined properties, Python dicts raise KeyError.

```typescript
// TypeScript - returns undefined
const value = obj['nonexistent'];  // undefined
```

```python
# Python - raises KeyError
value = obj['nonexistent']  # KeyError!

# Use get() with default
value = obj.get('nonexistent')  # None
value = obj.get('nonexistent', 'default')  # 'default'

# Or check first
if 'nonexistent' in obj:
    value = obj['nonexistent']
```

**Solution:** Use `dict.get()` with defaults or check key existence with `in` operator.

### 5. Integer Division

**Problem:** TypeScript `/` always returns number (float), Python `/` returns float but `//` returns int.

```typescript
// TypeScript
const result = 5 / 2;  // 2.5
```

```python
# Python - different operators
result = 5 / 2   # 2.5 (float division)
result = 5 // 2  # 2 (floor division)

# Be explicit about intent
import math
result = math.floor(5 / 2)  # Explicit floor
result = int(5 / 2)  # Truncate toward zero
```

**Solution:** Use `//` for integer division, `/` for float division. Be explicit with `math.floor()` or `int()` for clarity.

### 6. Class Property Initialization

**Problem:** TypeScript class properties initialize before constructor, Python requires `__init__`.

```typescript
// TypeScript
class Counter {
  count = 0;  // Initialized before constructor

  constructor(initial?: number) {
    if (initial !== undefined) {
      this.count = initial;
    }
  }
}
```

```python
# Python - WRONG
class Counter:
    count = 0  # Class variable (shared across instances!)

    def __init__(self, initial: int | None = None):
        if initial is not None:
            self.count = initial

# Correct - instance variables in __init__
class Counter:
    def __init__(self, initial: int | None = None):
        self.count = initial if initial is not None else 0

# Or use dataclass
from dataclasses import dataclass, field

@dataclass
class Counter:
    count: int = 0
```

**Solution:** Always initialize instance variables in `__init__`. Use `@dataclass` for simple data classes.

### 7. Async Event Loop Requirements

**Problem:** Python requires explicit event loop management.

```typescript
// TypeScript - just use async/await
async function main() {
  const result = await fetchData();
  return result;
}

main();
```

```python
# Python - WRONG (can't await at top level before 3.10)
async def main():
    result = await fetch_data()
    return result

await main()  # SyntaxError in scripts before Python 3.10

# Correct - run with asyncio
import asyncio

async def main():
    result = await fetch_data()
    return result

if __name__ == '__main__':
    asyncio.run(main())  # Python 3.7+

# Or top-level await (3.10+ in scripts, 3.8+ in REPL)
await main()
```

**Solution:** Use `asyncio.run()` for entry point, or use top-level await in Python 3.10+ scripts.

### 8. JSON Serialization

**Problem:** Python's `json` module is stricter than JavaScript's `JSON.stringify()`.

```typescript
// TypeScript - serializes dates, undefined becomes null
JSON.stringify({
  date: new Date(),
  value: undefined
});  // {"date":"2024-...","value":null}
```

```python
# Python - WRONG: TypeError for datetime
import json
from datetime import datetime

json.dumps({
    'date': datetime.now(),  # TypeError!
    'value': None
})

# Correct - custom encoder
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

json.dumps({'date': datetime.now()}, cls=CustomEncoder)

# Or convert before serialization
data = {
    'date': datetime.now().isoformat(),
    'value': None
}
json.dumps(data)
```

**Solution:** Use custom JSON encoders or convert objects before serialization. Libraries like `pydantic` handle this automatically.

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| **mypy** | Static type checking | Verifies type hints, like TypeScript compiler |
| **pyright** | Static type checker | Microsoft's type checker, VS Code integration |
| **pydantic** | Runtime validation | Validates data at runtime, like zod for TypeScript |
| **black** | Code formatting | Opinionated formatter, like prettier |
| **ruff** | Linting & formatting | Fast linter written in Rust, replaces flake8/black |
| **pytest** | Testing framework | Unit testing, like jest for TypeScript |
| **hypothesis** | Property-based testing | Generative testing, like fast-check |
| **aiohttp** | Async HTTP client | Like axios/fetch for async Python |
| **httpx** | Sync/async HTTP | Modern HTTP client supporting both modes |
| **typer** | CLI framework | Build CLIs with type hints, like commander |
| **pydantic-settings** | Config management | Type-safe config from env vars, like dotenv + zod |
| **dataclasses** | Data structures | Built-in, similar to TypeScript interfaces |

### Type Checking Setup

```python
# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true

# pyrightconfig.json
{
  "typeCheckingMode": "strict",
  "reportMissingTypeStubs": true,
  "pythonVersion": "3.11"
}
```

### Migration Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| **2to3** | Python 2 → 3 | Built-in, not for TS→Python |
| **js2py** | JavaScript → Python | Transliterates JS, not recommended for TS |
| **Manual** | TypeScript → Python | No mature automated tool exists |

**Recommendation:** Manual conversion following this skill. No production-ready TS→Python transpiler exists.

---

## Examples

### Example 1: Simple - HTTP Request Function

**Before (TypeScript):**
```typescript
interface User {
  id: string;
  name: string;
  email: string;
}

async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`https://api.example.com/users/${id}`);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return await response.json();
}

// Usage
try {
  const user = await fetchUser('123');
  console.log(user.name);
} catch (error) {
  console.error('Failed to fetch user:', error);
}
```

**After (Python):**
```python
from dataclasses import dataclass
import httpx

@dataclass
class User:
    id: str
    name: str
    email: str

async def fetch_user(id: str) -> User:
    async with httpx.AsyncClient() as client:
        response = await client.get(f'https://api.example.com/users/{id}')

        if not response.is_success:
            raise Exception(f"HTTP {response.status_code}: {response.reason_phrase}")

        data = response.json()
        return User(**data)

# Usage
async def main():
    try:
        user = await fetch_user('123')
        print(user.name)
    except Exception as error:
        print(f'Failed to fetch user: {error}')

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
```

### Example 2: Medium - Data Processing Pipeline

**Before (TypeScript):**
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
  const grouped = products
    .filter(p => p.inStock)
    .reduce((acc, product) => {
      const category = product.category;
      if (!acc[category]) {
        acc[category] = [];
      }
      acc[category].push(product);
      return acc;
    }, {} as Record<string, Product[]>);

  return Object.entries(grouped).map(([category, items]) => {
    const totalPrice = items.reduce((sum, item) => sum + item.price, 0);
    return {
      category,
      count: items.length,
      averagePrice: totalPrice / items.length,
      totalValue: totalPrice
    };
  }).sort((a, b) => b.totalValue - a.totalValue);
}

// Usage
const stats = analyzeProducts(products);
stats.forEach(s => {
  console.log(`${s.category}: ${s.count} items, avg $${s.averagePrice.toFixed(2)}`);
});
```

**After (Python):**
```python
from dataclasses import dataclass
from typing import NamedTuple
from itertools import groupby
from operator import attrgetter

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
    # Filter in-stock products
    in_stock = [p for p in products if p.in_stock]

    # Group by category (requires sorted input)
    in_stock.sort(key=attrgetter('category'))
    grouped = groupby(in_stock, key=attrgetter('category'))

    # Calculate statistics
    stats = []
    for category, items in grouped:
        items_list = list(items)
        total_price = sum(item.price for item in items_list)
        count = len(items_list)

        stats.append(CategoryStats(
            category=category,
            count=count,
            average_price=total_price / count if count > 0 else 0,
            total_value=total_price
        ))

    # Sort by total value descending
    return sorted(stats, key=attrgetter('total_value'), reverse=True)

# Alternative: using defaultdict (more similar to TS reduce)
from collections import defaultdict

def analyze_products_alt(products: list[Product]) -> list[CategoryStats]:
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

    return sorted(stats, key=lambda s: s.total_value, reverse=True)

# Usage
stats = analyze_products(products)
for s in stats:
    print(f"{s.category}: {s.count} items, avg ${s.average_price:.2f}")
```

### Example 3: Complex - Generic Repository with Caching

**Before (TypeScript):**
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

class CachedRepository<T extends Entity> {
  private cache = new Map<string, { value: T; expiresAt: number }>();
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
interface ApiError extends Error {
  status: number;
}

async function fetchUserFromApi(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) {
    const error = new Error(`HTTP ${response.status}`) as ApiError;
    error.status = response.status;
    throw error;
  }
  return response.json();
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
users.forEach((user, id) => {
  console.log(`${id}: ${user.name}`);
});
```

**After (Python):**
```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Generic, TypeVar, Protocol, Callable, Awaitable
from collections import OrderedDict
import asyncio
import httpx

# Entity protocol
class Entity(Protocol):
    id: str
    created_at: datetime
    updated_at: datetime

# Concrete entity
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

class ApiError(Exception):
    def __init__(self, message: str, status: int):
        super().__init__(message)
        self.status = status

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
            # Move to end (LRU)
            self._cache.move_to_end(id)
            return cached.value

        # Fetch from source
        try:
            value = await self._fetch_fn(id)
            self._set(id, value)
            return value
        except ApiError as error:
            if error.status == 404:
                return None
            raise

    async def get_many(self, ids: list[str]) -> dict[str, T]:
        # Fetch all in parallel
        results = await asyncio.gather(
            *[self._fetch_with_id(id) for id in ids],
            return_exceptions=False
        )

        # Filter out None values
        return {
            id: value
            for id, value in results
            if value is not None
        }

    async def _fetch_with_id(self, id: str) -> tuple[str, T | None]:
        value = await self.get(id)
        return (id, value)

    def _set(self, id: str, value: T) -> None:
        # Evict oldest if at capacity (FIFO eviction)
        if len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)  # Remove oldest (first item)

        self._cache[id] = CacheEntry(
            value=value,
            expires_at=datetime.now() + self._ttl
        )

    def invalidate(self, id: str) -> None:
        self._cache.pop(id, None)

    def clear(self) -> None:
        self._cache.clear()

# Usage
async def fetch_user_from_api(id: str) -> User:
    async with httpx.AsyncClient() as client:
        response = await client.get(f'/api/users/{id}')

        if not response.is_success:
            raise ApiError(
                f"HTTP {response.status_code}",
                status=response.status_code
            )

        data = response.json()
        return User(
            id=data['id'],
            name=data['name'],
            email=data['email'],
            created_at=datetime.fromisoformat(data['createdAt']),
            updated_at=datetime.fromisoformat(data['updatedAt'])
        )

async def main():
    user_repo = CachedRepository(
        fetch_user_from_api,
        CacheOptions(ttl_seconds=600, max_size=50)
    )

    # Fetch single user
    user = await user_repo.get('123')
    if user:
        print(f"Found user: {user.name}")

    # Fetch multiple users
    users = await user_repo.get_many(['1', '2', '3'])
    for id, user in users.items():
        print(f"{id}: {user.name}")

    # Invalidate and clear
    user_repo.invalidate('123')
    user_repo.clear()

if __name__ == '__main__':
    asyncio.run(main())
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-python-typescript` - Reverse conversion (Python → TypeScript)
- `lang-typescript-dev` - TypeScript development patterns
- `lang-python-dev` - Python development patterns
