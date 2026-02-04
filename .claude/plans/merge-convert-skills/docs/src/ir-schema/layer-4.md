# Layer 4: Structural IR

The Structural IR is the highest-level layer in the IR architecture, representing code organization constructs such as modules, packages, namespaces, and their relationships.

**Version:** 1.0
**Generated:** 2026-02-04
**Task:** ai-f33.2

---

## 1. Overview

Layer 4 captures the organizational structure of source code that exists above individual type definitions and functions. This includes:

- **Modules and packages**: Logical groupings of code
- **Namespaces**: Hierarchical naming schemes
- **Visibility boundaries**: Public/private/internal access control
- **Import/export relationships**: Dependencies between modules
- **Compilation units**: Physical file organization

### 1.1 Layer Position

```
Layer 4: Structural IR  <-- This document
    |
    v (contains)
Layer 3: Type IR        Types, interfaces, traits
    |
    v (contains)
Layer 2: Control Flow   Functions, control patterns
    |
    v (contains)
Layer 1: Data Flow      Bindings, lifetimes
    |
    v (contains)
Layer 0: Expression     AST details (optional)
```

### 1.2 When Layer 4 is Used

| Extraction Mode | Layer 4 Included | Notes |
|-----------------|------------------|-------|
| `full_module` | Yes | Complete structural information |
| `single_function` | Partial | Module context for the function |
| `type_only` | Yes | Module structure without function bodies |
| `signature_only` | Yes | API surface with visibility |

---

## 2. Schema Elements

### 2.1 Module

The primary container for code organization.

```yaml
module:
  id: ModuleId                    # Unique identifier
  name: string                    # Module name (e.g., "utils", "http")
  path: string[]                  # Namespace path (e.g., ["std", "collections"])
  visibility: Visibility          # Module-level visibility
  imports: Import[]               # Dependencies on other modules
  exports: Export[]               # Items exposed to consumers
  definitions: Definition[]       # Types, functions, constants defined here
  submodules: ModuleId[]          # Nested modules (optional)
  extraction_scope: ExtractionScope
  metadata: ModuleMetadata

Visibility:
  - public                        # Accessible from anywhere
  - internal                      # Accessible within package/crate
  - private                       # Accessible only within this module

ExtractionScope:
  - full                          # All content extracted
  - partial                       # Some content omitted or summarized
```

### 2.2 Module Metadata

Tracks extraction provenance and context.

```yaml
ModuleMetadata:
  source_file: string             # Original file path
  source_language: string         # Language identifier
  extraction_version: string      # IR version used (e.g., "ir-v1.0")
  extraction_mode: ExtractionMode
  source_hash: string?            # SHA-256 of source file (optional)
  extraction_timestamp: datetime? # When extraction occurred
  documentation: string?          # Module-level documentation

ExtractionMode:
  - full_module                   # Complete codebase conversion
  - single_function               # Function-level extraction
  - type_only                     # Interface/type extraction only
  - signature_only                # API surface only
```

### 2.3 Import

Represents a dependency on another module.

```yaml
import:
  id: ImportId                    # Unique identifier
  module_path: string[]           # Path to imported module
  imported_items: ImportedItem[]  # Specific items or wildcard
  alias: string?                  # Module alias (e.g., "np" for numpy)
  is_reexport: bool               # Whether this import is re-exported

ImportedItem:
  name: string                    # Original name in source module
  alias: string?                  # Local alias if renamed
  kind: ImportKind                # Type of imported item

ImportKind:
  - type                          # Type definition
  - function                      # Function or method
  - constant                      # Constant value
  - variable                      # Variable binding
  - module                        # Submodule
  - wildcard                      # Wildcard import (e.g., import *)
```

### 2.4 Export

Represents an item exposed to consumers of this module.

```yaml
export:
  id: ExportId                    # Unique identifier
  item: DefinitionRef             # Reference to the exported definition
  alias: string?                  # Public name if different from internal
  visibility: ExportVisibility
  documentation: string?          # Public documentation

ExportVisibility:
  - public                        # Accessible from anywhere
  - package                       # Accessible within the same package
  - internal                      # Accessible within a defined scope

DefinitionRef:
  module_id: ModuleId             # Module containing the definition
  definition_id: DefinitionId     # The definition itself
```

### 2.5 Definition

A reference to a defined item within the module.

```yaml
definition:
  id: DefinitionId                # Unique identifier
  kind: DefinitionKind            # Type of definition
  ref: TypeId | FunctionId | ConstantId | VariableId
  visibility: Visibility          # Item-level visibility
  attributes: Attribute[]         # Decorators, annotations, etc.

DefinitionKind:
  - type                          # struct, class, enum, interface, trait
  - function                      # function, method
  - constant                      # const, final static
  - variable                      # let, var, static mut

Attribute:
  name: string                    # Attribute name
  arguments: any[]?               # Attribute arguments
  target: string                  # What it applies to
```

---

## 3. Language Mappings

### 3.1 Python Module Example

**Source:**
```python
# src/mypackage/utils/helpers.py
"""Utility helper functions."""

from typing import Optional, List
from ..core import BaseClass
from . import constants

__all__ = ['process_data', 'Helper']

def process_data(items: List[str]) -> Optional[str]:
    """Process a list of items."""
    return items[0] if items else None

class Helper(BaseClass):
    """A helper class."""
    pass
```

**IR Representation:**
```yaml
module:
  id: "mod_mypackage_utils_helpers"
  name: "helpers"
  path: ["mypackage", "utils"]
  visibility: public
  imports:
    - id: "imp_typing"
      module_path: ["typing"]
      imported_items:
        - name: "Optional"
          kind: type
        - name: "List"
          kind: type
      alias: null
    - id: "imp_core"
      module_path: ["mypackage", "core"]
      imported_items:
        - name: "BaseClass"
          kind: type
      alias: null
    - id: "imp_constants"
      module_path: ["mypackage", "utils", "constants"]
      imported_items: []
      alias: "constants"
  exports:
    - id: "exp_process_data"
      item:
        module_id: "mod_mypackage_utils_helpers"
        definition_id: "def_process_data"
      visibility: public
    - id: "exp_Helper"
      item:
        module_id: "mod_mypackage_utils_helpers"
        definition_id: "def_Helper"
      visibility: public
  definitions:
    - id: "def_process_data"
      kind: function
      ref: "func_process_data"
      visibility: public
    - id: "def_Helper"
      kind: type
      ref: "type_Helper"
      visibility: public
  extraction_scope: full
  metadata:
    source_file: "src/mypackage/utils/helpers.py"
    source_language: "python"
    extraction_version: "ir-v1.0"
    extraction_mode: full_module
    documentation: "Utility helper functions."
```

### 3.2 Rust Crate Example

**Source:**
```rust
// src/lib.rs
//! HTTP client library.

pub mod request;
pub mod response;
mod internal;

pub use request::Request;
pub use response::{Response, StatusCode};

use std::collections::HashMap;

pub const DEFAULT_TIMEOUT: u64 = 30;

pub fn get(url: &str) -> Result<Response, Error> {
    // ...
}
```

**IR Representation:**
```yaml
module:
  id: "mod_http_client"
  name: "http_client"
  path: []
  visibility: public
  submodules:
    - "mod_http_client_request"
    - "mod_http_client_response"
    - "mod_http_client_internal"
  imports:
    - id: "imp_std_collections"
      module_path: ["std", "collections"]
      imported_items:
        - name: "HashMap"
          kind: type
      alias: null
  exports:
    - id: "exp_Request"
      item:
        module_id: "mod_http_client_request"
        definition_id: "def_Request"
      visibility: public
    - id: "exp_Response"
      item:
        module_id: "mod_http_client_response"
        definition_id: "def_Response"
      visibility: public
    - id: "exp_StatusCode"
      item:
        module_id: "mod_http_client_response"
        definition_id: "def_StatusCode"
      visibility: public
    - id: "exp_DEFAULT_TIMEOUT"
      item:
        module_id: "mod_http_client"
        definition_id: "def_DEFAULT_TIMEOUT"
      visibility: public
    - id: "exp_get"
      item:
        module_id: "mod_http_client"
        definition_id: "def_get"
      visibility: public
  definitions:
    - id: "def_DEFAULT_TIMEOUT"
      kind: constant
      ref: "const_DEFAULT_TIMEOUT"
      visibility: public
    - id: "def_get"
      kind: function
      ref: "func_get"
      visibility: public
  extraction_scope: full
  metadata:
    source_file: "src/lib.rs"
    source_language: "rust"
    extraction_version: "ir-v1.0"
    extraction_mode: full_module
    documentation: "HTTP client library."
```

### 3.3 Java Package Example

**Source:**
```java
// src/main/java/com/example/api/UserService.java
package com.example.api;

import java.util.List;
import java.util.Optional;
import com.example.model.User;
import com.example.repository.UserRepository;

/**
 * Service for user operations.
 */
public class UserService {
    private final UserRepository repository;

    public UserService(UserRepository repository) {
        this.repository = repository;
    }

    public Optional<User> findById(Long id) {
        return repository.findById(id);
    }

    public List<User> findAll() {
        return repository.findAll();
    }
}
```

**IR Representation:**
```yaml
module:
  id: "mod_com_example_api"
  name: "api"
  path: ["com", "example"]
  visibility: public
  imports:
    - id: "imp_java_util_list"
      module_path: ["java", "util"]
      imported_items:
        - name: "List"
          kind: type
      alias: null
    - id: "imp_java_util_optional"
      module_path: ["java", "util"]
      imported_items:
        - name: "Optional"
          kind: type
      alias: null
    - id: "imp_user"
      module_path: ["com", "example", "model"]
      imported_items:
        - name: "User"
          kind: type
      alias: null
    - id: "imp_user_repository"
      module_path: ["com", "example", "repository"]
      imported_items:
        - name: "UserRepository"
          kind: type
      alias: null
  exports:
    - id: "exp_UserService"
      item:
        module_id: "mod_com_example_api"
        definition_id: "def_UserService"
      visibility: public
  definitions:
    - id: "def_UserService"
      kind: type
      ref: "type_UserService"
      visibility: public
  extraction_scope: full
  metadata:
    source_file: "src/main/java/com/example/api/UserService.java"
    source_language: "java"
    extraction_version: "ir-v1.0"
    extraction_mode: full_module
    documentation: "Service for user operations."
```

---

## 4. Relationships to Other Layers

### 4.1 Layer 4 to Layer 3 (Types)

Layer 4 modules contain Layer 3 type definitions.

```
Module (Layer 4)
  |
  +-- definitions[kind=type]
        |
        +-- ref --> TypeDef (Layer 3)
                      |
                      +-- fields, methods, variants
```

**Connection points:**
- `Definition.ref` (when `kind=type`) references a `TypeId` in Layer 3
- Type visibility in Layer 3 inherits from or is constrained by module visibility
- Generic types in Layer 3 may reference types from imported modules

### 4.2 Layer 4 to Layer 2 (Functions)

Layer 4 modules contain Layer 2 function declarations.

```
Module (Layer 4)
  |
  +-- definitions[kind=function]
        |
        +-- ref --> Function (Layer 2)
                      |
                      +-- params, return_type, body
```

**Connection points:**
- `Definition.ref` (when `kind=function`) references a `FunctionId` in Layer 2
- Function visibility in Layer 2 aligns with export visibility
- Method definitions are accessed through their containing type

### 4.3 Import Resolution

Imports in Layer 4 create references that resolve to definitions in other modules.

```yaml
# Import resolution chain
import:
  module_path: ["std", "collections"]
  imported_items:
    - name: "HashMap"
      kind: type

# Resolves to
resolution:
  target_module: "mod_std_collections"
  target_definition: "def_HashMap"
  target_type: "type_HashMap"  # Layer 3 TypeId
```

---

## 5. Extraction Considerations

### 5.1 Full Extraction

When `extraction_scope: full`:

- All imports are resolved and recorded
- All exports are enumerated
- All definitions have complete Layer 3/2 representations
- Submodule structure is preserved

### 5.2 Partial Extraction

When `extraction_scope: partial`:

```yaml
module:
  extraction_scope: partial
  metadata:
    extraction_mode: single_function

  # Partial information
  imports:
    - module_path: ["external", "lib"]
      imported_items:
        - name: "ExternalType"
          kind: type
          # Note: ExternalType not included in IR

  definitions:
    - id: "def_target_function"
      kind: function
      ref: "func_target"      # Full representation
    - id: "def_helper"
      kind: function
      ref: null               # Body not extracted
      visibility: private
```

**Partial extraction markers:**

| Field | Full Mode | Partial Mode |
|-------|-----------|--------------|
| `imports` | All resolved | May include unresolved references |
| `exports` | Complete | May be incomplete |
| `definitions.ref` | Always present | May be `null` for omitted items |
| `submodules` | All included | May be omitted |

### 5.3 External References

When partial extraction encounters external dependencies:

```yaml
# External reference placeholder
external_reference:
  module_path: ["external", "package"]
  name: "ExternalType"
  kind: type
  resolved: false
  notes: "Type from external package, not included in extraction"
```

---

## 6. Language-Specific Notes

### 6.1 Visibility Mapping

| Language | `public` | `internal` | `private` |
|----------|----------|------------|-----------|
| Python | `__all__` or no `_` prefix | N/A (convention only) | `_` prefix |
| Rust | `pub` | `pub(crate)` | (no modifier) |
| Java | `public` | `protected`, package-private | `private` |
| Go | Capitalized name | N/A | Lowercase name |
| TypeScript | `export` | N/A | (no export) |
| C# | `public` | `internal` | `private` |

### 6.2 Module System Differences

**Python:**
- File-based modules (`__init__.py` creates packages)
- No explicit exports (use `__all__` convention)
- Circular imports possible but problematic

**Rust:**
- Declaration-based modules (`mod` keyword)
- Explicit `pub use` for re-exports
- Strict module hierarchy

**Java:**
- Package-based organization
- One public class per file (conventional)
- Fully qualified names

**Go:**
- Directory-based packages
- Visibility by capitalization
- No subpackages (flat structure)

### 6.3 Import Style Mapping

| Source Pattern | IR Representation |
|----------------|-------------------|
| `import foo` (Python) | `imported_items: []`, `alias: "foo"` |
| `from foo import bar` | `imported_items: [{name: "bar"}]` |
| `from foo import *` | `imported_items: [{kind: wildcard}]` |
| `use foo::bar` (Rust) | `imported_items: [{name: "bar"}]` |
| `use foo::*` | `imported_items: [{kind: wildcard}]` |
| `import foo.Bar` (Java) | `imported_items: [{name: "Bar"}]` |

### 6.4 Re-export Patterns

**Python:**
```python
# mypackage/__init__.py
from .submodule import public_function
```

**Rust:**
```rust
// lib.rs
pub use submodule::public_function;
```

**IR Representation:**
```yaml
import:
  id: "imp_submodule"
  module_path: ["mypackage", "submodule"]
  imported_items:
    - name: "public_function"
      kind: function
  is_reexport: true

export:
  id: "exp_public_function"
  item:
    module_id: "mod_mypackage_submodule"
    definition_id: "def_public_function"
  visibility: public
```

---

## 7. Semantic Annotations

Layer 4 supports annotations for structural concerns.

### 7.1 Common Annotations

```yaml
# Module-level deprecation
semantic_annotation:
  target: "mod_legacy_api"
  kind: deprecation
  value:
    deprecated_since: "2.0.0"
    removal_version: "3.0.0"
    replacement: "mod_new_api"
  confidence: 1.0
  source: explicit

# Circular dependency warning
semantic_annotation:
  target: "mod_feature_a"
  kind: circular_dependency
  value:
    cycle: ["mod_feature_a", "mod_feature_b", "mod_feature_a"]
    severity: warning
  confidence: 1.0
  source: inferred

# Visibility widening during conversion
semantic_annotation:
  target: "def_internal_helper"
  kind: visibility_change
  value:
    original: private
    converted: internal
    reason: "Required for cross-module access in target language"
  confidence: 0.9
  source: inferred
```

### 7.2 Gap Markers for Layer 4

```yaml
# Module system mismatch
gap_marker:
  id: "gap_circular_import"
  location: "mod_feature_a"
  gap_type: structural
  severity: medium
  description: "Circular import between modules"
  source_concept: "Python circular import"
  target_concept: "Rust strict module hierarchy"
  suggested_mitigations:
    - "Extract shared types to common module"
    - "Use forward declarations"
  preservation_level: 2

# Visibility system mismatch
gap_marker:
  id: "gap_visibility_mapping"
  location: "def_package_private"
  gap_type: structural
  severity: low
  description: "No direct equivalent for package-private visibility"
  source_concept: "Java package-private"
  target_concept: "Rust pub(crate) or pub(super)"
  suggested_mitigations:
    - "Use pub(crate) for crate-wide access"
    - "Restructure module hierarchy"
  preservation_level: 2
```

---

## 8. Validation Rules

### 8.1 Structural Integrity

| Rule | Description | Severity |
|------|-------------|----------|
| `L4-001` | Module ID must be unique | Error |
| `L4-002` | All exports must reference valid definitions | Error |
| `L4-003` | Import paths must be valid | Warning |
| `L4-004` | No duplicate export aliases | Error |
| `L4-005` | Private items cannot be exported as public | Error |

### 8.2 Cross-Layer Consistency

| Rule | Description | Severity |
|------|-------------|----------|
| `L4-L3-001` | Type definitions must exist in Layer 3 | Error |
| `L4-L2-001` | Function definitions must exist in Layer 2 | Error |
| `L4-META-001` | Source language must match Layer 3/2 types | Warning |

---

## 9. Serialization Notes

### 9.1 JSON Schema Considerations

```json
{
  "type": "object",
  "properties": {
    "module": {
      "type": "object",
      "required": ["id", "name", "path", "visibility"],
      "properties": {
        "id": { "type": "string", "pattern": "^mod_" },
        "path": { "type": "array", "items": { "type": "string" } },
        "visibility": { "enum": ["public", "internal", "private"] }
      }
    }
  }
}
```

### 9.2 Protobuf Mapping (Future)

```protobuf
message Module {
  string id = 1;
  string name = 2;
  repeated string path = 3;
  Visibility visibility = 4;
  repeated Import imports = 5;
  repeated Export exports = 6;
  repeated Definition definitions = 7;
  ExtractionScope extraction_scope = 8;
  ModuleMetadata metadata = 9;
}

enum Visibility {
  VISIBILITY_UNSPECIFIED = 0;
  VISIBILITY_PUBLIC = 1;
  VISIBILITY_INTERNAL = 2;
  VISIBILITY_PRIVATE = 3;
}
```

---

## 10. Cross-References

| Document | Relevance |
|----------|-----------|
| `overview.md` | IR architecture context |
| `layer-3.md` | Type definitions contained by modules |
| `layer-2.md` | Function definitions contained by modules |
| `preservation-levels.md` | How module structure affects preservation |
| `binary-formats.md` | Serialization specifications |

---

*Generated for Phase 4: IR Schema Design (ai-f33.2)*
