---
description: Explicit Conditionals
globs: "*.{py}"
alwaysApply: true
---

# Explicit Conditionals

## Lists

Don't use empty list as a conditional statement.
Instead check the length of the list explicitly.

**Bad:**

```python
if my_list:
    # do something
```

**Good:**

```python
if len(my_list) > 0:
    # do something
```
## Explicit None Check

Don't implicitly check for None in conditionals.
Instead check for None explicitly.

**Bad:**

```python
if my_var:
    # do something
```

**Good:**

```python
if my_var is not None:
    # do something
```

## Exception

DON'T ever compare compare boolean values to True or False.

**AWFUL:**

```python
my_var = is_valid(my_input)
if my_var == True:
    # do something
```

**Good:**

```python
my_var = is_valid(my_input)
if my_var:
    # do something
```
