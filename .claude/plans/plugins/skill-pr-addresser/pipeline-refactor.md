# Pipeline Refactor: Feedback Processing with Cement Hooks

> Separate discovery, filtering, consolidation, and task identification into distinct hook-based stages.

## Stage Documents

This design document is broken into implementation stages:

| Stage | Document | Description |
|-------|----------|-------------|
| 8 | [stage-8-data-models.md](stage-8-data-models.md) | Protocol-based feedback types, content hashing |
| 9 | [stage-9-filter.md](stage-9-filter.md) | "Is-new" logic, delta detection, cross-references |
| 10 | [stage-10-infrastructure.md](stage-10-infrastructure.md) | Session locking, thread resolution, dry-run mode |
| 11 | [stage-11-hooks.md](stage-11-hooks.md) | Cement hook definitions and handlers |
| 12 | [stage-12-pipeline.md](stage-12-pipeline.md) | Stage-based execution, partial addressing |
| 13 | [stage-13-testing.md](stage-13-testing.md) | Comprehensive testing for all components |

**Total Estimated Effort: ~20 hours**

---

## Problem Statement

The current agent has several issues:

1. **No delta tracking**: All unresolved thread comments are processed every run, even if already addressed
2. **No content change detection** (#796): Updated comments are skipped because only ID is checked
3. **Tightly coupled stages**: Discovery, filtering, and consolidation happen in a single function
4. **No hook points**: Can't inject logging, metrics, or custom logic between stages
5. **No session locking**: Two instances on same PR can cause race conditions
6. **Threads stay unresolved**: Agent comments but doesn't call GitHub API to resolve threads
7. **No dry-run mode**: Can't preview what would be addressed without making changes

## Proposed Architecture

### Pipeline Stages with Cement Hooks

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PIPELINE STAGES                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │  DISCOVERY   │────▶│   FILTER     │────▶│ CONSOLIDATE  │            │
│  │              │     │  (is-new)    │     │              │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│         │                    │                    │                     │
│         ▼                    ▼                    ▼                     │
│   post_discovery       post_filter        post_consolidate             │
│                                                                          │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │    PLAN      │────▶│     FIX      │────▶│   COMMIT     │            │
│  │  (identify   │     │   (batch     │     │  (push +     │            │
│  │   tasks)     │     │   execute)   │     │   comment)   │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│         │                    │                    │                     │
│         ▼                    ▼                    ▼                     │
│    post_plan            post_fix            post_commit                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Stage Definitions

| Stage | Input | Output | Purpose |
|-------|-------|--------|---------|
| **Discovery** | PR number | RawFeedback | Fetch all reviews, comments, threads from GitHub |
| **Filter** | RawFeedback + Session | FilteredFeedback | Remove already-addressed, detect content changes |
| **Consolidate** | FilteredFeedback | ConsolidatedFeedback | Group similar items, separate guidance |
| **Plan** | ConsolidatedFeedback | ExecutionPlan | Order tasks, estimate complexity |
| **Fix** | ExecutionPlan | FixResults | Execute changes in batches |
| **Commit** | FixResults | CommitResult | Stage, commit, push, comment |

## Data Models

### Protocol-Based Feedback Types

Instead of one overloaded `FeedbackItem`, use a Protocol with specialized types:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Feedback(Protocol):
    """Common interface for all feedback types."""

    @property
    def id(self) -> str: ...

    @property
    def content(self) -> str: ...

    @property
    def content_hash(self) -> str: ...

    @property
    def author(self) -> str: ...

    @property
    def created_at(self) -> datetime: ...

    def is_resolved_by(self, response: "Feedback") -> bool:
        """Check if this feedback is resolved by a response."""
        ...


@dataclass
class ReviewFeedback:
    """Feedback from a PR review."""

    id: str
    state: Literal["CHANGES_REQUESTED", "COMMENTED", "APPROVED"]
    body: str
    author: str
    submitted_at: datetime

    # Computed
    content_hash: str = field(init=False)

    # Cross-references (detected by parsing body)
    references_lines: list[int] = field(default_factory=list)
    references_files: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.content_hash = hash_content(self.body)

    @property
    def content(self) -> str:
        return self.body

    @property
    def created_at(self) -> datetime:
        return self.submitted_at

    def is_resolved_by(self, response: Feedback) -> bool:
        # Reviews are resolved by APPROVED state, not responses
        return False


@dataclass
class CommentFeedback:
    """Feedback from a PR comment (not on specific code)."""

    id: str
    body: str
    author: str
    created_at: datetime
    reactions: dict[str, int] = field(default_factory=dict)  # {"thumbsUp": 2, ...}

    # Computed
    content_hash: str = field(init=False)

    def __post_init__(self):
        self.content_hash = hash_content(self.body)

    @property
    def content(self) -> str:
        return self.body

    def has_acknowledgment_reaction(self, pr_author: str) -> bool:
        """Check if PR author reacted with acknowledgment."""
        # Would need to track who reacted, not just counts
        return self.reactions.get("thumbsUp", 0) > 0

    def is_resolved_by(self, response: Feedback) -> bool:
        # Comments resolved by author saying "done" or "fixed"
        if response.author != self.author:  # Must be from same reviewer
            return False
        resolved_phrases = ["never mind", "ignore", "looks good now", "resolved"]
        return any(p in response.content.lower() for p in resolved_phrases)


@dataclass
class ThreadComment:
    """A single comment within a review thread."""

    id: str
    body: str
    author: str
    created_at: datetime

    # Computed
    content_hash: str = field(init=False)
    is_resolution_signal: bool = field(init=False)

    def __post_init__(self):
        self.content_hash = hash_content(self.body)
        # Detect if this comment signals resolution
        resolution_phrases = ["done", "fixed", "addressed", "resolved", "will do"]
        self.is_resolution_signal = any(
            p in self.body.lower() for p in resolution_phrases
        )

    @property
    def content(self) -> str:
        return self.body


@dataclass
class ThreadFeedback:
    """Feedback from a code review thread (line-specific)."""

    id: str
    path: str
    line: int | None
    is_resolved: bool
    is_outdated: bool
    comments: list[ThreadComment]

    @property
    def first_comment(self) -> ThreadComment | None:
        return self.comments[0] if self.comments else None

    @property
    def author(self) -> str | None:
        return self.first_comment.author if self.first_comment else None

    @property
    def content(self) -> str:
        return self.first_comment.body if self.first_comment else ""

    @property
    def content_hash(self) -> str:
        # Hash of first comment (the original feedback)
        return self.first_comment.content_hash if self.first_comment else ""

    @property
    def created_at(self) -> datetime:
        return self.first_comment.created_at if self.first_comment else datetime.min

    def get_new_comments_since(self, last_seen_id: str | None) -> list[ThreadComment]:
        """Get comments added after last_seen_id."""
        if not last_seen_id:
            return self.comments

        found = False
        new_comments = []
        for comment in self.comments:
            if found:
                new_comments.append(comment)
            elif comment.id == last_seen_id:
                found = True
        return new_comments

    def has_author_resolution(self, pr_author: str) -> bool:
        """Check if PR author signaled resolution in thread."""
        for comment in self.comments[1:]:  # Skip first (original feedback)
            if comment.author == pr_author and comment.is_resolution_signal:
                return True
        return False

    def has_reviewer_withdrawal(self) -> bool:
        """Check if reviewer withdrew their feedback."""
        if not self.first_comment:
            return False
        reviewer = self.first_comment.author
        withdrawal_phrases = ["never mind", "ignore this", "my mistake", "disregard"]
        for comment in self.comments[1:]:
            if comment.author == reviewer:
                if any(p in comment.body.lower() for p in withdrawal_phrases):
                    return True
        return False

    def is_resolved_by(self, response: Feedback) -> bool:
        return self.has_author_resolution(response.author) or self.has_reviewer_withdrawal()
```

### AddressedFeedback (For Session Storage)

```python
@dataclass
class AddressedFeedback:
    """Record of addressed feedback for delta detection."""

    id: str
    content_hash: str
    addressed_at: datetime
    addressed_in_commit: str
    iteration: int

    # Thread comment tracking
    thread_comments_seen: list[str] = field(default_factory=list)
    last_comment_id: str | None = None
```

### Session Schema Update

```python
# In session.results["feedback_state"]
{
    "addressed": {
        "IC_abc123": {
            "content_hash": "sha256:...",
            "addressed_at": "2025-01-02T12:00:00Z",
            "addressed_in_commit": "abc1234",
            "iteration": 1
        }
    },
    "threads": {
        "PRRT_xyz789": {
            "last_seen_comment_id": "PRRTC_comment5",
            "comments_processed": ["PRRTC_c1", "PRRTC_c2", "PRRTC_c3"],
            "last_processed_at": "2025-01-02T12:00:00Z"
        }
    },
    "last_run": "2025-01-02T12:00:00Z"
}
```

## Cement Hook Implementation

### Hook Definitions

```python
# In app.py
class SkillPRAddresser(App):
    class Meta:
        label = 'skill-pr-addresser'

        define_hooks = [
            # Lifecycle
            'pre_address',           # Before any processing
            'post_address',          # After all processing

            # Discovery phase
            'pre_discovery',
            'post_discovery',

            # Filter phase
            'pre_filter',
            'post_filter',

            # Consolidation phase
            'pre_consolidate',
            'post_consolidate',

            # Fix phase
            'pre_fix',
            'pre_fix_batch',
            'post_fix_batch',
            'post_fix',

            # Commit phase
            'pre_commit',
            'post_commit',

            # Thread resolution
            'pre_resolve_threads',
            'post_resolve_threads',

            # Error handling
            'on_stage_error',        # When any stage fails
            'on_rate_limit',         # When GitHub rate limit hit
        ]
```

### Early Exit Checks

Each stage should check if there's work to do before proceeding:

```python
# In src/stages.py

def run_filter_stage(ctx: PipelineContext) -> StageResult:
    """Run filter stage with early exit check."""

    # Run hooks
    for result in ctx.app.hook.run('pre_filter', ctx):
        pass

    filtered = filter_feedback(ctx.raw_feedback, ctx.session, ctx.pr_author)

    # Early exit if nothing to process
    if filtered.is_empty:
        ctx.app.log.info("No new feedback to process - all items already addressed")
        return StageResult(
            stage="filter",
            success=True,
            should_continue=False,  # Signal to stop pipeline
            reason="no_new_feedback",
        )

    ctx.filtered_feedback = filtered

    for result in ctx.app.hook.run('post_filter', ctx):
        pass

    return StageResult(stage="filter", success=True, should_continue=True)
```

### Hook Handlers

```python
# In src/hooks.py

def log_discovery_results(app):
    """Log what was discovered."""
    ctx = app.pargs.ctx
    app.log.info(
        f"Discovered: {len(ctx.raw_reviews)} reviews, "
        f"{len(ctx.raw_comments)} comments, "
        f"{len(ctx.raw_threads)} threads"
    )

def log_filter_results(app):
    """Log what passed filtering."""
    ctx = app.pargs.ctx
    app.log.info(
        f"After filter: {len(ctx.filtered_items)} items "
        f"({ctx.skipped_already_addressed} already addressed, "
        f"{ctx.skipped_no_change} unchanged)"
    )

def record_metrics(app):
    """Record OTEL metrics after each stage."""
    # ... metrics recording

def persist_state(app):
    """Persist feedback state after commit."""
    ctx = app.pargs.ctx
    ctx.session.results["feedback_state"] = ctx.feedback_state.to_dict()
    ctx.session.save(app.sessions_dir)
```

### Registering Hooks

```python
# In app.py setup or extension

def setup(self):
    super().setup()

    # Register built-in hooks
    self.hook.register('post_discovery', log_discovery_results)
    self.hook.register('post_filter', log_filter_results)
    self.hook.register('post_commit', persist_state)

    # Metrics hooks (if OTEL enabled)
    if self.config.get('otel', 'enabled'):
        self.hook.register('post_discovery', record_metrics)
        self.hook.register('post_filter', record_metrics)
        self.hook.register('post_fix', record_metrics)
```

## Filter Stage: "Is-New" Logic

### Decision Tree

```
For each item in RawFeedback:
│
├── Is item.id in session.addressed?
│   ├── No → Item is NEW → include
│   └── Yes → Check content hash
│       ├── Hash matches → Item UNCHANGED → skip
│       └── Hash differs → Item UPDATED → include (re-process)
│
├── Is item a thread comment?
│   ├── Is thread resolved? → skip entire thread
│   ├── Is comment in session.threads[thread_id].comments_processed?
│   │   ├── No → Comment is NEW → include
│   │   └── Yes → Check if it's the latest
│   │       └── Is it the last comment AND there are newer? → skip
│   └── Is comment an author response?
│       └── Yes → Mark previous comment as potentially resolved
```

### Implementation

```python
# In src/filter.py

def filter_feedback(
    raw: RawFeedback,
    session: AgentSession,
    pr_author: str,
) -> FilteredFeedback:
    """Filter feedback to only new/changed items.

    Implements "is-new" logic:
    1. Skip already-addressed items (unless content changed)
    2. Skip processed thread comments (unless new replies exist)
    3. Identify author responses that may resolve feedback
    """
    feedback_state = FeedbackState.from_session(session)
    result = FilteredFeedback()

    # Filter reviews
    for review in raw.reviews:
        if _is_new_or_changed(review, feedback_state):
            result.reviews.append(review)
        else:
            result.skipped_unchanged.append(review.id)

    # Filter comments
    for comment in raw.comments:
        if _is_new_or_changed(comment, feedback_state):
            result.comments.append(comment)
        else:
            result.skipped_unchanged.append(comment.id)

    # Filter threads (more complex)
    for thread in raw.threads:
        if thread.is_resolved:
            result.skipped_resolved.append(thread.id)
            continue

        thread_state = feedback_state.threads.get(thread.id)
        new_comments = _get_new_thread_comments(thread, thread_state, pr_author)

        if new_comments:
            # Create filtered thread with only new comments
            result.threads.append(FilteredThread(
                thread=thread,
                new_comments=new_comments,
                has_author_response=any(c.is_author_response for c in new_comments),
            ))

    return result


def _is_new_or_changed(item: FeedbackItem, state: FeedbackState) -> bool:
    """Check if item is new or content has changed."""
    addressed = state.addressed.get(item.id)
    if not addressed:
        return True  # Never seen before

    # Content hash comparison (addresses #796)
    current_hash = hash_content(item.content)
    return current_hash != addressed.content_hash


def _get_new_thread_comments(
    thread: ReviewThread,
    thread_state: ThreadState | None,
    pr_author: str,
) -> list[ThreadComment]:
    """Get only new comments from a thread."""
    if not thread_state:
        # First time seeing this thread - all comments are new
        return thread.comments

    new_comments = []
    for comment in thread.comments:
        if comment.id not in thread_state.comments_processed:
            comment.is_reply = comment != thread.comments[0]
            comment.is_author_response = comment.author == pr_author and comment.is_reply
            new_comments.append(comment)

    return new_comments
```

## Consolidation Stage

### Consolidator (LLM-Powered)

The consolidation stage remains LLM-powered but receives pre-filtered input:

```python
# In src/consolidate.py

def consolidate_feedback(
    agent_dir: Path,
    filtered: FilteredFeedback,
    ctx: DiscoveryContext,
) -> ConsolidatedFeedback:
    """Consolidate filtered feedback using feedback-analyzer.

    Only receives NEW or CHANGED items, not the full history.
    """
    task = f"""Analyze the following NEW feedback for PR #{ctx.pr_number}:

## Important Context
- These are ONLY new or changed items since last processing
- Author responses are marked - consider if they resolve the feedback
- Thread comments include only unprocessed replies

## Reviews (New/Changed)
{json.dumps([r.to_dict() for r in filtered.reviews], indent=2)}

## Comments (New/Changed)
{json.dumps([c.to_dict() for c in filtered.comments], indent=2)}

## Thread Updates
{json.dumps([t.to_consolidation_dict() for t in filtered.threads], indent=2)}

Consolidate into action groups. If an author response resolves feedback,
mark it as "resolved_by_author" type instead of "change_request".
"""

    result, cost = run_subagent(agent_dir, "feedback-analyzer", task, ctx.worktree.path)
    return parse_consolidated_result(result), cost
```

## Session Locking

Prevent concurrent runs on the same PR:

```python
# In src/locking.py

import fcntl
from pathlib import Path
from contextlib import contextmanager

@dataclass
class SessionLock:
    """File-based lock for a PR session."""

    pr_number: int
    lock_file: Path
    holder_pid: int | None = None
    acquired_at: datetime | None = None

    @classmethod
    def acquire(cls, sessions_dir: Path, pr_number: int, timeout: float = 5.0) -> "SessionLock":
        """Acquire lock for a PR session.

        Raises:
            LockError: If lock cannot be acquired within timeout
        """
        lock_file = sessions_dir / f".lock-pr-{pr_number}"
        lock_file.parent.mkdir(parents=True, exist_ok=True)

        fd = open(lock_file, "w")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            # Lock held by another process
            existing = cls._read_lock_info(lock_file)
            raise LockError(
                f"PR #{pr_number} is being processed by PID {existing.holder_pid} "
                f"since {existing.acquired_at}"
            )

        # Write lock info
        lock = cls(
            pr_number=pr_number,
            lock_file=lock_file,
            holder_pid=os.getpid(),
            acquired_at=datetime.utcnow(),
        )
        fd.write(json.dumps(lock.to_dict()))
        fd.flush()

        lock._fd = fd
        return lock

    def release(self):
        """Release the lock."""
        if hasattr(self, '_fd'):
            fcntl.flock(self._fd, fcntl.LOCK_UN)
            self._fd.close()
            self.lock_file.unlink(missing_ok=True)


@contextmanager
def session_lock(sessions_dir: Path, pr_number: int):
    """Context manager for session locking."""
    lock = SessionLock.acquire(sessions_dir, pr_number)
    try:
        yield lock
    finally:
        lock.release()
```

Usage in pipeline:

```python
def address(self, pr_number: int, **kwargs):
    with session_lock(self.sessions_dir, pr_number) as lock:
        self.app.log.debug(f"Acquired lock: {lock.lock_file}")
        return self._run_pipeline(pr_number, **kwargs)
```

## Thread Resolution via GitHub API

After addressing feedback, resolve the thread via GitHub API:

```python
# In src/github_pr.py

def resolve_thread(owner: str, repo: str, thread_id: str) -> bool:
    """Resolve a review thread via GitHub GraphQL API.

    Args:
        owner: Repository owner
        repo: Repository name
        thread_id: Thread node ID (e.g., "PRRT_...")

    Returns:
        True if resolved successfully
    """
    mutation = """
    mutation($threadId: ID!) {
      resolveReviewThread(input: {threadId: $threadId}) {
        thread {
          id
          isResolved
        }
      }
    }
    """

    result = subprocess.run(
        [
            "gh", "api", "graphql",
            "-f", f"query={mutation}",
            "-f", f"threadId={thread_id}",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        log.warning(f"Failed to resolve thread {thread_id}: {result.stderr}")
        return False

    return True


def resolve_addressed_threads(
    owner: str,
    repo: str,
    addressed_thread_ids: list[str],
) -> dict[str, bool]:
    """Resolve multiple threads, returning success status for each."""
    results = {}
    for thread_id in addressed_thread_ids:
        results[thread_id] = resolve_thread(owner, repo, thread_id)
    return results
```

Integration in post_commit hook:

```python
def resolve_threads_hook(app):
    """Resolve threads after successful commit."""
    ctx = app.pargs.ctx

    # Get thread IDs from addressed action groups
    thread_ids = []
    for group in ctx.fix_result.addressed:
        thread_ids.extend(group.get("thread_ids", []))

    if not thread_ids:
        return

    app.log.info(f"Resolving {len(thread_ids)} threads...")
    results = resolve_addressed_threads(
        ctx.owner, ctx.repo, thread_ids
    )

    resolved = sum(1 for v in results.values() if v)
    app.log.info(f"Resolved {resolved}/{len(thread_ids)} threads")
```

## Dry-Run Mode

Preview what would be addressed without making changes:

```python
# In app.py

@ex(
    help='Address review feedback on a PR',
    arguments=[
        (['pr_number'], {'type': int, 'help': 'Pull request number'}),
        (['--dry-run'], {'action': 'store_true', 'help': 'Preview without making changes'}),
        (['--stop-after'], {'choices': ['discovery', 'filter', 'consolidate', 'plan'],
                            'help': 'Stop after specified stage'}),
    ],
)
def address(self):
    pr_number = self.app.pargs.pr_number
    dry_run = self.app.pargs.dry_run
    stop_after = self.app.pargs.stop_after

    if dry_run:
        self.app.log.info("DRY RUN - no changes will be made")
        stop_after = stop_after or 'plan'  # Default to stopping before fix

    result = self.addresser.address(
        pr_number,
        dry_run=dry_run,
        stop_after=stop_after,
    )

    if dry_run:
        self._print_dry_run_summary(result)
```

Dry-run output:

```
$ just address 795 --dry-run

DRY RUN - Previewing what would be addressed for PR #795

=== Discovery ===
  Reviews: 1 (CHANGES_REQUESTED)
  Comments: 0
  Threads: 8 unresolved

=== Filter (Is-New) ===
  New items: 3
  Unchanged: 5 (already addressed)
  Skipped: 0 (content unchanged)

=== Consolidation ===
  Action Groups: 2
    - group-1: move_to_examples (3 locations)
    - group-2: add_documentation (1 location)
  Guidance: 1 item
    - "Follow progressive disclosure pattern"

=== Execution Plan ===
  1. [HIGH] group-1: Move code blocks to examples/
  2. [MEDIUM] group-2: Add missing documentation

Would address 4 feedback items in 2 action groups.
No changes made (dry run).
```

## Partial Addressing

Track progress at the location level, not just action group level:

```python
@dataclass
class AddressedLocation:
    """Record of an addressed location within an action group."""

    file: str
    line: int | None
    thread_id: str | None
    addressed_at: datetime
    commit_sha: str


@dataclass
class ActionGroupProgress:
    """Progress tracking for an action group."""

    group_id: str
    total_locations: int
    addressed_locations: list[AddressedLocation]

    @property
    def is_complete(self) -> bool:
        return len(self.addressed_locations) >= self.total_locations

    @property
    def progress_pct(self) -> float:
        if self.total_locations == 0:
            return 100.0
        return (len(self.addressed_locations) / self.total_locations) * 100


# In session.results["action_group_progress"]
{
    "group-1": {
        "total_locations": 4,
        "addressed_locations": [
            {"file": "SKILL.md", "line": 239, "addressed_at": "...", "commit_sha": "abc123"},
            {"file": "SKILL.md", "line": 398, "addressed_at": "...", "commit_sha": "abc123"},
            # 2 more pending
        ]
    }
}
```

Resume from partial progress:

```python
def fix_action_group(ctx: PipelineContext, group: ActionGroup) -> FixResult:
    """Fix an action group, resuming from partial progress if any."""

    progress = ctx.get_group_progress(group.id)
    if progress and progress.is_complete:
        log.info(f"Group {group.id} already complete, skipping")
        return FixResult(skipped=[{"id": group.id, "reason": "already_complete"}])

    # Filter to only unaddressed locations
    pending_locations = [
        loc for loc in group.locations
        if not progress or not progress.has_location(loc)
    ]

    log.info(f"Group {group.id}: {len(pending_locations)}/{group.location_count} locations pending")

    # Fix pending locations
    result = run_fixer_for_locations(ctx, group, pending_locations)

    # Update progress
    for loc in result.addressed_locations:
        ctx.record_location_addressed(group.id, loc)

    return result
```

## Cross-Reference Detection

Detect when review body references line comments:

```python
# In src/cross_reference.py

import re

def extract_line_references(text: str) -> list[int]:
    """Extract line number references from text.

    Detects patterns like:
    - "line 42"
    - "L42"
    - "lines 10-20"
    - "#L42" (GitHub link format)
    """
    patterns = [
        r'\bline\s+(\d+)\b',
        r'\bL(\d+)\b',
        r'\blines?\s+(\d+)[-–](\d+)\b',
        r'#L(\d+)',
    ]

    lines = set()
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            lines.add(int(match.group(1)))
            if match.lastindex >= 2:
                lines.add(int(match.group(2)))

    return sorted(lines)


def link_reviews_to_threads(
    reviews: list[ReviewFeedback],
    threads: list[ThreadFeedback],
) -> dict[str, list[str]]:
    """Link review IDs to related thread IDs based on line references.

    Returns:
        Dict mapping review ID to list of related thread IDs
    """
    links = {}

    for review in reviews:
        referenced_lines = extract_line_references(review.body)
        if not referenced_lines:
            continue

        related_threads = []
        for thread in threads:
            if thread.line in referenced_lines:
                related_threads.append(thread.id)

        if related_threads:
            links[review.id] = related_threads
            review.references_lines = referenced_lines

    return links
```

Usage in consolidation:

```python
def consolidate_feedback(filtered: FilteredFeedback, ctx: PipelineContext):
    # Detect cross-references before sending to LLM
    links = link_reviews_to_threads(filtered.reviews, filtered.threads)

    # Mark linked threads to avoid double-processing
    for review_id, thread_ids in links.items():
        for thread_id in thread_ids:
            thread = next((t for t in filtered.threads if t.id == thread_id), None)
            if thread:
                thread.linked_to_review = review_id

    # Send to LLM with link information
    task = build_consolidation_task(filtered, links)
    ...
```

## Implementation Plan

See individual stage documents for detailed implementation steps:

| Phase | Stage | Document |
|-------|-------|----------|
| Phase 1: Data Models | Stage 8 | [stage-8-data-models.md](stage-8-data-models.md) |
| Phase 2: Filter Stage | Stage 9 | [stage-9-filter.md](stage-9-filter.md) |
| Phase 3: Infrastructure | Stage 10 | [stage-10-infrastructure.md](stage-10-infrastructure.md) |
| Phase 4: Cement Hooks | Stage 11 | [stage-11-hooks.md](stage-11-hooks.md) |
| Phase 5: Pipeline Refactor | Stage 12 | [stage-12-pipeline.md](stage-12-pipeline.md) |
| Phase 6: Testing | Stage 13 | [stage-13-testing.md](stage-13-testing.md) |

Each stage document contains:
- **Objective**: What this stage accomplishes
- **Dependencies**: Required prior stages
- **Steps**: Detailed implementation with code samples
- **Checklist Gate**: Criteria to proceed to next stage
- **Files Created/Modified**: Table of file changes
- **Effort Estimate**: Hours for this stage

## Acceptance Criteria

### Issue #796 (Updated Comment Detection)
- [ ] Store content hash when marking feedback as addressed
- [ ] Compare hash when filtering already-addressed feedback
- [ ] Re-process comments whose content has changed
- [ ] Add tests for updated comment detection

### Thread Comment Tracking
- [ ] Track which thread comments have been processed
- [ ] Only process new comments in threads
- [ ] Detect author responses that signal resolution
- [ ] Detect reviewer withdrawals ("never mind", "ignore this")
- [ ] Skip threads with author resolution signals

### Session Locking
- [ ] Acquire file-based lock before processing
- [ ] Prevent concurrent runs on same PR
- [ ] Display helpful error when lock held
- [ ] Release lock on completion or error

### Thread Resolution
- [ ] Call GitHub GraphQL to resolve threads after addressing
- [ ] Track which threads were resolved in session
- [ ] Handle resolution failures gracefully

### Dry-Run Mode
- [ ] `--dry-run` flag runs discovery→filter→consolidate only
- [ ] `--stop-after` flag allows stopping at any stage
- [ ] Dry-run output shows what would be addressed

### Partial Addressing
- [ ] Track progress at location level, not just action group
- [ ] Resume from partial progress on re-run
- [ ] Skip already-complete action groups

### Cross-Reference Detection
- [ ] Detect line references in review body ("see line 42")
- [ ] Link reviews to threads at referenced lines
- [ ] Mark linked threads to avoid double-processing

### Hook Integration
- [ ] Define all pipeline hooks (pre/post for each stage)
- [ ] Hooks fire at correct points in pipeline
- [ ] Error hooks fire on stage failure
- [ ] State persists correctly via post_commit hook

### Pipeline Separation
- [ ] Discovery stage is pure GitHub API calls
- [ ] Filter stage is deterministic (no LLM)
- [ ] Consolidation stage is LLM-powered
- [ ] Fix stage executes in batches
- [ ] Commit stage handles git operations + thread resolution

## Migration Path

1. **Backward Compatible**: New schema fields are optional
2. **Graceful Upgrade**: First run after upgrade processes all items (no history)
3. **No Data Loss**: Old sessions still work, just without delta detection
4. **Lock Files**: Created in sessions directory, auto-cleaned on release

## Estimated Effort

| Phase | Effort |
|-------|--------|
| Phase 1: Data Models | 3 hours |
| Phase 2: Filter Stage | 4 hours |
| Phase 3: Infrastructure | 3 hours |
| Phase 4: Cement Hooks | 2 hours |
| Phase 5: Pipeline Refactor | 4 hours |
| Phase 6: Testing | 4 hours |
| **Total** | **20 hours** |

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Thread resolution fails | Log warning, don't fail pipeline |
| Lock file orphaned | Add PID check, allow force-unlock CLI |
| Cross-reference false positives | LLM consolidation as second pass |
| Content hash collision | Use SHA-256, collision astronomically unlikely |
