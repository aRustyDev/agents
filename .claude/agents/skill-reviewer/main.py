#!/usr/bin/env python3
"""
Skill Reviewer Agent - Main Entry Point

Orchestrates the review of Claude Code skills using specialized sub-agents.

Usage:
    # Review a single skill
    python main.py --skill components/skills/lang-rust-dev --issue 123

    # Resume an interrupted session
    python main.py --resume abc123

    # Dry run (no GitHub changes)
    python main.py --skill components/skills/lang-rust-dev --issue 123 --dry-run

    # Batch review from GitHub issues
    python main.py --batch --label review --label skills

    # Run specific stages only
    python main.py --skill components/skills/lang-rust-dev --issue 123 \
        --stages validation,analysis
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import load_config
from src.models import Stage
from src.orchestrator import Orchestrator
from src.parse import parse_args, parse_stages
from src.review import batch_review, review_single_skill
from src.session import list_sessions, resume_session


def main():
    args = parse_args()

    # Load config
    agent_dir = Path(__file__).parent
    config_path = (
        Path(args.config) if args.config else agent_dir / "data" / "config.json"
    )
    config = load_config(config_path)

    if args.dry_run:
        config.dry_run = True

    if args.max_parallel:
        config.max_parallel = args.max_parallel

    # Create orchestrator
    orchestrator = Orchestrator(agent_dir, config)

    # Parse stages
    stages = parse_stages(args.stages)

    # Execute based on mode
    if args.list_sessions:
        list_sessions(orchestrator)

    elif args.resume:
        result = resume_session(orchestrator, args.resume, stages, args.verbose)
        print(f"\nSession {result.session_id}: {result.stage.value}")

    elif args.batch:
        # Use config defaults if not specified
        labels = args.label if args.label else None
        max_parallel = args.max_parallel or config.max_parallel

        results = batch_review(
            orchestrator,
            labels,
            args.assignee,
            max_parallel,
            stages,
            args.verbose,
        )
        print(f"\nCompleted {len(results)} reviews")
        total_cost = sum(r.estimated_cost_usd for r in results)
        print(f"Total estimated cost: ${total_cost:.2f}")

    elif args.skill:
        if not args.issue:
            print("Error: --issue is required when using --skill", file=sys.stderr)
            sys.exit(1)

        result = review_single_skill(
            orchestrator, args.skill, args.issue, stages, args.verbose
        )

        if args.cleanup and result.stage == Stage.COMPLETE:
            orchestrator.cleanup_session(result)
            print("Cleaned up worktree")

        # Exit with appropriate code
        sys.exit(0 if result.stage == Stage.COMPLETE else 1)

    else:
        print("Error: Specify --skill, --resume, --batch, or --list-sessions")
        sys.exit(1)


if __name__ == "__main__":
    main()
