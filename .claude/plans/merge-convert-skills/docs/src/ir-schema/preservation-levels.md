# Semantic Preservation Levels

## Overview

### Why Preservation Levels Matter

Code conversion is not a binary operation. A translation from one language to another can be "correct" in multiple ways, each with different implications for the resulting code's behavior, maintainability, and performance. Preservation levels provide a formal framework for:

1. **Setting expectations**: Users understand what quality of output to expect from automated tools
2. **Guiding tool design**: Implementers know what guarantees their tools must provide
3. **Measuring progress**: Teams can track conversion quality objectively
4. **Informing review scope**: Reviewers know which aspects need human attention

### How Levels Inform Tool Design

Different tools and use cases target different preservation levels:

| Tool Type | Typical Target | Rationale |
|-----------|---------------|-----------|
| Transpilers | Level 1 | Correctness over style |
| Migration tools | Level 2 | Code must be maintainable |
| Refactoring tools | Level 2-3 | Idiomatic output expected |
| Performance optimizers | Level 3 | Speed is the goal |

### Relationship to IR Layer Design

The Intermediate Representation (IR) captures semantic information at different granularities:

- **Core semantics** enable Level 1 (what the code does)
- **Structural patterns** enable Level 2 (how it organizes logic)
- **Idiom annotations** enable Level 3 (how to express it naturally)

A well-designed IR must capture enough information to support the target preservation level.

---

## Level Definitions

---

## Level 0: Syntactically Valid

### Definition

The converted code compiles (or parses) without errors in the target language. No guarantees are made about runtime behavior, correctness, or semantic equivalence to the source.

### Criteria

- [ ] Code parses without syntax errors
- [ ] Code compiles without type errors (for statically-typed targets)
- [ ] All referenced identifiers are defined
- [ ] Import/module dependencies are resolvable

### What This Level Guarantees

- The output is valid code in the target language
- A developer can open it in an IDE without red squiggles
- It can be used as a starting point for manual correction

### What This Level Does NOT Guarantee

- Runtime behavior matches the source
- The program produces correct output
- Edge cases are handled properly
- The code is readable or maintainable

### Use Cases

- **Bootstrapping**: Getting a first-pass skeleton for manual refinement
- **Syntax exploration**: Seeing how constructs might translate
- **Template generation**: Creating boilerplate to fill in
- **Partial conversions**: When only structure matters, not behavior

### Example

**Source (Python):**
```python
def calculate_average(numbers):
    total = sum(numbers)
    return total / len(numbers)
```

**Target (Rust) at Level 0:**
```rust
fn calculate_average(numbers: Vec<i32>) -> i32 {
    let total: i32 = numbers.iter().sum();
    total / numbers.len()
}
```

**Why this is Level 0:**
- Compiles (with the right imports)
- Type mismatch: `len()` returns `usize`, division with `i32` fails
- Return type `i32` loses floating-point precision
- Empty vector causes panic (division by zero)
- The code is structurally similar but semantically broken

---

## Level 1: Semantically Equivalent

### Definition

The converted code produces the same observable behavior as the source for all valid inputs. Edge cases, error handling, and output values match the original program's specification.

### Criteria

- [ ] All Level 0 criteria are met
- [ ] Same output for same input (functional equivalence)
- [ ] Same error conditions and error messages (where applicable)
- [ ] Same side effects (I/O, state mutations)
- [ ] Equivalent handling of edge cases (empty inputs, nulls, boundaries)

### What This Level Guarantees

- The converted code is a correct implementation of the source's logic
- Tests written for the source will pass on the target (modulo syntax)
- Behavioral bugs in the source are faithfully reproduced
- The conversion is "safe" for production use (behavior-wise)

### What This Level Does NOT Guarantee

- Code follows target language conventions
- Performance is acceptable
- Code is readable or maintainable by target-language developers
- Memory usage is optimal
- The solution is the "right way" to solve the problem in the target

### Use Cases

- **Automated migration**: When correctness is paramount
- **Test suite conversion**: Tests must preserve assertions
- **Algorithm porting**: Mathematical correctness required
- **Compliance-critical code**: Behavior must be auditable

### Example

**Source (Python):**
```python
def calculate_average(numbers):
    if not numbers:
        return None
    total = sum(numbers)
    return total / len(numbers)
```

**Target (Rust) at Level 1:**
```rust
fn calculate_average(numbers: &[f64]) -> Option<f64> {
    if numbers.is_empty() {
        return None;
    }
    let total: f64 = numbers.iter().sum();
    Some(total / numbers.len() as f64)
}
```

**Why this is Level 1:**
- Compiles and runs correctly
- Returns `None`/`None` for empty input (semantically equivalent to Python's `None`)
- Returns correct floating-point average
- Handles all edge cases the same way
- However: uses `&[f64]` slice (idiomatic) but that's incidental, not systematic

---

## Level 2: Idiomatically Correct

### Definition

The converted code not only behaves correctly but follows the conventions, patterns, and best practices of the target language. A native developer of the target language would find the code natural and maintainable.

### Criteria

- [ ] All Level 1 criteria are met
- [ ] Follows target language naming conventions (snake_case, camelCase, etc.)
- [ ] Uses appropriate data structures (Vec vs array, HashMap vs dict)
- [ ] Uses language-specific idioms (iterators, pattern matching, comprehensions)
- [ ] Error handling follows target conventions (Result, exceptions, error codes)
- [ ] Documentation style matches target ecosystem
- [ ] Module/package structure follows target conventions

### What This Level Guarantees

- Native developers can maintain the code without "foreign" patterns
- Code integrates well with the target ecosystem's tooling
- Static analysis and linters pass without warnings
- Code reviews focus on logic, not style corrections
- The codebase feels "native" to the target language

### What This Level Does NOT Guarantee

- Optimal performance
- Minimal memory allocation
- Zero-cost abstractions used where possible
- Parallelism or concurrency opportunities exploited

### Use Cases

- **Production migrations**: Code will be maintained long-term
- **Team handoff**: Target-language experts will own the code
- **Open source**: Community contributors expect idiomatic code
- **Code review gates**: Idiomatic code is a merge requirement

### Example

**Source (Python):**
```python
def calculate_average(numbers):
    if not numbers:
        return None
    total = sum(numbers)
    return total / len(numbers)

def process_data(data_list):
    results = []
    for item in data_list:
        if item > 0:
            results.append(item * 2)
    return results
```

**Target (Rust) at Level 2:**
```rust
/// Calculates the arithmetic mean of a slice of numbers.
///
/// Returns `None` if the slice is empty.
pub fn calculate_average(numbers: &[f64]) -> Option<f64> {
    if numbers.is_empty() {
        return None;
    }
    Some(numbers.iter().sum::<f64>() / numbers.len() as f64)
}

/// Filters positive values and doubles them.
pub fn process_data(data: &[i32]) -> Vec<i32> {
    data.iter()
        .filter(|&&x| x > 0)
        .map(|&x| x * 2)
        .collect()
}
```

**Why this is Level 2:**
- Semantically equivalent (Level 1)
- Uses iterator chains instead of manual loops (Rust idiom)
- Uses doc comments with `///` (Rust convention)
- Uses slices for input (idiomatic borrowing)
- Uses functional combinators (`filter`, `map`, `collect`)
- Function visibility is explicit (`pub`)
- Type inference used appropriately (`::<f64>` turbofish)

---

## Level 3: Optimized

### Definition

The converted code is not only correct and idiomatic but also optimized for performance, memory usage, and/or concurrency in the target language's execution model. The code takes advantage of target-specific optimizations that may have no equivalent in the source language.

### Criteria

- [ ] All Level 2 criteria are met
- [ ] Algorithmic complexity is optimal for the target's capabilities
- [ ] Memory allocation is minimized where appropriate
- [ ] Cache-friendly data layouts are used
- [ ] Concurrency/parallelism opportunities are exploited (where safe)
- [ ] Target-specific compiler hints are applied (inlining, specialization)
- [ ] Zero-cost abstractions are preferred over runtime abstractions
- [ ] Hot paths are identified and optimized

### What This Level Guarantees

- Performance is competitive with hand-written target code
- Resource usage is appropriate for production workloads
- The code can serve as a reference implementation
- Profiling reveals no obvious optimization opportunities
- Scalability characteristics are well-understood

### What This Level Does NOT Guarantee

- Maximum theoretical performance (may require unsafe code)
- Platform-specific optimizations (SIMD, GPU, etc.)
- Micro-optimizations that harm readability
- Performance under all possible workloads

### Use Cases

- **Performance-critical systems**: Latency and throughput matter
- **Resource-constrained environments**: Memory or CPU budgets
- **High-traffic services**: Efficiency at scale
- **Reference implementations**: Demonstrating best practices

### Example

**Source (Python):**
```python
def calculate_average(numbers):
    if not numbers:
        return None
    total = sum(numbers)
    return total / len(numbers)

def process_data(data_list):
    results = []
    for item in data_list:
        if item > 0:
            results.append(item * 2)
    return results
```

**Target (Rust) at Level 3:**
```rust
use rayon::prelude::*;

/// Calculates the arithmetic mean of a slice of numbers.
///
/// Returns `None` if the slice is empty. Uses SIMD-friendly iteration.
#[inline]
pub fn calculate_average(numbers: &[f64]) -> Option<f64> {
    let len = numbers.len();
    if len == 0 {
        return None;
    }
    // Cache length to avoid repeated bounds checks
    let sum: f64 = numbers.iter().copied().sum();
    Some(sum / len as f64)
}

/// Filters positive values and doubles them.
///
/// For large datasets, consider `process_data_parallel`.
#[inline]
pub fn process_data(data: &[i32]) -> Vec<i32> {
    // Pre-allocate with estimated capacity
    let mut results = Vec::with_capacity(data.len() / 2);
    results.extend(
        data.iter()
            .copied()
            .filter(|&x| x > 0)
            .map(|x| x * 2)
    );
    results
}

/// Parallel version for large datasets (> 10,000 elements recommended).
pub fn process_data_parallel(data: &[i32]) -> Vec<i32> {
    data.par_iter()
        .copied()
        .filter(|&x| x > 0)
        .map(|x| x * 2)
        .collect()
}
```

**Why this is Level 3:**
- Semantically equivalent and idiomatic (Level 2)
- `#[inline]` hints for compiler optimization
- Pre-allocation with `Vec::with_capacity` to reduce allocations
- `.copied()` avoids reference overhead for Copy types
- Parallel version using Rayon for large datasets
- Documentation notes performance characteristics
- Length cached before division to assist bounds-check elimination

---

## Level Comparison Matrix

| Aspect | Level 0 | Level 1 | Level 2 | Level 3 |
|--------|:-------:|:-------:|:-------:|:-------:|
| **Compiles/Parses** | Yes | Yes | Yes | Yes |
| **Correct Output** | No | Yes | Yes | Yes |
| **Handles Edge Cases** | No | Yes | Yes | Yes |
| **Idiomatic Style** | No | Maybe | Yes | Yes |
| **Follows Conventions** | No | No | Yes | Yes |
| **Performant** | No | No | Maybe | Yes |
| **Maintainable** | No | No | Yes | Yes |
| **Production-Ready** | No | Maybe | Yes | Yes |
| **Optimal Resource Use** | No | No | No | Yes |

### Verification Methods by Level

| Level | Verification Approach |
|-------|----------------------|
| Level 0 | Compiler/parser success |
| Level 1 | Test suite passes, property-based testing |
| Level 2 | Linter passes, code review by native developer |
| Level 3 | Benchmarks, profiling, load testing |

---

## Progression Path

### Level 0 to Level 1: Correctness Pass

**Transformations Required:**
1. Fix type mismatches and conversions
2. Add error/null handling for edge cases
3. Ensure equivalent behavior for boundary conditions
4. Add missing runtime checks (bounds, overflow)
5. Handle language-specific semantic differences (integer division, truthiness)

**Automation Potential:** Medium-High
- Type inference can catch many issues
- Test suite execution reveals behavioral gaps
- Static analysis identifies unsafe patterns

**Typical Tools:** Type checkers, test generators, formal verification

### Level 1 to Level 2: Idiom Pass

**Transformations Required:**
1. Replace imperative loops with functional idioms (where appropriate)
2. Apply naming conventions (snake_case to camelCase, etc.)
3. Restructure error handling to match target conventions
4. Use appropriate data structures from standard library
5. Add documentation in target format
6. Organize code into idiomatic module structure

**Automation Potential:** Medium
- Pattern recognition can suggest idioms
- Linters can enforce naming conventions
- Some idiom transformations are well-defined

**Typical Tools:** Linters, formatters, idiom suggestion engines

### Level 2 to Level 3: Optimization Pass

**Transformations Required:**
1. Profile to identify hot paths
2. Reduce allocations (pre-allocation, pooling, stack allocation)
3. Exploit parallelism where safe and beneficial
4. Add compiler hints (inlining, specialization)
5. Consider cache-friendly data layouts
6. Document performance characteristics

**Automation Potential:** Low-Medium
- Profile-guided optimization can help
- Some patterns (pre-allocation) are automatable
- Parallelism requires semantic understanding
- Many optimizations require domain knowledge

**Typical Tools:** Profilers, benchmarks, optimization advisors

### Progression Summary

```
Level 0  ──────────────>  Level 1  ──────────────>  Level 2  ──────────────>  Level 3
         Correctness Pass          Idiom Pass             Optimization Pass

         - Fix types               - Apply idioms         - Profile
         - Add error handling      - Fix naming           - Pre-allocate
         - Handle edge cases       - Add docs             - Parallelize
         - Match semantics         - Restructure          - Add hints

         HIGH automation           MEDIUM automation      LOW automation
```

---

## Tool Implications

### What Automated Converters Can Achieve

| Target Level | Feasibility | Notes |
|--------------|-------------|-------|
| Level 0 | Straightforward | Syntax translation is well-understood |
| Level 1 | Achievable | Requires semantic analysis, may need runtime shims |
| Level 2 | Partially | Some idioms are pattern-matchable, others need AI |
| Level 3 | Rarely | Requires profiling, domain knowledge, benchmarking |

### Recommended Tool Output Levels

| Converter Type | Minimum Level | Target Level | Notes |
|----------------|---------------|--------------|-------|
| Transpiler | Level 1 | Level 1 | Correctness is the contract |
| Migration assistant | Level 1 | Level 2 | Code will be maintained |
| AI-assisted converter | Level 2 | Level 2-3 | Can suggest idioms |
| Manual rewrite | Level 2 | Level 3 | Human judgment for optimization |

### Communicating Level to Users

Converters should clearly indicate the output level:

```
# Conversion Report

Source: main.py (Python 3.11)
Target: main.rs (Rust 1.75)

Preservation Level: Level 1 (Semantically Equivalent)

This means:
  [x] Code compiles without errors
  [x] Behavior matches source for all test cases
  [ ] Code may not follow Rust idioms
  [ ] Performance has not been optimized

Recommended next steps:
  1. Run `cargo clippy` for idiom suggestions
  2. Review generated code with a Rust developer
  3. Profile if performance is critical
```

### User Expectations by Level

| User Goal | Acceptable Level | User Action Required |
|-----------|------------------|---------------------|
| "Just make it work" | Level 1 | Run tests, deploy |
| "I need to maintain this" | Level 2 | Light review, merge |
| "This is performance-critical" | Level 3 | Profile, benchmark, iterate |

---

## Relationship to Gap Categories

Semantic gaps between languages constrain the maximum achievable preservation level. The following table maps gap categories to realistic preservation targets.

### Gap Category to Preservation Level Mapping

| Gap Category | Max Achievable Level | Strategy | Example |
|--------------|---------------------|----------|---------|
| **impossible** | Level 0 (with loss) | Emit warning, stub, or panic | Python `eval()` to Rust |
| **lossy** | Level 1 | Preserve semantics with runtime warnings | Arbitrary-precision int to fixed-width |
| **structural** | Level 2 | Transform to equivalent pattern | Class inheritance to trait composition |
| **idiomatic** | Level 2-3 | Apply target idioms | List comprehension to iterator chain |
| **runtime** | Level 1-2 | Use shims or polyfills | GC semantics to ownership |
| **semantic** | Level 1 | Document caveats | Float NaN handling differences |

### Detailed Gap Analysis

#### Impossible Gaps (Max: Level 0)

When a source language feature has no meaningful target equivalent:

- **Example**: Python `exec()` executing dynamic code
- **Strategy**: Emit a compilation error or panic stub
- **User action**: Manual redesign required

```rust
// Generated stub for impossible conversion
fn dynamic_exec(_code: &str) -> ! {
    panic!("Dynamic code execution not supported in Rust. Manual redesign required.");
}
```

#### Lossy Gaps (Max: Level 1)

When conversion requires accepting precision or capability loss:

- **Example**: Python `int` (arbitrary precision) to Rust `i64`
- **Strategy**: Convert with overflow detection
- **User action**: Review for potential overflow scenarios

```rust
// Level 1: Correct but may panic on overflow
fn convert_big_int(py_int: &PyInt) -> Result<i64, OverflowError> {
    py_int.try_into()  // Returns error if value doesn't fit
}
```

#### Structural Gaps (Max: Level 2)

When language paradigms differ but equivalent patterns exist:

- **Example**: Python class inheritance to Rust traits
- **Strategy**: Transform to idiomatic target pattern
- **User action**: Review trait design for correctness

```rust
// Level 2: Structurally transformed, idiomatic
trait Animal {
    fn speak(&self) -> String;
}

struct Dog;
impl Animal for Dog {
    fn speak(&self) -> String {
        "Woof!".to_string()
    }
}
```

#### Idiomatic Gaps (Max: Level 2-3)

When equivalent constructs exist but style differs:

- **Example**: Python list comprehension to Rust iterator
- **Strategy**: Apply target idioms automatically
- **User action**: Minimal review

```rust
// Level 2-3: Idiomatic transformation
let squares: Vec<i32> = (0..10)
    .map(|x| x * x)
    .collect();
```

#### Runtime Gaps (Max: Level 1-2)

When execution models differ fundamentally:

- **Example**: Python GC to Rust ownership
- **Strategy**: Use runtime abstractions (Rc, Arc) or redesign
- **User action**: Review ownership patterns

```rust
// Level 1-2: Correct with runtime overhead
use std::rc::Rc;
use std::cell::RefCell;

// Cyclic reference requires Rc + RefCell
struct Node {
    value: i32,
    next: Option<Rc<RefCell<Node>>>,
}
```

#### Semantic Gaps (Max: Level 1)

When language semantics differ subtly:

- **Example**: Floating-point NaN comparison
- **Strategy**: Document behavior, preserve source semantics
- **User action**: Understand edge case behavior

```rust
// Level 1: Preserves Python semantics with explicit NaN handling
fn py_float_eq(a: f64, b: f64) -> bool {
    // Python: float('nan') == float('nan') is False
    // Rust: f64::NAN == f64::NAN is also false (IEEE 754)
    // Semantics preserved, but document for clarity
    a == b
}
```

### Gap Resolution Decision Tree

```
Is there a direct target equivalent?
├── Yes -> Level 2-3 achievable (apply idioms)
└── No
    └── Is there a semantic equivalent?
        ├── Yes -> Level 1-2 achievable (structural transform)
        └── No
            └── Can behavior be approximated?
                ├── Yes (with loss) -> Level 1 achievable (emit warnings)
                └── No -> Level 0 only (stub + manual redesign)
```

---

## Appendix: Quick Reference Card

### Level Summary

| Level | Name | Key Guarantee | One-Liner |
|-------|------|---------------|-----------|
| 0 | Syntactically Valid | Compiles | "It builds" |
| 1 | Semantically Equivalent | Correct behavior | "It works" |
| 2 | Idiomatically Correct | Native feel | "It fits" |
| 3 | Optimized | High performance | "It flies" |

### When to Target Each Level

- **Level 0**: Exploration, prototyping, syntax learning
- **Level 1**: Automated migration, compliance, testing
- **Level 2**: Production code, long-term maintenance
- **Level 3**: Performance-critical paths, reference implementations

### Effort Estimation

| Transition | Automated Effort | Manual Effort |
|------------|-----------------|---------------|
| 0 -> 1 | Hours | Hours-Days |
| 1 -> 2 | Hours-Days | Days |
| 2 -> 3 | Days | Days-Weeks |
