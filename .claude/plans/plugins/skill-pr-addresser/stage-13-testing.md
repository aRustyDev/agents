# Stage 13: Pipeline Testing

> Comprehensive testing for filter, hooks, and pipeline integration.

## Objective

Ensure all pipeline refactor components work correctly through unit tests, integration tests, and end-to-end validation.

## Dependencies

- Stage 12 complete (Pipeline refactor implemented)

## Steps

### 13.1 Create test fixtures

```python
# tests/fixtures.py
"""Shared test fixtures for pipeline testing."""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

from src.models import (
    ReviewFeedback,
    CommentFeedback,
    ThreadFeedback,
    ThreadComment,
)
from src.pipeline import RawFeedback, PipelineContext


@pytest.fixture
def mock_app():
    """Create a mock Cement app."""
    app = MagicMock()
    app.log = MagicMock()
    app.hook.run.return_value = [None]
    app.config.get.return_value = '/tmp/sessions'
    return app


@pytest.fixture
def temp_sessions_dir():
    """Create a temporary sessions directory."""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_review():
    """Create a sample ReviewFeedback."""
    return ReviewFeedback(
        id="PRR_123",
        state="CHANGES_REQUESTED",
        body="Please fix the type errors on line 42",
        author="reviewer",
        submitted_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def sample_comment():
    """Create a sample CommentFeedback."""
    return CommentFeedback(
        id="IC_456",
        body="Consider adding tests for this feature",
        author="reviewer",
        created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def sample_thread():
    """Create a sample ThreadFeedback with comments."""
    return ThreadFeedback(
        id="PRRT_789",
        path="SKILL.md",
        line=42,
        is_resolved=False,
        is_outdated=False,
        comments=[
            ThreadComment(
                id="PRRTC_1",
                body="This code block should be in examples/",
                author="reviewer",
                created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            ),
            ThreadComment(
                id="PRRTC_2",
                body="Good point, I'll move it",
                author="pr_author",
                created_at=datetime(2025, 1, 1, 12, 30, 0, tzinfo=timezone.utc),
            ),
        ],
    )


@pytest.fixture
def sample_raw_feedback(sample_review, sample_comment, sample_thread):
    """Create sample RawFeedback."""
    return RawFeedback(
        reviews=[sample_review],
        comments=[sample_comment],
        threads=[sample_thread],
    )


@pytest.fixture
def mock_session():
    """Create a mock session."""
    session = MagicMock()
    session.results = {}
    return session


@pytest.fixture
def pipeline_context(mock_app, temp_sessions_dir, mock_session):
    """Create a PipelineContext for testing."""
    return PipelineContext(
        app=mock_app,
        pr_number=795,
        owner="owner",
        repo="repo",
        pr_author="pr_author",
        worktree_path=Path("/tmp/worktree"),
        agent_dir=Path("/tmp/agent"),
        sessions_dir=temp_sessions_dir,
        session=mock_session,
    )
```

- [ ] Create `tests/fixtures.py`
- [ ] Add mock_app fixture
- [ ] Add sample feedback fixtures
- [ ] Add pipeline_context fixture

### 13.2 Expand filter tests

```python
# tests/test_filter_comprehensive.py
"""Comprehensive filter stage tests."""

import pytest
from datetime import datetime

from src.filter import filter_feedback, FilteredFeedback, _is_new_or_changed
from src.session_schema import FeedbackState, AddressedItem, ThreadState
from src.models import ReviewFeedback, CommentFeedback, ThreadFeedback, ThreadComment
from src.pipeline import RawFeedback


class TestContentHashDelta:
    """Tests for content hash delta detection (Issue #796)."""

    def test_new_item_included(self, sample_review, mock_session):
        """New items (not in state) are included."""
        raw = RawFeedback(reviews=[sample_review])
        result = filter_feedback(raw, mock_session, "pr_author")

        assert len(result.reviews) == 1
        assert result.reviews[0].id == sample_review.id

    def test_unchanged_item_skipped(self, sample_review, mock_session):
        """Items with matching hash are skipped."""
        from datetime import timezone

        raw = RawFeedback(reviews=[sample_review])

        # Mark as addressed with same hash
        mock_session.results["feedback_state"] = {
            "addressed": {
                sample_review.id: {
                    "id": sample_review.id,
                    "content_hash": sample_review.content_hash,
                    "addressed_at": datetime.now(timezone.utc).isoformat(),
                    "addressed_in_commit": "abc123",
                    "iteration": 1,
                }
            }
        }

        result = filter_feedback(raw, mock_session, "pr_author")

        assert len(result.reviews) == 0
        assert sample_review.id in result.skipped_unchanged

    def test_updated_item_included(self, mock_session):
        """Items with changed content are included."""
        from datetime import timezone

        review = ReviewFeedback(
            id="PRR_123",
            state="CHANGES_REQUESTED",
            body="UPDATED: Please fix the type errors",
            author="reviewer",
            submitted_at=datetime.now(timezone.utc),
        )
        raw = RawFeedback(reviews=[review])

        # Mark as addressed with OLD hash
        mock_session.results["feedback_state"] = {
            "addressed": {
                "PRR_123": {
                    "id": "PRR_123",
                    "content_hash": "sha256:oldhashvalue",
                    "addressed_at": datetime.now(timezone.utc).isoformat(),
                    "addressed_in_commit": "abc123",
                    "iteration": 1,
                }
            }
        }

        result = filter_feedback(raw, mock_session, "pr_author")

        assert len(result.reviews) == 1
        assert result.reviews[0].id == "PRR_123"


class TestThreadDelta:
    """Tests for thread comment delta detection."""

    def test_all_comments_new_first_time(self, sample_thread, mock_session):
        """All comments included on first run."""
        raw = RawFeedback(threads=[sample_thread])
        result = filter_feedback(raw, mock_session, "pr_author")

        assert len(result.threads) == 1
        assert len(result.threads[0].new_comments) == 2

    def test_only_new_comments_included(self, sample_thread, mock_session):
        """Only unprocessed comments included on subsequent runs."""
        from datetime import timezone

        # Add a third comment
        sample_thread.comments.append(
            ThreadComment(
                id="PRRTC_3",
                body="New comment",
                author="someone",
                created_at=datetime.now(timezone.utc),
            )
        )
        raw = RawFeedback(threads=[sample_thread])

        # Mark first two comments as processed
        mock_session.results["feedback_state"] = {
            "threads": {
                sample_thread.id: {
                    "thread_id": sample_thread.id,
                    "comments_processed": ["PRRTC_1", "PRRTC_2"],
                    "last_processed_at": datetime.now(timezone.utc).isoformat(),
                }
            }
        }

        result = filter_feedback(raw, mock_session, "pr_author")

        assert len(result.threads) == 1
        assert len(result.threads[0].new_comments) == 1
        assert result.threads[0].new_comments[0].id == "PRRTC_3"

    def test_resolved_thread_skipped(self, mock_session):
        """Resolved threads are skipped."""
        thread = ThreadFeedback(
            id="PRRT_999",
            path="SKILL.md",
            line=100,
            is_resolved=True,
            is_outdated=False,
            comments=[],
        )
        raw = RawFeedback(threads=[thread])

        result = filter_feedback(raw, mock_session, "pr_author")

        assert len(result.threads) == 0
        assert thread.id in result.skipped_resolved

    def test_outdated_thread_skipped(self, mock_session):
        """Outdated threads are skipped."""
        thread = ThreadFeedback(
            id="PRRT_999",
            path="SKILL.md",
            line=100,
            is_resolved=False,
            is_outdated=True,
            comments=[],
        )
        raw = RawFeedback(threads=[thread])

        result = filter_feedback(raw, mock_session, "pr_author")

        assert len(result.threads) == 0
        assert thread.id in result.skipped_outdated


class TestAuthorResolution:
    """Tests for author resolution signal detection."""

    def test_author_resolution_detected(self, mock_session):
        """Thread with author 'done' signal flagged."""
        from datetime import timezone

        thread = ThreadFeedback(
            id="PRRT_123",
            path="SKILL.md",
            line=42,
            is_resolved=False,
            is_outdated=False,
            comments=[
                ThreadComment(
                    id="c1",
                    body="Fix this",
                    author="reviewer",
                    created_at=datetime.now(timezone.utc),
                ),
                ThreadComment(
                    id="c2",
                    body="Done!",
                    author="pr_author",
                    created_at=datetime.now(timezone.utc),
                ),
            ],
        )
        raw = RawFeedback(threads=[thread])

        result = filter_feedback(raw, mock_session, "pr_author")

        assert len(result.threads) == 1
        assert result.threads[0].has_author_response is True


class TestReviewerWithdrawal:
    """Tests for reviewer withdrawal detection."""

    def test_reviewer_withdrawal_skips_thread(self, mock_session):
        """Thread with reviewer 'never mind' is skipped."""
        from datetime import timezone

        thread = ThreadFeedback(
            id="PRRT_123",
            path="SKILL.md",
            line=42,
            is_resolved=False,
            is_outdated=False,
            comments=[
                ThreadComment(
                    id="c1",
                    body="Fix this",
                    author="reviewer",
                    created_at=datetime.now(timezone.utc),
                ),
                ThreadComment(
                    id="c2",
                    body="Actually, never mind",
                    author="reviewer",
                    created_at=datetime.now(timezone.utc),
                ),
            ],
        )
        raw = RawFeedback(threads=[thread])

        result = filter_feedback(raw, mock_session, "pr_author")

        assert len(result.threads) == 0
        assert thread.id in result.skipped_resolved
```

- [ ] Create `tests/test_filter_comprehensive.py`
- [ ] Test content hash delta detection
- [ ] Test thread comment delta detection
- [ ] Test author resolution detection
- [ ] Test reviewer withdrawal detection

### 13.3 Add cross-reference tests

```python
# tests/test_cross_reference_comprehensive.py
"""Comprehensive cross-reference tests."""

import pytest

from src.cross_reference import (
    extract_line_references,
    extract_file_references,
    link_reviews_to_threads,
    mark_linked_threads,
)
from src.models import ReviewFeedback, ThreadFeedback, ThreadComment
from src.filter import FilteredFeedback, FilteredThread


class TestExtractLineReferences:
    """Tests for line reference extraction."""

    @pytest.mark.parametrize("text,expected", [
        ("see line 42", [42]),
        ("at L42", [42]),
        ("lines 10-20", [10, 20]),
        ("SKILL.md#L42", [42]),
        ("line 1, line 2, line 3", [1, 2, 3]),
        ("LINE 42", [42]),  # Case insensitive
        ("no references here", []),
    ])
    def test_extraction_patterns(self, text, expected):
        result = extract_line_references(text)
        assert result == expected


class TestExtractFileReferences:
    """Tests for file reference extraction."""

    @pytest.mark.parametrize("text,expected", [
        ("in SKILL.md", ["SKILL.md"]),
        ("see examples/foo.py", ["examples/foo.py"]),
        ("check `src/app.py`", ["src/app.py"]),
        ("in SKILL.md and examples/bar.py", ["SKILL.md", "examples/bar.py"]),
        ("no file references", []),
    ])
    def test_extraction_patterns(self, text, expected):
        result = extract_file_references(text)
        assert result == expected


class TestLinkReviewsToThreads:
    """Tests for review-to-thread linking."""

    def test_links_review_to_thread_by_line(self):
        """Review mentioning line is linked to thread at that line."""
        from datetime import timezone

        reviews = [
            ReviewFeedback(
                id="R_1",
                state="COMMENTED",
                body="The issue at line 42 needs fixing",
                author="reviewer",
                submitted_at=datetime.now(timezone.utc),
            )
        ]
        threads = [
            ThreadFeedback(
                id="T_1",
                path="SKILL.md",
                line=42,
                is_resolved=False,
                is_outdated=False,
                comments=[],
            ),
            ThreadFeedback(
                id="T_2",
                path="SKILL.md",
                line=100,
                is_resolved=False,
                is_outdated=False,
                comments=[],
            ),
        ]

        links = link_reviews_to_threads(reviews, threads)

        assert links == {"R_1": ["T_1"]}
        assert reviews[0].references_lines == [42]

    def test_multiple_threads_linked(self):
        """Review mentioning multiple lines links to multiple threads."""
        from datetime import timezone

        reviews = [
            ReviewFeedback(
                id="R_1",
                state="COMMENTED",
                body="See issues at lines 42-50",
                author="reviewer",
                submitted_at=datetime.now(timezone.utc),
            )
        ]
        threads = [
            ThreadFeedback(
                id="T_1",
                path="SKILL.md",
                line=42,
                is_resolved=False,
                is_outdated=False,
                comments=[],
            ),
            ThreadFeedback(
                id="T_2",
                path="SKILL.md",
                line=50,
                is_resolved=False,
                is_outdated=False,
                comments=[],
            ),
            ThreadFeedback(
                id="T_3",
                path="SKILL.md",
                line=100,
                is_resolved=False,
                is_outdated=False,
                comments=[],
            ),
        ]

        links = link_reviews_to_threads(reviews, threads)

        assert "R_1" in links
        assert set(links["R_1"]) == {"T_1", "T_2"}

    def test_no_links_when_no_matching_lines(self):
        """No links when review lines don't match threads."""
        from datetime import timezone

        reviews = [
            ReviewFeedback(
                id="R_1",
                state="COMMENTED",
                body="Check line 999",
                author="reviewer",
                submitted_at=datetime.now(timezone.utc),
            )
        ]
        threads = [
            ThreadFeedback(
                id="T_1",
                path="SKILL.md",
                line=42,
                is_resolved=False,
                is_outdated=False,
                comments=[],
            ),
        ]

        links = link_reviews_to_threads(reviews, threads)

        assert links == {}


class TestMarkLinkedThreads:
    """Tests for marking linked threads."""

    def test_threads_marked_with_review_id(self):
        """Linked threads get marked with their parent review ID."""
        from datetime import timezone

        filtered = FilteredFeedback(
            reviews=[
                ReviewFeedback(
                    id="R_1",
                    state="COMMENTED",
                    body="See line 42",
                    author="reviewer",
                    submitted_at=datetime.now(timezone.utc),
                ),
            ],
            comments=[],
            threads=[
                FilteredThread(
                    thread=ThreadFeedback(
                        id="T_1",
                        path="SKILL.md",
                        line=42,
                        is_resolved=False,
                        is_outdated=False,
                        comments=[],
                    ),
                    new_comments=[],
                ),
                FilteredThread(
                    thread=ThreadFeedback(
                        id="T_2",
                        path="SKILL.md",
                        line=100,
                        is_resolved=False,
                        is_outdated=False,
                        comments=[],
                    ),
                    new_comments=[],
                ),
            ],
        )
        links = {"R_1": ["T_1"]}

        mark_linked_threads(filtered, links)

        assert filtered.threads[0].thread.linked_to_review == "R_1"
        assert filtered.threads[1].thread.linked_to_review is None
```

- [ ] Create `tests/test_cross_reference_comprehensive.py`
- [ ] Test line reference patterns with parametrize
- [ ] Test file reference patterns
- [ ] Test review-to-thread linking
- [ ] Test thread marking

### 13.4 Add hook integration tests

```python
# tests/test_hooks_integration.py
"""Integration tests for hook execution."""

import pytest
from unittest.mock import MagicMock, call, patch

from src.stages import run_stage, StageResult
from src.pipeline import Pipeline, PipelineContext


class TestHookExecutionOrder:
    """Tests for hook execution order."""

    def test_pre_post_hooks_fire_in_order(self, mock_app, pipeline_context):
        """Pre-hook fires before stage, post-hook after."""
        execution_order = []

        def pre_hook(ctx):
            execution_order.append("pre")

        def post_hook(ctx, result):
            execution_order.append("post")

        mock_app.hook.run.side_effect = [
            [pre_hook(None)],  # pre_test
            [post_hook(None, None)],  # post_test
        ]

        def stage_fn(ctx):
            execution_order.append("stage")
            return StageResult.success("test")

        run_stage(mock_app, "test", stage_fn, pipeline_context)

        assert execution_order == ["pre", "stage", "post"]

    def test_error_hook_fires_on_exception(self, mock_app, pipeline_context):
        """Error hook fires when stage raises."""
        mock_app.hook.run.side_effect = [
            [None],  # pre_test
            [None],  # on_stage_error
        ]

        def failing_stage(ctx):
            raise ValueError("stage error")

        result = run_stage(mock_app, "test", failing_stage, pipeline_context)

        assert result.status.value == "failed"
        # Check on_stage_error was called
        calls = [c[0][0] for c in mock_app.hook.run.call_args_list]
        assert "on_stage_error" in calls


class TestHookEarlyExit:
    """Tests for hook-triggered early exit."""

    def test_pre_hook_false_skips_stage(self, mock_app, pipeline_context):
        """Pre-hook returning False skips stage execution."""
        mock_app.hook.run.return_value = [False]

        stage_called = False

        def stage_fn(ctx):
            nonlocal stage_called
            stage_called = True
            return StageResult.success("test")

        result = run_stage(mock_app, "test", stage_fn, pipeline_context)

        assert not stage_called
        assert result.status.value == "skipped"


class TestStatePersistenceHooks:
    """Tests for state persistence via hooks."""

    def test_state_persisted_after_commit(self, mock_app, pipeline_context):
        """Feedback state saved after post_commit hook."""
        from src.hooks import persist_feedback_state
        from src.session_schema import FeedbackState

        pipeline_context.feedback_state = FeedbackState()
        pipeline_context.feedback_state.mark_addressed(
            "R_1", "sha256:abc", "def456", 1
        )

        result = StageResult.success("commit")

        persist_feedback_state(mock_app, pipeline_context, result)

        # Check state was set in session
        assert "feedback_state" in pipeline_context.session.results
        assert "R_1" in pipeline_context.session.results["feedback_state"]["addressed"]

        # Check session was saved
        pipeline_context.session.save.assert_called_once()
```

- [ ] Create `tests/test_hooks_integration.py`
- [ ] Test hook execution order
- [ ] Test error hook fires on exception
- [ ] Test pre-hook can skip stage
- [ ] Test state persistence

### 13.5 Add pipeline integration tests

```python
# tests/test_pipeline_integration.py
"""Integration tests for full pipeline execution."""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from tempfile import TemporaryDirectory

from src.pipeline import Pipeline, PipelineContext, RawFeedback
from src.stages import StageResult
from src.models import ReviewFeedback, ThreadFeedback, ThreadComment


class TestPipelineExecution:
    """Tests for full pipeline execution."""

    def test_full_pipeline_dry_run(self, mock_app):
        """Dry run executes discovery→filter→consolidate→plan."""
        pipeline = Pipeline(mock_app)

        with patch.object(pipeline, '_create_context') as mock_ctx:
            with patch.object(pipeline, '_load_or_create_session') as mock_sess:
                with patch.object(pipeline, '_load_progress') as mock_prog:
                    with patch('src.pipeline.session_lock'):
                        # Setup mocks
                        ctx = MagicMock()
                        ctx.dry_run = True
                        ctx.stop_after = 'plan'
                        ctx.should_stop_after = lambda s: s == 'plan'
                        mock_ctx.return_value = ctx
                        mock_sess.return_value = MagicMock(results={})
                        mock_prog.return_value = MagicMock()

                        # Mock stage results
                        pipeline._stage_discovery = MagicMock(
                            return_value=StageResult.success('discovery')
                        )
                        pipeline._stage_filter = MagicMock(
                            return_value=StageResult.success('filter')
                        )
                        pipeline._stage_consolidate = MagicMock(
                            return_value=StageResult.success('consolidate')
                        )
                        pipeline._stage_plan = MagicMock(
                            return_value=StageResult.success('plan')
                        )
                        pipeline._stage_fix = MagicMock()

                        result = pipeline.execute(795, dry_run=True, stop_after='plan')

                        # Verify stages called
                        pipeline._stage_discovery.assert_called_once()
                        pipeline._stage_filter.assert_called_once()
                        pipeline._stage_consolidate.assert_called_once()
                        pipeline._stage_plan.assert_called_once()

                        # Fix should NOT be called (stopped at plan)
                        pipeline._stage_fix.assert_not_called()

    def test_pipeline_stops_on_no_feedback(self, mock_app):
        """Pipeline stops when filter finds nothing new."""
        pipeline = Pipeline(mock_app)

        # ... setup mocks

        pipeline._stage_discovery = MagicMock(
            return_value=StageResult.success('discovery')
        )
        pipeline._stage_filter = MagicMock(
            return_value=StageResult.early_exit('filter', 'no_new_feedback')
        )
        pipeline._stage_consolidate = MagicMock()

        # Execute
        # ...

        # Consolidate should not be called
        pipeline._stage_consolidate.assert_not_called()

    def test_pipeline_respects_session_lock(self, mock_app):
        """Pipeline acquires session lock before execution."""
        with TemporaryDirectory() as tmpdir:
            mock_app.config.get.return_value = tmpdir

            with patch('src.pipeline.session_lock') as mock_lock:
                mock_lock.return_value.__enter__ = MagicMock()
                mock_lock.return_value.__exit__ = MagicMock()

                pipeline = Pipeline(mock_app)
                # ... minimal setup to trigger execute

                mock_lock.assert_called_once()


class TestIterationLoop:
    """Tests for addresser iteration loop."""

    def test_max_iterations_respected(self, mock_app):
        """Addresser stops after max iterations."""
        from src.addresser import Addresser

        addresser = Addresser(mock_app)
        addresser.max_iterations = 2

        with patch.object(addresser, '_run_single_iteration') as mock_iter:
            # Each iteration returns "needs more work"
            mock_iter.return_value = MagicMock(
                filtered_feedback=MagicMock(is_empty=False),
                consolidated=MagicMock(action_groups=[{}]),
            )

            result = addresser.address(795)

            assert mock_iter.call_count == 2
            assert 'iterations' in result
            assert result['iterations'] == 2

    def test_stops_when_no_more_feedback(self, mock_app):
        """Addresser stops when filter returns empty."""
        from src.addresser import Addresser

        addresser = Addresser(mock_app)

        with patch.object(addresser, '_run_single_iteration') as mock_iter:
            # First iteration: has work
            # Second iteration: no more work
            mock_iter.side_effect = [
                MagicMock(
                    filtered_feedback=MagicMock(is_empty=False),
                    consolidated=MagicMock(action_groups=[{}]),
                ),
                MagicMock(
                    filtered_feedback=MagicMock(is_empty=True),
                ),
            ]

            result = addresser.address(795)

            assert mock_iter.call_count == 2
            assert result['iterations'] == 2
```

- [ ] Create `tests/test_pipeline_integration.py`
- [ ] Test dry-run execution path
- [ ] Test early exit on no feedback
- [ ] Test session lock acquisition
- [ ] Test iteration loop limits

### 13.6 Add end-to-end tests

```python
# tests/test_e2e.py
"""End-to-end tests with mocked GitHub API."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from tempfile import TemporaryDirectory

from src.app import SkillPRAddresser


@pytest.fixture
def app_instance():
    """Create a test app instance."""
    with TemporaryDirectory() as tmpdir:
        app = SkillPRAddresser(
            config_files=[],  # No external config
            config_defaults={
                'skill-pr-addresser': {
                    'sessions_dir': tmpdir,
                    'max_iterations': 2,
                }
            }
        )
        with app:
            yield app


class TestE2EDryRun:
    """End-to-end dry run tests."""

    @patch('src.discovery.fetch_reviews')
    @patch('src.discovery.fetch_comments')
    @patch('src.discovery.fetch_threads')
    @patch('src.discovery.discover_pr_info')
    def test_dry_run_shows_summary(
        self,
        mock_pr_info,
        mock_threads,
        mock_comments,
        mock_reviews,
        app_instance,
    ):
        """Dry run outputs summary without making changes."""
        # Setup mocks
        mock_pr_info.return_value = MagicMock(
            owner='owner',
            repo='repo',
            author='pr_author',
            worktree_path=Path('/tmp/wt'),
        )
        mock_reviews.return_value = [
            {
                'id': 'R_1',
                'state': 'CHANGES_REQUESTED',
                'body': 'Fix this type error',
                'author': {'login': 'reviewer'},
                'submittedAt': '2025-01-01T12:00:00Z',
            }
        ]
        mock_comments.return_value = []
        mock_threads.return_value = [
            {
                'id': 'T_1',
                'path': 'SKILL.md',
                'line': 42,
                'isResolved': False,
                'isOutdated': False,
                'comments': {'nodes': []},
            }
        ]

        # Run dry-run
        app_instance.run(['address', '795', '--dry-run'])

        # Verify no git commits were made
        # In dry-run mode, the pipeline stops before fix/commit stages
        # No assertions needed beyond successful execution


class TestE2EFullRun:
    """End-to-end full execution tests."""

    @patch('src.github_pr.resolve_thread')
    @patch('src.commit.commit_and_push')
    @patch('src.fix.run_fixer_for_locations')
    @patch('src.consolidate.consolidate_feedback')
    @patch('src.discovery.fetch_reviews')
    @patch('src.discovery.fetch_comments')
    @patch('src.discovery.fetch_threads')
    @patch('src.discovery.discover_pr_info')
    def test_full_run_commits_and_resolves(
        self,
        mock_pr_info,
        mock_threads,
        mock_comments,
        mock_reviews,
        mock_consolidate,
        mock_fixer,
        mock_commit,
        mock_resolve,
        app_instance,
    ):
        """Full run commits changes and resolves threads."""
        # Setup mocks
        mock_pr_info.return_value = MagicMock(
            owner='owner',
            repo='repo',
            author='pr_author',
            branch='feat/test',
            worktree_path=Path('/tmp/wt'),
        )
        mock_reviews.return_value = [
            {
                'id': 'R_1',
                'state': 'CHANGES_REQUESTED',
                'body': 'Fix this type error',
                'author': {'login': 'reviewer'},
                'submittedAt': '2025-01-01T12:00:00Z',
            }
        ]
        mock_comments.return_value = []
        mock_threads.return_value = [
            {
                'id': 'T_1',
                'path': 'SKILL.md',
                'line': 42,
                'isResolved': False,
                'isOutdated': False,
                'comments': {'nodes': [
                    {
                        'id': 'TC_1',
                        'body': 'Fix this type annotation',
                        'author': {'login': 'reviewer'},
                        'createdAt': '2025-01-01T12:00:00Z',
                    }
                ]},
            }
        ]
        mock_consolidate.return_value = MagicMock(
            action_groups=[{
                'id': 'g1',
                'type': 'fix',
                'description': 'Fix type annotation',
                'locations': [{'file': 'SKILL.md', 'line': 42}],
                'priority': 'high',
            }],
            guidance=[],
            token_usage=MagicMock(input_tokens=100, output_tokens=50),
            thread_links={},
        )
        mock_fixer.return_value = MagicMock(
            has_changes=True,
            addressed_thread_ids=['T_1'],
        )
        mock_commit.return_value = 'abc123'
        mock_resolve.return_value = True

        # Run
        app_instance.run(['address', '795'])

        # Verify commit was made
        mock_commit.assert_called_once()

        # Verify thread was resolved
        mock_resolve.assert_called_with('owner', 'repo', 'T_1')
```

- [ ] Create `tests/test_e2e.py`
- [ ] Test dry-run end-to-end
- [ ] Test full run with mocked GitHub
- [ ] Test iteration loop end-to-end

### 13.7 Run all tests and verify coverage

```bash
# Run all tests
pytest tests/ -v --cov=src --cov-report=html

# Check specific test files
pytest tests/test_filter_comprehensive.py -v
pytest tests/test_hooks_integration.py -v
pytest tests/test_pipeline_integration.py -v

# Generate coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

- [ ] Run full test suite
- [ ] Verify >80% code coverage
- [ ] Fix any failing tests
- [ ] Document test coverage gaps

## Checklist Gate

All pipeline refactor tests pass:

- [ ] Filter tests: delta detection, thread comments, resolution signals
- [ ] Cross-reference tests: line patterns, file patterns, linking
- [ ] Hook tests: execution order, early exit, error handling
- [ ] Pipeline tests: stage execution, early exit, iteration
- [ ] E2E tests: dry-run, full execution
- [ ] Coverage >80% for new code
- [ ] No regressions in existing tests

## Files Created

| File | Purpose |
|------|---------|
| `tests/fixtures.py` | Shared test fixtures |
| `tests/test_filter_comprehensive.py` | Filter stage tests |
| `tests/test_cross_reference_comprehensive.py` | Cross-reference tests |
| `tests/test_hooks_integration.py` | Hook integration tests |
| `tests/test_pipeline_integration.py` | Pipeline integration tests |
| `tests/test_e2e.py` | End-to-end tests |

## Estimated Effort

- Test fixtures: ~30 minutes
- Filter tests: ~45 minutes
- Cross-reference tests: ~30 minutes
- Hook tests: ~30 minutes
- Pipeline tests: ~45 minutes
- E2E tests: ~30 minutes
- Coverage verification: ~30 minutes
- **Total: ~4 hours**

## Acceptance Criteria Summary

After completing all pipeline refactor stages (8-13):

### Issue #796 (Updated Comment Detection)
- [x] Store content hash when marking feedback as addressed
- [x] Compare hash when filtering already-addressed feedback
- [x] Re-process comments whose content has changed
- [x] Tests verify updated comment detection

### Thread Comment Tracking
- [x] Track which thread comments have been processed
- [x] Only process new comments in threads
- [x] Detect author responses that signal resolution
- [x] Detect reviewer withdrawals
- [x] Skip threads with resolution signals

### Session Locking
- [x] Acquire file-based lock before processing
- [x] Prevent concurrent runs on same PR
- [x] Display helpful error when lock held
- [x] Release lock on completion or error

### Thread Resolution
- [x] Call GitHub GraphQL to resolve threads after addressing
- [x] Track which threads were resolved in session
- [x] Handle resolution failures gracefully

### Dry-Run Mode
- [x] `--dry-run` flag runs discovery→filter→consolidate→plan only
- [x] `--stop-after` flag allows stopping at any stage
- [x] Dry-run output shows what would be addressed

### Partial Addressing
- [x] Track progress at location level
- [x] Resume from partial progress on re-run
- [x] Skip already-complete action groups

### Cross-Reference Detection
- [x] Detect line references in review body
- [x] Link reviews to threads at referenced lines
- [x] Mark linked threads to avoid double-processing

### Hook Integration
- [x] Define all pipeline hooks
- [x] Hooks fire at correct points
- [x] Error hooks fire on stage failure
- [x] State persists correctly via hooks

### Pipeline Separation
- [x] Discovery stage is pure GitHub API calls
- [x] Filter stage is deterministic (no LLM)
- [x] Consolidation stage is LLM-powered
- [x] Fix stage executes in batches
- [x] Commit stage handles git operations + thread resolution
