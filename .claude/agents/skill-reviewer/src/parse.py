import argparse
import sys

from models import Stage


def parse_args():
    parser = argparse.ArgumentParser(
        description="Skill Reviewer Agent - Orchestrated skill review pipeline"
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--skill", help="Path to skill to review")
    mode_group.add_argument("--resume", help="Session ID to resume")
    mode_group.add_argument(
        "--batch", action="store_true", help="Batch mode - review all matching issues"
    )
    mode_group.add_argument(
        "--list-sessions", action="store_true", help="List all sessions"
    )

    # Options
    parser.add_argument("--issue", type=int, help="GitHub issue number to link")
    parser.add_argument(
        "--label",
        action="append",
        default=[],
        help="Labels to filter issues (batch mode)",
    )
    parser.add_argument("--stages", help="Comma-separated list of stages to run")
    parser.add_argument("--only", help="Run only a specific sub-agent (for testing)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Don't make actual changes"
    )
    parser.add_argument(
        "--max-parallel",
        type=int,
        default=3,
        help="Maximum parallel reviews (batch mode)",
    )
    parser.add_argument(
        "--cleanup", action="store_true", help="Clean up worktree after completion"
    )
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    return parser.parse_args()


def parse_stages(stages_str: str | None) -> list[Stage] | None:
    """Parse comma-separated stages string."""
    if not stages_str:
        return None

    stage_map = {
        "github_start": Stage.GITHUB_UPDATE_START,
        "validation": Stage.VALIDATION,
        "complexity": Stage.COMPLEXITY_ASSESSMENT,
        "analysis": Stage.ANALYSIS,
        "fixing": Stage.FIXING,
        "pr": Stage.PR_CREATION,
        "github_end": Stage.GITHUB_UPDATE_END,
    }

    stages = []
    for s in stages_str.split(","):
        s = s.strip().lower()
        if s in stage_map:
            stages.append(stage_map[s])
        else:
            print(f"Warning: Unknown stage '{s}'", file=sys.stderr)

    return stages if stages else None
