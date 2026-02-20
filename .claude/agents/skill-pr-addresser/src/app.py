"""Cement application class for skill-pr-addresser."""

import sys
from pathlib import Path

from cement import App, Controller, ex
from cement.ext.ext_colorlog import ColorLogHandler

# Add parent directory to path for shared library import
_agents_dir = Path(__file__).parent.parent.parent
if str(_agents_dir) not in sys.path:
    sys.path.insert(0, str(_agents_dir))


from .addresser import Addresser
from .costs import format_cost
from .discovery import discover
from .exceptions import (
    AddresserError,
    NoFeedbackError,
    PRClosedError,
    PRNotFoundError,
)
from .ext_toml import TomlConfigHandler
from .github_pr import find_prs_with_feedback
from .progress import ProgressTracker
from .tracing import TracingConfig, init_tracing


class Base(Controller):
    """Base controller for skill-pr-addresser."""

    class Meta:
        label = "base"
        description = "Address PR review feedback for skills"
        arguments = [
            (
                ["-v", "--version"],
                {"action": "version", "version": "skill-pr-addresser 0.1.0"},
            ),
        ]

    def _default(self):
        """Default action when no subcommand given."""
        self.app.args.print_help()

    @ex(
        help="Address review feedback on a PR",
        arguments=[
            (["pr_number"], {"help": "Pull request number", "type": int}),
            (
                ["--skill"],
                {"help": "Skill path (auto-detected from PR if not specified)"},
            ),
            (
                ["--max-iterations"],
                {
                    "help": "Maximum addressing iterations (default: 3)",
                    "type": int,
                    "default": 3,
                },
            ),
            (
                ["--dry-run"],
                {
                    "help": "Show what would be done without making changes",
                    "action": "store_true",
                },
            ),
            (
                ["--force"],
                {
                    "help": "Force addressing even if PR has no pending feedback",
                    "action": "store_true",
                },
            ),
            (
                ["--verbose"],
                {
                    "help": "Enable verbose/debug output",
                    "action": "store_true",
                },
            ),
            (
                ["--interactive"],
                {
                    "help": "Run sub-agents in TUI mode (for watching only, workflow won't complete)",
                    "action": "store_true",
                },
            ),
            (
                ["--stream"],
                {
                    "help": "Stream sub-agent output in real-time (recommended for debugging)",
                    "action": "store_true",
                },
            ),
        ],
    )
    def address(self):
        """Address review feedback on a PR."""
        import logging

        from .feedback import set_debug_mode

        pr_number = self.app.pargs.pr_number
        skill = self.app.pargs.skill
        dry_run = self.app.pargs.dry_run
        force = self.app.pargs.force
        max_iterations = self.app.pargs.max_iterations
        verbose = self.app.pargs.verbose
        interactive = self.app.pargs.interactive
        stream = self.app.pargs.stream

        # Set sub-agent debug mode
        if interactive or stream:
            set_debug_mode(interactive=interactive, verbose=stream)
            if interactive:
                self.app.log.info("[DEBUG] Interactive mode: sub-agents will run in TUI")
                self.app.log.warning("[DEBUG] Workflow will NOT complete in interactive mode")
                self.app.log.warning(
                    "[DEBUG] Use --stream instead for debugging with workflow completion"
                )
            if stream:
                self.app.log.info("[DEBUG] Stream mode: sub-agent output will be shown")

        # Enable debug logging if verbose
        if verbose:
            for handler in self.app.log.backend.handlers:
                handler.setLevel(logging.DEBUG)
            self.app.log.backend.setLevel(logging.DEBUG)
            # Also set module-level loggers
            logging.getLogger("src").setLevel(logging.DEBUG)

        owner = self.app.config.get("skill-pr-addresser", "repo_owner")
        repo = self.app.config.get("skill-pr-addresser", "repo_name")

        self.app.log.info(f"Discovering context for PR #{pr_number}...")

        try:
            ctx = discover(
                owner=owner,
                repo=repo,
                pr_number=pr_number,
                sessions_dir=self.app.sessions_dir,
                worktree_base=self.app.worktree_base,
                repo_path=self.app.repo_path,
                skill_path=skill,
                force=force,
            )

            # Print discovery summary
            self.app.log.info("Discovery complete:")
            for line in ctx.summary().split("\n"):
                self.app.log.info(line)

            if dry_run:
                self.app.log.info("[DRY RUN] Would address feedback:")
                for review in ctx.blocking_reviews:
                    self.app.log.info(f"  - Review from {review.author}: {review.state}")
                for thread in ctx.unresolved_threads:
                    self.app.log.info(
                        f"  - Thread on {thread.path}:{thread.line} by {thread.author}"
                    )
                self.app.log.info("[DRY RUN] No changes made")
                return

            # Run the addresser
            agent_dir = Path(__file__).parent.parent
            rate_limit = self.app.config.get("skill-pr-addresser", "rate_limit_delay")

            addresser = Addresser(
                agent_dir=agent_dir,
                sessions_dir=self.app.sessions_dir,
                owner=owner,
                repo=repo,
                rate_limit_delay=float(rate_limit) if rate_limit else 1.0,
            )

            result = addresser.address(ctx, max_iterations)

            # Report final summary
            if result.success:
                self.app.log.info(
                    f"Addressed {result.total_addressed} items across "
                    f"{result.iterations_run} iteration(s)"
                )
                if result.total_skipped:
                    self.app.log.warning(f"Skipped {result.total_skipped} items")
                if result.ready_for_review:
                    self.app.log.info("PR is ready for re-review")
                self.app.log.info(f"Total cost: {result.cost_formatted}")
            else:
                self.app.log.warning("Could not address feedback")
                if result.error:
                    self.app.log.error(result.error)
                if result.total_cost > 0:
                    self.app.log.info(f"Cost incurred: {result.cost_formatted}")

        except PRNotFoundError as e:
            self.app.log.error(str(e))
            self.app.exit_code = 1

        except PRClosedError as e:
            self.app.log.info(str(e))
            # Exit code 0 - not an error, just nothing to do

        except NoFeedbackError as e:
            self.app.log.info(str(e))
            # Exit code 0 - not an error, just nothing to do

        except AddresserError as e:
            self.app.log.error(str(e))
            self.app.exit_code = e.exit_code

    @ex(
        help="Check addressing status for a PR",
        arguments=[
            (["pr_number"], {"help": "Pull request number", "type": int}),
        ],
    )
    def status(self):
        """Check addressing status for a PR."""
        pr_number = self.app.pargs.pr_number
        owner = self.app.config.get("skill-pr-addresser", "repo_owner")
        repo = self.app.config.get("skill-pr-addresser", "repo_name")

        self.app.log.info(f"Checking status for PR #{pr_number}...")

        try:
            # Use discovery to get current state
            ctx = discover(
                owner=owner,
                repo=repo,
                pr_number=pr_number,
                sessions_dir=self.app.sessions_dir,
                worktree_base=self.app.worktree_base,
                repo_path=self.app.repo_path,
                force=True,  # Don't fail if no feedback
            )

            print(ctx.summary())

            if ctx.pr.review_decision == "APPROVED":
                self.app.log.info("PR is approved!")
            elif ctx.needs_changes:
                self.app.log.info(f"PR needs changes ({ctx.feedback_count} items)")
            else:
                self.app.log.info("PR has no pending feedback")

        except PRNotFoundError as e:
            self.app.log.error(str(e))
            self.app.exit_code = 1

        except PRClosedError as e:
            self.app.log.info(str(e))

    @ex(
        help="List sessions",
        arguments=[
            (
                ["--all"],
                {
                    "help": "Include completed sessions",
                    "action": "store_true",
                    "dest": "show_all",
                },
            ),
        ],
    )
    def sessions(self):
        """List all sessions."""
        from skill_agents_common.session import list_sessions as list_sessions_common

        sessions = list_sessions_common(self.app.sessions_dir)

        if not sessions:
            self.app.log.info("No sessions found")
            return

        show_all = self.app.pargs.show_all

        # Filter if not showing all
        if not show_all:
            sessions = [s for s in sessions if s.get("stage") not in ("complete", "failed")]

        if not sessions:
            self.app.log.info("No active sessions found (use --all to see completed)")
            return

        # Print header
        print(f"{'ID':<10} {'PR':<8} {'Stage':<20} {'Skill':<40}")
        print("-" * 80)

        for s in sessions:
            pr = s.get("pr_number", "-")
            print(
                f"{s['session_id']:<10} "
                f"{'#' + str(pr) if pr else '-':<8} "
                f"{s['stage']:<20} "
                f"{s.get('skill_path', '-'):<40}"
            )

    @ex(
        help="Find PRs with pending feedback",
        arguments=[
            (
                ["--label"],
                {
                    "help": "Filter by label (can be used multiple times)",
                    "action": "append",
                    "dest": "labels",
                },
            ),
            (
                ["--limit"],
                {
                    "help": "Maximum number of PRs to return (default: 50)",
                    "type": int,
                    "default": 50,
                },
            ),
        ],
    )
    def find(self):
        """Find PRs with pending feedback."""
        owner = self.app.config.get("skill-pr-addresser", "repo_owner")
        repo = self.app.config.get("skill-pr-addresser", "repo_name")
        labels = self.app.pargs.labels
        limit = self.app.pargs.limit

        self.app.log.info(f"Finding PRs with pending feedback in {owner}/{repo}...")

        prs = find_prs_with_feedback(
            owner=owner,
            repo=repo,
            labels=labels,
            limit=limit,
        )

        if not prs:
            self.app.log.info("No PRs with pending feedback found")
            return

        # Print header
        print(f"{'PR':<8} {'Reviewers':<30} {'Title':<50}")
        print("-" * 90)

        for pr in prs:
            reviewers = ", ".join(pr.get("blocking_reviewers", []))[:28]
            title = pr.get("title", "")[:48]
            print(f"#{pr['pr_number']:<7} {reviewers:<30} {title:<50}")

        print(f"\nFound {len(prs)} PR(s) with pending feedback")

    @ex(
        help="Address feedback on all PRs with pending reviews",
        arguments=[
            (
                ["--label"],
                {
                    "help": "Filter by label (can be used multiple times)",
                    "action": "append",
                    "dest": "labels",
                },
            ),
            (
                ["--max-iterations"],
                {
                    "help": "Maximum addressing iterations per PR (default: 3)",
                    "type": int,
                    "default": 3,
                },
            ),
            (
                ["--dry-run"],
                {
                    "help": "Show what would be done without making changes",
                    "action": "store_true",
                },
            ),
            (
                ["--limit"],
                {
                    "help": "Maximum number of PRs to process (default: 10)",
                    "type": int,
                    "default": 10,
                },
            ),
        ],
    )
    def batch(self):
        """Address feedback on all PRs with pending reviews."""
        owner = self.app.config.get("skill-pr-addresser", "repo_owner")
        repo = self.app.config.get("skill-pr-addresser", "repo_name")
        labels = self.app.pargs.labels
        max_iterations = self.app.pargs.max_iterations
        dry_run = self.app.pargs.dry_run
        limit = self.app.pargs.limit

        self.app.log.info(f"Finding PRs with pending feedback in {owner}/{repo}...")

        prs = find_prs_with_feedback(
            owner=owner,
            repo=repo,
            labels=labels,
            limit=limit,
        )

        if not prs:
            self.app.log.info("No PRs with pending feedback found")
            return

        self.app.log.info(f"Found {len(prs)} PR(s) with pending feedback")

        if dry_run:
            self.app.log.info("[DRY RUN] Would address:")
            for pr in prs:
                reviewers = ", ".join(pr.get("blocking_reviewers", []))
                self.app.log.info(f"  PR #{pr['pr_number']}: {pr['title']}")
                if reviewers:
                    self.app.log.info(f"    Blocking reviewers: {reviewers}")
            self.app.log.info("[DRY RUN] No changes made")
            return

        # Initialize progress tracker
        tracker = ProgressTracker(self.app.data_dir)
        pr_numbers = [pr["pr_number"] for pr in prs]
        tracker.start_batch(pr_numbers)

        # Track total cost across batch
        total_batch_cost = 0.0

        for i, pr_info in enumerate(prs, 1):
            pr_number = pr_info["pr_number"]
            self.app.log.info(f"\n[{i}/{len(prs)}] Addressing PR #{pr_number}...")

            try:
                ctx = discover(
                    owner=owner,
                    repo=repo,
                    pr_number=pr_number,
                    sessions_dir=self.app.sessions_dir,
                    worktree_base=self.app.worktree_base,
                    repo_path=self.app.repo_path,
                    force=False,
                )

                tracker.start_pr(
                    pr_number,
                    title=pr_info.get("title", ""),
                    skill_path=ctx.skill_path,
                )

                # Run the addresser
                agent_dir = Path(__file__).parent.parent
                rate_limit = self.app.config.get("skill-pr-addresser", "rate_limit_delay")

                addresser = Addresser(
                    agent_dir=agent_dir,
                    sessions_dir=self.app.sessions_dir,
                    owner=owner,
                    repo=repo,
                    rate_limit_delay=float(rate_limit) if rate_limit else 1.0,
                )

                result = addresser.address(ctx, max_iterations)

                if result.success:
                    self.app.log.info(
                        f"  ✓ Addressed {result.total_addressed} items ({result.cost_formatted})"
                    )
                    tracker.update_iteration(
                        pr_number,
                        iteration=result.iterations_run,
                        feedback_count=result.total_addressed + result.total_skipped,
                        addressed_count=result.total_addressed,
                        skipped_count=result.total_skipped,
                        cost=result.total_cost,
                    )
                    tracker.complete_pr(pr_number, success=True)
                    total_batch_cost += result.total_cost
                else:
                    self.app.log.warning(f"  ✗ Failed: {result.error}")
                    tracker.complete_pr(pr_number, success=False, error=result.error)
                    total_batch_cost += result.total_cost

            except (PRClosedError, NoFeedbackError) as e:
                self.app.log.info(f"  - Skipped: {e}")
                tracker.skip_pr(pr_number, reason=str(e))

            except (PRNotFoundError, AddresserError) as e:
                self.app.log.error(f"  ✗ Error: {e}")
                tracker.complete_pr(pr_number, success=False, error=str(e))

        # Complete batch and print summary
        tracker.complete_batch()

        self.app.log.info("\n" + "=" * 50)
        self.app.log.info(tracker.get_summary())
        self.app.log.info(f"Total batch cost: {format_cost(total_batch_cost)}")


class SkillPRAddresser(App):
    """Cement application for addressing PR review feedback."""

    class Meta:
        label = "skill-pr-addresser"
        handlers = [Base, ColorLogHandler, TomlConfigHandler]
        config_handler = "toml"
        extensions = ["colorlog"]
        config_file_suffix = ".toml"
        config_files = [
            # Local config (relative to agent directory)
            str(Path(__file__).parent.parent / "config.toml"),
            # User config
            "~/.config/skill-pr-addresser/config.toml",
        ]
        config_defaults = {
            "skill-pr-addresser": {
                "repo_owner": "aRustyDev",
                "repo_name": "ai",
                "max_iterations": 3,
                "rate_limit_delay": 1.0,
                "worktree_base": "/private/tmp/worktrees",
            },
            "otel": {
                "enabled": False,
                "endpoint": "localhost:4317",  # gRPC endpoint (no http:// prefix)
                "service_name": "skill-pr-addresser",
                "version": "0.1.0",
            },
        }
        exit_on_close = True

    def setup(self):
        """Set up the application."""
        super().setup()
        self._init_tracing()

    def _init_tracing(self):
        """Initialize OpenTelemetry tracing from config."""
        otel_enabled = self.config.get("otel", "enabled")
        if otel_enabled and str(otel_enabled).lower() in ("true", "1", "yes"):
            tracing_config = TracingConfig(
                enabled=True,
                endpoint=self.config.get("otel", "endpoint"),
                service_name=self.config.get("otel", "service_name"),
                version=self.config.get("otel", "version"),
            )
            if init_tracing(tracing_config):
                self.log.debug("OpenTelemetry tracing initialized")
            else:
                self.log.debug("OpenTelemetry tracing not available")

    @property
    def data_dir(self) -> Path:
        """Directory for agent data storage."""
        return Path(__file__).parent.parent / "data"

    @property
    def sessions_dir(self) -> Path:
        """Directory for session storage."""
        sessions = self.data_dir / "sessions"
        sessions.mkdir(parents=True, exist_ok=True)
        return sessions

    @property
    def worktree_base(self) -> Path:
        """Base directory for worktrees."""
        base = self.config.get("skill-pr-addresser", "worktree_base")
        return Path(base)

    @property
    def repo_path(self) -> Path:
        """Path to the main repository.

        Walks up from the agent directory to find the repo root.
        """
        # Agent is at .claude/agents/skill-pr-addresser/
        # Repo root is 4 levels up
        agent_dir = Path(__file__).parent.parent
        repo_root = agent_dir.parent.parent.parent
        return repo_root
