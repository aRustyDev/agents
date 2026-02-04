# Dynamic Languages Family

> Dynamically-typed languages emphasizing flexibility, rapid development, and runtime metaprogramming.

## Overview

The Dynamic family includes languages where types are checked at runtime rather than compile time, enabling:

- **Rapid prototyping** - No type annotations required
- **Duck typing** - "If it walks like a duck..."
- **Runtime flexibility** - Add/modify behavior at runtime
- **REPL-driven development** - Interactive exploration
- **Metaprogramming** - Reflection, eval, monkey patching

This family is the most common **source** for conversions (13 skills as source), particularly Python which is the source for 11 skills.

## Subtypes

| Subtype | Description | Languages |
|---------|-------------|-----------|
| **scripting** | General-purpose scripting | Python, Ruby, Perl |
| **web** | Web-focused development | JavaScript, PHP |

### Scripting vs Web Differences

| Aspect | Scripting | Web |
|--------|-----------|-----|
| Primary use | Automation, data, backend | Browser, full-stack |
| Concurrency | Threads (with GIL) or async | Event loop (JS) |
| Module system | Import-based | Various (ES modules, CommonJS) |
| Type hints | Available (Python, Ruby 3) | TypeScript ecosystem |

## Key Characteristics

- **No compile step** - Interpret directly or JIT compile
- **Duck typing** - Behavior over declared types
- **First-class functions** - Closures, higher-order functions
- **Dynamic dispatch** - Method lookup at runtime
- **Reflection** - Introspect and modify at runtime
- **REPL** - Interactive development environment
- **Flexible syntax** - Often multiple ways to express same thing

## Languages in Family

| Language | Subtype | Platform | Notes |
|----------|---------|----------|-------|
| Python | scripting | CPython/PyPy | Indentation-based, data science |
| Ruby | scripting | MRI/JRuby | Everything is object, blocks |
| JavaScript | web | Browser/Node | Ubiquitous, event loop |
| TypeScript | web | Transpiled JS | Gradual typing for JS |
| PHP | web | Zend | Server-side web, improved in 7+ |
| Perl | scripting | Native | Text processing, regex |

## Type System

### Characteristics

- **Runtime typing** - Types checked during execution
- **Duck typing** - Interface by behavior, not declaration
- **No type annotations required** - Optional in modern versions
- **Coercion** - Implicit type conversions (JS especially)

### Gradual Typing Options

| Language | Type System | Tools |
|----------|-------------|-------|
| Python | Type hints (PEP 484+) | mypy, pyright, Pyre |
| TypeScript | Structural types | tsc |
| Ruby | RBS signatures | Steep, Sorbet |
| PHP | Type declarations (7+) | PHPStan, Psalm |

### Common Type Patterns

```python
# Python with type hints
def greet(name: str) -> str:
    return f"Hello, {name}"

# Optional types
def find(items: list[int], target: int) -> int | None:
    ...

# Generic types
from typing import TypeVar, Generic
T = TypeVar('T')
class Container(Generic[T]):
    def get(self) -> T: ...
```

## Memory Model

- **Garbage collected** - Reference counting (Python, PHP) + cycle detection
- **Mutable by default** - Objects mutable unless frozen
- **Reference semantics** - Variables hold references to objects
- **No manual memory** - Automatic allocation and deallocation

### Memory Characteristics

| Language | GC Type | Notes |
|----------|---------|-------|
| Python | Reference counting + cycle GC | GIL limits parallelism |
| JavaScript | Mark-and-sweep | Per-isolate in V8 |
| Ruby | Mark-and-sweep | Generational in newer versions |
| PHP | Reference counting | Per-request cleanup |

## Concurrency Model

| Language | Primary Model | Limitations |
|----------|---------------|-------------|
| Python | asyncio / threading | GIL limits CPU parallelism |
| JavaScript | Event loop + async/await | Single-threaded |
| Ruby | Threads / Fibers | GIL (MRI) |
| PHP | Process-based / Fibers (8.1+) | Shared-nothing |

### Async Patterns

```python
# Python asyncio
async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

```javascript
// JavaScript async/await
async function fetchData(url) {
    const response = await fetch(url);
    return response.json();
}
```

## Common Patterns

### Duck Typing

```python
def process(items):
    for item in items:  # Anything iterable works
        print(item)
```

### Metaprogramming

```python
# Python: dynamic attribute access
class Dynamic:
    def __getattr__(self, name):
        return f"Accessing {name}"
```

```ruby
# Ruby: method_missing
class Dynamic
  def method_missing(name, *args)
    "Called #{name} with #{args}"
  end
end
```

### Closures

```javascript
function counter() {
    let count = 0;
    return () => ++count;
}
```

### Decorators/Annotations

```python
@cache
def expensive_computation(x):
    ...
```

## Conversion Considerations

### Converting FROM Dynamic

**What's easy to preserve:**

- Algorithm logic (control flow maps directly)
- Function signatures (with type inference)
- Data structures (lists, dicts → arrays, maps)
- String operations (universally similar)

**What's hard to translate:**

- Duck typing → explicit interfaces
- Monkey patching → must restructure
- `eval` / `exec` → not portable
- Dynamic attribute access → static members
- Metaprogramming → target-specific patterns

**Common pitfalls:**

- Assuming all values are typed (need inference)
- Missing null/None handling
- Ignoring implicit coercions
- Relying on mutable default arguments

**Semantic gaps:**

- Dynamic → ML-FP: 39 gaps (type inference, immutability)
- Dynamic → Systems: 29 gaps (memory management, strict typing)

### Converting TO Dynamic

**What maps naturally:**

- Static types → runtime checks (or removed)
- Interfaces → duck typing
- Enums → constants or classes
- Generics → no change needed (erased)

**What requires restructuring:**

- Compile-time checks → runtime validation
- Ownership (Rust) → GC
- Pattern matching → if/elif chains or match (Python 3.10+)

**Idiomatic patterns to target:**

- Use duck typing over explicit interfaces
- Leverage dynamic features (but carefully)
- List/dict comprehensions (Python)
- Destructuring (JavaScript)

**Anti-patterns to avoid:**

- Over-typing (defeating duck typing purpose)
- Ignoring conventions (PEP 8, etc.)
- Not using language-specific idioms

## Cross-References

### Phase 0 Pattern Clusters

- **Universal patterns**: bool, String, int, float (high frequency)
- **Family-specific**: T[] / Array<T> (2 patterns), Coroutine (2 patterns)
- **Gap patterns**: 39 gaps Dynamic → ML-FP, 29 gaps Dynamic → Systems

### Related convert-* Skills

- convert-python-haskell (238 patterns)
- convert-python-rust (234 patterns)
- convert-python-elixir (227 patterns)
- convert-python-scala (198 patterns)
- convert-python-typescript (182 patterns)
- convert-typescript-rust (244 patterns)

## Sources

- [Python Documentation](https://docs.python.org/)
- [MDN JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [Ruby Documentation](https://ruby-doc.org/)
- [PHP Manual](https://www.php.net/manual/)

## See Also

- [Gradual Typing](gradual-typing.md) - Adding optional static types
- [ML-FP](ml-fp.md) - Common target for Dynamic conversions
- [Overview](overview.md) - Cross-family comparison matrices
