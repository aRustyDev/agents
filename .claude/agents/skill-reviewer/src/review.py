from concurrent.futures import ThreadPoolExecutor, as_completed

from github_ops import find_review_issues
from models import AgentSession, Stage
from orchestrator import Orchestrator
from session import generate_session_id


def batch_review(
    orchestrator: Orchestrator,
    labels: list[str],
    max_parallel: int,
    stages: list[Stage] | None = None,
    verbose: bool = False,
) -> list[AgentSession]:
    """Review multiple skills in parallel."""
    # Find matching issues
    issues = find_review_issues(
        orchestrator.config.repo_owner,
        orchestrator.config.repo_name,
        labels or orchestrator.config.review_labels,
    )

    if not issues:
        print("No matching issues found")
        return []

    if verbose:
        print(f"Found {len(issues)} issues to review")
        for issue in issues:
            print(f"  #{issue.number}: {issue.title}")

    results = []

    # Extract skill paths from issue bodies (assume format: "Skill: <path>")
    def extract_skill_path(body: str | None) -> str | None:
        if not body:
            return None
        for line in body.split("\n"):
            if line.lower().startswith("skill:"):
                return line.split(":", 1)[1].strip()
        return None

    # Run reviews in parallel with limited concurrency
    with ThreadPoolExecutor(max_workers=max_parallel) as executor:
        futures = {}

        for issue in issues:
            skill_path = extract_skill_path(issue.body)
            if not skill_path:
                print(
                    f"Warning: Could not extract skill path from issue #{issue.number}"
                )
                continue

            future = executor.submit(
                review_single_skill,
                orchestrator,
                skill_path,
                issue.number,
                stages,
                verbose,
            )
            futures[future] = issue

        for future in as_completed(futures):
            issue = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(f"Completed: #{issue.number} - {result.stage.value}")
            except Exception as e:
                print(f"Failed: #{issue.number} - {e}")

    return results


def review_single_skill(
    orchestrator: Orchestrator,
    skill_path: str,
    issue_number: int,
    stages: list[Stage] | None = None,
    verbose: bool = False,
) -> AgentSession:
    """Review a single skill."""
    session = AgentSession(
        session_id=generate_session_id(),
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
