---
description: Complex Boolean Expression
globs: "**/*.{js,ts,py,go,java,rb,cs,php,cpp,c}"
alwaysApply: true
---

# Simplify complex boolean expressions

Break down complex boolean expressions into smaller, more readable parts using intermediate variables or helper functions.

## Bad

```python
if (user.is_active and user.has_permission('read') and not user.is_suspended and 
    (user.role == 'admin' or user.role == 'moderator') and 
    user.last_login > datetime.now() - timedelta(days=30)):
    allow_access()
```

## Good

```python
is_user_valid = user.is_active and not user.is_suspended
has_required_permission = user.has_permission('read')
is_privileged_user = user.role in ['admin', 'moderator']
is_recently_active = user.last_login > datetime.now() - timedelta(days=30)

if is_user_valid and has_required_permission and is_privileged_user and is_recently_active:
    allow_access()
```

## Why

Complex boolean expressions are error-prone and difficult to debug. Breaking them into named variables makes the logic clearer and easier to modify or test individual conditions.

