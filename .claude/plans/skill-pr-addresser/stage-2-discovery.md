# Stage 2: Discovery

> Implement PR discovery, session lookup, and worktree management.

## Objective

Build the deterministic discovery stage that gathers all context needed before LLM processing.

## Dependencies

- Stage 0 complete (skill-agents-common)
- Stage 1 complete (Cement skeleton)

## Steps

### 2.1 Create src/github_pr.py

PR-specific GitHub operations (extends skill-agents-common):

```python
"""PR-specific GitHub operations."""

from dataclasses import dataclass
from skill_agents_common.github_ops import PullRequest

@dataclass
class PRDetails(PullRequest):
    """Extended PR details for addresser."""
    is_draft: bool = False
    review_decision: str | None = None
    reviews: list[dict] = None
    comments: list[dict] = None
    review_threads: list[dict] = None

def get_pr_details(owner: str, repo: str, pr_number: int) -> PRDetails | None:
    """Get comprehensive PR details."""
    ...

def get_pr_reviews(owner: str, repo: str, pr_number: int) -> list[dict]:
    """Get all reviews on a PR."""
    ...

def get_pr_comments(owner: str, repo: str, pr_number: int) -> list[dict]:
    """Get all comments on a PR."""
    ...

def get_review_threads(owner: str, repo: str, pr_number: int) -> list[dict]:
    """Get review threads with resolution status."""
    ...

def extract_linked_issues(body: str) -> list[int]:
    """Parse 'Closes #X' patterns from PR body."""
    ...

def request_rereview(owner: str, repo: str, pr_number: int, reviewers: list[str]) -> bool:
    """Request re-review from specified reviewers."""
    ...
```

- [ ] Create `github_pr.py`
- [ ] Implement `get_pr_details()`
- [ ] Implement `get_pr_reviews()`
- [ ] Implement `get_pr_comments()`
- [ ] Implement `get_review_threads()`
- [ ] Implement `extract_linked_issues()`
- [ ] Implement `request_rereview()`

### 2.2 Create src/discovery.py

Main discovery logic:

```python
"""PR and session discovery."""

from dataclasses import dataclass
from pathlib import Path

from skill_agents_common.session import find_session_by_issue, create_session_from_pr
from skill_agents_common.worktree import get_or_create_worktree
from .github_pr import get_pr_details, get_pr_reviews, get_pr_comments, get_review_threads
from .exceptions import PRNotFoundError, PRClosedError, NoFeedbackError

@dataclass
class IterationContext:
    """Context for a single iteration cycle."""
    pr: PRDetails
    session: IterationSession
    worktree_path: Path
    reviews: list[dict]
    comments: list[dict]
    review_threads: list[dict]

    @property
    def feedback_count(self) -> int:
        return len(self.reviews) + len(self.comments) + len(self.review_threads)

    @property
    def blocking_reviewers(self) -> list[str]:
        return [r['author'] for r in self.reviews if r['state'] == 'CHANGES_REQUESTED']

def discover(
    owner: str,
    repo: str,
    pr_number: int,
    sessions_dir: Path,
    repo_path: Path,
) -> IterationContext:
    """Gather all context needed for addressing review feedback."""

    # 1. Get PR details and validate
    pr = get_pr_details(owner, repo, pr_number)
    if not pr:
        raise PRNotFoundError(f"PR #{pr_number} does not exist")

    if pr.state in ("MERGED", "CLOSED"):
        raise PRClosedError(f"PR #{pr_number} is already {pr.state.lower()}")

    # 2. Get feedback
    reviews = get_pr_reviews(owner, repo, pr_number)
    comments = get_pr_comments(owner, repo, pr_number)
    review_threads = get_review_threads(owner, repo, pr_number)

    if not reviews and not comments and not review_threads:
        raise NoFeedbackError(f"PR #{pr_number} has no feedback to address")

    # 3. Find session (with fallback)
    issues = extract_linked_issues(pr.body)
    session = find_session_by_issue(sessions_dir, issues[0]) if issues else None
    if not session:
        session = create_session_from_pr(pr, sessions_dir)

    # 4. Get or recreate worktree
    worktree_path = get_or_create_worktree(repo_path, session.worktree_path, pr.branch)

    return IterationContext(
        pr=pr,
        session=session,
        worktree_path=worktree_path,
        reviews=reviews,
        comments=comments,
        review_threads=review_threads,
    )
```

- [ ] Create `discovery.py`
- [ ] Implement `IterationContext` dataclass
- [ ] Implement `discover()` function
- [ ] Add logging for each step

### 2.3 Update skill-agents-common/session.py

Add new functions:

```python
def find_session_by_issue(sessions_dir: Path, issue_number: int) -> AgentSession | None:
    """Find session by linked issue number."""
    for session_dir in sessions_dir.iterdir():
        if not session_dir.is_dir():
            continue
        session_file = session_dir / "session.json"
        if session_file.exists():
            session = AgentSession.load(session_file)
            if session.issue_number == issue_number:
                return session
    return None

def create_session_from_pr(pr: PRDetails, sessions_dir: Path) -> AgentSession:
    """Create a new session from PR metadata when original not found."""
    session = AgentSession(
        session_id=f"pr-{pr.number}",
        issue_number=None,  # No linked issue
        pr_number=pr.number,
        skill_path=None,  # Will be inferred from changed files
        worktree_path=f"/private/tmp/worktrees/pr-{pr.number}",
        branch_name=pr.branch,
    )
    session.save(sessions_dir)
    return session
```

- [ ] Add `find_session_by_issue()`
- [ ] Add `create_session_from_pr()`

### 2.4 Update skill-agents-common/worktree.py

Add new function:

```python
def get_or_create_worktree(
    repo_path: Path,
    worktree_path: str,
    branch: str,
) -> Path:
    """Get existing worktree or recreate from branch."""
    wt_path = Path(worktree_path)

    if wt_path.exists() and (wt_path / ".git").exists():
        # Worktree exists, pull latest
        subprocess.run(["git", "-C", str(wt_path), "pull", "--rebase"], check=True)
        return wt_path

    # Recreate worktree from branch
    wt_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "-C", str(repo_path), "worktree", "add", str(wt_path), branch],
        check=True
    )
    return wt_path
```

- [ ] Add `get_or_create_worktree()`

### 2.5 Wire up discovery to controller

Update `src/controllers/base.py`:

```python
@ex(
    arguments=[
        (['pr_number'], {'type': int, 'help': 'PR number to address'}),
        (['--dry-run'], {'action': 'store_true', 'help': 'Show what would be done'}),
    ]
)
def address(self):
    """Address review feedback on a PR."""
    pr_number = self.app.pargs.pr_number

    try:
        ctx = discover(
            owner=self.app.config.get('skill-pr-addresser', 'repo_owner'),
            repo=self.app.config.get('skill-pr-addresser', 'repo_name'),
            pr_number=pr_number,
            sessions_dir=self.app.data_dir / "sessions",
            repo_path=self.app.repo_path,
        )

        self.app.log.info(f"Discovered PR #{pr_number}")
        self.app.log.info(f"  Feedback items: {ctx.feedback_count}")
        self.app.log.info(f"  Blocking reviewers: {ctx.blocking_reviewers}")
        self.app.log.info(f"  Worktree: {ctx.worktree_path}")

    except PRNotFoundError as e:
        self.app.log.error(str(e))
        self.app.exit_code = 1
    except PRClosedError as e:
        self.app.log.info(str(e))
    except NoFeedbackError as e:
        self.app.log.info(str(e))
```

- [ ] Update `address` command
- [ ] Add exception handling with correct exit codes

### 2.6 Add discovery tests

```python
# tests/test_discovery.py
import pytest
from src.discovery import discover
from src.exceptions import PRNotFoundError, PRClosedError, NoFeedbackError

def test_discover_pr_not_found(mocker):
    mocker.patch('src.discovery.get_pr_details', return_value=None)
    with pytest.raises(PRNotFoundError):
        discover("owner", "repo", 999, ...)

def test_discover_pr_closed(mocker):
    mocker.patch('src.discovery.get_pr_details', return_value=PRDetails(state="MERGED"))
    with pytest.raises(PRClosedError):
        discover("owner", "repo", 123, ...)

def test_discover_no_feedback(mocker):
    mocker.patch('src.discovery.get_pr_details', return_value=PRDetails(state="OPEN"))
    mocker.patch('src.discovery.get_pr_reviews', return_value=[])
    mocker.patch('src.discovery.get_pr_comments', return_value=[])
    mocker.patch('src.discovery.get_review_threads', return_value=[])
    with pytest.raises(NoFeedbackError):
        discover("owner", "repo", 123, ...)
```

- [ ] Create `tests/test_discovery.py`
- [ ] Add fixtures for mock PR data

## Checklist Gate

Before proceeding to Stage 3:

- [ ] `just address-skill-reviews 795` discovers real PR
- [ ] Missing PR raises `PRNotFoundError` with exit code 1
- [ ] Closed PR raises `PRClosedError` with exit code 0
- [ ] No-feedback PR raises `NoFeedbackError` with exit code 0
- [ ] Missing worktree is recreated from branch
- [ ] Missing session creates fallback from PR metadata
- [ ] All discovery tests pass

## Files Created/Modified

| File | Action |
|------|--------|
| `src/github_pr.py` | Create |
| `src/discovery.py` | Create |
| `src/controllers/base.py` | Modify |
| `skill-agents-common/session.py` | Modify |
| `skill-agents-common/worktree.py` | Modify |
| `tests/test_discovery.py` | Create |
| `tests/fixtures/pr_response.json` | Create |

## Estimated Effort

- GitHub PR functions: ~2 hours
- Discovery logic: ~1 hour
- Common library updates: ~1 hour
- Tests: ~1 hour
- **Total: ~5 hours**
