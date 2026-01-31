---
name: Coverage.py Guide
module_type: guide
scope: temporary
priority: low
triggers: ["coverage.py", "python coverage", "code coverage", "test coverage", "coverage report"]
dependencies: []
conflicts: []
version: 1.0.0
---

# Coverage.py Guide

## Purpose
Master Coverage.py for measuring code coverage of Python programs, generating reports, and integrating with CI/CD pipelines to maintain code quality.

## Installation and Setup

### Installation
```bash
# Install coverage.py
pip install coverage

# Install with extras
pip install coverage[toml]  # TOML config support

# For development
pip install pytest pytest-cov  # Pytest integration
```

### Basic Configuration (.coveragerc)
```ini
[run]
source = src
omit = 
    */tests/*
    */venv/*
    */__pycache__/*
    */migrations/*
    */config.py
    */setup.py

[report]
precision = 2
show_missing = True
skip_covered = False
sort = Cover

exclude_lines =
    # Have to re-enable the standard pragma
    pragma: no cover
    
    # Don't complain about missing debug-only code:
    def __repr__
    if self\.debug
    
    # Don't complain if tests don't hit defensive assertion code:
    raise AssertionError
    raise NotImplementedError
    
    # Don't complain if non-runnable code isn't run:
    if 0:
    if __name__ == .__main__.:
    
    # Type checking
    if TYPE_CHECKING:

[html]
directory = htmlcov

[xml]
output = coverage.xml
```

### pyproject.toml Configuration
```toml
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/__init__.py",
]
parallel = true
context = "${CONTEXT}"

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
fail_under = 80
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]

[tool.coverage.html]
directory = "htmlcov"
title = "My Project Coverage"

[tool.coverage.json]
output = "coverage.json"
pretty_print = true
```

## Basic Usage

### Running Coverage
```bash
# Run coverage on a Python script
coverage run script.py

# Run coverage with module
coverage run -m pytest

# Run with specific configuration
coverage run --rcfile=.coveragerc -m pytest

# Append to existing coverage data
coverage run --append test_suite2.py

# Run in parallel mode
coverage run --parallel-mode -m pytest
```

### Generating Reports
```bash
# Simple terminal report
coverage report

# Detailed terminal report
coverage report --show-missing

# HTML report
coverage html
# Open htmlcov/index.html in browser

# XML report (for CI tools)
coverage xml

# JSON report
coverage json

# Combined command
coverage run -m pytest && coverage report && coverage html
```

### Report Output Example
```
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
src/calculator.py            20      2    90%   15-16
src/database.py              45      5    89%   23, 67-70
src/utils/helpers.py         30      0   100%
-------------------------------------------------------
TOTAL                        95      7    93%
```

## pytest Integration

### Using pytest-cov
```bash
# Install pytest-cov
pip install pytest-cov

# Run tests with coverage
pytest --cov=src

# With coverage report
pytest --cov=src --cov-report=html --cov-report=term

# Set minimum coverage
pytest --cov=src --cov-fail-under=80

# Coverage for specific tests
pytest --cov=src tests/unit/ --cov-report=term-missing
```

### pytest Configuration
```ini
# pytest.ini or setup.cfg
[tool:pytest]
addopts = 
    --cov=src
    --cov-branch
    --cov-report=term-missing:skip-covered
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80
```

### Markers for Coverage
```python
import pytest

@pytest.mark.no_cover
def test_debug_function():
    """Test that shouldn't count toward coverage"""
    debug_only_function()

# In conftest.py
def pytest_collection_modifyitems(config, items):
    for item in items:
        if "no_cover" in item.keywords:
            item.add_marker(pytest.mark.no_cover)
```

## Advanced Features

### Context Coverage
```python
# Track coverage by test
# Run with: coverage run --context=test -m pytest

# In your tests
import coverage
cov = coverage.Coverage()

def test_feature_a():
    cov.switch_context("test_feature_a")
    # test code
    
def test_feature_b():
    cov.switch_context("test_feature_b")
    # test code

# Generate context report
# coverage html --show-contexts
```

### Dynamic Contexts
```bash
# Automatic test contexts
coverage run --context=test -m pytest

# Custom contexts
export COVERAGE_CONTEXT="integration"
coverage run --parallel-mode integration_tests.py

# Combine parallel runs
coverage combine
coverage report
```

### Branch Coverage
```bash
# Enable branch coverage
coverage run --branch -m pytest

# In .coveragerc
[run]
branch = True

# Report shows branch coverage
coverage report
# BranchCov = percentage of branches covered
```

### Excluding Code

#### Using Comments
```python
def complex_function(x):
    if x > 0:
        return x * 2
    else:  # pragma: no cover
        # This branch is for error cases only
        raise ValueError("x must be positive")

class BaseClass:
    def not_implemented(self):  # pragma: no cover
        raise NotImplementedError

    def debug_repr(self):  # pragma: no cover
        return f"<{self.__class__.__name__} at {id(self)}>"
```

#### Excluding Files
```python
# Entire file exclusion
# pragma: no cover
# This file is excluded from coverage

# Or in .coveragerc
[run]
omit = 
    */migrations/*
    */tests/*
    setup.py
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Tests with Coverage

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install coverage pytest-cov
    
    - name: Run tests with coverage
      run: |
        pytest --cov=src --cov-report=xml --cov-report=term
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
    
    - name: Coverage comment
      uses: py-cov-action/python-coverage-comment-action@v3
      with:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        MINIMUM_GREEN: 85
        MINIMUM_ORANGE: 70
```

### GitLab CI
```yaml
test:
  stage: test
  script:
    - pip install -r requirements.txt
    - pip install coverage pytest-cov
    - pytest --cov=src --cov-report=term --cov-report=xml
    - coverage report
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

### Pre-commit Hook
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: coverage-check
        name: Check test coverage
        entry: bash -c 'pytest --cov=src --cov-fail-under=80'
        language: system
        pass_filenames: false
        always_run: true
```

## Coverage Analysis

### Finding Uncovered Code
```bash
# Show missing lines
coverage report -m

# Generate annotated source
coverage annotate
# Creates .py,cover files showing coverage

# HTML report with highlighting
coverage html
# Green = covered, Red = not covered
```

### Coverage Trends
```python
# Track coverage over time
import json
import datetime

def track_coverage():
    with open('coverage.json') as f:
        data = json.load(f)
    
    timestamp = datetime.datetime.now().isoformat()
    percent = data['totals']['percent_covered']
    
    with open('coverage_history.jsonl', 'a') as f:
        json.dump({
            'timestamp': timestamp,
            'coverage': percent,
            'files': data['totals']['num_files']
        }, f)
        f.write('\n')
```

### Diff Coverage
```bash
# Coverage for changed files only
# Using diff-cover
pip install diff-cover

# Generate diff coverage report
diff-cover coverage.xml --compare-branch=main

# With minimum coverage for new code
diff-cover coverage.xml --fail-under=90
```

## Best Practices

### Configuration Management
```python
# Multiple coverage configs for different scenarios

# .coveragerc.unit
[run]
source = src
omit = */integration/*

# .coveragerc.integration  
[run]
source = src
include = */integration/*

# Run with specific config
coverage run --rcfile=.coveragerc.unit -m pytest tests/unit/
```

### Combining Coverage Data
```bash
# Parallel test execution
coverage run --parallel-mode -m pytest tests/unit/
coverage run --parallel-mode -m pytest tests/integration/

# Combine results
coverage combine

# Generate unified report
coverage report
coverage html
```

### Coverage in Different Environments
```python
# Environment-specific coverage
import os
import sys

# Skip coverage in production
if os.getenv('ENV') != 'production':
    import coverage
    cov = coverage.Coverage()
    cov.start()
    
    # Application code
    
    cov.stop()
    cov.save()
```

## Common Patterns

### Testing Error Paths
```python
# Ensure error handling is covered
def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None
    except TypeError:
        return None

def test_divide_coverage():
    assert divide(10, 2) == 5
    assert divide(10, 0) is None  # Cover ZeroDivisionError
    assert divide('10', 2) is None  # Cover TypeError
```

### Conditional Coverage
```python
# Platform-specific code
import sys

def get_platform_info():
    if sys.platform == "win32":  # pragma: no cover
        return "Windows"
    elif sys.platform == "darwin":  # pragma: no cover
        return "macOS"
    else:
        return "Linux"

# Test what's relevant for CI
def test_platform_info():
    # Will only cover the branch that runs
    info = get_platform_info()
    assert info in ["Windows", "macOS", "Linux"]
```

### Mock Coverage
```python
# Ensure mocked code paths are covered
from unittest.mock import patch

def fetch_data():
    try:
        response = external_api_call()
        return response.json()
    except ConnectionError:
        return None

@patch('module.external_api_call')
def test_connection_error(mock_api):
    mock_api.side_effect = ConnectionError()
    assert fetch_data() is None  # Covers error path
```

## Troubleshooting

### Common Issues
```bash
# Coverage data not found
coverage combine  # Try combining first

# Module not found
export PYTHONPATH="${PYTHONPATH}:src"

# Wrong source directory
coverage report --include="src/*"

# Duplicate coverage data
coverage erase  # Clear all coverage data
```

### Debugging Coverage
```python
# Debug why code isn't covered
import coverage

cov = coverage.Coverage(debug=['trace'])
cov.start()

# Your code here

cov.stop()
cov.save()

# Check .coverage file
sqlite3 .coverage "SELECT * FROM file;"
```

## Integration Examples

### Makefile Integration
```makefile
.PHONY: test coverage

test:
	coverage run -m pytest

coverage: test
	coverage report
	coverage html
	@echo "Opening coverage report..."
	@python -m webbrowser htmlcov/index.html

coverage-check: test
	coverage report --fail-under=80
```

### tox Integration
```ini
# tox.ini
[tox]
envlist = py{38,39,310,311}, coverage

[testenv]
deps = 
    pytest
    coverage
commands =
    coverage run -p -m pytest {posargs}

[testenv:coverage]
deps = coverage
skip_install = true
commands =
    coverage combine
    coverage report
    coverage html
```

---
*Coverage.py provides comprehensive code coverage measurement for Python, helping maintain code quality and identify untested code paths.*