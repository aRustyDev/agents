---
description: Complex Execution Flow
globs: "**/*.{js,ts,py,go,java,rb,cs,php,cpp,c}"
alwaysApply: true
---

# Avoid complex execution flow

Keep code execution flow simple and sequential. Avoid deeply nested conditions, excessive function calls within expressions, and convoluted control structures that make code difficult to follow.

## Bad

```python
def process_data(data):
    if data:
        if isinstance(data, list):
            if len(data) > 0:
                for item in data:
                    if item:
                        if hasattr(item, 'process'):
                            result = item.process() if item.is_valid() else None
                            if result:
                                return transform(result) if should_transform() else result
    return None
```

## Good

```python
def process_data(data):
    if not data or not isinstance(data, list) or len(data) == 0:
        return None
    
    for item in data:
        if not item or not hasattr(item, 'process'):
            continue
            
        if not item.is_valid():
            continue
            
        result = item.process()
        if not result:
            continue
            
        return transform(result) if should_transform() else result
    
    return None
```

## Why

Complex execution flow increases cognitive load, makes debugging difficult, and increases the likelihood of bugs. Linear, predictable flow is easier to understand, test, and maintain.

