# Gradual Typing Family

> Type systems that allow mixing typed and untyped code, enabling incremental adoption of static typing.

## Overview

Gradual typing bridges dynamic and static typing:

- **Optional types** - Type annotations not required
- **Incremental adoption** - Add types to existing codebase gradually
- **Any type** - Escape hatch for untyped code
- **Structural typing** - Types based on shape, not names (TypeScript)
- **Soundness trade-offs** - Practical usability over formal guarantees

## Base Family

This is a **feature family** that applies to languages from the [Dynamic](dynamic.md) family.

## Languages

| Language | Base | Type Checker | Notes |
|----------|------|--------------|-------|
| TypeScript | JavaScript | tsc | Structural types, broad adoption |
| Python (typed) | Python | mypy, pyright | PEP 484+, growing ecosystem |
| Hack | PHP | HHVM | Facebook's PHP with types |
| Flow | JavaScript | flow | Alternative to TypeScript |
| Ruby (typed) | Ruby | Sorbet, Steep | RBS type definitions |

## Key Characteristics

- **Types as documentation** - Improve readability without runtime changes
- **Tooling benefits** - IDE completion, refactoring, error detection
- **Escape hatches** - `any` (TS), `Any` (Python), `mixed` (Hack)
- **Runtime erasure** - Types typically removed before execution
- **Gradual migration** - Can type one file/function at a time

## Type System Features

### TypeScript

```typescript
// Structural typing
interface Point {
  x: number;
  y: number;
}

function distance(p1: Point, p2: Point): number {
  return Math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2);
}

// Any object with x, y works
distance({ x: 0, y: 0 }, { x: 3, y: 4 });

// Union types
type StringOrNumber = string | number;

// Generics
function first<T>(arr: T[]): T | undefined {
  return arr[0];
}

// Conditional types
type Awaited<T> = T extends Promise<infer U> ? U : T;
```

### Python (typed)

```python
from typing import TypeVar, Generic, Optional

# Type hints
def greet(name: str) -> str:
    return f"Hello, {name}"

# Generics
T = TypeVar('T')

class Stack(Generic[T]):
    def push(self, item: T) -> None: ...
    def pop(self) -> T: ...

# Union types (3.10+)
def process(value: int | str) -> str:
    return str(value)

# Optional
def find(items: list[int], target: int) -> Optional[int]:
    return items.index(target) if target in items else None
```

## Conversion Considerations

### Converting FROM Gradual Typing

**What's easy:**

- Typed portions map directly to static types
- Interfaces → traits/protocols
- Generic types → generics

**What's hard:**

- `any`/untyped code requires inference
- Structural types → nominal types (some targets)
- Union types → sum types or overloads

### Converting TO Gradual Typing

**What's easy:**

- Static types → type annotations (can be 1:1)
- Removing types → just omit annotations

**What's hard:**

- Dependent types → runtime checks
- HKT → not available

**Idiomatic patterns:**

- Use strict mode (TypeScript `strict: true`)
- Avoid `any` where possible
- Use type guards for narrowing

## Sources

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [Python typing module](https://docs.python.org/3/library/typing.html)
- [mypy Documentation](https://mypy.readthedocs.io/)

## See Also

- [Dynamic](dynamic.md) - Base family
- [ML-FP](ml-fp.md) - Full static typing
- [Overview](overview.md) - Comparison matrices
