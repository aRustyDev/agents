# IR Schema Overview

The Intermediate Representation (IR) is a multi-layer architecture for capturing code semantics during language-to-language conversion.

**Version:** 1.0
**Generated:** 2026-02-04
**Task:** ai-f33.1

---

## 1. Design Goals

1. **Language Agnostic**: Represent code from any of the 9 supported language families
2. **Semantic Preservation**: Enable high-fidelity conversion with measurable preservation levels (0-3)
3. **Gap Awareness**: Annotate semantic gaps that cannot be automatically bridged
4. **Partial Extraction**: Support extracting subsets of code (functions, types, signatures)
5. **Incremental Processing**: Enable change detection via content hashing

---

## 2. Layer Architecture

The IR uses a 5-layer model, numbered 0-4 from most detailed to most abstract:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EXTRACTION (Source → IR)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Layer 4: Structural IR                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Modules, packages, namespaces                                        │   │
│  │ Public/private visibility boundaries                                 │   │
│  │ Import/export dependencies                                           │   │
│  │ Build/compilation units                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  Layer 3: Type IR                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Type definitions (ADTs, classes, interfaces, traits)                 │   │
│  │ Type relationships (subtyping, implements, extends)                  │   │
│  │ Generic/parametric types with variance                               │   │
│  │ Type constraints and bounds                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  Layer 2: Control Flow IR                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Function/method signatures                                           │   │
│  │ Control patterns (branch, loop, match, try)                          │   │
│  │ Effect annotations (pure, throws, async, unsafe)                     │   │
│  │ Concurrency patterns (spawn, await, channel)                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  Layer 1: Data Flow IR                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Variable bindings and scopes                                         │   │
│  │ Lifetimes and ownership tracking                                     │   │
│  │ Data transformations (map, filter, fold)                             │   │
│  │ Side effect tracking and dependency graphs                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  Layer 0: Expression IR (optional)                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Full AST representation                                              │   │
│  │ Operator semantics                                                   │   │
│  │ Literal values and constants                                         │   │
│  │ Source location spans                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                        SYNTHESIS (IR → Target)                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Layer Responsibilities

| Layer | Name | Responsibility | Key Constructs |
|-------|------|----------------|----------------|
| 4 | Structural | Code organization | module, import, export, definition |
| 3 | Type | Type system | type_def, type_param, type_ref, type_relationship |
| 2 | Control Flow | Execution structure | function, effect, block, terminator |
| 1 | Data Flow | Data dependencies | binding, lifetime, data_flow_node, transformation |
| 0 | Expression | AST details (optional) | expression, source_span |

### 2.2 Layer Relationships

**Top-down containment:**
- Layer 4 modules contain Layer 3 type definitions and Layer 2 function declarations
- Layer 3 types reference other types and are used in Layer 2 signatures
- Layer 2 functions have bodies represented as Layer 1 data flow graphs
- Layer 1 bindings optionally include Layer 0 expression details

**Cross-layer references:**
- Type references (TypeRef) can appear at any layer
- Annotations can attach to nodes at any layer
- Gap markers can appear anywhere semantic issues are detected

---

## 3. Extraction Modes

The IR supports partial extraction for different use cases:

| Mode | Layers Used | Use Case | Example |
|------|-------------|----------|---------|
| `full_module` | 0-4 | Complete codebase conversion | Converting entire Python package to Rust |
| `single_function` | 0-2 | Function-level conversion | Porting one algorithm implementation |
| `type_only` | 3-4 | Interface/type extraction | Generating TypeScript types from Rust structs |
| `signature_only` | 2-4 | API surface extraction | Creating FFI bindings |

### 3.1 Extraction Scope in IR

```yaml
module:
  id: ModuleId
  extraction_scope: full | partial
  metadata:
    extraction_mode: full_module | single_function | type_only | signature_only
```

When `extraction_scope: partial`:
- Some definitions may reference external types not included in the IR
- Function bodies may be omitted (Layer 0-1 empty)
- Import/export information may be incomplete

---

## 4. Semantic Annotations

Annotations are the primary mechanism for tracking conversion-relevant metadata. They integrate the 54 gap patterns identified in Phase 3.

### 4.1 Annotation Structure

```yaml
semantic_annotation:
  target: AnyId          # ID of the annotated node
  kind: AnnotationKind   # Type of annotation
  value: any             # Annotation-specific data
  confidence: 0.0-1.0    # For inferred annotations
  source: explicit | inferred | default | test_suite
  evidence: string[]?    # Supporting evidence
```

### 4.2 Annotation Categories

| Category | Count | Example Kinds |
|----------|-------|---------------|
| Type System | 16 | `inferred_type`, `nullability`, `hkt_specialization`, `variance_annotation` |
| Memory Model | 12 | `ownership_hint`, `lifetime_hint`, `mutability_analysis`, `arc_cycle_risk` |
| Effect System | 12 | `error_handling_conversion`, `null_to_option`, `evaluation_strategy` |
| Concurrency | 14 | `concurrency_model_conversion`, `channel_to_async`, `thread_safety` |

### 4.3 Cross-Cutting Annotations

| Annotation | Purpose | Reference |
|------------|---------|-----------|
| `preservation_level` | Track semantic fidelity (0-3) | `preservation-levels.md` |
| `decision_required` | Mark human decision points | `decision-points.md` (16 points) |
| `asymmetry_info` | Bidirectional conversion metadata | `bidirectional-gaps.md` |

---

## 5. Gap Markers

Gap markers flag semantic issues that may require human intervention or result in imperfect conversion.

### 5.1 Gap Marker Structure

```yaml
gap_marker:
  id: GapMarkerId
  location: AnyId           # Node where gap occurs
  gap_type: impossible | lossy | structural | idiomatic | runtime | semantic
  gap_pattern_id: string?   # Reference to Phase 3 pattern (e.g., "TS-001")
  severity: critical | high | medium | low
  description: string
  source_concept: string    # Source language concept
  target_concept: string?   # Target language equivalent (if any)
  suggested_mitigations: string[]
  decision_point_id: string?  # Link to human decision if needed
  preservation_level: 0-3   # Max achievable with this gap
```

### 5.2 Gap Distribution (from Phase 3)

| Gap Type | Count | Typical Mitigation |
|----------|-------|-------------------|
| impossible | 0 | Stub generation, redesign |
| lossy | 108 (33.8%) | Precision warnings, explicit casts |
| structural | 176 (55.0%) | Dual representation, transformation |
| idiomatic | 2 (0.6%) | Style rules |
| runtime | 22 (6.9%) | Shim libraries, feature detection |
| semantic | 12 (3.8%) | Annotations, caveats in output |

---

## 6. Preservation Levels

Every IR unit tracks its semantic preservation level:

| Level | Name | Definition |
|-------|------|------------|
| 0 | Syntactic | Target code compiles/parses |
| 1 | Semantic | Equivalent behavior for tested inputs |
| 2 | Idiomatic | Follows target language conventions |
| 3 | Optimized | Performance comparable to native implementation |

### 6.1 Preservation Tracking

```yaml
preservation_status:
  unit_id: AnyId
  current_level: 0-3
  max_achievable_level: 0-3
  blocking_gaps: GapMarkerId[]
  level_evidence:
    level_0: bool  # Syntax valid
    level_1: bool  # Tests pass
    level_2: bool  # Lint/style checks pass
    level_3: bool  # Performance benchmarks pass
```

### 6.2 Gap Impact on Preservation

| Gap Category | Max Achievable Level |
|--------------|---------------------|
| impossible | 0 (stub only) |
| lossy | 1 (semantic equivalent) |
| structural | 2 (idiomatic) |
| idiomatic | 2-3 |
| runtime | 1-2 (shim required) |
| semantic | 1 (with caveats) |

---

## 7. Content Hashing

IR units use SHA-256 content hashing for deduplication and change detection (see ADR-008).

### 7.1 Hash Computation

```python
import hashlib
import json

def compute_content_hash(content: dict) -> str:
    """SHA-256 of canonicalized JSON."""
    canonical = json.dumps(content, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
```

### 7.2 Hash Uses

| Use Case | Mechanism |
|----------|-----------|
| Deduplication | `UNIQUE(version_id, content_hash)` |
| Change detection | Compare hash across version_ids |
| Cache invalidation | Hash change triggers re-processing |
| Content addressing | Hash as stable reference ID |

---

## 8. Schema Versioning

### 8.1 Version Strategy

- IR schema versions use semantic versioning: `ir-v{major}.{minor}`
- Major version: Breaking schema changes
- Minor version: Additive changes (new optional fields)

### 8.2 Version Metadata

```yaml
module:
  metadata:
    extraction_version: "ir-v1.0"
    source_language: "python"
    source_file: "src/main.py"
    extraction_mode: full_module
```

### 8.3 Compatibility Rules

1. Readers should ignore unknown fields (forward compatibility)
2. Required fields never removed in minor versions
3. Field types never changed (use new field names instead)
4. Enums may add values in minor versions

---

## 9. Supported Language Families

The IR is designed to represent code from 9 language families:

| Family | Example Languages | Key Characteristics |
|--------|-------------------|---------------------|
| ML-FP | Haskell, OCaml, F# | HKT, pattern matching, immutability |
| BEAM | Erlang, Elixir | Actors, supervision, hot code reload |
| LISP | Clojure, Common Lisp, Racket | Homoiconicity, macros, dynamic |
| Systems | Rust, C, C++, Zig | Manual/ownership memory, unsafe |
| Dynamic | Python, Ruby, JavaScript, TypeScript | Duck typing, runtime metaprogramming |
| Managed-OOP | Java, C#, Kotlin | GC, classes, interfaces |
| Apple | Swift, Objective-C | ARC, protocols, optionals |
| Logic | Prolog | Unification, backtracking |
| Procedural | Go | Simplicity, goroutines, interfaces |

### 9.1 Family-Specific Considerations

| Family Pair | Difficulty | Key Gaps |
|-------------|------------|----------|
| Dynamic → Systems | 4 (Hard) | Type inference, memory management |
| ML-FP → Systems | 4 (Hard) | HKT, ownership |
| BEAM → Systems | 4 (Hard) | Actor model, GC |
| GC → Ownership | 4:1 asymmetry | Memory model fundamental mismatch |

---

## 10. File Organization

IR-related files in this project:

| File | Purpose |
|------|---------|
| `docs/src/ir-schema/overview.md` | This document |
| `docs/src/ir-schema/layer-{0-4}.md` | Per-layer documentation |
| `docs/src/ir-schema/binary-formats.md` | Protobuf/MessagePack specs |
| `docs/src/ir-schema/preservation-levels.md` | Preservation model |
| `docs/src/adr/008-ir-content-hashing.md` | Hashing decision |
| `schemas/ir-v1.json` | JSON Schema definitions |
| `data/schema.sql` | Base SQL schema |
| `data/ir-schema.sql` | Phase 4 schema extensions |

---

## 11. Cross-References

### Phase 3 Documents

| Document | Contents | Usage in IR |
|----------|----------|-------------|
| `gap-patterns.md` | 54 conversion patterns | Annotation kinds |
| `severity-matrix.md` | 9x9 difficulty matrix | Asymmetry metadata |
| `bidirectional-gaps.md` | Asymmetry analysis | Conversion planning |
| `decision-points.md` | 16 human decisions | Gap marker links |
| `ir-implications.md` | IR design recommendations | Layer mapping |

### Key Metrics from Phase 3

- **320 gaps classified**: 0 impossible, 108 lossy, 176 structural, 22 runtime, 12 semantic, 2 idiomatic
- **54 patterns documented**: 16 type, 12 memory, 12 effect, 14 concurrency
- **9 language families**: 81 conversion pairs in difficulty matrix
- **16 decision points**: Human choices that cannot be automated

---

## 12. Next Steps

1. **Layer Documentation** (4.2-4.6): Detailed schema for each layer
2. **JSON Schema** (4.10): Machine-readable schema definitions
3. **SQL Extensions** (4.9): Database schema for IR storage
4. **Validation** (4.11): Test IR against Phase 0 patterns

---

*Generated for Phase 4: IR Schema Design (ai-f33)*
