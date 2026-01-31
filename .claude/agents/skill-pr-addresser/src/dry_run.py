# src/dry_run.py
"""Dry-run mode support for previewing changes.

Stage 10 implementation: Preview pipeline stages without making changes.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .filter import FilteredFeedback


@dataclass
class DryRunSummary:
    """Summary of what would be done in a full run."""

    pr_number: int
    discovery_summary: dict = field(default_factory=dict)
    filter_summary: dict = field(default_factory=dict)
    consolidation_summary: dict | None = None
    plan_summary: dict | None = None

    def to_text(self) -> str:
        """Format as human-readable text."""
        lines = [
            f"DRY RUN - Previewing what would be addressed for PR #{self.pr_number}",
            "",
            "=== Discovery ===",
            f"  Reviews: {self.discovery_summary.get('reviews', 0)}",
            f"  Comments: {self.discovery_summary.get('comments', 0)}",
            f"  Threads: {self.discovery_summary.get('threads', 0)} unresolved",
            "",
            "=== Filter (Is-New) ===",
            f"  New items: {self.filter_summary.get('item_count', 0)}",
            f"  Unchanged: {len(self.filter_summary.get('skipped_unchanged', []))} (already addressed)",
            f"  Resolved: {len(self.filter_summary.get('skipped_resolved', []))}",
            "",
        ]

        if self.consolidation_summary:
            lines.extend([
                "=== Consolidation ===",
                f"  Action Groups: {len(self.consolidation_summary.get('action_groups', []))}",
            ])
            for group in self.consolidation_summary.get("action_groups", []):
                lines.append(
                    f"    - {group['id']}: {group['type']} ({group['location_count']} locations)"
                )

            lines.extend([
                f"  Guidance: {len(self.consolidation_summary.get('guidance', []))} items",
                "",
            ])

        if self.plan_summary:
            lines.extend([
                "=== Execution Plan ===",
            ])
            for i, step in enumerate(self.plan_summary.get("steps", []), 1):
                lines.append(
                    f"  {i}. [{step['priority']}] {step['group_id']}: {step['description']}"
                )

            lines.extend([
                "",
                f"Would address {self.plan_summary.get('total_items', 0)} feedback items "
                f"in {len(self.plan_summary.get('steps', []))} action groups.",
            ])

        lines.append("")
        lines.append("No changes made (dry run).")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output."""
        return {
            "pr_number": self.pr_number,
            "discovery": self.discovery_summary,
            "filter": self.filter_summary,
            "consolidation": self.consolidation_summary,
            "plan": self.plan_summary,
        }


def run_dry_run(
    addresser,
    pr_number: int,
    stop_after: str = "plan",
) -> DryRunSummary:
    """Execute pipeline stages up to stop_after for preview.

    Args:
        addresser: Addresser instance
        pr_number: PR to analyze
        stop_after: Stage to stop after (discovery, filter, consolidate, plan)

    Returns:
        DryRunSummary with stage outputs
    """
    summary = DryRunSummary(
        pr_number=pr_number,
        discovery_summary={},
        filter_summary={},
    )

    # Run discovery
    ctx = addresser.run_discovery(pr_number)
    summary.discovery_summary = {
        "reviews": len(ctx.raw_reviews),
        "comments": len(ctx.raw_comments),
        "threads": len(ctx.raw_threads),
    }

    if stop_after == "discovery":
        return summary

    # Run filter
    filtered = addresser.run_filter(ctx)
    summary.filter_summary = filtered.summary()
    summary.filter_summary["item_count"] = filtered.item_count

    if stop_after == "filter":
        return summary

    # Run consolidation
    consolidated = addresser.run_consolidate(ctx, filtered)
    summary.consolidation_summary = {
        "action_groups": [
            {
                "id": g.id,
                "type": g.type,
                "location_count": len(g.locations),
            }
            for g in consolidated.action_groups
        ],
        "guidance": consolidated.guidance if hasattr(consolidated, "guidance") else [],
    }

    if stop_after == "consolidate":
        return summary

    # Run planning
    plan = addresser.run_plan(ctx, consolidated)
    summary.plan_summary = {
        "steps": [
            {
                "group_id": s.group_id,
                "priority": s.priority,
                "description": s.description if hasattr(s, "description") else "",
            }
            for s in plan.steps
        ],
        "total_items": plan.total_items if hasattr(plan, "total_items") else len(plan.steps),
    }

    return summary


class DryRunMode:
    """Context for dry-run execution mode."""

    def __init__(self, enabled: bool = False, stop_after: str = "plan"):
        """Initialize dry-run mode.

        Args:
            enabled: Whether dry-run is enabled
            stop_after: Stage to stop after
        """
        self.enabled = enabled
        self.stop_after = stop_after
        self._actions: list[dict] = []

    def record_action(self, action_type: str, **details) -> None:
        """Record an action that would be taken.

        Args:
            action_type: Type of action (commit, resolve, comment, etc.)
            **details: Action-specific details
        """
        if self.enabled:
            self._actions.append({
                "type": action_type,
                **details,
            })

    @property
    def recorded_actions(self) -> list[dict]:
        """Get all recorded actions."""
        return self._actions.copy()

    def would_commit(self, message: str, files: list[str]) -> None:
        """Record a commit that would be made."""
        self.record_action("commit", message=message, files=files)

    def would_resolve(self, thread_id: str) -> None:
        """Record a thread that would be resolved."""
        self.record_action("resolve_thread", thread_id=thread_id)

    def would_comment(self, pr_number: int, body: str) -> None:
        """Record a comment that would be posted."""
        self.record_action("comment", pr_number=pr_number, body=body[:100] + "...")

    def would_push(self, branch: str) -> None:
        """Record a push that would be made."""
        self.record_action("push", branch=branch)

    def get_summary_text(self) -> str:
        """Get summary of recorded actions."""
        if not self._actions:
            return "No actions would be taken."

        lines = ["Actions that would be taken:", ""]
        for i, action in enumerate(self._actions, 1):
            action_type = action.pop("type")
            details = ", ".join(f"{k}={v}" for k, v in action.items())
            lines.append(f"  {i}. {action_type}: {details}")

        return "\n".join(lines)
