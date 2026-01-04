# src/planner.py
"""Execution planning for action groups.

Stage 7.5 interface module that creates execution plans from
consolidated action groups.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .consolidate import ConsolidationResult
    from .feedback import ActionGroup


@dataclass
class PlanStep:
    """A single step in the execution plan."""

    group_id: str
    priority: str  # "critical", "high", "medium", "low"
    description: str
    estimated_changes: int
    dependencies: list[str] = field(default_factory=list)


@dataclass
class ExecutionPlan:
    """Ordered execution plan."""

    steps: list[PlanStep] = field(default_factory=list)

    @property
    def total_items(self) -> int:
        return len(self.steps)

    def get_step(self, group_id: str) -> PlanStep | None:
        return next((s for s in self.steps if s.group_id == group_id), None)

    def get_next_pending(self, completed: set[str]) -> PlanStep | None:
        """Get the next step whose dependencies are all completed.

        Args:
            completed: Set of completed group IDs

        Returns:
            Next executable step, or None if all done or blocked
        """
        for step in self.steps:
            if step.group_id in completed:
                continue
            if all(dep in completed for dep in step.dependencies):
                return step
        return None

    def get_executable_steps(self, completed: set[str]) -> list[PlanStep]:
        """Get all steps that can be executed in parallel.

        Args:
            completed: Set of completed group IDs

        Returns:
            List of steps whose dependencies are satisfied
        """
        executable = []
        for step in self.steps:
            if step.group_id in completed:
                continue
            if all(dep in completed for dep in step.dependencies):
                executable.append(step)
        return executable


def create_plan(consolidated: "ConsolidationResult") -> ExecutionPlan:
    """Create execution plan from consolidated feedback.

    Ordering strategy:
    1. Critical items first (blocking issues)
    2. High priority (major improvements)
    3. Medium priority (enhancements)
    4. Low priority (nice-to-have)

    Within priority, order by:
    - Dependencies (do prerequisites first)
    - Location (top-to-bottom in file)
    - Size (smaller changes first)

    Args:
        consolidated: Consolidated feedback

    Returns:
        ExecutionPlan with ordered steps
    """
    steps: list[PlanStep] = []

    for group in consolidated.action_groups:
        priority = _assign_priority(group)
        estimated = _estimate_changes(group)
        deps = _find_dependencies(group, consolidated.action_groups)

        steps.append(
            PlanStep(
                group_id=group.id,
                priority=priority,
                description=group.description,
                estimated_changes=estimated,
                dependencies=deps,
            )
        )

    # Sort by priority, then by dependencies
    steps = _sort_by_priority(steps)
    steps = _sort_by_dependencies(steps)

    return ExecutionPlan(steps=steps)


def _assign_priority(group: "ActionGroup") -> str:
    """Assign priority based on action group type and content.

    Args:
        group: Action group to prioritize

    Returns:
        Priority string: "critical", "high", "medium", or "low"
    """
    # Map existing priority to standardized values
    priority_map = {
        "critical": "critical",
        "high": "high",
        "medium": "medium",
        "low": "low",
    }

    # Use group's priority if valid
    if group.priority in priority_map:
        base_priority = priority_map[group.priority]
    else:
        base_priority = "medium"

    # Elevate priority for change_request type
    if group.type == "change_request":
        if base_priority == "low":
            return "medium"
        if base_priority == "medium":
            return "high"
        return "critical"

    # Lower priority for nitpicks
    if group.type == "nitpick":
        if base_priority == "critical":
            return "high"
        if base_priority == "high":
            return "medium"
        return "low"

    return base_priority


def _estimate_changes(group: "ActionGroup") -> int:
    """Estimate number of changes needed for an action group.

    Args:
        group: Action group

    Returns:
        Estimated number of changes
    """
    # Base estimate on number of locations
    base = len(group.locations)

    # Adjust based on action type
    action_multipliers = {
        "add_section": 3,
        "move_to_examples": 2,
        "move_to_references": 2,
        "fix_typo": 1,
        "update_content": 2,
        "delete": 1,
    }

    multiplier = action_multipliers.get(group.action, 2)
    return max(1, base * multiplier)


def _find_dependencies(
    group: "ActionGroup",
    all_groups: list["ActionGroup"],
) -> list[str]:
    """Find dependencies for an action group.

    Args:
        group: Action group to check
        all_groups: All action groups

    Returns:
        List of group IDs that must complete first
    """
    deps: list[str] = []

    # Check for file dependencies
    # If another group modifies a file this group reads from, depend on it
    group_files = {loc.file for loc in group.locations if loc.file}

    for other in all_groups:
        if other.id == group.id:
            continue

        other_files = {loc.file for loc in other.locations if loc.file}

        # If other group creates/moves content that this group references
        if other.action in ("add_section", "move_to_references", "move_to_examples"):
            # Check for overlapping files
            if group_files & other_files:
                # Higher priority actions should be dependencies
                if _priority_value(other.priority) > _priority_value(group.priority):
                    deps.append(other.id)

    return deps


def _priority_value(priority: str) -> int:
    """Convert priority string to numeric value for comparison."""
    values = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1,
    }
    return values.get(priority, 2)


def _sort_by_priority(steps: list[PlanStep]) -> list[PlanStep]:
    """Sort steps by priority (critical first).

    Args:
        steps: Unsorted steps

    Returns:
        Steps sorted by priority
    """
    return sorted(steps, key=lambda s: -_priority_value(s.priority))


def _sort_by_dependencies(steps: list[PlanStep]) -> list[PlanStep]:
    """Topological sort by dependencies.

    Args:
        steps: Steps sorted by priority

    Returns:
        Steps sorted to respect dependencies
    """
    # Build adjacency list
    step_map = {s.group_id: s for s in steps}
    result: list[PlanStep] = []
    visited: set[str] = set()
    temp_mark: set[str] = set()

    def visit(step: PlanStep) -> None:
        if step.group_id in temp_mark:
            # Cycle detected, skip
            return
        if step.group_id in visited:
            return

        temp_mark.add(step.group_id)

        # Visit dependencies first
        for dep_id in step.dependencies:
            if dep_id in step_map:
                visit(step_map[dep_id])

        temp_mark.remove(step.group_id)
        visited.add(step.group_id)
        result.append(step)

    # Process all steps
    for step in steps:
        if step.group_id not in visited:
            visit(step)

    return result
