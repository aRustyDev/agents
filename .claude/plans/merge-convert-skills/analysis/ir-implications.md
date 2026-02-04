# IR Design Implications

Synthesis of Phase 3 gap analysis into concrete Intermediate Representation (IR) design recommendations.

**Generated:** 2026-02-04
**Task:** ai-p29.9
**Input Data:**
- severity-matrix.md (9x9 family difficulty matrix)
- gap-patterns.md (54 patterns across 4 categories)
- bidirectional-gaps.md (asymmetry analysis)
- gap-classification.md (320 gaps in 6 categories)
- preservation-levels.md (4 semantic preservation levels)
- schema.sql (base database schema)

---

## 1. Gap Category to IR Layer Mapping

### 1.1 Primary Mapping Table

| Gap Category | Primary Layer | Secondary Layer | IR Representation | Automation |
|--------------|---------------|-----------------|-------------------|------------|
| **impossible** | Layer 2 (Semantic Core) | Layer 3 (Target Lowering) | Rejection marker + stub generation | none |
| **lossy** | Layer 2 (Semantic Core) | Layer 1 (Abstract Syntax) | Loss annotation + precision warning | partial |
| **structural** | Layer 1 (Abstract Syntax) | Layer 2 (Semantic Core) | Dual representation preserved | partial |
| **idiomatic** | Layer 3 (Target Lowering) | - | Style transform rules | full |
| **runtime** | Layer 0 (Concrete Syntax) | Layer 2 (Semantic Core) | Runtime shim or redesign flag | partial |
| **semantic** | Layer 2 (Semantic Core) | - | Semantic annotation + caveat | partial |

### 1.2 Layer Definitions

```
Layer 0: Concrete Syntax
  - Source-specific AST
  - Preserves comments, formatting hints
  - Language-specific keywords and operators

Layer 1: Abstract Syntax
  - Language-agnostic structure
  - Normalized control flow
  - Generic data structure representations

Layer 2: Semantic Core
  - Typed and annotated
  - Effect tracking
  - Ownership/lifetime hints
  - Semantic equivalence guarantees

Layer 3: Target Lowering
  - Target-specific optimizations
  - Idiom application
  - Performance hints
```

### 1.3 Gap Distribution by Layer

| IR Layer | Gap Categories Handled | Pattern Count | Priority |
|----------|----------------------|---------------|----------|
| Layer 0 | runtime (partial) | 14 | P2 |
| Layer 1 | structural, lossy (partial) | 28 | P1 |
| Layer 2 | impossible, lossy, semantic, runtime (partial) | 32 | P0 |
| Layer 3 | idiomatic | 8 | P3 |

---

## 2. Annotation Requirements by Pattern

### 2.1 Type System Patterns (16 patterns)

#### Pattern TS-001: Dynamic to Static Typing

**Layer:** 2 (Semantic Core)
**Severity:** high
**Automation:** partial

**Annotation Type:** `@inferred_type`

**Required Fields:**
- `original_type: "any" | "dynamic" | "object"`
- `inferred_type: "<concrete type>"`
- `confidence: 0.0-1.0`
- `inference_source: "usage" | "annotation" | "default" | "test_suite"`

**IR Node:**
```json
{
  "node": "binding",
  "name": "data",
  "type": {
    "concrete": "String",
    "annotations": {
      "@inferred_type": {
        "original": "dynamic",
        "inferred": "String",
        "confidence": 0.85,
        "source": "usage",
        "evidence": ["line 42: data.upper()", "line 58: return data + suffix"]
      }
    }
  }
}
```

**Preservation Level:** Max Level 1 without human verification

---

#### Pattern TS-002: Nullable to Non-Null Types

**Layer:** 2 (Semantic Core)
**Severity:** medium
**Automation:** partial

**Annotation Type:** `@nullability`

**Required Fields:**
- `source_nullability: "nullable" | "non_null" | "unknown"`
- `target_representation: "Option" | "Maybe" | "null_check"`
- `null_check_locations: [line_numbers]`

**IR Node:**
```json
{
  "node": "function_return",
  "type": {
    "base": "User",
    "annotations": {
      "@nullability": {
        "source": "nullable",
        "target": "Option<User>",
        "null_paths": [
          {"condition": "user == null", "line": 15},
          {"condition": "db.find() returns null", "line": 12}
        ]
      }
    }
  }
}
```

**Preservation Level:** Max Level 2

---

#### Pattern TS-003: Higher-Kinded Types to No HKT

**Layer:** 2 (Semantic Core)
**Severity:** high
**Automation:** none

**Annotation Type:** `@hkt_specialization`

**Required Fields:**
- `original_abstraction: "Functor" | "Monad" | "Traversable" | ...`
- `specializations: [{container, implementation}]`
- `loss_acknowledged: boolean`
- `user_decision_required: true`

**IR Node:**
```json
{
  "node": "type_class_use",
  "abstraction": "Functor",
  "annotations": {
    "@hkt_specialization": {
      "original": "fmap :: Functor f => (a -> b) -> f a -> f b",
      "specializations": [
        {"container": "List", "impl": "mapList"},
        {"container": "Option", "impl": "mapOption"},
        {"container": "Result", "impl": "mapResult"}
      ],
      "loss": "abstraction_over_containers",
      "user_decision_required": true,
      "mitigation": "code_generation_for_new_containers"
    }
  }
}
```

**Preservation Level:** Max Level 1 (with loss marker)

---

#### Pattern TS-010: Type Classes to Interface Dispatch

**Layer:** 2 (Semantic Core)
**Severity:** high
**Automation:** partial

**Annotation Type:** `@type_class_conversion`

**Required Fields:**
- `source_type_class: string`
- `target_pattern: "interface" | "protocol" | "trait"`
- `retroactive_conformance_lost: boolean`
- `instances: [{type, methods}]`

**IR Node:**
```json
{
  "node": "type_class_def",
  "name": "Eq",
  "annotations": {
    "@type_class_conversion": {
      "source": "class Eq a where (==) :: a -> a -> Bool",
      "target_pattern": "interface",
      "generated_interface": "Eq<T>",
      "retroactive_lost": true,
      "orphan_instances": ["Eq Int", "Eq String"],
      "mitigation": "wrapper_types_for_third_party"
    }
  }
}
```

**Preservation Level:** Max Level 1 (retroactive conformance lost)

---

#### Pattern TS-011: Dependent Types to Runtime Checks

**Layer:** 2 (Semantic Core)
**Severity:** critical
**Automation:** none

**Annotation Type:** `@dependent_type_erasure`

**Required Fields:**
- `original_predicate: string`
- `runtime_check: string`
- `proof_lost: boolean`
- `test_coverage_recommended: boolean`

**IR Node:**
```json
{
  "node": "type_def",
  "name": "Vec",
  "annotations": {
    "@dependent_type_erasure": {
      "original": "Vect n a -- length encoded in type",
      "target": "Vec<T> -- length is runtime value",
      "proof_lost": true,
      "guarantees_lost": ["length_preservation", "bounds_safety"],
      "runtime_checks_added": [
        "assert!(result.len() == input.len())",
        "bounds check on index"
      ],
      "test_coverage": "property_based_testing_recommended"
    }
  }
}
```

**Preservation Level:** Max Level 0 (with extensive warnings)

---

### 2.2 Memory Model Patterns (12 patterns)

#### Pattern MM-001: GC to Manual Allocation

**Layer:** 2 (Semantic Core)
**Severity:** critical
**Automation:** none

**Annotation Type:** `@ownership_transfer`

**Required Fields:**
- `allocation_site: line_number`
- `deallocation_responsibility: "caller" | "callee" | "shared"`
- `lifetime_region: string`
- `potential_leaks: [locations]`
- `potential_use_after_free: [locations]`

**IR Node:**
```json
{
  "node": "allocation",
  "type": "String",
  "annotations": {
    "@ownership_transfer": {
      "source_memory_model": "GC",
      "target_memory_model": "manual",
      "allocation": {"line": 12, "function": "create_string"},
      "ownership": "caller_must_free",
      "lifetime": "until_caller_frees",
      "risks": [
        {"type": "leak", "if": "caller forgets to free"},
        {"type": "use_after_free", "if": "reference retained after free"}
      ],
      "mitigation": "RAII_wrapper_recommended"
    }
  }
}
```

**Preservation Level:** Max Level 1 (requires extensive human review)

---

#### Pattern MM-002: GC to Ownership/Borrowing

**Layer:** 2 (Semantic Core)
**Severity:** high
**Automation:** partial

**Annotation Type:** `@ownership_hint`

**Required Fields:**
- `recommended_ownership: "owned" | "borrowed" | "shared" | "mutable_borrow"`
- `lifetime_annotation: string | null`
- `clone_recommendation: boolean`
- `interior_mutability_needed: boolean`

**IR Node:**
```json
{
  "node": "parameter",
  "name": "items",
  "annotations": {
    "@ownership_hint": {
      "source": "passed by reference (Python)",
      "analysis": {
        "mutated": false,
        "returned": true,
        "stored": false,
        "escapes_function": false
      },
      "recommendation": {
        "primary": "&[T] (borrowed slice)",
        "alternative": "Vec<T> (if mutation needed)",
        "rationale": "no mutation, iteration only"
      },
      "lifetime": "'a (tied to input)",
      "clone_if": "mutation_needed_while_iterating"
    }
  }
}
```

**Preservation Level:** Max Level 2

---

#### Pattern MM-004: Mutable Default to Immutable Default

**Layer:** 2 (Semantic Core)
**Severity:** medium
**Automation:** partial

**Annotation Type:** `@mutability_analysis`

**Required Fields:**
- `mutation_sites: [line_numbers]`
- `can_be_immutable: boolean`
- `transformation_strategy: "rebind" | "persistent_ds" | "state_monad"`

**IR Node:**
```json
{
  "node": "binding",
  "name": "items",
  "annotations": {
    "@mutability_analysis": {
      "source_mutability": "mutable",
      "mutation_sites": [
        {"line": 15, "operation": "append"},
        {"line": 22, "operation": "remove"}
      ],
      "analysis": {
        "can_eliminate_mutation": true,
        "strategy": "rebuild_with_fold"
      },
      "transformation": {
        "original": "items.append(x)",
        "target": "items = [...items, x]"
      }
    }
  }
}
```

**Preservation Level:** Max Level 2

---

#### Pattern MM-010: Per-Process Heap to Shared Heap

**Layer:** 2 (Semantic Core)
**Severity:** medium
**Automation:** partial

**Annotation Type:** `@isolation_boundary`

**Required Fields:**
- `process_boundary: boolean`
- `data_copied_across: [types]`
- `synchronization_needed: boolean`
- `race_condition_risks: [descriptions]`

**IR Node:**
```json
{
  "node": "message_send",
  "annotations": {
    "@isolation_boundary": {
      "source_model": "per_process_heap",
      "target_model": "shared_heap",
      "data_crossing_boundary": ["result", "state"],
      "in_source": "data copied on send",
      "in_target": "data shared (aliased)",
      "synchronization_required": true,
      "suggested_primitive": "Arc<Mutex<T>>",
      "race_risks": [
        "concurrent modification of result",
        "data race if not synchronized"
      ]
    }
  }
}
```

**Preservation Level:** Max Level 1 (isolation guarantees lost)

---

### 2.3 Effect System Patterns (12 patterns)

#### Pattern EF-001: Exceptions to Result/Either

**Layer:** 2 (Semantic Core)
**Severity:** high
**Automation:** partial

**Annotation Type:** `@error_handling_conversion`

**Required Fields:**
- `exception_types: [type_names]`
- `result_type: string`
- `propagation_sites: [line_numbers]`
- `catch_sites: [line_numbers]`

**IR Node:**
```json
{
  "node": "function",
  "name": "find_user",
  "annotations": {
    "@error_handling_conversion": {
      "source_pattern": "throws",
      "target_pattern": "Result<T, E>",
      "exceptions": [
        {"type": "UserNotFoundException", "maps_to": "UserError::NotFound"},
        {"type": "DatabaseException", "maps_to": "UserError::DbError"}
      ],
      "propagation": {
        "original": "throws clause",
        "target": "? operator"
      },
      "catch_conversions": [
        {"line": 45, "original": "try-catch", "target": "match on Result"}
      ]
    }
  }
}
```

**Preservation Level:** Max Level 2

---

#### Pattern EF-004: Monadic Effects to Direct Style

**Layer:** 2 (Semantic Core)
**Severity:** high
**Automation:** partial

**Annotation Type:** `@monad_flattening`

**Required Fields:**
- `monad_type: string`
- `bind_sites: [line_numbers]`
- `effect_type: "IO" | "State" | "Reader" | "Writer" | ...`
- `direct_style_equivalent: string`

**IR Node:**
```json
{
  "node": "do_block",
  "annotations": {
    "@monad_flattening": {
      "source_monad": "IO",
      "binds": [
        {"line": 10, "var": "response", "expr": "httpGet url"},
        {"line": 11, "var": "parsed", "expr": "parseJson response"}
      ],
      "target_style": "sequential_statements",
      "transformation": {
        "do_notation": "do { x <- action1; y <- action2; return (x, y) }",
        "direct_style": "x = action1(); y = action2(); return (x, y)"
      },
      "effect_tracking_lost": true,
      "mitigation": "document_side_effects"
    }
  }
}
```

**Preservation Level:** Max Level 1 (effect tracking lost)

---

#### Pattern EF-009: Lazy to Strict Evaluation

**Layer:** 2 (Semantic Core)
**Severity:** high
**Automation:** partial

**Annotation Type:** `@evaluation_strategy`

**Required Fields:**
- `laziness_usage: "infinite_structure" | "deferred_computation" | "memoization"`
- `strict_equivalent: string | null`
- `impossible_patterns: [descriptions]`

**IR Node:**
```json
{
  "node": "binding",
  "name": "naturals",
  "annotations": {
    "@evaluation_strategy": {
      "source": "lazy",
      "target": "strict",
      "pattern": "infinite_list",
      "analysis": {
        "is_infinite": true,
        "consumption_pattern": "take_first_n",
        "max_consumed": "variable"
      },
      "transformation": {
        "strategy": "iterator",
        "target_type": "impl Iterator<Item = u64>",
        "bounded_alternative": "0..limit"
      },
      "if_truly_infinite": {
        "strategy": "generator_or_stream",
        "user_must_bound": true
      }
    }
  }
}
```

**Preservation Level:** Max Level 1 (infinite structures impossible)

---

### 2.4 Concurrency Patterns (14 patterns)

#### Pattern CC-001: Actors to Threads

**Layer:** 2 (Semantic Core)
**Severity:** high
**Automation:** partial

**Annotation Type:** `@concurrency_model_conversion`

**Required Fields:**
- `actor_state: [field_types]`
- `message_types: [types]`
- `isolation_guarantees_lost: boolean`
- `synchronization_primitive: string`

**IR Node:**
```json
{
  "node": "actor_definition",
  "name": "Counter",
  "annotations": {
    "@concurrency_model_conversion": {
      "source_model": "actor",
      "target_model": "shared_memory_threads",
      "state": ["count: int"],
      "messages": [
        {"name": "increment", "handler": "count += 1"},
        {"name": "get", "handler": "return count"}
      ],
      "transformation": {
        "state_to": "AtomicInteger or Mutex<i32>",
        "mailbox_to": "method_calls",
        "isolation": "lost (shared memory)"
      },
      "guarantees_lost": [
        "message_ordering",
        "failure_isolation",
        "location_transparency"
      ],
      "supervision_to": "try-catch with restart logic"
    }
  }
}
```

**Preservation Level:** Max Level 1 (isolation lost)

---

#### Pattern CC-009: Supervision Trees to Exception Handling

**Layer:** 2 (Semantic Core)
**Severity:** high
**Automation:** partial

**Annotation Type:** `@supervision_conversion`

**Required Fields:**
- `supervision_strategy: "one_for_one" | "one_for_all" | "rest_for_one"`
- `restart_policy: "permanent" | "transient" | "temporary"`
- `exception_handling_equivalent: string`

**IR Node:**
```json
{
  "node": "supervisor",
  "name": "AppSupervisor",
  "annotations": {
    "@supervision_conversion": {
      "source": "OTP Supervisor",
      "strategy": "one_for_one",
      "children": [
        {"name": "Worker", "restart": "permanent"},
        {"name": "Cache", "restart": "temporary"}
      ],
      "target_pattern": "retry_loop_with_backoff",
      "transformation": {
        "permanent": "while(true) { try { run() } catch { restart() } }",
        "temporary": "try { run() } catch { log_and_continue() }",
        "transient": "retry_n_times(3)"
      },
      "semantics_lost": [
        "child_dependency_restart",
        "max_restart_intensity",
        "graceful_shutdown_ordering"
      ],
      "library_recommendation": "resilience4j or similar"
    }
  }
}
```

**Preservation Level:** Max Level 1 (supervision semantics lost)

---

## 3. Asymmetry Handling

Based on bidirectional-gaps.md analysis, the IR must handle asymmetric conversions differently.

### 3.1 Information Preservation for Hard-Direction Conversions

| Hard Direction | Information to Preserve | IR Annotation |
|----------------|------------------------|---------------|
| Dynamic to Static | All inferred types | `@inferred_type` with confidence |
| GC to Ownership | Ownership hints, lifetimes | `@ownership_hint`, `@lifetime_region` |
| Impure to Pure | Effect boundaries | `@effect_boundary`, `@purity_marker` |
| Mutable to Immutable | Mutation graph | `@mutability_analysis` |
| Threads to Actors | State isolation points | `@isolation_boundary` |

### 3.2 Safe Discard for Easy-Direction Conversions

| Easy Direction | Information Safe to Discard | Rationale |
|----------------|----------------------------|-----------|
| Static to Dynamic | Type annotations | Runtime handles types |
| Ownership to GC | Lifetime annotations | GC handles memory |
| Pure to Impure | Effect markers | Effects become implicit |
| Immutable to Mutable | Immutability markers | Mutation allowed |
| Result to Exception | Error type mapping | Catch handles all |

### 3.3 Bidirectional Annotation Strategy

For every annotation, track whether it was:
- **Explicit**: Present in source code
- **Inferred**: Derived through analysis
- **Default**: Applied based on target language conventions

```json
{
  "annotation": "@inferred_type",
  "origin": "inferred",
  "confidence": 0.85,
  "reversible": true,
  "reverse_strategy": "emit_as_comment_or_drop"
}
```

### 3.4 Asymmetry Ratio Impact on IR Design

| Asymmetry Ratio | IR Strategy | User Interaction |
|-----------------|-------------|------------------|
| 4:1+ (GC to Ownership) | Full annotation required | Human decision points |
| 2:1 - 3:1 (Type inference) | Annotation + confidence | Review recommended |
| 1:1 (Symmetric) | Bidirectional annotations | Minimal intervention |
| 0.5:1 (Easy direction) | Minimal annotation | Automatic |

---

## 4. Preservation Level Integration

### 4.1 Gap Category to Maximum Preservation Level

| Gap Category | Max Level | Conditions for Max | Typical Level |
|--------------|-----------|-------------------|---------------|
| **impossible** | 0 (with loss) | User acknowledges loss, stub provided | 0 |
| **lossy** | 1 | Semantic equivalent with warnings | 1 |
| **structural** | 2 | Idiom transforms applied correctly | 2 |
| **idiomatic** | 3 | Style transforms + optimization | 2-3 |
| **runtime** | 1-2 | Shims or redesign accepted | 1 |
| **semantic** | 1 | Caveats documented, tests pass | 1 |

### 4.2 Preservation Level Achievement Criteria

#### Level 0 (Syntactically Valid)
- All gap categories can achieve
- IR produces parseable output
- Type errors may exist

#### Level 1 (Semantically Equivalent)
- Requires: lossy, structural, idiomatic, runtime, semantic handling
- Blocked by: impossible gaps
- Tests from source pass on target

#### Level 2 (Idiomatically Correct)
- Requires: structural and idiomatic gap handling
- Blocked by: impossible, lossy (without mitigation)
- Native developer approves style

#### Level 3 (Optimized)
- Requires: All gap types handled + performance optimization
- Blocked by: impossible, lossy, runtime gaps
- Benchmarks meet targets

### 4.3 IR Annotations for Preservation Tracking

```json
{
  "unit_id": 42,
  "preservation": {
    "current_level": 1,
    "max_achievable": 2,
    "blockers": [
      {
        "gap_id": "TS-003",
        "category": "lossy",
        "description": "HKT abstraction lost",
        "blocks_level": 2
      }
    ],
    "path_to_next_level": [
      "Apply idiom transforms",
      "Review with native developer"
    ]
  }
}
```

---

## 5. Schema Extensions

### 5.1 IR Gap Annotations Table

```sql
-- IR gap annotations for tracking gaps in converted code
CREATE TABLE IF NOT EXISTS ir_gap_annotations (
    id INTEGER PRIMARY KEY,
    ir_unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,
    gap_pattern_id TEXT NOT NULL,  -- Pattern ID like 'TS-001', 'MM-002'
    gap_category TEXT NOT NULL,    -- impossible, lossy, structural, idiomatic, runtime, semantic
    severity TEXT NOT NULL,        -- critical, high, medium, low
    layer INTEGER NOT NULL,        -- 0-3

    -- Annotation details
    annotation_type TEXT NOT NULL,  -- e.g., '@inferred_type', '@ownership_hint'
    annotation_json TEXT NOT NULL,  -- Full annotation as JSON

    -- Resolution status
    mitigation_applied TEXT,        -- Description of mitigation if any
    user_decision_required BOOLEAN DEFAULT FALSE,
    user_decision TEXT,             -- User's choice if decision was required

    -- Preservation impact
    max_preservation_level INTEGER, -- 0-3, what level this gap allows
    preservation_blocker BOOLEAN DEFAULT FALSE,

    -- Metadata
    confidence REAL DEFAULT 1.0,    -- For inferred annotations
    source TEXT NOT NULL,           -- 'explicit', 'inferred', 'default'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(ir_unit_id, gap_pattern_id)
);

CREATE INDEX IF NOT EXISTS idx_gap_annotations_unit ON ir_gap_annotations(ir_unit_id);
CREATE INDEX IF NOT EXISTS idx_gap_annotations_pattern ON ir_gap_annotations(gap_pattern_id);
CREATE INDEX IF NOT EXISTS idx_gap_annotations_category ON ir_gap_annotations(gap_category);
CREATE INDEX IF NOT EXISTS idx_gap_annotations_severity ON ir_gap_annotations(severity);
CREATE INDEX IF NOT EXISTS idx_gap_annotations_decision ON ir_gap_annotations(user_decision_required);
```

### 5.2 IR Asymmetry Metadata Table

```sql
-- Track asymmetric conversion metadata
CREATE TABLE IF NOT EXISTS ir_asymmetry_metadata (
    id INTEGER PRIMARY KEY,
    ir_version_id INTEGER REFERENCES ir_versions(id) ON DELETE CASCADE,
    source_family TEXT NOT NULL,
    target_family TEXT NOT NULL,

    -- Asymmetry analysis
    conversion_difficulty INTEGER NOT NULL,  -- 1-5
    reverse_difficulty INTEGER NOT NULL,     -- 1-5
    asymmetry_ratio REAL NOT NULL,           -- forward/reverse

    -- Direction-specific annotations
    hard_direction_annotations TEXT,  -- JSON array of required annotations
    easy_direction_discards TEXT,     -- JSON array of safe-to-discard items

    -- Preservation potential
    max_preservation_forward INTEGER,  -- 0-3
    max_preservation_reverse INTEGER,  -- 0-3

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(ir_version_id, source_family, target_family)
);
```

### 5.3 IR Preservation Tracking Table

```sql
-- Track preservation level for each IR unit
CREATE TABLE IF NOT EXISTS ir_preservation_status (
    id INTEGER PRIMARY KEY,
    ir_unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,

    -- Current status
    current_level INTEGER NOT NULL,       -- 0-3
    max_achievable_level INTEGER NOT NULL, -- 0-3

    -- Blockers
    blocker_gaps TEXT,  -- JSON array of gap IDs blocking next level

    -- Level 0 criteria
    level_0_compiles BOOLEAN DEFAULT FALSE,
    level_0_parses BOOLEAN DEFAULT FALSE,

    -- Level 1 criteria
    level_1_tests_pass BOOLEAN DEFAULT FALSE,
    level_1_edge_cases_handled BOOLEAN DEFAULT FALSE,
    level_1_semantically_equivalent BOOLEAN DEFAULT FALSE,

    -- Level 2 criteria
    level_2_idiomatic BOOLEAN DEFAULT FALSE,
    level_2_linter_passes BOOLEAN DEFAULT FALSE,
    level_2_native_review_approved BOOLEAN DEFAULT FALSE,

    -- Level 3 criteria
    level_3_optimized BOOLEAN DEFAULT FALSE,
    level_3_benchmarked BOOLEAN DEFAULT FALSE,
    level_3_profiled BOOLEAN DEFAULT FALSE,

    -- Timestamps
    level_achieved_at TEXT,  -- JSON object with timestamps per level
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(ir_unit_id)
);
```

### 5.4 Decision Point Resolution Table

```sql
-- Track user decisions for gaps requiring human input
CREATE TABLE IF NOT EXISTS ir_decision_resolutions (
    id INTEGER PRIMARY KEY,
    ir_unit_id INTEGER REFERENCES ir_units(id) ON DELETE CASCADE,
    gap_annotation_id INTEGER REFERENCES ir_gap_annotations(id) ON DELETE CASCADE,

    -- Decision context
    decision_point_name TEXT NOT NULL,
    options_presented TEXT NOT NULL,  -- JSON array of options

    -- Resolution
    selected_option TEXT NOT NULL,
    rationale TEXT,
    decided_by TEXT,  -- 'user', 'default', 'heuristic'

    -- Impact
    preservation_impact TEXT,  -- How this affects preservation level

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5.5 Pattern Statistics View

```sql
-- View for analyzing gap pattern frequency and impact
CREATE VIEW IF NOT EXISTS v_gap_pattern_stats AS
SELECT
    iga.gap_pattern_id,
    iga.gap_category,
    iga.severity,
    COUNT(*) as occurrence_count,
    SUM(CASE WHEN iga.user_decision_required THEN 1 ELSE 0 END) as decisions_required,
    AVG(iga.confidence) as avg_confidence,
    MIN(iga.max_preservation_level) as worst_preservation,
    GROUP_CONCAT(DISTINCT iga.mitigation_applied) as mitigations_used
FROM ir_gap_annotations iga
GROUP BY iga.gap_pattern_id, iga.gap_category, iga.severity
ORDER BY occurrence_count DESC;
```

---

## 6. Implementation Priorities

Based on severity matrix (difficulty scores) and pattern frequency from gap analysis.

### 6.1 P0 (Critical) - Patterns Affecting >50% of Conversions

| Pattern ID | Category | Severity | Affected Pairs | Automation | IR Layer |
|------------|----------|----------|----------------|------------|----------|
| TS-001 | type_system | high | Dynamic to Static (40% of pairs) | partial | 2 |
| MM-002 | memory | high | GC to Ownership (35% of pairs) | partial | 2 |
| EF-001 | effects | high | Exceptions to Result (45% of pairs) | partial | 2 |
| MM-001 | memory | critical | GC to Manual (25% of pairs) | none | 2 |

**Implementation Order:**
1. `@inferred_type` annotation system
2. `@ownership_hint` with lifetime analysis
3. `@error_handling_conversion` transformer
4. `@ownership_transfer` with leak detection

### 6.2 P1 (High) - Patterns with High Asymmetry Ratios (>=3:1)

| Pattern ID | Category | Asymmetry | Direction | Automation | IR Layer |
|------------|----------|-----------|-----------|------------|----------|
| MM-004 | memory | 3:1 | Mutable to Immutable | partial | 2 |
| TS-003 | type_system | N/A (lossy) | HKT to No HKT | none | 2 |
| EF-004 | effects | 3:1 | Monadic to Direct | partial | 2 |
| EF-009 | effects | 1.5:1 | Lazy to Strict | partial | 2 |

**Implementation Order:**
1. `@mutability_analysis` for mutation tracking
2. `@hkt_specialization` for type class handling
3. `@monad_flattening` for do-notation
4. `@evaluation_strategy` for laziness

### 6.3 P2 (Medium) - Structural Patterns

| Pattern ID | Category | Severity | Automation | IR Layer |
|------------|----------|----------|------------|----------|
| TS-005 | type_system | medium | partial | 1-2 |
| TS-006 | type_system | medium | full | 1 |
| TS-007 | type_system | medium | partial | 1-2 |
| CC-001 | concurrency | high | partial | 2 |
| CC-009 | concurrency | high | partial | 2 |

**Implementation Order:**
1. `@interface_extraction` for duck typing
2. `@union_to_tagged` for type unions
3. `@structural_to_nominal` converter
4. `@concurrency_model_conversion`
5. `@supervision_conversion`

### 6.4 P3 (Low) - Idiomatic Patterns

| Pattern ID | Category | Severity | Automation | IR Layer |
|------------|----------|----------|------------|----------|
| TS-008 | type_system | low | full | 1 |
| TS-015 | type_system | low | full | 1 |
| MM-005 | memory | low | full | 2 |
| MM-012 | memory | low | full | 2 |

**Implementation Order:**
1. Style transform rules
2. Naming convention converters
3. Documentation format transformers
4. Performance hint inserters

---

## 7. Summary Table

### 7.1 Complete Pattern to IR Mapping

| Pattern ID | Category | Severity | Layer | Annotation | Priority | Automation | Max Level |
|------------|----------|----------|-------|------------|----------|------------|-----------|
| TS-001 | type | high | 2 | @inferred_type | P0 | partial | 1 |
| TS-002 | type | medium | 2 | @nullability | P2 | partial | 2 |
| TS-003 | type | high | 2 | @hkt_specialization | P1 | none | 1 |
| TS-004 | type | medium | 2 | @gradual_type | P2 | partial | 2 |
| TS-005 | type | medium | 1-2 | @interface_extraction | P2 | partial | 2 |
| TS-006 | type | medium | 1 | @union_to_tagged | P2 | full | 2 |
| TS-007 | type | medium | 1-2 | @structural_to_nominal | P2 | partial | 2 |
| TS-008 | type | low | 1 | @explicit_generics | P3 | full | 2 |
| TS-009 | type | medium | 1 | @type_erasure | P2 | partial | 1 |
| TS-010 | type | high | 2 | @type_class_conversion | P1 | partial | 1 |
| TS-011 | type | critical | 2 | @dependent_type_erasure | P0 | none | 0 |
| TS-012 | type | medium | 1 | @row_poly_to_fixed | P2 | partial | 1 |
| TS-013 | type | high | 2 | @refinement_to_runtime | P1 | partial | 1 |
| TS-014 | type | low | 1 | @phantom_type_handling | P3 | partial | 1 |
| TS-015 | type | low | 1 | @type_inference_explicit | P3 | full | 2 |
| TS-016 | type | medium | 1 | @variance_handling | P2 | partial | 2 |
| MM-001 | memory | critical | 2 | @ownership_transfer | P0 | none | 1 |
| MM-002 | memory | high | 2 | @ownership_hint | P0 | partial | 2 |
| MM-003 | memory | high | 2 | @linear_type_conversion | P1 | partial | 1 |
| MM-004 | memory | medium | 2 | @mutability_analysis | P1 | partial | 2 |
| MM-005 | memory | low | 2 | @allocation_strategy | P3 | full | 2 |
| MM-006 | memory | medium | 2 | @rc_to_gc | P2 | full | 2 |
| MM-007 | memory | medium | 2 | @gc_to_arc | P2 | partial | 2 |
| MM-008 | memory | medium | 2 | @copy_semantics | P2 | partial | 2 |
| MM-009 | memory | medium | 2 | @value_ref_semantics | P2 | partial | 1 |
| MM-010 | memory | medium | 2 | @isolation_boundary | P2 | partial | 1 |
| MM-011 | memory | medium | 2 | @arena_allocation | P2 | partial | 2 |
| MM-012 | memory | low | 2 | @cow_optimization | P3 | full | 2 |
| EF-001 | effects | high | 2 | @error_handling_conversion | P0 | partial | 2 |
| EF-002 | effects | medium | 2 | @null_to_option | P2 | full | 2 |
| EF-003 | effects | medium | 2 | @callback_to_async | P2 | partial | 2 |
| EF-004 | effects | high | 2 | @monad_flattening | P1 | partial | 1 |
| EF-005 | effects | medium | 2 | @effect_tracking | P2 | partial | 2 |
| EF-006 | effects | high | 2 | @global_to_pure | P1 | partial | 2 |
| EF-007 | effects | low | 2 | @checked_to_unchecked | P3 | full | 2 |
| EF-008 | effects | medium | 2 | @tagged_tuple_to_exception | P2 | partial | 2 |
| EF-009 | effects | high | 2 | @evaluation_strategy | P1 | partial | 1 |
| EF-010 | effects | medium | 2 | @strict_to_lazy | P2 | partial | 2 |
| EF-011 | effects | medium | 2 | @sync_to_async | P2 | partial | 2 |
| EF-012 | effects | medium | 2 | @error_code_to_result | P2 | partial | 2 |
| CC-001 | concurrency | high | 2 | @concurrency_model_conversion | P2 | partial | 1 |
| CC-002 | concurrency | high | 2 | @threads_to_actors | P2 | partial | 2 |
| CC-003 | concurrency | medium | 2 | @green_to_os_threads | P2 | partial | 1 |
| CC-004 | concurrency | medium | 2 | @csp_to_async | P2 | partial | 1 |
| CC-005 | concurrency | high | 2 | @shared_to_message | P2 | partial | 2 |
| CC-006 | concurrency | high | 2 | @locks_to_stm | P2 | none | 2 |
| CC-007 | concurrency | medium | 2 | @async_to_callback | P2 | full | 2 |
| CC-008 | concurrency | low | 2 | @future_to_blocking | P3 | full | 1 |
| CC-009 | concurrency | high | 2 | @supervision_conversion | P2 | partial | 1 |
| CC-010 | concurrency | medium | 2 | @single_to_multi_thread | P2 | none | 2 |
| CC-011 | concurrency | low | 2 | @parallel_to_sequential | P3 | full | 1 |
| CC-012 | concurrency | medium | 2 | @reactive_to_pull | P2 | partial | 1 |
| CC-013 | concurrency | medium | 2 | @coroutine_to_state_machine | P2 | partial | 2 |
| CC-014 | concurrency | low | 2 | @virtual_to_thread_pool | P3 | partial | 1 |

### 7.2 Coverage Statistics

| Category | Pattern Count | P0 | P1 | P2 | P3 | Avg Automation |
|----------|--------------|----|----|----|----|----------------|
| Type System | 16 | 2 | 3 | 9 | 2 | partial (69%) |
| Memory Model | 12 | 2 | 2 | 6 | 2 | partial (67%) |
| Effect System | 12 | 1 | 3 | 7 | 1 | partial (75%) |
| Concurrency | 14 | 0 | 0 | 11 | 3 | partial (64%) |
| **Total** | **54** | **5** | **8** | **33** | **8** | **partial (69%)** |

### 7.3 IR Layer Distribution

| Layer | Pattern Count | Primary Responsibility |
|-------|--------------|----------------------|
| Layer 0 | 0 | Parsing (no gap patterns) |
| Layer 1 | 8 | Syntax normalization |
| Layer 1-2 | 4 | Structure + semantics |
| Layer 2 | 42 | Semantic analysis |
| Layer 3 | 0 | Target lowering (idioms) |

---

## 8. Recommendations

### 8.1 Immediate Actions

1. **Implement P0 annotations first** - These affect the majority of conversions
2. **Build confidence scoring** - Critical for inferred annotations
3. **Create decision point framework** - Required for human-in-the-loop patterns
4. **Add preservation level tracking** - Users need visibility into conversion quality

### 8.2 Schema Implementation Order

1. `ir_gap_annotations` - Core gap tracking
2. `ir_preservation_status` - Quality tracking
3. `ir_decision_resolutions` - User decision logging
4. `ir_asymmetry_metadata` - Bidirectional conversion support

### 8.3 Tool Integration Points

| Tool | Integration Point | Purpose |
|------|------------------|---------|
| Parser | Layer 0 to 1 | Extract source annotations |
| Type Inference | Layer 1 to 2 | Populate @inferred_type |
| Ownership Analysis | Layer 2 | Populate @ownership_hint |
| Effect Analysis | Layer 2 | Populate @effect_boundary |
| Idiom Recognizer | Layer 2 to 3 | Apply idiomatic transforms |
| Test Generator | All layers | Validate preservation level |

### 8.4 Metrics to Track

| Metric | Target | Purpose |
|--------|--------|---------|
| Gap coverage | 100% | All 54 patterns have annotations |
| Automation rate | >70% | Minimize human intervention |
| Avg preservation level | >1.5 | Quality of conversions |
| Decision resolution rate | <20% | Reduce human decisions needed |
| Confidence threshold | >0.85 | Reliable inferred annotations |

---

*Generated for task ai-p29.9*
*Synthesized from severity-matrix.md, gap-patterns.md, bidirectional-gaps.md, gap-classification.md, preservation-levels.md, schema.sql*
