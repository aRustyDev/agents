# Phase 4: IR Schema Design

Design the multi-layer Intermediate Representation architecture.

## Goal

Create a comprehensive IR schema that can represent code semantics from any supported language and enable high-fidelity conversion.

## Dependencies

- Phase 3: Semantic Gaps (informs what the IR must capture)

## Input Data Sources

Phase 4 builds on Phase 3's extensive gap analysis:

| Source | Location | Contents |
|--------|----------|----------|
| IR Implications | `analysis/ir-implications.md` | Layer mapping, 54 annotation requirements, priority ordering |
| Gap Patterns | `analysis/gap-patterns.md` | 54 patterns (16 type, 12 memory, 12 effect, 14 concurrency) |
| Severity Matrix | `analysis/severity-matrix.md` | 9x9 family conversion difficulty |
| Bidirectional Gaps | `analysis/bidirectional-gaps.md` | Asymmetry ratios (GC→Ownership 4:1, etc.) |
| Decision Points | `analysis/decision-points.md` | 16 human decision points |
| Preservation Levels | `docs/src/ir-schema/preservation-levels.md` | 4-level preservation model |
| Gap Data | `data/gaps.sql` | 54 patterns, 38 semantic gaps, 16 decision points |
| Base Schema | `data/schema.sql` | Existing tables: ir_versions, ir_units, ir_annotations, etc. |

**Key insight**: Phase 3 identified 320 gaps (0 impossible, 108 lossy, 176 structural, 22 runtime, 12 semantic, 2 idiomatic). The IR must be able to annotate all of these.

## Deliverables

- [ ] `docs/src/ir-schema/overview.md` - IR architecture documentation
- [ ] `docs/src/ir-schema/layer-{0-4}.md` - Per-layer documentation (5 files)
- [ ] `docs/src/ir-schema/binary-formats.md` - Protobuf/MessagePack documentation (for future extractor)
- [x] `<project>/docs/src/adr/008-ir-content-hashing.md` - Hashing algorithm decision record (DONE)
- [ ] `schemas/ir-v1.json` - JSON Schema definitions
- [ ] `data/ir-schema.sql` - SQL schema extensions (builds on existing schema.sql)
- [ ] `analysis/ir-validation.md` - Validation against Phase 0 patterns

## Layer Architecture Note

This plan uses a 5-layer model (0-4). Note that `ir-implications.md` from Phase 3 used a 4-layer model (0-3) with different semantics:

| Phase 4 (this plan) | Phase 3 (ir-implications.md) |
|---------------------|------------------------------|
| Layer 0: Expression IR | Layer 0: Concrete Syntax |
| Layer 1: Data Flow IR | Layer 1: Abstract Syntax |
| Layer 2: Control Flow IR | Layer 2: Semantic Core |
| Layer 3: Type IR | Layer 3: Target Lowering |
| Layer 4: Structural IR | (not defined) |

**Resolution**: Phase 4's 5-layer model is canonical. Update ir-implications.md references during implementation.

## Tasks

### 4.1 Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     EXTRACTION (Source → IR)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Layer 4: Structural IR                                         │
│  ├── Modules, packages, namespaces                              │
│  ├── Public/private boundaries                                  │
│  ├── Import/export dependencies                                 │
│  └── Build/compilation units                                    │
│                                                                 │
│  Layer 3: Type IR                                               │
│  ├── Type definitions (ADTs, classes, interfaces)               │
│  ├── Type relationships (subtyping, implements, extends)        │
│  ├── Generic/parametric types                                   │
│  └── Type constraints and bounds                                │
│                                                                 │
│  Layer 2: Control Flow IR                                       │
│  ├── Function/method signatures                                 │
│  ├── Control patterns (branch, loop, match, try)                │
│  ├── Effect annotations (pure, throws, async)                   │
│  └── Concurrency patterns (spawn, await, channel)               │
│                                                                 │
│  Layer 1: Data Flow IR                                          │
│  ├── Variable bindings and lifetimes                            │
│  ├── Data transformations (map, filter, fold)                   │
│  ├── Side effect tracking                                       │
│  └── Dependency graph between expressions                       │
│                                                                 │
│  Layer 0: Expression IR (optional, for deep analysis)           │
│  ├── Full AST representation                                    │
│  ├── Operator semantics                                         │
│  └── Literal values and constants                               │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    SYNTHESIS (IR → Target)                       │
└─────────────────────────────────────────────────────────────────┘
```

**Extraction Modes** (partial extraction supported):

| Mode | Layers | Use Case |
|------|--------|----------|
| Full module | 0-4 | Complete codebase conversion |
| Single function | 0-2 | Function-level conversion |
| Type only | 3-4 | Interface/type extraction |
| Signature only | 2-4 | API surface extraction |

### 4.2 Layer 4: Structural IR

Represents the high-level organization of code.

```yaml
module:
  id: ModuleId
  name: string
  path: string[]  # namespace path
  visibility: public | internal | private
  imports: Import[]
  exports: Export[]
  definitions: Definition[]
  extraction_scope: full | partial  # NEW: supports partial extraction
  metadata:
    source_file: string
    source_language: string
    extraction_version: string
    extraction_mode: full_module | single_function | type_only | signature_only

import:
  id: ImportId
  module_path: string[]
  imported_items: ImportedItem[]  # specific items or wildcard
  alias: string?

export:
  id: ExportId
  item: DefinitionRef
  alias: string?
  visibility: public | package | internal

definition:
  kind: type | function | constant | variable
  ref: TypeId | FunctionId | ConstantId | VariableId
```

### 4.3 Layer 3: Type IR

Represents type definitions and relationships.

```yaml
type_def:
  id: TypeId
  name: string
  kind: struct | enum | class | interface | alias | opaque | primitive
  params: TypeParam[]  # generic parameters
  constraints: Constraint[]  # where clauses, bounds
  body: TypeBody
  visibility: Visibility

type_param:
  name: string
  variance: invariant | covariant | contravariant
  bounds: TypeRef[]
  default: TypeRef?

type_body:
  # For struct/class
  fields: Field[]
  methods: MethodRef[]

  # For enum
  variants: Variant[]

  # For interface/trait
  required_methods: MethodSignature[]
  provided_methods: MethodRef[]

  # For alias
  aliased_type: TypeRef

type_ref:
  kind: named | generic | function | tuple | union | intersection
  # For named
  type_id: TypeId
  args: TypeRef[]  # generic arguments
  # For function
  params: TypeRef[]
  return_type: TypeRef
  effects: Effect[]
  # For tuple
  elements: TypeRef[]
  # For union/intersection
  members: TypeRef[]

type_relationship:
  from_type: TypeId
  to_type: TypeId
  kind: extends | implements | subtype_of | convertible_to
```

### 4.4 Layer 2: Control Flow IR

Represents function signatures and control structures.

```yaml
function:
  id: FunctionId
  name: string
  params: Param[]
  return_type: TypeRef
  type_params: TypeParam[]
  effects: Effect[]  # pure, throws, async, etc.
  body: ControlFlowGraph?  # None for declarations
  visibility: Visibility
  receiver: Receiver?  # for methods

param:
  name: string
  type: TypeRef
  default: Expression?
  mutability: mutable | immutable | move

effect:
  kind: pure | throws | async | unsafe | io | suspends | allocates | captures
  type: TypeRef?  # e.g., throws(ErrorType)

control_flow_graph:
  entry: BlockId
  blocks: Block[]
  exit: BlockId

block:
  id: BlockId
  statements: Statement[]
  terminator: Terminator

terminator:
  kind: return | branch | switch | loop | try | unreachable
  # For return
  value: Expression?
  # For branch
  condition: Expression
  then_block: BlockId
  else_block: BlockId?
  # For switch/match
  scrutinee: Expression
  arms: SwitchArm[]
  # For loop
  body: BlockId
  continue_target: BlockId
  break_target: BlockId
  # For try
  try_block: BlockId
  catch_blocks: CatchBlock[]
  finally_block: BlockId?
```

### 4.5 Layer 1: Data Flow IR

Represents data bindings and transformations.

```yaml
binding:
  id: BindingId
  name: string
  type: TypeRef
  mutability: mutable | immutable | linear
  lifetime: Lifetime
  value: Expression?
  scope: ScopeId

lifetime:
  kind: static | scoped | owned | borrowed
  scope: ScopeId?
  borrow_kind: shared | mutable | move

data_flow_node:
  id: NodeId
  kind: source | transform | sink
  expression: Expression
  inputs: NodeId[]
  outputs: NodeId[]
  effects: Effect[]

transformation:
  kind: map | filter | fold | flat_map | collect
  input_type: TypeRef
  output_type: TypeRef
  function: FunctionRef | Lambda
```

### 4.6 Layer 0: Expression IR

Full AST representation for deep analysis. **Optional** - most conversions use Layers 1-4 only.

**When to use Layer 0:**
- Preserving exact formatting/comments for review
- Complex expression-level transformations
- Debugging conversion issues
- Round-trip fidelity testing

```yaml
expression:
  id: ExpressionId
  kind: literal | identifier | call | operator | lambda | ...
  type: TypeRef
  span: SourceSpan

  # For literal
  literal_kind: int | float | string | bool | null | ...
  literal_value: any

  # For identifier
  binding_ref: BindingId

  # For call
  callee: Expression
  arguments: Argument[]

  # For operator
  operator: string
  operands: Expression[]

  # For lambda
  params: Param[]
  body: Expression | ControlFlowGraph
  captures: Capture[]

source_span:
  file: string
  start_line: int
  start_col: int
  end_line: int
  end_col: int
```

### 4.7 Cross-Cutting Concerns

#### Semantic Annotations (from Phase 3)

Integrates the 54 gap patterns from `ir-implications.md`:

```yaml
semantic_annotation:
  target: AnyId  # type, function, expression, etc.
  kind: AnnotationKind
  value: any
  confidence: float  # 0.0-1.0 for inferred annotations
  source: explicit | inferred | default | test_suite
  evidence: string[]?  # supporting evidence for inference

# Annotation kinds from Phase 3 gap patterns
AnnotationKind:
  # Type System (16 patterns)
  - inferred_type        # TS-001: Dynamic → Static
  - nullability          # TS-002: Nullable → Non-null
  - hkt_specialization   # TS-003: HKT → No HKT
  - type_erasure_info    # TS-009: Type erasure boundaries
  - variance_annotation  # TS-014: Variance handling

  # Memory Model (12 patterns)
  - ownership_hint       # MM-002: GC → Ownership
  - ownership_transfer   # MM-003: Ownership transfer
  - mutability_analysis  # MM-004: Mutable → Immutable
  - lifetime_hint        # MM-005: Lifetime inference
  - arc_cycle_risk       # MM-007: ARC cycle detection

  # Effect System (12 patterns)
  - error_handling_conversion  # EF-001: Exceptions → Results
  - null_to_option            # EF-002: Null → Option
  - monad_flattening          # EF-004: Monads → Direct
  - evaluation_strategy       # EF-009: Lazy → Strict
  - effect_boundary           # EF-011: Effect isolation

  # Concurrency (14 patterns)
  - concurrency_model_conversion  # CC-001: Actors → Threads
  - channel_to_async             # CC-004: CSP → Async
  - supervision_conversion       # CC-009: Supervision trees
  - thread_safety               # CC-012: Thread safety analysis

  # Cross-cutting
  - preservation_level    # Level 0-3 from preservation-levels.md
  - decision_required     # Links to decision_points
  - asymmetry_info       # From bidirectional-gaps.md
```

**Example annotation (from ir-implications.md):**

```json
{
  "target": "binding:data",
  "kind": "inferred_type",
  "value": {
    "original": "dynamic",
    "inferred": "String",
    "confidence": 0.85,
    "source": "usage",
    "evidence": ["line 42: data.upper()", "line 58: return data + suffix"]
  }
}
```

#### Gap Markers

```yaml
gap_marker:
  id: GapMarkerId
  location: AnyId
  gap_type: impossible | lossy | structural | idiomatic | runtime | semantic
  gap_pattern_id: string?  # Reference to gap_patterns table (e.g., "TS-001")
  severity: critical | high | medium | low
  description: string
  source_concept: string
  target_concept: string?
  suggested_mitigations: string[]
  decision_point_id: string?  # Reference to decision_points if human decision needed
  preservation_level: 0 | 1 | 2 | 3  # Max achievable level with this gap
```

#### Preservation Level Tracking

```yaml
preservation_status:
  unit_id: AnyId
  current_level: 0 | 1 | 2 | 3
  max_achievable_level: 0 | 1 | 2 | 3
  blocking_gaps: GapMarkerId[]  # Gaps preventing higher level
  level_evidence:
    level_0: bool  # Syntactically valid
    level_1: bool  # Semantically equivalent
    level_2: bool  # Idiomatically correct
    level_3: bool  # Optimized
```

#### Asymmetry Metadata (for bidirectional conversions)

```yaml
asymmetry_info:
  source_family: string
  target_family: string
  direction_difficulty: 1-5
  reverse_difficulty: 1-5
  asymmetry_ratio: float  # e.g., 4.0 for GC→Ownership
  preserved_in_reverse: bool  # Can info be recovered going back?
  notes: string
```

### 4.8 Format Specifications

| Use Case | Format | Status | Scope |
|----------|--------|--------|-------|
| Human review | YAML/JSON | ✅ In scope | This project |
| Storage | SQLite | ✅ In scope | This project |
| Tool interop | Protobuf | 📄 Documentation only | Future extractor CLI |
| Transport | MessagePack | 📄 Documentation only | Future extractor CLI |

#### Binary Format Documentation (Out of Scope for Implementation)

A future "universal extractor" CLI will scan codebases and emit IR. This project provides **documentation only** for binary formats that CLI should use.

**Deliverable**: `docs/src/ir-schema/binary-formats.md`

Contents:
1. **Protobuf schema specification** - `.proto` file structure matching the YAML/JSON schemas
2. **Usage guidelines** - When to use Protobuf vs JSON (file size thresholds, streaming scenarios)
3. **MessagePack considerations** - For embedded scenarios where Protobuf overhead is excessive
4. **Cross-language compatibility** - Language-specific notes for Python, Rust, Go, TypeScript consumers
5. **Schema evolution rules** - How to add fields without breaking existing consumers

**Why document now?**
- Ensures JSON schema and future Protobuf schema stay aligned
- Provides architectural guidance for future implementers
- Identifies any JSON constructs that don't map cleanly to Protobuf

### 4.9 Incremental IR Design

#### Content Hashing (Unified Approach)

**Decision**: Use a single hashing algorithm for both deduplication and change detection. See `<project>/docs/src/adr/008-ir-content-hashing.md` for full rationale.

**Algorithm**: SHA-256 of canonicalized JSON content

```python
# Canonical hash computation
import hashlib
import json

def compute_content_hash(content: dict) -> str:
    """Compute SHA-256 hash of canonicalized JSON content."""
    # Canonicalize: sorted keys, no whitespace, UTF-8
    canonical = json.dumps(content, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
```

**Hash uses**:

| Use Case | How Hash is Used |
|----------|------------------|
| Deduplication | `UNIQUE(version_id, content_hash)` prevents duplicate units |
| Change detection | Compare `content_hash` across `version_id` values |
| Cache invalidation | Hash change triggers re-processing |
| Content addressing | Hash can serve as stable reference ID |

#### Incremental Update Schema

```yaml
incremental_unit:
  id: UnitId
  content_hash: ContentHash  # SHA-256, unified with ir_units.content_hash
  layer: 0-4
  dependencies: UnitId[]  # what this depends on
  dependents: UnitId[]  # what depends on this
  content: LayerContent
  version: int

change_set:
  base_version: VersionId
  timestamp: datetime
  changes:
    - unit_id: UnitId
      change_type: add | modify | delete
      old_hash: ContentHash?  # from previous version
      new_hash: ContentHash?  # in this version
```

**Note**: `old_content` and `new_content` removed from change_set - content is retrieved via hash lookup, not duplicated.

## SQL Schema Extensions

**Note**: Base tables (ir_versions, ir_units, ir_dependencies, ir_annotations) already exist in `data/schema.sql`. This schema adds Phase 4 extensions.

```sql
-- Phase 4 IR Schema Extensions
-- Run AFTER schema.sql

-- Preservation level tracking (from Phase 3)
CREATE TABLE IF NOT EXISTS ir_preservation_status (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,
    current_level INTEGER NOT NULL CHECK(current_level >= 0 AND current_level <= 3),
    max_achievable_level INTEGER NOT NULL CHECK(max_achievable_level >= 0 AND max_achievable_level <= 3),
    blocking_gaps TEXT,  -- JSON array of gap IDs
    level_0_achieved BOOLEAN DEFAULT FALSE,
    level_1_achieved BOOLEAN DEFAULT FALSE,
    level_2_achieved BOOLEAN DEFAULT FALSE,
    level_3_achieved BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Asymmetry metadata (from bidirectional-gaps.md)
CREATE TABLE IF NOT EXISTS ir_asymmetry_metadata (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,
    source_family TEXT NOT NULL,
    target_family TEXT NOT NULL,
    direction_difficulty INTEGER CHECK(direction_difficulty >= 1 AND direction_difficulty <= 5),
    reverse_difficulty INTEGER CHECK(reverse_difficulty >= 1 AND reverse_difficulty <= 5),
    asymmetry_ratio REAL,
    preserved_in_reverse BOOLEAN DEFAULT TRUE,
    notes TEXT
);

-- Decision resolutions (human decisions made during conversion)
CREATE TABLE IF NOT EXISTS ir_decision_resolutions (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,
    decision_point_id TEXT NOT NULL,  -- References decision_points table
    chosen_option TEXT NOT NULL,
    rationale TEXT,
    resolved_by TEXT,  -- 'human' or 'heuristic'
    resolved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Extend ir_gaps with Phase 3 fields
ALTER TABLE ir_gaps ADD COLUMN IF NOT EXISTS gap_pattern_id TEXT;
ALTER TABLE ir_gaps ADD COLUMN IF NOT EXISTS severity TEXT;
ALTER TABLE ir_gaps ADD COLUMN IF NOT EXISTS target_concept TEXT;
ALTER TABLE ir_gaps ADD COLUMN IF NOT EXISTS decision_point_id TEXT;
ALTER TABLE ir_gaps ADD COLUMN IF NOT EXISTS preservation_level INTEGER;

-- Indexes for new tables
CREATE INDEX IF NOT EXISTS idx_preservation_unit ON ir_preservation_status(unit_id);
CREATE INDEX IF NOT EXISTS idx_preservation_level ON ir_preservation_status(current_level);
CREATE INDEX IF NOT EXISTS idx_asymmetry_unit ON ir_asymmetry_metadata(unit_id);
CREATE INDEX IF NOT EXISTS idx_asymmetry_families ON ir_asymmetry_metadata(source_family, target_family);
CREATE INDEX IF NOT EXISTS idx_decisions_unit ON ir_decision_resolutions(unit_id);
CREATE INDEX IF NOT EXISTS idx_decisions_point ON ir_decision_resolutions(decision_point_id);
```

## Tasks (Detailed)

### 4.10 Validate IR Against Phase 0 Patterns

Verify the IR schema can represent actual extracted patterns:

1. Select 10 representative patterns from `patterns.sql`:
   - 3 type mappings (TS-001, TS-002, TS-003)
   - 3 memory patterns (MM-001, MM-002, MM-004)
   - 2 effect patterns (EF-001, EF-004)
   - 2 concurrency patterns (CC-001, CC-004)

2. For each pattern, show:
   - Source code example
   - IR representation at each relevant layer
   - Annotations required
   - Gap markers if applicable

3. Output: `analysis/ir-validation.md`

## Success Criteria

- [ ] All 5 layers fully specified with YAML schemas
- [ ] JSON schemas validate against examples
- [ ] Can represent all 54 gap patterns from Phase 3
- [ ] Partial extraction modes documented (function, type, signature)
- [ ] Gap markers integrated with Phase 3 pattern IDs
- [ ] Preservation level tracking in schema
- [ ] SQL extensions build on existing schema.sql
- [ ] 10 patterns validated against IR (task 4.10)

## Quality Gates

| Gate | Validation |
|------|------------|
| Schema completeness | All layer schemas have required fields |
| Pattern coverage | All 54 gap patterns expressible in annotations |
| Preservation integration | All 4 levels trackable per IR unit |
| Decision point linkage | 16 decision points referenceable from gaps |
| SQL compatibility | Extensions work with existing schema.sql |

## Effort Estimate

5-7 days

## Output Files

| File | Description |
|------|-------------|
| `docs/src/ir-schema/overview.md` | Architecture overview |
| `docs/src/ir-schema/layer-0.md` | Expression IR (optional layer) |
| `docs/src/ir-schema/layer-1.md` | Data Flow IR |
| `docs/src/ir-schema/layer-2.md` | Control Flow IR |
| `docs/src/ir-schema/layer-3.md` | Type IR |
| `docs/src/ir-schema/layer-4.md` | Structural IR |
| `docs/src/ir-schema/binary-formats.md` | Protobuf/MessagePack documentation |
| `<project>/docs/src/adr/008-ir-content-hashing.md` | Hashing algorithm decision (DONE) |
| `schemas/ir-v1.json` | JSON Schema definitions |
| `data/ir-schema.sql` | SQL schema extensions |
| `analysis/ir-validation.md` | Pattern validation results |

---

## Resolved Discussion Topics

### Topic 1: Serialization Formats (Protobuf, MessagePack)

**Resolution**: Documentation only, not implemented in this project.

**Rationale**: A future "universal extractor" CLI is planned but out of scope. This project documents the expected Protobuf schema to ensure future compatibility.

**Deliverable**: `docs/src/ir-schema/binary-formats.md` (documentation only)

### Topic 2: Incremental IR and Content Hashing

**Resolution**: Unified hashing using SHA-256.

**Rationale**: Single algorithm serves both deduplication and change detection, avoiding redundant hashes and inconsistent comparisons.

**Deliverable**: `<project>/docs/src/adr/008-ir-content-hashing.md` (full decision record - DONE)
