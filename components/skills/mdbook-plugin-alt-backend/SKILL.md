---
name: mdbook-plugin-alt-backend
description: Developing custom MDBook alternative backend (renderer) plugins in Rust. Use this skill when the user asks to 'create an mdbook backend', 'build an mdbook renderer', 'develop mdbook-<foo> renderer', or 'scaffold an alt-backend'.
---

# MDBook Alternative Backend Plugin Development

## Overview

Guide for developing custom MDBook alternative backend (renderer) plugins in Rust.

**This skill covers:**
- Planning plugin requirements with the user
- Skeleton project setup and templating
- RenderContext handling and output generation
- Test-driven development workflow
- Documentation (ADR, data flow, schema, I/O, examples, user stories)
- Finding existing backends that may already solve the problem
- Creating GitHub repos in `arustydev/*` namespace
- Configuration and `book.toml` integration

**This skill does NOT cover:**
- Preprocessors (see `mdbook-plugin-preprocessor` skill)
- Using existing backends (configuring, not building)
- Writing book content
- General Rust development patterns

## Prerequisites

- Rust toolchain installed (`rustup`)
- MDBook installed (`cargo install mdbook`)
- GitHub CLI (`gh`) for repo creation
- Familiarity with Rust and Cargo

## Workflow

### Step 1: Discover Existing Backends

Before building, check if a backend already exists.

```bash
# Search GitHub for existing backends
gh search repos mdbook-<keyword> --limit 20

# Check crates.io
cargo search mdbook-<keyword>

# Browse the wiki
open "https://github.com/rust-lang/mdBook/wiki/Third-party-plugins"
```

**Existing backends include:**
- [mdbook-epub](https://github.com/Michael-F-Bryan/mdbook-epub) - EPUB generator
- [mdbook-pdf](https://github.com/HollowMan6/mdbook-pdf) - PDF via Chrome
- [mdbook-typst](https://github.com/LegNeato/mdbook-typst) - PDF/PNG/SVG via Typst
- [mdbook-pandoc](https://github.com/max-heller/mdbook-pandoc) - Multiple formats via Pandoc
- [mdbook-man](https://github.com/vv9k/mdbook-man) - Man pages
- [mdbook-texi](https://git.sr.ht/~pem/mdbook-texi) - Texinfo format

If existing backend covers your use case, adopt it instead.

### Step 2: Plan Plugin Functionality

Gather requirements before writing code.

#### 2.1 Define the Problem

Ask these questions:
1. What output format is needed?
2. What features of the book should be preserved?
3. What styling/theming options are needed?
4. What external tools (if any) are required?

#### 2.2 Document with ADR

Create an Architecture Decision Record:

```markdown
# ADR-001: <Backend Name> Design

## Status
Proposed

## Context
<Why is this backend needed? What format does it produce?>

## Decision
<How will it transform the book? What libraries/tools will it use?>

## Consequences
<Trade-offs: performance, dependencies, format limitations>
```

#### 2.3 Map Data Flow (Mermaid)

```mermaid
flowchart LR
    A[book.toml] --> B[mdbook build]
    B --> C[Load Book]
    C --> D[Run Preprocessors]
    D --> E[RenderContext JSON]
    E --> F[mdbook-foo stdin]
    F --> G[Process Chapters]
    G --> H[Generate Output]
    H --> I[Write to destination/]
```

#### 2.4 Define Input/Output Schema

**Input** (received via stdin as JSON):
```rust
// RenderContext structure
pub struct RenderContext {
    /// Version of mdbook that invoked this backend
    pub version: String,
    /// The book's root directory
    pub root: PathBuf,
    /// The book structure with all chapters
    pub book: Book,
    /// Configuration from book.toml
    pub config: Config,
    /// Where to write output files
    pub destination: PathBuf,
}
```

**Output**: Files written to `destination` directory in your target format.

#### 2.5 Write User Stories

```markdown
## User Stories

### US-001: Basic Rendering
As a book author,
I want to run `mdbook build` and get <format> output,
So that I can distribute my book in <format>.

### US-002: Configuration
As a book author,
I want to configure output options in `book.toml`,
So that I can customize the generated output.

### US-003: Error Handling
As a book author,
I want clear error messages when rendering fails,
So that I can diagnose and fix issues.
```

### Step 3: Create GitHub Repository

```bash
# Create repo with standard naming
gh repo create arustydev/mdbook-<foo> \
  --public \
  --description "MDBook backend for <format> output" \
  --clone

cd mdbook-<foo>

# Initialize Rust project
cargo init --name mdbook-<foo>

# Apply standard templates
just apply-gist lang_rust type=bin
just apply-gist github_labels_rust
just apply-gist common
```

### Step 4: Set Up Project Structure

```
mdbook-<foo>/
├── Cargo.toml
├── src/
│   ├── main.rs          # CLI entry point
│   └── lib.rs           # Rendering logic
├── templates/           # Output templates (if needed)
├── tests/
│   ├── integration.rs   # Integration tests
│   └── fixtures/        # Test book fixtures
├── docs/
│   ├── adr/             # Architecture decisions
│   └── book.toml        # Example configuration
├── .github/
│   └── workflows/
│       └── ci.yml       # CI/CD pipeline
└── README.md
```

### Step 5: Configure Cargo.toml

```toml
[package]
name = "mdbook-<foo>"
version = "0.1.0"
edition = "2021"
description = "MDBook backend for <format> output"
license = "MIT"
repository = "https://github.com/arustydev/mdbook-<foo>"
keywords = ["mdbook", "backend", "renderer"]
categories = ["command-line-utilities", "text-processing"]

[dependencies]
mdbook-renderer = "0.2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
anyhow = "1"
log = "0.4"
env_logger = "0.11"
semver = "1"               # For version compatibility checks

[dev-dependencies]
pretty_assertions = "1"
tempfile = "3"
```

### Step 6: Implement with TDD

#### 6.1 Write Failing Test First

```rust
// tests/integration.rs
use mdbook_foo::render_book;
use tempfile::TempDir;

#[test]
fn test_basic_render() {
    let book_json = include_str!("fixtures/simple-book.json");
    let ctx: RenderContext = serde_json::from_str(book_json).unwrap();

    let output_dir = TempDir::new().unwrap();
    let result = render_book(&ctx, output_dir.path());

    assert!(result.is_ok());
    assert!(output_dir.path().join("output.foo").exists());
}

#[test]
fn test_empty_book() {
    // Test handling of books with no chapters
}

#[test]
fn test_configuration_options() {
    // Test custom configuration from book.toml
}
```

#### 6.2 Implement RenderContext Handling

```rust
// src/lib.rs
use mdbook_renderer::RenderContext;
use anyhow::Result;
use std::path::Path;
use std::fs;

/// Backend configuration from book.toml
#[derive(Debug, Default, serde::Deserialize)]
#[serde(default, rename_all = "kebab-case")]
pub struct FooConfig {
    pub output_file: Option<String>,
    pub option1: bool,
    pub option2: String,
}

pub fn render_book(ctx: &RenderContext, destination: &Path) -> Result<()> {
    // Check version compatibility
    check_version(&ctx.version)?;

    // Get backend config
    let config: FooConfig = ctx.config
        .get_deserialized_opt("output.foo")?
        .unwrap_or_default();

    // Ensure destination exists
    fs::create_dir_all(destination)?;

    // Process each chapter
    for item in ctx.book.iter() {
        if let BookItem::Chapter(chapter) = item {
            process_chapter(chapter, &config, destination)?;
        }
    }

    Ok(())
}

fn check_version(version: &str) -> Result<()> {
    let version = semver::Version::parse(version)?;
    let min_version = semver::Version::new(0, 4, 0);

    if version < min_version {
        log::warn!(
            "mdbook version {} may not be compatible (minimum: {})",
            version,
            min_version
        );
    }
    Ok(())
}

fn process_chapter(
    chapter: &Chapter,
    config: &FooConfig,
    destination: &Path,
) -> Result<()> {
    // Transform chapter content to target format
    let output = transform_content(&chapter.content, config)?;

    // Write to destination
    let output_path = destination.join(format!("{}.foo", chapter.name));
    fs::write(output_path, output)?;

    Ok(())
}

fn transform_content(content: &str, config: &FooConfig) -> Result<String> {
    // TODO: Implement content transformation
    Ok(content.to_string())
}
```

#### 6.3 Implement CLI Entry Point

```rust
// src/main.rs
use mdbook_renderer::RenderContext;
use mdbook_foo::render_book;
use std::io;
use std::process;

fn main() {
    env_logger::init();

    // Read RenderContext from stdin
    let mut stdin = io::stdin();
    let ctx = match RenderContext::from_json(&mut stdin) {
        Ok(ctx) => ctx,
        Err(e) => {
            eprintln!("Error parsing RenderContext: {}", e);
            process::exit(1);
        }
    };

    // Render the book
    if let Err(e) = render_book(&ctx, &ctx.destination) {
        eprintln!("Error rendering book: {}", e);
        process::exit(1);
    }
}
```

#### 6.4 Run Tests and Iterate

```bash
# Run tests (expect failures initially)
cargo test

# Implement until tests pass
cargo test -- --nocapture

# Check with clippy
cargo clippy -- -D warnings

# Format code
cargo fmt
```

### Step 7: Test with Real Book

Create a test book:

```bash
mkdir -p tests/fixtures/test-book/src
cat > tests/fixtures/test-book/book.toml << 'EOF'
[book]
title = "Test Book"

[output.foo]
output-file = "book.foo"
option1 = true
EOF

cat > tests/fixtures/test-book/src/SUMMARY.md << 'EOF'
# Summary

- [Chapter 1](chapter1.md)
EOF

cat > tests/fixtures/test-book/src/chapter1.md << 'EOF'
# Chapter 1

Test content for backend rendering.
EOF
```

Test manually:

```bash
# Build and install locally
cargo install --path .

# Test with book
cd tests/fixtures/test-book
mdbook build
ls book/foo/  # Check output directory
```

### Step 8: Document Configuration

Add to README.md:

```markdown
## Installation

```bash
cargo install mdbook-<foo>
```

## Configuration

Add to your `book.toml`:

```toml
[output.foo]
output-file = "book.foo"
option1 = true
option2 = "value"
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `output-file` | string | `"output.foo"` | Output filename |
| `option1` | bool | `false` | Enable feature 1 |
| `option2` | string | `""` | Configuration value |

### Disabling HTML Output

By default, if you add a custom backend, the HTML backend is disabled.
To keep HTML output alongside your backend:

```toml
[output.html]

[output.foo]
```
```

### Step 9: Set Up CI/CD

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo test
      - run: cargo clippy -- -D warnings
      - run: cargo fmt --check

  integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo install mdbook
      - run: cargo install --path .
      - run: cd tests/fixtures/test-book && mdbook build
      - name: Verify output
        run: test -d tests/fixtures/test-book/book/foo
```

## Examples

### Example: Simple Text Output

```rust
fn transform_content(content: &str, _config: &FooConfig) -> Result<String> {
    // Strip markdown, output plain text
    Ok(content.lines()
        .filter(|l| !l.starts_with('#'))
        .collect::<Vec<_>>()
        .join("\n"))
}
```

### Example: JSON Output

```rust
use serde::Serialize;

#[derive(Serialize)]
struct ChapterOutput {
    name: String,
    content: String,
    word_count: usize,
}

fn transform_chapter(chapter: &Chapter) -> Result<String> {
    let output = ChapterOutput {
        name: chapter.name.clone(),
        content: chapter.content.clone(),
        word_count: chapter.content.split_whitespace().count(),
    };
    Ok(serde_json::to_string_pretty(&output)?)
}
```

### Example: Template-Based Output

```rust
use handlebars::Handlebars;

fn render_with_template(chapter: &Chapter, template: &str) -> Result<String> {
    let mut handlebars = Handlebars::new();
    handlebars.register_template_string("chapter", template)?;

    let data = serde_json::json!({
        "title": chapter.name,
        "content": chapter.content,
    });

    Ok(handlebars.render("chapter", &data)?)
}
```

## Troubleshooting

### Backend not running

Check `book.toml` has `[output.foo]` section and binary is in PATH.

### JSON parse errors

Ensure stdin handling is correct. Debug with:

```bash
RUST_LOG=debug mdbook build 2>&1 | head -100
```

### Output directory issues

Always use `fs::create_dir_all()` before writing:

```rust
fs::create_dir_all(&ctx.destination)?;
```

### HTML output missing

When custom backends are configured, HTML is disabled by default. Add `[output.html]` to keep it:

```toml
[output.html]

[output.foo]
```

## Key Differences from Preprocessors

| Aspect | Preprocessor | Backend |
|--------|--------------|---------|
| Purpose | Modify book content | Generate output format |
| Config | `[preprocessor.foo]` | `[output.foo]` |
| Input | `[PreprocessorContext, Book]` | `RenderContext` |
| Output | Modified `Book` JSON | Files to destination |
| Crate | `mdbook-preprocessor` | `mdbook-renderer` |

## References

- [MDBook Backend Docs](https://rust-lang.github.io/mdBook/for_developers/backends.html)
- [mdbook-renderer crate](https://docs.rs/mdbook-renderer)
- [Third-party Plugins Wiki](https://github.com/rust-lang/mdBook/wiki/Third-party-plugins)
- [Example: mdbook-epub](https://github.com/Michael-F-Bryan/mdbook-epub)
- [Example: mdbook-typst](https://github.com/LegNeato/mdbook-typst)
