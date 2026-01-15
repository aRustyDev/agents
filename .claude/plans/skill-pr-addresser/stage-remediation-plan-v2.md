# Stage Remediation Plan v2

> Fixes for gaps identified in stages 7.5-13 gap analysis (second review).

## Overview

After completing the first remediation pass, a second review identified 13 additional gaps across stages 8-13. This plan addresses those gaps.

## Critical Fixes (5)

### Fix 1: Add `linked_to_review` field to ThreadFeedback (Stage 8)

**Problem**: Stage 9's `mark_linked_threads()` and Stage 13 tests set/check `thread.linked_to_review`, but `ThreadFeedback` doesn't define this field.

**Location**: `stage-8-data-models.md` → ThreadFeedback dataclass

**Change**:
```python
@dataclass
class ThreadFeedback:
    # ... existing fields ...
    linked_to_review: str | None = None  # Set by cross-reference detection
```

---

### Fix 2: Add `references_lines` and `references_files` to ReviewFeedback (Stage 8)

**Problem**: Stage 13 test asserts `reviews[0].references_lines == [42]`, but `ReviewFeedback` doesn't have this field.

**Location**: `stage-8-data-models.md` → ReviewFeedback dataclass

**Change**:
```python
@dataclass
class ReviewFeedback:
    # ... existing fields ...
    references_lines: list[int] = field(default_factory=list)  # Populated by cross-reference
    references_files: list[str] = field(default_factory=list)
```

---

### Fix 3: Add skip tracking fields to FilteredFeedback (Stage 9)

**Problem**: Stage 13 tests reference `skipped_unchanged`, `skipped_resolved`, `skipped_outdated` but these aren't defined.

**Location**: `stage-9-filter.md` → FilteredFeedback dataclass

**Change**:
```python
@dataclass
class FilteredFeedback:
    reviews: list[ReviewFeedback] = field(default_factory=list)
    comments: list[CommentFeedback] = field(default_factory=list)
    threads: list[FilteredThread] = field(default_factory=list)

    # Tracking for skipped items
    skipped_unchanged: list[str] = field(default_factory=list)
    skipped_resolved: list[str] = field(default_factory=list)
    skipped_outdated: list[str] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not self.reviews and not self.comments and not self.threads
```

---

### Fix 4: Add `is_empty` property to FilteredFeedback (Stage 9)

**Problem**: Stage 12 uses `filtered.is_empty` but this property isn't defined.

**Location**: `stage-9-filter.md` → FilteredFeedback dataclass

**Change**: Included in Fix 3 above.

---

### Fix 5: Add `has_author_response` to FilteredThread (Stage 9)

**Problem**: Stage 13 test checks `result.threads[0].has_author_response` but `FilteredThread` doesn't define this.

**Location**: `stage-9-filter.md` → FilteredThread dataclass

**Change**:
```python
@dataclass
class FilteredThread:
    thread: ThreadFeedback
    new_comments: list[ThreadComment]
    has_author_response: bool = False  # Author said "done", "fixed", etc.
```

---

## Medium Fixes (4)

### Fix 6: Add `IterationProgress.from_dict()` and `to_dict()` methods (Stage 10)

**Problem**: Stage 12 calls `IterationProgress.from_dict(data)` but this isn't defined.

**Location**: `stage-10-infrastructure.md` → IterationProgress dataclass (add if missing)

**Change**:
```python
@dataclass
class IterationProgress:
    iteration: int
    started_at: datetime
    completed_groups: list[str] = field(default_factory=list)
    current_group: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "IterationProgress":
        return cls(
            iteration=data["iteration"],
            started_at=datetime.fromisoformat(data["started_at"]),
            completed_groups=data.get("completed_groups", []),
            current_group=data.get("current_group"),
        )

    def to_dict(self) -> dict:
        return {
            "iteration": self.iteration,
            "started_at": self.started_at.isoformat(),
            "completed_groups": self.completed_groups,
            "current_group": self.current_group,
        }
```

---

### Fix 7: Add `addressed_thread_ids` property and `failed` property to FixResult (Stage 8)

**Problem**: Stage 12 references `result.addressed_thread_ids` and `result.failed` but these aren't on FixResult.

**Location**: `stage-8-data-models.md` → FixResult dataclass

**Change**:
```python
@dataclass
class FixResult:
    group_id: str
    addressed_locations: list[AddressedLocation] = field(default_factory=list)
    changes_made: list[str] = field(default_factory=list)
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    error: str | None = None

    @property
    def has_changes(self) -> bool:
        return len(self.changes_made) > 0

    @property
    def failed(self) -> bool:
        return self.error is not None

    @property
    def addressed_thread_ids(self) -> list[str]:
        """Extract thread IDs from addressed locations."""
        return [loc.thread_id for loc in self.addressed_locations if loc.thread_id]
```

---

### Fix 8: Add `on_rate_limit` hook definition (Stage 11)

**Problem**: Stage 10 references `on_rate_limit` hook but Stage 11 doesn't define it.

**Location**: `stage-11-hooks.md` → App.Meta.hooks list

**Change**:
```python
class App(CementApp):
    class Meta:
        hooks = [
            # ... existing hooks ...
            ('on_rate_limit', weight=0),
        ]
```

Also add hook handler example.

---

### Fix 9: Update test fixtures to use timezone-aware datetime (Stage 13)

**Problem**: Section 13.1's fixtures.py uses naive datetime, contradicting timezone-aware usage elsewhere.

**Location**: `stage-13-testing.md` → Section 13.1 fixtures.py

**Change**: Update all datetime instantiations to use `tzinfo=timezone.utc`.

---

## Minor Fixes (4)

### Fix 10: Add ThreadComment to explicit exports note (Stage 8)

**Problem**: Stage 13 imports `ThreadComment` from `src.models` but export isn't documented.

**Location**: `stage-8-data-models.md` → Add exports note

---

### Fix 11: Add missing progress import to Stage 12

**Problem**: `_load_progress` uses `IterationProgress` but import not shown.

**Location**: `stage-12-pipeline.md` → imports section

---

### Fix 12: Add `thread_id` field to AddressedLocation (Stage 8)

**Problem**: Fix 7's `addressed_thread_ids` property references `loc.thread_id` but `AddressedLocation` may not have this.

**Location**: `stage-8-data-models.md` → AddressedLocation dataclass

---

### Fix 13: Document unused PRInfo fields (Stage 7.5)

**Problem**: PRInfo has `base_branch` and `title` but Stage 12 doesn't use them.

**Location**: `stage-7.5-prerequisites.md` → Add note about optional fields

---

## Implementation Order

1. Stage 8 (data models) - Fixes 1, 2, 7, 10, 12
2. Stage 9 (filter) - Fixes 3, 4, 5
3. Stage 10 (infrastructure) - Fix 6
4. Stage 11 (hooks) - Fix 8
5. Stage 12 (pipeline) - Fix 11
6. Stage 13 (testing) - Fix 9
7. Stage 7.5 (prerequisites) - Fix 13

## Implementation Results

Upon review, **most gaps were already fixed** in the existing stage documents from a previous remediation pass. Only one fix was actually needed:

### Fix Applied
- **Stage 13 (section 13.1)**: Updated test fixtures to use timezone-aware datetime
  - Added `timezone` import: `from datetime import datetime, timezone`
  - Changed all `datetime(2025, 1, 1, ...)` to include `tzinfo=timezone.utc`

### Already Fixed (No Changes Needed)
- **Stage 8**: `linked_to_review`, `references_lines`, `references_files`, `FixResult.failed`, `FixResult.addressed_thread_ids` - all present
- **Stage 9**: `skipped_unchanged`, `skipped_resolved`, `skipped_outdated`, `is_empty`, `has_author_response` - all present
- **Stage 10**: `IterationProgress.from_dict()` and `to_dict()` - present
- **Stage 11**: `on_rate_limit` hook - present
- **Stage 12**: `from .progress import IterationProgress` - present

## Validation Checklist

After implementation:

- [x] All ThreadFeedback usages have `linked_to_review` available
- [x] All ReviewFeedback usages have `references_lines` available
- [x] FilteredFeedback has `is_empty`, skip tracking fields
- [x] FilteredThread has `has_author_response`
- [x] IterationProgress has `from_dict()` and `to_dict()`
- [x] FixResult has `failed`, `has_changes`, `addressed_thread_ids`
- [x] `on_rate_limit` hook is defined
- [x] All test fixtures use timezone-aware datetime
- [x] No import errors in stage code examples
