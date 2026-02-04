# Cross-Cutting Concerns

This document defines IR constructs that span all layers: semantic annotations, gap markers, preservation tracking, and asymmetry metadata.

**Version:** 1.0
**Generated:** 2026-02-04
**Task:** ai-f33.7

---

## 1. Overview

Cross-cutting concerns attach metadata to any IR node regardless of layer:

```
┌──────────────────────────────────────────────────────────────┐
│                        IR Node (any layer)                    │
├──────────────────────────────────────────────────────────────┤
│  Semantic Annotations    →  Conversion-relevant metadata      │
│  Gap Markers             →  Semantic issues and mitigations   │
│  Preservation Status     →  Quality level tracking            │
│  Asymmetry Metadata      →  Bidirectional conversion info     │
└──────────────────────────────────────────────────────────────┘
```

**Key principle**: Any node at any layer can have any combination of these concerns attached.

---

## 2. Semantic Annotations

Annotations provide conversion-relevant metadata discovered during analysis. They integrate the 54 gap patterns from Phase 3.

### 2.1 Annotation Structure

```yaml
semantic_annotation:
  id: AnnotationId
  target: AnyId              # ID of annotated node (any layer)
  kind: AnnotationKind       # One of 54 kinds (see §2.2)
  value: any                 # Kind-specific payload
  confidence: float          # 0.0-1.0 for inferred annotations
  source: AnnotationSource   # How annotation was determined
  evidence: string[]?        # Supporting evidence for inference
  created_at: timestamp
  created_by: string         # Tool or human identifier

AnnotationSource:
  - explicit    # Declared in source code
  - inferred    # Determined by static analysis
  - default     # Applied as language default
  - test_suite  # Derived from test execution
  - human       # Manually specified by user
```

### 2.2 Annotation Kinds (54 Total)

#### Type System Annotations (16)

| ID | Kind | Description | Value Schema |
|----|------|-------------|--------------|
| TS-001 | `inferred_type` | Dynamic → Static type inference | `{original, inferred, confidence, evidence[]}` |
| TS-002 | `nullability` | Nullable → Non-null tracking | `{source_nullability, target_representation, null_paths[]}` |
| TS-003 | `hkt_specialization` | HKT → No HKT specialization | `{original_hkt, specialized_types[], abstraction_lost}` |
| TS-004 | `gradual_type_coverage` | Gradual → Full static | `{coverage_percent, untyped_locations[]}` |
| TS-005 | `duck_type_interface` | Duck typing → Explicit interface | `{inferred_interface, methods[], structural_match}` |
| TS-006 | `type_alias_expansion` | Type alias resolution | `{alias_name, expanded_type, recursive}` |
| TS-007 | `generic_bounds` | Generic constraint mapping | `{source_bounds[], target_bounds[], lossy}` |
| TS-008 | `coercion_site` | Implicit → Explicit coercion | `{from_type, to_type, coercion_kind}` |
| TS-009 | `type_erasure_info` | Type erasure boundaries | `{erased_params[], runtime_available}` |
| TS-010 | `phantom_type` | Phantom type parameters | `{phantom_params[], purpose}` |
| TS-011 | `existential_type` | Existential type handling | `{existential_bounds, boxed}` |
| TS-012 | `dependent_type_approx` | Dependent type approximation | `{original_constraint, approximation, sound}` |
| TS-013 | `refinement_type` | Refinement type encoding | `{base_type, refinement_predicate, runtime_check}` |
| TS-014 | `variance_annotation` | Variance handling | `{declared, inferred, safe_covariant}` |
| TS-015 | `associated_type` | Associated type mapping | `{trait_type, concrete_type, default}` |
| TS-016 | `type_family` | Type family/function | `{family_name, instances[], open}` |

#### Memory Model Annotations (12)

| ID | Kind | Description | Value Schema |
|----|------|-------------|--------------|
| MM-001 | `gc_to_manual` | GC → Manual memory | `{allocation_sites[], deallocation_strategy}` |
| MM-002 | `ownership_hint` | GC → Ownership model | `{suggested_owner, lifetime, borrow_pattern}` |
| MM-003 | `ownership_transfer` | Ownership transfer point | `{from_scope, to_scope, transfer_kind}` |
| MM-004 | `mutability_analysis` | Mutable → Immutable | `{mutation_sites[], can_be_immutable, blocker}` |
| MM-005 | `lifetime_hint` | Lifetime inference | `{inferred_lifetime, scope_bound, elision_ok}` |
| MM-006 | `borrow_check_issue` | Potential borrow violation | `{conflict_type, locations[], suggested_fix}` |
| MM-007 | `arc_cycle_risk` | ARC cycle detection | `{cycle_path[], weak_ref_suggestion}` |
| MM-008 | `stack_vs_heap` | Allocation strategy | `{suggested_location, size_estimate, escape_analysis}` |
| MM-009 | `copy_vs_move` | Copy vs move semantics | `{type_id, suggested_semantics, reason}` |
| MM-010 | `interior_mutability` | Interior mutability pattern | `{cell_type, thread_safety, use_sites[]}` |
| MM-011 | `pinning_required` | Self-referential structure | `{self_ref_fields[], pin_strategy}` |
| MM-012 | `arena_allocation` | Arena/pool allocation hint | `{lifetime_group, arena_type}` |

#### Effect System Annotations (12)

| ID | Kind | Description | Value Schema |
|----|------|-------------|--------------|
| EF-001 | `error_handling_conversion` | Exceptions → Results | `{exception_types[], result_type, panic_on[]}` |
| EF-002 | `null_to_option` | Null → Option/Maybe | `{null_sources[], option_type, unwrap_sites[]}` |
| EF-003 | `checked_exception_mapping` | Checked → Unchecked | `{checked_exceptions[], handling_strategy}` |
| EF-004 | `monad_flattening` | Monads → Direct style | `{monad_type, flattened_representation, bind_sites[]}` |
| EF-005 | `effect_inference` | Inferred effect | `{effect_kind, evidence[], propagates_to[]}` |
| EF-006 | `purity_analysis` | Purity determination | `{is_pure, side_effects[], can_be_pure_with[]}` |
| EF-007 | `io_boundary` | IO effect boundary | `{io_operations[], isolation_strategy}` |
| EF-008 | `resource_management` | RAII/try-with-resources | `{resource_type, acquisition, release, scope}` |
| EF-009 | `evaluation_strategy` | Lazy → Strict | `{lazy_sites[], strictness_analysis, force_points[]}` |
| EF-010 | `algebraic_effect` | Algebraic effect handling | `{effect_type, handlers[], resumption}` |
| EF-011 | `effect_boundary` | Effect system boundary | `{inner_effects[], outer_effects[], boundary_handling}` |
| EF-012 | `continuation_capture` | Continuation/callback | `{capture_point, resume_point, cps_transform}` |

#### Concurrency Annotations (14)

| ID | Kind | Description | Value Schema |
|----|------|-------------|--------------|
| CC-001 | `concurrency_model_conversion` | Actors → Threads/Async | `{source_model, target_model, mapping_strategy}` |
| CC-002 | `shared_state_analysis` | Shared mutable state | `{shared_vars[], access_pattern, sync_needed}` |
| CC-003 | `lock_ordering` | Lock acquisition order | `{locks[], suggested_order, deadlock_risk}` |
| CC-004 | `channel_to_async` | CSP → Async/Await | `{channel_ops[], async_equivalent, buffering}` |
| CC-005 | `green_thread_mapping` | Green → OS threads | `{spawn_sites[], pool_strategy, blocking_calls[]}` |
| CC-006 | `stm_decomposition` | STM → Lock-based | `{transaction_blocks[], lock_granularity}` |
| CC-007 | `message_passing_pattern` | Message passing type | `{pattern, serialization, delivery_guarantee}` |
| CC-008 | `race_condition_risk` | Potential race | `{shared_access[], timing_dependent, mitigation}` |
| CC-009 | `supervision_conversion` | Supervision tree mapping | `{supervisor_strategy, restart_policy, child_specs[]}` |
| CC-010 | `async_boundary` | Sync/async boundary | `{boundary_type, blocking_risk, bridge_strategy}` |
| CC-011 | `atomicity_requirement` | Atomic operation need | `{operation, current_impl, atomic_alternative}` |
| CC-012 | `thread_safety` | Thread safety analysis | `{type_id, is_send, is_sync, unsafe_reason}` |
| CC-013 | `parallelism_hint` | Parallelization opportunity | `{loop_id, parallel_strategy, dependencies[]}` |
| CC-014 | `cancellation_handling` | Cancellation/timeout | `{cancellation_points[], cleanup_required, timeout_strategy}` |

### 2.3 Annotation Examples

#### Type Inference (TS-001)

```json
{
  "id": "ann-001",
  "target": "binding:data",
  "kind": "inferred_type",
  "value": {
    "original": "dynamic",
    "inferred": "String",
    "confidence": 0.85,
    "evidence": [
      "line 42: data.upper()",
      "line 58: return data + suffix"
    ]
  },
  "source": "inferred",
  "confidence": 0.85
}
```

#### Ownership Hint (MM-002)

```json
{
  "id": "ann-002",
  "target": "binding:connection",
  "kind": "ownership_hint",
  "value": {
    "suggested_owner": "ConnectionPool",
    "lifetime": "scoped",
    "borrow_pattern": {
      "shared_borrows": ["read_query"],
      "mutable_borrows": ["execute_transaction"],
      "transfers": ["close"]
    }
  },
  "source": "inferred",
  "confidence": 0.72
}
```

#### Error Handling (EF-001)

```json
{
  "id": "ann-003",
  "target": "function:fetch_user",
  "kind": "error_handling_conversion",
  "value": {
    "exception_types": ["ValueError", "NotFoundError"],
    "result_type": "Result<User, UserError>",
    "panic_on": [],
    "mapping": {
      "ValueError": "UserError::InvalidId",
      "NotFoundError": "UserError::NotFound"
    }
  },
  "source": "inferred",
  "confidence": 0.95
}
```

#### Thread Safety (CC-012)

```json
{
  "id": "ann-004",
  "target": "type:SharedCounter",
  "kind": "thread_safety",
  "value": {
    "type_id": "SharedCounter",
    "is_send": true,
    "is_sync": false,
    "unsafe_reason": "interior mutability without synchronization",
    "suggested_wrapper": "Arc<Mutex<Counter>>"
  },
  "source": "inferred",
  "confidence": 0.90
}
```

---

## 3. Gap Markers

Gap markers flag semantic issues that may affect conversion quality or require human intervention.

### 3.1 Gap Marker Structure

```yaml
gap_marker:
  id: GapMarkerId
  location: AnyId              # Node where gap occurs
  gap_type: GapType            # Category of gap
  gap_pattern_id: string?      # Reference to pattern (TS-001, MM-002, etc.)
  severity: Severity
  description: string
  source_concept: string       # What exists in source
  target_concept: string?      # Equivalent in target (if any)
  suggested_mitigations: string[]
  decision_point_id: string?   # Link to human decision if needed
  preservation_level: 0-3      # Max achievable with this gap
  automation_level: AutomationLevel
  affected_layers: int[]       # Which IR layers affected

GapType:
  - impossible    # Cannot be converted (0 found in Phase 3)
  - lossy         # Information lost (108 gaps, 33.8%)
  - structural    # Structural mismatch (176 gaps, 55.0%)
  - idiomatic     # Style difference (2 gaps, 0.6%)
  - runtime       # Runtime behavior difference (22 gaps, 6.9%)
  - semantic      # Meaning difference (12 gaps, 3.8%)

Severity:
  - critical   # Blocks conversion entirely
  - high       # Significant manual work required
  - medium     # Automated with review
  - low        # Cosmetic or minor

AutomationLevel:
  - none       # Requires human decision
  - partial    # Can suggest, human confirms
  - full       # Fully automated
```

### 3.2 Gap Distribution by Category

| Gap Type | Count | Percentage | Typical Automation |
|----------|-------|------------|-------------------|
| impossible | 0 | 0.0% | none (stub generation) |
| lossy | 108 | 33.8% | partial |
| structural | 176 | 55.0% | partial |
| idiomatic | 2 | 0.6% | full |
| runtime | 22 | 6.9% | partial |
| semantic | 12 | 3.8% | partial |
| **Total** | **320** | **100%** | |

### 3.3 Gap Marker Examples

#### Lossy Gap (HKT to No HKT)

```json
{
  "id": "gap-001",
  "location": "function:traverse",
  "gap_type": "lossy",
  "gap_pattern_id": "TS-003",
  "severity": "high",
  "description": "Higher-kinded type abstraction cannot be preserved in target language",
  "source_concept": "Traversable t => (a -> f b) -> t a -> f (t b)",
  "target_concept": "Specialized implementations for each container type",
  "suggested_mitigations": [
    "Generate specialized functions for List, Option, Either",
    "Use code generation for common patterns",
    "Accept duplication for type safety"
  ],
  "decision_point_id": "DP-003",
  "preservation_level": 1,
  "automation_level": "partial",
  "affected_layers": [2, 3]
}
```

#### Structural Gap (GC to Ownership)

```json
{
  "id": "gap-002",
  "location": "type:TreeNode",
  "gap_type": "structural",
  "gap_pattern_id": "MM-002",
  "severity": "high",
  "description": "Garbage-collected recursive type requires ownership design",
  "source_concept": "GC-managed tree with parent/child references",
  "target_concept": "Ownership-based tree (parent: Weak, children: Vec<Rc>)",
  "suggested_mitigations": [
    "Use Rc/Weak for parent-child relationships",
    "Consider arena allocation for tree lifetime",
    "Use indices instead of references"
  ],
  "decision_point_id": "DP-007",
  "preservation_level": 2,
  "automation_level": "partial",
  "affected_layers": [1, 3]
}
```

#### Runtime Gap (Async Model)

```json
{
  "id": "gap-003",
  "location": "module:server",
  "gap_type": "runtime",
  "gap_pattern_id": "CC-001",
  "severity": "medium",
  "description": "Actor-based concurrency model differs from async/await",
  "source_concept": "Erlang actors with message passing and supervision",
  "target_concept": "Rust async tasks with tokio runtime",
  "suggested_mitigations": [
    "Map mailbox to channel (mpsc/broadcast)",
    "Implement supervision as task wrapper",
    "Use actor library (actix) for closer mapping"
  ],
  "decision_point_id": "DP-012",
  "preservation_level": 2,
  "automation_level": "partial",
  "affected_layers": [2, 4]
}
```

---

## 4. Preservation Level Tracking

Every IR unit tracks its semantic preservation quality.

### 4.1 Preservation Levels

| Level | Name | Definition | Verification Method |
|-------|------|------------|---------------------|
| 0 | Syntactic | Target code compiles/parses | Compiler/parser success |
| 1 | Semantic | Equivalent behavior for tested inputs | Test suite passes |
| 2 | Idiomatic | Follows target language conventions | Linter/style checks pass |
| 3 | Optimized | Performance comparable to native | Benchmark comparison |

### 4.2 Preservation Status Schema

```yaml
preservation_status:
  id: PreservationStatusId
  unit_id: AnyId              # IR unit being tracked
  current_level: 0-3          # Currently achieved level
  max_achievable_level: 0-3   # Highest possible given gaps
  blocking_gaps: GapMarkerId[]  # Gaps preventing higher level
  level_evidence:
    level_0:
      achieved: bool
      verified_at: timestamp?
      verifier: string?        # Compiler, tool name
    level_1:
      achieved: bool
      test_coverage: float?    # 0.0-1.0
      passing_tests: int?
      total_tests: int?
    level_2:
      achieved: bool
      lint_warnings: int?
      style_score: float?      # 0.0-1.0
    level_3:
      achieved: bool
      benchmark_ratio: float?  # Target/source performance
      memory_ratio: float?
  progression_notes: string[]
```

### 4.3 Gap Impact on Preservation

| Gap Category | Max Achievable Level | Rationale |
|--------------|---------------------|-----------|
| impossible | 0 | Only stub can be generated |
| lossy | 1 | Semantic equivalence but information lost |
| structural | 2 | Can be idiomatic with restructuring |
| idiomatic | 2-3 | Style only, full preservation possible |
| runtime | 1-2 | Behavior may differ under edge cases |
| semantic | 1 | Behavior preserved with documented caveats |

### 4.4 Preservation Example

```json
{
  "id": "pres-001",
  "unit_id": "module:user_service",
  "current_level": 1,
  "max_achievable_level": 2,
  "blocking_gaps": ["gap-002", "gap-005"],
  "level_evidence": {
    "level_0": {
      "achieved": true,
      "verified_at": "2026-02-04T10:30:00Z",
      "verifier": "rustc 1.75.0"
    },
    "level_1": {
      "achieved": true,
      "test_coverage": 0.87,
      "passing_tests": 42,
      "total_tests": 42
    },
    "level_2": {
      "achieved": false,
      "lint_warnings": 3,
      "style_score": 0.82
    },
    "level_3": {
      "achieved": false,
      "benchmark_ratio": null,
      "memory_ratio": null
    }
  },
  "progression_notes": [
    "Level 2 blocked by non-idiomatic error handling (gap-002)",
    "Recommend refactoring to ? operator for Rust idioms"
  ]
}
```

---

## 5. Asymmetry Metadata

Tracks difficulty differences between forward and reverse conversions.

### 5.1 Asymmetry Schema

```yaml
asymmetry_info:
  id: AsymmetryId
  unit_id: AnyId?             # Specific unit, or null for general
  source_family: string       # e.g., "Dynamic"
  target_family: string       # e.g., "Systems"
  direction_difficulty: 1-5   # Forward conversion difficulty
  reverse_difficulty: 1-5     # Reverse conversion difficulty
  asymmetry_ratio: float      # direction / reverse (>1 means forward harder)
  preserved_in_reverse: bool  # Can info be recovered going back?
  key_asymmetries: AsymmetryDetail[]
  notes: string?

AsymmetryDetail:
  concept: string
  forward_action: string      # What happens going forward
  reverse_action: string      # What happens going back
  information_flow: gains | loses | preserves
```

### 5.2 Key Asymmetry Patterns

| Conversion | Forward | Reverse | Ratio | Key Factor |
|------------|---------|---------|-------|------------|
| GC → Ownership | 4 (Hard) | 1 (Easy) | 4:1 | Must design ownership; dropping it trivial |
| GC → Manual | 5 (V. Hard) | 1 (Easy) | 5:1 | Must track all allocations |
| Dynamic → Static | 3 (Mod) | 1 (Easy) | 3:1 | Must infer types; erasing trivial |
| Mutable → Immutable | 3 (Mod) | 1 (Easy) | 3:1 | Must prove no mutation needed |
| Actors → Threads | 3 (Mod) | 2 (Easy) | 1.5:1 | Losing isolation is risky |

### 5.3 Asymmetry Example

```json
{
  "id": "asym-001",
  "unit_id": "module:data_processor",
  "source_family": "Dynamic",
  "target_family": "Systems",
  "direction_difficulty": 4,
  "reverse_difficulty": 1,
  "asymmetry_ratio": 4.0,
  "preserved_in_reverse": false,
  "key_asymmetries": [
    {
      "concept": "type annotations",
      "forward_action": "Infer and add explicit types",
      "reverse_action": "Remove type annotations",
      "information_flow": "gains"
    },
    {
      "concept": "ownership model",
      "forward_action": "Design ownership hierarchy",
      "reverse_action": "Let GC handle memory",
      "information_flow": "gains"
    },
    {
      "concept": "lifetime annotations",
      "forward_action": "Add lifetime parameters",
      "reverse_action": "Remove (not applicable)",
      "information_flow": "gains"
    }
  ],
  "notes": "Converting Python to Rust gains significant information; reverse loses it"
}
```

---

## 6. Decision Points Integration

Gap markers can reference human decision points requiring intervention.

### 6.1 Decision Point Reference Schema

```yaml
decision_point_ref:
  id: string                  # e.g., "DP-001"
  category: DecisionCategory
  description: string
  options: DecisionOption[]
  guidance: string
  applicable_patterns: string[]  # Pattern IDs where this applies
  automation_hint: string?    # Suggested default

DecisionCategory:
  - error_handling
  - null_handling
  - memory_management
  - concurrency_model
  - type_representation
  - api_design
  - performance_tradeoff

DecisionOption:
  label: string
  description: string
  pros: string[]
  cons: string[]
  best_for: string[]
```

### 6.2 Key Decision Points (16 from Phase 3)

| ID | Category | Decision | Options |
|----|----------|----------|---------|
| DP-001 | error_handling | Exception vs Result | Result types, Exceptions, Error returns |
| DP-002 | error_handling | Panic behavior | Panic on unrecoverable, Always Result |
| DP-003 | type_representation | HKT specialization | Code generation, Manual specialization |
| DP-004 | null_handling | Null strategy | Option types, Null checks, Default values |
| DP-005 | null_handling | Unwrap policy | Explicit unwrap, Propagate Option |
| DP-006 | memory_management | Ownership strategy | Single owner, Shared (Rc/Arc), Arena |
| DP-007 | memory_management | Recursive types | Rc/Weak, Indices, Arena |
| DP-008 | memory_management | Interior mutability | RefCell, Mutex, Atomic |
| DP-009 | concurrency_model | Async runtime | tokio, async-std, Custom |
| DP-010 | concurrency_model | Channel buffering | Unbounded, Bounded, Rendezvous |
| DP-011 | concurrency_model | Synchronization | Mutex, RwLock, Atomic, Lock-free |
| DP-012 | concurrency_model | Actor mapping | actix, Channel-based, Manual |
| DP-013 | api_design | Visibility | Public API surface decisions |
| DP-014 | api_design | Error types | Unified error, Per-function errors |
| DP-015 | performance_tradeoff | Allocation strategy | Stack, Heap, Pool |
| DP-016 | performance_tradeoff | Copy vs Clone | Implicit copy, Explicit clone |

### 6.3 Decision Resolution Schema

```yaml
decision_resolution:
  id: DecisionResolutionId
  unit_id: AnyId
  decision_point_id: string   # DP-001, DP-002, etc.
  chosen_option: string
  rationale: string
  resolved_by: human | heuristic | default
  resolved_at: timestamp
  confidence: float?          # For heuristic decisions
  overridable: bool           # Can user change later?
```

---

## 7. Cross-Layer Application

### 7.1 Which Layers Support What

| Concern | Layer 0 | Layer 1 | Layer 2 | Layer 3 | Layer 4 |
|---------|---------|---------|---------|---------|---------|
| Semantic Annotations | ✓ | ✓ | ✓ | ✓ | ✓ |
| Gap Markers | ✓ | ✓ | ✓ | ✓ | ✓ |
| Preservation Status | - | ✓ | ✓ | ✓ | ✓ |
| Asymmetry Metadata | - | - | - | - | ✓ |

### 7.2 Typical Annotation Distribution

| Annotation Category | Primary Layers | Rationale |
|--------------------|----------------|-----------|
| Type System (TS-*) | 1, 3 | Type inference affects bindings and type defs |
| Memory Model (MM-*) | 1 | Ownership/lifetime tracked at binding level |
| Effect System (EF-*) | 2 | Effects tracked at function level |
| Concurrency (CC-*) | 2, 4 | Concurrency affects functions and modules |

---

## 8. SQL Schema Support

These cross-cutting concerns have corresponding SQL tables (see `data/ir-schema.sql`):

```sql
-- Semantic annotations
CREATE TABLE ir_annotations (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id),
    annotation_type TEXT NOT NULL,   -- TS-001, MM-002, etc.
    annotation_value TEXT NOT NULL,  -- JSON payload
    confidence REAL DEFAULT 1.0,
    source TEXT NOT NULL             -- explicit, inferred, default
);

-- Gap markers
CREATE TABLE ir_gap_markers (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id),
    gap_type TEXT NOT NULL,
    gap_pattern_id TEXT,
    severity TEXT,
    description TEXT,
    source_concept TEXT,
    target_concept TEXT,
    decision_point_id TEXT,
    preservation_level INTEGER
);

-- Preservation status
CREATE TABLE ir_preservation_status (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id),
    current_level INTEGER NOT NULL,
    max_achievable_level INTEGER NOT NULL,
    blocking_gaps TEXT,              -- JSON array
    level_0_achieved BOOLEAN,
    level_1_achieved BOOLEAN,
    level_2_achieved BOOLEAN,
    level_3_achieved BOOLEAN
);

-- Asymmetry metadata
CREATE TABLE ir_asymmetry_metadata (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id),
    source_family TEXT NOT NULL,
    target_family TEXT NOT NULL,
    direction_difficulty INTEGER,
    reverse_difficulty INTEGER,
    asymmetry_ratio REAL,
    preserved_in_reverse BOOLEAN
);

-- Decision resolutions
CREATE TABLE ir_decision_resolutions (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER REFERENCES ir_units(id),
    decision_point_id TEXT NOT NULL,
    chosen_option TEXT NOT NULL,
    rationale TEXT,
    resolved_by TEXT,
    resolved_at TIMESTAMP
);
```

---

## 9. Summary

### Annotation Coverage

| Category | Patterns | Automation |
|----------|----------|------------|
| Type System | 16 | 69% partial |
| Memory Model | 12 | 67% partial |
| Effect System | 12 | 75% partial |
| Concurrency | 14 | 64% partial |
| **Total** | **54** | **~69% partial** |

### Gap Distribution

| Type | Count | Max Preservation |
|------|-------|------------------|
| impossible | 0 | Level 0 |
| lossy | 108 | Level 1 |
| structural | 176 | Level 2 |
| idiomatic | 2 | Level 3 |
| runtime | 22 | Level 2 |
| semantic | 12 | Level 1 |

### Decision Points

- **16 key decision points** requiring human input
- Categories: error handling, null handling, memory, concurrency, API, performance
- Each gap marker can reference applicable decision points

---

## 10. Cross-References

| Document | Relationship |
|----------|--------------|
| `overview.md` | Architecture context |
| `layer-{0-4}.md` | Layer-specific schemas |
| `preservation-levels.md` | Detailed preservation model |
| `../analysis/gap-patterns.md` | All 54 pattern definitions |
| `../analysis/decision-points.md` | Full decision point catalog |
| `../analysis/bidirectional-gaps.md` | Asymmetry analysis |
| `../data/ir-schema.sql` | SQL table definitions |

---

*Generated for Phase 4: IR Schema Design (ai-f33.7)*
