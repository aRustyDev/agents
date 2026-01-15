# Stage 4: Commit & Status

> Implement git commit, push, PR status updates, and the main addressing loop.

## Objective

Complete the iteration cycle with git operations, PR comments, and status updates.

## Dependencies

- Stage 3 complete (Feedback loop works)

## Steps

### 4.1 Create src/addresser.py

Main addressing loop:

```python
"""Main addressing loop."""

import time
from dataclasses import dataclass
from pathlib import Path

from skill_agents_common.github_ops import add_issue_comment, mark_pr_ready
from .discovery import discover, IterationContext
from .feedback import analyze_feedback, fix_with_escalation, FixResult, AnalysisResult
from .github_pr import request_rereview, update_project_status
from .exceptions import IterationLimitError, ConflictError

@dataclass
class AddressingResult:
    """Result of addressing a PR."""
    pr_number: int
    iterations: int
    total_addressed: int
    total_skipped: int
    all_addressed: bool
    pr_url: str | None = None

class Addresser:
    def __init__(self, app):
        self.app = app
        self.config = app.config
        self.agent_dir = Path(__file__).parent.parent
        self.max_iterations = int(self.config.get('skill-pr-addresser', 'max_iterations') or 3)
        self.rate_limit_delay = float(self.config.get('skill-pr-addresser', 'rate_limit_delay') or 1.0)

    def address(
        self,
        pr_number: int,
        dry_run: bool = False,
    ) -> AddressingResult:
        """Address all feedback on a PR."""

        iterations = 0
        total_addressed = 0
        total_skipped = 0

        while iterations < self.max_iterations:
            iterations += 1
            self.app.log.info(f"Iteration {iterations}/{self.max_iterations}")

            # Discover current state
            ctx = discover(
                owner=self.config.get('skill-pr-addresser', 'repo_owner'),
                repo=self.config.get('skill-pr-addresser', 'repo_name'),
                pr_number=pr_number,
                sessions_dir=self.agent_dir / "data" / "sessions",
                repo_path=self.app.repo_path,
            )

            # Analyze feedback
            analysis = analyze_feedback(self.agent_dir, ctx)

            unresolved = [i for i in analysis.feedback_items if not i.resolved]
            if not unresolved:
                self.app.log.info("All feedback addressed!")
                break

            self.app.log.info(f"Unresolved items: {len(unresolved)}")

            # Fix feedback
            if not dry_run:
                result = fix_with_escalation(self.agent_dir, ctx, analysis)
                total_addressed += len(result.addressed)
                total_skipped += len(result.skipped)

                # Commit and push
                if result.addressed:
                    self._commit_and_push(ctx, result, analysis)

                # Rate limiting
                time.sleep(self.rate_limit_delay)
            else:
                self.app.log.info("[DRY RUN] Would fix feedback")
                break

        if iterations >= self.max_iterations:
            self.app.log.warning(f"Reached max iterations ({self.max_iterations})")

        # Final status update
        all_addressed = total_skipped == 0 and iterations < self.max_iterations

        if not dry_run:
            self._update_final_status(ctx, all_addressed, total_addressed, total_skipped)

        return AddressingResult(
            pr_number=pr_number,
            iterations=iterations,
            total_addressed=total_addressed,
            total_skipped=total_skipped,
            all_addressed=all_addressed,
            pr_url=ctx.pr.url,
        )

    def _commit_and_push(
        self,
        ctx: IterationContext,
        result: FixResult,
        analysis: AnalysisResult,
    ):
        """Commit changes and push to remote."""
        import subprocess

        wt = ctx.worktree_path

        # Check for conflicts before committing
        status = subprocess.run(
            ["git", "-C", str(wt), "status", "--porcelain"],
            capture_output=True, text=True
        )
        if "UU " in status.stdout or "AA " in status.stdout:
            raise ConflictError("Merge conflict detected in worktree")

        # Stage all changes
        subprocess.run(["git", "-C", str(wt), "add", "-A"], check=True)

        # Build commit message
        changes = "\n".join(f"- {a['action']}" for a in result.addressed)
        reviewers = ", ".join(analysis.blocking_reviews) or "reviewers"

        message = f"""fix({ctx.session.skill_path}): address review feedback

### Changed
{changes}

Addresses feedback from: {reviewers}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
"""

        subprocess.run(
            ["git", "-C", str(wt), "commit", "-m", message],
            check=True
        )

        subprocess.run(
            ["git", "-C", str(wt), "push"],
            check=True
        )

        # Comment on PR
        self._add_iteration_comment(ctx, result)

    def _add_iteration_comment(self, ctx: IterationContext, result: FixResult):
        """Add comment to PR summarizing changes."""
        import chevron

        template = (self.agent_dir / "templates" / "iteration_comment.hbs").read_text()
        comment = chevron.render(template, {
            "addressed": result.addressed,
            "skipped": result.skipped,
            "files_modified": result.files_modified,
            "lines_added": result.lines_added,
            "lines_removed": result.lines_removed,
        })

        add_issue_comment(
            self.config.get('skill-pr-addresser', 'repo_owner'),
            self.config.get('skill-pr-addresser', 'repo_name'),
            ctx.pr.number,
            comment,
        )

    def _update_final_status(
        self,
        ctx: IterationContext,
        all_addressed: bool,
        total_addressed: int,
        total_skipped: int,
    ):
        """Update PR status after all iterations."""
        owner = self.config.get('skill-pr-addresser', 'repo_owner')
        repo = self.config.get('skill-pr-addresser', 'repo_name')

        if all_addressed:
            # Mark PR as ready for review
            mark_pr_ready(owner, repo, ctx.pr.number)

            # Update project status
            update_project_status(owner, repo, ctx.pr.number, "In Review")

            # Request re-review from blocking reviewers
            if ctx.blocking_reviewers:
                request_rereview(owner, repo, ctx.pr.number, ctx.blocking_reviewers)

            self.app.log.info("PR marked as ready for review")
        else:
            # Comment with progress
            add_issue_comment(
                owner, repo, ctx.pr.number,
                f"Addressed {total_addressed} items. {total_skipped} items could not be addressed automatically."
            )
```

- [ ] Create `src/addresser.py`
- [ ] Implement `Addresser` class
- [ ] Implement `address()` main loop
- [ ] Implement `_commit_and_push()`
- [ ] Implement `_add_iteration_comment()`
- [ ] Implement `_update_final_status()`

### 4.2 Create templates

```handlebars
{{! templates/iteration_comment.hbs }}
## Feedback Addressed

{{#if addressed}}
### Changes Made

{{#each addressed}}
- ✅ **{{id}}**: {{action}}
{{/each}}
{{/if}}

{{#if skipped}}
### Items Not Addressed

{{#each skipped}}
- ⚠️ **{{id}}**: {{reason}}
{{/each}}
{{/if}}

### Summary

- Files modified: {{files_modified.length}}
- Lines added: {{lines_added}}
- Lines removed: {{lines_removed}}

---
*🤖 Generated with [Claude Code](https://claude.com/claude-code)*
```

```handlebars
{{! templates/ready_comment.hbs }}
## Ready for Review

All feedback has been addressed.

### Summary

- Iterations: {{iterations}}
- Items addressed: {{total_addressed}}
- Files modified: {{files_count}}

Please re-review when convenient.

---
*🤖 Generated with [Claude Code](https://claude.com/claude-code)*
```

- [ ] Create `templates/iteration_comment.hbs`
- [ ] Create `templates/ready_comment.hbs`

### 4.3 Add update_project_status to github_pr.py

```python
def update_project_status(
    owner: str,
    repo: str,
    pr_number: int,
    status: str,
) -> bool:
    """Update the project status for a PR."""
    # Use gh api to update project item status
    # Similar to skill-reviewer's github_projects.py
    ...
```

- [ ] Implement `update_project_status()`

### 4.4 Wire up to controller

```python
# controllers/base.py
@ex(
    arguments=[
        (['pr_number'], {'type': int, 'help': 'PR number to address'}),
        (['--dry-run'], {'action': 'store_true'}),
        (['--tui'], {'action': 'store_true'}),
        (['--verbose'], {'action': 'store_true'}),
    ]
)
def address(self):
    """Address review feedback on a PR."""
    from ..addresser import Addresser

    addresser = Addresser(self.app)

    try:
        result = addresser.address(
            pr_number=self.app.pargs.pr_number,
            dry_run=self.app.pargs.dry_run,
        )

        self.app.log.info(f"Completed in {result.iterations} iterations")
        self.app.log.info(f"Addressed: {result.total_addressed}, Skipped: {result.total_skipped}")

        if result.all_addressed:
            self.app.log.info("PR is ready for review")
        else:
            self.app.log.warning("Some items could not be addressed")

    except Exception as e:
        self.app.log.error(str(e))
        self.app.exit_code = 1
```

- [ ] Update `address` command
- [ ] Add proper result logging

### 4.5 Add addresser tests

```python
# tests/test_addresser.py
import pytest
from src.addresser import Addresser

def test_address_stops_after_max_iterations(mocker, app):
    addresser = Addresser(app)
    # Mock to always return unresolved feedback
    result = addresser.address(795, dry_run=True)
    assert result.iterations == 3

def test_address_commits_changes(mocker, app, tmp_path):
    # ... verify git commit is called

def test_address_marks_ready_when_complete(mocker, app):
    # ... verify mark_pr_ready is called
```

- [ ] Create `tests/test_addresser.py`

## Checklist Gate

Before proceeding to Stage 5:

- [ ] `just address-skill-reviews 795` completes full cycle
- [ ] Changes are committed with proper message format
- [ ] Changes are pushed to remote
- [ ] PR comment is added after each iteration
- [ ] PR marked ready when all feedback addressed
- [ ] Skipped items are commented on PR
- [ ] Max iterations limit is respected
- [ ] All addresser tests pass

## Files Created/Modified

| File | Action |
|------|--------|
| `src/addresser.py` | Create |
| `src/github_pr.py` | Modify (add update_project_status) |
| `src/controllers/base.py` | Modify |
| `templates/iteration_comment.hbs` | Create |
| `templates/ready_comment.hbs` | Create |
| `tests/test_addresser.py` | Create |

## Estimated Effort

- Addresser class: ~3 hours
- Git operations: ~1 hour
- Templates: ~30 minutes
- Controller integration: ~1 hour
- Tests: ~1 hour
- **Total: ~6.5 hours**
