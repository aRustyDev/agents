---
description: Mutable Default Arguments
globs: "*.py"
alwaysApply: true
---

# Avoid mutable objects as default function arguments

## Bad

```python
def add_item(item, target_list=[]):
    target_list.append(item)
    return target_list

# This creates unexpected behavior
list1 = add_item("first")
list2 = add_item("second")  # list2 will contain ["first", "second"]
```

**Also bad:**

```python
def process_data(data, cache={}):
    if data in cache:
        return cache[data]
    result = expensive_operation(data)
    cache[data] = result
    return result
```

## Good

```python
def add_item(item, target_list=None):
    if target_list is None:
        target_list = []
    target_list.append(item)
    return target_list

def process_data(data, cache=None):
    if cache is None:
        cache = {}
    if data in cache:
        return cache[data]
    result = expensive_operation(data)
    cache[data] = result
    return result
```

## Why

Python evaluates default arguments only once when the function is defined, not each time it's called. This means mutable defaults are shared across all function calls, leading to unexpected behavior where modifications persist between calls.

