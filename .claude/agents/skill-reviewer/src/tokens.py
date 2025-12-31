"""Token estimation and cost calculation."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import Model


@dataclass
class TokenEstimate:
    """Estimated token usage for a skill review."""
    skill_path: str

    # File metrics
    total_files: int
    total_lines: int
    total_chars: int

    # Token estimates (chars / 4 is rough approximation)
    estimated_skill_tokens: int
    estimated_reference_tokens: int
    estimated_total_tokens: int

    # Per-stage estimates
    validation_input: int
    validation_output: int
    analysis_input: int
    analysis_output: int
    fixing_input: int
    fixing_output: int

    # Cost estimates by model
    cost_haiku: float
    cost_sonnet: float
    cost_opus: float
    cost_mixed: float  # Using optimal model mix


# Pricing per million tokens (input, output)
MODEL_PRICING = {
    Model.HAIKU_35: (0.25, 1.25),
    Model.SONNET_35: (3.0, 15.0),
    Model.SONNET_4: (3.0, 15.0),
    Model.OPUS_45: (15.0, 75.0),
}


def count_tokens_approx(text: str) -> int:
    """Approximate token count for text.

    Uses a simple heuristic: ~4 chars per token for code/prose.
    More accurate would be to use tiktoken, but this is faster.
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Rough approximation
    return len(text) // 4


def analyze_skill_files(skill_path: Path) -> dict[str, Any]:
    """Analyze skill files to estimate token usage.

    Args:
        skill_path: Path to skill directory

    Returns:
        Dict with file metrics
    """
    metrics = {
        "files": [],
        "total_lines": 0,
        "total_chars": 0,
        "skill_md_lines": 0,
        "skill_md_chars": 0,
        "reference_chars": 0,
    }

    if not skill_path.exists():
        return metrics

    for file_path in skill_path.rglob("*"):
        if not file_path.is_file():
            continue

        # Skip binary files
        if file_path.suffix in [".png", ".jpg", ".gif", ".ico", ".pdf"]:
            continue

        try:
            content = file_path.read_text()
            lines = len(content.splitlines())
            chars = len(content)

            metrics["files"].append({
                "path": str(file_path.relative_to(skill_path)),
                "lines": lines,
                "chars": chars,
                "tokens": count_tokens_approx(content),
            })

            metrics["total_lines"] += lines
            metrics["total_chars"] += chars

            if file_path.name == "SKILL.md":
                metrics["skill_md_lines"] = lines
                metrics["skill_md_chars"] = chars
            elif file_path.suffix == ".md":
                metrics["reference_chars"] += chars

        except (UnicodeDecodeError, IOError):
            continue

    return metrics


def estimate_tokens(skill_path: Path) -> TokenEstimate:
    """Estimate token usage for reviewing a skill.

    Args:
        skill_path: Path to skill directory

    Returns:
        TokenEstimate with breakdown
    """
    metrics = analyze_skill_files(skill_path)

    # Base tokens from skill content
    skill_tokens = count_tokens_approx(" " * metrics["skill_md_chars"])
    reference_tokens = count_tokens_approx(" " * metrics["reference_chars"])

    # System prompts and context overhead (~2k tokens per stage)
    context_overhead = 2000

    # Validation stage: read skill + check structure
    validation_input = skill_tokens + context_overhead
    validation_output = 500  # Structured JSON output

    # Complexity assessment: read validation results
    complexity_input = validation_output + context_overhead
    complexity_output = 300

    # Analysis stage: read all content + validation + complexity
    analysis_input = skill_tokens + reference_tokens + validation_output + complexity_output + context_overhead
    # Output: detailed improvement plan
    analysis_output = min(skill_tokens, 5000)  # Proportional to skill size

    # Fixing stage: read analysis + apply changes
    fixing_input = analysis_output + skill_tokens + context_overhead
    # Output: new/modified content
    fixing_output = max(2000, analysis_output)  # At least match analysis

    # PR creation: read fixes + create PR
    pr_input = fixing_output + context_overhead
    pr_output = 1000

    # GitHub operations (minimal)
    github_input = 500
    github_output = 200

    # Totals
    total_input = (
        validation_input +
        complexity_input +
        analysis_input +
        fixing_input +
        pr_input +
        github_input * 2  # Start and end
    )

    total_output = (
        validation_output +
        complexity_output +
        analysis_output +
        fixing_output +
        pr_output +
        github_output * 2
    )

    # Cost calculations
    def calc_cost(model: Model, input_tokens: int, output_tokens: int) -> float:
        in_rate, out_rate = MODEL_PRICING[model]
        return (input_tokens * in_rate + output_tokens * out_rate) / 1_000_000

    # All Haiku
    cost_haiku = calc_cost(Model.HAIKU_35, total_input, total_output)

    # All Sonnet
    cost_sonnet = calc_cost(Model.SONNET_35, total_input, total_output)

    # All Opus
    cost_opus = calc_cost(Model.OPUS_45, total_input, total_output)

    # Mixed (our actual usage pattern)
    # Haiku: validation, github ops
    haiku_input = validation_input + github_input * 2
    haiku_output = validation_output + github_output * 2

    # Sonnet: complexity, fixing, pr
    sonnet_input = complexity_input + fixing_input + pr_input
    sonnet_output = complexity_output + fixing_output + pr_output

    # Opus: analysis (worst case)
    opus_input = analysis_input
    opus_output = analysis_output

    cost_mixed = (
        calc_cost(Model.HAIKU_35, haiku_input, haiku_output) +
        calc_cost(Model.SONNET_35, sonnet_input, sonnet_output) +
        calc_cost(Model.OPUS_45, opus_input, opus_output)
    )

    return TokenEstimate(
        skill_path=str(skill_path),
        total_files=len(metrics["files"]),
        total_lines=metrics["total_lines"],
        total_chars=metrics["total_chars"],
        estimated_skill_tokens=skill_tokens,
        estimated_reference_tokens=reference_tokens,
        estimated_total_tokens=total_input + total_output,
        validation_input=validation_input,
        validation_output=validation_output,
        analysis_input=analysis_input,
        analysis_output=analysis_output,
        fixing_input=fixing_input,
        fixing_output=fixing_output,
        cost_haiku=cost_haiku,
        cost_sonnet=cost_sonnet,
        cost_opus=cost_opus,
        cost_mixed=cost_mixed,
    )


def estimate_batch(skill_paths: list[Path]) -> dict[str, Any]:
    """Estimate tokens and cost for a batch of skills.

    Args:
        skill_paths: List of skill paths

    Returns:
        Summary with totals and breakdown
    """
    estimates = [estimate_tokens(p) for p in skill_paths]

    return {
        "skill_count": len(estimates),
        "total_tokens": sum(e.estimated_total_tokens for e in estimates),
        "total_cost_haiku": sum(e.cost_haiku for e in estimates),
        "total_cost_sonnet": sum(e.cost_sonnet for e in estimates),
        "total_cost_opus": sum(e.cost_opus for e in estimates),
        "total_cost_mixed": sum(e.cost_mixed for e in estimates),
        "avg_tokens_per_skill": sum(e.estimated_total_tokens for e in estimates) / len(estimates) if estimates else 0,
        "avg_cost_per_skill": sum(e.cost_mixed for e in estimates) / len(estimates) if estimates else 0,
        "estimates": estimates,
    }


def format_estimate(estimate: TokenEstimate) -> str:
    """Format a token estimate for display."""
    return f"""
Skill: {estimate.skill_path}
Files: {estimate.total_files} ({estimate.total_lines} lines)

Token Estimates:
  Skill content: {estimate.estimated_skill_tokens:,}
  References: {estimate.estimated_reference_tokens:,}
  Total (all stages): {estimate.estimated_total_tokens:,}

Per-Stage Breakdown:
  Validation: {estimate.validation_input:,} in / {estimate.validation_output:,} out
  Analysis: {estimate.analysis_input:,} in / {estimate.analysis_output:,} out
  Fixing: {estimate.fixing_input:,} in / {estimate.fixing_output:,} out

Cost Estimates:
  All Haiku: ${estimate.cost_haiku:.4f}
  All Sonnet: ${estimate.cost_sonnet:.4f}
  All Opus: ${estimate.cost_opus:.4f}
  Mixed (recommended): ${estimate.cost_mixed:.4f}
""".strip()
