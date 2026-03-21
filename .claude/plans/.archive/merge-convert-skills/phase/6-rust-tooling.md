# Phase 6: Rust Extractor & Synthesizer

Implement Rust language support for the IR extraction/synthesis pipeline.

## Goal

Build Rust extractor and synthesizer using the patterns established in Phase 5, with special attention to ownership, lifetimes, and the borrow checker.

## Dependencies

- **Phase 5**: Python MVP (patterns, infrastructure, equivalence levels)
- **Phase 4**: IR Schema (ownership annotations, lifetime tracking)

### Phase 5 Deliverables (Required)

| Deliverable | Usage |
|-------------|-------|
| `tools/ir-extract/core/` | Base extractor infrastructure |
| `tools/ir-synthesize/core/` | Base synthesizer infrastructure |
| `tools/ir-validate/` | IR validation tool |
| `tools/ir-query/` | Database query interface |
| `docs/src/adr/adr-009-extractor-architecture.md` | Architecture guidance |
| `docs/src/validation/equivalence-levels.md` | Equivalence definitions |

### Rust-Specific IR Requirements

From `docs/src/ir-schema/layer-1.md` (Data Flow IR):
- Ownership tracking (`Owned`, `Borrowed`, `MutBorrowed`)
- Lifetime annotations (`'a`, `'static`, elided)
- Move vs copy semantics
- Borrow checker constraints

From `docs/src/ir-schema/cross-cutting.md`:
- Annotation kinds: `MM-002` (GC→Ownership), `MM-009` (Copy vs Move), `MM-010` (Lifetimes), `MM-011` (Borrowing)

## Deliverables

- [ ] Rust extractor with ownership/lifetime extraction
- [ ] Rust synthesizer with borrow-checker-valid output
- [ ] Cross-language tests (Python ↔ Rust)
- [ ] 30+ Rust-specific test cases
- [ ] Validation report

---

## Rust-Specific Challenges

### Ownership Model Extraction

```rust
// Source: Must extract ownership semantics
fn process(data: Vec<i32>) -> Vec<i32> {  // Takes ownership
    data.into_iter().map(|x| x * 2).collect()
}

fn view(data: &[i32]) -> i32 {  // Borrows immutably
    data.iter().sum()
}

fn modify(data: &mut Vec<i32>) {  // Borrows mutably
    data.push(42);
}
```

**IR Representation**:

```yaml
function:
  name: process
  parameters:
    - name: data
      type: Vec<i32>
      ownership: owned  # Takes ownership
  return_type: Vec<i32>
  annotations:
    - kind: MM-009
      value: { semantics: move }
```

### Lifetime Extraction

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

**IR Representation**:

```yaml
function:
  name: longest
  lifetime_params: ['a]
  parameters:
    - name: x
      type: "&'a str"
      ownership: borrowed
      lifetime: 'a
    - name: y
      type: "&'a str"
      ownership: borrowed
      lifetime: 'a
  return_type: "&'a str"
  annotations:
    - kind: MM-010
      value: { lifetime: 'a, constraint: "return bound to inputs" }
```

---

## Tasks

### 6.1 Rust Extractor Implementation

Build Rust source → IR extractor.

**Implementation Approach**:
- **Syntax**: `tree-sitter-rust` for parsing
- **Semantics**: `rust-analyzer` (via LSP) for type information
- **Alternative**: `syn` crate for Rust-native parsing (if tree-sitter insufficient)

```python
# tools/ir-extract/rust/extract.py
class RustExtractor:
    def extract(self, source: str, path: str) -> IRVersion:
        # 1. Parse with tree-sitter-rust
        tree = self.parser.parse(source.encode())

        # 2. Extract ownership information
        ownership_info = self.analyze_ownership(tree)

        # 3. Extract lifetime annotations
        lifetimes = self.extract_lifetimes(tree)

        # 4. Enrich with rust-analyzer (types, trait impls)
        enriched = self.enrich_with_ra(tree, path)

        # 5. Generate IR with ownership annotations
        ir = self.generate_ir(enriched, ownership_info, lifetimes)

        return ir
```

**Layers to Extract**:
- Layer 4: Modules, use statements, visibility (pub/pub(crate)/private)
- Layer 3: Structs, enums, traits, impl blocks, generics with bounds
- Layer 2: Functions, control flow, Result/Option handling, async
- Layer 1: Ownership, borrowing, lifetimes, move semantics
- Layer 0: (Optional) Full AST for macro expansion tracking

**Deliverable**: `tools/ir-extract/rust/`

**Acceptance**:
- Extracts 20+ Rust fixtures to valid IR
- Ownership semantics preserved in annotations
- Lifetime relationships captured

---

### 6.2 Rust Synthesizer Implementation

Build IR → Rust code synthesizer.

**Key Challenges**:
1. Generate borrow-checker-valid code
2. Insert appropriate lifetime annotations
3. Choose between `&`, `&mut`, and owned appropriately
4. Handle Result/Option patterns

```python
# tools/ir-synthesize/rust/synthesize.py
class RustSynthesizer:
    def synthesize(self, ir: IRVersion) -> str:
        # 1. Analyze ownership requirements
        ownership_plan = self.plan_ownership(ir)

        # 2. Infer required lifetimes
        lifetimes = self.infer_lifetimes(ir, ownership_plan)

        # 3. Generate module structure
        module = self.gen_module(ir.structural)

        # 4. Generate types with derives
        types = self.gen_types(ir.types, ownership_plan)

        # 5. Generate functions with borrows
        functions = self.gen_functions(ir.control_flow, ownership_plan, lifetimes)

        # 6. Format with rustfmt
        return self.format(module + types + functions)
```

**Ownership Decision Logic**:

```python
def choose_ownership(self, param: IRParameter, usage: UsageAnalysis) -> str:
    if usage.is_consumed:
        return "owned"  # T
    elif usage.is_mutated:
        return "mut_borrowed"  # &mut T
    else:
        return "borrowed"  # &T
```

**Deliverable**: `tools/ir-synthesize/rust/`

**Acceptance**:
- Generates valid Rust code that compiles
- Borrow checker passes without errors
- Uses idiomatic Rust patterns (Result, Option, iterators)

---

### 6.3 Cross-Language Testing (Python ↔ Rust)

Test conversions between Python and Rust.

**Test Matrix**:

| Direction | Expected Success | Key Gaps |
|-----------|------------------|----------|
| Python → Rust | 70%+ | Ownership, typing |
| Rust → Python | 85%+ | Ownership info lost |

**Test Cases**:

```python
# tests/integration/test_python_rust.py

def test_python_to_rust_simple_function():
    """Python function → Rust with inferred types."""
    python_source = '''
def add(a: int, b: int) -> int:
    return a + b
'''
    ir = python_extractor.extract(python_source)
    rust_code = rust_synthesizer.synthesize(ir)

    assert "fn add(a: i32, b: i32) -> i32" in rust_code
    assert compiles_rust(rust_code)

def test_rust_to_python_ownership():
    """Rust ownership → Python (ownership lost, but functional)."""
    rust_source = '''
fn process(data: Vec<i32>) -> Vec<i32> {
    data.into_iter().map(|x| x * 2).collect()
}
'''
    ir = rust_extractor.extract(rust_source)
    python_code = python_synthesizer.synthesize(ir)

    # Ownership is lost but behavior preserved
    assert "def process(data: list[int]) -> list[int]" in python_code
```

**Deliverable**: `tests/integration/test_python_rust.py`

**Acceptance**:
- Python → Rust: 70%+ success
- Rust → Python: 85%+ success
- All gaps documented with pattern IDs

---

### 6.4 Rust Test Suite

Build comprehensive Rust-specific tests.

**Test Categories**:

```
tests/fixtures/rust/
├── ownership/
│   ├── move_semantics.rs
│   ├── borrowing.rs
│   ├── lifetimes.rs
│   └── interior_mutability.rs
├── types/
│   ├── structs.rs
│   ├── enums.rs
│   ├── traits.rs
│   └── generics.rs
├── control_flow/
│   ├── pattern_matching.rs
│   ├── result_option.rs
│   └── async_await.rs
└── modules/
    ├── visibility.rs
    └── use_statements.rs
```

**Deliverable**: `tests/fixtures/rust/` + `tests/unit/test_rust_*.py`

**Acceptance**:
- 30+ Rust test fixtures
- Unit tests for extractor and synthesizer
- Property tests for ownership preservation

---

### 6.5 Validation Report

Compile Rust-specific validation report.

**Template**:

```markdown
# Phase 6 Validation Report: Rust

## Summary
- Rust fixtures tested: X
- Round-trip success: Y%
- Cross-language (Python↔Rust): Z%

## Ownership Model Coverage

| Pattern | Extracted | Synthesized | Notes |
|---------|-----------|-------------|-------|
| Owned values | ✓ | ✓ | |
| Immutable borrows | ✓ | ✓ | |
| Mutable borrows | ✓ | ✓ | |
| Lifetimes (explicit) | ✓ | Partial | Elision preferred |
| Lifetimes (elided) | ✓ | ✓ | |

## Known Gaps

| Gap ID | Description | Impact |
|--------|-------------|--------|
| MM-002 | GC→Ownership conversion | Requires decision point |
| ... | ... | ... |
```

**Deliverable**: `analysis/phase6-validation-report.md`

---

### 6.6 Final Review

Final review of Phase 6 deliverables.

**Checklist**:
- [ ] Rust extractor handles ownership/lifetimes
- [ ] Rust synthesizer generates borrow-checker-valid code
- [ ] 30+ Rust test cases passing
- [ ] Python ↔ Rust cross-language tests passing
- [ ] Validation report complete

**Deliverable**: `analysis/phase6-review.md`

---

## Success Criteria

- [ ] Rust extractor working (20+ fixtures)
- [ ] Rust synthesizer producing compilable code
- [ ] Ownership semantics preserved in IR
- [ ] Lifetime annotations extracted and synthesized
- [ ] 70%+ Python → Rust success
- [ ] 85%+ Rust → Python success
- [ ] 30+ test cases passing

## Effort Estimate

7-10 days

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| rust-analyzer integration complex | Medium | High | Use syn crate as fallback |
| Lifetime inference too hard | High | Medium | Focus on explicit lifetimes only |
| Borrow checker violations in output | Medium | High | Conservative ownership choices |

## Output Files

| File | Description |
|------|-------------|
| `tools/ir-extract/rust/` | Rust extractor |
| `tools/ir-synthesize/rust/` | Rust synthesizer |
| `tests/fixtures/rust/` | Rust test fixtures |
| `tests/integration/test_python_rust.py` | Cross-language tests |
| `analysis/phase6-validation-report.md` | Validation results |
