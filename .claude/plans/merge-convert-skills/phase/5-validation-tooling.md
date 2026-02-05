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
- [ ] Extractor architecture decision (ADR-009)
- [ ] **Core infrastructure** (base classes for Phase 6+ reuse)
- [ ] Python extractor producing valid IR
- [ ] Python synthesizer generating valid code
- [ ] IR validation tool
- [ ] Test data in database
- [ ] 30+ test cases
- [ ] Validation report

## Python Version Compatibility

| Context | Version | Notes |
|---------|---------|-------|
| Source (input) | Python 3.8+ | Must handle older codebases |
| Target (output) | Python 3.10+ | Can use pattern matching, walrus operator |
| Tooling runtime | Python 3.11+ | For `tomllib`, performance, typing features |

**Compatibility handling**: When extracting 3.8 source that uses constructs unavailable in 3.10+ (rare), emit warning but continue.

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
- **Semantics**: See decision criteria below
- **Formatting**: `black` for clean output (default), `LibCST` for comment preservation

#### Semantic Enrichment Decision (Pyright vs Jedi)

| Criterion | Use Pyright | Use Jedi |
|-----------|-------------|----------|
| Project has `py.typed` marker | ✓ | |
| Type stubs available | ✓ | |
| Need cross-file type resolution | ✓ | |
| Simple single-file extraction | | ✓ |
| No LSP setup available | | ✓ |
| Performance critical (many files) | | ✓ |

**Default**: Start with `jedi` for simplicity. Upgrade to `pyright` when cross-file analysis is needed.

**Fallback chain**: `pyright` → `jedi` → `typing.Any` with E003 annotation.

#### Formatting Strategy

| Use Case | Tool | When |
|----------|------|------|
| Clean conversion output | `black` | Default for all synthesis |
| Refactoring (preserve comments) | `LibCST` | When `--preserve-formatting` flag set |
| Round-trip testing | `black` | Normalize both sides before comparison |

---

## Cross-File Analysis Strategy

Python imports create cross-file dependencies. The extractor must handle these gracefully.

### Module Resolution Approach

```
Source File
    │
    ▼
[Import Parser] ──► List of imports (absolute, relative, from...import)
    │
    ▼
[Module Resolver] ──► Resolved paths or "external" markers
    │                  - Local: resolve to file path
    │                  - Stdlib: mark as stdlib
    │                  - Third-party: mark as external
    ▼
[Dependency Graph] ──► DAG of module dependencies
    │
    ▼
[Extraction Order] ──► Topological sort for extraction sequence
```

### Resolution Rules

| Import Type | Resolution | IR Representation |
|-------------|------------|-------------------|
| `import foo` (local) | Find `foo.py` or `foo/__init__.py` | Full extraction if in scope |
| `import foo` (stdlib) | Mark as `stdlib:foo` | Reference only, no extraction |
| `import foo` (third-party) | Mark as `external:foo` | Reference only, use type stubs if available |
| `from . import bar` | Resolve relative to package | Full extraction |
| `from typing import X` | Mark as `stdlib:typing` | Type reference only |

### Extraction Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| `single` | Extract one file, imports as references | Quick testing, simple scripts |
| `package` | Extract all files in package | Library/application conversion |
| `project` | Extract with dependency graph | Full project migration |

**Phase 5 MVP**: Implement `single` mode fully, `package` mode basic support.

### Handling Unresolved Imports

When an import cannot be resolved:
1. Log warning with E004 error code
2. Create placeholder type reference: `external:<module>.<name>`
3. Continue extraction
4. Include unresolved imports in IR metadata for downstream handling

---

## Semantic Equivalence Verification

### L3 (Semantic) Verification Protocol

For Phase 5 MVP, L3 equivalence means: **same observable I/O behavior**.

```python
# tools/ir-validate/semantic_equiv.py

def verify_l3_equivalence(
    original: str,
    generated: str,
    test_inputs: list[dict],
    timeout_seconds: float = 5.0
) -> EquivalenceResult:
    """
    Verify L3 semantic equivalence between original and generated code.

    Returns:
        EquivalenceResult with pass/fail status and details
    """
    results = []

    for inputs in test_inputs:
        # Execute original
        orig_output = execute_safely(original, inputs, timeout_seconds)

        # Execute generated
        gen_output = execute_safely(generated, inputs, timeout_seconds)

        # Compare outputs
        results.append(compare_outputs(orig_output, gen_output))

    return EquivalenceResult(
        passed=all(r.matches for r in results),
        details=results
    )
```

### Test Input Generation

Use `hypothesis` to generate test inputs:

```python
from hypothesis import given, strategies as st

# Strategy for function under test
@st.composite
def function_inputs(draw, signature: FunctionSignature):
    """Generate valid inputs based on function type hints."""
    args = {}
    for param in signature.parameters:
        if param.type == "int":
            args[param.name] = draw(st.integers())
        elif param.type == "str":
            args[param.name] = draw(st.text(max_size=100))
        elif param.type == "list[int]":
            args[param.name] = draw(st.lists(st.integers()))
        # ... extend for other types
    return args
```

### Execution Sandbox

Execute code safely using `RestrictedPython` or subprocess isolation:

```python
def execute_safely(code: str, inputs: dict, timeout: float) -> ExecutionResult:
    """Execute code in isolated subprocess with timeout."""
    # Write code to temp file
    # Execute via subprocess with resource limits
    # Capture stdout, stderr, return value
    # Handle timeout and exceptions
    ...
```

### What L3 Equivalence Checks

| Aspect | Checked | Not Checked |
|--------|---------|-------------|
| Return values | ✓ | |
| Stdout output | ✓ | |
| Side effects (files, network) | ✓ (via mocking) | |
| Execution time | | ✓ (allowed to differ) |
| Memory usage | | ✓ |
| Internal variable names | | ✓ |
| Code structure | | ✓ |
| Comments | | ✓ |

### Equivalence Test Categories

| Category | Input Strategy | Expected Coverage |
|----------|----------------|-------------------|
| Pure functions | Random inputs via hypothesis | 95%+ |
| I/O functions | Mocked I/O, predefined scenarios | 80%+ |
| Stateful classes | Sequence of method calls | 75%+ |
| Async functions | Event loop with timeouts | 70%+ |
| Decorators | Decorated function behavior | 85%+ |

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

### 5.3 Core Infrastructure

Create reusable base infrastructure that Phase 6+ will extend.

```python
# tools/ir-core/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol

class Extractor(ABC):
    """Base class for language-specific extractors."""

    @abstractmethod
    def extract(self, source: str, path: str, config: ExtractConfig) -> IRVersion:
        """Extract IR from source code."""
        ...

    @abstractmethod
    def supported_features(self) -> set[str]:
        """Return set of supported language features."""
        ...

class Synthesizer(ABC):
    """Base class for language-specific synthesizers."""

    @abstractmethod
    def synthesize(self, ir: IRVersion, config: SynthConfig) -> str:
        """Generate code from IR."""
        ...

@dataclass
class ExtractConfig:
    """Configuration for extraction."""
    depth: Literal["minimal", "standard", "full"] = "standard"
    resolve_imports: bool = True
    include_comments: bool = False
    type_inference: Literal["none", "jedi", "pyright"] = "jedi"

@dataclass
class SynthConfig:
    """Configuration for synthesis."""
    target_version: str = "3.10"
    format_style: Literal["black", "preserve"] = "black"
    include_type_hints: bool = True
```

**Core Components**:

| Component | Location | Purpose |
|-----------|----------|---------|
| `Extractor` base | `tools/ir-core/base.py` | Abstract extractor interface |
| `Synthesizer` base | `tools/ir-core/base.py` | Abstract synthesizer interface |
| `IRVersion` model | `tools/ir-core/models.py` | IR data structures |
| `TreeSitterAdapter` | `tools/ir-core/treesitter.py` | Shared tree-sitter integration |
| `SchemaValidator` | `tools/ir-core/validation.py` | JSON schema validation |
| `GapDetector` | `tools/ir-core/gaps.py` | Gap pattern matching |

**Deliverable**: `tools/ir-core/`

**Acceptance**:
- Base classes documented with docstrings
- Type hints throughout
- Unit tests for shared utilities
- Phase 6 (Rust) can import and extend without modification

---

### 5.4 Database Query Interface

Implement SQL query interface for tools.

```python
# tools/ir-query/db.py
class IRDatabase:
    """Query interface for convert-skills database."""

    def __init__(self, db_path: str = "data/convert-skills.db"):
        self.conn = sqlite3.connect(db_path)
        self._cache: dict[str, Any] = {}

    # Pattern queries (cached, 6273 rows)
    def get_patterns_for_language(
        self, lang: str, limit: int = 100, offset: int = 0
    ) -> list[Pattern]:
        """Get patterns with pagination for memory efficiency."""
        ...

    def get_patterns_by_type(
        self, pattern_type: str, source_lang: str | None = None
    ) -> list[Pattern]:
        """Get patterns filtered by type."""
        ...

    # Gap queries (54 patterns, cacheable)
    def get_gap_patterns(self, category: str | None = None) -> list[GapPattern]:
        """Get gap patterns, optionally filtered by category."""
        ...

    def get_gaps_for_conversion(
        self, source: str, target: str
    ) -> list[SemanticGap]:
        """Get known gaps for a language pair."""
        ...

    # Decision points (16 rows, cached on init)
    def get_decision_points(self) -> list[DecisionPoint]:
        """Get all decision points (cached)."""
        ...

    def get_decision_point(self, dp_id: str) -> DecisionPoint | None:
        """Get specific decision point by ID."""
        ...

    # IR storage
    def store_ir_unit(self, unit: IRUnit) -> int:
        """Store extracted IR unit, return ID."""
        ...

    def get_ir_unit(self, unit_id: int) -> IRUnit | None:
        """Retrieve stored IR unit."""
        ...
```

**Required Queries**:

```sql
-- Patterns by language pair (for test case selection)
SELECT pattern_type, COUNT(*) FROM ir_patterns
WHERE source_lang = ? GROUP BY pattern_type;

-- Gap patterns for detection (with join to get full info)
SELECT gp.id, gp.name, gp.category, gp.from_concept, gp.to_concept,
       gp.severity, gp.description
FROM gap_patterns gp
WHERE gp.category = ? OR ? IS NULL;

-- Decision points for prompting
SELECT id, name, description, options, guidance
FROM decision_points WHERE id = ?;

-- Batch pattern retrieval with pagination
SELECT * FROM ir_patterns
WHERE source_lang = ?
ORDER BY id
LIMIT ? OFFSET ?;
```

**Performance Considerations**:
- Cache `gap_patterns` and `decision_points` on initialization (small tables)
- Use pagination for `ir_patterns` queries (6,273 rows)
- Connection pooling for concurrent access
- Prepared statements for repeated queries

**Deliverable**: `tools/ir-query/`

**Acceptance**:
- All query methods implemented with type hints
- Pagination for large result sets
- Caching strategy documented
- Tests pass against `convert-skills.db`
- Integrated with extractor pipeline via dependency injection

---

### 5.5 Python Extractor Implementation

Build Python source → IR extractor using hybrid approach, extending core infrastructure.

```python
# tools/ir-extract/python/extract.py
from tools.ir_core.base import Extractor, ExtractConfig
from tools.ir_core.treesitter import TreeSitterAdapter

class PythonExtractor(Extractor):
    """Python-specific extractor using tree-sitter + jedi/pyright."""

    def __init__(self, db: IRDatabase):
        self.db = db
        self.parser = TreeSitterAdapter("python")
        self.gap_patterns = db.get_gap_patterns()

    def extract(self, source: str, path: str, config: ExtractConfig) -> IRVersion:
        # 1. Parse with tree-sitter
        tree = self.parser.parse(source.encode())

        # 2. Convert to generic AST
        gast = self.normalize(tree)

        # 3. Resolve imports (if enabled)
        if config.resolve_imports:
            imports = self.resolve_imports(gast, path)
            gast = self.annotate_imports(gast, imports)

        # 4. Enrich with type info (based on config)
        typed_gast = self.enrich_types(gast, path, config.type_inference)

        # 5. Generate IR layers (based on depth)
        ir = self.generate_ir(typed_gast, config.depth)

        # 6. Detect gaps
        ir = self.detect_gaps(ir, self.gap_patterns)

        # 7. Validate against schema
        self.validate(ir)

        return ir

    def supported_features(self) -> set[str]:
        return {
            "functions", "classes", "async", "decorators",
            "comprehensions", "pattern_matching", "type_hints",
            "dataclasses", "protocols"
        }
```

**Extraction Depth Configuration**:

| Depth | Layers | Use Case |
|-------|--------|----------|
| `minimal` | 2-4 only | Quick structural analysis |
| `standard` | 1-4 | Normal conversion (default) |
| `full` | 0-4 | Debugging, detailed analysis |

**Layers to Extract**:
- Layer 4: Module structure, imports, exports, definitions
- Layer 3: Type hints, dataclasses, protocols
- Layer 2: Control flow, effects (try/except), async
- Layer 1: Variable bindings, assignments, closures
- Layer 0: Expression AST for debugging (only with `depth=full`)

**Deliverable**: `tools/ir-extract/python/`

**Test Fixtures** (from `ir_patterns` where `source_lang = 'python'`):
- Simple functions with type hints
- Classes with methods
- Async/await patterns
- Decorators
- List comprehensions
- Pattern matching (3.10+)

**Acceptance**:
- Extends `Extractor` base class from `ir-core`
- Extracts 15+ test fixtures to valid IR
- IR validates against `ir-v1.json`
- All configured layers populated
- Gap detection integrated

---

### 5.6 Python Synthesizer Implementation

Build IR → Python code synthesizer, extending core infrastructure.

```python
# tools/ir-synthesize/python/synthesize.py
from tools.ir_core.base import Synthesizer, SynthConfig

class PythonSynthesizer(Synthesizer):
    """Python-specific synthesizer generating Python 3.10+ code."""

    def synthesize(self, ir: IRVersion, config: SynthConfig) -> str:
        # 1. Generate module structure (Layer 4)
        module = self.gen_module(ir.structural)

        # 2. Generate types (Layer 3)
        types = self.gen_types(ir.types, include_hints=config.include_type_hints)

        # 3. Generate functions (Layer 2)
        functions = self.gen_functions(ir.control_flow)

        # 4. Apply Python idioms
        code = self.apply_idioms(module, types, functions)

        # 5. Format based on config
        if config.format_style == "black":
            return self.format_with_black(code)
        else:
            return code  # preserve as-is
```

**Deliverable**: `tools/ir-synthesize/python/`

**Acceptance**:
- Extends `Synthesizer` base class from `ir-core`
- Generates valid Python 3.10+ code
- Code passes `ruff check`
- Type hints included where IR has type info
- Configurable formatting (black vs preserve)

---

### 5.7 IR Validation Tool

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

### 5.8 Test Suite Development

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

### 5.9 Round-Trip Validation

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

### 5.10 Validation Report

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

### 5.11 Final Review

Final review of Phase 5 deliverables.

**Checklist**:
- [ ] Equivalence levels documented and formalized (5.1)
- [ ] Extractor architecture decided (ADR-009) (5.2)
- [ ] Core infrastructure reusable by Phase 6+ (5.3)
- [ ] Database query interface working (5.4)
- [ ] Python extractor producing valid IR (5.5)
- [ ] Python synthesizer generating valid code (5.6)
- [ ] IR validation tool working (5.7)
- [ ] 30+ test cases passing (5.8)
- [ ] 85%+ round-trip success (5.9)
- [ ] Validation report complete (5.10)
- [ ] Performance targets met
- [ ] Infrastructure integrated (`just ir-*` commands)

**Deliverable**: `analysis/phase5-review.md`

**Acceptance**:
- All checklist items complete
- No blocking issues
- Core infrastructure approved for Phase 6 use
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

### Functional Requirements

- [ ] Equivalence levels (5) formally specified
- [ ] Extractor architecture decided (ADR-009)
- [ ] Core infrastructure usable by Phase 6+
- [ ] Python extractor working (15+ fixtures)
- [ ] Python synthesizer working
- [ ] IR validator working
- [ ] 30+ test cases passing
- [ ] 85%+ Python round-trip success
- [ ] Error taxonomy implemented
- [ ] Database queries integrated
- [ ] Validation report complete

### Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| Extraction speed | < 5 seconds for 1000 LOC | `time just ir-extract large_file.py` |
| Synthesis speed | < 3 seconds for 1000 LOC | `time just ir-synthesize large_ir.json` |
| Round-trip overhead | < 10 seconds for 1000 LOC | `time just ir-roundtrip large_file.py` |
| Memory usage | < 500 MB for 10,000 LOC | `pytest --memray` |
| Test suite runtime | < 5 minutes total | `time just ir-test` |

### Quality Requirements

- [ ] Code coverage > 80% for core modules
- [ ] All public APIs documented with docstrings
- [ ] Type hints throughout (strict mypy)
- [ ] No ruff errors or warnings

## Effort Estimate

12-16 days (increased from original 7-10 to account for core infrastructure and cross-file analysis)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Tree-sitter Python grammar issues | Low | Medium | Fall back to `ast` module |
| Type inference too complex | Medium | Medium | Limit to explicit type hints; use fallback chain |
| Round-trip rate below 70% | Medium | High | Reduce test scope, document gaps, focus on pure functions |
| Pyright integration complexity | Medium | Medium | Start with jedi, upgrade when needed |
| Cross-file resolution failures | High | High | Implement graceful degradation; mark unresolved as E004 |
| Semantic equivalence hard to verify | Medium | High | Define testable subset; manual review for edge cases |
| Performance degradation at scale | Medium | Medium | Add benchmarks early; optimize hot paths |
| Core infrastructure over-engineering | Medium | Low | Start minimal; extend based on Phase 6 needs |

## Output Files

| File | Description |
|------|-------------|
| `docs/src/validation/equivalence-levels.md` | Equivalence taxonomy |
| `docs/src/adr/adr-009-extractor-architecture.md` | Architecture decision |
| `tools/ir-core/` | **Core infrastructure** (base classes, shared utilities) |
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
