# Python

> Dynamically-typed, high-level language emphasizing readability and rapid development.

## Overview

Python is a general-purpose programming language created by Guido van Rossum, first released in 1991. It emphasizes code readability with significant whitespace and a clean syntax that allows programmers to express concepts in fewer lines of code than languages like C++ or Java.

Python supports multiple programming paradigms including procedural, object-oriented, and functional programming. Its comprehensive standard library and extensive ecosystem of third-party packages (via PyPI) make it suitable for web development, data science, machine learning, automation, and scripting.

The language's philosophy is captured in "The Zen of Python" (PEP 20), emphasizing simplicity, readability, and "one obvious way to do it."

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | Dynamic | Runtime typing, duck typing |
| Secondary Family | Gradual-Typing | With type hints (PEP 484+) |
| Subtype | scripting | General-purpose scripting |

See: [Dynamic Family](../language-families/dynamic.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| 2.7 | 2010-07 | Legacy: print statement, unicode vs str, / integer division |
| 3.6 | 2016-12 | f-strings, async/await stable, type hints expanded |
| 3.10 | 2021-10 | Pattern matching (match/case), union types `X \| Y` |
| 3.12 | 2023-10 | Type parameter syntax (PEP 695), improved f-strings |

## Feature Profile

### Type System

- **Strength:** dynamic (gradual with type hints)
- **Inference:** none (runtime typing)
- **Generics:** runtime (duck typing), static with `typing.Generic[T]`
- **Nullability:** nullable (`None` is valid for any type)

### Memory Model

- **Management:** gc (reference counting + cycle collector)
- **Mutability:** default-mutable
- **Allocation:** heap (automatic)

### Control Flow

- **Structured:** if-elif-else, for, while, try-except, match-case (3.10+)
- **Effects:** exceptions (`try`/`except`/`finally`)
- **Async:** async-await (`asyncio`), also threading, multiprocessing

### Data Types

- **Primitives:** int (arbitrary precision), float, bool, str, bytes, None
- **Composites:** list, tuple, dict, set, frozenset, dataclass
- **Collections:** collections module (deque, Counter, OrderedDict, defaultdict)
- **Abstraction:** classes, modules, protocols (typing.Protocol)

### Metaprogramming

- **Macros:** none
- **Reflection:** full runtime (inspect, `__dict__`, `getattr`/`setattr`)
- **Code generation:** decorators, metaclasses, `exec`/`eval`

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | pip, uv, poetry | uv is modern/fast |
| Build System | setuptools, hatch, flit | pyproject.toml standard |
| LSP | pylsp, pyright | pyright for type checking |
| Formatter | black, ruff | ruff is faster |
| Linter | ruff, flake8, pylint | ruff consolidates tools |
| REPL | python, ipython, jupyter | ipython for interactive |
| Test Framework | pytest, unittest | pytest is standard |

## Syntax Patterns

```python
# Function definition
def greet(name: str, times: int = 1) -> str:
    return f"Hello, {name}! " * times

# Async function
async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Type definition (dataclass)
@dataclass
class User:
    name: str
    age: int
    email: str | None = None

# Type definition (Protocol)
class Drawable(Protocol):
    def draw(self) -> None: ...

# Pattern matching (3.10+)
match command:
    case ["quit"]:
        return
    case ["load", filename]:
        load_file(filename)
    case _:
        print("Unknown command")

# Error handling
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
except Exception as e:
    logger.exception("Unexpected error")
    raise
finally:
    cleanup()

# Context manager
with open("file.txt") as f:
    content = f.read()

# List comprehension
squares = [x**2 for x in range(10) if x % 2 == 0]

# Generator
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| No static type enforcement | moderate | Use mypy/pyright for static analysis |
| GIL limits true parallelism | moderate | Use multiprocessing or async for I/O |
| No tail call optimization | minor | Use iteration instead of recursion |
| Mutable default arguments | minor | Use `None` default, assign in function |
| No private members (only convention) | minor | Use `_` prefix convention |
| No pattern matching before 3.10 | moderate | Use if-elif chains or dict dispatch |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 11 | python-clojure, python-elixir, python-elm, python-erlang, python-fsharp, python-golang, python-haskell, python-roc, python-rust, python-scala, python-typescript |
| As Target | 0 | — |

**Missing high-value pairs:** ruby→python, javascript→python, java→python

## Idiomatic Patterns

### Error Handling → Result Types

```python
# Python: exceptions
def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Division by zero")
    return a / b

# IR equivalent: Result type
# Result[float, ValueError]
```

### Duck Typing → Traits/Interfaces

```python
# Python: duck typing
def process(item):
    item.save()  # Assumes .save() exists

# IR equivalent: trait bound
# fn process<T: Saveable>(item: T)
```

### Generators → Iterators/Streams

```python
# Python: generator
def items():
    for i in range(10):
        yield transform(i)

# IR equivalent: lazy iterator
# Iterator<Item=T>
```

## Related Languages

- **Influenced by:** ABC, C, Haskell, Lisp, Modula-3
- **Influenced:** Ruby, Swift, Go, Julia, Nim
- **Compiles to:** Bytecode (.pyc), also Cython→C, mypyc→C
- **FFI compatible:** C (ctypes, cffi), C++ (pybind11)

## Sources

- [Python Language Reference](https://docs.python.org/3/reference/)
- [Python Standard Library](https://docs.python.org/3/library/)
- [PEP Index](https://peps.python.org/)
- [typing module](https://docs.python.org/3/library/typing.html)

## See Also

- [Dynamic Family](../language-families/dynamic.md)
- [Gradual-Typing Family](../language-families/gradual-typing.md)
- [TypeScript](typescript.md) - Gradual typing comparison
