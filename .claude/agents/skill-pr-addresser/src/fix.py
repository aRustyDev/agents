# src/fix.py
"""Fix execution for action groups.

Stage 7.5 interface module that wraps feedback.py's fix functions
with the interface expected by stages 8-13.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from .feedback import (
    ActionGroup,
    FixResult,
    fix_action_group as _fix_action_group,
    fix_batch as _fix_batch,
    fix_all_batches as _fix_all_batches,
    fix_with_escalation as _fix_with_escalation,
)
from .costs import CallCost

if TYPE_CHECKING:
    from .pipeline import PipelineContext
    from .planner import PlanStep
    from .models import AddressedLocation, TokenUsage


@dataclass
class AddressedLocation:
    """A location that was addressed during fixing."""

    file: str
    line: int | None = None
    thread_id: str | None = None
    description: str = ""


@dataclass
class FixStepResult:
    """Result from fixing a single plan step.

    Extended version of FixResult with additional tracking.
    """

    group_id: str
    addressed_locations: list[AddressedLocation] = field(default_factory=list)
    changes_made: list[str] = field(default_factory=list)
    token_usage: "TokenUsage | None" = None
    error: str | None = None

    @property
    def has_changes(self) -> bool:
        return len(self.changes_made) > 0

    @property
    def failed(self) -> bool:
        return self.error is not None

    @property
    def addressed_thread_ids(self) -> list[str]:
        """Extract thread IDs from addressed locations."""
        return [loc.thread_id for loc in self.addressed_locations if loc.thread_id]

    @classmethod
    def from_fix_result(
        cls,
        group_id: str,
        result: FixResult,
        cost: CallCost | None = None,
    ) -> "FixStepResult":
        """Convert a FixResult to FixStepResult.

        Args:
            group_id: ID of the action group
            result: FixResult from feedback.py
            cost: Optional call cost

        Returns:
            FixStepResult with converted data
        """
        # Convert addressed items to AddressedLocation
        locations = []
        for item in result.addressed:
            locations.append(
                AddressedLocation(
                    file=item.get("file", ""),
                    line=item.get("line"),
                    thread_id=item.get("thread_id"),
                    description=item.get("description", ""),
                )
            )

        # Build changes list
        changes = []
        for item in result.addressed:
            if desc := item.get("description"):
                changes.append(desc)
            elif item_id := item.get("id"):
                changes.append(f"Addressed {item_id}")

        # Add file modifications to changes
        for f in result.files_modified:
            changes.append(f"Modified {f}")

        # Convert cost to token usage
        token_usage = None
        if cost:
            try:
                from .models import TokenUsage
                token_usage = TokenUsage(
                    input_tokens=0,
                    output_tokens=0,
                    total_cost=cost.total_cost,
                )
            except ImportError:
                pass

        # Check for errors (skipped items indicate partial failure)
        error = None
        if result.skipped and not result.addressed:
            reasons = [s.get("reason", "Unknown") for s in result.skipped[:3]]
            error = "; ".join(reasons)

        return cls(
            group_id=group_id,
            addressed_locations=locations,
            changes_made=changes,
            token_usage=token_usage,
            error=error,
        )


def fix_action_group(
    ctx: "PipelineContext",
    step: "PlanStep",
) -> FixStepResult:
    """Execute fixes for an action group.

    Args:
        ctx: Pipeline context
        step: Plan step with group_id and metadata

    Returns:
        FixStepResult with addressed locations
    """
    # Find the action group from context
    group = _find_group(ctx, step.group_id)
    if not group:
        return FixStepResult(
            group_id=step.group_id,
            error=f"Action group {step.group_id} not found",
        )

    # Get agent directory from context
    agent_dir = ctx.agent_dir

    # Build discovery context for fix function
    from .discovery import DiscoveryContext

    discovery_ctx = DiscoveryContext(
        pr=ctx.pr_info,
        pr_number=ctx.pr_info.pr_number,
        skill_path=ctx.skill_path,
        worktree=ctx.worktree,
        blocking_reviews=[],
        actionable_reviews=[],
        actionable_comments=[],
        unresolved_threads=[],
    )

    # Get guidance from consolidation result if available
    guidance = ctx.guidance if hasattr(ctx, 'guidance') else []

    # Call the existing fix function
    result, cost = _fix_action_group(
        agent_dir,
        discovery_ctx,
        group,
        guidance,
    )

    return FixStepResult.from_fix_result(step.group_id, result, cost)


def run_fixer_for_locations(
    ctx: "PipelineContext",
    group: ActionGroup,
    pending_locations: list,
) -> FixStepResult:
    """Run fixer sub-agent for pending locations.

    Args:
        ctx: Pipeline context
        group: Action group to fix
        pending_locations: Only locations not yet addressed

    Returns:
        FixStepResult with changes made

    Implementation:
        Invokes subagent/fixer with:
        - Skill file content
        - Action group description
        - Specific locations to fix
    """
    from .feedback import Location

    # Create a modified group with only pending locations
    modified_group = ActionGroup(
        id=group.id,
        action=group.action,
        description=group.description,
        locations=[
            Location(
                file=loc.file if hasattr(loc, 'file') else loc.get("file", ""),
                line=loc.line if hasattr(loc, 'line') else loc.get("line"),
                thread_id=loc.thread_id if hasattr(loc, 'thread_id') else loc.get("thread_id"),
            )
            for loc in pending_locations
        ],
        priority=group.priority,
        type=group.type,
    )

    # Build discovery context
    from .discovery import DiscoveryContext

    discovery_ctx = DiscoveryContext(
        pr=ctx.pr_info,
        pr_number=ctx.pr_info.pr_number,
        skill_path=ctx.skill_path,
        worktree=ctx.worktree,
        blocking_reviews=[],
        actionable_reviews=[],
        actionable_comments=[],
        unresolved_threads=[],
    )

    # Get guidance
    guidance = ctx.guidance if hasattr(ctx, 'guidance') else []

    # Call the existing fix function
    result, cost = _fix_action_group(
        ctx.agent_dir,
        discovery_ctx,
        modified_group,
        guidance,
    )

    return FixStepResult.from_fix_result(group.id, result, cost)


def _find_group(ctx: "PipelineContext", group_id: str) -> ActionGroup | None:
    """Find an action group by ID in the context.

    Args:
        ctx: Pipeline context
        group_id: ID to find

    Returns:
        ActionGroup if found, None otherwise
    """
    # Check consolidated result if available
    if hasattr(ctx, 'consolidation') and ctx.consolidation:
        for group in ctx.consolidation.action_groups:
            if group.id == group_id:
                return group

    # Check analysis result if available
    if hasattr(ctx, 'analysis') and ctx.analysis:
        for group in ctx.analysis.action_groups:
            if group.id == group_id:
                return group

    return None


# Re-export underlying functions for direct use
fix_batch = _fix_batch
fix_all_batches = _fix_all_batches
fix_with_escalation = _fix_with_escalation
