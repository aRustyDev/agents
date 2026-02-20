"""Cost tracking for LLM API calls.

Estimates costs based on model pricing and tracks cumulative spending.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

log = logging.getLogger(__name__)

# Approximate pricing per 1K tokens (as of 2024)
# These are estimates and should be updated when pricing changes
MODEL_PRICING = {
    # Claude 3.5 Haiku
    "claude-3-5-haiku-20241022": {"input": 0.001, "output": 0.005},
    # Claude Sonnet 4
    "claude-sonnet-4-20250514": {"input": 0.003, "output": 0.015},
    # Legacy names for compatibility
    "haiku-35": {"input": 0.001, "output": 0.005},
    "sonnet-4": {"input": 0.003, "output": 0.015},
}

# Average tokens per call (rough estimates)
# Based on typical skill-pr-addresser usage patterns
ESTIMATED_TOKENS = {
    "feedback-analyzer": {"input": 2000, "output": 500},
    "feedback-fixer": {"input": 3000, "output": 2000},
}


@dataclass
class CallCost:
    """Cost for a single API call."""

    subagent: str
    model: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SessionCosts:
    """Cumulative costs for a session."""

    session_id: str
    pr_number: int
    calls: list[CallCost] = field(default_factory=list)
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost: float = 0.0

    def add_call(self, call: CallCost) -> None:
        """Add a call to the session."""
        self.calls.append(call)
        self.total_input_tokens += call.input_tokens
        self.total_output_tokens += call.output_tokens
        self.total_cost += call.total_cost

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "pr_number": self.pr_number,
            "calls": [
                {
                    "subagent": c.subagent,
                    "model": c.model,
                    "input_tokens": c.input_tokens,
                    "output_tokens": c.output_tokens,
                    "input_cost": c.input_cost,
                    "output_cost": c.output_cost,
                    "total_cost": c.total_cost,
                    "timestamp": c.timestamp,
                }
                for c in self.calls
            ],
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost": self.total_cost,
        }

    def save(self, sessions_dir: Path) -> None:
        """Save costs to session directory."""
        session_path = sessions_dir / self.session_id
        session_path.mkdir(parents=True, exist_ok=True)
        costs_file = session_path / "costs.json"
        costs_file.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, sessions_dir: Path, session_id: str) -> "SessionCosts | None":
        """Load costs from session directory."""
        costs_file = sessions_dir / session_id / "costs.json"
        if not costs_file.exists():
            return None

        try:
            data = json.loads(costs_file.read_text())
            costs = cls(
                session_id=data["session_id"],
                pr_number=data["pr_number"],
                total_input_tokens=data.get("total_input_tokens", 0),
                total_output_tokens=data.get("total_output_tokens", 0),
                total_cost=data.get("total_cost", 0.0),
            )
            for call_data in data.get("calls", []):
                costs.calls.append(
                    CallCost(
                        subagent=call_data["subagent"],
                        model=call_data["model"],
                        input_tokens=call_data["input_tokens"],
                        output_tokens=call_data["output_tokens"],
                        input_cost=call_data["input_cost"],
                        output_cost=call_data["output_cost"],
                        total_cost=call_data["total_cost"],
                        timestamp=call_data.get("timestamp", ""),
                    )
                )
            return costs
        except Exception as e:
            log.warning(f"Failed to load costs: {e}")
            return None


def get_model_pricing(model: str) -> dict[str, float]:
    """Get pricing for a model.

    Args:
        model: Model name or ID

    Returns:
        Dict with 'input' and 'output' prices per 1K tokens
    """
    # Try exact match first
    if model in MODEL_PRICING:
        return MODEL_PRICING[model]

    # Try partial match
    model_lower = model.lower()
    for key, pricing in MODEL_PRICING.items():
        if key in model_lower or model_lower in key:
            return pricing

    # Default to Sonnet pricing (most common)
    return MODEL_PRICING["claude-sonnet-4-20250514"]


def estimate_call_cost(
    subagent: str,
    model: str,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
) -> CallCost:
    """Estimate the cost of a sub-agent call.

    Args:
        subagent: Sub-agent name
        model: Model used
        input_tokens: Actual input tokens (or None for estimate)
        output_tokens: Actual output tokens (or None for estimate)

    Returns:
        CallCost with estimated values
    """
    pricing = get_model_pricing(model)

    # Use estimates if actual tokens not provided
    if input_tokens is None:
        estimates = ESTIMATED_TOKENS.get(subagent, {"input": 2000, "output": 1000})
        input_tokens = estimates["input"]
    if output_tokens is None:
        estimates = ESTIMATED_TOKENS.get(subagent, {"input": 2000, "output": 1000})
        output_tokens = estimates["output"]

    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]

    return CallCost(
        subagent=subagent,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_cost=round(input_cost, 6),
        output_cost=round(output_cost, 6),
        total_cost=round(input_cost + output_cost, 6),
    )


def estimate_pr_cost(
    num_iterations: int = 1,
    use_haiku_for_analysis: bool = True,
    use_sonnet_for_fixes: bool = True,
) -> float:
    """Estimate total cost for addressing a PR.

    Args:
        num_iterations: Expected number of iterations
        use_haiku_for_analysis: Whether Haiku is used for analysis
        use_sonnet_for_fixes: Whether Sonnet is used for fixes

    Returns:
        Estimated total cost in USD
    """
    total = 0.0

    for _ in range(num_iterations):
        # Analysis call
        analysis_model = (
            "claude-3-5-haiku-20241022" if use_haiku_for_analysis else "claude-sonnet-4-20250514"
        )
        total += estimate_call_cost("feedback-analyzer", analysis_model).total_cost

        # Fix call
        fix_model = (
            "claude-sonnet-4-20250514" if use_sonnet_for_fixes else "claude-3-5-haiku-20241022"
        )
        total += estimate_call_cost("feedback-fixer", fix_model).total_cost

    return round(total, 4)


def format_cost(cost: float) -> str:
    """Format cost as currency string.

    Args:
        cost: Cost in USD

    Returns:
        Formatted string like "$0.75"
    """
    if cost < 0.01:
        return f"${cost:.4f}"
    return f"${cost:.2f}"


def get_cost_summary(costs: SessionCosts) -> str:
    """Generate a human-readable cost summary.

    Args:
        costs: Session costs

    Returns:
        Multi-line summary string
    """
    lines = [
        f"Cost Summary for PR #{costs.pr_number}",
        "-" * 40,
        f"Total calls: {len(costs.calls)}",
        f"Input tokens: {costs.total_input_tokens:,}",
        f"Output tokens: {costs.total_output_tokens:,}",
        f"Total cost: {format_cost(costs.total_cost)}",
        "",
        "By sub-agent:",
    ]

    # Group by subagent
    by_subagent: dict[str, list[CallCost]] = {}
    for call in costs.calls:
        if call.subagent not in by_subagent:
            by_subagent[call.subagent] = []
        by_subagent[call.subagent].append(call)

    for subagent, calls in by_subagent.items():
        subagent_cost = sum(c.total_cost for c in calls)
        lines.append(f"  {subagent}: {len(calls)} calls, {format_cost(subagent_cost)}")

    return "\n".join(lines)
