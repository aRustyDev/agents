---
name: lang-rust-library-dev
description: Rust-specific library development patterns. Use when creating Rust crates, designing public APIs with ownership semantics, configuring Cargo.toml, managing feature flags, publishing to crates.io, or writing rustdoc. Extends meta-library-dev with Rust tooling and idioms.
---

# Rust Library Development

Rust-specific patterns for library (crate) development. This skill extends `meta-library-dev` with Rust tooling, ownership idioms, and ecosystem practices.

## This Skill Extends

- `meta-library-dev` - Foundational library patterns (API design, versioning, testing strategies)

For general concepts like semantic versioning, module organization principles, and testing pyramids, see the meta-skill first.

## This Skill Adds

- **Rust tooling**: Cargo.toml, feature flags, workspaces, rustdoc
- **Rust idioms**: Ownership in public APIs, borrowing patterns, trait design
- **Rust ecosystem**: crates.io, docs.rs, MSRV policy, common dependencies

## This Skill Does NOT Cover

- General library patterns - see `meta-library-dev`
- Error handling details - see `lang-rust-errors-dev`
- Documentation patterns - see `lang-rust-docs-dev`
- Cargo dependencies - see `lang-rust-cargo-dev`
- CLI development - see `lang-rust-cli-dev`

---

## Quick Reference

| Task | Command/Pattern |
|------|-----------------|
| New library crate | `cargo new --lib <name>` |
| Build | `cargo build` |
| Test | `cargo test` |
| Doc | `cargo doc --no-deps --open` |
| Publish (dry run) | `cargo publish --dry-run` |
| Publish | `cargo publish` |
| Check MSRV | `cargo msrv` (requires cargo-msrv) |
| Lint | `cargo clippy -- -D warnings` |
| Format | `cargo fmt` |

---

## Cargo.toml Structure

### Required Fields for Publishing

```toml
[package]
name = "my-crate"
version = "0.1.0"
edition = "2021"
rust-version = "1.70"  # MSRV

# Required for crates.io
license = "MIT OR Apache-2.0"
description = "A brief description of what this crate does"
repository = "https://github.com/username/repo"

# Recommended
documentation = "https://docs.rs/my-crate"
readme = "README.md"
keywords = ["keyword1", "keyword2"]  # Max 5
categories = ["category"]  # From crates.io list

[lib]
name = "my_crate"
path = "src/lib.rs"
```

### Metadata Best Practices

```toml
[package.metadata.docs.rs]
all-features = true
rustdoc-args = ["--cfg", "docsrs"]

[badges]
maintenance = { status = "actively-developed" }
```

---

## Feature Flags

### Design Principles

1. **Default features should be minimal** - Enable broad compatibility
2. **Additive only** - Features should never remove functionality
3. **Document all features** - In Cargo.toml and README
4. **Test all combinations** - CI should test feature matrix

### Common Patterns

```toml
[features]
default = []

# Serialization (opt-in)
serde = ["dep:serde", "dep:serde_json"]

# Async runtime support
tokio = ["dep:tokio"]
async-std = ["dep:async-std"]

# Performance features
simd = []

# Development/debugging
tracing = ["dep:tracing"]

# Full feature set for docs.rs
full = ["serde", "tokio", "tracing"]
```

### Feature-Gated Code

```rust
#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone)]
#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
pub struct Config {
    pub name: String,
    pub value: i32,
}
```

### Feature Documentation

```rust
//! # Feature Flags
//!
//! - `serde` - Enable serialization support
//! - `tokio` - Enable async support with Tokio runtime
//! - `tracing` - Enable tracing instrumentation
```

---

## Public API Design (Rust-Specific)

### Ownership Patterns

**Prefer borrowing over ownership for inputs:**
```rust
// Good: Borrows input
pub fn process(data: &str) -> Result<Output, Error>

// Avoid: Takes ownership unnecessarily
pub fn process(data: String) -> Result<Output, Error>
```

**Use `impl Trait` for flexible inputs:**
```rust
// Good: Accepts &str, String, Cow<str>, etc.
pub fn process(data: impl AsRef<str>) -> Result<Output, Error>

// Good: Accepts any iterator
pub fn from_iter(items: impl IntoIterator<Item = Item>) -> Self
```

**Return owned data when caller needs ownership:**
```rust
// Good: Caller gets owned data
pub fn generate() -> String

// Good: Zero-cost abstraction for optional allocation
pub fn get_name(&self) -> Cow<'_, str>
```

### Type Design

**Newtypes for type safety:**
```rust
/// User ID (cannot be confused with other integer IDs)
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct UserId(u64);

impl UserId {
    pub fn new(id: u64) -> Self {
        Self(id)
    }

    pub fn as_u64(self) -> u64 {
        self.0
    }
}
```

**Builder pattern for complex construction:**
```rust
#[derive(Debug, Clone)]
pub struct Config {
    timeout: Duration,
    retries: u32,
    strict: bool,
}

#[derive(Debug, Default)]
pub struct ConfigBuilder {
    timeout: Option<Duration>,
    retries: Option<u32>,
    strict: Option<bool>,
}

impl ConfigBuilder {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn timeout(mut self, timeout: Duration) -> Self {
        self.timeout = Some(timeout);
        self
    }

    pub fn retries(mut self, retries: u32) -> Self {
        self.retries = Some(retries);
        self
    }

    pub fn strict(mut self, strict: bool) -> Self {
        self.strict = Some(strict);
        self
    }

    pub fn build(self) -> Config {
        Config {
            timeout: self.timeout.unwrap_or(Duration::from_secs(30)),
            retries: self.retries.unwrap_or(3),
            strict: self.strict.unwrap_or(false),
        }
    }
}
```

### Trait Design

**Traits for extensibility:**
```rust
/// Trait for custom parsers
pub trait Parser {
    type Output;
    type Error;

    fn parse(&self, input: &str) -> Result<Self::Output, Self::Error>;
}

/// Provide a default implementation
pub struct DefaultParser;

impl Parser for DefaultParser {
    type Output = Document;
    type Error = ParseError;

    fn parse(&self, input: &str) -> Result<Self::Output, Self::Error> {
        // ...
    }
}
```

**Extension traits for foreign types:**
```rust
pub trait StringExt {
    fn to_snake_case(&self) -> String;
    fn to_camel_case(&self) -> String;
}

impl StringExt for str {
    fn to_snake_case(&self) -> String {
        // ...
    }

    fn to_camel_case(&self) -> String {
        // ...
    }
}
```

---

## Module Organization

### Standard Crate Structure

```
my-crate/
├── Cargo.toml
├── README.md
├── LICENSE-MIT
├── LICENSE-APACHE
├── src/
│   ├── lib.rs          # Public API, re-exports
│   ├── error.rs        # Error types
│   ├── types.rs        # Core types
│   ├── parser.rs       # Parser implementation
│   └── internal/       # Private modules
│       └── mod.rs
├── tests/              # Integration tests
│   └── integration.rs
├── examples/           # Usage examples
│   └── basic.rs
└── benches/            # Benchmarks
    └── parsing.rs
```

### lib.rs Organization

```rust
//! # My Crate
//!
//! Brief description of the crate.
//!
//! ## Quick Start
//!
//! ```rust
//! use my_crate::parse;
//!
//! let result = parse("input")?;
//! # Ok::<(), my_crate::Error>(())
//! ```

// Re-export public API
pub use self::error::{Error, Result};
pub use self::parser::parse;
pub use self::types::{Config, Document};

// Public modules (if users need access)
pub mod types;

// Private modules
mod error;
mod parser;
mod internal;

// Feature-gated re-exports
#[cfg(feature = "serde")]
pub use self::types::SerializableDocument;
```

### Visibility Patterns

```rust
// Public - part of API
pub fn public_function() {}

// Crate-public - visible within crate only
pub(crate) fn internal_function() {}

// Module-public - visible to parent module
pub(super) fn parent_visible() {}

// Private - visible only in current module
fn private_function() {}
```

---

## Testing Patterns

### Unit Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_valid_input() {
        let result = parse("valid input").unwrap();
        assert_eq!(result.value, "expected");
    }

    #[test]
    fn parse_invalid_input() {
        let result = parse("invalid");
        assert!(matches!(result, Err(Error::InvalidSyntax { .. })));
    }
}
```

### Doc Tests

```rust
/// Parses the input string.
///
/// # Examples
///
/// ```
/// use my_crate::parse;
///
/// let result = parse("hello")?;
/// assert_eq!(result.len(), 5);
/// # Ok::<(), my_crate::Error>(())
/// ```
///
/// Error case:
///
/// ```
/// use my_crate::parse;
///
/// let result = parse("");
/// assert!(result.is_err());
/// ```
pub fn parse(input: &str) -> Result<Output, Error> {
    // ...
}
```

### Integration Tests

```rust
// tests/integration.rs
use my_crate::{parse, Config};

#[test]
fn end_to_end_parsing() {
    let config = Config::builder()
        .strict(true)
        .build();

    let result = parse_with_config("input", &config).unwrap();
    assert!(result.is_valid());
}
```

### Property-Based Testing

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn parse_never_panics(s in "\\PC*") {
        let _ = parse(&s);
    }

    #[test]
    fn roundtrip(input in valid_input_strategy()) {
        let parsed = parse(&input).unwrap();
        let serialized = serialize(&parsed);
        assert_eq!(input, serialized);
    }
}
```

---

## MSRV (Minimum Supported Rust Version)

### Policy Guidelines

| Crate Type | Recommended MSRV Policy |
|------------|------------------------|
| Widely-used utility | N-2 stable (conservative) |
| Application-specific | Latest stable |
| Async libraries | Match async runtime MSRV |

### Configuration

```toml
# Cargo.toml
[package]
rust-version = "1.70"
```

### CI Verification

```yaml
# .github/workflows/ci.yml
jobs:
  msrv:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@1.70  # MSRV
      - run: cargo check --all-features
```

---

## Publishing to crates.io

### Pre-publish Checklist

- [ ] `cargo fmt --check` passes
- [ ] `cargo clippy -- -D warnings` passes
- [ ] `cargo test --all-features` passes
- [ ] `cargo doc --no-deps --all-features` succeeds
- [ ] Version bumped in Cargo.toml
- [ ] CHANGELOG.md updated
- [ ] README.md is current
- [ ] All required Cargo.toml fields present
- [ ] Correct license files included
- [ ] `cargo publish --dry-run` succeeds

### Publishing Commands

```bash
# Verify everything is ready
cargo publish --dry-run

# Publish to crates.io
cargo publish

# For workspace members
cargo publish -p my-crate
```

### Yanking Versions

```bash
# Yank a bad version (prevents new installs)
cargo yank --version 1.0.1

# Undo yank
cargo yank --undo --version 1.0.1
```

---

## Common Dependencies

### Serialization

```toml
[dependencies]
serde = { version = "1", features = ["derive"], optional = true }
serde_json = { version = "1", optional = true }
```

### Error Handling

```toml
[dependencies]
thiserror = "1"  # For library error types
# OR
error-stack = "0.5"  # For rich error context
```

### Async

```toml
[dependencies]
tokio = { version = "1", features = ["rt", "macros"], optional = true }
async-trait = { version = "0.1", optional = true }
futures = { version = "0.3", optional = true }
```

### Logging/Tracing

```toml
[dependencies]
tracing = { version = "0.1", optional = true }
log = { version = "0.4", optional = true }
```

---

## docs.rs Configuration

### Enable All Features

```toml
[package.metadata.docs.rs]
all-features = true
rustdoc-args = ["--cfg", "docsrs"]
```

### Feature Badges in Docs

```rust
#![cfg_attr(docsrs, feature(doc_cfg))]

#[cfg(feature = "serde")]
#[cfg_attr(docsrs, doc(cfg(feature = "serde")))]
pub fn serialize<T: Serialize>(value: &T) -> String {
    // ...
}
```

---

## Workspace Patterns

### Multi-Crate Workspace

```toml
# Root Cargo.toml
[workspace]
resolver = "2"
members = [
    "crates/core",
    "crates/derive",
    "crates/utils",
]

[workspace.package]
version = "0.1.0"
edition = "2021"
license = "MIT OR Apache-2.0"
repository = "https://github.com/username/repo"

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["rt-multi-thread"] }
```

### Workspace Member

```toml
# crates/core/Cargo.toml
[package]
name = "my-crate-core"
version.workspace = true
edition.workspace = true
license.workspace = true

[dependencies]
serde = { workspace = true, optional = true }
```

---

## Anti-Patterns

### 1. Exposing Internal Types

```rust
// Bad: Exposes implementation detail
pub fn get_data() -> HashMap<String, Vec<InternalType>>

// Good: Return domain type
pub fn get_data() -> DataCollection
```

### 2. Breaking Semver

```rust
// v1.0.0
pub fn process(input: &str) -> Result<Output, Error>

// v1.1.0 - WRONG! This is breaking
pub fn process(input: &str, options: Options) -> Result<Output, Error>

// v1.1.0 - Correct: Add new function
pub fn process(input: &str) -> Result<Output, Error>
pub fn process_with_options(input: &str, options: Options) -> Result<Output, Error>
```

### 3. Missing `#[must_use]`

```rust
// Bad: Easy to ignore error
pub fn validate(input: &str) -> bool

// Good: Compiler warns if ignored
#[must_use = "validation result should be checked"]
pub fn validate(input: &str) -> bool
```

### 4. Non-Exhaustive Enums

```rust
// Good: Allow adding variants without breaking
#[non_exhaustive]
pub enum Error {
    NotFound,
    InvalidInput,
    // Future variants can be added
}
```

---

## References

- `meta-library-dev` - Foundational library patterns
- `lang-rust-errors-dev` - Error handling patterns
- `lang-rust-docs-dev` - Documentation patterns
- `lang-rust-cargo-dev` - Dependency management
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [crates.io](https://crates.io/)
- [docs.rs](https://docs.rs/)
