"""Review functions for skill reviewer agent."""

from concurrent.futures import ThreadPoolExecutor, as_completed

from .github_projects import get_project_id, find_backlog_issues
from .models import AgentSession, Stage
from .orchestrator import Orchestrator
from .session import generate_session_id
from .progress import ProgressTracker


def batch_review(
    orchestrator: Orchestrator,
    labels: list[str] | None,
    assignee: str | None,
    max_parallel: int,
    stages: list[Stage] | None = None,
    verbose: bool = False,
) -> list[AgentSession]:
    """Review multiple skills in parallel.

    Args:
        orchestrator: The orchestrator instance
        labels: Labels to filter by (uses config.review_labels if None)
        assignee: Assignee to filter by (None = any assignee)
        max_parallel: Maximum parallel reviews
        stages: Optional subset of stages to run
        verbose: Print verbose output

    Returns:
        List of completed AgentSession objects
    """
    config = orchestrator.config

    # Get project ID for filtering by project status
    project_id = get_project_id(config.repo_owner, config.project_number)
    if not project_id:
        print(f"Error: Could not find project {config.project_number}")
        return []

    # Find matching issues from project backlog
    issues = find_backlog_issues(
        project_id=project_id,
        owner=config.repo_owner,
        repo=config.repo_name,
        status_name=config.backlog_status,
        assignee=assignee,
        labels=labels or config.review_labels,
    )

    if not issues:
        print("No matching backlog issues found")
        return []

    if verbose:
        print(f"Found {len(issues)} issues to review")
        for issue in issues:
            print(f"  #{issue.issue_number}: {issue.title}")

    # Initialize progress tracker
    progress_file = orchestrator.data_dir / "progress.json"
    tracker = ProgressTracker(progress_file)
    tracker.start_batch(
        batch_id=generate_session_id(),
        total_issues=len(issues)
    )

    results = []

    # Extract skill paths from issue titles (assume format: "[skill-name] description")
    def extract_skill_path(title: str) -> str | None:
        """Extract skill path from issue title.

        Expects format like: "[lang-rust-dev] Missing Module System section"
        """
        if title.startswith("[") and "]" in title:
            skill_name = title[1:title.index("]")]
            return f"components/skills/{skill_name}"
        return None

    # Run reviews with limited concurrency
    with ThreadPoolExecutor(max_workers=max_parallel) as executor:
        futures = {}

        for issue in issues:
            skill_path = extract_skill_path(issue.title)
            if not skill_path:
                print(
                    f"Warning: Could not extract skill path from issue #{issue.issue_number}: {issue.title}"
                )
                continue

            # Track session start
            session_id = generate_session_id()
            tracker.start_session(session_id, issue.issue_number, skill_path)

            future = executor.submit(
                _review_with_tracking,
                orchestrator,
                skill_path,
                issue.issue_number,
                session_id,
                tracker,
                stages,
                verbose,
            )
            futures[future] = issue

        for future in as_completed(futures):
            issue = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(f"Completed: #{issue.issue_number} - {result.stage.value}")
            except Exception as e:
                print(f"Failed: #{issue.issue_number} - {e}")

    tracker.complete_batch()
    return results


def _review_with_tracking(
    orchestrator: Orchestrator,
    skill_path: str,
    issue_number: int,
    session_id: str,
    tracker: ProgressTracker,
    stages: list[Stage] | None,
    verbose: bool,
) -> AgentSession:
    """Review a skill with progress tracking."""
    try:
        result = review_single_skill(
            orchestrator,
            skill_path,
            issue_number,
            stages,
            verbose,
            session_id=session_id,
        )

        # Update tracker
        tracker.update_session(
            session_id,
            stage=result.stage.value,
            status="completed" if result.stage == Stage.COMPLETE else "failed",
            pr_url=getattr(result, "pr_url", None),
            error=result.errors[-1] if result.errors else None,
            cost=result.estimated_cost_usd,
        )

        return result

    except Exception as e:
        tracker.update_session(
            session_id,
            stage="failed",
            status="failed",
            error=str(e),
        )
        raise


def review_single_skill(
    orchestrator: Orchestrator,
    skill_path: str,
    issue_number: int,
    stages: list[Stage] | None = None,
    verbose: bool = False,
    session_id: str | None = None,
) -> AgentSession:
    """Review a single skill.

    Args:
        orchestrator: The orchestrator instance
        skill_path: Path to the skill to review
        issue_number: GitHub issue number to link
        stages: Optional subset of stages to run
        verbose: Print verbose output
        session_id: Optional session ID (generated if not provided)

    Returns:
        AgentSession with results
    """
    session = AgentSession(
        session_id=session_id or generate_session_id(),
        skill_path=skill_path,
        issue_number=issue_number,
        repo_owner=orchestrator.config.repo_owner,
        repo_name=orchestrator.config.repo_name,
    )

    if verbose:
        print(f"Starting session {session.session_id}")
        print(f"  Skill: {skill_path}")
        print(f"  Issue: #{issue_number}")

    result = orchestrator.run_pipeline(session, stages)

    if verbose:
        print(f"\nSession {session.session_id} complete")
        print(f"  Stage: {result.stage.value}")
        print(
            f"  Tokens: {result.total_input_tokens} in / {result.total_output_tokens} out"
        )
        print(f"  Est. Cost: ${result.estimated_cost_usd:.4f}")
        if result.errors:
            print(f"  Errors: {len(result.errors)}")
            for err in result.errors:
                print(f"    - {err}")

    return result
