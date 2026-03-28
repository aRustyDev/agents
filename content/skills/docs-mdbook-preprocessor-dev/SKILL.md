---
name: docs-mdbook-preprocessor-dev
description: Developing custom MDBook preprocessor plugins in Rust. Use this skill when the user asks to 'create an mdbook preprocessor', 'build an mdbook plugin', 'develop mdbook-<foo>', or 'scaffold a new mdbook preprocessor'.
---

# MDBook Preprocessor Plugin Development

## Overview

Guide for developing custom MDBook preprocessor plugins in Rust, following TDD practices.

**This skill covers:**
- Planning plugin functionality with the user
- Skeleton project setup and templating
- Test-driven development workflow
- Documentation (ADR, data flow, schema, I/O, examples, user stories)
- Finding existing plugins that may already solve the problem
- Creating GitHub repos in `arustydev/*` namespace
- Configuration and `book.toml` integration

**This skill does NOT cover:**
- Using existing preprocessors (configuring, not building)
- Writing book content
- MDBook backends/alternative renderers
- General Rust development patterns

## Prerequisites

- Rust toolchain installed (`rustup`)
- MDBook installed (`cargo install mdbook`)
- GitHub CLI (`gh`) for repo creation
- Familiarity with Rust and Cargo

## Workflow

### Step 1: Discover Existing Plugins

Before building, check if a preprocessor already exists.

```bash
# Search GitHub for existing preprocessors
gh search repos mdbook-<keyword> --limit 20

# Check crates.io
cargo search mdbook-<keyword>

# Browse tagged repos
open "https://github.com/topics/mdbook-preprocessor?l=rust"
```

**44+ preprocessors exist** on GitHub. Popular ones include:
- [mdbook-admonish](https://github.com/tommilligan/mdbook-admonish) - Material Design callouts
- [mdbook-i18n](https://github.com/nicholaslusar/mdbook-i18n-helpers) - Translation support
- [mdbook-cmdrun](https://github.com/FauconFan/mdbook-cmdrun) - Execute shell commands
- [mdbook-mermaid](https://github.com/badboy/mdbook-mermaid) - Mermaid diagrams

If existing plugin covers your use case, adopt it instead.

### Step 2: Plan Plugin Functionality

Gather requirements before writing code.

#### 2.1 Define the Problem

Ask these questions:
1. What content transformation is needed?
2. What syntax will users write in their markdown?
3. What output should be generated?
4. Which renderers should be supported? (html, pdf, epub)

#### 2.2 Document with ADR

Create an Architecture Decision Record:

```markdown
# ADR-001: <Preprocessor Name> Design

## Status
Proposed

## Context
<Why is this preprocessor needed?>

## Decision
<How will it work?>

## Consequences
<Trade-offs and implications>
```

#### 2.3 Map Data Flow (Mermaid)

```mermaid
flowchart LR
    A[book.toml] --> B[mdbook build]
    B --> C[Load Book]
    C --> D[PreprocessorContext + Book JSON]
    D --> E[mdbook-foo stdin]
    E --> F[Transform Chapters]
    F --> G[Modified Book JSON]
    G --> H[stdout]
    H --> I[Renderer]
```

#### 2.4 Define Input/Output Schema

**Input** (received via stdin):
```json
[
  {
    "root": "/path/to/book",
    "config": { "book": {...}, "preprocessor": {"foo": {...}} },
    "renderer": "html",
    "mdbook_version": "0.4.40"
  },
  {
    "sections": [
      { "Chapter": { "name": "...", "content": "...", ... } }
    ]
  }
]
```

**Output** (write to stdout):
```json
{
  "sections": [
    { "Chapter": { "name": "...", "content": "<transformed>", ... } }
  ]
}
```

#### 2.5 Write User Stories

```markdown
## User Stories

### US-001: Basic Usage
As a book author,
I want to write `{{#foo bar}}` in my markdown,
So that it renders as <expected output>.

### US-002: Configuration
As a book author,
I want to configure options in `book.toml`,
So that I can customize behavior without changing markdown.

### US-003: Error Handling
As a book author,
I want clear error messages when syntax is invalid,
So that I can fix issues quickly.
```

### Step 3: Create GitHub Repository

```bash
# Create repo with standard naming
gh repo create arustydev/mdbook-<foo> \
  --public \
  --description "MDBook preprocessor for <description>" \
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
│   └── lib.rs           # Preprocessor implementation
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
description = "MDBook preprocessor for <description>"
license = "MIT"
repository = "https://github.com/arustydev/mdbook-<foo>"
keywords = ["mdbook", "preprocessor", "markdown"]
categories = ["command-line-utilities", "text-processing"]

[dependencies]
mdbook-preprocessor = "0.2"
mdbook-markdown = "0.2"      # For markdown parsing
serde = { version = "1", features = ["derive"] }
serde_json = "1"
anyhow = "1"
log = "0.4"
env_logger = "0.11"

[dev-dependencies]
pretty_assertions = "1"
```

### Step 6: Implement with TDD

#### 6.1 Write Failing Test First

```rust
// tests/integration.rs
use mdbook_foo::process_chapter;

#[test]
fn test_basic_transformation() {
    let input = r#"# Chapter
Some text with {{#foo bar}}.
"#;

    let expected = r#"# Chapter
Some text with <transformed content>.
"#;

    let result = process_chapter(input);
    assert_eq!(result, expected);
}

#[test]
fn test_no_transformation_needed() {
    let input = "# Chapter\nPlain markdown.";
    let result = process_chapter(input);
    assert_eq!(result, input);
}
```

#### 6.2 Implement Preprocessor Trait

```rust
// src/lib.rs
use mdbook_preprocessor::prelude::*;
use anyhow::Result;

pub struct FooPreprocessor;

impl Preprocessor for FooPreprocessor {
    fn name(&self) -> &str {
        "foo"
    }

    fn run(&self, ctx: &PreprocessorContext, mut book: Book) -> Result<Book> {
        let config = ctx.config.get_preprocessor(self.name());

        book.for_each_mut(|item| {
            if let BookItem::Chapter(chapter) = item {
                chapter.content = process_chapter(&chapter.content);
            }
        });

        Ok(book)
    }

    fn supports_renderer(&self, renderer: &str) -> bool {
        renderer == "html"
    }
}

pub fn process_chapter(content: &str) -> String {
    // TODO: Implement transformation
    content.to_string()
}
```

#### 6.3 Implement CLI Entry Point

```rust
// src/main.rs
use mdbook_preprocessor::prelude::*;
use mdbook_foo::FooPreprocessor;
use std::io;

fn main() {
    env_logger::init();

    let preprocessor = FooPreprocessor;

    if std::env::args().nth(1).as_deref() == Some("supports") {
        let renderer = std::env::args().nth(2).unwrap_or_default();
        if preprocessor.supports_renderer(&renderer) {
            std::process::exit(0);
        } else {
            std::process::exit(1);
        }
    }

    let (ctx, book) = CmdPreprocessor::parse_input(io::stdin()).unwrap();
    let result = preprocessor.run(&ctx, book).unwrap();
    serde_json::to_writer(io::stdout(), &result).unwrap();
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

[preprocessor.foo]
# Custom configuration here
EOF

cat > tests/fixtures/test-book/src/SUMMARY.md << 'EOF'
# Summary

- [Chapter 1](chapter1.md)
EOF

cat > tests/fixtures/test-book/src/chapter1.md << 'EOF'
# Chapter 1

Test content with {{#foo bar}}.
EOF
```

Test manually:

```bash
# Build and install locally
cargo install --path .

# Test with book
cd tests/fixtures/test-book
mdbook build
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
[preprocessor.foo]
option1 = "value"
option2 = true
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `option1` | string | `""` | Description |
| `option2` | bool | `false` | Description |
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
```

## Examples

### Example: Simple Text Replacement

```rust
pub fn process_chapter(content: &str) -> String {
    content.replace("{{#hello}}", "Hello, World!")
}
```

### Example: Regex-Based Transformation

```rust
use regex::Regex;

pub fn process_chapter(content: &str) -> String {
    let re = Regex::new(r"\{\{#include\s+(\S+)\}\}").unwrap();
    re.replace_all(content, |caps: &regex::Captures| {
        let path = &caps[1];
        format!("<!-- included from {} -->", path)
    }).to_string()
}
```

### Example: Markdown Event Processing

```rust
use mdbook_markdown::{pulldown_cmark::{Event, Parser, Tag}, CMarkWriter};

pub fn process_chapter(content: &str) -> String {
    let parser = Parser::new(content);
    let events: Vec<Event> = parser.map(|event| {
        match event {
            Event::Text(text) => Event::Text(text.to_uppercase().into()),
            other => other,
        }
    }).collect();

    let mut output = String::new();
    CMarkWriter::new(&mut output).write(events.iter()).unwrap();
    output
}
```

## Troubleshooting

### Preprocessor not running

Check `book.toml` has `[preprocessor.foo]` section and binary is in PATH.

### JSON parse errors

Ensure stdin/stdout handling is correct. Use `env_logger` for debugging:

```bash
RUST_LOG=debug mdbook build
```

### Changes not appearing

Clear mdbook cache:

```bash
rm -rf book/
mdbook build
```

## References

- [MDBook Preprocessor Docs](https://rust-lang.github.io/mdBook/for_developers/preprocessors.html)
- [mdbook-preprocessor crate](https://docs.rs/mdbook-preprocessor)
- [GitHub Topic: mdbook-preprocessor](https://github.com/topics/mdbook-preprocessor?l=rust)
- [Example: mdbook-cmdrun](https://github.com/FauconFan/mdbook-cmdrun)
