# Pattern Clustering and Gap Analysis

## Clustering Summary

### Cluster Distribution

| Cluster | Unique Patterns | Pattern Instances |
|---------|-----------------|-------------------|
| Universal | 173 | 2186 |
| Family-specific | 417 | 1332 |
| Language-specific | 3293 | 3677 |
| **Total** | **3883** | **7195** |

### Family-Specific Pattern Counts

| Family | Pattern Instances |
|--------|-------------------|
| ml-fp | 215 |
| systems | 78 |
| apple | 63 |
| beam | 10 |
| dynamic | 8 |

### Cluster Classification Criteria

- **Universal**: Appears in 5+ patterns across 3+ language families
- **Family-specific**: Appears within a single language family
- **Language-specific**: Appears in only 1-2 language pairs

## Gap Analysis Summary

### Gap Types

| Gap Type | Count | Description |
|----------|-------|-------------|
| negative | 29 | Anti-patterns (what NOT to do) |
| human_decision | 183 | Requires manual choice |
| lossy | 108 | Information loss in conversion |
| impossible | 0 | Cannot be translated |
| **Total** | **320** | |

### Gap Severity Distribution

| Severity | Count |
|----------|-------|
| critical | 0 |
| high | 0 |
| medium | 320 |
| low | 0 |

## Key Findings

### Universal Patterns (apply to most conversions)

These patterns are good candidates for core IR constructs:

1. **`bool`** (81 occurrences)
2. **`String`** (78 occurrences)
3. **`int`** (76 occurrences)
4. **`float`** (63 occurrences)
5. **-** (59 occurrences)
6. **General conversion methodology** (46 occurrences)
7. **`Double`** (42 occurrences)
8. **Test equivalence** (40 occurrences)
9. **`List a`** (39 occurrences)
10. **`Str`** (36 occurrences)

### Family-Specific Patterns

Patterns that are shared within language families but not universal:

#### APPLE Family

- `@property (weak)` (3 patterns)
- `weak var` (3 patterns)
- `@property (copy)` (3 patterns)
- `NSString *` (2 patterns)
- `NSInteger` (2 patterns)

#### BEAM Family

- Qualified calls (2 patterns)
- `1` (2 patterns)
- `1.0` (2 patterns)
- `false` (2 patterns)
- `{1, 2, 3}` (2 patterns)

#### DYNAMIC Family

- `T[]` / `Array<T>` (2 patterns)
- `Coroutine[Any, Any, T]` (2 patterns)
- `dict[str, V]` (2 patterns)
- `class X:` (2 patterns)

#### ML-FP Family

- `unit` (10 patterns)
- `IO a` (6 patterns)
- `{}` (5 patterns)
- `'a array` (4 patterns)
- `( a, b )` (4 patterns)

#### SYSTEMS Family

- ptr-sized (4 patterns)
- `T*` (4 patterns)
- `std::unique_ptr<T>` (4 patterns)
- `std::shared_ptr<T>` (4 patterns)
- `nullptr` (3 patterns)


### Critical Gaps

Conversions that cannot be performed automatically:


### Negative Patterns (Anti-patterns)

What NOT to do during conversion:

- **c → cpp**: Forgetting to Use `nullptr` Instead of `NULL`
- **c → rust**: Use-After-Free
- **clojure → elm**: Assuming Dynamic Typing
  - Instead: Treating Elm like dynamically-typed Clojure

```elm
-- ❌ WRONG: Can't have heterogeneous lists
users...
- **clojure → erlang**: Atom Table Exhaustion
- **clojure → haskell**: Dynamic Type Assumptions → Static Type Requirements
  - Instead: Clojure allows heterogeneous collections; Haskell requires homogeneous types.

```clojure
;; Clojure...
- **cpp → rust**: Overusing Rc/Arc (Avoid C++ shared_ptr Mindset)
  - Instead: Prefer borrowing or single ownership:

```rust
// Good: Use Box for owned children
struct Node {
   ...
- **elixir → elm**: Expecting Runtime Dynamism
- **elixir → erlang**: String vs Binary Confusion
  - Instead: Always translate Elixir `"strings"` to Erlang binaries `<<"strings">>`.

---...
- **elixir → roc**: Process-Based Thinking in Pure Code
  - Instead: ```roc
# ✓ Use explicit state passing
State : I64

increment : State -> State
increment = \count -> ...
- **elixir → scala**: Dynamic Typing → Static Typing
  - Instead: Use sealed trait ADT for type safety.

```scala
sealed trait Data
case class IntData(value: Int) ext...

## Recommendations for IR Design

Based on the clustering analysis:

1. **Core IR should support universal patterns first** - These have the widest applicability
2. **Family extensions for family-specific patterns** - ML-FP, BEAM, Systems families have distinct patterns
3. **Language annotations for unique features** - Ownership (Rust), Actors (BEAM), etc.
4. **Gap registry** - Track impossible/lossy conversions to warn users

## Data Files

- `pattern-clusters.json` - Full clustering data
- `gap-analysis.json` - Full gap analysis data
