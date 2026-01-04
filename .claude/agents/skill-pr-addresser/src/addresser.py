"""Main addresser orchestration for skill-pr-addresser.

Orchestrates the full feedback addressing loop:
1. Analyze feedback
2. Fix issues
3. Commit and push changes
4. Post iteration comment
5. Request re-review when done
"""

import logging
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Add parent directory to path for shared library import
_agents_dir = Path(__file__).parent.parent.parent
if str(_agents_dir) not in sys.path:
    sys.path.insert(0, str(_agents_dir))

from skill_agents_common.models import Stage

from .costs import CallCost, SessionCosts, format_cost
from .discovery import DiscoveryContext
from .exceptions import ConflictError, IterationLimitError
from .feedback import (
    AnalysisResult,
    FixResult,
    SubstantiveCheckResult,
    analyze_feedback,
    check_substantive_feedback,
    fix_with_escalation,
)
from .github_pr import add_pr_comment, request_rereview
from .templates import render_template
from .tracing import span, record_iteration, traced


log = logging.getLogger(__name__)


@dataclass
class IterationResult:
    """Result from a single addressing iteration."""

    iteration: int
    analysis: AnalysisResult
    fix_result: FixResult
    commit_sha: str | None = None
    pushed: bool = False
    comment_url: str | None = None
    costs: list[CallCost] = field(default_factory=list)

    @property
    def iteration_cost(self) -> float:
        """Total cost for this iteration."""
        return sum(c.total_cost for c in self.costs)


@dataclass
class AddressingResult:
    """Final result from the addressing process."""

    success: bool
    iterations_run: int
    total_addressed: int
    total_skipped: int
    files_modified: list[str] = field(default_factory=list)
    final_commit_sha: str | None = None
    ready_for_review: bool = False
    error: str | None = None
    iteration_results: list[IterationResult] = field(default_factory=list)
    total_cost: float = 0.0

    @property
    def cost_formatted(self) -> str:
        """Format total cost for display."""
        return format_cost(self.total_cost)


class Addresser:
    """Orchestrates the feedback addressing loop."""

    def __init__(
        self,
        agent_dir: Path,
        sessions_dir: Path,
        owner: str,
        repo: str,
        rate_limit_delay: float = 1.0,
    ):
        """Initialize the addresser.

        Args:
            agent_dir: Path to the agent directory
            sessions_dir: Path to sessions directory
            owner: Repository owner
            repo: Repository name
            rate_limit_delay: Delay between API calls in seconds
        """
        self.agent_dir = agent_dir
        self.sessions_dir = sessions_dir
        self.owner = owner
        self.repo = repo
        self.rate_limit_delay = rate_limit_delay

    @traced("addresser.address")
    def address(
        self,
        ctx: DiscoveryContext,
        max_iterations: int = 3,
    ) -> AddressingResult:
        """Run the feedback addressing loop.

        Args:
            ctx: Discovery context with PR info
            max_iterations: Maximum number of addressing iterations

        Returns:
            AddressingResult with summary of what was done
        """
        total_addressed = 0
        total_skipped = 0
        all_files_modified: set[str] = set()
        iteration_results: list[IterationResult] = []
        final_sha: str | None = None

        # Initialize cost tracking
        session_costs = SessionCosts(
            session_id=ctx.session.session_id,
            pr_number=ctx.pr_number,
        )

        # Run substantive checks on pending feedback (if any)
        if ctx.needs_substantive_check:
            log.info(
                f"Running substantive check on {len(ctx.pending_reviews)} reviews, "
                f"{len(ctx.pending_comments)} comments..."
            )
            with span("substantive_check"):
                subst_result, subst_cost = check_substantive_feedback(
                    self.agent_dir,
                    ctx.pending_reviews,
                    ctx.pending_comments,
                )
                if subst_cost:
                    session_costs.add_call(subst_cost)
                    log.debug(f"Substantive check cost: {format_cost(subst_cost.total_cost)}")

                # Move substantive items into context
                ctx.substantive_reviews = subst_result.substantive_reviews
                ctx.substantive_comments = subst_result.substantive_comments

                log.info(
                    f"Substantive check: {len(subst_result.substantive_reviews)} reviews, "
                    f"{len(subst_result.substantive_comments)} comments are actionable"
                )

                if subst_result.not_substantive_ids:
                    log.debug(f"Not substantive: {subst_result.not_substantive_ids}")

        # Check if we have any feedback to address
        log.debug(
            f"Feedback counts - blocking: {len(ctx.blocking_reviews)}, "
            f"actionable: {len(ctx.actionable_reviews)}, "
            f"substantive: {len(ctx.substantive_reviews)}, "
            f"threads: {len(ctx.unresolved_threads)}, "
            f"total: {ctx.feedback_count}"
        )

        if not ctx.needs_changes:
            log.info("No actionable feedback to address")
            return AddressingResult(
                success=True,
                iterations_run=0,
                total_addressed=0,
                total_skipped=0,
                ready_for_review=True,
                total_cost=session_costs.total_cost,
            )

        for iteration in range(1, max_iterations + 1):
            log.info(f"=== Iteration {iteration}/{max_iterations} ===")
            iteration_costs: list[CallCost] = []

            with span(f"iteration.{iteration}", {"pr": ctx.pr_number}):
                # Update session stage
                ctx.session.update_stage(Stage.ANALYSIS)
                ctx.session.save(self.sessions_dir)

                # Step 1: Analyze feedback
                log.info("Analyzing feedback...")
                log.debug(
                    f"Passing to analyzer - reviews: {len(ctx.all_reviews)}, "
                    f"comments: {len(ctx.all_comments)}, threads: {len(ctx.unresolved_threads)}"
                )
                with span("analyze_feedback"):
                    analysis, analysis_cost = analyze_feedback(self.agent_dir, ctx)
                    if analysis_cost:
                        iteration_costs.append(analysis_cost)
                        session_costs.add_call(analysis_cost)

                # Check for feedback in both new (action_groups) and legacy (feedback_items) formats
                has_feedback = bool(analysis.action_groups) or bool(analysis.feedback_items)
                if not has_feedback:
                    log.info("No feedback items found from analyzer")
                    log.debug(f"Analyzer summary: {analysis.summary}")
                    break

                # Log what was found
                if analysis.action_groups:
                    log.info(
                        f"Found {len(analysis.action_groups)} action groups "
                        f"({len(analysis.guidance)} guidance items)"
                    )
                else:
                    log.info(f"Found {len(analysis.feedback_items)} feedback items (legacy format)")

                if not analysis.actionable_count:
                    log.info("No actionable items to fix")
                    break

                # Step 2: Fix feedback
                ctx.session.update_stage(Stage.FIXING)
                ctx.session.save(self.sessions_dir)

                log.info("Fixing feedback...")
                with span("fix_feedback"):
                    fix_result, fix_costs = fix_with_escalation(self.agent_dir, ctx, analysis)
                    for cost in fix_costs:
                        iteration_costs.append(cost)
                        session_costs.add_call(cost)

                total_addressed += len(fix_result.addressed)
                total_skipped += len(fix_result.skipped)
                all_files_modified.update(fix_result.files_modified)

            # Step 3: Commit and push if changes were made
            commit_sha = None
            pushed = False

            if fix_result.addressed:
                try:
                    commit_sha = self._commit_changes(
                        ctx, iteration, fix_result
                    )
                    if commit_sha:
                        self._push_changes(ctx)
                        pushed = True
                        final_sha = commit_sha
                        log.info(f"Pushed changes: {commit_sha[:8]}")
                except ConflictError as e:
                    log.error(f"Git conflict: {e}")
                    ctx.session.add_error(str(e))
                    break

            # Step 4: Post iteration comment
            comment_url = self._add_iteration_comment(
                ctx, iteration, analysis, fix_result, commit_sha
            )

            iteration_result = IterationResult(
                iteration=iteration,
                analysis=analysis,
                fix_result=fix_result,
                commit_sha=commit_sha,
                pushed=pushed,
                comment_url=comment_url,
                costs=iteration_costs,
            )
            iteration_results.append(iteration_result)

            # Record iteration for tracing
            record_iteration(
                iteration=iteration,
                feedback_count=analysis.actionable_count,
                addressed_count=len(fix_result.addressed),
                skipped_count=len(fix_result.skipped),
                success_rate=fix_result.success_rate,
            )

            # Store in session
            ctx.session.results[f"iteration_{iteration}"] = {
                "analysis_summary": analysis.summary,
                "feedback_count": analysis.actionable_count,
                "action_groups": len(analysis.action_groups),
                "guidance": analysis.guidance,
                "addressed": len(fix_result.addressed),
                "skipped": len(fix_result.skipped),
                "files_modified": fix_result.files_modified,
                "commit_sha": commit_sha,
                "cost": iteration_result.iteration_cost,
            }
            ctx.session.save(self.sessions_dir)

            # Log iteration cost
            if iteration_costs:
                log.info(f"Iteration {iteration} cost: {format_cost(iteration_result.iteration_cost)}")

            # Check if we're done
            if fix_result.success_rate >= 0.9:
                log.info("High success rate - addressing complete")
                break

            if not fix_result.addressed:
                log.warning("No items addressed in this iteration")
                break

        # Final status update
        ready_for_review = total_addressed > 0 and total_skipped == 0
        success = total_addressed > 0

        # Save session costs
        session_costs.save(self.sessions_dir)
        total_cost = session_costs.total_cost

        if success:
            ctx.session.update_stage(Stage.COMPLETE)
            log.info("Feedback addressing complete!")
            log.info(f"Total cost: {format_cost(total_cost)}")

            if ready_for_review:
                # Request re-review from blocking reviewers
                self._request_rereview(ctx)
        else:
            ctx.session.update_stage(Stage.FAILED)
            log.warning("Could not address feedback")

        # Store final cost in session
        ctx.session.results["total_cost"] = total_cost
        ctx.session.save(self.sessions_dir)

        return AddressingResult(
            success=success,
            iterations_run=len(iteration_results),
            total_addressed=total_addressed,
            total_skipped=total_skipped,
            files_modified=list(all_files_modified),
            final_commit_sha=final_sha,
            ready_for_review=ready_for_review,
            iteration_results=iteration_results,
            total_cost=total_cost,
        )

    def _commit_changes(
        self,
        ctx: DiscoveryContext,
        iteration: int,
        fix_result: FixResult,
    ) -> str | None:
        """Commit changes made in the worktree.

        Args:
            ctx: Discovery context
            iteration: Current iteration number
            fix_result: Result from fixing

        Returns:
            Commit SHA if successful, None otherwise

        Raises:
            ConflictError: If there are merge conflicts
        """
        worktree_path = Path(ctx.worktree.path)

        # Check for unstaged changes
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=worktree_path,
            capture_output=True,
            text=True,
        )

        if not status_result.stdout.strip():
            log.info("No changes to commit")
            return None

        # Stage all changes
        subprocess.run(
            ["git", "add", "-A"],
            cwd=worktree_path,
            check=True,
        )

        # Build commit message
        addressed_summary = ", ".join(
            item.get("id", "unknown")[:20] for item in fix_result.addressed[:5]
        )
        if len(fix_result.addressed) > 5:
            addressed_summary += f", ... (+{len(fix_result.addressed) - 5} more)"

        commit_message = f"""fix(skills): address PR #{ctx.pr_number} feedback (iteration {iteration})

### Changed
- Addressed {len(fix_result.addressed)} feedback items: {addressed_summary}
- Modified files: {', '.join(fix_result.files_modified)}

### Stats
- Lines added: +{fix_result.lines_added}
- Lines removed: -{fix_result.lines_removed}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4 <noreply@anthropic.com>
"""

        # Create commit
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=worktree_path,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            if "conflict" in result.stderr.lower():
                raise ConflictError(f"Merge conflict during commit: {result.stderr}")
            log.error(f"Commit failed: {result.stderr}")
            return None

        # Get commit SHA
        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=worktree_path,
            capture_output=True,
            text=True,
        )

        return sha_result.stdout.strip() if sha_result.returncode == 0 else None

    def _push_changes(self, ctx: DiscoveryContext) -> bool:
        """Push changes to remote.

        Attempts to push, and if rejected due to remote changes,
        pulls with rebase and retries.

        Args:
            ctx: Discovery context

        Returns:
            True if push succeeded
        """
        worktree_path = Path(ctx.worktree.path)

        # First attempt to push
        result = subprocess.run(
            ["git", "push", "origin", ctx.pr.branch],
            cwd=worktree_path,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return True

        # Check if rejected due to remote changes
        if "fetch first" in result.stderr or "non-fast-forward" in result.stderr:
            log.info("Remote has changes, pulling with rebase...")

            # Pull with rebase
            pull_result = subprocess.run(
                ["git", "pull", "--rebase", "origin", ctx.pr.branch],
                cwd=worktree_path,
                capture_output=True,
                text=True,
            )

            if pull_result.returncode != 0:
                if "conflict" in pull_result.stderr.lower() or "conflict" in pull_result.stdout.lower():
                    log.error(f"Rebase conflict: {pull_result.stderr}")
                    # Abort the rebase
                    subprocess.run(
                        ["git", "rebase", "--abort"],
                        cwd=worktree_path,
                        capture_output=True,
                    )
                    raise ConflictError(f"Rebase conflict during pull: {pull_result.stderr}")
                log.error(f"Pull failed: {pull_result.stderr}")
                return False

            # Retry push
            retry_result = subprocess.run(
                ["git", "push", "origin", ctx.pr.branch],
                cwd=worktree_path,
                capture_output=True,
                text=True,
            )

            if retry_result.returncode != 0:
                log.error(f"Push failed after rebase: {retry_result.stderr}")
                return False

            log.info("Push succeeded after rebase")
            return True

        log.error(f"Push failed: {result.stderr}")
        return False

    def _add_iteration_comment(
        self,
        ctx: DiscoveryContext,
        iteration: int,
        analysis: AnalysisResult,
        fix_result: FixResult,
        commit_sha: str | None,
    ) -> str | None:
        """Add a comment summarizing the iteration.

        Args:
            ctx: Discovery context
            iteration: Iteration number
            analysis: Analysis result
            fix_result: Fix result
            commit_sha: Commit SHA if changes were made

        Returns:
            Comment URL if successful
        """
        template_data = {
            "iteration": iteration,
            "pr_number": ctx.pr_number,
            "skill_path": ctx.skill_path,
            "feedback_count": analysis.actionable_count,
            "action_groups_count": len(analysis.action_groups),
            "guidance": analysis.guidance,
            "addressed_count": len(fix_result.addressed),
            "skipped_count": len(fix_result.skipped),
            "addressed": fix_result.addressed,
            "skipped": fix_result.skipped,
            "files_modified": fix_result.files_modified,
            "lines_added": fix_result.lines_added,
            "lines_removed": fix_result.lines_removed,
            "commit_sha": commit_sha,
            "commit_short": commit_sha[:8] if commit_sha else None,
            "success_rate": f"{fix_result.success_rate * 100:.0f}%",
            "timestamp": datetime.utcnow().isoformat(),
        }

        body = render_template(self.agent_dir / "templates", "iteration_comment", template_data)

        return add_pr_comment(
            self.owner, self.repo, ctx.pr_number, body
        )

    def _request_rereview(self, ctx: DiscoveryContext) -> bool:
        """Request re-review from blocking reviewers.

        Args:
            ctx: Discovery context

        Returns:
            True if re-review was requested
        """
        if not ctx.blocking_reviewers:
            log.info("No blocking reviewers to request re-review from")
            return False

        # Post ready comment
        template_data = {
            "pr_number": ctx.pr_number,
            "skill_path": ctx.skill_path,
            "reviewers": ctx.blocking_reviewers,
            "timestamp": datetime.utcnow().isoformat(),
        }

        body = render_template(self.agent_dir / "templates", "ready_comment", template_data)
        add_pr_comment(self.owner, self.repo, ctx.pr_number, body)

        # Request re-review
        success = request_rereview(
            self.owner, self.repo, ctx.pr_number, ctx.blocking_reviewers
        )

        if success:
            log.info(f"Requested re-review from: {', '.join(ctx.blocking_reviewers)}")
        else:
            log.warning("Failed to request re-review")

        return success
