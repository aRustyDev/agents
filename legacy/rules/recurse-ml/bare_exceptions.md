---
description: Bare Exceptions
globs: "*.{py}"
alwaysApply: true
---

# Don't catch bare exceptions

## Bad

```python
try:
    risky_operation()
except:
    handle_error()
```

**Equally bad:**

```python
try:
    risky_operation()
except Exception:
    handle_error()
```

## Good

```python
try:
    risky_operation()
except SpecificException:
    handle_error()
```


## Exception

This rule doesn't apply if we reraise the exception after handling it:

```python
try:
    risky_operation()
except SpecificException as e:
    handle_error(e)
    raise  # Reraise the exception
```

## Why

Catching bare exceptions can hide unintended exceptions leading to bugs.
They give an illusion of stability while potentially masking issues that should be addressed.

