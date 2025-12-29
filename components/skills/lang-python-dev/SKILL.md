---
name: lang-python-dev
description: Foundational Python patterns covering core syntax, idioms, type hints, testing, and modern tooling. Use when writing Python code, understanding Pythonic patterns, working with type hints, or needing guidance on which specialized Python skill to use. This is the entry point for Python development.
---

# Python Fundamentals

Foundational Python patterns and core language features. This skill serves as both a reference for common patterns and an index to specialized Python skills.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Python Skill Hierarchy                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                  ┌─────────────────────┐                        │
│                  │  lang-python-dev    │ ◄── You are here       │
│                  │   (foundation)      │                        │
│                  └──────────┬──────────┘                        │
│                             │                                   │
│     ┌───────────┬───────────┼───────────┬───────────┐          │
│     │           │           │           │           │          │
│     ▼           ▼           ▼           ▼           ▼          │
│ ┌────────┐ ┌────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐      │
│ │packaging│ │testing │ │ async   │ │  data   │ │ web    │      │
│ │  -dev  │ │  -dev  │ │  -dev   │ │ science │ │ api    │      │
│ └────────┘ └────────┘ └─────────┘ └─────────┘ └────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**This skill covers:**
- Core syntax (functions, classes, decorators)
- Pythonic idioms and conventions
- Type hints and type checking
- Iteration and comprehensions
- Context managers and protocols
- Modern tooling (uv, ruff, mypy)
- Testing fundamentals

**This skill does NOT cover (see specialized skills):**
- Package publishing → `python-packaging-dev`
- Advanced testing strategies → `python-testing-dev`
- Async/await patterns → `python-async-dev`
- Data science libraries → `data-analysis-polars-dev`
- Web framework specifics → Framework-specific skills

---

## Quick Reference

| Task | Pattern |
|------|---------|
| Define function | `def name(param: type) -> return_type:` |
| Define class | `class Name:` |
| List comprehension | `[expr for item in iterable if condition]` |
| Dict comprehension | `{k: v for k, v in items if condition}` |
| Context manager | `with resource as r:` |
| Decorator | `@decorator` above function |
| Type hint | `variable: Type = value` |
| Match statement | `match value: case pattern: ...` |
| Walrus operator | `if (x := func()) is not None:` |

---

## Skill Routing

Use this table to find the right specialized skill:

| When you need to... | Use this skill |
|---------------------|----------------|
| Package and publish to PyPI | `python-packaging-dev` |
| Set up pytest, fixtures, mocking | `python-testing-dev` |
| Work with async/await, asyncio | `python-async-dev` |
| Data analysis with Polars/Pandas | `data-analysis-polars-dev` |
| Build REST APIs | Framework-specific skills |

---

## Core Syntax

### Functions

```python
# Basic function
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Default arguments
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

# *args and **kwargs
def log_message(*args, **kwargs):
    print(f"Args: {args}")
    print(f"Kwargs: {kwargs}")

# Type hints with Optional, Union
from typing import Optional, Union

def find_user(user_id: int) -> Optional[dict]:
    # Returns dict or None
    return None

def process(value: Union[int, str]) -> str:
    return str(value)

# Modern union syntax (Python 3.10+)
def process(value: int | str) -> str:
    return str(value)
```

### Classes

```python
# Basic class
class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    def greet(self) -> str:
        return f"Hello, {self.name}!"

# Dataclass (preferred for data containers)
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str
    age: int = 0  # Default value

    def greet(self) -> str:
        return f"Hello, {self.name}!"

# Inheritance
class AdminUser(User):
    def __init__(self, name: str, email: str, permissions: list[str]):
        super().__init__(name, email)
        self.permissions = permissions

# Property decorator
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
print(circle.area)  # 78.53975
circle.radius = 10  # Uses setter
```

### Decorators

```python
# Function decorator
from functools import wraps
from typing import Callable, Any

def log_calls(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    return wrapper

@log_calls
def process_data(data: list) -> int:
    return len(data)

# Decorator with arguments
def repeat(times: int):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def say_hello():
    print("Hello!")

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
    def __init__(self):
        self.connection = "Connected"
```

---

## Type Hints

### Basic Types

```python
from typing import Any, Optional, Union

# Built-in types
name: str = "Alice"
age: int = 30
height: float = 5.8
is_active: bool = True

# Collections
numbers: list[int] = [1, 2, 3]
coords: tuple[float, float] = (10.5, 20.3)
user_ids: set[int] = {1, 2, 3}
config: dict[str, Any] = {"key": "value"}

# Optional (value or None)
middle_name: Optional[str] = None
# Equivalent to:
middle_name: str | None = None

# Union (multiple types)
user_id: Union[int, str] = 123
# Modern syntax:
user_id: int | str = 123
```

### Advanced Type Hints

```python
from typing import Protocol, TypeVar, Generic, Callable

# TypeVar for generics
T = TypeVar('T')

def first(items: list[T]) -> T:
    return items[0]

# Generic class
class Stack(Generic[T]):
    def __init__(self):
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

# Protocol (structural typing)
class Drawable(Protocol):
    def draw(self) -> None: ...

def render(obj: Drawable) -> None:
    obj.draw()

# Callable type hints
def apply(func: Callable[[int], int], value: int) -> int:
    return func(value)

# TypedDict for dict with known keys
from typing import TypedDict

class UserDict(TypedDict):
    name: str
    email: str
    age: int

user: UserDict = {
    "name": "Alice",
    "email": "alice@example.com",
    "age": 30
}
```

### Type Checking

```python
# Runtime type checking with isinstance
def process(value: int | str) -> str:
    if isinstance(value, int):
        return f"Number: {value}"
    else:
        return f"String: {value}"

# Static type checking with mypy
# Run: mypy your_file.py

# Type narrowing
def get_length(value: str | list) -> int:
    if isinstance(value, str):
        # Type narrowed to str
        return len(value)
    else:
        # Type narrowed to list
        return len(value)

# Assert for type narrowing
def process_user(user: dict | None) -> str:
    assert user is not None
    # Type narrowed to dict
    return user["name"]
```

---

## Pythonic Idioms

### List Comprehensions

```python
# Basic list comprehension
squares = [x**2 for x in range(10)]

# With condition
evens = [x for x in range(10) if x % 2 == 0]

# Nested
matrix = [[i+j for j in range(3)] for i in range(3)]

# Dict comprehension
word_lengths = {word: len(word) for word in ["hello", "world"]}

# Set comprehension
unique_lengths = {len(word) for word in ["hello", "world", "hi"]}

# Generator expression (lazy evaluation)
squares_gen = (x**2 for x in range(1000000))  # Memory efficient
```

### Iteration Patterns

```python
# Enumerate for index + value
for i, value in enumerate(["a", "b", "c"]):
    print(f"{i}: {value}")

# Zip for parallel iteration
names = ["Alice", "Bob"]
ages = [30, 25]
for name, age in zip(names, ages):
    print(f"{name} is {age}")

# Reversed iteration
for item in reversed([1, 2, 3]):
    print(item)

# Sorted iteration
for name in sorted(["Charlie", "Alice", "Bob"]):
    print(name)

# Dict iteration
user = {"name": "Alice", "age": 30}
for key, value in user.items():
    print(f"{key}: {value}")
```

### Context Managers

```python
# File handling
with open("file.txt", "r") as f:
    content = f.read()
# File automatically closed

# Multiple context managers
with open("input.txt") as infile, open("output.txt", "w") as outfile:
    outfile.write(infile.read())

# Custom context manager (class)
class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        print(f"Elapsed: {self.end - self.start:.2f}s")

with Timer():
    # Code to time
    time.sleep(1)

# Custom context manager (generator)
from contextlib import contextmanager

@contextmanager
def timer():
    start = time.time()
    yield
    end = time.time()
    print(f"Elapsed: {end - start:.2f}s")

with timer():
    time.sleep(1)
```

### Match Statements (Python 3.10+)

```python
# Basic match
def http_status(code: int) -> str:
    match code:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Server Error"
        case _:
            return "Unknown"

# Pattern matching with structures
def process_command(command):
    match command:
        case {"action": "create", "type": type_}:
            return f"Creating {type_}"
        case {"action": "delete", "id": id_}:
            return f"Deleting {id_}"
        case {"action": action}:
            return f"Unknown action: {action}"
        case _:
            return "Invalid command"

# Sequence patterns
def describe_point(point):
    match point:
        case (0, 0):
            return "Origin"
        case (0, y):
            return f"Y-axis at {y}"
        case (x, 0):
            return f"X-axis at {x}"
        case (x, y):
            return f"Point at ({x}, {y})"
```

### Walrus Operator (Python 3.8+)

```python
# Assignment expression
if (n := len(data)) > 10:
    print(f"Large dataset: {n} items")

# In while loops
while (line := file.readline()):
    process(line)

# In comprehensions
filtered = [y for x in data if (y := transform(x)) is not None]

# Multiple uses
if (match := pattern.search(text)) and match.group(1):
    return match.group(1)
```

---

## Error Handling

### Exception Basics

```python
# Try-except
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero")

# Multiple exceptions
try:
    data = load_data()
except (FileNotFoundError, PermissionError) as e:
    print(f"Error loading data: {e}")

# Try-except-else-finally
try:
    result = risky_operation()
except ValueError as e:
    print(f"Invalid value: {e}")
else:
    # Runs if no exception
    print("Success!")
finally:
    # Always runs
    cleanup()
```

### Custom Exceptions

```python
class ValidationError(Exception):
    """Raised when validation fails."""
    pass

class ConfigError(Exception):
    """Configuration-related errors."""
    def __init__(self, key: str, message: str):
        self.key = key
        super().__init__(f"Config error for '{key}': {message}")

# Raising exceptions
def validate_age(age: int) -> None:
    if age < 0:
        raise ValidationError("Age cannot be negative")
    if age > 150:
        raise ValidationError("Age unrealistic")

# Exception chaining
try:
    process_data()
except ValueError as e:
    raise ConfigError("database_url", "Invalid format") from e
```

---

## Modern Tooling

### uv (Fast Python Package Manager)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create new project
uv init my-project
cd my-project

# Add dependencies
uv add requests pytest

# Run script
uv run python script.py

# Sync dependencies
uv sync
```

### ruff (Fast Linter & Formatter)

```bash
# Install
uv add --dev ruff

# Lint
ruff check .

# Format
ruff format .

# Auto-fix issues
ruff check --fix .
```

**pyproject.toml configuration:**
```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = ["E501"]  # Line too long (handled by formatter)

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### mypy (Static Type Checker)

```bash
# Install
uv add --dev mypy

# Run type checking
mypy src/

# With strict mode
mypy --strict src/
```

**pyproject.toml configuration:**
```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
strict_equality = true
```

---

## Testing Fundamentals

### pytest Basics

```python
# test_example.py

def test_addition():
    assert 1 + 1 == 2

def test_string_operations():
    text = "hello world"
    assert text.upper() == "HELLO WORLD"
    assert "world" in text

# Parametrize tests
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 3),
    (10, 11),
])
def test_increment(input, expected):
    assert input + 1 == expected

# Fixtures
@pytest.fixture
def sample_user():
    return {"name": "Alice", "age": 30}

def test_user_data(sample_user):
    assert sample_user["name"] == "Alice"
    assert sample_user["age"] == 30

# Exception testing
def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        1 / 0
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_example.py

# Run tests matching pattern
pytest -k "test_user"

# Show print output
pytest -s

# Coverage report
pytest --cov=src tests/
```

**pyproject.toml configuration:**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "-ra",
]
```

---

## Common Patterns

### Singleton Pattern

```python
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# Or use decorator (shown earlier)
```

### Factory Pattern

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self) -> str:
        pass

class Dog(Animal):
    def speak(self) -> str:
        return "Woof!"

class Cat(Animal):
    def speak(self) -> str:
        return "Meow!"

def animal_factory(animal_type: str) -> Animal:
    if animal_type == "dog":
        return Dog()
    elif animal_type == "cat":
        return Cat()
    else:
        raise ValueError(f"Unknown animal type: {animal_type}")

# Usage
animal = animal_factory("dog")
print(animal.speak())  # "Woof!"
```

### Builder Pattern

```python
class RequestBuilder:
    def __init__(self):
        self._url = ""
        self._method = "GET"
        self._headers: dict[str, str] = {}
        self._body: dict | None = None

    def url(self, url: str) -> "RequestBuilder":
        self._url = url
        return self

    def method(self, method: str) -> "RequestBuilder":
        self._method = method
        return self

    def header(self, key: str, value: str) -> "RequestBuilder":
        self._headers[key] = value
        return self

    def body(self, body: dict) -> "RequestBuilder":
        self._body = body
        return self

    def build(self) -> dict:
        return {
            "url": self._url,
            "method": self._method,
            "headers": self._headers,
            "body": self._body,
        }

# Usage
request = (RequestBuilder()
    .url("https://api.example.com/users")
    .method("POST")
    .header("Content-Type", "application/json")
    .body({"name": "Alice"})
    .build())
```

---

## Troubleshooting

### ImportError / ModuleNotFoundError

**Problem:** `ModuleNotFoundError: No module named 'xyz'`

**Fixes:**
1. Install the package: `uv add xyz`
2. Check virtual environment is activated
3. Verify package name (e.g., `beautifulsoup4` not `bs4`)

### Type Errors with mypy

**Problem:** `error: Incompatible types in assignment`

**Fixes:**
1. Add explicit type hints
2. Use type narrowing with `isinstance()`
3. Use `# type: ignore` comment if necessary (last resort)

### Circular Imports

**Problem:** `ImportError: cannot import name 'X' from partially initialized module`

**Fixes:**
1. Move import inside function (lazy import)
2. Restructure code to remove circular dependency
3. Use `TYPE_CHECKING` for type-only imports:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from other_module import SomeClass

def my_function(obj: "SomeClass") -> None:
    # String annotation avoids runtime import
    pass
```

### Mutable Default Arguments

**Problem:** Default list/dict shared across calls

```python
# Bad
def add_item(item, items=[]):
    items.append(item)
    return items

# Each call shares the same list!
```

**Fix:**
```python
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

---

## References

- [Python Documentation](https://docs.python.org/3/)
- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [Type Hints - PEP 484](https://peps.python.org/pep-0484/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- Specialized skills: `python-packaging-dev`, `python-testing-dev`, `python-async-dev`, `data-analysis-polars-dev`
