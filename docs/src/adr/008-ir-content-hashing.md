# ADR-008: IR Content Hashing Strategy

**Status**: Accepted
**Date**: 2026-02-04
**Context**: Convert Skills IR Research (Phase 4)
**Deciders**: Project maintainers

## Context

The IR schema requires content hashing for two distinct purposes:

1. **Deduplication**: Prevent storing identical IR units within the same extraction version
2. **Change Detection**: Identify what changed between extraction runs for incremental updates

The existing `ir_units` table in `schema.sql` already has a `content_hash` column used for deduplication:

```sql
CREATE TABLE IF NOT EXISTS ir_units (
    ...
    content_hash TEXT NOT NULL,
    UNIQUE(version_id, content_hash)  -- Deduplication constraint
);
```

The question: Should change detection use the same hash, or a separate mechanism?

## Decision

**Use a unified hashing approach**: A single SHA-256 hash of canonicalized JSON content serves both deduplication and change detection.

### Algorithm Specification

```python
import hashlib
import json

def compute_content_hash(content: dict) -> str:
    """
    Compute SHA-256 hash of canonicalized JSON content.

    Canonicalization rules:
    1. Keys sorted alphabetically (recursive)
    2. No whitespace between elements
    3. UTF-8 encoding
    4. Deterministic float representation
    """
    canonical = json.dumps(
        content,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False
    )
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
```

### Hash Format

- **Algorithm**: SHA-256
- **Output**: 64-character lowercase hexadecimal string
- **Example**: `a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a`

## Alternatives Considered

### Option A: Unified Hashing (Chosen)

**Description**: Single SHA-256 hash of `content_json` for all purposes.

**Pros**:
- Simple: One algorithm to maintain
- Consistent: Same content always produces same hash
- Space-efficient: No redundant hash columns
- Content-addressable: Hash can serve as stable reference ID

**Cons**:
- Hash doesn't capture metadata (layer, unit_type)
- Identical content in different contexts has same hash

**Mitigation**: The `UNIQUE(version_id, content_hash)` constraint ensures context is preserved.

### Option B: Composite Hashing

**Description**: Hash includes structural metadata: `SHA256(layer + unit_type + content_json)`

```python
def compute_composite_hash(layer: int, unit_type: str, content: dict) -> str:
    composite = f"{layer}:{unit_type}:{json.dumps(content, sort_keys=True)}"
    return hashlib.sha256(composite.encode('utf-8')).hexdigest()
```

**Pros**:
- More precise: Same content in different layers produces different hashes
- Explicit: Hash encodes structural context

**Cons**:
- Breaks content-addressability: Can't look up content by hash alone
- Redundant: Layer and unit_type already stored in separate columns
- Migration: Requires recomputing all existing hashes

**Verdict**: Rejected. The precision gain doesn't justify the complexity.

### Option C: Dual Hashing

**Description**: Maintain two separate hash columns:
- `content_hash`: For deduplication (content only)
- `structural_hash`: For change detection (content + metadata)

**Pros**:
- Maximum flexibility
- Each hash optimized for its purpose

**Cons**:
- Storage overhead: Two 64-char strings per row
- Maintenance: Must keep both hashes in sync
- Complexity: Consumers must choose which hash to use

**Verdict**: Rejected. Over-engineering for current requirements.

### Option D: Content-Addressed Storage (CAS)

**Description**: Hash becomes the primary key; content stored separately.

```sql
CREATE TABLE ir_content (
    hash TEXT PRIMARY KEY,  -- SHA-256
    content_json TEXT NOT NULL
);

CREATE TABLE ir_units (
    id INTEGER PRIMARY KEY,
    version_id INTEGER,
    layer INTEGER,
    unit_type TEXT,
    content_hash TEXT REFERENCES ir_content(hash)
);
```

**Pros**:
- Perfect deduplication across all versions
- Immutable content: Hash guarantees integrity
- Efficient storage for large codebases with repeated patterns

**Cons**:
- Schema change: Requires migration
- Join overhead: Every content access needs a join
- Orphan cleanup: Must garbage-collect unreferenced content

**Verdict**: Considered for future optimization. Not needed at current scale.

### Option E: Merkle Tree Hashing

**Description**: Hash includes hashes of dependencies, creating a tree structure.

```python
def compute_merkle_hash(content: dict, dependency_hashes: list[str]) -> str:
    combined = json.dumps(content, sort_keys=True) + ''.join(sorted(dependency_hashes))
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()
```

**Pros**:
- Cascade detection: Change in dependency propagates up the tree
- Integrity verification: Can verify entire subgraph with root hash

**Cons**:
- Expensive: Must recompute hashes up the tree on any change
- Circular dependencies: Requires special handling
- Complexity: Significant implementation overhead

**Verdict**: Rejected. Overkill for current incremental update needs. The simpler approach of comparing individual hashes across versions is sufficient.

## Consequences

### Positive

1. **Simplicity**: Single hashing algorithm used everywhere
2. **Consistency**: IR units with identical content have identical hashes
3. **Efficiency**: No redundant hash storage
4. **Interoperability**: Any tool can compute the same hash independently

### Negative

1. **Metadata blindness**: Hash doesn't encode layer or unit_type
2. **Collision theoretical**: SHA-256 collisions are theoretically possible (practically negligible)

### Neutral

1. **Migration**: Existing `content_hash` values are compatible (no changes needed)
2. **Future CAS**: Can migrate to content-addressed storage later without hash algorithm change

## Implementation Notes

### SQL Schema (No Changes Required)

The existing schema already supports this decision:

```sql
-- ir_units.content_hash is already TEXT NOT NULL
-- Just ensure all code uses the same canonicalization
```

### Validation Query

```sql
-- Verify no hash collisions with different content
SELECT content_hash, COUNT(*) as cnt, COUNT(DISTINCT content_json) as unique_content
FROM ir_units
GROUP BY content_hash
HAVING cnt > 1 AND unique_content > 1;
-- Should return 0 rows
```

### Change Detection Query

```sql
-- Find units that changed between versions
SELECT
    old.id as old_id,
    new.id as new_id,
    old.content_hash as old_hash,
    new.content_hash as new_hash
FROM ir_units old
JOIN ir_units new ON old.layer = new.layer
    AND old.unit_type = new.unit_type
    -- Match by some stable identifier, e.g., module path
WHERE old.version_id = :old_version
    AND new.version_id = :new_version
    AND old.content_hash != new.content_hash;
```

## References

- Phase 4 Plan: `.claude/plans/merge-convert-skills/phase/4-ir-schema-design.md` (§4.9)
- Existing Schema: `.claude/plans/merge-convert-skills/data/schema.sql`
- JSON Canonicalization: RFC 8785 (JSON Canonicalization Scheme)

---

*Generated: 2026-02-04*
