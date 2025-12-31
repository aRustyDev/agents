"""Deterministic pipeline operations.

This module contains all operations that are purely programmatic and
do NOT require an LLM. These should be fast, predictable, and testable.

Operations covered:
- Issue discovery and selection
- Issue status updates (GitHub Projects)
- Worktree creation/cleanup
- Branch management
- Draft PR creation
- Token estimation

The LLM is only used for:
- Skill validation (analyzing content)
- Complexity assessment
- Deep analysis
- Applying fixes (generating content)
"""

import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import PipelineConfig
from .github_ops import (
    Issue,
    get_issue_details,
    add_issue_comment,
)
from .github_projects import (
    get_project_id,
    get_status_field,
    get_status_option_id,
    find_backlog_issues,
    get_issue_project_item,
    update_project_item_status,
    ProjectItem,
)
from .tokens import estimate_tokens, TokenEstimate
from .templates import render_inline
from .worktree import (
    create_worktree,
    remove_worktree,
    get_worktree_status,
    WorktreeInfo,
)


@dataclass
class PipelineContext:
    """Context for a pipeline run - all deterministic state."""

    # Identifiers
    session_id: str
    issue_number: int
    skill_path: str

    # Repository info
    repo_owner: str
    repo_name: str
    project_number: int | None

    # GitHub state
    issue: Issue | None = None
    project_item: ProjectItem | None = None
    project_id: str | None = None
    status_field_id: str | None = None

    # Worktree state
    worktree: WorktreeInfo | None = None
    branch_name: str | None = None

    # Estimates
    token_estimate: TokenEstimate | None = None

    # PR state
    pr_number: int | None = None
    pr_url: str | None = None

    # Timing
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Errors
    errors: list[str] | None = None

    def add_error(self, error: str):
        if self.errors is None:
            self.errors = []
        self.errors.append(error)


class DeterministicPipeline:
    """Handles all deterministic (non-LLM) pipeline operations."""

    def __init__(self, config: PipelineConfig, repo_path: Path):
        self.config = config
        self.repo_path = repo_path

    # =========================================================================
    # Issue Discovery
    # =========================================================================

    def find_next_issue(
        self,
        labels: list[str] | None = None,
        assignee: str | None = None
    ) -> ProjectItem | None:
        """Find the oldest backlog issue matching criteria.

        Args:
            labels: Required labels (defaults to config.review_labels)
            assignee: Required assignee (optional)

        Returns:
            Oldest backlog issue or None
        """
        if self.config.project_number is None:
            raise ValueError("project_number must be set in config for issue discovery")

        project_id = get_project_id(self.config.repo_owner, self.config.project_number)
        if not project_id:
            return None

        issues = find_backlog_issues(
            project_id=project_id,
            owner=self.config.repo_owner,
            repo=self.config.repo_name,
            status_name=self.config.backlog_status,
            assignee=assignee,
            labels=labels or self.config.review_labels
        )

        if not issues:
            return None

        # Already sorted oldest first
        return issues[0]

    def get_backlog_count(
        self,
        labels: list[str] | None = None,
        assignee: str | None = None
    ) -> int:
        """Get count of backlog issues matching criteria."""
        if self.config.project_number is None:
            return 0

        project_id = get_project_id(self.config.repo_owner, self.config.project_number)
        if not project_id:
            return 0

        issues = find_backlog_issues(
            project_id=project_id,
            owner=self.config.repo_owner,
            repo=self.config.repo_name,
            status_name=self.config.backlog_status,
            assignee=assignee,
            labels=labels or self.config.review_labels
        )

        return len(issues)

    # =========================================================================
    # Issue Status Management
    # =========================================================================

    def set_issue_in_progress(self, ctx: PipelineContext) -> bool:
        """Set issue to in-progress status.

        Args:
            ctx: Pipeline context

        Returns:
            True if successful
        """
        if self.config.project_number is None:
            # Fall back to labels
            return self._set_status_via_labels(ctx, self.config.in_progress_label)

        return self._set_status_via_project(ctx, self.config.in_progress_status)

    def set_issue_in_review(self, ctx: PipelineContext) -> bool:
        """Set issue to in-review status.

        Args:
            ctx: Pipeline context

        Returns:
            True if successful
        """
        if self.config.project_number is None:
            return self._set_status_via_labels(ctx, self.config.in_review_label)

        return self._set_status_via_project(ctx, self.config.in_review_status)

    def _set_status_via_project(self, ctx: PipelineContext, status_name: str) -> bool:
        """Set status via GitHub Projects."""
        if not ctx.project_id:
            ctx.project_id = get_project_id(
                self.config.repo_owner,
                self.config.project_number
            )

        if not ctx.project_id:
            ctx.add_error(f"Could not find project {self.config.project_number}")
            return False

        # Get status field
        status_field = get_status_field(ctx.project_id)
        if not status_field:
            ctx.add_error("Could not find Status field in project")
            return False

        ctx.status_field_id = status_field.id

        # Get option ID
        option_id = get_status_option_id(status_field, status_name)
        if not option_id:
            ctx.add_error(f"Could not find status option: {status_name}")
            return False

        # Get project item
        if not ctx.project_item:
            ctx.project_item = get_issue_project_item(
                ctx.project_id,
                ctx.issue_number,
                self.config.repo_owner,
                self.config.repo_name
            )

        if not ctx.project_item:
            ctx.add_error(f"Issue #{ctx.issue_number} not found in project")
            return False

        # Update status
        return update_project_item_status(
            ctx.project_id,
            ctx.project_item.item_id,
            status_field.id,
            option_id
        )

    def _set_status_via_labels(self, ctx: PipelineContext, label: str) -> bool:
        """Set status via labels (fallback)."""
        result = subprocess.run(
            ["gh", "issue", "edit", str(ctx.issue_number),
             "--repo", f"{self.config.repo_owner}/{self.config.repo_name}",
             "--add-label", label],
            capture_output=True
        )
        return result.returncode == 0

    # =========================================================================
    # Worktree Management
    # =========================================================================

    def create_worktree(self, ctx: PipelineContext) -> bool:
        """Create worktree for the review.

        Args:
            ctx: Pipeline context

        Returns:
            True if successful
        """
        skill_name = Path(ctx.skill_path).name
        branch_name = f"feat/fix-{skill_name}-{ctx.issue_number}"
        identifier = f"issue-{ctx.issue_number}"

        try:
            worktree = create_worktree(
                repo_path=self.repo_path,
                worktree_base=Path(self.config.worktree_base),
                branch_name=branch_name,
                base_branch=self.config.base_branch,
                identifier=identifier
            )

            ctx.worktree = worktree
            ctx.branch_name = branch_name
            return True

        except subprocess.CalledProcessError as e:
            ctx.add_error(f"Failed to create worktree: {e}")
            return False

    def cleanup_worktree(self, ctx: PipelineContext) -> bool:
        """Remove worktree after completion.

        Args:
            ctx: Pipeline context

        Returns:
            True if successful
        """
        if not ctx.worktree:
            return True

        try:
            remove_worktree(self.repo_path, ctx.worktree.path)
            return True
        except Exception as e:
            ctx.add_error(f"Failed to cleanup worktree: {e}")
            return False

    # =========================================================================
    # Token Estimation
    # =========================================================================

    def estimate_tokens(self, ctx: PipelineContext) -> TokenEstimate:
        """Estimate tokens for the skill review.

        Args:
            ctx: Pipeline context

        Returns:
            TokenEstimate
        """
        skill_path = self.repo_path / ctx.skill_path
        estimate = estimate_tokens(skill_path)
        ctx.token_estimate = estimate
        return estimate

    def check_cost_limits(self, ctx: PipelineContext) -> bool:
        """Check if estimated cost is within limits.

        Args:
            ctx: Pipeline context

        Returns:
            True if within limits
        """
        if not ctx.token_estimate:
            self.estimate_tokens(ctx)

        if ctx.token_estimate.cost_mixed > self.config.max_cost_per_skill:
            ctx.add_error(
                f"Estimated cost ${ctx.token_estimate.cost_mixed:.2f} exceeds "
                f"limit ${self.config.max_cost_per_skill:.2f}"
            )
            return False

        return True

    # =========================================================================
    # GitHub Comments
    # =========================================================================

    def post_start_comment(self, ctx: PipelineContext) -> bool:
        """Post a comment indicating review has started.

        Args:
            ctx: Pipeline context

        Returns:
            True if successful
        """
        if not ctx.token_estimate:
            self.estimate_tokens(ctx)

        comment = render_inline("issue_comment_start", {
            "session_id": ctx.session_id,
            "started_at": ctx.started_at.isoformat() if ctx.started_at else datetime.utcnow().isoformat(),
            "skill_path": ctx.skill_path,
            "estimated_input": f"{ctx.token_estimate.estimated_total_tokens:,}",
            "estimated_output": f"{ctx.token_estimate.fixing_output:,}",
            "estimated_cost": f"{ctx.token_estimate.cost_mixed:.4f}",
        })

        return add_issue_comment(
            self.config.repo_owner,
            self.config.repo_name,
            ctx.issue_number,
            comment
        )

    def post_complete_comment(
        self,
        ctx: PipelineContext,
        results: dict[str, Any]
    ) -> bool:
        """Post a comment indicating review is complete.

        Args:
            ctx: Pipeline context
            results: Results from LLM stages

        Returns:
            True if successful
        """
        duration = "N/A"
        if ctx.started_at and ctx.completed_at:
            delta = ctx.completed_at - ctx.started_at
            duration = f"{int(delta.total_seconds() // 60)}m {int(delta.total_seconds() % 60)}s"

        comment = render_inline("issue_comment_complete", {
            "session_id": ctx.session_id,
            "duration": duration,
            "pillars_before": results.get("pillars_before", "?"),
            "pillars_after": results.get("pillars_after", "?"),
            "lines_added": results.get("lines_added", 0),
            "files_modified": results.get("files_modified", 0),
            "pr_url": ctx.pr_url or "N/A",
            "actual_input": results.get("total_input_tokens", 0),
            "actual_output": results.get("total_output_tokens", 0),
            "actual_cost": f"{results.get('total_cost', 0):.4f}",
        })

        return add_issue_comment(
            self.config.repo_owner,
            self.config.repo_name,
            ctx.issue_number,
            comment
        )

    # =========================================================================
    # Git Operations
    # =========================================================================

    def commit_changes(self, ctx: PipelineContext, message: str) -> bool:
        """Commit staged changes in the worktree.

        Args:
            ctx: Pipeline context
            message: Commit message

        Returns:
            True if successful
        """
        if not ctx.worktree:
            ctx.add_error("No worktree to commit in")
            return False

        # Stage all changes
        result = subprocess.run(
            ["git", "add", "."],
            cwd=ctx.worktree.path,
            capture_output=True
        )
        if result.returncode != 0:
            ctx.add_error("Failed to stage changes")
            return False

        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=ctx.worktree.path,
            capture_output=True
        )
        if result.returncode != 0:
            # Check if nothing to commit
            status = get_worktree_status(ctx.worktree.path)
            if status["clean"]:
                ctx.add_error("No changes to commit")
            else:
                ctx.add_error("Failed to commit changes")
            return False

        return True

    def push_branch(self, ctx: PipelineContext) -> bool:
        """Push the branch to origin.

        Args:
            ctx: Pipeline context

        Returns:
            True if successful
        """
        if not ctx.worktree or not ctx.branch_name:
            ctx.add_error("No worktree or branch to push")
            return False

        result = subprocess.run(
            ["git", "push", "-u", "origin", ctx.branch_name],
            cwd=ctx.worktree.path,
            capture_output=True
        )
        if result.returncode != 0:
            ctx.add_error("Failed to push branch")
            return False

        return True

    # =========================================================================
    # PR Creation
    # =========================================================================

    def create_draft_pr(
        self,
        ctx: PipelineContext,
        title: str,
        body: str
    ) -> bool:
        """Create a draft pull request.

        Args:
            ctx: Pipeline context
            title: PR title
            body: PR body (should include 'Closes #issue')

        Returns:
            True if successful
        """
        if not ctx.branch_name:
            ctx.add_error("No branch for PR")
            return False

        # Ensure body includes issue link
        if f"#{ctx.issue_number}" not in body:
            body += f"\n\nCloses #{ctx.issue_number}"

        result = subprocess.run(
            ["gh", "pr", "create",
             "--repo", f"{self.config.repo_owner}/{self.config.repo_name}",
             "--title", title,
             "--body", body,
             "--head", ctx.branch_name,
             "--base", self.config.base_branch,
             "--draft",
             "--json", "number,url"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            ctx.add_error(f"Failed to create PR: {result.stderr}")
            return False

        import json
        data = json.loads(result.stdout)
        ctx.pr_number = data["number"]
        ctx.pr_url = data["url"]

        return True

    # =========================================================================
    # Full Deterministic Setup
    # =========================================================================

    def setup(self, ctx: PipelineContext) -> bool:
        """Run all deterministic setup steps.

        This includes:
        1. Validate issue exists
        2. Estimate tokens
        3. Check cost limits
        4. Create worktree
        5. Set issue to in-progress
        6. Post start comment

        Args:
            ctx: Pipeline context

        Returns:
            True if all steps succeeded
        """
        ctx.started_at = datetime.utcnow()

        # 1. Get issue details
        ctx.issue = get_issue_details(
            self.config.repo_owner,
            self.config.repo_name,
            ctx.issue_number
        )
        if not ctx.issue:
            ctx.add_error(f"Issue #{ctx.issue_number} not found")
            return False

        # 2. Estimate tokens
        self.estimate_tokens(ctx)

        # 3. Check cost limits
        if not self.check_cost_limits(ctx):
            return False

        # 4. Create worktree
        if not self.create_worktree(ctx):
            return False

        # 5. Set issue to in-progress
        if not self.config.dry_run:
            if not self.set_issue_in_progress(ctx):
                ctx.add_error("Failed to set issue to in-progress")
                # Non-fatal, continue

        # 6. Post start comment
        if not self.config.dry_run:
            self.post_start_comment(ctx)

        return True

    def teardown(
        self,
        ctx: PipelineContext,
        results: dict[str, Any],
        success: bool
    ) -> bool:
        """Run all deterministic teardown steps.

        This includes:
        1. Commit changes (if any)
        2. Push branch
        3. Create draft PR
        4. Set issue to in-review
        5. Post complete comment
        6. Optionally cleanup worktree

        Args:
            ctx: Pipeline context
            results: Results from LLM stages
            success: Whether LLM stages succeeded

        Returns:
            True if all steps succeeded
        """
        ctx.completed_at = datetime.utcnow()

        if not success:
            # Just post error comment and cleanup
            if not self.config.dry_run:
                add_issue_comment(
                    self.config.repo_owner,
                    self.config.repo_name,
                    ctx.issue_number,
                    f"## Review Failed\n\nSession: `{ctx.session_id}`\n\nErrors:\n" +
                    "\n".join(f"- {e}" for e in (ctx.errors or ["Unknown error"]))
                )
            return False

        # 1. Commit changes
        commit_msg = render_inline("commit_message", {
            "type": "feat",
            "scope": Path(ctx.skill_path).name,
            "description": results.get("description", "improve skill documentation"),
            "added": results.get("added", []),
            "changed": results.get("changed", []),
            "fixed": results.get("fixed", []),
            "closes": ctx.issue_number,
        })

        if not self.config.dry_run:
            self.commit_changes(ctx, commit_msg)

        # 2. Push branch
        if not self.config.dry_run:
            self.push_branch(ctx)

        # 3. Create draft PR
        pr_body = render_inline("pr_body", {
            "summary": results.get("summary", ["Improved skill documentation"]),
            "added": results.get("added", []),
            "changed": results.get("changed", []),
            "issues": [ctx.issue_number],
        })

        if not self.config.dry_run:
            self.create_draft_pr(
                ctx,
                f"feat({Path(ctx.skill_path).name}): {results.get('description', 'improve documentation')}",
                pr_body
            )

        # 4. Set issue to in-review
        if not self.config.dry_run:
            self.set_issue_in_review(ctx)

        # 5. Post complete comment
        if not self.config.dry_run:
            self.post_complete_comment(ctx, results)

        return True
