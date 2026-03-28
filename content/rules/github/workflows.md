---
globs:
  - ".github/workflows/*.yml"
  - ".github/workflows/*.yaml"
---

Prefer to reuse workflows from github.com/aRustyDev/gh
- if the available workflows are not sufficient, first determine if extending an existing workflow is possible before creating a new one.
- Any extension of a workflow MUST be backwards compatible and MUST NOT break existing functionality.
