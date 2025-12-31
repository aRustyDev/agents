# 8 Pillars Checklist

Coverage validation for `lang-*-dev` and `convert-*-*` skills.

## The 8 Pillars

| Pillar | Purpose | Detection Patterns |
|--------|---------|-------------------|
| **Module** | Import/export, visibility, namespacing | `import`, `export`, `module`, `use`, `require`, `package` |
| **Error** | Error handling model, exceptions | `Result`, `Exception`, `Error`, `try`, `catch`, `?`, `unwrap` |
| **Concurrency** | Async, parallelism, synchronization | `async`, `await`, `thread`, `channel`, `spawn`, `Actor` |
| **Metaprogramming** | Macros, reflection, code generation | `macro`, `decorator`, `@`, `derive`, `annotation`, `quote` |
| **Zero/Default** | Null handling, default values, optionality | `null`, `None`, `nil`, `Option`, `Maybe`, `default`, `?` |
| **Serialization** | Data encoding/decoding, marshaling | `JSON`, `serde`, `marshal`, `encode`, `decode`, `parse` |
| **Build** | Package management, build systems | `Cargo`, `npm`, `pip`, `mix`, `make`, `package.json`, `deps` |
| **Testing** | Test framework, assertions, mocking | `test`, `describe`, `it`, `assert`, `expect`, `mock`, `#[test]` |

## Scoring Rubric

| Score | Status | Definition |
|-------|--------|------------|
| 1.0 | ✓ Full | Dedicated section with examples and patterns |
| 0.5 | ~ Partial | Mentioned but limited coverage |
| 0.0 | ✗ None | Not addressed |

### Examples by Score

**Full (1.0):**
```markdown
## Error Handling

Rust uses `Result<T, E>` for recoverable errors...

### Pattern: Error Propagation
```rust
fn read_file() -> Result<String, io::Error> {
    let content = fs::read_to_string("file.txt")?;
    Ok(content)
}
```

### Common Conversions
| Python | Rust |
|--------|------|
| `try/except` | `match` on `Result` |
| `raise` | `Err(...)` |
```

**Partial (0.5):**
```markdown
Rust uses `Result` for error handling. See the standard library documentation for details.
```

**None (0.0):**
No mention of error handling patterns.

## Coverage Thresholds

| Score | Status | Interpretation |
|-------|--------|----------------|
| 8/8 | Excellent | Complete coverage |
| 6-7.5/8 | Good | Acceptable, minor gaps |
| 4-5.5/8 | Needs Work | Should improve |
| < 4/8 | Incomplete | Critical gaps |

## Pillar Details

### Module System

**Search terms:** `import`, `export`, `module`, `visibility`, `pub`, `private`, `namespace`, `package`

**Expected content:**
- How to import/export
- Visibility modifiers
- Module organization
- Re-exports

### Error Handling

**Search terms:** `Result`, `Error`, `Exception`, `try`, `catch`, `?`, `unwrap`, `panic`

**Expected content:**
- Error types and patterns
- Propagation mechanisms
- Recovery strategies
- Error conversion

### Concurrency

**Search terms:** `async`, `await`, `thread`, `spawn`, `channel`, `mutex`, `Actor`, `Future`

**Expected content:**
- Async model (if applicable)
- Thread primitives
- Synchronization
- Message passing

### Metaprogramming

**Search terms:** `macro`, `decorator`, `@`, `derive`, `annotation`, `quote`, `unquote`, `AST`

**Expected content:**
- Macro system (if applicable)
- Decorators/attributes
- Code generation
- Compile-time vs runtime

### Zero/Default Values

**Search terms:** `null`, `None`, `nil`, `Option`, `Maybe`, `default`, `?`, `Optional`

**Expected content:**
- Null safety approach
- Optional types
- Default values
- Empty/zero patterns

### Serialization

**Search terms:** `JSON`, `serde`, `marshal`, `encode`, `decode`, `Codable`, `parse`, `stringify`

**Expected content:**
- Serialization libraries
- Format support
- Custom serialization
- Schema validation

### Build System

**Search terms:** `Cargo`, `npm`, `pip`, `mix`, `maven`, `package.json`, `pyproject.toml`

**Expected content:**
- Package manager
- Dependency management
- Build configuration
- Publishing

### Testing

**Search terms:** `test`, `describe`, `it`, `assert`, `expect`, `#[test]`, `pytest`, `mock`

**Expected content:**
- Test framework
- Assertion patterns
- Test organization
- Mocking/fixtures

## Validation Automation

```bash
# Validate pillar coverage for a skill
just validate-pillars lang-rust-dev

# Output:
# Pillar Coverage: lang-rust-dev
# ├── Module:          ✓ (1.0)
# ├── Error:           ✓ (1.0)
# ├── Concurrency:     ~ (0.5)
# ├── Metaprogramming: ✓ (1.0)
# ├── Zero/Default:    ✓ (1.0)
# ├── Serialization:   ✓ (1.0)
# ├── Build:           ✓ (1.0)
# └── Testing:         ✓ (1.0)
# Total: 7.5/8
```

## Validation Checklist

```markdown
## 8 Pillars Validation

| Pillar | Score | Notes |
|--------|-------|-------|
| Module | _/1.0 | |
| Error | _/1.0 | |
| Concurrency | _/1.0 | |
| Metaprogramming | _/1.0 | |
| Zero/Default | _/1.0 | |
| Serialization | _/1.0 | |
| Build | _/1.0 | |
| Testing | _/1.0 | |
| **Total** | **_/8** | |

### Status
- [ ] Score >= 6/8 (acceptable)
- [ ] All pillars at least mentioned (0.5+)
- [ ] Critical pillars full (Module, Error, Build)
```

## Gap Mitigation

When a pillar cannot be fully covered:

1. **Acknowledge the gap** - Explain why (e.g., language doesn't have feature)
2. **Provide alternative** - How is the concept addressed differently
3. **Cross-reference** - Link to language documentation

```markdown
## Metaprogramming

Go does not have macros. Code generation is handled via:
- `go generate` directives
- Text templates (`text/template`)
- External tools (e.g., `stringer`)

> **See also:** [Go Generate](https://go.dev/blog/generate)
```
