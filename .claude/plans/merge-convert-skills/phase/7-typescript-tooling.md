# Phase 7: TypeScript Extractor & Synthesizer

Implement TypeScript language support for the IR extraction/synthesis pipeline.

## Goal

Build TypeScript extractor and synthesizer, leveraging the TypeScript Compiler API for rich type information. TypeScript is a high-priority target with 933+ patterns from the database.

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

- [ ] TypeScript extractor with full type extraction
- [ ] TypeScript synthesizer with proper type annotations
- [ ] Cross-language tests (Python ↔ TypeScript, Rust ↔ TypeScript)
- [ ] 30+ TypeScript-specific test cases
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

### 7.1 TypeScript Extractor Implementation

Build TypeScript source → IR extractor.

**Implementation Approach**:
- **Primary**: TypeScript Compiler API via `ts-morph`
- **Alternative**: `tree-sitter-typescript` + LSP for simpler cases

```python
# tools/ir-extract/typescript/extract.py
# Note: May use subprocess to call TypeScript tooling

class TypeScriptExtractor:
    def extract(self, source: str, path: str) -> IRVersion:
        # 1. Use ts-morph for full type information
        project = self.create_project(source, path)

        # 2. Extract module structure
        structural = self.extract_module(project)

        # 3. Extract all type definitions
        types = self.extract_types(project)

        # 4. Extract functions with full signatures
        functions = self.extract_functions(project)

        # 5. Generate IR
        return self.generate_ir(structural, types, functions)
```

**ts-morph Integration**:

```typescript
// tools/ir-extract/typescript/extract.ts
import { Project, SourceFile } from "ts-morph";

export function extractIR(source: string): IR {
  const project = new Project({ useInMemoryFileSystem: true });
  const sourceFile = project.createSourceFile("temp.ts", source);

  return {
    types: extractTypes(sourceFile),
    functions: extractFunctions(sourceFile),
    module: extractModule(sourceFile),
  };
}
```

**Deliverable**: `tools/ir-extract/typescript/`

**Acceptance**:
- Extracts 25+ TypeScript fixtures to valid IR
- Full type information preserved
- Generics and constraints captured

---

### 7.2 TypeScript Synthesizer Implementation

Build IR → TypeScript code synthesizer.

```python
# tools/ir-synthesize/typescript/synthesize.py
class TypeScriptSynthesizer:
    def synthesize(self, ir: IRVersion) -> str:
        # 1. Generate imports
        imports = self.gen_imports(ir.structural)

        # 2. Generate type definitions
        types = self.gen_types(ir.types)

        # 3. Generate functions
        functions = self.gen_functions(ir.control_flow)

        # 4. Assemble and format with prettier
        code = self.assemble(imports, types, functions)
        return self.format_with_prettier(code)
```

**Type Generation**:

```python
def gen_type(self, type_def: TypeDef) -> str:
    if type_def.kind == "interface":
        return self.gen_interface(type_def)
    elif type_def.kind == "type_alias":
        return self.gen_type_alias(type_def)
    elif type_def.kind == "enum":
        return self.gen_enum(type_def)
    # ...
```

**Deliverable**: `tools/ir-synthesize/typescript/`

**Acceptance**:
- Generates valid TypeScript that compiles with `tsc --strict`
- Preserves type information from IR
- Uses idiomatic TypeScript patterns

---

### 7.3 Cross-Language Testing

Test conversions involving TypeScript.

**Test Matrix**:

| Direction | Expected Success | Key Gaps |
|-----------|------------------|----------|
| Python → TypeScript | 90%+ | Few gaps |
| TypeScript → Python | 85%+ | Strict types → dynamic |
| TypeScript → Rust | 65%+ | Null handling, ownership |
| Rust → TypeScript | 80%+ | Ownership lost |

**Deliverable**: `tests/integration/test_typescript_*.py`

---

### 7.4 TypeScript Test Suite

**Test Categories**:

```
tests/fixtures/typescript/
├── types/
│   ├── interfaces.ts
│   ├── type_aliases.ts
│   ├── unions_intersections.ts
│   ├── generics.ts
│   └── conditional_types.ts
├── functions/
│   ├── overloads.ts
│   ├── async_await.ts
│   └── arrow_functions.ts
├── classes/
│   ├── inheritance.ts
│   ├── access_modifiers.ts
│   └── decorators.ts
└── modules/
    ├── imports_exports.ts
    └── namespaces.ts
```

**Deliverable**: `tests/fixtures/typescript/`

---

### 7.5 Validation Report

**Deliverable**: `analysis/phase7-validation-report.md`

### 7.6 Final Review

**Deliverable**: `analysis/phase7-review.md`

---

## Success Criteria

- [ ] TypeScript extractor working (25+ fixtures)
- [ ] TypeScript synthesizer producing `tsc --strict` valid code
- [ ] 90%+ Python → TypeScript success
- [ ] 30+ test cases passing

## Effort Estimate

7-10 days

## Output Files

| File | Description |
|------|-------------|
| `tools/ir-extract/typescript/` | TypeScript extractor |
| `tools/ir-synthesize/typescript/` | TypeScript synthesizer |
| `tests/fixtures/typescript/` | Test fixtures |
| `analysis/phase7-validation-report.md` | Results |
