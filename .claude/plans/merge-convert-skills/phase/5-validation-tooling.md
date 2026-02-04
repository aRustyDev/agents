# Phase 5: Validation & Tooling

Verify IR design and build extraction/synthesis tools.

## Goal

Validate that the IR schema meets requirements and build prototype tools to demonstrate the extraction → synthesis pipeline.

## Dependencies

- Phase 4: IR Schema Design

## Deliverables

- [ ] Validation report confirming IR completeness
- [ ] Prototype extraction tools (3+ languages)
- [ ] Prototype synthesis tools (3+ languages)
- [ ] Test suite with round-trip examples
- [ ] `tools/` directory with all prototypes

## Tasks

### 5.1 Validation Criteria

| Criterion | Description | Test Method |
|-----------|-------------|-------------|
| **Completeness** | Can represent all patterns from Phase 0 | Map each pattern to IR construct |
| **Round-trip** | Source → IR → Source' is semantically equivalent | Automated testing |
| **Cross-family** | IR supports family-to-family conversion | Manual verification |
| **Incrementality** | Partial updates work correctly | Change detection tests |
| **Gap Coverage** | All known gaps have markers | Cross-reference Phase 3 |

### 5.2 Pattern Coverage Validation

For each pattern extracted in Phase 0:

```yaml
pattern_validation:
  pattern_id: "P001"
  pattern_name: "Exception to Result conversion"
  ir_representation:
    layer: 2  # Control Flow
    constructs: [try_block, effect_annotation]
    mapping: |
      try { ... } catch (E e) { ... }
      →
      ControlFlowGraph:
        blocks:
          - id: try_block
            terminator: try
          - id: catch_block
            ...
        effects: [throws(E)]
  verified: true
  notes: "Fully representable"
```

### 5.3 Prototype Tools Architecture

```
tools/
├── ir-extract/           # Source code → IR
│   ├── core/             # Shared extraction logic
│   │   ├── parser.py     # Language-agnostic parsing
│   │   ├── ir_builder.py # IR construction
│   │   └── semantic.py   # Semantic analysis
│   ├── python/           # Python extractor
│   │   ├── parser.py     # AST parsing
│   │   ├── types.py      # Type inference
│   │   └── extract.py    # Main extractor
│   ├── typescript/       # TypeScript extractor
│   └── rust/             # Rust extractor
│
├── ir-synthesize/        # IR → Target code
│   ├── core/             # Shared synthesis logic
│   │   ├── ir_reader.py  # IR loading
│   │   ├── templates.py  # Code templates
│   │   └── formatter.py  # Code formatting
│   ├── python/           # Python synthesizer
│   ├── typescript/       # TypeScript synthesizer
│   └── rust/             # Rust synthesizer
│
├── ir-diff/              # Compare two IRs
│   ├── structural.py     # Structural comparison
│   ├── semantic.py       # Semantic comparison
│   └── report.py         # Diff report generation
│
├── ir-validate/          # Check IR consistency
│   ├── schema.py         # Schema validation
│   ├── references.py     # Reference integrity
│   └── semantic.py       # Semantic consistency
│
├── ir-visualize/         # Generate diagrams
│   ├── module_graph.py   # Module dependencies
│   ├── type_graph.py     # Type relationships
│   └── control_flow.py   # CFG visualization
│
└── ir-query/             # Query IR data
    ├── sql.py            # SQL queries
    └── patterns.py       # Pattern matching
```

### 5.4 Extraction Tool Design

```python
# tools/ir-extract/core/extractor.py

class Extractor(Protocol):
    """Base interface for language extractors."""

    def extract_module(self, source: str, path: str) -> ModuleIR:
        """Extract structural IR from source code."""
        ...

    def extract_types(self, module: ModuleIR) -> list[TypeIR]:
        """Extract type definitions."""
        ...

    def extract_functions(self, module: ModuleIR) -> list[FunctionIR]:
        """Extract function definitions with control flow."""
        ...

    def extract_data_flow(self, function: FunctionIR) -> DataFlowGraph:
        """Extract data flow graph."""
        ...

    def infer_semantics(self, ir: IR) -> SemanticAnnotations:
        """Infer semantic annotations (purity, nullability, etc.)."""
        ...
```

### 5.5 Synthesis Tool Design

```python
# tools/ir-synthesize/core/synthesizer.py

class Synthesizer(Protocol):
    """Base interface for language synthesizers."""

    def synthesize_module(self, ir: ModuleIR) -> str:
        """Generate module structure."""
        ...

    def synthesize_type(self, ir: TypeIR) -> str:
        """Generate type definition."""
        ...

    def synthesize_function(self, ir: FunctionIR) -> str:
        """Generate function implementation."""
        ...

    def apply_idioms(self, code: str) -> str:
        """Apply target-language idioms."""
        ...

    def format_code(self, code: str) -> str:
        """Format generated code."""
        ...
```

### 5.6 Test Suite Structure

```
tests/
├── unit/                 # Unit tests
│   ├── test_ir_schema.py
│   ├── test_extraction.py
│   └── test_synthesis.py
│
├── integration/          # Integration tests
│   ├── test_roundtrip.py     # Source → IR → Source'
│   ├── test_cross_lang.py    # Python IR → Rust code
│   └── test_incremental.py   # Change detection
│
├── regression/           # Regression tests from convert-* skills
│   ├── python_to_rust/
│   ├── typescript_to_go/
│   └── ...
│
├── property/             # Property-based tests
│   ├── test_ir_generation.py  # Random valid IR
│   └── test_invariants.py     # IR invariants
│
└── fixtures/             # Test fixtures
    ├── python/
    │   ├── simple.py
    │   ├── types.py
    │   └── async.py
    ├── typescript/
    └── rust/
```

### 5.7 Round-Trip Testing

```python
# tests/integration/test_roundtrip.py

@pytest.mark.parametrize("fixture", PYTHON_FIXTURES)
def test_python_roundtrip(fixture: Path):
    """Test Python → IR → Python preserves semantics."""
    # Extract
    original = fixture.read_text()
    ir = python_extractor.extract(original)

    # Synthesize
    generated = python_synthesizer.synthesize(ir)

    # Verify semantic equivalence
    assert semantically_equivalent(original, generated)

@pytest.mark.parametrize("source,target", [
    ("python", "rust"),
    ("python", "typescript"),
    ("typescript", "go"),
])
def test_cross_language(source: str, target: str, fixture: Path):
    """Test cross-language conversion."""
    original = fixture.read_text()

    # Extract from source
    ir = extractors[source].extract(original)

    # Check for gaps
    gaps = ir.get_gaps()
    if gaps.has_impossible():
        pytest.skip(f"Impossible gaps: {gaps.impossible}")

    # Synthesize to target
    generated = synthesizers[target].synthesize(ir)

    # Verify it compiles
    assert compiles(generated, target)

    # Verify behavior (where possible)
    if can_test_behavior(source, target):
        assert same_behavior(original, generated)
```

### 5.8 Validation Report Template

```markdown
# IR Validation Report

## Summary
- Patterns tested: X/Y (Z%)
- Round-trips passing: A/B
- Cross-family conversions: C/D

## Pattern Coverage

| Pattern Category | Total | Covered | Notes |
|------------------|-------|---------|-------|
| Type mappings | ... | ... | ... |
| Idiom translations | ... | ... | ... |
| Error handling | ... | ... | ... |
| Concurrency | ... | ... | ... |

## Round-Trip Results

| Language | Extract | Synthesize | Round-trip |
|----------|---------|------------|------------|
| Python | ✓ | ✓ | 95% |
| TypeScript | ✓ | ✓ | 92% |
| Rust | ✓ | ✓ | 88% |

## Cross-Language Results

| From | To | Success Rate | Common Gaps |
|------|----|--------------:|-------------|
| Python | Rust | 78% | Ownership, typing |
| Python | TS | 95% | Few |
| TS | Go | 82% | Generics, null |

## Known Issues
1. ...
2. ...

## Recommendations
1. ...
2. ...
```

## Success Criteria

- [ ] 100% of Phase 0 patterns mappable to IR
- [ ] 3+ language extractors working
- [ ] 3+ language synthesizers working
- [ ] 90%+ round-trip success rate
- [ ] Test suite with 50+ test cases
- [ ] Validation report complete

## Effort Estimate

7-10 days

## Output Files

| File | Description |
|------|-------------|
| `tools/` | All prototype tools |
| `tests/` | Test suite |
| `analysis/validation-report.md` | Validation results |
| `docs/src/tools/` | Tool documentation |
