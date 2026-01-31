---
name: lang-rust-library-dev
description: Rust crate and library development patterns covering Cargo.toml for libraries, crate structure, module organization, rustdoc, publishing to crates.io, feature flags, semantic versioning, and API design. Use when creating a Rust library or crate, publishing to crates.io, documenting APIs with rustdoc, or managing library features and versions. This is the specialized skill for Rust library/crate development.
---

# Rust Library Development

Specialized patterns for creating, maintaining, and publishing Rust libraries and crates. This skill focuses on library-specific concerns like API design, documentation, versioning, and distribution.

## Overview

```
┌──────────────────────────────────────────────────────────────┐
│                Rust Skill Hierarchy                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│              ┌─────────────────────┐                         │
│              │   lang-rust-dev     │                         │
│              │   (foundation)      │                         │
│              └──────────┬──────────┘                         │
│                         │                                    │
│     ┌───────────┬───────┼───────┬───────────┐               │
│     │           │       │       │           │               │
│     ▼           ▼       ▼       ▼           ▼               │
│ ┌────────┐ ┌────────┐ ... ┌─────────────────────┐           │
│ │  bin   │ │testing │     │lang-rust-library-dev│ ◄─ HERE   │
│ │  -dev  │ │  -dev  │     │   (library focus)   │           │
│ └────────┘ └────────┘     └─────────────────────┘           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**This skill covers:**
- Cargo.toml configuration for libraries
- Crate structure and module organization
- Public API design and stability
- Documentation with rustdoc
- Publishing to crates.io
- Feature flags and conditional compilation
- Semantic versioning (SemVer)
- Dependency management for libraries
- Examples, tests, and benches organization

**This skill does NOT cover:**
- Binary application development → `lang-rust-bin-dev`
- Testing strategies → `lang-rust-testing-dev`
- Async runtime patterns → `lang-rust-async-dev`
- General Rust syntax → `lang-rust-dev`

---

## Quick Reference

| Task | Command/Pattern |
|------|-----------------|
| Create new library | `cargo new mylib --lib` |
| Build library | `cargo build --release` |
| Run library tests | `cargo test` |
| Generate docs | `cargo doc --open` |
| Check API docs | `cargo doc --no-deps --open` |
| Publish to crates.io | `cargo publish` |
| Feature flag | `#[cfg(feature = "my-feature")]` |
| Public re-export | `pub use internal::Type;` |
| Doc example | `/// # Examples` |
| Hide from docs | `#[doc(hidden)]` |

---

## Skill Routing

Use this table to find the right specialized skill:

| When you need to... | Use this skill |
|---------------------|----------------|
| Create and publish Rust libraries | This skill (`lang-rust-library-dev`) |
| Build CLI or binary applications | `lang-rust-bin-dev` |
| Set up testing, mocking, property tests | `lang-rust-testing-dev` |
| Work with async/await, tokio, futures | `lang-rust-async-dev` |
| Learn Rust syntax and fundamentals | `lang-rust-dev` |

---

## Cargo.toml for Libraries

### Basic Library Configuration

```toml
[package]
name = "my-library"
version = "0.1.0"
edition = "2021"
authors = ["Your Name <you@example.com>"]
license = "MIT OR Apache-2.0"
description = "A brief description of what this library does"
documentation = "https://docs.rs/my-library"
homepage = "https://github.com/user/my-library"
repository = "https://github.com/user/my-library"
readme = "README.md"
keywords = ["keyword1", "keyword2", "keyword3"]
categories = ["category1", "category2"]
rust-version = "1.70.0"  # Minimum supported Rust version (MSRV)

[lib]
name = "my_library"  # Optional: overrides package name
path = "src/lib.rs"  # Default path
crate-type = ["lib"]  # Default for libraries

[dependencies]
# Regular dependencies
serde = "1.0"
# Optional dependencies (for features)
tokio = { version = "1.0", optional = true }

[dev-dependencies]
# Test-only dependencies
criterion = "0.5"
proptest = "1.0"

[features]
# Feature flags
default = ["std"]
std = []
async = ["tokio", "tokio/rt-multi-thread"]
serde = ["dep:serde", "serde/derive"]

[package.metadata.docs.rs]
# Documentation build configuration for docs.rs
all-features = true
rustdoc-args = ["--cfg", "docsrs"]
```

### Dependency Specifications

```toml
[dependencies]
# Version requirements
exact = "=1.2.3"           # Exact version
caret = "^1.2.3"           # Compatible: >=1.2.3 <2.0.0 (default)
tilde = "~1.2.3"           # Compatible: >=1.2.3 <1.3.0
wildcard = "1.*"           # Any 1.x.x version
range = ">=1.2, <1.5"      # Version range

# Git dependencies
my-git-dep = { git = "https://github.com/user/repo" }
my-git-dep-tag = { git = "https://github.com/user/repo", tag = "v1.0" }
my-git-dep-rev = { git = "https://github.com/user/repo", rev = "abc123" }

# Path dependencies (local development)
my-local-crate = { path = "../my-local-crate" }

# Optional dependencies (enabled via features)
optional-dep = { version = "1.0", optional = true }

# Dependency features
serde = { version = "1.0", features = ["derive"], default-features = false }
```

### Library Types

```toml
[lib]
# Library output types
crate-type = ["lib"]           # Rust library (default)
# crate-type = ["dylib"]       # Dynamic library
# crate-type = ["staticlib"]   # Static library
# crate-type = ["cdylib"]      # C-compatible dynamic library
# crate-type = ["rlib"]        # Rust library (explicit)

# For FFI libraries
# crate-type = ["cdylib", "rlib"]  # Both C-compatible and Rust library
```

---

## Crate Structure

### Standard Library Layout

```
my-library/
├── Cargo.toml
├── Cargo.lock          # Commit for binaries, gitignore for libraries
├── README.md
├── LICENSE-MIT
├── LICENSE-APACHE
├── CHANGELOG.md
├── src/
│   ├── lib.rs          # Library root
│   ├── prelude.rs      # Common imports (optional)
│   ├── error.rs        # Error types
│   ├── config.rs       # Configuration
│   ├── module1.rs      # Top-level module
│   ├── module2/        # Module with submodules
│   │   ├── mod.rs      # Module root
│   │   ├── sub1.rs
│   │   └── sub2.rs
│   └── internal/       # Private internals
│       ├── mod.rs
│       └── helper.rs
├── examples/           # Usage examples
│   ├── basic.rs
│   └── advanced.rs
├── tests/              # Integration tests
│   ├── integration_test.rs
│   └── common/         # Test utilities
│       └── mod.rs
├── benches/            # Benchmarks
│   └── benchmark.rs
└── docs/               # Additional documentation
    └── architecture.md
```

### lib.rs - Library Root

```rust
//! # My Library
//!
//! This is the top-level documentation for the library.
//! It appears on the crate's main documentation page.
//!
//! ## Quick Start
//!
//! ```
//! use my_library::Something;
//!
//! let thing = Something::new();
//! ```

// Deny warnings to catch issues early
#![warn(missing_docs)]
#![warn(missing_debug_implementations)]
#![deny(unsafe_code)]  // If appropriate

// Feature attributes
#![cfg_attr(not(feature = "std"), no_std)]
#![cfg_attr(docsrs, feature(doc_cfg))]

// Public modules
pub mod config;
pub mod error;

// Private internal modules
mod internal;

// Re-exports for convenience
pub use error::{Error, Result};
pub use config::Config;

// Prelude module (optional)
pub mod prelude {
    //! Common imports for users of this library
    pub use crate::{Config, Error, Result};
    pub use crate::something::Something;
}
```

### Module Organization

```rust
// src/module1.rs - Flat module file
//! Module documentation

pub struct PublicStruct {
    pub field: String,
    private_field: u32,
}

impl PublicStruct {
    /// Creates a new instance
    pub fn new(field: String) -> Self {
        Self {
            field,
            private_field: 0,
        }
    }
}

// Private helper
fn internal_helper() -> u32 {
    42
}
```

```rust
// src/module2/mod.rs - Module directory with submodules
//! Module2 documentation

mod sub1;
mod sub2;

// Re-export public items
pub use sub1::PublicType1;
pub use sub2::PublicType2;

// Module-level items
pub struct ModuleStruct;
```

---

## Public API Design

### Visibility and Re-exports

```rust
// src/lib.rs
pub mod high_level {
    //! High-level API

    // Re-export from internal modules
    pub use crate::internal::core::CoreType;
    pub use crate::internal::utils::UtilType;
}

// Internal modules (not in public API)
mod internal {
    pub(crate) mod core {
        // pub(crate) = visible within crate
        pub struct CoreType;
    }

    pub(crate) mod utils {
        pub struct UtilType;
    }
}

// Users access via:
// use my_library::high_level::{CoreType, UtilType};
```

### Prelude Pattern

```rust
// src/prelude.rs
//! The prelude module re-exports commonly used items

pub use crate::error::{Error, Result};
pub use crate::config::Config;
pub use crate::builder::Builder;
pub use crate::traits::{MyTrait, AnotherTrait};

// Users can import with:
// use my_library::prelude::*;
```

### Builder Pattern

```rust
/// Configuration builder for `MyType`
#[derive(Debug, Default)]
pub struct MyTypeBuilder {
    field1: Option<String>,
    field2: Option<u32>,
}

impl MyTypeBuilder {
    /// Creates a new builder
    pub fn new() -> Self {
        Self::default()
    }

    /// Sets field1
    pub fn field1(mut self, value: impl Into<String>) -> Self {
        self.field1 = Some(value.into());
        self
    }

    /// Sets field2
    pub fn field2(mut self, value: u32) -> Self {
        self.field2 = Some(value);
        self
    }

    /// Builds the final type
    pub fn build(self) -> Result<MyType, BuildError> {
        Ok(MyType {
            field1: self.field1.ok_or(BuildError::MissingField1)?,
            field2: self.field2.unwrap_or(42),
        })
    }
}

/// The main type
pub struct MyType {
    field1: String,
    field2: u32,
}

impl MyType {
    /// Creates a builder for this type
    pub fn builder() -> MyTypeBuilder {
        MyTypeBuilder::new()
    }
}

#[derive(Debug, thiserror::Error)]
pub enum BuildError {
    #[error("field1 is required")]
    MissingField1,
}
```

### Type-State Pattern

```rust
use std::marker::PhantomData;
use crate::error::Result;

/// Type states
pub struct Uninitialized;
pub struct Initialized;

/// Connection in different states
pub struct Connection<State = Uninitialized> {
    url: String,
    _state: PhantomData<State>,
}

impl Connection<Uninitialized> {
    /// Creates a new uninitialized connection
    pub fn new(url: impl Into<String>) -> Self {
        Self {
            url: url.into(),
            _state: PhantomData,
        }
    }

    /// Initializes the connection
    pub fn initialize(self) -> Result<Connection<Initialized>> {
        // Perform initialization
        Ok(Connection {
            url: self.url,
            _state: PhantomData,
        })
    }
}

impl Connection<Initialized> {
    /// Send data (only available when initialized)
    pub fn send(&self, data: &[u8]) -> Result<()> {
        // Send implementation
        Ok(())
    }
}
```

---

## Documentation with Rustdoc

### Documentation Comments

```rust
/// Single-line documentation
///
/// Multi-line documentation continues on subsequent lines.
/// Use markdown for formatting.
///
/// # Examples
///
/// ```
/// use my_library::MyType;
///
/// let instance = MyType::new("value");
/// assert_eq!(instance.get(), "value");
/// ```
///
/// # Errors
///
/// Returns `Err` when:
/// - The input is empty
/// - The value is invalid
///
/// # Panics
///
/// Panics if the internal state is corrupted.
///
/// # Safety
///
/// This function is unsafe because...
///
pub struct MyType {
    value: String,
}

//! Inner doc comment for modules
//! Documents the item that contains it (e.g., in lib.rs or mod.rs)

/// Method documentation
impl MyType {
    /// Creates a new instance
    ///
    /// # Arguments
    ///
    /// * `value` - The initial value
    ///
    /// # Examples
    ///
    /// ```
    /// # use my_library::MyType;
    /// let instance = MyType::new("test");
    /// ```
    pub fn new(value: impl Into<String>) -> Self {
        Self {
            value: value.into(),
        }
    }

    /// Gets the value
    #[must_use]
    pub fn get(&self) -> &str {
        &self.value
    }
}
```

### Documentation Attributes

```rust
// Hide from documentation
#[doc(hidden)]
pub struct InternalType;

// Add documentation link
#[doc(alias = "alternative_name")]
pub struct MyType;

// Inline documentation from another item
#[doc(inline)]
pub use internal::PublicType;

// Conditional documentation (for docs.rs)
#[cfg_attr(docsrs, doc(cfg(feature = "async")))]
#[cfg(feature = "async")]
pub mod async_module {
    // Async functionality
}
```

### Code Examples in Docs

```rust
/// Example with hidden setup code
///
/// ```
/// # use my_library::MyType;
/// # fn main() -> Result<(), Box<dyn std::error::Error>> {
/// let instance = MyType::new("value")?;
/// assert_eq!(instance.get(), "value");
/// # Ok(())
/// # }
/// ```
pub fn example() {}

/// No-run example (compiles but doesn't run)
///
/// ```no_run
/// use my_library::connect;
/// let conn = connect("localhost:8080");
/// ```
pub fn no_run_example() {}

/// Ignore example (doesn't compile)
///
/// ```ignore
/// // Pseudo-code
/// let x = something_not_real();
/// ```
pub fn ignore_example() {}

/// Example that should fail
///
/// ```should_panic
/// use my_library::MyType;
/// MyType::new("");  // Panics on empty string
/// ```
pub fn should_panic_example() {}

/// Example with compile_fail
///
/// ```compile_fail
/// use my_library::MyType;
/// let x: i32 = MyType::new("test");  // Type error
/// ```
pub fn compile_fail_example() {}
```

### Module-Level Documentation

```rust
//! # Module Name
//!
//! This module provides...
//!
//! ## Overview
//!
//! Detailed description...
//!
//! ## Examples
//!
//! ```
//! use my_library::module::Type;
//! ```

// Module contents
```

---

## Feature Flags

### Defining Features

```toml
# Cargo.toml
[features]
# Default features (enabled automatically)
default = ["std"]

# Feature flag with no dependencies
std = []

# Feature flag that enables optional dependencies
async = ["tokio", "futures"]

# Feature that enables other features
full = ["std", "async", "serde"]

# Feature that enables dependency features
serde = ["dep:serde", "serde/derive"]

[dependencies]
tokio = { version = "1.0", optional = true }
futures = { version = "0.3", optional = true }
serde = { version = "1.0", optional = true }
```

### Using Features in Code

```rust
// Conditional compilation based on feature
#[cfg(feature = "async")]
pub mod async_module {
    use tokio::runtime::Runtime;

    pub fn async_function() {
        // Async implementation
    }
}

#[cfg(not(feature = "std"))]
use core::fmt;
#[cfg(feature = "std")]
use std::fmt;

// Function available only with feature
#[cfg(feature = "async")]
pub async fn process_async(data: &[u8]) -> Result<()> {
    // Implementation
    Ok(())
}

// Different implementations based on features
#[cfg(feature = "std")]
pub fn allocate() -> Vec<u8> {
    Vec::new()
}

#[cfg(not(feature = "std"))]
pub fn allocate() -> heapless::Vec<u8, 256> {
    heapless::Vec::new()
}
```

### Feature Documentation

```rust
#![cfg_attr(docsrs, feature(doc_cfg))]

/// This type requires the `async` feature
#[cfg(feature = "async")]
#[cfg_attr(docsrs, doc(cfg(feature = "async")))]
pub struct AsyncType;

/// This function requires either `feature1` or `feature2`
#[cfg(any(feature = "feature1", feature = "feature2"))]
#[cfg_attr(docsrs, doc(cfg(any(feature = "feature1", feature = "feature2"))))]
pub fn conditional_function() {}
```

---

## Semantic Versioning

### SemVer Rules

Format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Incompatible API changes
- **MINOR**: Add functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Pre-1.0.0: Different rules apply
- `0.0.x`: Any change can break compatibility
- `0.y.z`: MINOR acts like MAJOR, PATCH acts like MINOR

### What Requires a Major Version Bump

```rust
// Breaking changes (require MAJOR bump):

// 1. Removing public items
pub struct OldType;  // Removed entirely

// 2. Adding trait bounds to public types
pub struct Generic<T>;  // Changed to:
pub struct Generic<T: Clone>;

// 3. Changing function signatures
pub fn process(x: u32) {}  // Changed to:
pub fn process(x: u64) {}

// 4. Changing trait methods
pub trait MyTrait {
    fn method(&self);  // Changed to:
    fn method(&self) -> i32;
}

// 5. Removing or renaming public fields
pub struct Type {
    pub field: String,  // Removed or renamed
}

// 6. Changing error types
pub fn operation() -> Result<(), OldError> {}  // Changed to:
pub fn operation() -> Result<(), NewError> {}
```

### What is Compatible (MINOR version)

```rust
// Compatible changes (MINOR bump):

// 1. Adding new public items
pub struct NewType;
pub fn new_function() {}

// 2. Adding trait implementations
impl Clone for ExistingType {}

// 3. Adding defaulted type parameters
pub struct Type<T = DefaultType>;

// 4. Adding private fields to structs (if not constructable)
pub struct Type {
    existing: String,
    new_private: u32,  // OK if struct is #[non_exhaustive] or has no pub constructor
}

// 5. Making things more public
pub(crate) fn internal() {}  // Changed to:
pub fn internal() {}

// 6. Relaxing trait bounds
pub fn process<T: Clone + Send>(x: T) {}  // Changed to:
pub fn process<T: Clone>(x: T) {}
```

### Preventing Breaking Changes

```rust
// Use #[non_exhaustive] to reserve right to add fields
#[non_exhaustive]
pub struct Config {
    pub field1: String,
    pub field2: u32,
}

// Use builder pattern to avoid breaking changes
impl Config {
    pub fn builder() -> ConfigBuilder {
        ConfigBuilder::default()
    }
}

// Use sealed trait pattern to prevent external implementations
mod sealed {
    pub trait Sealed {}
}

pub trait MyTrait: sealed::Sealed {
    // Methods
}

impl sealed::Sealed for MyType {}
impl MyTrait for MyType {
    // Implementation
}
```

---

## Publishing to crates.io

### Pre-Publication Checklist

```bash
# 1. Verify package builds
cargo build --release

# 2. Run all tests
cargo test --all-features

# 3. Check documentation
cargo doc --no-deps --all-features --open

# 4. Run clippy
cargo clippy --all-features -- -D warnings

# 5. Format code
cargo fmt --check

# 6. Verify package contents
cargo package --list

# 7. Do a dry-run publish
cargo publish --dry-run
```

### Required Files

```
my-library/
├── Cargo.toml       # Must have required metadata
├── README.md        # Shown on crates.io
├── LICENSE-MIT      # or LICENSE-APACHE or LICENSE
├── CHANGELOG.md     # Version history (recommended)
└── src/
    └── lib.rs       # Library code
```

### Cargo.toml Metadata for Publishing

```toml
[package]
name = "my-library"
version = "0.1.0"
edition = "2021"
authors = ["Your Name <email@example.com>"]
license = "MIT OR Apache-2.0"
description = "A short description (max 256 chars)"
documentation = "https://docs.rs/my-library"
homepage = "https://github.com/user/my-library"
repository = "https://github.com/user/my-library"
readme = "README.md"
keywords = ["cli", "tool", "utility"]  # Max 5, each max 20 chars
categories = ["command-line-utilities"]  # From crates.io list
exclude = [
    "tests/fixtures/*",
    ".github/*",
    "*.png",
]

[badges]
# CI badge
github-actions = { repository = "user/repo", workflow = "CI" }
```

### Publishing Workflow

```bash
# 1. Create crates.io account and get API token
# Visit https://crates.io/me

# 2. Login to crates.io
cargo login <your-api-token>

# 3. Publish the crate
cargo publish

# 4. Verify publication
# Visit https://crates.io/crates/my-library
```

### Yanking Versions

```bash
# Yank a published version (prevents new projects from using it)
cargo yank --version 0.1.0

# Unyank a version
cargo yank --vers 0.1.0 --undo
```

### Publishing Updates

```bash
# 1. Update version in Cargo.toml
# 2. Update CHANGELOG.md
# 3. Commit changes
git add Cargo.toml CHANGELOG.md
git commit -m "chore: bump version to 0.2.0"

# 4. Tag release
git tag -a v0.2.0 -m "Release v0.2.0"

# 5. Publish
cargo publish

# 6. Push commits and tags
git push origin main --tags
```

---

## Examples and Tests

### Examples Directory

```rust
// examples/basic.rs
//! Basic usage example

use my_library::MyType;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Simple example showing basic usage
    let instance = MyType::new("example")?;
    println!("Created: {:?}", instance);

    // Show key functionality
    let result = instance.process()?;
    println!("Result: {}", result);

    Ok(())
}
```

```bash
# Run examples
cargo run --example basic
cargo run --example advanced --features async
```

### Integration Tests

```rust
// tests/integration_test.rs
use my_library::MyType;

#[test]
fn test_basic_usage() {
    let instance = MyType::new("test").unwrap();
    assert_eq!(instance.get(), "test");
}

#[test]
#[cfg(feature = "async")]
fn test_async_feature() {
    // Test async functionality
}
```

### Benchmarks

```rust
// benches/benchmark.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion};
use my_library::MyType;

fn benchmark_operation(c: &mut Criterion) {
    c.bench_function("my_operation", |b| {
        let instance = MyType::new("bench");
        b.iter(|| {
            black_box(instance.process())
        });
    });
}

criterion_group!(benches, benchmark_operation);
criterion_main!(benches);
```

```bash
# Run benchmarks
cargo bench
```

---

## Error Handling

### Library Error Types

```rust
use std::fmt;

/// Library error type
#[derive(Debug)]
pub enum Error {
    /// IO error occurred
    Io(std::io::Error),
    /// Invalid input
    InvalidInput(String),
    /// Configuration error
    Config(ConfigError),
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::Io(e) => write!(f, "IO error: {}", e),
            Error::InvalidInput(msg) => write!(f, "Invalid input: {}", msg),
            Error::Config(e) => write!(f, "Config error: {}", e),
        }
    }
}

impl std::error::Error for Error {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            Error::Io(e) => Some(e),
            Error::Config(e) => Some(e),
            _ => None,
        }
    }
}

// Conversions from other error types
impl From<std::io::Error> for Error {
    fn from(err: std::io::Error) -> Self {
        Error::Io(err)
    }
}

impl From<ConfigError> for Error {
    fn from(err: ConfigError) -> Self {
        Error::Config(err)
    }
}

/// Result type alias for convenience
pub type Result<T> = std::result::Result<T, Error>;

#[derive(Debug)]
pub struct ConfigError {
    message: String,
}

impl fmt::Display for ConfigError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.message)
    }
}

impl std::error::Error for ConfigError {}
```

### Using thiserror

```rust
// Add to Cargo.toml:
// thiserror = "1.0"

use thiserror::Error;

#[derive(Error, Debug)]
pub enum Error {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("Invalid input: {0}")]
    InvalidInput(String),

    #[error("Configuration error")]
    Config(#[from] ConfigError),

    #[error("Not found: {0}")]
    NotFound(String),
}

pub type Result<T> = std::result::Result<T, Error>;
```

---

## Troubleshooting

### Documentation Build Failures

**Problem**: Broken doc links

```rust
// Error: unresolved link to `NonExistent`
/// See [`NonExistent`] for details

// Fix: Use correct paths
/// See [`crate::actual::Type`] for details
/// Or: See [Type](crate::actual::Type)
```

**Problem**: Doc tests fail

```bash
# Run doc tests to see failures
cargo test --doc

# Fix: Add necessary imports to doc examples
/// ```
/// # use my_library::MyType;  # Hidden line
/// let x = MyType::new();
/// ```
```

### Publishing Failures

**Problem**: Version already published

```bash
# Error: crate version `0.1.0` is already uploaded
# Fix: Bump version in Cargo.toml
```

**Problem**: Missing required fields

```toml
# Error: missing required field `description`
# Fix: Add to Cargo.toml
description = "A library that does X"
license = "MIT OR Apache-2.0"
```

**Problem**: Package too large

```toml
# Error: package size exceeds 10 MB limit
# Fix: Exclude unnecessary files
exclude = [
    "tests/fixtures/*.bin",
    "docs/images/*.png",
    ".github/",
]
```

---

## Best Practices

### API Design

1. **Prefer explicit over implicit**
   - Clear function names
   - Explicit error types
   - Documented behavior

2. **Use builders for complex construction**
   - Many optional parameters → builder pattern
   - Complex validation → builder with `build()` method

3. **Provide type safety**
   - Use type-state pattern where applicable
   - Leverage the type system to prevent invalid states

4. **Follow naming conventions**
   - `new()` for constructors
   - `with_*` for builders
   - `into_*` for consuming conversions
   - `as_*` for cheap references
   - `to_*` for expensive conversions

### Versioning

1. **Follow SemVer strictly**
2. **Maintain a CHANGELOG.md**
3. **Use `#[non_exhaustive]` for extensible types**
4. **Document MSRV (Minimum Supported Rust Version)**

### Documentation

1. **Document all public items**
2. **Include examples in documentation**
3. **Use doc tests to verify examples**
4. **Add crate-level documentation in lib.rs**

### Testing

1. **Test public API in integration tests**
2. **Provide examples for common use cases**
3. **Use doc tests for simple examples**
4. **Benchmark performance-critical code**

---

## References

- [The Cargo Book](https://doc.rust-lang.org/cargo/)
- [API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [The Rustdoc Book](https://doc.rust-lang.org/rustdoc/)
- [crates.io Publishing Guide](https://doc.rust-lang.org/cargo/reference/publishing.html)
- [Semantic Versioning](https://semver.org/)

---

## See Also

- `lang-rust-dev` - Rust fundamentals and syntax
- `lang-rust-bin-dev` - Binary application development
- `lang-rust-testing-dev` - Testing strategies
