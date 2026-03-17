"""Configuration management for skill reviewer."""

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PipelineConfig:
    """Configuration for the review pipeline."""

    # Repository settings
    repo_owner: str = "aRustyDev"
    repo_name: str = "ai"
    base_branch: str = "main"

    # GitHub Projects settings (for project-status workflow)
    project_number: int | None = None  # e.g., 1 for first project
    backlog_status: str = "Backlog"
    in_progress_status: str = "In Progress"
    in_review_status: str = "In Review"
    done_status: str = "Done"

    # Worktree settings
    # Pattern: /private/tmp/worktrees/<project_id>/<issue-id>/
    worktree_base: str = "/private/tmp/worktrees"

    # Execution settings
    max_parallel: int = 3
    dry_run: bool = False

    # Model overrides (optional)
    model_overrides: dict[str, str] = field(default_factory=dict)

    # GitHub labels (fallback when not using Projects)
    review_labels: list[str] = field(default_factory=lambda: ["review", "skills"])
    in_progress_label: str = "status:in-progress"
    in_review_label: str = "status:in-review"

    # Token limits
    max_tokens_per_skill: int = 200000

    # Cost limits
    max_cost_per_skill: float = 5.0  # USD
    max_total_cost: float = 500.0  # USD

    # Assignee filter (only process issues assigned to this user)
    assignee: str | None = None


def load_config(config_path: Path) -> PipelineConfig:
    """Load configuration from JSON file."""
    if not config_path.exists():
        return PipelineConfig()

    with open(config_path) as f:
        data = json.load(f)

    return PipelineConfig(**data)


def save_config(config: PipelineConfig, config_path: Path):
    """Save configuration to JSON file."""
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(config.__dict__, f, indent=2)


def get_default_config_path() -> Path:
    """Get the default config file path."""
    return Path(__file__).parent.parent / "data" / "config.json"
