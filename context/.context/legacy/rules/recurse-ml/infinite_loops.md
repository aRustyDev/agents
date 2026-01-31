---
description: Infinite Loop
globs: "**/*.{js,ts,py,go,java,rb,cs,php,cpp,c}"
alwaysApply: true
---

# Prevent infinite loops

Ensure all loops have proper termination conditions and avoid situations where the loop condition never becomes false.

## Bad

```python
i = 0
while i < 10:
    print(i)
    # Missing increment - infinite loop!
```

**Also bad:**

```python
while True:
    process_data()
    # No break condition
```

## Good

```python
i = 0
while i < 10:
    print(i)
    i += 1  # Proper increment
```

**Or with explicit break:**

```python
while True:
    data = get_next_data()
    if not data:
        break
    process_data(data)
```

## Why

Infinite loops cause programs to hang or consume excessive resources. Always ensure loop variables are properly modified and termination conditions are reachable.

