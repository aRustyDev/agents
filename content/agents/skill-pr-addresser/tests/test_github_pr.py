"""Tests for github_pr module."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add agent directory to path
_agent_dir = Path(__file__).parent.parent
if str(_agent_dir) not in sys.path:
    sys.path.insert(0, str(_agent_dir))

from src.github_pr import (
    PendingFeedback,
    ReviewThread,
    find_prs_with_feedback,
    get_pending_feedback,
    get_pr_details,
    get_pr_reviews,
    get_review_threads,
    infer_skill_from_files,
)

# --- Test Data ---


SAMPLE_PR_JSON = {
    "number": 795,
    "title": "feat(skills): add lang-rust-dev skill",
    "url": "https://github.com/aRustyDev/agents/pull/795",
    "state": "OPEN",
    "headRefName": "feat/lang-rust-dev",
    "body": "Closes #123",
    "isDraft": False,
    "mergeable": "MERGEABLE",
    "reviewDecision": "CHANGES_REQUESTED",
    "baseRefName": "main",
    "headRefOid": "abc123def456",
    "files": [
        {"path": "components/skills/lang-rust-dev/SKILL.md"},
        {"path": "components/skills/lang-rust-dev/examples/ownership.md"},
    ],
}


SAMPLE_REVIEWS_JSON = {
    "reviews": [
        {
            "author": {"login": "reviewer1"},
            "state": "CHANGES_REQUESTED",
            "body": "Please add more examples",
            "submittedAt": "2024-01-15T10:00:00Z",
        },
        {
            "author": {"login": "reviewer2"},
            "state": "APPROVED",
            "body": "LGTM",
            "submittedAt": "2024-01-15T11:00:00Z",
        },
    ]
}


SAMPLE_COMMENTS_JSON = {
    "comments": [
        {
            "author": {"login": "commenter1"},
            "body": "Great work!",
            "createdAt": "2024-01-15T09:00:00Z",
            "url": "https://github.com/aRustyDev/agents/pull/795#issuecomment-1",
        }
    ]
}


SAMPLE_THREADS_GRAPHQL = {
    "data": {
        "repository": {
            "pullRequest": {
                "reviewThreads": {
                    "nodes": [
                        {
                            "id": "thread_1",
                            "path": "components/skills/lang-rust-dev/SKILL.md",
                            "line": 42,
                            "isResolved": False,
                            "isOutdated": False,
                            "comments": {
                                "nodes": [
                                    {
                                        "author": {"login": "reviewer1"},
                                        "body": "Missing ownership section",
                                        "createdAt": "2024-01-15T10:05:00Z",
                                    }
                                ]
                            },
                        },
                        {
                            "id": "thread_2",
                            "path": "components/skills/lang-rust-dev/SKILL.md",
                            "line": 100,
                            "isResolved": True,
                            "isOutdated": False,
                            "comments": {
                                "nodes": [
                                    {
                                        "author": {"login": "reviewer1"},
                                        "body": "Fixed typo",
                                        "createdAt": "2024-01-15T10:10:00Z",
                                    }
                                ]
                            },
                        },
                    ]
                }
            }
        }
    }
}


# --- Tests ---


class TestGetPRDetails:
    """Tests for get_pr_details function."""

    def test_returns_pr_details_on_success(self):
        """Should return PRDetails when gh command succeeds."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(SAMPLE_PR_JSON)

        with patch("subprocess.run", return_value=mock_result):
            pr = get_pr_details("aRustyDev", "ai", 795)

        assert pr is not None
        assert pr.number == 795
        assert pr.title == "feat(skills): add lang-rust-dev skill"
        assert pr.state == "OPEN"
        assert pr.branch == "feat/lang-rust-dev"
        assert pr.review_decision == "CHANGES_REQUESTED"
        assert len(pr.changed_files) == 2

    def test_returns_none_on_failure(self):
        """Should return None when gh command fails."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        with patch("subprocess.run", return_value=mock_result):
            pr = get_pr_details("aRustyDev", "ai", 99999)

        assert pr is None


class TestGetPRReviews:
    """Tests for get_pr_reviews function."""

    def test_returns_reviews(self):
        """Should return list of Review objects."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(SAMPLE_REVIEWS_JSON)

        with patch("subprocess.run", return_value=mock_result):
            reviews = get_pr_reviews("aRustyDev", "ai", 795)

        assert len(reviews) == 2
        assert reviews[0].author == "reviewer1"
        assert reviews[0].state == "CHANGES_REQUESTED"
        assert reviews[1].author == "reviewer2"
        assert reviews[1].state == "APPROVED"

    def test_returns_empty_on_failure(self):
        """Should return empty list when gh command fails."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        with patch("subprocess.run", return_value=mock_result):
            reviews = get_pr_reviews("aRustyDev", "ai", 795)

        assert reviews == []


class TestGetReviewThreads:
    """Tests for get_review_threads function."""

    def test_returns_threads(self):
        """Should return list of ReviewThread objects."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(SAMPLE_THREADS_GRAPHQL)

        with patch("subprocess.run", return_value=mock_result):
            threads = get_review_threads("aRustyDev", "ai", 795)

        assert len(threads) == 2
        assert threads[0].id == "thread_1"
        assert threads[0].is_resolved is False
        assert threads[0].author == "reviewer1"
        assert threads[1].id == "thread_2"
        assert threads[1].is_resolved is True


class TestGetPendingFeedback:
    """Tests for get_pending_feedback function."""

    def test_filters_to_pending_only(self):
        """Should return PendingFeedback with categorized feedback."""
        mock_reviews_result = MagicMock()
        mock_reviews_result.returncode = 0
        mock_reviews_result.stdout = json.dumps(SAMPLE_REVIEWS_JSON)

        mock_comments_result = MagicMock()
        mock_comments_result.returncode = 0
        mock_comments_result.stdout = json.dumps(SAMPLE_COMMENTS_JSON)

        mock_threads_result = MagicMock()
        mock_threads_result.returncode = 0
        mock_threads_result.stdout = json.dumps(SAMPLE_THREADS_GRAPHQL)

        def side_effect(args, **kwargs):
            if "--json" in args:
                json_idx = args.index("--json")
                json_fields = args[json_idx + 1]
                if "reviews" in json_fields and "files" not in json_fields:
                    return mock_reviews_result
                elif "comments" in json_fields:
                    return mock_comments_result
            elif "graphql" in args:
                return mock_threads_result
            return mock_reviews_result

        with patch("subprocess.run", side_effect=side_effect):
            feedback = get_pending_feedback("aRustyDev", "ai", 795)

        # Should return a PendingFeedback object
        assert isinstance(feedback, PendingFeedback)

        # Only CHANGES_REQUESTED reviews in blocking
        assert len(feedback.blocking_reviews) == 1
        assert feedback.blocking_reviews[0].state == "CHANGES_REQUESTED"

        # Only unresolved, non-outdated threads
        assert len(feedback.unresolved_threads) == 1
        assert feedback.unresolved_threads[0].id == "thread_1"


class TestInferSkillFromFiles:
    """Tests for infer_skill_from_files function."""

    def test_infers_from_skill_path(self):
        """Should infer skill path from changed files."""
        files = [
            "components/skills/lang-rust-dev/SKILL.md",
            "components/skills/lang-rust-dev/examples/ownership.md",
        ]
        assert infer_skill_from_files(files) == "components/skills/lang-rust-dev"

    def test_returns_none_for_non_skill_files(self):
        """Should return None when no skill files changed."""
        files = [
            "README.md",
            ".github/workflows/ci.yml",
        ]
        assert infer_skill_from_files(files) is None

    def test_handles_mixed_files(self):
        """Should find skill even with mixed file types."""
        files = [
            "README.md",
            "components/skills/lang-rust-dev/SKILL.md",
            ".github/workflows/ci.yml",
        ]
        assert infer_skill_from_files(files) == "components/skills/lang-rust-dev"


class TestReviewThread:
    """Tests for ReviewThread dataclass."""

    def test_first_comment_property(self):
        """Should return first comment when available."""
        thread = ReviewThread(
            id="thread_1",
            path="test.md",
            line=10,
            is_resolved=False,
            is_outdated=False,
            comments=[{"author": {"login": "user1"}, "body": "Comment 1"}],
        )
        assert thread.first_comment is not None
        assert thread.first_comment["body"] == "Comment 1"

    def test_first_comment_none_when_empty(self):
        """Should return None when no comments."""
        thread = ReviewThread(
            id="thread_1",
            path="test.md",
            line=10,
            is_resolved=False,
            is_outdated=False,
            comments=[],
        )
        assert thread.first_comment is None

    def test_author_property(self):
        """Should extract author from first comment."""
        thread = ReviewThread(
            id="thread_1",
            path="test.md",
            line=10,
            is_resolved=False,
            is_outdated=False,
            comments=[{"author": {"login": "reviewer1"}, "body": "Comment"}],
        )
        assert thread.author == "reviewer1"


# --- Test Data for Batch ---


SAMPLE_PR_LIST_JSON = [
    {
        "number": 795,
        "title": "feat(skills): add lang-rust-dev skill",
        "reviewDecision": "CHANGES_REQUESTED",
        "reviewRequests": [],
        "reviews": [
            {"author": {"login": "reviewer1"}, "state": "CHANGES_REQUESTED"},
        ],
    },
    {
        "number": 800,
        "title": "feat(skills): add lang-go-dev skill",
        "reviewDecision": "APPROVED",
        "reviewRequests": [],
        "reviews": [
            {"author": {"login": "reviewer2"}, "state": "APPROVED"},
        ],
    },
    {
        "number": 805,
        "title": "fix(skills): update examples",
        "reviewDecision": "CHANGES_REQUESTED",
        "reviewRequests": [],
        "reviews": [
            {"author": {"login": "reviewer1"}, "state": "CHANGES_REQUESTED"},
            {"author": {"login": "reviewer2"}, "state": "CHANGES_REQUESTED"},
        ],
    },
]


class TestFindPRsWithFeedback:
    """Tests for find_prs_with_feedback function."""

    def test_finds_prs_needing_changes(self):
        """Should return PRs with CHANGES_REQUESTED reviews."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(SAMPLE_PR_LIST_JSON)

        with patch("subprocess.run", return_value=mock_result):
            prs = find_prs_with_feedback("aRustyDev", "ai")

        # Should only return PRs with blocking reviews
        assert len(prs) == 2
        assert prs[0]["pr_number"] == 795
        assert prs[1]["pr_number"] == 805

    def test_includes_blocking_reviewers(self):
        """Should include list of blocking reviewers."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(SAMPLE_PR_LIST_JSON)

        with patch("subprocess.run", return_value=mock_result):
            prs = find_prs_with_feedback("aRustyDev", "ai")

        # PR 805 has two blocking reviewers
        pr_805 = next(p for p in prs if p["pr_number"] == 805)
        assert len(pr_805["blocking_reviewers"]) == 2
        assert "reviewer1" in pr_805["blocking_reviewers"]
        assert "reviewer2" in pr_805["blocking_reviewers"]

    def test_returns_empty_on_failure(self):
        """Should return empty list when gh command fails."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        with patch("subprocess.run", return_value=mock_result):
            prs = find_prs_with_feedback("aRustyDev", "ai")

        assert prs == []

    def test_filters_by_labels(self):
        """Should pass labels to gh pr list command."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps([])

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            find_prs_with_feedback("aRustyDev", "ai", labels=["skills", "review"])

        # Check that --label flags were passed
        call_args = mock_run.call_args[0][0]
        assert "--label" in call_args
        assert "skills" in call_args
        assert "review" in call_args
