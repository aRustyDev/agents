---
description: Unexpected Mutability Side Effects
globs: "*.py"
alwaysApply: true
---

# Functions should not have unexpected mutability side effects

## Bad

```python
def normalize_values(data_dict):
    for key, value in data_dict.items():
        data_dict[key] = value.lower().strip()
    return data_dict

def filter_items(items):
    items.sort()
    return [item for item in items if item > 0]
```

## Good

```python
def normalize_values(data_dict):
    """Returns a new dictionary with normalized values."""
    return {key: value.lower().strip() for key, value in data_dict.items()}

def filter_items(items):
    """Returns a new filtered and sorted list."""
    sorted_items = sorted(items)
    return [item for item in sorted_items if item > 0]
```

**Or be explicit about in-place operations:**

```python
def normalize_values_inplace(data_dict):
    """Modifies the dictionary in-place and returns it."""
    for key, value in data_dict.items():
        data_dict[key] = value.lower().strip()
    return data_dict

def sort_and_filter_inplace(items):
    """Sorts the list in-place and returns filtered items."""
    items.sort()
    return [item for item in items if item > 0]
```

## Why

Functions that appear to be pure but modify their input arguments create unexpected side effects. This violates the principle of least surprise and can lead to difficult-to-debug issues where data is modified unexpectedly. Functions should either clearly indicate they operate in-place or return new objects without modifying inputs.

