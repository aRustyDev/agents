# Phase 4: IR Schema Design

Design the multi-layer Intermediate Representation architecture.

## Goal

Create a comprehensive IR schema that can represent code semantics from any supported language and enable high-fidelity conversion.

## Dependencies

- Phase 3: Semantic Gaps (informs what the IR must capture)

## Deliverables

- [ ] `docs/src/ir-schema/overview.md` - IR architecture documentation
- [ ] `docs/src/ir-schema/layer-{n}.md` - Per-layer documentation
- [ ] `schemas/ir-v1.proto` - Protobuf definitions
- [ ] `schemas/ir-v1.json` - JSON Schema definitions
- [ ] `data/ir-schema.sql` - SQL schema for IR storage

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
  metadata:
    source_file: string
    source_language: string
    extraction_version: string

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
  kind: pure | throws | async | unsafe | io
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

Full AST representation for deep analysis.

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

#### Semantic Annotations

```yaml
semantic_annotation:
  target: AnyId  # type, function, expression, etc.
  kind: purity | nullability | ownership | thread_safety | ...
  value: any
  confidence: float  # for inferred annotations
  source: explicit | inferred | default
```

#### Gap Markers

```yaml
gap_marker:
  id: GapMarkerId
  location: AnyId
  gap_type: impossible | lossy | structural | idiomatic
  description: string
  source_concept: string
  suggested_mitigations: string[]
```

### 4.8 Format Specifications

| Use Case | Format | Rationale |
|----------|--------|-----------|
| Human review | YAML/JSON | Readable, diffable |
| Tool interop | Protobuf | Fast, typed, versioned |
| Storage | SQLite | Queryable, incremental |
| Transport | MessagePack | Compact, fast |

### 4.9 Incremental IR Design

```yaml
incremental_unit:
  id: UnitId
  hash: ContentHash  # for change detection
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
      old_hash: ContentHash?
      new_hash: ContentHash?
      old_content: LayerContent?
      new_content: LayerContent?
```

## SQL Schema for IR Storage

```sql
-- IR versions
CREATE TABLE ir_versions (
    id INTEGER PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_language TEXT NOT NULL,
    source_path TEXT,
    extraction_tool_version TEXT,
    notes TEXT
);

-- IR units (atomic pieces of IR)
CREATE TABLE ir_units (
    id INTEGER PRIMARY KEY,
    version_id INTEGER REFERENCES ir_versions(id),
    layer INTEGER NOT NULL,  -- 0-4
    unit_type TEXT NOT NULL,  -- module, type, function, binding, expression
    content_hash TEXT NOT NULL,
    content_json TEXT NOT NULL,  -- JSON representation
    UNIQUE(version_id, content_hash)
);

-- IR dependencies
CREATE TABLE ir_dependencies (
    from_unit_id INTEGER REFERENCES ir_units(id),
    to_unit_id INTEGER REFERENCES ir_units(id),
    dependency_type TEXT NOT NULL,  -- uses, extends, imports, calls
    PRIMARY KEY (from_unit_id, to_unit_id, dependency_type)
);

-- Semantic annotations
CREATE TABLE ir_annotations (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id),
    annotation_type TEXT NOT NULL,
    annotation_value TEXT NOT NULL,  -- JSON
    confidence REAL DEFAULT 1.0,
    source TEXT NOT NULL  -- explicit, inferred, default
);

-- Gap markers
CREATE TABLE ir_gaps (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id),
    gap_type TEXT NOT NULL,
    description TEXT,
    source_concept TEXT,
    mitigations TEXT  -- JSON array
);

-- Indexes
CREATE INDEX idx_units_version ON ir_units(version_id);
CREATE INDEX idx_units_layer ON ir_units(layer);
CREATE INDEX idx_deps_from ON ir_dependencies(from_unit_id);
CREATE INDEX idx_deps_to ON ir_dependencies(to_unit_id);
```

## Success Criteria

- [ ] All 5 layers fully specified
- [ ] Protobuf schemas compile cleanly
- [ ] JSON schemas validate
- [ ] Can represent patterns from Phase 0 extraction
- [ ] Incremental update design verified
- [ ] Gap markers integrated into schema

## Effort Estimate

5-7 days

## Output Files

| File | Description |
|------|-------------|
| `docs/src/ir-schema/overview.md` | Architecture overview |
| `docs/src/ir-schema/layer-0.md` | Expression IR |
| `docs/src/ir-schema/layer-1.md` | Data Flow IR |
| `docs/src/ir-schema/layer-2.md` | Control Flow IR |
| `docs/src/ir-schema/layer-3.md` | Type IR |
| `docs/src/ir-schema/layer-4.md` | Structural IR |
| `schemas/ir-v1.proto` | Protobuf definitions |
| `schemas/ir-v1.json` | JSON Schema definitions |
| `data/ir-schema.sql` | SQL storage schema |
