# Phase 9: Roc Extractor & Synthesizer

Implement Roc language support for the IR extraction/synthesis pipeline.

## Goal

Build Roc extractor and synthesizer, focusing on Roc's pure functional approach, algebraic effects via platforms, and lack of runtime exceptions.

## Dependencies

- **Phase 5**: Python MVP
- **Phase 6**: Rust tooling (similar syntax, performance focus)
- **Phase 7**: TypeScript tooling (type system patterns)

### Roc-Specific IR Requirements

From `docs/src/ir-schema/layer-2.md` (Control Flow IR):
- Task-based effects (via platforms)
- No exceptions (Result everywhere)
- Pattern matching

From `docs/src/ir-schema/cross-cutting.md`:
- Annotation kinds: `EF-002` (Implicit→Explicit effects), `EF-005` (Effect handlers)

## Deliverables

- [ ] Roc extractor using Roc compiler APIs or tree-sitter
- [ ] Roc synthesizer with platform-aware code generation
- [ ] Cross-language tests (especially Python ↔ Roc, Rust ↔ Roc)
- [ ] 20+ Roc-specific test cases
- [ ] Validation report

---

## Roc-Specific Challenges

### Pure Functional with Platform Effects

```roc
app [main] { pf: platform "https://..." }

import pf.Stdout
import pf.Task exposing [Task]

main : Task {} *
main =
    Stdout.line "Hello, World!"

processNumbers : List I64 -> List I64
processNumbers = \numbers ->
    List.map numbers \n -> n * 2
```

**IR Representation**:

```yaml
module:
  app: main
  platform: pf
  imports:
    - module: pf.Stdout
    - module: pf.Task
      exposing: [Task]

function:
  name: main
  type: "Task {} *"
  effects:
    - kind: EF-002
      value: { effect_type: platform_task }
  purity: effectful_via_platform

function:
  name: processNumbers
  type: "List I64 -> List I64"
  purity: pure  # No effects
```

### No Exceptions Pattern

```roc
parseNumber : Str -> Result I64 [InvalidNumber]
parseNumber = \str ->
    when Str.toI64 str is
        Ok n -> Ok n
        Err _ -> Err InvalidNumber

# Usage always handles errors
processInput : Str -> Str
processInput = \input ->
    when parseNumber input is
        Ok n -> Num.toStr (n * 2)
        Err InvalidNumber -> "Invalid input"
```

**IR Representation**:

```yaml
function:
  name: parseNumber
  returns:
    type: "Result I64 [InvalidNumber]"
  annotations:
    - kind: EF-001
      value: { pattern: result_type, error_variants: [InvalidNumber] }
```

---

## Tasks

### 9.1 Roc Extractor Implementation

**Implementation Approach**:
- **Primary**: Roc compiler source (if APIs available)
- **Fallback**: tree-sitter-roc (community grammar)
- **Semantic**: Parse type annotations directly (Roc has explicit types)

**Challenges**:
- Roc is newer; tooling less mature
- Platform system is unique
- May need custom grammar development

**Deliverable**: `tools/ir-extract/roc/`

---

### 9.2 Roc Synthesizer Implementation

**Key Patterns**:
- Function syntax with backslash lambdas
- `when...is` pattern matching
- Record syntax
- Tag unions
- Platform imports

```python
def gen_function(self, func: FunctionIR) -> str:
    # Roc syntax: name : Type \n name = \params -> body
    type_sig = f"{func.name} : {self.gen_type(func.type)}"
    impl = f"{func.name} = \\{', '.join(func.params)} ->\n    {self.gen_body(func.body)}"
    return f"{type_sig}\n{impl}"
```

**Deliverable**: `tools/ir-synthesize/roc/`

---

### 9.3-9.6 Testing, Cross-Language, Report, Review

**Cross-Language Focus**:
- Python → Roc: High value (dynamic → pure)
- Rust → Roc: Similar syntax patterns
- Roc → Python: Pure functions easy to convert

---

## Success Criteria

- [ ] Roc extractor working (15+ fixtures)
- [ ] Roc synthesizer producing valid code
- [ ] Platform effects captured in IR
- [ ] Result patterns preserved
- [ ] 20+ test cases passing

## Effort Estimate

7-10 days (less mature tooling)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Roc tooling immature | High | Medium | Contribute to tree-sitter-roc |
| Platform system complex | Medium | Medium | Focus on pure functions first |
| Syntax changes (Roc is pre-1.0) | Medium | High | Pin to specific Roc version |

## Output Files

| File | Description |
|------|-------------|
| `tools/ir-extract/roc/` | Roc extractor |
| `tools/ir-synthesize/roc/` | Roc synthesizer |
| `tests/fixtures/roc/` | Test fixtures |
| `analysis/phase9-validation-report.md` | Results |
