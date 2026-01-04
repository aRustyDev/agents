"""Pipeline executor for skill-pr-addresser.

Orchestrates all pipeline stages using the hooks framework:
1. Discovery - Find PR and extract feedback
2. Filter - Remove already-addressed items (delta detection)
3. Consolidate - Group feedback into action groups
4. Plan - Create execution plan
5. Fix - Implement fixes for each action group
6. Commit - Commit and push changes
7. Notify - Post comments and request re-review

Each stage has pre_/post_ hooks for extensibility.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .commit import create_iteration_commit, push_changes
from .consolidate import consolidate_feedback, ConsolidationResult
from .discovery import discover, DiscoveryContext
from .dry_run import DryRunMode, DryRunSummary
from .filter import filter_feedback, FilterResult
from .fix import fix_action_group, FixGroupResult
from .github_pr import (
    add_pr_comment,
    request_rereview,
    resolve_addressed_threads,
)
from .hooks import (
    HookContext,
    HookRegistry,
    PIPELINE_HOOKS,
    run_hook,
)
from .location_progress import PRLocationProgress
from .locking import session_lock, LockError
from .models import ActionGroup, FeedbackItem
from .planner import create_execution_plan, ExecutionPlan
from .templates import (
    format_summary_comment,
    format_iteration_limit_comment,
    format_error_comment,
    format_no_feedback_comment,
    format_partial_progress_comment,
)

log = logging.getLogger(__name__)


@dataclass
class StageResult:
    """Result from a single pipeline stage."""

    stage: str
    success: bool
    duration_ms: float = 0.0
    error: str | None = None
    data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "stage": self.stage,
            "success": self.success,
            "duration_ms": self.duration_ms,
            "error": self.error,
            "data": self.data,
        }


@dataclass
class IterationResult:
    """Result from a single addressing iteration."""

    iteration: int
    addressed_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0
    commit_sha: str | None = None
    pushed: bool = False
    stage_results: list[StageResult] = field(default_factory=list)
    cost: float = 0.0

    @property
    def success(self) -> bool:
        return all(r.success for r in self.stage_results)

    def to_dict(self) -> dict:
        return {
            "iteration": self.iteration,
            "addressed_count": self.addressed_count,
            "skipped_count": self.skipped_count,
            "failed_count": self.failed_count,
            "commit_sha": self.commit_sha,
            "pushed": self.pushed,
            "success": self.success,
            "cost": self.cost,
            "stages": [r.to_dict() for r in self.stage_results],
        }


@dataclass
class PipelineResult:
    """Final result from the pipeline."""

    success: bool
    pr_number: int
    iterations_run: int = 0
    total_addressed: int = 0
    total_skipped: int = 0
    total_failed: int = 0
    final_commit_sha: str | None = None
    ready_for_review: bool = False
    error: str | None = None
    iteration_results: list[IterationResult] = field(default_factory=list)
    total_cost: float = 0.0
    dry_run: bool = False

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "pr_number": self.pr_number,
            "iterations_run": self.iterations_run,
            "total_addressed": self.total_addressed,
            "total_skipped": self.total_skipped,
            "total_failed": self.total_failed,
            "final_commit_sha": self.final_commit_sha,
            "ready_for_review": self.ready_for_review,
            "error": self.error,
            "total_cost": self.total_cost,
            "dry_run": self.dry_run,
            "iterations": [r.to_dict() for r in self.iteration_results],
        }


class Pipeline:
    """Orchestrates the feedback addressing pipeline.

    Usage:
        pipeline = Pipeline(
            agent_dir=Path("..."),
            sessions_dir=Path("..."),
            owner="aRustyDev",
            repo="ai",
        )
        result = pipeline.run(pr_number=795, max_iterations=3)

    With hooks:
        pipeline = Pipeline(...)
        pipeline.hooks.register("pre_fix", my_custom_hook)
        result = pipeline.run(pr_number=795)

    Dry-run mode:
        result = pipeline.run(pr_number=795, dry_run=True)
    """

    def __init__(
        self,
        agent_dir: Path,
        sessions_dir: Path,
        owner: str,
        repo: str,
        repo_path: Path | None = None,
        worktree_base: Path | None = None,
        rate_limit_delay: float = 1.0,
        app=None,  # Optional Cement app for hooks
    ):
        """Initialize the pipeline.

        Args:
            agent_dir: Path to the agent directory
            sessions_dir: Path to sessions directory
            owner: Repository owner
            repo: Repository name
            repo_path: Path to the repository root
            worktree_base: Base directory for worktrees
            rate_limit_delay: Delay between API calls
            app: Optional Cement app for hooks integration
        """
        self.agent_dir = agent_dir
        self.sessions_dir = sessions_dir
        self.owner = owner
        self.repo = repo
        self.repo_path = repo_path or agent_dir.parent.parent.parent
        self.worktree_base = worktree_base or Path("/private/tmp/worktrees")
        self.rate_limit_delay = rate_limit_delay
        self.app = app

        # Create standalone hook registry if no app
        self.hooks = HookRegistry()
        for hook_name in PIPELINE_HOOKS:
            self.hooks.define(hook_name)

        # Progress tracking
        self._progress: PRLocationProgress | None = None
        self._dry_run_mode: DryRunMode | None = None

    def run(
        self,
        pr_number: int,
        max_iterations: int = 3,
        skill_path: str | None = None,
        force: bool = False,
        dry_run: bool = False,
        stop_after: str | None = None,
    ) -> PipelineResult:
        """Run the pipeline for a PR.

        Args:
            pr_number: Pull request number
            max_iterations: Maximum addressing iterations
            skill_path: Explicit skill path (auto-detected if None)
            force: Force addressing even if no pending feedback
            dry_run: Preview changes without making them
            stop_after: Stop after this stage (for debugging)

        Returns:
            PipelineResult with summary of what was done
        """
        import time

        start_time = time.perf_counter()

        # Initialize dry-run mode
        self._dry_run_mode = DryRunMode(enabled=dry_run, stop_after=stop_after)

        # Initialize progress tracking
        self._progress = PRLocationProgress(pr_number=pr_number)

        result = PipelineResult(
            success=False,
            pr_number=pr_number,
            dry_run=dry_run,
        )

        try:
            # Acquire session lock
            with session_lock(self.sessions_dir, pr_number) as lock:
                log.info(f"Acquired lock for PR #{pr_number}")

                # Run the pipeline
                result = self._run_pipeline(
                    pr_number=pr_number,
                    max_iterations=max_iterations,
                    skill_path=skill_path,
                    force=force,
                )

        except LockError as e:
            log.error(f"Could not acquire lock: {e}")
            result.error = f"Lock error: {e}"

        except Exception as e:
            log.exception(f"Pipeline error: {e}")
            result.error = str(e)

            # Run error hook
            self._run_hook(
                "on_error",
                HookContext(
                    pr_number=pr_number,
                    stage="pipeline",
                    data={"error": str(e), "stage": "pipeline"},
                ),
            )

        duration_ms = (time.perf_counter() - start_time) * 1000
        log.info(f"Pipeline completed in {duration_ms:.0f}ms")

        return result

    def _run_pipeline(
        self,
        pr_number: int,
        max_iterations: int,
        skill_path: str | None,
        force: bool,
    ) -> PipelineResult:
        """Internal pipeline execution."""
        result = PipelineResult(
            success=False,
            pr_number=pr_number,
            dry_run=self._dry_run_mode.enabled if self._dry_run_mode else False,
        )

        # Stage 1: Discovery
        ctx = self._run_discovery(pr_number, skill_path, force)
        if ctx is None:
            result.error = "Discovery failed"
            return result

        if self._should_stop("discovery"):
            result.success = True
            return result

        # Check if there's feedback to address
        if not ctx.needs_changes and not force:
            log.info("No actionable feedback to address")
            result.success = True
            result.ready_for_review = True
            return result

        # Run iterations
        for iteration in range(1, max_iterations + 1):
            log.info(f"=== Iteration {iteration}/{max_iterations} ===")

            iteration_result = self._run_iteration(ctx, iteration)
            result.iteration_results.append(iteration_result)
            result.iterations_run = iteration

            # Aggregate counts
            result.total_addressed += iteration_result.addressed_count
            result.total_skipped += iteration_result.skipped_count
            result.total_failed += iteration_result.failed_count
            result.total_cost += iteration_result.cost

            if iteration_result.commit_sha:
                result.final_commit_sha = iteration_result.commit_sha

            # Check if we're done
            if iteration_result.addressed_count == 0:
                log.info("No items addressed in this iteration, stopping")
                break

            # Re-discover for next iteration
            if iteration < max_iterations:
                ctx = self._run_discovery(pr_number, skill_path, force=True)
                if ctx is None or not ctx.needs_changes:
                    log.info("No more feedback to address")
                    break

        # Final notification
        if not self._dry_run_mode.enabled:
            self._run_notify(ctx, result)

        result.success = True
        result.ready_for_review = result.total_failed == 0

        return result

    def _run_discovery(
        self,
        pr_number: int,
        skill_path: str | None,
        force: bool,
    ) -> DiscoveryContext | None:
        """Run discovery stage."""
        import time

        start = time.perf_counter()
        hook_ctx = HookContext(pr_number=pr_number, stage="discovery")

        self._run_hook("pre_discovery", hook_ctx)
        if hook_ctx.cancelled:
            return None

        try:
            ctx = discover(
                owner=self.owner,
                repo=self.repo,
                pr_number=pr_number,
                sessions_dir=self.sessions_dir,
                worktree_base=self.worktree_base,
                repo_path=self.repo_path,
                skill_path=skill_path,
                force=force,
            )

            hook_ctx.data["discovery_context"] = ctx
            self._run_hook("post_discovery", hook_ctx)

            duration = (time.perf_counter() - start) * 1000
            log.debug(f"Discovery completed in {duration:.0f}ms")

            return ctx

        except Exception as e:
            log.error(f"Discovery failed: {e}")
            hook_ctx.data["error"] = str(e)
            self._run_hook("on_error", hook_ctx)
            return None

    def _run_iteration(
        self,
        ctx: DiscoveryContext,
        iteration: int,
    ) -> IterationResult:
        """Run a single addressing iteration."""
        import time

        result = IterationResult(iteration=iteration)
        hook_ctx = HookContext(
            pr_number=ctx.pr_number,
            iteration=iteration,
            stage="iteration",
        )

        self._run_hook("pre_iteration", hook_ctx)
        if hook_ctx.cancelled:
            return result

        # Start progress tracking for this iteration
        iter_progress = self._progress.get_or_start_iteration()

        # Stage 2: Filter (delta detection)
        filter_result = self._run_filter(ctx, iteration)
        if filter_result is None or self._should_stop("filter"):
            return result

        # Stage 3: Consolidate
        consolidation = self._run_consolidate(ctx, filter_result, iteration)
        if consolidation is None or self._should_stop("consolidate"):
            return result

        # Stage 4: Plan
        plan = self._run_plan(consolidation, iteration)
        if plan is None or self._should_stop("plan"):
            return result

        # Stage 5: Fix (for each action group)
        fix_results = self._run_fixes(ctx, plan, iteration)

        # Aggregate fix results
        addressed_threads = []
        for fix_result in fix_results:
            if fix_result.success and not fix_result.skipped:
                result.addressed_count += len(fix_result.addressed_locations)
                addressed_threads.extend(fix_result.addressed_thread_ids)
            elif fix_result.skipped:
                result.skipped_count += 1
            else:
                result.failed_count += 1

        # Stage 6: Commit
        if result.addressed_count > 0 and not self._dry_run_mode.enabled:
            commit_result = self._run_commit(ctx, fix_results, iteration)
            if commit_result:
                result.commit_sha = commit_result.get("sha")
                result.pushed = commit_result.get("pushed", False)

                # Resolve addressed threads
                if addressed_threads:
                    resolve_addressed_threads(
                        self.owner,
                        self.repo,
                        addressed_threads,
                        delay=self.rate_limit_delay,
                    )

        # Complete iteration progress
        iter_progress.complete()

        self._run_hook("post_iteration", hook_ctx)

        return result

    def _run_filter(
        self,
        ctx: DiscoveryContext,
        iteration: int,
    ) -> FilterResult | None:
        """Run filter stage for delta detection."""
        import time

        start = time.perf_counter()
        hook_ctx = HookContext(
            pr_number=ctx.pr_number,
            iteration=iteration,
            stage="filter",
        )

        self._run_hook("pre_filter", hook_ctx)
        if hook_ctx.cancelled:
            return None

        try:
            # Get all feedback items from context
            all_items = self._extract_feedback_items(ctx)

            # Load previous session state for delta detection
            prev_state = self._load_previous_state(ctx.pr_number)

            filter_result = filter_feedback(
                feedback_items=all_items,
                previous_state=prev_state,
            )

            hook_ctx.data["filter_result"] = filter_result
            self._run_hook("post_filter", hook_ctx)

            duration = (time.perf_counter() - start) * 1000
            log.debug(
                f"Filter: {filter_result.new_count} new, "
                f"{filter_result.unchanged_count} unchanged, "
                f"{filter_result.resolved_count} resolved "
                f"({duration:.0f}ms)"
            )

            return filter_result

        except Exception as e:
            log.error(f"Filter stage failed: {e}")
            return None

    def _run_consolidate(
        self,
        ctx: DiscoveryContext,
        filter_result: FilterResult,
        iteration: int,
    ) -> ConsolidationResult | None:
        """Run consolidation stage."""
        import time

        start = time.perf_counter()
        hook_ctx = HookContext(
            pr_number=ctx.pr_number,
            iteration=iteration,
            stage="consolidate",
        )

        self._run_hook("pre_consolidate", hook_ctx)
        if hook_ctx.cancelled:
            return None

        try:
            consolidation = consolidate_feedback(
                agent_dir=self.agent_dir,
                ctx=ctx,
                filtered_items=filter_result.new_items,
            )

            hook_ctx.data["consolidation"] = consolidation
            self._run_hook("post_consolidate", hook_ctx)

            duration = (time.perf_counter() - start) * 1000
            log.debug(
                f"Consolidation: {len(consolidation.action_groups)} groups "
                f"({duration:.0f}ms)"
            )

            return consolidation

        except Exception as e:
            log.error(f"Consolidation stage failed: {e}")
            return None

    def _run_plan(
        self,
        consolidation: ConsolidationResult,
        iteration: int,
    ) -> ExecutionPlan | None:
        """Run planning stage."""
        import time

        start = time.perf_counter()
        hook_ctx = HookContext(
            pr_number=0,  # Not available here
            iteration=iteration,
            stage="plan",
        )

        self._run_hook("pre_plan", hook_ctx)
        if hook_ctx.cancelled:
            return None

        try:
            plan = create_execution_plan(
                action_groups=consolidation.action_groups,
                guidance=consolidation.guidance,
            )

            hook_ctx.data["plan"] = plan
            self._run_hook("post_plan", hook_ctx)

            duration = (time.perf_counter() - start) * 1000
            log.debug(f"Plan: {len(plan.steps)} steps ({duration:.0f}ms)")

            return plan

        except Exception as e:
            log.error(f"Planning stage failed: {e}")
            return None

    def _run_fixes(
        self,
        ctx: DiscoveryContext,
        plan: ExecutionPlan,
        iteration: int,
    ) -> list[FixGroupResult]:
        """Run fix stage for each planned step."""
        import time

        results = []
        hook_ctx = HookContext(
            pr_number=ctx.pr_number,
            iteration=iteration,
            stage="fix",
        )

        self._run_hook("pre_fix", hook_ctx)
        if hook_ctx.cancelled:
            return results

        for step in plan.steps:
            start = time.perf_counter()

            group_ctx = HookContext(
                pr_number=ctx.pr_number,
                iteration=iteration,
                stage="fix_group",
                data={"group_id": step.group_id},
            )

            self._run_hook("pre_fix_group", group_ctx)
            if group_ctx.cancelled:
                continue

            try:
                if self._dry_run_mode.enabled:
                    # Dry run - record what would be done
                    self._dry_run_mode.would_commit(
                        f"Fix {step.group_id}",
                        [loc.file for loc in step.action_group.locations],
                    )
                    fix_result = FixGroupResult(
                        group_id=step.group_id,
                        success=True,
                        skipped=False,
                        addressed_locations=[],
                        addressed_thread_ids=[],
                    )
                else:
                    fix_result = fix_action_group(
                        agent_dir=self.agent_dir,
                        ctx=ctx,
                        action_group=step.action_group,
                        guidance=plan.guidance,
                    )

                group_ctx.data["fix_result"] = fix_result
                self._run_hook("post_fix_group", group_ctx)

                results.append(fix_result)

                duration = (time.perf_counter() - start) * 1000
                log.debug(
                    f"Fixed group {step.group_id}: "
                    f"{len(fix_result.addressed_locations)} locations "
                    f"({duration:.0f}ms)"
                )

            except Exception as e:
                log.error(f"Fix failed for group {step.group_id}: {e}")
                results.append(
                    FixGroupResult(
                        group_id=step.group_id,
                        success=False,
                        skipped=False,
                        reason=str(e),
                        addressed_locations=[],
                        addressed_thread_ids=[],
                    )
                )

        hook_ctx.data["fix_results"] = results
        self._run_hook("post_fix", hook_ctx)

        return results

    def _run_commit(
        self,
        ctx: DiscoveryContext,
        fix_results: list[FixGroupResult],
        iteration: int,
    ) -> dict | None:
        """Run commit stage."""
        import time

        start = time.perf_counter()
        hook_ctx = HookContext(
            pr_number=ctx.pr_number,
            iteration=iteration,
            stage="commit",
        )

        self._run_hook("pre_commit", hook_ctx)
        if hook_ctx.cancelled:
            return None

        try:
            # Create commit
            commit_sha = create_iteration_commit(
                worktree_path=ctx.worktree_path,
                pr_number=ctx.pr_number,
                iteration=iteration,
                fix_results=fix_results,
            )

            if not commit_sha:
                log.warning("No changes to commit")
                return None

            # Push changes
            pushed = push_changes(
                worktree_path=ctx.worktree_path,
                branch=ctx.pr.head_branch,
            )

            result = {"sha": commit_sha, "pushed": pushed}

            hook_ctx.data["commit_result"] = result
            self._run_hook("post_commit", hook_ctx)

            duration = (time.perf_counter() - start) * 1000
            log.debug(f"Commit {commit_sha[:7]} pushed={pushed} ({duration:.0f}ms)")

            return result

        except Exception as e:
            log.error(f"Commit stage failed: {e}")
            return None

    def _run_notify(
        self,
        ctx: DiscoveryContext,
        result: PipelineResult,
    ) -> None:
        """Run notification stage."""
        hook_ctx = HookContext(
            pr_number=ctx.pr_number,
            iteration=result.iterations_run,
            stage="notify",
        )

        self._run_hook("pre_notify", hook_ctx)
        if hook_ctx.cancelled:
            return

        try:
            # Format summary comment
            if result.total_addressed > 0:
                comment = format_summary_comment(
                    pr_number=ctx.pr_number,
                    iteration=result.iterations_run,
                    fix_results=[r.to_dict() for r in result.iteration_results],
                    commit_sha=result.final_commit_sha or "",
                )
                add_pr_comment(self.owner, self.repo, ctx.pr_number, comment)

                # Request re-review if ready
                if result.ready_for_review:
                    reviewers = [r.author for r in ctx.blocking_reviews]
                    if reviewers:
                        request_rereview(self.owner, self.repo, ctx.pr_number, reviewers)

            elif result.error:
                comment = format_error_comment("pipeline", result.error)
                add_pr_comment(self.owner, self.repo, ctx.pr_number, comment)

            else:
                comment = format_no_feedback_comment()
                add_pr_comment(self.owner, self.repo, ctx.pr_number, comment)

            self._run_hook("post_notify", hook_ctx)

        except Exception as e:
            log.error(f"Notification failed: {e}")

    def _run_hook(self, hook_name: str, context: HookContext) -> None:
        """Run a hook, using app hooks if available, otherwise standalone registry."""
        if self.app and hasattr(self.app, "hook"):
            run_hook(self.app, hook_name, context)
        else:
            list(self.hooks.run(hook_name, self, context))

    def _should_stop(self, stage: str) -> bool:
        """Check if we should stop after this stage."""
        if self._dry_run_mode and self._dry_run_mode.stop_after == stage:
            log.info(f"[DRY RUN] Stopping after {stage} stage")
            return True
        return False

    def _extract_feedback_items(self, ctx: DiscoveryContext) -> list[FeedbackItem]:
        """Extract feedback items from discovery context."""
        items = []

        # From reviews
        for review in ctx.all_reviews:
            items.append(
                FeedbackItem(
                    id=f"review-{review.id}",
                    source_type="review",
                    author=review.author,
                    body=review.body or "",
                    file=None,
                    line=None,
                    thread_id=None,
                )
            )

        # From threads
        for thread in ctx.unresolved_threads:
            items.append(
                FeedbackItem(
                    id=f"thread-{thread.id}",
                    source_type="thread",
                    author=thread.author,
                    body=thread.body or "",
                    file=thread.path,
                    line=thread.line,
                    thread_id=thread.id,
                )
            )

        return items

    def _load_previous_state(self, pr_number: int) -> dict | None:
        """Load previous session state for delta detection."""
        import json

        state_file = self.sessions_dir / f"pr-{pr_number}" / "state.json"
        if state_file.exists():
            try:
                return json.loads(state_file.read_text())
            except Exception:
                pass
        return None


def run_pipeline(
    pr_number: int,
    agent_dir: Path,
    sessions_dir: Path,
    owner: str,
    repo: str,
    max_iterations: int = 3,
    dry_run: bool = False,
    **kwargs,
) -> PipelineResult:
    """Convenience function to run the pipeline.

    Args:
        pr_number: Pull request number
        agent_dir: Path to agent directory
        sessions_dir: Path to sessions directory
        owner: Repository owner
        repo: Repository name
        max_iterations: Maximum iterations
        dry_run: Preview changes only
        **kwargs: Additional Pipeline constructor args

    Returns:
        PipelineResult
    """
    pipeline = Pipeline(
        agent_dir=agent_dir,
        sessions_dir=sessions_dir,
        owner=owner,
        repo=repo,
        **kwargs,
    )
    return pipeline.run(
        pr_number=pr_number,
        max_iterations=max_iterations,
        dry_run=dry_run,
    )
