---
description: Unreachable Code
globs: "**/*.{js,ts,py,go,java,rb,cs,php,cpp,c}"
alwaysApply: true
---

# Remove unreachable code

Eliminate code that can never be executed due to control flow issues such as statements after return, break, continue, or within impossible conditions.

## Bad

```python
def process_user(user):
    if user.is_valid():
        return user.process()
    else:
        return None
    
    # This code is unreachable
    print("Processing complete")
    log_activity(user)
```

**Also bad:**

```python
if True:
    return "success"
else:
    return "failure"  # Unreachable
```

## Good

```python
def process_user(user):
    if user.is_valid():
        result = user.process()
        print("Processing complete")
        log_activity(user)
        return result
    else:
        return None
```

