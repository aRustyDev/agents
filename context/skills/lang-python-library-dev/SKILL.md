---
name: lang-python-library-dev
description: Python-specific library/package development patterns. Use when creating Python packages, designing public APIs with Python idioms, configuring pyproject.toml, managing dependencies with uv, publishing to PyPI, or writing package documentation. Extends meta-library-dev with Python tooling and ecosystem practices.
---

# Python Library Development

Python-specific patterns for library/package development. This skill extends `meta-library-dev` with Python tooling, package management, and ecosystem practices.

## This Skill Extends

- `meta-library-dev` - Foundational library patterns (API design, versioning, testing strategies)

For general concepts like semantic versioning, module organization principles, and testing pyramids, see the meta-skill first.

## This Skill Adds

- **Python tooling**: pyproject.toml, uv, build backends, setuptools, hatch
- **Python idioms**: Pythonic API design, type hints, decorators, context managers
- **Python ecosystem**: PyPI, TestPyPI, package discovery, documentation hosting

## This Skill Does NOT Cover

- General library patterns - see `meta-library-dev`
- Basic Python syntax - see `lang-python-dev`
- Web frameworks - see framework-specific skills
- Data science libraries - see `data-analysis-polars-dev`

---

## Quick Reference

| Task | Command/Pattern |
|------|-----------------|
| New project with uv | `uv init --lib <name>` |
| Add dependency | `uv add <package>` |
| Add dev dependency | `uv add --dev <package>` |
| Install project | `uv sync` |
| Run tests | `uv run pytest` |
| Build package | `uv build` |
| Publish to TestPyPI | `uv publish --index-url https://test.pypi.org/legacy/` |
| Publish to PyPI | `uv publish` |
| Format code | `uv run ruff format .` |
| Lint code | `uv run ruff check .` |
| Type check | `uv run mypy src/` |

---

## Package Structure

### Modern Python Package Layout

```
my-package/
├── pyproject.toml      # Project metadata and dependencies
├── README.md           # Package description
├── LICENSE             # License file
├── .gitignore          # Git ignore rules
├── src/
│   └── my_package/     # Source code (import name uses underscores)
│       ├── __init__.py # Public API exports
│       ├── py.typed    # PEP 561 marker for type hints
│       ├── core.py     # Core functionality
│       ├── types.py    # Type definitions
│       └── _internal.py # Private module (leading underscore)
├── tests/              # Test directory
│   ├── __init__.py
│   ├── test_core.py
│   └── test_types.py
├── docs/               # Documentation
│   ├── conf.py
│   └── index.md
└── examples/           # Usage examples
    └── basic_usage.py
```

### Why src/ Layout?

**Advantages:**
1. **Prevents import confusion** - Can't accidentally import from source instead of installed package
2. **Forces testing of installed package** - Ensures distribution works correctly
3. **Standard practice** - Expected by modern Python tools

---

## pyproject.toml Configuration

### Minimal Configuration

```toml
[project]
name = "my-package"
version = "0.1.0"
description = "A brief description of the package"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "you@example.com"}
]
keywords = ["keyword1", "keyword2"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "requests>=2.31.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.4.0",
]

[project.urls]
Homepage = "https://github.com/username/my-package"
Documentation = "https://my-package.readthedocs.io"
Repository = "https://github.com/username/my-package"
Issues = "https://github.com/username/my-package/issues"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/my_package"]
```

### With Entry Points (CLI Tools)

```toml
[projectcli]
my-cli = "my_package.cli:main"

# Or for plugins
[project.entry-points."some.plugin.system"]
my-plugin = "my_package.plugin:PluginClass"
```

### Build Backend Options

| Backend | Use Case | Configuration |
|---------|----------|---------------|
| **hatchling** | Modern, simple (recommended) | `build-backend = "hatchling.build"` |
| **setuptools** | Traditional, widely compatible | `build-backend = "setuptools.build_meta"` |
| **flit** | Minimal, for pure Python | `build-backend = "flit_core.buildapi"` |
| **poetry-core** | If using Poetry | `build-backend = "poetry.core.masonry.api"` |

---

## Public API Design (Python-Specific)

### \_\_init\_\_.py Patterns

**Minimal re-exports (recommended):**
```python
# src/my_package/__init__.py

"""My Package - A brief description.

Example usage:
    from my_package import parse_data

    result = parse_data("input")
"""

__version__ = "0.1.0"

# Public API - explicitly exported
from my_package.core import parse_data, process_data
from my_package.types import Config, Result

__all__ = [
    "parse_data",
    "process_data",
    "Config",
    "Result",
]
```

**Why __all__?**
1. Controls `from my_package import *`
2. Documents public API
3. IDE autocomplete hints
4. Type checkers respect it

### Type Hints in Public APIs

**Always provide type hints for public functions:**
```python
from typing import Optional, Union, Sequence
from pathlib import Path

def load_config(
    path: Union[str, Path],
    *,
    strict: bool = False,
    encoding: str = "utf-8",
) -> Config:
    """Load configuration from file.

    Args:
        path: Path to configuration file
        strict: Enable strict parsing mode
        encoding: File encoding (default: utf-8)

    Returns:
        Parsed configuration object

    Raises:
        ConfigError: If file cannot be parsed
        FileNotFoundError: If file does not exist
    """
    # Implementation
```

**Modern union syntax (Python 3.10+):**
```python
def process(value: int | str | None) -> dict[str, Any]:
    """Process input value."""
    # Implementation
```

### Pythonic Patterns

**Context managers for resource management:**
```python
from contextlib import contextmanager
from typing import Iterator

class Database:
    """Database connection manager."""

    def __enter__(self) -> "Database":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

# Or as generator
@contextmanager
def temporary_directory() -> Iterator[Path]:
    """Create and cleanup temporary directory."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)

# Usage
with Database() as db:
    db.query("SELECT * FROM users")
```

**Decorators for functionality enhancement:**
```python
from functools import wraps
from typing import Callable, TypeVar

T = TypeVar("T")

def retry(max_attempts: int = 3):
    """Retry decorator with configurable attempts."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    continue
            raise RuntimeError("Should not reach here")
        return wrapper
    return decorator

@retry(max_attempts=5)
def fetch_data(url: str) -> dict:
    """Fetch data with automatic retry."""
    # Implementation
```

**Properties for computed attributes:**
```python
class Document:
    """Document with metadata."""

    def __init__(self, content: str):
        self._content = content
        self._word_count: Optional[int] = None

    @property
    def content(self) -> str:
        """Document content."""
        return self._content

    @property
    def word_count(self) -> int:
        """Cached word count."""
        if self._word_count is None:
            self._word_count = len(self._content.split())
        return self._word_count

    @property
    def is_empty(self) -> bool:
        """Check if document is empty."""
        return len(self._content) == 0
```

### Dataclasses for Data Containers

**Modern Python data modeling:**
```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Config:
    """Application configuration."""

    # Required fields
    api_key: str
    base_url: str

    # Optional with defaults
    timeout: int = 30
    retries: int = 3
    debug: bool = False

    # Computed default (factory)
    headers: dict[str, str] = field(default_factory=dict)

    # Exclude from repr
    _internal_state: Optional[str] = field(default=None, repr=False)

    def __post_init__(self):
        """Validate after initialization."""
        if self.timeout < 0:
            raise ValueError("timeout must be non-negative")

# Usage
config = Config(
    api_key="secret",
    base_url="https://api.example.com",
    headers={"User-Agent": "my-package/1.0"}
)
```

**Frozen dataclasses for immutability:**
```python
@dataclass(frozen=True)
class Point:
    """Immutable 2D point."""
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        """Calculate distance to another point."""
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5
```

---

## Module Organization

### Private vs Public Modules

**Use leading underscore for private modules:**
```python
# Public modules (part of API)
my_package/
├── __init__.py
├── api.py          # Public: my_package.api
├── types.py        # Public: my_package.types

# Private modules (internal use only)
├── _internal.py    # Private: implementation details
├── _utils.py       # Private: internal utilities
└── _compat.py      # Private: compatibility layer
```

**Why private modules?**
- Signals internal implementation
- Free to refactor without breaking users
- Not imported by `from my_package import *`

### Subpackages for Organization

**Large packages benefit from subpackages:**
```python
my_package/
├── __init__.py
├── io/             # I/O operations
│   ├── __init__.py
│   ├── readers.py
│   └── writers.py
├── parsers/        # Parser implementations
│   ├── __init__.py
│   ├── json.py
│   └── yaml.py
└── validators/     # Validation logic
    ├── __init__.py
    └── schema.py

# Usage
from my_package.io import read_file
from my_package.parsers.json import JsonParser
```

**Re-export for convenience:**
```python
# my_package/__init__.py
from my_package.io import read_file, write_file
from my_package.parsers import parse_json, parse_yaml

__all__ = ["read_file", "write_file", "parse_json", "parse_yaml"]

# Users can do:
from my_package import read_file, parse_json
# Instead of:
from my_package.io import read_file
from my_package.parsers.json import parse_json
```

---

## Dependency Management with uv

### Adding Dependencies

```bash
# Add runtime dependency
uv add requests

# Add with version constraint
uv add "requests>=2.31.0,<3.0"

# Add development dependency
uv add --dev pytest pytest-cov ruff mypy

# Add optional dependency group
uv add --optional docs mkdocs mkdocs-material
```

### pyproject.toml Dependency Specification

```toml
[project]
dependencies = [
    "requests>=2.31.0,<3.0",
    "pydantic>=2.0",
]

[project.optional-dependencies]
# Development tools
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]

# Documentation
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.4.0",
]

# All extras combined
all = [
    "my-package[dev,docs]",
]
```

### Dependency Version Constraints

| Constraint | Meaning | Example |
|------------|---------|---------|
| `>=1.0` | Minimum version | `requests>=2.31.0` |
| `<2.0` | Maximum version (exclusive) | `requests<3.0` |
| `>=1.0,<2.0` | Range | `requests>=2.31.0,<3.0` |
| `~=1.4.2` | Compatible release | `~=1.4.2` means `>=1.4.2,<1.5.0` |
| `==1.4.2` | Exact version (avoid in libraries) | `pytest==7.4.0` |

**Best practices:**
- **Libraries**: Use loose constraints (`>=2.0,<3.0`)
- **Applications**: Can use exact versions or lockfiles
- **Avoid upper bounds** unless there's a known incompatibility

---

## Testing Patterns

### pytest Structure

**Standard test organization:**
```python
# tests/test_core.py
import pytest
from my_package import parse_data, Config
from my_package.errors import ParseError

def test_parse_valid_input():
    """Test parsing valid input."""
    result = parse_data("key=value")
    assert result == {"key": "value"}

def test_parse_invalid_input():
    """Test parsing invalid input raises error."""
    with pytest.raises(ParseError, match="Invalid format"):
        parse_data("invalid")

@pytest.mark.parametrize("input,expected", [
    ("a=1", {"a": "1"}),
    ("a=1,b=2", {"a": "1", "b": "2"}),
    ("", {}),
])
def test_parse_various_inputs(input, expected):
    """Test parsing various input formats."""
    result = parse_data(input)
    assert result == expected
```

### Fixtures for Setup

**Reusable test fixtures:**
```python
# tests/conftest.py
import pytest
from pathlib import Path
from my_package import Config

@pytest.fixture
def sample_config():
    """Provide sample configuration."""
    return Config(
        api_key="test_key",
        base_url="https://test.example.com"
    )

@pytest.fixture
def temp_file(tmp_path):
    """Create temporary test file."""
    file = tmp_path / "test.txt"
    file.write_text("test content")
    return file

# tests/test_something.py
def test_with_config(sample_config):
    """Test using fixture."""
    assert sample_config.api_key == "test_key"

def test_with_file(temp_file):
    """Test using temporary file."""
    content = temp_file.read_text()
    assert content == "test content"
```

### Coverage Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--cov=my_package",
    "--cov-report=term-missing",
    "--cov-report=html",
]

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
]
```

---

## Type Checking with mypy

### Configuration

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.9"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true

# Per-module options
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[[tool.mypy.overrides]]
module = "third_party_lib.*"
ignore_missing_imports = true
```

### py.typed Marker

**Enable type checking for your package:**
```bash
# Create marker file
touch src/my_package/py.typed
```

**Include in package distribution:**
```toml
# pyproject.toml (hatchling)
[tool.hatch.build.targets.wheel]
packages = ["src/my_package"]
include = ["src/my_package/py.typed"]
```

**This enables:**
- Type checkers see your package as typed
- Users get type hints in their IDE
- Exported types can be used in annotations

---

## Code Quality Tools

### ruff Configuration

**Modern linter and formatter (replaces flake8, black, isort):**
```toml
# pyproject.toml
[tool.ruff]
line-length = 88
target-version = "py39"
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
]
ignore = [
    "E501",   # line too long (handled by formatter)
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["ARG001"]  # Allow unused arguments in tests

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### Pre-commit Integration

**.pre-commit-config.yaml:**
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

---

## Publishing to PyPI

### Pre-publish Checklist

- [ ] Version bumped in `pyproject.toml`
- [ ] `CHANGELOG.md` updated
- [ ] `README.md` is current
- [ ] All tests pass: `uv run pytest`
- [ ] Type checking passes: `uv run mypy src/`
- [ ] Linting passes: `uv run ruff check .`
- [ ] Package builds: `uv build`
- [ ] Test installation: `uv pip install dist/*.whl`

### Building the Package

```bash
# Build source distribution and wheel
uv build

# Output:
# dist/
# ├── my_package-0.1.0.tar.gz    # Source distribution
# └── my_package-0.1.0-py3-none-any.whl  # Wheel
```

### Publishing

**First, test on TestPyPI:**
```bash
# Publish to TestPyPI
uv publish --index-url https://test.pypi.org/legacy/

# Test installation from TestPyPI
uv pip install --index-url https://test.pypi.org/simple/ my-package
```

**Then publish to PyPI:**
```bash
# Publish to PyPI (requires PyPI account and token)
uv publish

# Or specify token
uv publish --token pypi-TOKEN
```

### PyPI Credentials

**Configure in `~/.pypirc`:**
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
```

**Or use environment variables:**
```bash
export UV_PUBLISH_TOKEN=pypi-TOKEN
uv publish
```

---

## Documentation

### README.md Structure

```markdown
# My Package

Brief description of what the package does.

## Installation

```bash
pip install my-package
```

## Quick Start

```python
from my_package import parse_data

result = parse_data("input")
print(result)
```

## Features

- Feature 1
- Feature 2
- Feature 3

## Documentation

Full documentation available at [docs.example.com](https://my-package.readthedocs.io).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE) file.
```

### Docstring Conventions

**Use Google or NumPy style docstrings:**
```python
def process_data(
    input_data: str,
    *,
    strict: bool = False,
    encoding: str = "utf-8",
) -> dict[str, Any]:
    """Process input data and return structured output.

    Args:
        input_data: Raw input string to process
        strict: Enable strict parsing mode (default: False)
        encoding: Character encoding to use (default: utf-8)

    Returns:
        Dictionary containing parsed data with keys:
        - 'status': Processing status
        - 'data': Processed data
        - 'errors': List of errors (if any)

    Raises:
        ValueError: If input_data is empty
        ParseError: If parsing fails in strict mode

    Example:
        >>> result = process_data("key=value")
        >>> result['status']
        'success'
    """
    if not input_data:
        raise ValueError("input_data cannot be empty")

    # Implementation
```

### MkDocs for Documentation

**mkdocs.yml:**
```yaml
site_name: My Package
site_url: https://my-package.readthedocs.io
repo_url: https://github.com/username/my-package

theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - toc.integrate

nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - API Reference: api.md
  - Contributing: contributing.md

markdown_extensions:
  - admonition
  - codehilite
  - pymdownx.superfences

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
```

---

## Versioning and Releases

### Semantic Versioning

**Follow semver for library releases:**
- `0.x.y` - Pre-1.0, no stability guarantees
- `1.0.0` - First stable release
- `1.x.y` - Backward compatible changes
- `2.0.0` - Breaking changes

### Version Bumping

**Single source of truth:**
```python
# src/my_package/__init__.py
__version__ = "0.1.0"
```

**Read in pyproject.toml (dynamic versioning):**
```toml
[project]
dynamic = ["version"]

[tool.hatch.version]
path = "src/my_package/__init__.py"
```

**Or use static version:**
```toml
[project]
version = "0.1.0"
```

### CHANGELOG.md

**Keep a changelog:**
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- New feature X

### Changed
- Updated behavior of Y

## [0.1.0] - 2024-01-15

### Added
- Initial release
- Feature A
- Feature B
```

---

## Common Patterns

### Factory Functions

```python
from typing import Protocol

class Parser(Protocol):
    """Parser protocol."""
    def parse(self, data: str) -> dict:
        ...

def create_parser(format: str) -> Parser:
    """Create parser for specified format.

    Args:
        format: One of 'json', 'yaml', 'toml'

    Returns:
        Parser instance for the format

    Raises:
        ValueError: If format is unsupported
    """
    if format == "json":
        return JsonParser()
    elif format == "yaml":
        return YamlParser()
    elif format == "toml":
        return TomlParser()
    else:
        raise ValueError(f"Unsupported format: {format}")
```

### Singleton Pattern

```python
class DatabaseConnection:
    """Singleton database connection."""

    _instance: Optional["DatabaseConnection"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize connection (called once)."""
        self.connection = self._create_connection()
```

### Configuration Management

```python
from pathlib import Path
from typing import Any
import json

class Config:
    """Application configuration manager."""

    def __init__(self, config_path: Optional[Path] = None):
        self._data: dict[str, Any] = {}
        if config_path:
            self.load(config_path)

    def load(self, path: Path) -> None:
        """Load configuration from file."""
        with open(path) as f:
            self._data = json.load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Dictionary-style access."""
        return self._data[key]
```

---

## Anti-Patterns

### 1. Mutable Default Arguments

```python
# Bad: Mutable default
def add_item(item, items=[]):
    items.append(item)
    return items

# Good: Use None and create new
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### 2. Catching All Exceptions

```python
# Bad: Swallows all errors
try:
    result = risky_operation()
except Exception:
    return None

# Good: Catch specific exceptions
try:
    result = risky_operation()
except ValueError as e:
    logger.warning(f"Invalid value: {e}")
    return None
```

### 3. Circular Imports

```python
# Bad: module_a.py imports module_b, module_b imports module_a

# Good: Use TYPE_CHECKING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from module_b import ClassB

def my_function(obj: "ClassB") -> None:
    # Use string annotation to avoid runtime import
    pass
```

### 4. Missing Type Hints

```python
# Bad: No type hints
def process(data):
    return data.upper()

# Good: Clear types
def process(data: str) -> str:
    return data.upper()
```

---

## Troubleshooting

### Import Errors After Installation

**Problem:** `ModuleNotFoundError: No module named 'my_package'`

**Solutions:**
1. Ensure package is installed: `uv pip list | grep my-package`
2. Check package name vs import name (hyphens vs underscores)
3. Verify src/ layout is configured in `pyproject.toml`
4. Reinstall in editable mode: `uv pip install -e .`

### Type Checking Errors

**Problem:** `mypy` reports errors but code runs fine

**Solutions:**
1. Add type hints to function signatures
2. Use `# type: ignore[error-code]` for false positives
3. Configure mypy properly in `pyproject.toml`
4. Add `py.typed` marker file

### Package Not Found on PyPI

**Problem:** Published package but can't install

**Solutions:**
1. Wait a few minutes for PyPI to index
2. Check package name isn't already taken
3. Verify upload succeeded: check PyPI web interface
4. Try exact version: `pip install my-package==0.1.0`

---

## References

- `meta-library-dev` - Foundational library patterns
- `lang-python-dev` - Basic Python syntax and patterns
- [Python Packaging User Guide](https://packaging.python.org/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [PyPI](https://pypi.org/) - Python Package Index
- [TestPyPI](https://test.pypi.org/) - Test package repository
- [PEP 517](https://peps.python.org/pep-0517/) - Build system interface
- [PEP 518](https://peps.python.org/pep-0518/) - pyproject.toml
- [PEP 621](https://peps.python.org/pep-0621/) - Project metadata
