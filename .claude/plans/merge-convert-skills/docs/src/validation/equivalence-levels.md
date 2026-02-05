# Semantic Equivalence Levels Specification

**Version:** 1.0
**Phase:** 5 (Validation & Tooling)
**Task:** 5.1 Validation Criteria & Equivalence Specification
**Date:** 2026-02-05

---

## 1. Executive Summary

This document defines a five-level taxonomy (L1-L5) for measuring semantic equivalence between source code and converted output during language-to-language translation. The taxonomy draws from formal verification research (CompCert, Isabelle/HOL) and industrial practice (Scala.js, ClojureScript, Fable) to establish rigorous, testable definitions.

**Key decisions:**

- **Phase 5 Target:** L3 (Semantic) equivalence for Python MVP
- **Verification Strategy:** Property-based testing with Hypothesis
- **Trade-off:** Internal execution may differ; only observable I/O behavior must match

The taxonomy enables:
1. Objective measurement of conversion quality
2. Clear expectations for developers and users
3. Systematic test generation strategies
4. Informed decisions about conversion fidelity vs. performance

---

## 2. Five-Level Equivalence Taxonomy

### 2.1 Overview

| Level | Name | Definition | Preservation | Typical Use Case |
|-------|------|------------|--------------|------------------|
| **L1** | Syntactic | AST isomorphism after normalization | Structure | Reformatting, linting |
| **L2** | Operational | Lock-step execution traces match | Trace | Debugger-compatible translation |
| **L3** | Semantic | Same I/O behavior for all inputs | I/O | Cross-language migration |
| **L4** | Contextual | Same behavior in any program context | Interop | Library/API conversion |
| **L5** | Idiomatic | Native patterns achieving same functionality | Style | Legacy modernization |

### 2.2 Relationship Between Levels

```
L1 (Syntactic) --> L2 (Operational) --> L3 (Semantic) --> L4 (Contextual) --> L5 (Idiomatic)
      |                  |                   |                   |                  |
  Strictest         Relaxed             Industry            Full              Target
  (AST match)       (trace)            Standard          Interop           Language
                                                                            Native
```

Each level is a strict relaxation of the previous:
- L1 implies L2 implies L3 implies L4 implies L5
- L5 does NOT imply L4 (idiomatic code may differ in edge cases)
- Higher numbers = more relaxed = more practical for cross-language work

---

## 3. Level Definitions

### 3.1 L1: Syntactic Equivalence

**Formal Definition:**

Two programs `P` and `P'` are L1-equivalent if:

```
normalize(AST(P)) = normalize(AST(P'))
```

where `normalize` applies a canonical ordering and removes purely syntactic variations (whitespace, parentheses, comment placement).

**Informal Definition:**

The programs have the same structure after accounting for superficial syntactic differences. This is the strictest level, rarely achievable in cross-language scenarios.

**What is preserved:**
- Control flow structure
- Variable names
- Expression nesting
- Statement ordering

**What may differ:**
- Whitespace and formatting
- Comment positioning
- Redundant parentheses
- Trailing commas/semicolons

**Verification Method:**
- Parse both programs to AST
- Apply normalization passes
- Deep equality comparison

**Formal Reference:**

From program equivalence theory, L1 corresponds to alpha-equivalence extended to full AST structure:

> Two programs are syntactically equivalent iff they differ only in bound variable names and purely syntactic sugar.

---

### 3.2 L2: Operational Equivalence

**Formal Definition (from Isabelle/HOL):**

For commands `c` and `c'`:

```
P |= c ~ c'
```

means: for all states `s` and `s'`, if precondition `P` holds and `(c, s)` executes to `s'`, then `(c', s)` also executes to `s'` in the same number of steps through corresponding intermediate states.

**Informal Definition:**

Both programs execute in lock-step, visiting corresponding states at each step. Useful when debugging compatibility or step-through execution matters.

**What is preserved:**
- Execution order
- Intermediate states
- Step count (within tolerance)
- Control flow branching decisions

**What may differ:**
- Internal variable representations
- Memory layout
- Register allocation

**Verification Method:**
- Instrumented execution (tracing)
- Step-wise trace comparison
- State machine bisimulation checking

**Formal Reference (Isabelle/HOL IMP language):**

```isabelle
lemma equiv_c_c':
  assumes "P s"
  shows "(c, s) => s' <-> (c', s) => s'"
```

This requires the big-step semantics to produce identical final states for any initial state satisfying precondition `P`.

---

### 3.3 L3: Semantic Equivalence

**Formal Definition (from CompCert):**

> "The generated executable code behaves exactly as prescribed by the semantics of the source program."

More precisely, for programs `P` and `P'`:

```
forall input I: observable(run(P, I)) = observable(run(P', I))
```

where `observable` captures all externally visible effects (return values, stdout, file writes, network calls).

**Informal Definition:**

Same black-box behavior. Given any input, both programs produce the same output. Internal execution may differ arbitrarily (different algorithms, optimizations, intermediate values).

**What is preserved:**
- Return values
- Standard output/error
- File system effects
- Network effects
- Exit codes
- Raised exceptions (by type and message)

**What may differ:**
- Execution time
- Memory usage
- Internal variable values
- Execution order (for independent operations)
- Garbage collection timing

**Verification Method:**
- Property-based testing (Hypothesis, QuickCheck)
- Differential testing
- Symbolic execution
- Fuzz testing

**Formal Reference (CompCert):**

From the CompCert verification paper:

```coq
Theorem transf_program_correct:
  forall prog tprog,
  transf_program prog = OK tprog ->
  forward_simulation (Clight.semantics prog) (Asm.semantics tprog).
```

This theorem states that any trace of the compiled program can be matched by a trace of the source program.

---

### 3.4 L4: Contextual Equivalence

**Formal Definition (from PLFA Bisimulation):**

Two terms `M` and `N` are contextually equivalent if:

```
forall C[]: C[M] evaluates to v <=> C[N] evaluates to v
```

where `C[]` is any valid program context (surrounding code that uses the term).

Extended for cross-language:

> "Every reduction in the source has a corresponding reduction sequence in the target" and vice versa, **including when embedded in foreign code**.

**Informal Definition:**

The converted code behaves identically not just in isolation, but when used as a library, API, or component in larger systems. This accounts for FFI, interop, and edge cases exposed by external callers.

**What is preserved:**
- All L3 guarantees
- API contract compatibility
- Exception propagation across boundaries
- Callback behavior
- Thread safety guarantees
- Resource cleanup semantics

**What may differ:**
- Internal performance characteristics
- Memory representations (if not exposed)
- Implementation details hidden behind abstraction

**Verification Method:**
- Integration testing
- Contract testing (Pact, consumer-driven contracts)
- FFI boundary testing
- Interop test suites
- Property-based testing across FFI

**Formal Reference (PLFA):**

From Programming Language Foundations in Agda, bisimulation is defined as:

```agda
record _~_ (M N : Term) : Set where
  field
    to   : M --> M' -> exists N'. N --> N' x M' ~ N'
    from : N --> N' -> exists M'. M --> M' x M' ~ N'
```

This ensures that each step in one term can be matched by corresponding steps in the other, maintaining the bisimulation relation.

---

### 3.5 L5: Idiomatic Equivalence

**Formal Definition:**

Two programs `P` (source) and `P'` (target) are L5-equivalent if:

```
L4(P, P') AND style_lint(P', target_lang) = PASS
```

where `style_lint` checks conformance to target language idioms, conventions, and best practices.

**Informal Definition:**

The converted code not only behaves correctly but looks like it was written by an expert in the target language. Uses native patterns, appropriate data structures, and follows community conventions.

**What is preserved:**
- All L4 guarantees
- Idiomatic style
- Performance patterns
- Community conventions
- Maintainability

**What may differ:**
- Algorithm choice (may use target-native equivalent)
- Data structure choice (may use target-native equivalent)
- Control flow patterns (may use target idioms)
- Error handling style

**Verification Method:**
- Linting tools (ruff, clippy, eslint)
- Human code review
- Style guide conformance checks
- Community acceptance testing
- Readability metrics

**Industry Reference:**

From the Scala.js project:

> "Scala.js aims to be as Scala-like as possible, but generates JavaScript that could have been written by a JavaScript developer."

---

## 4. Verification Methods by Level

### 4.1 Summary Table

| Level | Primary Method | Tools | Automation | Confidence |
|-------|----------------|-------|------------|------------|
| L1 | AST comparison | Tree-sitter, custom parsers | Full | 100% |
| L2 | Trace comparison | Debuggers, instrumentation | Partial | 95%+ |
| L3 | Property-based testing | Hypothesis, QuickCheck | Full | 99%+ (statistical) |
| L4 | Integration testing | pytest, cargo test | High | 90%+ |
| L5 | Code review + linting | ruff, clippy, human review | Partial | Subjective |

### 4.2 L1 Verification Protocol

```python
def verify_l1(source: str, target: str, source_lang: str, target_lang: str) -> bool:
    """Verify L1 (Syntactic) equivalence."""
    # Parse both
    source_ast = parse(source, source_lang)
    target_ast = parse(target, target_lang)

    # Normalize
    source_norm = normalize(source_ast)
    target_norm = normalize(target_ast)

    # Deep comparison
    return ast_equal(source_norm, target_norm)
```

**Applicability:** Same-language transformations only. Cross-language L1 equivalence is rarely meaningful due to fundamental syntax differences.

### 4.3 L2 Verification Protocol

```python
def verify_l2(source: str, target: str, inputs: list[dict]) -> bool:
    """Verify L2 (Operational) equivalence via trace comparison."""
    for input_data in inputs:
        source_trace = trace_execution(source, input_data)
        target_trace = trace_execution(target, input_data)

        if not traces_bisimulate(source_trace, target_trace):
            return False
    return True

def traces_bisimulate(t1: list[State], t2: list[State]) -> bool:
    """Check if traces are bisimilar (lock-step correspondence)."""
    if len(t1) != len(t2):
        return False
    return all(states_correspond(s1, s2) for s1, s2 in zip(t1, t2))
```

**Applicability:** Debugging-sensitive conversions, interpreter implementations.

### 4.4 L3 Verification Protocol

```python
from hypothesis import given, strategies as st

def verify_l3(source: str, target: str, sig: FunctionSignature) -> EquivalenceResult:
    """Verify L3 (Semantic) equivalence via property-based testing."""

    @given(generate_inputs(sig))
    def test_equivalence(inputs):
        source_output = execute_safely(source, inputs)
        target_output = execute_safely(target, inputs)
        assert outputs_equal(source_output, target_output)

    try:
        test_equivalence()
        return EquivalenceResult(passed=True, level=3)
    except AssertionError as e:
        return EquivalenceResult(passed=False, level=3, counterexample=e.args)
```

**Applicability:** All cross-language conversions. Primary method for Phase 5.

### 4.5 L4 Verification Protocol

```python
def verify_l4(source_lib: str, target_lib: str, consumer_tests: list[TestCase]) -> bool:
    """Verify L4 (Contextual) equivalence via integration testing."""
    for test in consumer_tests:
        # Test in isolation
        assert verify_l3(source_lib, target_lib, test.signature)

        # Test with mocked consumers
        for consumer in test.consumers:
            source_result = run_with_consumer(source_lib, consumer)
            target_result = run_with_consumer(target_lib, consumer)
            assert results_equal(source_result, target_result)

    return True
```

**Applicability:** Library and API conversions, FFI-heavy code.

### 4.6 L5 Verification Protocol

```python
def verify_l5(source: str, target: str, target_lang: str) -> IdiomaResult:
    """Verify L5 (Idiomatic) equivalence via linting and review."""

    # First verify L4
    if not verify_l4(source, target):
        return IdiomaResult(passed=False, reason="L4 failed")

    # Run linters
    lint_results = run_linter(target, target_lang)
    if lint_results.errors:
        return IdiomaResult(passed=False, lint_errors=lint_results.errors)

    # Check style metrics
    style_score = compute_style_score(target, target_lang)
    if style_score < IDIOM_THRESHOLD:
        return IdiomaResult(passed=False, style_score=style_score)

    return IdiomaResult(passed=True, style_score=style_score)
```

**Applicability:** Legacy modernization, high-quality production conversions.

---

## 5. Python-Specific Examples

### 5.1 L1 Example: Formatting Differences

**Source (Python):**
```python
def   add(a,b):
    return a+b
```

**Target (Python, reformatted):**
```python
def add(a, b):
    return a + b
```

**Verdict:** L1 equivalent (same AST after normalization)

**Verification:**
```python
>>> normalize(parse("def add(a,b):\n    return a+b"))
>>> normalize(parse("def add(a, b):\n    return a + b"))
# Both produce: FunctionDef(name='add', args=['a', 'b'], body=[Return(BinOp(...))])
```

---

### 5.2 L2 Example: Execution Trace Match

**Source:**
```python
def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result = result * i
    return result
```

**Target:**
```python
def factorial(n):
    result = 1
    i = 1
    while i <= n:
        result = result * i
        i = i + 1
    return result
```

**Verdict:** L2 equivalent (same execution trace for any n)

**Trace for `n=3`:**
```
Source Trace:                    Target Trace:
1. result = 1                    1. result = 1
2. i = 1, result = 1            2. i = 1, result = 1
3. i = 2, result = 2            3. i = 2, result = 2
4. i = 3, result = 6            4. i = 3, result = 6
5. return 6                      5. return 6
```

---

### 5.3 L3 Example: Different Implementation, Same I/O

**Source:**
```python
def is_palindrome(s: str) -> bool:
    """Check if string is palindrome using reversal."""
    return s == s[::-1]
```

**Target:**
```python
def is_palindrome(s: str) -> bool:
    """Check if string is palindrome using two pointers."""
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True
```

**Verdict:** L3 equivalent (same output for all inputs)

**Property-Based Test:**
```python
from hypothesis import given, strategies as st

@given(st.text())
def test_is_palindrome_equivalence(s):
    assert source_is_palindrome(s) == target_is_palindrome(s)
```

**NOT L2 equivalent:** Execution traces differ significantly (one operation vs. loop iterations).

---

### 5.4 L4 Example: Context-Dependent Behavior

**Source:**
```python
class Counter:
    def __init__(self):
        self._count = 0

    def increment(self):
        self._count += 1
        return self._count
```

**Target:**
```python
class Counter:
    def __init__(self):
        self._count = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self._count += 1
            return self._count
```

**Verdict:** L4 equivalent (same behavior including in multi-threaded contexts)

**L3 Test (passes):**
```python
c = Counter()
assert c.increment() == 1
assert c.increment() == 2
```

**L4 Test (verifies thread-safety):**
```python
import threading

def stress_test():
    c = Counter()
    threads = [threading.Thread(target=c.increment) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert c._count == 100  # Only target passes reliably
```

---

### 5.5 L5 Example: Idiomatic Transformation

**Source (non-idiomatic):**
```python
def get_even_squares(numbers):
    result = []
    for n in numbers:
        if n % 2 == 0:
            result.append(n * n)
    return result
```

**Target (idiomatic Python):**
```python
def get_even_squares(numbers: list[int]) -> list[int]:
    return [n * n for n in numbers if n % 2 == 0]
```

**Verdict:** L5 equivalent (idiomatic, passes ruff/pylint, type-hinted)

**Style Verification:**
```bash
$ ruff check target.py
All checks passed!

$ python -c "import target; print(target.get_even_squares([1,2,3,4]))"
[4, 16]
```

---

### 5.6 Negative Examples (Non-Equivalence)

#### Not L3 Equivalent (Different Semantics)

**Source:**
```python
def divide(a: int, b: int) -> float:
    return a / b  # Float division
```

**Target:**
```python
def divide(a: int, b: int) -> int:
    return a // b  # Integer division
```

**Counterexample:** `divide(5, 2)` returns `2.5` in source, `2` in target.

#### Not L4 Equivalent (Context-Dependent Failure)

**Source:**
```python
cache = {}

def memoized_expensive(x):
    if x not in cache:
        cache[x] = expensive_computation(x)
    return cache[x]
```

**Target:**
```python
def memoized_expensive(x):
    return expensive_computation(x)  # No caching
```

**L3 Equivalent:** Same I/O for each call in isolation.

**Not L4:** When embedded in performance-sensitive context, behavior differs (target is slower, may timeout).

---

## 6. Phase 5 Target Level Justification

### 6.1 Decision: L3 (Semantic) Equivalence

For the Python MVP in Phase 5, we target **L3 (Semantic) equivalence**.

### 6.2 Rationale

| Factor | L3 Advantage |
|--------|--------------|
| **Feasibility** | L3 is achievable with automated property-based testing |
| **Practicality** | Most cross-language conversions don't require L2 trace matching |
| **Industry Standard** | CompCert, Scala.js, and similar projects target semantic preservation |
| **Optimization Freedom** | Allows synthesizer to use efficient target patterns |
| **Verification Scalability** | Property-based testing scales to 1000s of test cases |

### 6.3 Why Not L2?

L2 (Operational) equivalence would require:
- Lock-step execution traces
- Matching intermediate states
- No optimization

This is impractical for cross-language work where:
- Loop constructs differ fundamentally
- Variable scoping rules vary
- Optimization is desirable

### 6.4 Why Not L4?

L4 (Contextual) equivalence requires:
- FFI/interop testing
- Multi-threaded context testing
- Consumer-driven contract testing

These are valuable but outside the MVP scope:
- Phase 5 focuses on single-language round-trip (Python -> IR -> Python)
- Interop testing is deferred to cross-language phases (6+)

### 6.5 L4/L5 Gaps to Document

Known scenarios where Phase 5 may achieve L3 but not L4/L5:

| Gap | L3 Status | L4/L5 Impact |
|-----|-----------|--------------|
| Thread safety | Not tested | May fail under concurrency |
| Performance | Ignored | May timeout in production |
| Style | Not verified | May fail code review |
| Pickling/serialization | Not tested | May fail with pickle/json |
| Metaclass behavior | Limited testing | May diverge on introspection |

---

## 7. Testing Strategies by Level

### 7.1 L3 Testing Strategy (Primary for Phase 5)

#### 7.1.1 Property-Based Testing with Hypothesis

```python
from hypothesis import given, strategies as st, settings

@settings(max_examples=1000)
@given(st.integers(), st.integers().filter(lambda x: x != 0))
def test_division_equivalence(a, b):
    """Verify division function equivalence."""
    source_result = execute_source(f"divide({a}, {b})")
    target_result = execute_target(f"divide({a}, {b})")
    assert source_result == target_result
```

#### 7.1.2 Type-Driven Input Generation

```python
def generate_inputs(signature: FunctionSignature) -> st.SearchStrategy:
    """Generate test inputs based on type hints."""
    strategies = {}
    for param in signature.parameters:
        strategies[param.name] = type_to_strategy(param.type)
    return st.fixed_dictionaries(strategies)

def type_to_strategy(type_hint: str) -> st.SearchStrategy:
    """Map type hints to Hypothesis strategies."""
    mapping = {
        "int": st.integers(),
        "str": st.text(max_size=100),
        "float": st.floats(allow_nan=False),
        "bool": st.booleans(),
        "list[int]": st.lists(st.integers()),
        "dict[str, int]": st.dictionaries(st.text(), st.integers()),
        "Optional[int]": st.none() | st.integers(),
    }
    return mapping.get(type_hint, st.nothing())
```

#### 7.1.3 Execution Sandbox

```python
import subprocess
import tempfile
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    return_value: any
    stdout: str
    stderr: str
    exception: str | None
    timeout: bool

def execute_safely(code: str, inputs: dict, timeout: float = 5.0) -> ExecutionResult:
    """Execute code in isolated subprocess with timeout."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        # Wrap code with input injection and output capture
        wrapped = f'''
import json
inputs = {json.dumps(inputs)}
{code}
result = main(**inputs)
print(json.dumps({{"result": result}}))
'''
        f.write(wrapped)
        f.flush()

        try:
            result = subprocess.run(
                ['python', f.name],
                capture_output=True,
                timeout=timeout,
                text=True
            )
            output = json.loads(result.stdout)
            return ExecutionResult(
                return_value=output['result'],
                stdout=result.stdout,
                stderr=result.stderr,
                exception=None,
                timeout=False
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(None, "", "", None, timeout=True)
        except Exception as e:
            return ExecutionResult(None, "", "", str(e), timeout=False)
```

### 7.2 L4 Testing Strategy (Post-MVP)

#### 7.2.1 Integration Test Framework

```python
@pytest.fixture
def library_under_test():
    """Load converted library for integration testing."""
    return import_module("converted_library")

def test_integration_with_consumer(library_under_test):
    """Test library in realistic consumer context."""
    consumer = MockConsumer(library_under_test)
    result = consumer.perform_complex_operation()
    assert result.is_valid()
```

#### 7.2.2 FFI Boundary Testing

```python
def test_ffi_callback_propagation():
    """Verify callbacks work correctly across FFI boundary."""
    results = []

    def callback(value):
        results.append(value)

    source_lib.register_callback(callback)
    source_lib.trigger_events()
    source_results = list(results)
    results.clear()

    target_lib.register_callback(callback)
    target_lib.trigger_events()
    target_results = list(results)

    assert source_results == target_results
```

### 7.3 L5 Testing Strategy

#### 7.3.1 Linting Integration

```python
def verify_idiomatic(code: str, language: str) -> LintResult:
    """Verify code follows target language idioms."""
    if language == "python":
        result = subprocess.run(
            ["ruff", "check", "--select=ALL", "-"],
            input=code,
            capture_output=True,
            text=True
        )
        return LintResult(
            passed=result.returncode == 0,
            issues=parse_ruff_output(result.stdout)
        )
```

#### 7.3.2 Style Metrics

```python
def compute_style_score(code: str) -> float:
    """Compute idiomatic style score (0.0 - 1.0)."""
    metrics = {
        "uses_list_comprehensions": check_list_comprehensions(code),
        "uses_type_hints": check_type_hints(code),
        "uses_context_managers": check_context_managers(code),
        "follows_pep8": check_pep8(code),
        "uses_dataclasses": check_dataclasses(code),
    }
    return sum(metrics.values()) / len(metrics)
```

---

## 8. Known Limitations

### 8.1 Fundamental Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Undecidability** | Cannot prove equivalence for all programs (Rice's theorem) | Use testing, not proof |
| **Side effects** | I/O, network, filesystem effects hard to isolate | Mock external dependencies |
| **Non-determinism** | Random, threading, timing-dependent code | Control via seeding, isolation |
| **Resource limits** | Memory, time limits affect execution | Set reasonable bounds |

### 8.2 Python-Specific Limitations

| Feature | L3 Testability | Notes |
|---------|----------------|-------|
| `eval`/`exec` | Low | Dynamic code execution hard to test |
| Metaclasses | Medium | Introspection may reveal differences |
| C extensions | Low | Cannot verify native code equivalence |
| Generators | Medium | Lazy evaluation complicates comparison |
| Decorators with side effects | Low | May affect global state |
| `__slots__` | Medium | Memory layout differences |

### 8.3 Testing Limitations

| Limitation | Description | Mitigation |
|------------|-------------|------------|
| **Finite testing** | Cannot test all inputs | Use property-based testing for coverage |
| **Oracle problem** | Need ground truth for comparison | Use source as oracle |
| **State explosion** | Stateful code has many paths | Focus on common paths |
| **Flaky tests** | Non-determinism causes failures | Retry with controlled seeds |

### 8.4 Scope Limitations for Phase 5

| Out of Scope | Reason | Future Phase |
|--------------|--------|--------------|
| Cross-language L4 | Requires FFI testing | Phase 6+ |
| Multi-file analysis | Complexity | Phase 5.5 (package mode) |
| Performance equivalence | Orthogonal concern | Separate benchmarking phase |
| Security equivalence | Specialized analysis | Security audit phase |

---

## 9. Appendices

### A. Formal Verification References

#### A.1 CompCert

Leroy, X. (2009). "Formal verification of a realistic compiler." *Communications of the ACM*, 52(7), 107-115.

Key insight: Forward simulation between source and target semantics is sufficient to prove semantic preservation.

#### A.2 Isabelle/HOL

Nipkow, T., & Klein, G. (2014). *Concrete Semantics with Isabelle/HOL*. Springer.

Key insight: Operational equivalence can be expressed as bisimulation between abstract machines.

#### A.3 PLFA (Programming Language Foundations in Agda)

Wadler, P., & Kokke, W. (2019). *Programming Language Foundations in Agda*.

Key insight: Contextual equivalence is the gold standard but requires reasoning about all possible contexts.

### B. Industry Practice References

| Project | Equivalence Target | Verification Method |
|---------|-------------------|---------------------|
| Scala.js | L3-L4 | Test suite compatibility |
| ClojureScript | L3 | Property-based testing |
| Fable (F# -> JS) | L3-L4 | F# test suite on JS output |
| GraalVM Native | L3-L4 | Differential testing |
| Emscripten | L3 | Test suite compatibility |

### C. Equivalence Decision Matrix

Use this matrix to determine the appropriate equivalence level:

| Conversion Scenario | Recommended Level | Verification Effort |
|--------------------|-------------------|---------------------|
| Code formatting | L1 | AST comparison |
| Interpreter implementation | L2 | Trace comparison |
| Algorithm port | L3 | Property-based testing |
| Library migration | L4 | Integration testing |
| Legacy modernization | L5 | Full review |
| Performance optimization | L3 | Testing + benchmarks |
| Security-critical | L4 + audit | Manual + automated |

---

## 10. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-05 | Phase 5 Team | Initial specification |

---

*This document is a Phase 5 deliverable for task 5.1 (Validation Criteria & Equivalence Specification).*
