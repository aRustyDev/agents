# Module Interface Specification

Common interface for module creation and validation.

## Module Structure
- name: string
- version: string
- dependencies: array
- validate(): function

## Shared Constants
MODULE_VERSION_PATTERN = /^\d+\.\d+\.\d+$/
MAX_DEPENDENCY_DEPTH = 3