---
name: "Python Typing Conventions"
glob: "*.py"
---

# Python Typing Conventions

When using python types:
1. ALWAYS use built in types over `typing` module types.
    For example, prefer `list` over `typing.List`, `dict` over `typing.Dict`, etc.
2. ALWAYS use `typing.Optional` for optional types.
    For example, prefer `Optional[str]` over `str | None`.
3. Never use `# type: ignore` to ignore type errors.

