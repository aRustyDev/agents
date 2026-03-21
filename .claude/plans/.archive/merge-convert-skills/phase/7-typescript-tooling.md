# Phase 7: TypeScript Extractor & Synthesizer

Implement TypeScript language support for the IR extraction/synthesis pipeline.

## Goal

Build TypeScript extractor and synthesizer for TypeScript-specific patterns. TypeScript is a high-priority target with 933+ patterns from the database.

**Design Decision**: This phase focuses on TypeScript-only tooling. Cross-language conversion capabilities are out of scope for the initial implementation.

## Dependencies

- **Phase 5**: Python MVP (patterns, infrastructure)
- **Phase 6**: Rust tooling (cross-language patterns)

### TypeScript-Specific IR Requirements

From `docs/src/ir-schema/layer-3.md` (Type IR):
- Structural typing vs nominal
- Union and intersection types
- Generic constraints and variance
- Type inference and widening

From `docs/src/ir-schema/cross-cutting.md`:
- Annotation kinds: `TS-004` (Structural→Nominal), `TS-006` (Type inference), `TS-009` (Union types)

## Deliverables

- [x] TypeScript extractor with full type extraction
- [x] TypeScript synthesizer with proper type annotations
- [x] JSDoc documentation parsing and extraction
- [x] ESLint integration for code validation
- [x] tsc --strict compilation verification tests
- [x] 30+ TypeScript-specific test fixtures
- [ ] Cross-language tests (Python ↔ TypeScript, Rust ↔ TypeScript) - *future phase*
- [ ] Validation report

---

## TypeScript-Specific Challenges

### Rich Type System Extraction

```typescript
// Complex types to extract
interface User<T extends string = string> {
  readonly id: number;
  name: T;
  email?: string;  // Optional
  tags: string[];
}

type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

function process<T>(input: T | null): T | undefined {
  return input ?? undefined;
}
```

**IR Representation**:

```yaml
type_def:
  name: User
  kind: interface
  type_params:
    - name: T
      constraint: string
      default: string
  properties:
    - name: id
      type: number
      readonly: true
    - name: name
      type: T
    - name: email
      type: string
      optional: true
    - name: tags
      type: "string[]"
  annotations:
    - kind: TS-004
      value: { typing: structural }
```

### Union and Intersection Types

```typescript
type StringOrNumber = string | number;
type Named = { name: string };
type Aged = { age: number };
type Person = Named & Aged;
```

---

## Tasks

### 7.1 TypeScript Extractor Implementation [COMPLETED]

Build TypeScript source → IR extractor.

**Actual Implementation Approach**:
- **Primary**: `tree-sitter-typescript` via `tree-sitter-language-pack` (pure Python)
- **Type Analysis**: Custom `TypeAnalyzer` for union/intersection/conditional type parsing
- **JSDoc Integration**: Custom `JSDocParser` for documentation extraction
- **No external TypeScript runtime required** (tsc only for validation tests)

```python
# tools/ir-extract-typescript/ir_extract_typescript/extractor.py
@register_extractor("typescript")
class TypeScriptExtractor(Extractor):
    def __init__(self) -> None:
        self._parser = TypeScriptParser()  # tree-sitter based
        self._type_analyzer = TypeAnalyzer()

    def extract(self, source: str, path: str, config: ExtractConfig) -> IRVersion:
        # 1. Parse with tree-sitter
        parsed = self._parser.parse(source)

        # 2. Extract module structure (Layer 4)
        ir.structural = self._extract_module_structure(parsed, path)

        # 3. Extract types with JSDoc (Layer 3)
        ir.types = self._extract_types(parsed)

        # 4. Extract functions with JSDoc (Layer 2)
        ir.functions = self._extract_functions(parsed)

        # 5. Generate semantic annotations
        ir.annotations = self._generate_annotations(parsed, ir)

        return ir
```

**Key Modules**:
- `parser.py` - Tree-sitter AST traversal and dataclass extraction
- `types.py` - TypeAnalyzer for complex type categorization
- `jsdoc.py` - JSDoc comment parsing with @param, @returns, @template support

**Deliverable**: `tools/ir-extract-typescript/`

**Acceptance** [MET]:
- [x] Extracts 30+ TypeScript fixtures to valid IR
- [x] Full type information preserved (interfaces, type aliases, enums, classes)
- [x] Generics and constraints captured
- [x] JSDoc documentation extracted and attached to IR

---

### 7.2 TypeScript Synthesizer Implementation [COMPLETED]

Build IR → TypeScript code synthesizer.

**Actual Implementation**:
- `generator.py` - TypeScript code generation from IR
- `formatter.py` - Prettier integration (with SimpleFormatter fallback)
- `linter.py` - ESLint integration for code validation
- `synthesizer.py` - Main synthesizer with cross-language gap detection

```python
# tools/ir-synthesize-typescript/ir_synthesize_typescript/synthesizer.py
@register_synthesizer("typescript")
class TypeScriptSynthesizer(Synthesizer):
    def synthesize(self, ir: IRVersion, config: SynthConfig) -> str:
        # 1. Configure generator
        self._generator = TypeScriptCodeGenerator(gen_config)

        # 2. Detect cross-language conversion gaps
        if ir.source_language != "typescript":
            self._detect_conversion_gaps(ir)

        # 3. Generate code
        code = self._generator.generate(
            types=ir.types,
            functions=ir.functions,
            imports=imports,
        )

        # 4. Format output (Prettier or SimpleFormatter)
        return self._format_code(code, config)

    def lint(self, code: str, strict: bool = False) -> LintResult:
        """Lint generated code using ESLint."""
        return self._linter.lint(code)

    def synthesize_and_lint(self, ir, config, lint_fix=False) -> tuple[str, LintResult]:
        """Synthesize and lint in one step."""
        code = self.synthesize(ir, config)
        if lint_fix:
            return self.lint_and_fix(code)
        return code, self.lint(code)
```

**Deliverable**: `tools/ir-synthesize-typescript/`

**Acceptance** [MET]:
- [x] Generates valid TypeScript that compiles with `tsc --strict`
- [x] Preserves type information from IR
- [x] Uses idiomatic TypeScript patterns
- [x] ESLint integration for code quality validation
- [x] Prettier/fallback formatting support

---

### 7.3 Cross-Language Testing [DEFERRED]

Cross-language conversions involving TypeScript are deferred to a future phase.

**Estimated Success Rates** (when implemented):

| Direction | Estimated Success | Key Gaps |
|-----------|-------------------|----------|
| Python → TypeScript | ~90% | Few gaps expected |
| TypeScript → Python | ~85% | Strict types → dynamic |
| TypeScript → Rust | ~65% | Null handling, ownership |
| Rust → TypeScript | ~80% | Ownership semantics lost |

*Note: These are estimates based on type system analysis, not measured results.*

**Deliverable**: `tests/integration/test_typescript_*.py` (future)

---

### 7.4 TypeScript Test Suite [COMPLETED - 30 FIXTURES]

**Actual Test Categories**:

```
tests/fixtures/typescript/
├── types/                        # 5 fixtures
│   ├── interfaces.ts
│   ├── type_aliases.ts
│   ├── unions_intersections.ts
│   ├── generics.ts
│   └── conditional_types.ts
├── functions/                    # 3 fixtures
│   ├── overloads.ts
│   ├── async_await.ts
│   └── arrow_functions.ts
├── classes/                      # 3 fixtures
│   ├── inheritance.ts
│   ├── access_modifiers.ts
│   └── decorators.ts
├── modules/                      # 2 fixtures
│   ├── imports_exports.ts
│   └── namespaces.ts
├── utilities/                    # 5 fixtures (NEW)
│   ├── pick_omit.ts              # Pick, Omit, Partial, Required
│   ├── readonly_record.ts        # Readonly, Record, DeepReadonly
│   ├── extract_exclude.ts        # Extract, Exclude, NonNullable
│   ├── return_parameters.ts      # ReturnType, Parameters
│   └── awaited.ts                # Awaited, Promise patterns
├── narrowing/                    # 4 fixtures (NEW)
│   ├── type_guards.ts            # User-defined type predicates
│   ├── discriminated_unions.ts   # Tagged unions, exhaustiveness
│   ├── control_flow.ts           # Truthiness, equality narrowing
│   └── in_operator.ts            # Property checking narrowing
├── advanced/                     # 4 fixtures (NEW)
│   ├── template_literals.ts      # Template literal types
│   ├── recursive_types.ts        # LinkedList, Tree, JSON types
│   ├── infer_keyword.ts          # Conditional type inference
│   └── variance.ts               # Covariance, contravariance
├── jsdoc/                        # 2 fixtures (NEW)
│   ├── type_annotations.ts       # @param, @returns, @template
│   └── documentation.ts          # @fileoverview, @example, @deprecated
└── multi_version/                # 2 fixtures (NEW)
    ├── es2015_features.ts        # Arrow, classes, destructuring
    └── es2022_features.ts        # Private fields, static blocks
```

**Total: 30 fixtures** (exceeds 30+ target)

**Deliverable**: `tests/fixtures/typescript/`

---

### 7.5 Compilation Verification Tests [COMPLETED]

**tsc --strict Compilation Tests**:

```python
# tools/ir-synthesize-typescript/tests/test_compilation.py
class TestSimpleTypeCompilation:
    def test_interface_compiles(self): ...
    def test_type_alias_compiles(self): ...
    def test_generic_interface_compiles(self): ...

class TestFunctionCompilation:
    def test_simple_function_compiles(self): ...
    def test_generic_function_compiles(self): ...
    def test_async_function_compiles(self): ...
    def test_overloaded_function_compiles(self): ...

class TestClassCompilation:
    def test_simple_class_compiles(self): ...
    def test_class_with_inheritance_compiles(self): ...
    def test_class_with_private_fields_compiles(self): ...

class TestAdvancedTypesCompilation:
    def test_conditional_type_compiles(self): ...
    def test_mapped_type_compiles(self): ...
    def test_template_literal_type_compiles(self): ...
    def test_discriminated_union_compiles(self): ...

class TestStrictModeCompilation:
    def test_strict_null_checks(self): ...  # Verify strict catches issues
    def test_no_implicit_any(self): ...
```

**Total: 20 compilation tests** (skipped when tsc unavailable)

### 7.6 JSDoc Support [COMPLETED]

**JSDoc Parser Implementation**:

```python
# tools/ir-extract-typescript/ir_extract_typescript/jsdoc.py
@dataclass
class JSDocComment:
    description: str | None
    params: list[JSDocParam]
    returns: JSDocReturns | None
    templates: list[JSDocTemplate]
    throws: list[tuple[str | None, str]]
    examples: list[JSDocExample]
    deprecated: str | None
    # ... 20+ supported tags

class JSDocParser:
    def parse(self, comment: str) -> JSDocComment | None:
        # Parses @param, @returns, @template, @deprecated, etc.
```

**Supported Tags**: @param, @returns, @template, @throws, @example, @deprecated, @see, @since, @author, @type, @typedef, @callback, @fires, @listens, @readonly, @private, @protected, @public, @internal, @override, @abstract, @async, @generator, @fileoverview, @module

Total: 25 JSDoc tests passing.

### 7.7 ESLint Integration [COMPLETED]

**Linter Implementation**:

```python
# tools/ir-synthesize-typescript/ir_synthesize_typescript/linter.py
class ESLinter:
    def lint(self, code: str, fix: bool = False) -> LintResult: ...
    def fix(self, code: str) -> tuple[str, LintResult]: ...

class ESLintConfig:
    DEFAULT_RULES = {...}   # Recommended rules
    STRICT_RULES = {...}    # Strict enforcement
    RELAXED_RULES = {...}   # For less strict checking
```

Total: 16 linter tests passing.

### 7.8 Validation Report

**Deliverable**: `analysis/phase7-validation-report.md` [TODO]

### 7.9 Final Review

**Deliverable**: `analysis/phase7-review.md` [TODO]

---

## Success Criteria

- [x] TypeScript extractor working (30 fixtures - exceeds 25+)
- [x] TypeScript synthesizer producing `tsc --strict` valid code
- [x] 30+ test fixtures created
- [x] JSDoc documentation support
- [x] ESLint integration for code quality
- [ ] Cross-language tests (deferred to future phase)
- [ ] Validation report (TODO)

## TypeScript Version Support

The implementation supports multiple TypeScript target versions:

| Target | Key Features |
|--------|--------------|
| ES2015 | Classes, arrow functions, destructuring, symbols |
| ES2022 | Private fields, static blocks, at(), findLast() |

**Note**: Version-specific code patterns are tested in `multi_version/` fixtures.

## Effort Estimate

7-10 days (actual: ~8 days)

## Output Files

| File | Description | Status |
|------|-------------|--------|
| `tools/ir-extract-typescript/` | TypeScript extractor | DONE |
| `tools/ir-synthesize-typescript/` | TypeScript synthesizer | DONE |
| `tests/fixtures/typescript/` | 30 test fixtures | DONE |
| `tools/ir-extract-typescript/ir_extract_typescript/jsdoc.py` | JSDoc parser | DONE |
| `tools/ir-synthesize-typescript/ir_synthesize_typescript/linter.py` | ESLint integration | DONE |
| `tools/ir-synthesize-typescript/tests/test_compilation.py` | tsc verification | DONE |
| `analysis/phase7-validation-report.md` | Results | TODO |
