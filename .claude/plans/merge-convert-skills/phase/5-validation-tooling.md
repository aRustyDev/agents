# Phase 5: Validation & Tooling (MVP - Python)

Validate IR design and build Python extraction/synthesis prototypes.

## Goal

Validate that the IR schema meets requirements by building a complete Python extraction → synthesis pipeline. This phase establishes patterns and infrastructure that subsequent language phases will follow.

## Dependencies

### Phase 4 Deliverables (Required)

| Deliverable | Location | Usage |
|-------------|----------|-------|
| IR Overview | `docs/src/ir-schema/overview.md` | Architecture reference |
| Layer Specs | `docs/src/ir-schema/layer-*.md` | Extraction implementation guide |
| Annotations | `docs/src/ir-schema/cross-cutting.md` | Annotation assignment logic |
| JSON Schema | `schemas/ir-v1.json` | Output validation |
| SQL Extensions | `data/ir-schema.sql` | Database schema for IR storage |
| Sample IRs | `analysis/ir-validation.md` | 10 validated patterns as fixtures |

### Database (Required)

| Table | Rows | Usage |
|-------|------|-------|
| `ir_patterns` | 6,273 | Extraction test cases |
| `gap_patterns` | 54 | Gap detection rules |
| `languages` | 29 | Language metadata |
| `semantic_gaps` | 320 | Known gaps for validation |
| `decision_points` | 16 | Human decision prompts |

### Project Infrastructure

| Component | Location | Usage |
|-----------|----------|-------|
| Package config | `pyproject.toml` | Dependencies via `uv` |
| Task runner | `justfile` | `just ir-*` commands |
| Linting | `ruff` | Code style enforcement |
| Testing | `pytest` | Test execution |

## Deliverables

- [ ] Semantic equivalence specification
- [ ] Extractor architecture decision (custom vs hybrid)
- [ ] Python extractor producing valid IR
- [ ] Python synthesizer generating valid code
- [ ] IR validation tool
- [ ] Test data in database
- [ ] 30+ test cases
- [ ] Validation report

---

## Semantic Equivalence Levels

Based on research into academic literature, formal verification (CompCert, Isabelle/HOL), and industry practice (Scala.js, ClojureScript, Fable), we define **five levels** of semantic equivalence:

### Level Definitions

| Level | Name | Definition | Verification Method |
|-------|------|------------|---------------------|
| **L1** | Syntactic | Same structure, different syntax; AST isomorphism after normalization | AST comparison |
| **L2** | Operational | Same execution trace; lock-step simulation | Step-wise trace comparison |
| **L3** | Semantic | Same I/O behavior for all inputs; may differ internally | Property-based testing |
| **L4** | Contextual | Same behavior in any program context; accounts for interop | Integration testing |
| **L5** | Idiomatic | Native patterns achieving same functionality | Code review + style linting |

### Level Selection by Conversion Type

| Conversion Type | Target Level | Rationale |
|-----------------|--------------|-----------|
| Same-language refactoring | L1-L2 | Preserve structure for maintainability |
| Cross-language migration | L3-L4 | Ensure correctness + interoperability |
| Legacy modernization | L4-L5 | Maximize target language benefits |
| Performance optimization | L3 | Allow restructuring for efficiency |

### Formal Definitions

**L2 (Operational)** - From Isabelle/HOL:
> For commands `c` and `c'`: `P |= c ~ c'` means for all states `s` and `s'`, if precondition `P` holds and `(c, s)` executes to `s'`, then `(c', s)` also executes to `s'`.

**L3 (Semantic)** - From CompCert:
> "The generated executable code behaves exactly as prescribed by the semantics of the source program."

**L4 (Contextual)** - From PLFA Bisimulation:
> Two terms are contextually equivalent if "every reduction in the source has a corresponding reduction sequence in the target" and vice versa.

### Phase 5 Target

For Python MVP, target **L3 (Semantic) equivalence** for round-trip testing:
- Same I/O behavior verified via property-based testing
- Internal execution may differ (optimization allowed)
- Document any L4/L5 gaps as known limitations

---

## Extractor Architecture Analysis

### Approach Comparison

| Approach | Impl. Complexity | Semantic Richness | Cross-Lang Consistency | Maintenance |
|----------|------------------|-------------------|------------------------|-------------|
| Custom Parsers | 5/5 | 4/5 | 5/5 | 5/5 |
| Tree-sitter Only | 2/5 | 2/5 | 4/5 | 2/5 |
| Compiler APIs | 4/5 | 5/5 | 1/5 | 4/5 |
| LSP | 3/5 | 4/5 | 3/5 | 2/5 |
| **Hybrid (Recommended)** | 3/5 | 4/5 | 4/5 | 3/5 |

### Recommended: Hybrid Tree-sitter + Semantic Enrichment

```
Source Code
    │
    ▼
[Tree-sitter Parser] ──► Concrete Syntax Tree
    │
    ▼
[AST Normalizer] ──► Generic AST (language-agnostic structure)
    │
    ▼
[Semantic Enrichment] ──► Types, bindings, definitions
    │                      (LSP/pyright for Python)
    ▼
[IR Generator] ──► 5-Layer IR (validated against ir-v1.json)
```

### Rationale

1. **Tree-sitter** provides:
   - Consistent API across 165+ languages
   - Fast, incremental, error-tolerant parsing
   - Community-maintained grammars

2. **Semantic enrichment** (per-language) provides:
   - Type information
   - Name resolution
   - Cross-file references

3. **Generic AST layer** enables:
   - Reusable IR generation logic
   - Consistent handling of common constructs
   - Simplified testing

### Python-Specific Implementation

For Python MVP, use:
- **Syntax**: `tree-sitter-python` via `tree-sitter-language-pack`
- **Semantics**: `pyright` (LSP) or direct `ast` + `jedi` for type inference
- **CST**: `LibCST` for round-trip preserving formatting

---

## Error Handling Taxonomy

### Extraction Errors

| Code | Category | Description | Recovery |
|------|----------|-------------|----------|
| `E001` | Parse Error | Syntax error in source | Skip file, report location |
| `E002` | Unsupported Syntax | Valid syntax not yet supported | Mark as gap, continue |
| `E003` | Type Inference Failed | Cannot determine type | Use `Any`, annotate gap |
| `E004` | Cross-File Reference | Reference to external module | Record as dependency |
| `E005` | Macro/Metaprogramming | Dynamic code generation | Mark as impossible gap |

### Synthesis Errors

| Code | Category | Description | Recovery |
|------|----------|-------------|----------|
| `S001` | Missing Type | IR lacks type info for target | Use target's `Any` equivalent |
| `S002` | Impossible Gap | Semantic gap with no mitigation | Skip construct, emit TODO |
| `S003` | Decision Required | Human decision point reached | Prompt or use default |
| `S004` | Idiom Mismatch | No idiomatic translation exists | Use structural translation |
| `S005` | Format Error | Generated code won't format | Return unformatted with warning |

### Validation Errors

| Code | Category | Description | Recovery |
|------|----------|-------------|----------|
| `V001` | Schema Violation | IR doesn't match ir-v1.json | Report violations |
| `V002` | Reference Integrity | Dangling reference in IR | Report broken refs |
| `V003` | Layer Consistency | Cross-layer inconsistency | Report conflict |
| `V004` | Gap Marker Invalid | Gap references unknown pattern | Warn and continue |

---

## Tasks

### 5.0 Test Data Generation

Seed the database with test data before validation.

```sql
-- Insert sample IR units from ir-validation.md patterns
INSERT INTO ir_units (version_id, layer, unit_type, content_hash, content_json)
SELECT ...

-- Verify views work
SELECT * FROM v_preservation_summary LIMIT 5;
SELECT * FROM v_gaps_by_pattern;
SELECT * FROM v_decision_audit;
```

**Deliverable**: `scripts/seed_test_data.py`

**Acceptance**:
- 20+ IR units in database
- All views return expected data
- Gap markers linked to patterns

---

### 5.1 Validation Criteria & Equivalence Specification

Define validation criteria and formalize equivalence levels.

**Deliverable**: `docs/src/validation/equivalence-levels.md`

**Contents**:
- 5-level equivalence taxonomy (as above)
- Verification methods per level
- Examples for each level
- Phase 5 target level justification

**Acceptance**:
- All 5 levels formally defined
- Verification methods specified
- Examples from Python provided

---

### 5.2 Extractor Architecture Decision

Finalize extractor approach with implementation plan.

**Deliverable**: `docs/src/adr/adr-009-extractor-architecture.md`

**Contents**:
- Decision: Hybrid tree-sitter + semantic enrichment
- Alternatives considered
- Per-language implementation strategy
- Generic AST specification

**Acceptance**:
- ADR approved
- Generic AST schema documented
- Python implementation path clear

---

### 5.3 Database Query Interface

Implement SQL query interface for tools.

```python
# tools/ir-query/db.py
class IRDatabase:
    def get_patterns_for_language(self, lang: str) -> list[Pattern]: ...
    def get_gap_patterns(self) -> list[GapPattern]: ...
    def get_decision_points(self) -> list[DecisionPoint]: ...
    def store_ir_unit(self, unit: IRUnit) -> int: ...
    def get_gaps_for_conversion(self, source: str, target: str) -> list[Gap]: ...
```

**Required Queries**:

```sql
-- Patterns by language pair (for test case selection)
SELECT pattern_type, COUNT(*) FROM ir_patterns
WHERE source_lang = ? GROUP BY pattern_type;

-- Gap patterns for detection
SELECT name, category, from_concept, to_concept
FROM gap_patterns WHERE category = ?;

-- Decision points for prompting
SELECT name, description, options, guidance
FROM decision_points WHERE id = ?;
```

**Deliverable**: `tools/ir-query/`

**Acceptance**:
- All query methods implemented
- Tests pass against `convert-skills.db`
- Integrated with IR extraction pipeline

---

### 5.4 Python Extractor Implementation

Build Python source → IR extractor using hybrid approach.

```python
# tools/ir-extract/python/extract.py
class PythonExtractor:
    def extract(self, source: str, path: str) -> IRVersion:
        # 1. Parse with tree-sitter
        tree = self.parser.parse(source.encode())

        # 2. Convert to generic AST
        gast = self.normalize(tree)

        # 3. Enrich with type info (pyright/jedi)
        typed_gast = self.enrich_types(gast, path)

        # 4. Generate IR layers
        ir = self.generate_ir(typed_gast)

        # 5. Validate against schema
        self.validate(ir)

        return ir
```

**Layers to Extract**:
- Layer 4: Module structure, imports, exports, definitions
- Layer 3: Type hints, dataclasses, protocols
- Layer 2: Control flow, effects (try/except), async
- Layer 1: Variable bindings, assignments, closures
- Layer 0: (Optional) Expression AST for debugging

**Deliverable**: `tools/ir-extract/python/`

**Test Fixtures** (from `ir_patterns` where `source_lang = 'python'`):
- Simple functions with type hints
- Classes with methods
- Async/await patterns
- Decorators
- List comprehensions
- Pattern matching (3.10+)

**Acceptance**:
- Extracts 15+ test fixtures to valid IR
- IR validates against `ir-v1.json`
- All 5 layers populated where applicable

---

### 5.5 Python Synthesizer Implementation

Build IR → Python code synthesizer.

```python
# tools/ir-synthesize/python/synthesize.py
class PythonSynthesizer:
    def synthesize(self, ir: IRVersion) -> str:
        # 1. Generate module structure (Layer 4)
        module = self.gen_module(ir.structural)

        # 2. Generate types (Layer 3)
        types = self.gen_types(ir.types)

        # 3. Generate functions (Layer 2)
        functions = self.gen_functions(ir.control_flow)

        # 4. Apply Python idioms
        code = self.apply_idioms(module, types, functions)

        # 5. Format with black
        return self.format(code)
```

**Deliverable**: `tools/ir-synthesize/python/`

**Acceptance**:
- Generates valid Python 3.10+ code
- Code passes `ruff check`
- Type hints included where IR has type info

---

### 5.6 IR Validation Tool

Build tool to validate IR against schema and semantic rules.

```python
# tools/ir-validate/validate.py
class IRValidator:
    def validate(self, ir: IRVersion) -> ValidationResult:
        errors = []

        # Schema validation
        errors += self.validate_schema(ir)

        # Reference integrity
        errors += self.validate_references(ir)

        # Cross-layer consistency
        errors += self.validate_layers(ir)

        # Gap marker validity
        errors += self.validate_gaps(ir)

        return ValidationResult(errors)
```

**Deliverable**: `tools/ir-validate/`

**Acceptance**:
- Validates against `ir-v1.json`
- Detects all error categories (V001-V004)
- Reports actionable error messages

---

### 5.7 Test Suite Development

Build comprehensive test suite for Python tools.

```
tests/
├── unit/
│   ├── test_python_extractor.py
│   ├── test_python_synthesizer.py
│   └── test_ir_validator.py
├── integration/
│   ├── test_python_roundtrip.py
│   └── test_database_queries.py
├── property/
│   └── test_ir_invariants.py
└── fixtures/
    └── python/
        ├── simple_function.py
        ├── typed_class.py
        ├── async_code.py
        └── ... (15+ files)
```

**Property Tests** (using `hypothesis`):

```python
@given(valid_python_functions())
def test_roundtrip_preserves_semantics(source: str):
    ir = extractor.extract(source)
    generated = synthesizer.synthesize(ir)
    assert semantically_equivalent(source, generated, level=3)
```

**Deliverable**: `tests/`

**Acceptance**:
- 30+ test cases
- Unit tests for each component
- Integration tests for round-trip
- Property tests for IR invariants
- Coverage > 80% for core modules

---

### 5.8 Round-Trip Validation

Execute round-trip tests with semantic equivalence verification.

**Test Protocol**:
1. Extract Python source to IR
2. Validate IR against schema
3. Synthesize IR back to Python
4. Verify L3 (Semantic) equivalence via:
   - Parse both versions
   - Execute with test inputs
   - Compare outputs

**Deliverable**:
- `tests/integration/test_python_roundtrip.py`
- `analysis/python-roundtrip-results.md`

**Acceptance**:
- 85%+ round-trip success rate
- All failures documented with root cause
- Gap patterns identified for failures

---

### 5.9 Validation Report

Compile final validation report for Phase 5.

**Template**:

```markdown
# Phase 5 Validation Report: Python MVP

## Summary
- Patterns tested: X/Y (Z%)
- Round-trips passing: A/B
- Equivalence level achieved: L3

## Pattern Coverage

| Category | Total | Covered | Notes |
|----------|-------|---------|-------|
| type_mapping | ... | ... | ... |

## Round-Trip Results

| Test Category | Pass | Fail | Skip |
|---------------|------|------|------|
| Simple functions | ... | ... | ... |

## Known Gaps

| Gap ID | Description | Impact |
|--------|-------------|--------|
| ... | ... | ... |

## Recommendations for Phase 6+
1. ...
```

**Deliverable**: `analysis/phase5-validation-report.md`

**Acceptance**:
- All sections complete
- Quantitative metrics provided
- Clear recommendations for next phases

---

### 5.10 Final Review

Final review of Phase 5 deliverables.

**Checklist**:
- [ ] Equivalence levels documented and formalized
- [ ] Extractor architecture decided (ADR-009)
- [ ] Python extractor producing valid IR
- [ ] Python synthesizer generating valid code
- [ ] IR validation tool working
- [ ] 30+ test cases passing
- [ ] 85%+ round-trip success
- [ ] Validation report complete
- [ ] Infrastructure integrated (`just ir-*` commands)

**Deliverable**: `analysis/phase5-review.md`

**Acceptance**:
- All checklist items complete
- No blocking issues
- Ready for Phase 6 (Rust)

---

## justfile Integration

```justfile
# Phase 5: IR Validation & Tooling
[group('ir')]
ir-extract file language='python':
    uv run python tools/ir-extract/{{language}}/extract.py {{file}}

[group('ir')]
ir-synthesize ir_file language='python':
    uv run python tools/ir-synthesize/{{language}}/synthesize.py {{ir_file}}

[group('ir')]
ir-validate ir_file:
    uv run python tools/ir-validate/validate.py {{ir_file}}

[group('ir')]
ir-roundtrip file language='python':
    uv run python tools/ir-roundtrip.py {{file}} --language {{language}}

[group('ir')]
ir-test:
    uv run pytest tests/ -v --cov=tools

[group('ir')]
ir-seed-db:
    uv run python scripts/seed_test_data.py
```

---

## Success Criteria

- [ ] Equivalence levels (5) formally specified
- [ ] Extractor architecture decided (ADR-009)
- [ ] Python extractor working (15+ fixtures)
- [ ] Python synthesizer working
- [ ] IR validator working
- [ ] 30+ test cases passing
- [ ] 85%+ Python round-trip success
- [ ] Error taxonomy implemented
- [ ] Database queries integrated
- [ ] Validation report complete

## Effort Estimate

10-14 days (reduced from original 7-10 by adding research and infrastructure tasks)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Tree-sitter Python grammar issues | Low | Medium | Fall back to `ast` module |
| Type inference too complex | Medium | Medium | Limit to explicit type hints |
| Round-trip rate below 70% | Medium | High | Reduce test scope, document gaps |
| Pyright integration complexity | Medium | Medium | Use simpler `jedi` instead |

## Output Files

| File | Description |
|------|-------------|
| `docs/src/validation/equivalence-levels.md` | Equivalence taxonomy |
| `docs/src/adr/adr-009-extractor-architecture.md` | Architecture decision |
| `tools/ir-extract/python/` | Python extractor |
| `tools/ir-synthesize/python/` | Python synthesizer |
| `tools/ir-validate/` | IR validation tool |
| `tools/ir-query/` | Database query interface |
| `tests/` | Test suite |
| `analysis/phase5-validation-report.md` | Validation results |
| `analysis/phase5-review.md` | Final review |

---

## Subsequent Phases

Phase 5 establishes patterns for language-specific phases:

| Phase | Language | Priority | Rationale |
|-------|----------|----------|-----------|
| 6 | Rust | High | Systems language, ownership model validation |
| 7 | TypeScript | High | Most patterns as target (933+) |
| 8 | Golang | Medium | Concurrency model, simplicity |
| 9 | Roc | Medium | Pure FP, algebraic effects |
| 10 | Scala | Medium | JVM + FP, HKT validation |

Each subsequent phase follows the same structure:
1. Extractor implementation
2. Synthesizer implementation
3. Test suite
4. Round-trip validation
5. Cross-language testing (with Python)
6. Validation report
