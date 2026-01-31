# Conversion Forms & Templates

Templates, checklists, and decision trees for language conversion projects.

---

## Type Mapping Template

Use this template when planning a conversion. Fill in all rows before starting transformation.

```markdown
## Type Mapping: <Source> → <Target>

### Primitive Types

| <Source> | <Target> | Notes |
|----------|----------|-------|
| `string` | | |
| `number` / `int` | | |
| `float` / `double` | | |
| `boolean` / `bool` | | |
| `null` / `nil` / `None` | | |
| `undefined` | | |
| `void` / `unit` | | |

### Composite Types

| <Source> | <Target> | Notes |
|----------|----------|-------|
| `Array<T>` / `list` / `[]T` | | |
| `Map<K,V>` / `dict` / `map[K]V` | | |
| `Set<T>` / `set` | | |
| `Tuple` | | |
| `Optional<T>` / `T?` / `Option[T]` | | |
| `Union` / `enum` | | |

### Structural Types

| <Source> | <Target> | Notes |
|----------|----------|-------|
| `interface` | | |
| `class` | | |
| `abstract class` | | |
| `enum` | | |
| `type alias` | | |

### Function Types

| <Source> | <Target> | Notes |
|----------|----------|-------|
| Function signature | | |
| Lambda / closure | | |
| Generic function | | |
| Async function | | |
```

---

## Ownership Decision Tree

Use when converting from GC languages to ownership-based (Rust).

```
START: Is this data shared across components?
│
├─ YES: Is it mutated by multiple parts?
│   │
│   ├─ YES: Multi-threaded access?
│   │   ├─ YES → Arc<Mutex<T>> or channels
│   │   └─ NO  → Rc<RefCell<T>>
│   │
│   └─ NO: → Arc<T> (shared, immutable)
│
└─ NO: Single owner
    │
    ├─ Does data outlive its creator?
    │   ├─ YES → Return owned value (move)
    │   └─ NO  → Return borrowed reference (&T)
    │
    └─ Is mutation needed?
        ├─ YES → &mut T (exclusive borrow)
        └─ NO  → &T (shared borrow)
```

---

## Clone vs Borrow Decision Tree

```
START: Is the data expensive to clone?
│
├─ YES: Use borrowing with lifetimes
│   │
│   ├─ Single owner needed? → &T / &mut T
│   └─ Multiple owners needed? → Arc<T> / Rc<T>
│
└─ NO: Clone freely
    │
    ├─ Small data (< 64 bytes)? → Copy if possible
    └─ Larger data? → Clone explicitly, consider Cow<T>
```

---

## Conversion Self-Review Checklist

Complete before marking a conversion done:

### Type System
- [ ] All primitive types mapped
- [ ] All composite types mapped
- [ ] Generic constraints translated
- [ ] Nullable handling explicit (Option/Maybe/nil)

### Error Handling
- [ ] Exception → Result/Error return pattern applied
- [ ] Error types defined
- [ ] Error propagation idiom used (?, try, if err != nil)
- [ ] Panic/crash conditions documented

### Concurrency
- [ ] Async model translated (Promise → Future, etc.)
- [ ] Thread safety verified
- [ ] Shared state properly synchronized
- [ ] Cancellation patterns implemented

### Memory (if applicable)
- [ ] Ownership clearly defined
- [ ] Lifetimes annotated where needed
- [ ] No unnecessary cloning
- [ ] Resource cleanup verified (RAII/defer/finally)

### Idioms
- [ ] Code follows target language conventions
- [ ] Naming conventions applied (snake_case, camelCase, etc.)
- [ ] Not "source language in target syntax"
- [ ] Standard library used where appropriate

### Testing
- [ ] Original tests ported
- [ ] Golden tests for I/O comparison
- [ ] Edge cases covered
- [ ] Property-based tests for invariants

### Documentation
- [ ] Public APIs documented
- [ ] Conversion notes for non-obvious translations
- [ ] Dependencies documented

---

## Testing Strategy Checklist

```
TESTING PYRAMID FOR CONVERSIONS

                    ┌───────────────┐
                    │  Integration  │  ← Same API behavior
                    └───────────────┘
               ┌─────────────────────────┐
               │    Property-Based       │  ← Invariants hold
               └─────────────────────────┘
          ┌───────────────────────────────────┐
          │           Unit Tests              │  ← Logic match
          └───────────────────────────────────┘
     ┌─────────────────────────────────────────────┐
     │        Golden / Snapshot Tests              │  ← I/O match
     └─────────────────────────────────────────────┘
```

### Pre-Conversion
- [ ] Export golden test data from original implementation
- [ ] Document expected behavior for edge cases
- [ ] Identify performance baseline

### During Conversion
- [ ] Port unit tests first (before implementation)
- [ ] Run tests after each module conversion
- [ ] Track test coverage

### Post-Conversion
- [ ] All original tests pass
- [ ] Golden tests match original output
- [ ] Property-based tests verify invariants
- [ ] Performance meets or exceeds baseline
- [ ] Integration tests pass

---

## Performance Checklist

Use after conversion to verify performance characteristics:

### Memory
- [ ] No unnecessary allocations
- [ ] String building uses appropriate method (join, builder)
- [ ] Collections pre-sized when size known
- [ ] Large data uses references, not clones

### Computation
- [ ] Appropriate collection types (HashMap vs Vec for lookup)
- [ ] Lazy evaluation where beneficial
- [ ] Hot paths identified and optimized
- [ ] No redundant computation

### Concurrency
- [ ] Parallelism used where appropriate
- [ ] No unnecessary synchronization
- [ ] Lock contention minimized
- [ ] Async used for I/O-bound work

### Verification
- [ ] Benchmarks written for critical paths
- [ ] Compared to original implementation
- [ ] Memory profiling done
- [ ] No regressions from original

---

## APTV Phase Checklist

### Analyze Phase
- [ ] Source code structure understood
- [ ] All types/interfaces identified
- [ ] All functions/methods catalogued
- [ ] Module boundaries mapped
- [ ] External dependencies listed
- [ ] Language-specific features noted

### Plan Phase
- [ ] Type mapping table complete
- [ ] Idiom translations identified
- [ ] Module/package structure designed
- [ ] Dependencies selected
- [ ] Testing strategy defined
- [ ] Tooling set up

### Transform Phase
- [ ] Types and interfaces converted first
- [ ] Core logic converted
- [ ] Target idioms adopted (not transliterated)
- [ ] Tests passing incrementally
- [ ] Code reviewed for idiomatic style

### Validate Phase
- [ ] All tests pass
- [ ] Golden tests match
- [ ] Property-based tests pass
- [ ] Performance acceptable
- [ ] Code review complete
- [ ] Documentation complete

---

## Error Model Translation Template

```markdown
## Error Translation: <Source> → <Target>

### Source Error Model
- Pattern: (exceptions / error returns / Result types)
- Propagation: (throw/try-catch / if err != nil / ? operator)
- Hierarchy: (describe error class structure)

### Target Error Model
- Pattern: (exceptions / error returns / Result types)
- Propagation: (throw/try-catch / if err != nil / ? operator)
- Hierarchy: (describe error type structure)

### Mapping

| Source Error | Target Error | Notes |
|--------------|--------------|-------|
| Base exception | | |
| Not found | | |
| Validation | | |
| IO error | | |
| Network error | | |
| Auth error | | |

### Propagation Translation

| Source | Target |
|--------|--------|
| `throw new Error(msg)` | |
| `try { } catch (e) { }` | |
| `throw` (rethrow) | |
| `finally { }` | |
```

---

## Concurrency Translation Template

```markdown
## Concurrency Translation: <Source> → <Target>

### Source Model
- Async pattern: (Promises / async-await / goroutines / actors)
- Threading: (single-threaded / green threads / OS threads)
- Channels: (available / not available)

### Target Model
- Async pattern: (Promises / async-await / goroutines / actors)
- Threading: (single-threaded / green threads / OS threads)
- Channels: (available / not available)

### Pattern Mapping

| Source Pattern | Target Pattern | Notes |
|----------------|----------------|-------|
| `async function` | | |
| `await promise` | | |
| `Promise.all([])` | | |
| `Promise.race([])` | | |
| spawn/thread | | |
| channel send | | |
| channel receive | | |
| mutex/lock | | |
```
