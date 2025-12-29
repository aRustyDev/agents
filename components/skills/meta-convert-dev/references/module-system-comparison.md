# Module System Comparison

Reference for translating module/package systems between languages.

## Quick Comparison

| Aspect | TypeScript/JS | Python | Rust | Go |
|--------|---------------|--------|------|-----|
| Unit of code | File (module) | File (module) | File (module) | Package (directory) |
| Namespace | ES Modules | Packages | Crates/Modules | Packages |
| Visibility | `export` | `_prefix` convention | `pub` | PascalCase |
| Import style | Named/default | Named | Named (use) | Package-level |
| Circular deps | Allowed (carefully) | Allowed (carefully) | Not allowed | Not allowed |

---

## TypeScript / JavaScript

### Module Declaration

```typescript
// Named exports (preferred)
export function doSomething() { }
export const VALUE = 42;
export interface User { }
export class Service { }

// Default export
export default class MainClass { }

// Re-export
export { something } from './other';
export * from './utils';
export { foo as bar } from './foo';
```

### Import Patterns

```typescript
// Named imports
import { doSomething, VALUE } from './module';

// Default import
import MainClass from './module';

// Namespace import
import * as utils from './utils';

// Side effect import
import './polyfills';

// Dynamic import
const module = await import('./lazy');
```

### Module Resolution

```
project/
├── package.json
├── src/
│   ├── index.ts        # Entry point
│   ├── utils/
│   │   ├── index.ts    # utils barrel
│   │   └── helpers.ts
│   └── services/
│       └── api.ts
```

---

## Python

### Module Declaration

```python
# my_module.py

# Public by convention (no underscore)
def public_function():
    pass

PUBLIC_CONSTANT = 42

class PublicClass:
    pass

# Private by convention (single underscore)
def _private_function():
    pass

_PRIVATE_CONSTANT = "internal"

# Name-mangled (double underscore in classes)
class MyClass:
    def __private_method(self):
        pass
```

### Package Structure

```python
# __init__.py - Package initialization
from .module import public_function
from .subpackage import SubClass

__all__ = ['public_function', 'SubClass']  # Controls `from pkg import *`
```

### Import Patterns

```python
# Absolute imports (preferred)
from mypackage.module import function
from mypackage import module

# Relative imports (within package)
from . import sibling_module
from .sibling import function
from ..parent import something

# Namespace import
import mypackage.module as mod

# Conditional import
try:
    import fast_module as impl
except ImportError:
    import slow_module as impl
```

### Module Resolution

```
mypackage/
├── __init__.py         # Package marker
├── module.py
├── subpackage/
│   ├── __init__.py
│   └── submodule.py
└── py.typed            # PEP 561 marker for typing
```

---

## Rust

### Module Declaration

```rust
// lib.rs or main.rs

// Declare submodules
mod utils;           // Load from utils.rs or utils/mod.rs
mod services;        // Load from services.rs or services/mod.rs
pub mod public_mod;  // Public module

// Inline module
mod inline {
    pub fn helper() { }
}

// Re-export (common pattern)
pub use utils::helper_function;
pub use services::Service;
```

### Visibility

```rust
// Private (default)
fn private_function() { }
struct PrivateStruct { }

// Public
pub fn public_function() { }
pub struct PublicStruct {
    pub public_field: i32,
    private_field: String,  // Field still private
}

// Crate-public (visible within crate only)
pub(crate) fn crate_function() { }

// Super-public (visible to parent module)
pub(super) fn parent_visible() { }

// Path-restricted
pub(in crate::module) fn restricted() { }
```

### Import Patterns (use)

```rust
// Specific items
use std::collections::HashMap;
use crate::utils::{helper, another_helper};

// Glob import (avoid in libraries)
use std::io::prelude::*;

// Renaming
use std::io::Result as IoResult;

// Nested paths
use std::{
    collections::{HashMap, HashSet},
    io::{self, Read, Write},
};

// Re-export
pub use self::internal::PublicApi;
```

### Module Resolution

```
src/
├── lib.rs              # Library root
├── main.rs             # Binary root (optional)
├── utils.rs            # mod utils (file style)
├── services/           # mod services (directory style)
│   ├── mod.rs          # Module root
│   └── api.rs          # services::api
└── models/
    ├── mod.rs
    ├── user.rs
    └── order.rs
```

---

## Go

### Package Declaration

```go
// Every file starts with package declaration
package mypackage

// Exported (uppercase)
func PublicFunction() { }
var PublicVar = 42
type PublicStruct struct {
    PublicField  string
    privateField int  // unexported field
}

// Unexported (lowercase)
func privateFunction() { }
var privateVar = "internal"
type privateStruct struct { }
```

### Import Patterns

```go
// Single import
import "fmt"

// Multiple imports
import (
    "fmt"
    "strings"

    // Third-party
    "github.com/gin-gonic/gin"

    // Local packages
    "mymodule/internal/utils"
)

// Aliased import
import (
    myfmt "fmt"
    _ "github.com/lib/pq"  // Side effect only
    . "math"               // Dot import (avoid)
)
```

### Package Structure

```
mymodule/
├── go.mod              # Module definition
├── main.go             # package main
├── mypackage/          # package mypackage
│   ├── public.go
│   └── private.go
├── internal/           # Internal packages (not importable from outside)
│   └── utils/
│       └── helpers.go
└── cmd/                # Multiple binaries
    ├── server/
    │   └── main.go
    └── cli/
        └── main.go
```

### Internal Packages

Go has special `internal/` directory semantics:

```
mymodule/
├── internal/           # Only importable by mymodule and children
│   └── secret/
└── pkg/                # Convention: public packages
    └── api/
```

---

## Translation Patterns

### TypeScript → Python

| TypeScript | Python |
|------------|--------|
| `export function foo()` | `def foo():` (public by default) |
| `export default class X` | `class X:` + add to `__all__` |
| `import { x } from './mod'` | `from .mod import x` |
| `import * as utils` | `from . import utils` |
| Private (no export) | `def _private():` |
| `index.ts` barrel | `__init__.py` |

### TypeScript → Rust

| TypeScript | Rust |
|------------|------|
| `export function foo()` | `pub fn foo()` |
| `export default` | `pub use` re-export |
| `import { x } from './mod'` | `use crate::mod::x;` |
| `import * as utils` | `use crate::utils;` |
| Private (no export) | `fn private()` (default) |
| `index.ts` barrel | `mod.rs` or `lib.rs` re-exports |

### TypeScript → Go

| TypeScript | Go |
|------------|-----|
| `export function foo()` | `func Foo()` (uppercase) |
| `export default` | N/A (no default exports) |
| `import { x } from './mod'` | `import "pkg/mod"; mod.X` |
| Private (no export) | `func foo()` (lowercase) |
| `index.ts` barrel | N/A (all files in dir = package) |

### Python → Rust

| Python | Rust |
|--------|------|
| `def function():` | `pub fn function()` |
| `_private()` | `fn private()` |
| `__init__.py` | `mod.rs` or `lib.rs` |
| `from .mod import x` | `use crate::mod::x;` |
| `__all__` | `pub use` re-exports |

### Go → Rust

| Go | Rust |
|----|------|
| `func Public()` | `pub fn public()` |
| `func private()` | `fn private()` |
| `internal/` | `pub(crate)` |
| Package (directory) | Module (file or directory) |
| `import "pkg"` | `use crate::pkg;` |

---

## Circular Dependencies

### Handling Approaches

| Language | Circular Deps | Solution |
|----------|---------------|----------|
| TypeScript | Allowed (runtime issues) | Type-only imports, restructure |
| Python | Allowed (import at use) | Import inside function, restructure |
| Rust | Not allowed | Restructure into shared module |
| Go | Not allowed | Restructure, use interfaces |

### Resolution Pattern

```
Before (circular):
A ──imports──► B
▲              │
└───imports────┘

After (resolved):
A ──imports──► Common ◄──imports── B
```

---

## Re-export Patterns

### TypeScript (barrel)
```typescript
// index.ts
export { User, UserService } from './user';
export { Order } from './order';
export * from './utils';
```

### Python (__init__.py)
```python
from .user import User, UserService
from .order import Order
from .utils import *

__all__ = ['User', 'UserService', 'Order']
```

### Rust (lib.rs or mod.rs)
```rust
mod user;
mod order;
mod utils;

pub use user::{User, UserService};
pub use order::Order;
pub use utils::*;
```

### Go (no re-export, flat structure)
```go
// Go doesn't have re-exports
// All exported items in package are directly accessible
// Consumers import the package and access items directly
```

---

## Related

- `meta-convert-dev` - Core conversion patterns
- `references/build-system-mapping.md` - Build configuration
- `references/naming-conventions.md` - Naming translation
