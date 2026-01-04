"""Template rendering for skill-pr-addresser.

Uses chevron (Mustache/Handlebars) for template rendering.
"""

import logging
from pathlib import Path

import chevron


log = logging.getLogger(__name__)


def render_template(templates_dir: Path, template_name: str, data: dict) -> str:
    """Render a Handlebars template with data.

    Args:
        templates_dir: Directory containing templates
        template_name: Name of template (without .hbs extension)
        data: Template context data

    Returns:
        Rendered template string
    """
    template_file = templates_dir / f"{template_name}.hbs"

    if not template_file.exists():
        log.warning(f"Template not found: {template_file}")
        # Return a basic fallback
        return _fallback_template(template_name, data)

    template_content = template_file.read_text()

    try:
        return chevron.render(template_content, data)
    except Exception as e:
        log.error(f"Template render error: {e}")
        return _fallback_template(template_name, data)


def _fallback_template(template_name: str, data: dict) -> str:
    """Generate fallback content when template is missing or fails.

    Args:
        template_name: Name of the template
        data: Template data

    Returns:
        Basic formatted string
    """
    if template_name == "iteration_comment":
        return f"""## Addressing Iteration {data.get('iteration', '?')}

**Feedback items:** {data.get('feedback_count', 0)}
**Addressed:** {data.get('addressed_count', 0)}
**Skipped:** {data.get('skipped_count', 0)}

{_format_commit_info(data)}

---
*Automated by skill-pr-addresser*
"""

    if template_name == "ready_comment":
        reviewers = data.get('reviewers', [])
        mentions = ' '.join(f'@{r}' for r in reviewers)
        return f"""## Ready for Re-Review

All feedback has been addressed. {mentions}

Please re-review this PR when convenient.

---
*Automated by skill-pr-addresser*
"""

    if template_name == "skipped_feedback":
        skipped = data.get('skipped', [])
        items = '\n'.join(f"- **{s.get('id')}**: {s.get('reason')}" for s in skipped)
        return f"""## Feedback Not Addressed

The following items could not be addressed automatically:

{items}

---
*Manual review required*
"""

    # Generic fallback
    return f"Template '{template_name}' rendered with {len(data)} data items."


def _format_commit_info(data: dict) -> str:
    """Format commit information for iteration comment."""
    commit_sha = data.get('commit_sha')
    if not commit_sha:
        return "*No changes committed*"

    commit_short = data.get('commit_short', commit_sha[:8])
    files = data.get('files_modified', [])
    lines_added = data.get('lines_added', 0)
    lines_removed = data.get('lines_removed', 0)

    return f"""**Commit:** `{commit_short}`
**Files modified:** {', '.join(files) if files else 'none'}
**Lines:** +{lines_added} / -{lines_removed}"""


# =============================================================================
# PR Comment Templates (Stage 10)
# =============================================================================


def format_summary_comment(
    pr_number: int,
    iteration: int,
    fix_results: list,
    commit_sha: str,
) -> str:
    """Format the PR summary comment.

    Args:
        pr_number: PR number
        iteration: Current iteration
        fix_results: List of fix results (dicts with group_id, addressed_locations, etc.)
        commit_sha: Commit SHA

    Returns:
        Formatted markdown comment
    """
    total_addressed = sum(
        len(r.get("addressed_locations", [])) if isinstance(r, dict) else len(getattr(r, "addressed_locations", []))
        for r in fix_results
    )
    threads_resolved = sum(
        len(r.get("addressed_thread_ids", [])) if isinstance(r, dict) else len(getattr(r, "addressed_thread_ids", []))
        for r in fix_results
    )

    lines = [
        "## ✅ Feedback Addressed",
        "",
        f"**Iteration {iteration}** | Commit: [`{commit_sha[:7]}`](../commit/{commit_sha})",
        "",
    ]

    if fix_results:
        lines.extend([
            "### Changes Made",
            "",
            "| Action Group | Status | Locations | Threads |",
            "|--------------|--------|-----------|---------|",
        ])

        for result in fix_results:
            if isinstance(result, dict):
                group_id = result.get("group_id", "unknown")
                skipped = result.get("skipped", False)
                failed = result.get("failed", False)
                reason = result.get("reason", "")
                addressed_locs = len(result.get("addressed_locations", []))
                addressed_threads = len(result.get("addressed_thread_ids", []))
            else:
                group_id = getattr(result, "group_id", "unknown")
                skipped = getattr(result, "skipped", False)
                failed = getattr(result, "failed", False)
                reason = getattr(result, "reason", "")
                addressed_locs = len(getattr(result, "addressed_locations", []))
                addressed_threads = len(getattr(result, "addressed_thread_ids", []))

            if skipped:
                status = f"⏭️ Skipped ({reason})"
            elif failed:
                status = "❌ Failed"
            else:
                status = "✅ Complete"

            lines.append(
                f"| {group_id} | {status} | {addressed_locs} | {addressed_threads} |"
            )

        lines.append("")

    lines.extend([
        "---",
        f"📊 **Summary**: {total_addressed} locations addressed, {threads_resolved} threads resolved",
        "",
        "*🤖 Automated by [skill-pr-addresser](https://github.com/aRustyDev/ai)*",
    ])

    return "\n".join(lines)


def format_iteration_limit_comment(
    max_iterations: int,
    resolved_count: int,
) -> str:
    """Format the iteration limit warning comment.

    Args:
        max_iterations: Maximum iterations reached
        resolved_count: Number of threads resolved

    Returns:
        Formatted markdown comment
    """
    return f"""## ⚠️ Iteration Limit Reached

Reached maximum iterations ({max_iterations}). Some feedback may require manual attention.

**Resolved:** {resolved_count} threads
**Remaining:** See unresolved threads above.

If critical feedback remains unaddressed, consider:
1. Running the addresser again with `--max-iterations N`
2. Manually addressing complex feedback
3. Requesting reviewer clarification

---
*🤖 Automated by [skill-pr-addresser](https://github.com/aRustyDev/ai)*
"""


def format_error_comment(
    stage: str,
    error: str,
) -> str:
    """Format an error comment.

    Args:
        stage: Stage that failed
        error: Error message

    Returns:
        Formatted markdown comment
    """
    return f"""## ❌ Processing Failed

The addresser encountered an error during the **{stage}** stage:

```
{error}
```

Please check the logs for more details or try running again.

---
*🤖 Automated by [skill-pr-addresser](https://github.com/aRustyDev/ai)*
"""


def format_no_feedback_comment() -> str:
    """Format a comment when no new feedback is found.

    Returns:
        Formatted markdown comment
    """
    return """## ✅ No New Feedback

All feedback has been addressed or there's nothing new to process.

---
*🤖 Automated by [skill-pr-addresser](https://github.com/aRustyDev/ai)*
"""


def format_partial_progress_comment(
    iteration: int,
    addressed_count: int,
    total_count: int,
    pending_groups: list[str],
) -> str:
    """Format a comment for partial progress.

    Args:
        iteration: Current iteration
        addressed_count: Number of items addressed
        total_count: Total items to address
        pending_groups: List of pending group IDs

    Returns:
        Formatted markdown comment
    """
    pct = (addressed_count / total_count * 100) if total_count > 0 else 0

    lines = [
        "## ⏳ Partial Progress",
        "",
        f"**Iteration {iteration}** | Progress: {addressed_count}/{total_count} ({pct:.0f}%)",
        "",
    ]

    if pending_groups:
        lines.extend([
            "### Pending Groups",
            "",
        ])
        for group_id in pending_groups[:5]:  # Limit to 5
            lines.append(f"- {group_id}")

        if len(pending_groups) > 5:
            lines.append(f"- ... and {len(pending_groups) - 5} more")

        lines.append("")

    lines.extend([
        "The addresser will resume from here on the next run.",
        "",
        "---",
        "*🤖 Automated by [skill-pr-addresser](https://github.com/aRustyDev/ai)*",
    ])

    return "\n".join(lines)
