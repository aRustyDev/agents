"""Tests for the costs module."""

import pytest
from pathlib import Path

import sys

# Add agent directory to path
_agent_dir = Path(__file__).parent.parent
if str(_agent_dir) not in sys.path:
    sys.path.insert(0, str(_agent_dir))

from src.costs import (
    CallCost,
    SessionCosts,
    get_model_pricing,
    estimate_call_cost,
    estimate_pr_cost,
    format_cost,
    get_cost_summary,
)


class TestModelPricing:
    """Tests for get_model_pricing function."""

    def test_exact_match(self):
        """Should return pricing for exact model match."""
        pricing = get_model_pricing("claude-3-5-haiku-20241022")
        assert pricing["input"] == 0.001
        assert pricing["output"] == 0.005

    def test_partial_match(self):
        """Should return pricing for partial model match."""
        pricing = get_model_pricing("haiku-35")
        assert pricing["input"] == 0.001

    def test_unknown_model_defaults_to_sonnet(self):
        """Should default to Sonnet pricing for unknown models."""
        pricing = get_model_pricing("unknown-model")
        assert pricing["input"] == 0.003
        assert pricing["output"] == 0.015


class TestEstimateCallCost:
    """Tests for estimate_call_cost function."""

    def test_estimates_with_actual_tokens(self):
        """Should calculate cost from actual tokens."""
        cost = estimate_call_cost(
            "feedback-analyzer",
            "claude-3-5-haiku-20241022",
            input_tokens=1000,
            output_tokens=500,
        )

        # 1000/1000 * 0.001 = 0.001 input
        # 500/1000 * 0.005 = 0.0025 output
        assert cost.input_cost == 0.001
        assert cost.output_cost == 0.0025
        assert cost.total_cost == 0.0035

    def test_estimates_without_tokens(self):
        """Should use default estimates when tokens not provided."""
        cost = estimate_call_cost(
            "feedback-analyzer",
            "claude-3-5-haiku-20241022",
        )

        # Uses ESTIMATED_TOKENS defaults
        assert cost.input_tokens == 2000
        assert cost.output_tokens == 500
        assert cost.total_cost > 0


class TestEstimatePRCost:
    """Tests for estimate_pr_cost function."""

    def test_single_iteration(self):
        """Should estimate cost for single iteration."""
        cost = estimate_pr_cost(num_iterations=1)
        # Should be sum of analysis + fix
        assert cost > 0

    def test_multiple_iterations(self):
        """Should scale cost with iterations."""
        cost_1 = estimate_pr_cost(num_iterations=1)
        cost_3 = estimate_pr_cost(num_iterations=3)
        assert cost_3 > cost_1 * 2  # At least more than 2x


class TestFormatCost:
    """Tests for format_cost function."""

    def test_formats_small_cost(self):
        """Should format small costs with more precision."""
        assert format_cost(0.001) == "$0.0010"
        assert format_cost(0.0035) == "$0.0035"

    def test_formats_normal_cost(self):
        """Should format normal costs with 2 decimals."""
        assert format_cost(0.75) == "$0.75"
        assert format_cost(1.50) == "$1.50"


class TestSessionCosts:
    """Tests for SessionCosts class."""

    def test_add_call(self):
        """Should track cumulative costs."""
        costs = SessionCosts(session_id="test-123", pr_number=795)

        costs.add_call(
            CallCost(
                subagent="feedback-analyzer",
                model="haiku",
                input_tokens=1000,
                output_tokens=500,
                input_cost=0.001,
                output_cost=0.0025,
                total_cost=0.0035,
            )
        )

        assert len(costs.calls) == 1
        assert costs.total_input_tokens == 1000
        assert costs.total_output_tokens == 500
        assert costs.total_cost == 0.0035

    def test_save_and_load(self, tmp_path):
        """Should persist and reload costs."""
        costs = SessionCosts(session_id="test-123", pr_number=795)
        costs.add_call(
            CallCost(
                subagent="feedback-analyzer",
                model="haiku",
                input_tokens=1000,
                output_tokens=500,
                input_cost=0.001,
                output_cost=0.0025,
                total_cost=0.0035,
            )
        )

        # Save
        costs.save(tmp_path)

        # Load
        loaded = SessionCosts.load(tmp_path, "test-123")

        assert loaded is not None
        assert loaded.pr_number == 795
        assert len(loaded.calls) == 1
        assert loaded.total_cost == 0.0035


class TestGetCostSummary:
    """Tests for get_cost_summary function."""

    def test_generates_summary(self):
        """Should generate readable summary."""
        costs = SessionCosts(session_id="test-123", pr_number=795)
        costs.add_call(
            CallCost(
                subagent="feedback-analyzer",
                model="haiku",
                input_tokens=1000,
                output_tokens=500,
                input_cost=0.001,
                output_cost=0.0025,
                total_cost=0.0035,
            )
        )

        summary = get_cost_summary(costs)

        assert "PR #795" in summary
        assert "feedback-analyzer" in summary
        assert "$" in summary
