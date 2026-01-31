# src/consolidate.py
"""LLM-powered feedback consolidation.

Stage 7.5 interface module that wraps feedback.py's analyze_feedback
with the interface expected by stages 8-13.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from .feedback import (
    ActionGroup,
    AnalysisResult,
    analyze_feedback as _analyze_feedback,
)
from .costs import CallCost

if TYPE_CHECKING:
    from .filter import FilteredFeedback
    from .models import TokenUsage
    from .pipeline import PipelineContext


@dataclass
class ConsolidationResult:
    """Result of LLM consolidation."""

    action_groups: list[ActionGroup] = field(default_factory=list)
    guidance: list[str] = field(default_factory=list)
    token_usage: "TokenUsage | None" = None

    # Cross-reference info passed through
    thread_links: dict[str, list[str]] = field(default_factory=dict)

    # Additional metadata from analysis
    blocking_reviews: list[str] = field(default_factory=list)
    approved_by: list[str] = field(default_factory=list)
    summary: str = ""

    @classmethod
    def from_analysis_result(
        cls,
        result: AnalysisResult,
        cost: CallCost | None = None,
    ) -> "ConsolidationResult":
        """Convert an AnalysisResult to ConsolidationResult.

        Args:
            result: AnalysisResult from feedback.py
            cost: Optional call cost for token tracking

        Returns:
            ConsolidationResult with consolidated data
        """
        # Build thread_links from action groups
        thread_links: dict[str, list[str]] = {}
        for group in result.action_groups:
            if group.thread_ids:
                thread_links[group.id] = group.thread_ids

        # Convert cost to TokenUsage if available
        token_usage = None
        if cost:
            # Import here to avoid circular dependency
            try:
                from .models import TokenUsage
                token_usage = TokenUsage(
                    input_tokens=0,  # Cost estimate doesn't have token breakdown
                    output_tokens=0,
                    total_cost=cost.total_cost,
                )
            except ImportError:
                pass

        return cls(
            action_groups=result.action_groups,
            guidance=result.guidance,
            token_usage=token_usage,
            thread_links=thread_links,
            blocking_reviews=result.blocking_reviews,
            approved_by=result.approved_by,
            summary=result.summary,
        )


def consolidate_feedback(
    agent_dir: Path,
    filtered: "FilteredFeedback",
    ctx: "PipelineContext",
    thread_links: dict[str, list[str]] | None = None,
) -> ConsolidationResult:
    """Consolidate filtered feedback into action groups using LLM.

    The consolidator:
    1. Groups related feedback by theme/location
    2. Deduplicates overlapping requests
    3. Prioritizes by severity
    4. Creates actionable descriptions

    Args:
        agent_dir: Path to agent directory (for prompts)
        filtered: Filtered feedback from filter stage
        ctx: Pipeline context with PR info
        thread_links: Optional mapping of review IDs to linked thread IDs

    Returns:
        ConsolidationResult with action groups

    Implementation:
        Uses subagent/consolidator with structured output
    """
    # Build a DiscoveryContext-compatible object for analyze_feedback
    from .discovery import DiscoveryContext

    # Create a minimal discovery context from pipeline context
    # This adapts the Stage 8+ interface to the existing implementation
    discovery_ctx = DiscoveryContext(
        pr=ctx.pr_info,
        pr_number=ctx.pr_info.pr_number,
        skill_path=ctx.skill_path,
        blocking_reviews=filtered.reviews if hasattr(filtered, 'reviews') else [],
        actionable_reviews=[],
        actionable_comments=filtered.comments if hasattr(filtered, 'comments') else [],
        unresolved_threads=filtered.threads if hasattr(filtered, 'threads') else [],
    )

    # Call the existing analyze_feedback
    result, cost = _analyze_feedback(agent_dir, discovery_ctx)

    # Convert to ConsolidationResult
    consolidation = ConsolidationResult.from_analysis_result(result, cost)

    # Merge in provided thread_links if any
    if thread_links:
        consolidation.thread_links.update(thread_links)

    return consolidation


def _build_consolidation_prompt(
    filtered: "FilteredFeedback",
    ctx: "PipelineContext",
    thread_links: dict[str, list[str]] | None,
) -> str:
    """Build the prompt for consolidation LLM call.

    This is used internally by the consolidator sub-agent.
    """
    import json

    lines = [
        f"## PR Information",
        f"- PR Number: {ctx.pr_info.pr_number}",
        f"- Skill: {ctx.skill_path}",
        "",
        "## Feedback to Consolidate",
    ]

    # Add reviews
    if hasattr(filtered, 'reviews') and filtered.reviews:
        lines.append(f"\n### Reviews ({len(filtered.reviews)})")
        for review in filtered.reviews:
            lines.append(f"- {review.author}: {review.body[:200] if review.body else '(no body)'}...")

    # Add comments
    if hasattr(filtered, 'comments') and filtered.comments:
        lines.append(f"\n### Comments ({len(filtered.comments)})")
        for comment in filtered.comments:
            lines.append(f"- {comment.author}: {comment.body[:200]}...")

    # Add threads
    if hasattr(filtered, 'threads') and filtered.threads:
        lines.append(f"\n### Review Threads ({len(filtered.threads)})")
        for thread in filtered.threads:
            lines.append(f"- {thread.path}:{thread.line}")

    # Add thread links if available
    if thread_links:
        lines.append("\n### Cross-References")
        lines.append(json.dumps(thread_links, indent=2))

    lines.append("\n## Instructions")
    lines.append("Consolidate similar feedback into action groups.")

    return "\n".join(lines)


def _parse_consolidation_response(response: dict) -> ConsolidationResult:
    """Parse structured output from consolidation LLM."""
    from .feedback import ActionGroup, Location

    action_groups = []
    for group_data in response.get("action_groups", []):
        locations = [
            Location(
                file=loc.get("file", ""),
                line=loc.get("line"),
                thread_id=loc.get("thread_id"),
            )
            for loc in group_data.get("locations", [])
        ]
        action_groups.append(
            ActionGroup(
                id=group_data.get("id", "unknown"),
                action=group_data.get("action", "other"),
                description=group_data.get("description", ""),
                locations=locations,
                priority=group_data.get("priority", "medium"),
                type=group_data.get("type", "suggestion"),
            )
        )

    return ConsolidationResult(
        action_groups=action_groups,
        guidance=response.get("guidance", []),
        blocking_reviews=response.get("blocking_reviews", []),
        approved_by=response.get("approved_by", []),
        summary=response.get("summary", ""),
    )
