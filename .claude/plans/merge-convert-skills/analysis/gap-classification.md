# Gap Classification Analysis

Reclassification of Phase 0 gaps into the 6-category system.

**Generated:** 2026-02-04
**Total Gaps:** 320

## 1. Classification Summary Table

| Category | Count | % of Total | Severity | Original Mapping |
|----------|-------|------------|----------|------------------|
| **impossible** | 0 | 0.0% | critical | - |
| **lossy** | 108 | 33.8% | high | lossy:108 |
| **structural** | 176 | 55.0% | medium | human_decision:171, negative:5 |
| **idiomatic** | 2 | 0.6% | low | negative:2 |
| **runtime** | 22 | 6.9% | high | negative:10, human_decision:12 |
| **semantic** | 12 | 3.8% | medium | negative:12 |
| **TOTAL** | **320** | **100%** | - | - |

## 2. Detailed Classification by Category

### 2.1 Impossible (0 gaps)

No gaps were classified as truly impossible. While some conversions are difficult,
all can be achieved with sufficient restructuring or alternative approaches.

**Potential candidates for future 'impossible' classification:**

- Dependent types (Idris/Agda) to non-dependent type systems
- Linear types (Rust) to GC-only languages without ownership
- Effect systems (Koka) to languages without effect tracking
- First-class continuations (Scheme) to languages without call/cc

### 2.2 Lossy (108 gaps)

All 108 lossy gaps involve numeric precision differences between languages.

| Source | Target | Description | Mitigation |
|--------|--------|-------------|------------|
| clojure | elixir | `Long` / `42` to `integer` | arbitrary precision in both |
| elixir | clojure | `integer` to `Long` / `42` | arbitrary precision in both |
| clojure | elixir | `Double` / `3.14` to `float` | 64-bit double precision |
| clojure | erlang | `42` to `42` | integers (arbitrary precision) |
| clojure | fsharp | `BigInteger` to `bigint` | arbitrary precision integers |
| clojure | fsharp | `BigDecimal` to `decimal` | arbitrary precision decimals |
| clojure | haskell | `Long` to `Integer` | unbounded (arbitrary precision) |
| clojure | haskell | `Double` to `Float` | single precision |
| clojure | scala | `BigInt` to `BigInt` | arbitrary precision integers |
| elixir | erlang | `1` to `1` | integers (arbitrary precision) |
| elixir | fsharp | `float()` to `float` | 64-bit double precision |
| elixir | fsharp | `integer()` to `bigint` | arbitrary precision |
| elixir | haskell | `integer()` to `Int` / `Integer` | int fixed-width, integer arbitrary |
| elm | erlang | `Int` to `integer()` | arbitrary precision |
| elm | erlang | `Float` to `float()` | ieee 754 double precision |
| elm | haskell | `Int` to `Integer` | unbounded (arbitrary precision) |
| elm | haskell | `Float` to `Float` | single precision |
| elm | haskell | `Float` to `Double` | preferred double precision |
| elm | roc | `Int` to `I64` or `U64` | elm has arbitrary precision |
| erlang | haskell | `float()` to `Double` or `Float` | precision choice |
| ... | ... | *(88 more lossy gaps)* | ... |

**Key lossy patterns:**

- **Arbitrary precision integers**: Python/Clojure/Haskell `Integer` to fixed-size types
- **Floating point precision**: Float vs Double across languages
- **BigInt/BigDecimal**: Different arbitrary precision implementations

### 2.3 Structural (176 gaps)

Structural gaps require code reorganization but are achievable:

| Subcategory | Count | Examples |
|-------------|-------|----------|
| Scope boundaries | ~140 | Language fundamentals, reverse conversions |
| Framework-specific | ~15 | Phoenix, Django, framework migrations |
| Advanced patterns | ~10 | C++ templates, F# type providers |
| Other structural | ~11 | Object slicing, error handling |

**Sample structural gaps:**

- `c` to `cpp`: General conversion methodology
- `c` to `cpp`: C language fundamentals
- `c` to `cpp`: C++ language fundamentals
- `c` to `cpp`: Reverse conversion (C++ to C)
- `c` to `rust`: Advanced C memory engineering
- `c` to `rust`: Advanced Rust memory engineering
- `clojure` to `elixir`: ClojureScript specifics
- `cpp` to `rust`: Advanced C++ metaprogramming (SFINAE, CRTP)
- `elixir` to `erlang`: Phoenix-specific conversions
- `java` to `cpp`: Object Slicing

### 2.4 Idiomatic (2 gaps)

Style and convention differences (low severity):

- **c to cpp**: Forgetting to Use `nullptr` Instead of `NULL`
  - Mitigation: Use modern C++ style
- **fsharp to scala**: PascalCase vs camelCase
  - Mitigation: F# uses PascalCase for everything, Scala uses camelCase for members

### 2.5 Runtime (22 gaps)

Different execution models requiring careful consideration:

| Source | Target | Gap | Original Type |
|--------|--------|-----|---------------|
| c | rust | Use-After-Free | negative |
| cpp | rust | Overusing Rc/Arc (Avoid C++ shared_ptr Mindset) | negative |
| elixir | roc | Process-Based Thinking in Pure Code | negative |
| elixir | elm | Expecting Runtime Dynamism | negative |
| elm | erlang | Assuming Compile-Time Safety | negative |
| golang | rust | Trying to Return Borrowed References Without Life... | negative |
| haskell | roc | Lazy vs Strict - Infinite Lists | negative |
| haskell | scala | Assuming Lazy Evaluation | negative |
| python | elixir | Expecting Mutable State | negative |
| python | haskell | Forgetting About Laziness | negative |
| typescript | rust | Over-cloning to Satisfy Borrow Checker | negative |
| clojure | elm | ClojureScript to Elm (similar but with JS runtime) | human_decision |
| clojure | erlang | ClojureScript to Erlang - two-step conversion | human_decision |
| clojure | haskell | ClojureScript to PureScript/Elm | human_decision |
| clojure | roc | ClojureScript frontend patterns | human_decision |
| elixir | elm | Server-side Elixir deployment | human_decision |
| elixir | elm | Phoenix-specific patterns - LiveView | human_decision |
| elixir | fsharp | OTP distributed systems - .NET redesign | human_decision |
| elm | roc | Browser-specific Elm code - Roc no DOM | human_decision |
| fsharp | haskell | .NET interop specifics | human_decision |
| python | elm | Fable.Python - different toolchain | human_decision |
| python | haskell | Web frameworks - Django/Flask to Servant/Yesod | human_decision |

**Key runtime patterns:**

- **Memory model**: Ownership/borrowing (Rust) vs GC (Java, Python)
- **Evaluation strategy**: Lazy (Haskell) vs strict (Roc, Scala)
- **Concurrency model**: Actor-based (BEAM) vs async/await vs threads
- **Mutability**: Immutable-first (FP) vs mutable-default (imperative)

### 2.6 Semantic (12 gaps)

Subtle meaning changes that can lead to bugs:

| Source | Target | Gap | Mitigation |
|--------|--------|-----|------------|
| clojure | elm | Assuming Dynamic Typing | Define explicit types with Maybe |
| clojure | erlang | Atom Table Exhaustion | Avoid dynamic atom creation |
| clojure | haskell | Dynamic Type Assumptions to Static | Use ADTs for heterogeneous data |
| elixir | erlang | String vs Binary Confusion | Use binaries consistently |
| elixir | scala | Dynamic Typing to Static Typing | Use sealed trait ADT |
| elm | haskell | Assuming Elm's Simplicity Limits Apply | Use type classes, lazy eval |
| erlang | haskell | Forgetting Type Signatures | Always write top-level sigs |
| fsharp | haskell | Confusing Either Direction | Right is success, Left is error |
| objc | swift | Force Unwrapping Optionals | Use guard let, optional chaining |
| python | clojure | Mutable State to Immutable Data | Use atoms or rebinding |
| python | rust | Arbitrary Precision Integer Overflow | Use num_bigint::BigInt |
| python | typescript | Python `None` to TypeScript null/undefined | Choose convention |
| python | scala | Mutability Assumptions | Use immutable collections |
| roc | scala | Assuming Immutability is Enforced | Use immutable Scala patterns |
| typescript | golang | Ignoring Error Returns | Always check err != nil |

## 3. Human Decision Mapping

The 183 original `human_decision` gaps have been reclassified:

| New Category | Count | Decision Required | Common Options |
|--------------|-------|-------------------|----------------|
| structural | 171 | Yes | Use complementary skill, restructure code |
| runtime | 12 | Yes | Platform-specific implementation |

### Common Human Decision Patterns

| Pattern | Category | Decision Type | Guidance |
|---------|----------|---------------|----------|
| Language fundamentals | structural | Skill reference | Use `lang-*-dev` skills |
| Reverse conversion | structural | Skill reference | Use corresponding `convert-*` skill |
| Framework-specific | structural | Architecture | Redesign for target framework |
| Advanced type features | structural | Manual | Case-by-case translation |
| Platform differences | runtime | Architecture | Use platform-appropriate patterns |

### Human Decision Examples by Category

**Structural (requiring skill references):**
- General conversion methodology -> use `meta-convert-dev`
- Language fundamentals -> use `lang-{language}-dev` skills
- Reverse conversions -> use reverse `convert-*` skill
- Framework migrations -> consult framework-specific guides

**Runtime (requiring architecture decisions):**
- ClojureScript/frontend patterns -> assess target platform capabilities
- OTP/distributed systems -> redesign for target runtime model
- Browser-specific code -> identify non-portable sections

## 4. Validation

### 4.1 Gap Count Verification

- **Original gaps:** 320
- **Classified gaps:** 320
- **Orphans:** 0

### 4.2 Original Type Distribution

| Original Type | impossible | lossy | structural | idiomatic | runtime | semantic |
|---------------|------------|-------|------------|-----------|---------|----------|
| negative | 0 | 0 | 5 | 2 | 10 | 12 |
| human_decision | 0 | 0 | 171 | 0 | 12 | 0 |
| lossy | 0 | 108 | 0 | 0 | 0 | 0 |

### 4.3 Multi-Category Candidates

Some gaps could reasonably fit multiple categories. Primary assignment rationale:

| Gap | Primary | Could Also Be | Rationale |
|-----|---------|---------------|-----------|
| Integer overflow | semantic | lossy | Behavioral change prioritized over data loss |
| Lazy vs strict | runtime | semantic | Execution model is primary concern |
| Type system mismatch | semantic | structural | Subtle bugs prioritized over restructuring |
| Framework migration | structural | runtime | Code organization prioritized |
| Memory model differences | runtime | structural | Execution model is fundamental |
| String/binary confusion | semantic | idiomatic | Meaning matters more than style |

### 4.4 Potential 'Impossible' Gaps Not Found in Phase 0

The following gap types were not present in Phase 0 data but may exist:

| Gap Type | From | To | Why Potentially Impossible |
|----------|------|----|-----------------------------|
| Dependent types | Idris/Agda | Most languages | No type-level computation |
| Linear types | Rust | Python/JS | No ownership enforcement |
| First-class continuations | Scheme | C/Go | No call/cc equivalent |
| Algebraic effects | Koka/Eff | Most languages | No effect handlers |
| Compile-time reflection | Zig | Most languages | No comptime equivalent |
| Session types | Various | Most languages | No channel type checking |
| Uniqueness types | Clean | Most languages | No uniqueness tracking |

These would require future skill development to address.

## 5. Recommendations

### 5.1 Priority for IR Design

Based on gap distribution:

1. **Lossy gaps (108)** - IR needs numeric precision annotations
2. **Structural gaps (176)** - IR needs clear skill boundary markers
3. **Runtime gaps (22)** - IR needs execution model metadata
4. **Semantic gaps (12)** - IR needs semantic warning annotations
5. **Idiomatic gaps (2)** - Handled by style transformers

### 5.2 Human Decision Reduction

To reduce the 183 human_decision gaps:

1. **Create missing `lang-*-dev` skills** for referenced languages
2. **Add framework-specific conversion guides** for common stacks
3. **Document platform capability matrices** for runtime decisions
4. **Build decision trees** for common patterns (error handling, collections)

### 5.3 Gap Registry Integration

The 6-category classification should be stored in the IR database:

```sql
INSERT INTO semantic_gaps (gap_category, concept, severity, automation_level)
VALUES
  ('lossy', 'integer_precision', 'high', 'partial'),
  ('structural', 'framework_migration', 'medium', 'none'),
  ('runtime', 'memory_model', 'high', 'partial'),
  ('semantic', 'type_system_mismatch', 'medium', 'partial'),
  ('idiomatic', 'naming_convention', 'low', 'full');
```

## 6. Data Files

- **Source:** `.claude/plans/merge-convert-skills/data/gap-analysis.json`
- **Schema:** `.claude/plans/merge-convert-skills/data/schema.sql`
- **Patterns:** `.claude/plans/merge-convert-skills/data/patterns.sql`
