# ADR Code Traceability

Patterns for referencing ADRs from source code to maintain decision-to-implementation links.

## Language Patterns

### Rust

```rust
//! # Module Name
//!
//! ADR: 003 - Use event sourcing for audit trail

// Inline reference
let pool = create_pool(config); // ADR: 005 - Use connection pooling
```

### Go

```go
// Package store implements data persistence.
//
// ADR: 003 - Use event sourcing for audit trail
package store

// Inline reference
pool := NewPool(config) // ADR: 005 - Use connection pooling
```

### TypeScript

```typescript
/**
 * Data persistence layer.
 * @see ADR: 003 - Use event sourcing for audit trail
 */

// Inline reference
const pool = createPool(config); // ADR: 005 - Use connection pooling
```

### Python

```python
"""
Data persistence layer.

ADR: 003 - Use event sourcing for audit trail
"""

# Inline reference
pool = create_pool(config)  # ADR: 005 - Use connection pooling
```

## Reference Format

```
ADR: <number> - <short title>
```

- Use ADR number, not UUID (numbers are human-readable)
- Include short title for context without looking up the ADR
- Match the ADR's actual title

## Placement Decision Tree

| Question | Yes | No |
|----------|-----|-----|
| Does this module exist because of an ADR? | File header reference | Continue |
| Does this line implement a non-obvious ADR choice? | Inline comment | Continue |
| Is this a standard pattern anyone would write? | No reference needed | — |
| Would a future developer ask "why is it done this way?" | Inline comment | No reference needed |

## When to Add References

| Scenario | Add Reference? | Placement |
|----------|---------------|-----------|
| Module created by ADR | Yes | File header |
| Specific implementation choice from ADR | Yes | Inline |
| Configuration value from ADR | Yes | Inline |
| Standard library usage | No | — |
| Obvious implementation | No | — |
| Test files | Rarely | Only if testing ADR-specific behavior |

## When NOT to Add References

- **Every file in the project** — only files directly implementing an ADR decision
- **Obvious code** — if the approach is standard practice, no reference needed
- **Transient code** — scripts, one-off migrations, throwaway prototypes
- **Comments that will rot** — if the ADR number might change, reference by title only
- **Test utilities** — unless the test specifically validates ADR-mandated behavior

## Searching for ADR References

```bash
# Find all references to a specific ADR
grep -rn "ADR: 003" src/

# Find all ADR references in the codebase
grep -rn "ADR: [0-9]" src/

# Find files with ADR header references
grep -rln "ADR: [0-9]" src/ --include="*.rs" --include="*.go" --include="*.ts" --include="*.py"
```

## Maintaining References

| Event | Action |
|-------|--------|
| ADR superseded | Update references to point to new ADR number |
| ADR deprecated | Remove references (code should no longer depend on it) |
| Code moved | Keep references with the code |
| Code deleted | References removed with it (no action needed) |
