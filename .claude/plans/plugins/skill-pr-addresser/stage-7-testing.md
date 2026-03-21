# Stage 7: Testing & Polish

> Comprehensive testing, documentation, and final polish.

## Objective

Ensure production readiness with thorough testing, documentation, and edge case handling.

## Dependencies

- Stages 0-6 complete

## Steps

### 7.1 Create test fixtures

```python
# tests/conftest.py
import pytest
from pathlib import Path
import json

@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def pr_response(fixtures_dir):
    return json.loads((fixtures_dir / "pr_response.json").read_text())

@pytest.fixture
def reviews_response(fixtures_dir):
    return json.loads((fixtures_dir / "reviews.json").read_text())

@pytest.fixture
def mock_app(mocker):
    """Mock Cement app for testing."""
    app = mocker.MagicMock()
    app.config.get.return_value = "test"
    app.log = mocker.MagicMock()
    app.tracer = None
    app.meter = None
    return app

@pytest.fixture
def worktree_dir(tmp_path):
    """Create a mock worktree."""
    wt = tmp_path / "worktree"
    wt.mkdir()
    (wt / ".git").touch()
    return wt
```

```json
// tests/fixtures/pr_response.json
{
  "number": 795,
  "title": "fix(skill): address review feedback",
  "state": "OPEN",
  "isDraft": true,
  "body": "Closes #692\n\n## Summary\n...",
  "headRefName": "fix/github-app-dev-692",
  "url": "https://github.com/aRustyDev/agents/pull/795"
}
```

```json
// tests/fixtures/reviews.json
[
  {
    "author": {"login": "reviewer1"},
    "state": "CHANGES_REQUESTED",
    "body": "Please add error handling",
    "submittedAt": "2024-01-15T10:00:00Z"
  }
]
```

- [ ] Create `tests/conftest.py`
- [ ] Create `tests/fixtures/pr_response.json`
- [ ] Create `tests/fixtures/reviews.json`
- [ ] Create `tests/fixtures/review_threads.json`
- [ ] Create `tests/fixtures/comments.json`

### 7.2 Complete unit tests

```python
# tests/test_discovery.py
class TestDiscovery:
    def test_discover_success(self, mocker, pr_response, reviews_response):
        mocker.patch('src.discovery.get_pr_details', return_value=PRDetails(**pr_response))
        mocker.patch('src.discovery.get_pr_reviews', return_value=reviews_response)
        mocker.patch('src.discovery.get_pr_comments', return_value=[])
        mocker.patch('src.discovery.get_review_threads', return_value=[])

        ctx = discover("owner", "repo", 795, ...)

        assert ctx.pr.number == 795
        assert ctx.feedback_count == 1

    def test_discover_pr_not_found(self, mocker):
        mocker.patch('src.discovery.get_pr_details', return_value=None)
        with pytest.raises(PRNotFoundError):
            discover("owner", "repo", 999, ...)

    def test_discover_pr_merged(self, mocker, pr_response):
        pr_response["state"] = "MERGED"
        mocker.patch('src.discovery.get_pr_details', return_value=PRDetails(**pr_response))
        with pytest.raises(PRClosedError):
            discover("owner", "repo", 795, ...)

    def test_discover_session_fallback(self, mocker, pr_response):
        """Creates session when original not found."""
        mocker.patch('src.discovery.find_session_by_issue', return_value=None)
        mocker.patch('src.discovery.create_session_from_pr', return_value=MockSession())
        # ... verify fallback session is created

    def test_discover_worktree_recreate(self, mocker, pr_response, tmp_path):
        """Recreates worktree when deleted."""
        # ... verify worktree is recreated from branch
```

- [ ] Complete `test_discovery.py`
- [ ] Complete `test_feedback.py`
- [ ] Complete `test_addresser.py`
- [ ] Complete `test_exceptions.py`

### 7.3 Add integration tests

```python
# tests/test_integration.py
import subprocess
import pytest

@pytest.mark.integration
class TestIntegration:
    def test_dry_run_against_real_pr(self):
        """Verify dry run works against real GitHub PR."""
        result = subprocess.run(
            ["python", "-m", "skill_pr_addresser", "address", "795", "--dry-run"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Discovered PR #795" in result.stdout

    def test_status_command(self):
        result = subprocess.run(
            ["python", "-m", "skill_pr_addresser", "status", "795"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
```

- [ ] Create `tests/test_integration.py`
- [ ] Mark with `@pytest.mark.integration`

### 7.4 Add edge case tests

```python
# tests/test_edge_cases.py
class TestEdgeCases:
    def test_rate_limit_handling(self):
        """Handles GitHub rate limiting gracefully."""

    def test_network_failure_recovery(self):
        """Recovers from network failures."""

    def test_concurrent_pr_updates(self):
        """Handles PR updated during addressing."""

    def test_large_diff_handling(self):
        """Handles PRs with many changed files."""

    def test_unicode_in_comments(self):
        """Handles unicode in review comments."""

    def test_empty_pr_body(self):
        """Handles PR with no body."""
```

- [ ] Create `tests/test_edge_cases.py`

### 7.5 Add test coverage

```ini
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "integration: marks tests as integration tests",
]

[tool.coverage.run]
source = ["src"]
omit = ["src/tui/*"]

[tool.coverage.report]
fail_under = 80
```

```just
# justfile
test *FLAGS:
    pytest tests/ {{FLAGS}}

test-cov:
    pytest tests/ --cov=src --cov-report=html

test-integration:
    pytest tests/ -m integration --dry-run
```

- [ ] Configure pytest in `pyproject.toml`
- [ ] Add coverage configuration
- [ ] Add justfile recipes

### 7.6 Update agent entry point

```markdown
<!-- .claude/agents/skill-pr-addresser.md -->
---
description: Address PR review feedback for skills, iterating until approved
tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# Skill PR Addresser

Addresses review feedback on skill PRs created by skill-reviewer.

## Usage

```bash
# Address feedback on a PR
just address-skill-reviews <pr_number>

# With TUI
just address-skill-reviews <pr_number> --tui

# Dry run
just address-skill-reviews <pr_number> --dry-run
```

## Workflow

1. **Discovery**: Finds PR, linked issue, existing session and worktree
2. **Analysis**: Extracts actionable feedback items
3. **Implementation**: Fixes each item (with model escalation)
4. **Commit**: Pushes changes, comments on PR
5. **Status**: Marks ready when all feedback addressed

## Configuration

See `config/skill-pr-addresser.conf`:

- `max_iterations`: Maximum iteration cycles (default: 3)
- `rate_limit_delay`: Delay between API calls (default: 1.0s)

## Integration

Works with skill-reviewer sessions:
- Reuses existing worktree and branch
- Links back to original issue
- Preserves context across iterations
```

- [ ] Update agent entry point documentation

### 7.7 Create README

```markdown
<!-- README.md -->
# skill-pr-addresser

Address PR review feedback for Claude Code skills.

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
just address-skill-reviews 795
```

## Development

```bash
pip install -e ".[dev]"
just test
```

## Architecture

See `.ai/plans/skill-pr-addresser/` for detailed design documentation.
```

- [ ] Create `README.md`

### 7.8 Final polish

- [ ] Run `ruff check .` and fix issues
- [ ] Run `ruff format .`
- [ ] Verify all imports are correct
- [ ] Test fresh install: `pip install -e .`
- [ ] Verify all justfile recipes work

## Checklist Gate

Before marking complete:

- [ ] All unit tests pass: `just test`
- [ ] Coverage ≥ 80%: `just test-cov`
- [ ] Integration tests pass: `just test-integration`
- [ ] No linting errors: `ruff check .`
- [ ] Fresh install works
- [ ] README is complete
- [ ] Agent entry point is documented

## Files Created/Modified

| File | Action |
|------|--------|
| `tests/conftest.py` | Create |
| `tests/fixtures/*.json` | Create |
| `tests/test_*.py` | Complete |
| `pyproject.toml` | Modify (test config) |
| `justfile` | Modify (test recipes) |
| `README.md` | Create |
| `.claude/agents/skill-pr-addresser.md` | Update |

## Estimated Effort

- Fixtures: ~1 hour
- Unit tests: ~3 hours
- Integration tests: ~1 hour
- Edge case tests: ~2 hours
- Documentation: ~1 hour
- Polish: ~1 hour
- **Total: ~9 hours**

---

## Total Project Estimate

| Stage | Hours |
|-------|-------|
| Stage 0: Prerequisites | 4 |
| Stage 1: Foundation | 1.5 |
| Stage 2: Discovery | 5 |
| Stage 3: Feedback Loop | 7 |
| Stage 4: Commit & Status | 6.5 |
| Stage 5: Observability | 5 |
| Stage 6: TUI | 7 |
| Stage 7: Testing | 9 |
| **Total** | **~45 hours** |
