# Stage 12: Pipeline Refactor

> Refactor addresser into stage-based execution with hook integration.

## Objective

Split the monolithic `address()` function into discrete stages that use the hook system, support partial execution, and maintain state between runs.

## Dependencies

- Stage 11 complete (Cement hooks defined and registered)

## External Dependencies

This stage requires the `skill_agents_common` package:

```bash
# Install from local path (during development)
pip install -e /path/to/skill-agents-common

# OR install from package index (when published)
pip install skill-agents-common
```

**Required exports from skill_agents_common**:
- `AgentSession` - Session management and persistence
- `WorktreeManager` - Git worktree operations (optional, can use `src/worktree.py`)

If `skill_agents_common` is not available, use the inline `AgentSession` implementation below:

```python
# src/session.py (fallback if skill_agents_common not installed)
"""Fallback session implementation."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class AgentSession:
    """Session management for PR processing."""

    pr_number: int
    owner: str
    repo: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    results: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, pr_number: int, owner: str, repo: str) -> "AgentSession":
        return cls(pr_number=pr_number, owner=owner, repo=repo)

    @classmethod
    def load(cls, path: Path) -> "AgentSession":
        with open(path) as f:
            data = json.load(f)
        return cls(
            pr_number=data["pr_number"],
            owner=data["owner"],
            repo=data["repo"],
            created_at=datetime.fromisoformat(data["created_at"]),
            results=data.get("results", {}),
        )

    def save(self, sessions_dir: Path) -> None:
        sessions_dir.mkdir(parents=True, exist_ok=True)
        path = sessions_dir / f"pr-{self.pr_number}.json"
        with open(path, "w") as f:
            json.dump({
                "pr_number": self.pr_number,
                "owner": self.owner,
                "repo": self.repo,
                "created_at": self.created_at.isoformat(),
                "results": self.results,
            }, f, indent=2)
```

## Steps

### 12.1 Create PipelineContext

```python
# src/pipeline.py
"""Pipeline context and execution."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from cement import App
    from .filter import FilteredFeedback
    from .session_schema import FeedbackState
    from .progress import IterationProgress

# Import core types from models (defined in Stage 8)
from .models import (
    RawFeedback,
    ActionGroup,
    TokenUsage,
    FixResult,
)


@dataclass
class ConsolidatedFeedback:
    """Consolidated feedback from LLM."""

    action_groups: list[ActionGroup] = field(default_factory=list)
    guidance: list[str] = field(default_factory=list)
    token_usage: TokenUsage = field(default_factory=TokenUsage)

    # Cross-reference links from filter stage
    thread_links: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    """Planned execution order."""

    steps: list[dict] = field(default_factory=list)
    total_items: int = 0


@dataclass
class PipelineContext:
    """Context passed through all pipeline stages.

    Logging convention: Always use `ctx.app.log.<level>()` for consistency.
    Do not use `ctx.log()` - that method is removed for clarity.
    """

    # Immutable inputs
    app: "App"
    pr_number: int
    owner: str
    repo: str
    pr_author: str
    worktree_path: Path
    agent_dir: Path
    sessions_dir: Path
    dry_run: bool = False
    stop_after: str | None = None

    # Session
    session: Any = None
    iteration: int = 1

    # Stage outputs (populated as pipeline runs)
    raw_feedback: RawFeedback | None = None
    filtered_feedback: "FilteredFeedback | None" = None
    consolidated: ConsolidatedFeedback | None = None
    plan: ExecutionPlan | None = None
    fix_results: list[FixResult] = field(default_factory=list)
    commit_sha: str | None = None
    resolved_threads: list[str] = field(default_factory=list)

    # Cross-reference links (populated by filter stage)
    thread_links: dict[str, list[str]] = field(default_factory=dict)

    # State tracking
    feedback_state: "FeedbackState | None" = None
    iteration_progress: "IterationProgress | None" = None

    # Timing (using timezone-aware datetime)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    _stage_start_time: float | None = None

    @property
    def model(self) -> str:
        """Get configured model name."""
        return self.app.config.get('skill-pr-addresser', 'model', fallback='sonnet')

    def should_stop_after(self, stage: str) -> bool:
        """Check if pipeline should stop after this stage."""
        return self.stop_after == stage
```

**Note**: `RawFeedback`, `ActionGroup`, `TokenUsage`, and `FixResult` are imported from `src/models.py` (defined in Stage 8) to avoid circular dependencies.

- [ ] Create `src/pipeline.py`
- [ ] Define RawFeedback, ConsolidatedFeedback, ExecutionPlan
- [ ] Define PipelineContext with all stage outputs

### 12.2 Create pipeline executor

```python
# src/pipeline.py (continued)

from .stages import run_stage, StageResult, StageStatus
from .locking import session_lock


class Pipeline:
    """Stage-based pipeline executor."""

    STAGES = [
        'discovery',
        'filter',
        'consolidate',
        'plan',
        'fix',
        'commit',
        'resolve_threads',
    ]

    def __init__(self, app: "App"):
        self.app = app

    def execute(
        self,
        pr_number: int,
        dry_run: bool = False,
        stop_after: str | None = None,
    ) -> PipelineContext:
        """Execute the pipeline for a PR.

        Args:
            pr_number: PR to process
            dry_run: If True, don't make changes
            stop_after: Stop after this stage

        Returns:
            PipelineContext with all stage results
        """
        # Acquire session lock
        sessions_dir = Path(
            self.app.config.get('skill-pr-addresser', 'sessions_dir')
        )

        with session_lock(sessions_dir, pr_number) as lock:
            self.app.log.debug(f"Acquired lock: {lock.lock_file}")

            # Create context
            ctx = self._create_context(pr_number, dry_run, stop_after)

            # Load or create session
            ctx.session = self._load_or_create_session(ctx)
            ctx.feedback_state = FeedbackState.from_session(ctx.session)
            ctx.iteration_progress = self._load_progress(ctx)

            # Run pipeline hooks
            for result in self.app.hook.run('pre_address', ctx):
                pass

            try:
                # Execute stages
                for stage_name in self.STAGES:
                    result = self._run_stage(stage_name, ctx)

                    if not result.should_continue:
                        self.app.log.info(
                            f"Pipeline stopped at {stage_name}: {result.reason}"
                        )
                        break

                    if ctx.should_stop_after(stage_name):
                        self.app.log.info(f"Stopping after {stage_name} (--stop-after)")
                        break

            finally:
                # Always run post_address
                for result in self.app.hook.run('post_address', ctx):
                    pass

            return ctx

    def _run_stage(self, stage_name: str, ctx: PipelineContext) -> StageResult:
        """Run a single stage."""
        stage_fn = getattr(self, f'_stage_{stage_name}', None)
        if not stage_fn:
            raise ValueError(f"Unknown stage: {stage_name}")

        return run_stage(self.app, stage_name, stage_fn, ctx)

    def _create_context(
        self,
        pr_number: int,
        dry_run: bool,
        stop_after: str | None,
    ) -> PipelineContext:
        """Create pipeline context from PR info."""
        from .discovery import discover_pr_info

        pr_info = discover_pr_info(pr_number)

        return PipelineContext(
            app=self.app,
            pr_number=pr_number,
            owner=pr_info.owner,
            repo=pr_info.repo,
            pr_author=pr_info.author,
            worktree_path=pr_info.worktree_path,
            agent_dir=Path(__file__).parent.parent,
            sessions_dir=Path(
                self.app.config.get('skill-pr-addresser', 'sessions_dir')
            ),
            dry_run=dry_run,
            stop_after=stop_after,
        )

    def _load_or_create_session(self, ctx: PipelineContext):
        """Load existing session or create new one."""
        from skill_agents_common.session import AgentSession

        session_file = ctx.sessions_dir / f"pr-{ctx.pr_number}.json"
        if session_file.exists():
            return AgentSession.load(session_file)
        return AgentSession.create(
            pr_number=ctx.pr_number,
            owner=ctx.owner,
            repo=ctx.repo,
        )

    def _load_progress(self, ctx: PipelineContext) -> "IterationProgress":
        """Load iteration progress from session."""
        from .progress import IterationProgress

        data = ctx.session.results.get("iteration_progress")
        if data:
            return IterationProgress.from_dict(data)
        return IterationProgress(
            iteration=ctx.iteration,
            started_at=datetime.now(timezone.utc),
        )
```

- [ ] Create Pipeline class
- [ ] Define STAGES list
- [ ] Implement execute method with lock
- [ ] Create context and load session

### 12.3 Implement stage functions

```python
# src/pipeline.py (continued)

class Pipeline:
    # ... (previous code)

    def _stage_discovery(self, ctx: PipelineContext) -> StageResult:
        """Fetch all feedback from GitHub."""
        from .discovery import fetch_reviews, fetch_comments, fetch_threads
        from .models import ReviewFeedback, CommentFeedback, ThreadFeedback

        reviews = fetch_reviews(ctx.owner, ctx.repo, ctx.pr_number)
        comments = fetch_comments(ctx.owner, ctx.repo, ctx.pr_number)
        threads = fetch_threads(ctx.owner, ctx.repo, ctx.pr_number)

        ctx.raw_feedback = RawFeedback(
            reviews=[ReviewFeedback.from_github(r) for r in reviews],
            comments=[CommentFeedback.from_github(c) for c in comments],
            threads=[ThreadFeedback.from_github(t) for t in threads],
        )

        return StageResult.success('discovery', data=ctx.raw_feedback)

    def _stage_filter(self, ctx: PipelineContext) -> StageResult:
        """Filter to new/changed feedback only.

        Also extracts cross-reference links between reviews and threads.
        """
        from .filter import filter_feedback

        filtered = filter_feedback(
            ctx.raw_feedback,
            ctx.session,
            ctx.pr_author,
        )

        if filtered.is_empty:
            return StageResult.early_exit(
                stage='filter',
                reason='no_new_feedback',
            )

        ctx.filtered_feedback = filtered

        # Extract cross-reference links for consolidation stage
        # Maps review_id -> [thread_id, ...] for linked feedback
        ctx.thread_links = self._extract_thread_links(filtered)

        return StageResult.success('filter', data=filtered)

    def _extract_thread_links(
        self,
        filtered: "FilteredFeedback",
    ) -> dict[str, list[str]]:
        """Extract cross-reference links between reviews and threads.

        Builds a mapping of review IDs to linked thread IDs based on
        the linked_to_review field set during filtering.

        Returns:
            Dict mapping review_id -> [thread_id, ...]
        """
        links: dict[str, list[str]] = {}

        for thread in filtered.threads:
            if hasattr(thread, 'linked_to_review') and thread.linked_to_review:
                review_id = thread.linked_to_review
                if review_id not in links:
                    links[review_id] = []
                links[review_id].append(thread.id)

        return links

    def _stage_consolidate(self, ctx: PipelineContext) -> StageResult:
        """Consolidate feedback using LLM.

        Cross-reference integration: Passes thread_links from filter stage
        to the consolidator, which groups linked reviews+threads together.
        """
        from .consolidate import consolidate_feedback

        if ctx.dry_run:
            # In dry-run, still run consolidation for preview
            pass

        # Pass thread_links from filter stage to consolidator
        # This allows linked reviews and threads to be grouped together
        result = consolidate_feedback(
            ctx.agent_dir,
            ctx.filtered_feedback,
            ctx,
            thread_links=ctx.thread_links,  # Cross-reference links
        )

        if not result.action_groups:
            return StageResult.early_exit(
                stage='consolidate',
                reason='no_actionable_feedback',
            )

        # Store consolidated result with thread_links for downstream stages
        ctx.consolidated = ConsolidatedFeedback(
            action_groups=result.action_groups,
            guidance=result.guidance,
            token_usage=result.token_usage,
            thread_links=result.thread_links,  # Preserve cross-references
        )
        return StageResult.success('consolidate', data=ctx.consolidated)

    def _stage_plan(self, ctx: PipelineContext) -> StageResult:
        """Create execution plan."""
        from .planner import create_plan

        plan = create_plan(ctx.consolidated)
        ctx.plan = plan
        return StageResult.success('plan', data=plan)

    def _stage_fix(self, ctx: PipelineContext) -> StageResult:
        """Execute fixes for each action group."""
        from .fix import fix_action_group

        if ctx.dry_run:
            return StageResult.skipped('fix', reason='dry_run')

        results = []
        for step in ctx.plan.steps:
            group_id = step['group_id']

            # Pre-batch hook
            for r in self.app.hook.run('pre_fix_batch', ctx, group_id):
                pass

            result = fix_action_group(ctx, step)
            results.append(result)

            # Post-batch hook
            for r in self.app.hook.run('post_fix_batch', ctx, group_id, result):
                pass

            # Early exit if fix failed
            if result.failed:
                return StageResult.failed('fix', result.error)

        ctx.fix_results = results
        return StageResult.success('fix', data=results)

    def _stage_commit(self, ctx: PipelineContext) -> StageResult:
        """Commit and push changes."""
        from .commit import commit_and_push, post_pr_comment

        if ctx.dry_run:
            return StageResult.skipped('commit', reason='dry_run')

        # Check if there are changes to commit
        if not any(r.has_changes for r in ctx.fix_results):
            return StageResult.skipped('commit', reason='no_changes')

        commit_sha = commit_and_push(
            ctx.worktree_path,
            ctx.fix_results,
            ctx.iteration,
        )
        ctx.commit_sha = commit_sha

        # Post comment on PR
        post_pr_comment(
            ctx.owner,
            ctx.repo,
            ctx.pr_number,
            ctx.fix_results,
            commit_sha,
        )

        return StageResult.success('commit', data={'sha': commit_sha})

    def _stage_resolve_threads(self, ctx: PipelineContext) -> StageResult:
        """Resolve addressed threads via GitHub API."""
        from .github_pr import resolve_addressed_threads

        if ctx.dry_run:
            return StageResult.skipped('resolve_threads', reason='dry_run')

        # Collect thread IDs from fix results
        thread_ids = []
        for result in ctx.fix_results:
            thread_ids.extend(result.addressed_thread_ids)

        if not thread_ids:
            return StageResult.skipped('resolve_threads', reason='no_threads')

        results = resolve_addressed_threads(
            ctx.owner,
            ctx.repo,
            thread_ids,
        )

        resolved = [tid for tid, success in results.items() if success]
        ctx.resolved_threads = resolved

        return StageResult.success('resolve_threads', data={
            'resolved': len(resolved),
            'total': len(thread_ids),
        })
```

- [ ] Implement _stage_discovery
- [ ] Implement _stage_filter with early exit
- [ ] Implement _stage_consolidate
- [ ] Implement _stage_plan
- [ ] Implement _stage_fix with batch hooks
- [ ] Implement _stage_commit
- [ ] Implement _stage_resolve_threads

### 12.4 Update addresser to use pipeline

```python
# src/addresser.py
"""Main addresser logic using pipeline."""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cement import App


class Addresser:
    """Addresses PR feedback using the pipeline."""

    def __init__(self, app: "App"):
        self.app = app
        self.max_iterations = app.config.get(
            'skill-pr-addresser', 'max_iterations', fallback=3
        )

    def address(
        self,
        pr_number: int,
        dry_run: bool = False,
        stop_after: str | None = None,
    ) -> dict:
        """Address feedback on a PR.

        Args:
            pr_number: PR to process
            dry_run: Preview without changes
            stop_after: Stop after stage

        Returns:
            Result dict with summary
        """
        from .pipeline import Pipeline

        pipeline = Pipeline(self.app)

        # Run pipeline (may iterate)
        iteration = 0
        last_ctx = None

        while iteration < self.max_iterations:
            iteration += 1
            self.app.log.info(f"Iteration {iteration}/{self.max_iterations}")

            ctx = pipeline.execute(
                pr_number,
                dry_run=dry_run,
                stop_after=stop_after,
            )
            last_ctx = ctx

            # Check if we should continue
            if ctx.dry_run:
                break

            # Check if all feedback addressed
            if ctx.filtered_feedback and ctx.filtered_feedback.is_empty:
                self.app.log.info("All feedback addressed!")
                break

            # Check if no more actionable items
            if ctx.consolidated and not ctx.consolidated.action_groups:
                self.app.log.info("No more actionable feedback")
                break

        if iteration >= self.max_iterations and not dry_run:
            self.app.log.warning(
                f"Reached max iterations ({self.max_iterations}). "
                "Some feedback may not be addressed."
            )
            # Post comment about iteration limit
            self._post_iteration_limit_comment(last_ctx)

        return self._build_result(last_ctx, iteration)

    def _post_iteration_limit_comment(self, ctx):
        """Post comment when max iterations reached."""
        from .github_pr import post_pr_comment

        comment = (
            f"Reached maximum iterations ({self.max_iterations}). "
            "Some feedback may require manual attention.\n\n"
            f"**Addressed:** {len(ctx.resolved_threads)} threads\n"
            f"**Remaining:** See unresolved threads above."
        )

        post_pr_comment(
            ctx.owner,
            ctx.repo,
            ctx.pr_number,
            comment,
            is_iteration_limit=True,
        )

    def _build_result(self, ctx, iterations: int) -> dict:
        """Build result summary."""
        return {
            'pr_number': ctx.pr_number,
            'iterations': iterations,
            'resolved_threads': len(ctx.resolved_threads),
            'commit_sha': ctx.commit_sha,
            'dry_run': ctx.dry_run,
            'stopped_after': ctx.stop_after,
        }
```

- [ ] Update Addresser to use Pipeline
- [ ] Implement iteration loop with max limit
- [ ] Post comment when iteration limit reached
- [ ] Build result summary

### 12.5 Update CLI controller

```python
# src/controllers/base.py (update address command)

from ..addresser import Addresser
from ..dry_run import run_dry_run, DryRunSummary


class BaseController(Controller):

    @ex(
        help='Address review feedback on a PR',
        arguments=[
            (['pr_number'], {'type': int, 'help': 'Pull request number'}),
            (['--dry-run'], {
                'action': 'store_true',
                'help': 'Preview without making changes',
            }),
            (['--stop-after'], {
                'choices': ['discovery', 'filter', 'consolidate', 'plan'],
                'default': None,
                'help': 'Stop after specified stage',
            }),
            (['--max-iterations'], {
                'type': int,
                'default': None,
                'help': 'Override max iterations',
            }),
        ],
    )
    def address(self):
        """Address feedback on a pull request."""
        pr_number = self.app.pargs.pr_number
        dry_run = self.app.pargs.dry_run
        stop_after = self.app.pargs.stop_after
        max_iterations = self.app.pargs.max_iterations

        # --stop-after implies --dry-run
        if stop_after and not dry_run:
            dry_run = True
            self.app.log.debug("--stop-after implies --dry-run")

        if dry_run:
            self.app.log.info("DRY RUN - no changes will be made")
            summary = run_dry_run(
                Addresser(self.app),
                pr_number,
                stop_after or 'plan',
            )
            print(summary.to_text())
            return

        # Normal execution
        addresser = Addresser(self.app)
        if max_iterations:
            addresser.max_iterations = max_iterations

        result = addresser.address(pr_number)

        self._print_result(result)

    def _print_result(self, result: dict):
        """Print execution result."""
        if result['dry_run']:
            return

        print(f"\n{'='*50}")
        print(f"PR #{result['pr_number']} - Complete")
        print(f"{'='*50}")
        print(f"Iterations: {result['iterations']}")
        print(f"Resolved Threads: {result['resolved_threads']}")
        if result['commit_sha']:
            print(f"Commit: {result['commit_sha']}")
        print()
```

- [ ] Update address command with new options
- [ ] Support --max-iterations override
- [ ] Print result summary

### 12.6 Add pipeline tests

```python
# tests/test_pipeline.py
"""Tests for pipeline execution."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.pipeline import Pipeline, PipelineContext, RawFeedback
from src.stages import StageResult, StageStatus


class TestPipeline:
    def test_execute_runs_all_stages(self):
        """All stages execute in order."""
        app = MagicMock()
        app.hook.run.return_value = [None]
        app.config.get.return_value = '/tmp/sessions'

        pipeline = Pipeline(app)

        with patch.object(pipeline, '_create_context') as mock_ctx:
            with patch.object(pipeline, '_load_or_create_session'):
                with patch.object(pipeline, '_load_progress'):
                    mock_ctx.return_value = MagicMock(
                        dry_run=True,
                        stop_after='filter',
                        should_stop_after=lambda s: s == 'filter',
                    )

                    # Mock stages
                    pipeline._stage_discovery = MagicMock(
                        return_value=StageResult.success('discovery')
                    )
                    pipeline._stage_filter = MagicMock(
                        return_value=StageResult.success('filter')
                    )

                    with patch('src.pipeline.session_lock'):
                        ctx = pipeline.execute(795, dry_run=True, stop_after='filter')

                    pipeline._stage_discovery.assert_called_once()
                    pipeline._stage_filter.assert_called_once()

    def test_early_exit_stops_pipeline(self):
        """Early exit stops remaining stages."""
        app = MagicMock()
        pipeline = Pipeline(app)

        # Filter returns early exit
        pipeline._stage_discovery = MagicMock(
            return_value=StageResult.success('discovery')
        )
        pipeline._stage_filter = MagicMock(
            return_value=StageResult.early_exit('filter', 'no_new_feedback')
        )
        pipeline._stage_consolidate = MagicMock()

        # ... setup context and execute

        # Consolidate should not be called
        pipeline._stage_consolidate.assert_not_called()


class TestPipelineContext:
    def test_should_stop_after(self):
        ctx = PipelineContext(
            app=MagicMock(),
            pr_number=795,
            owner='owner',
            repo='repo',
            pr_author='author',
            worktree_path='/tmp/wt',
            agent_dir='/tmp/agent',
            sessions_dir='/tmp/sessions',
            stop_after='filter',
        )

        assert ctx.should_stop_after('filter')
        assert not ctx.should_stop_after('consolidate')
```

- [ ] Create `tests/test_pipeline.py`
- [ ] Test all stages execute
- [ ] Test early exit stops pipeline
- [ ] Test stop_after works
- [ ] Test context properties

## Checklist Gate

Before proceeding to Stage 13:

- [ ] Pipeline executes stages in order
- [ ] Hooks fire at correct points
- [ ] Early exit stops pipeline gracefully
- [ ] Dry-run mode prevents changes
- [ ] --stop-after works for all stages
- [ ] Session lock protects execution
- [ ] Iteration loop with max limit works
- [ ] Result summary is accurate

## Files Created/Modified

| File | Purpose |
|------|---------|
| `src/pipeline.py` | Pipeline context and executor |
| `src/addresser.py` | Refactored to use pipeline |
| `src/controllers/base.py` | Updated CLI commands |
| `tests/test_pipeline.py` | Pipeline tests |

## Estimated Effort

- PipelineContext: ~30 minutes
- Pipeline executor: ~1 hour
- Stage functions: ~1 hour
- Addresser refactor: ~30 minutes
- CLI updates: ~30 minutes
- Tests: ~30 minutes
- **Total: ~4 hours**
