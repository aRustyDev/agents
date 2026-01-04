"""Feedback analysis and fixing using LLM sub-agents.

This module orchestrates the feedback loop:
1. Analyze feedback using feedback-analyzer sub-agent
2. Fix issues using feedback-fixer sub-agent
3. Track what was addressed and what was skipped
"""

import json
import logging
import os
import re
import select
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from threading import Thread
from queue import Queue, Empty

import yaml

# Add parent directory to path for shared library import
_agents_dir = Path(__file__).parent.parent.parent
if str(_agents_dir) not in sys.path:
    sys.path.insert(0, str(_agents_dir))

from skill_agents_common.models import Model, SubagentConfig, SubagentResult

from .discovery import DiscoveryContext
from .github_pr import Review, Comment
from .tracing import span, record_subagent_call
from .costs import estimate_call_cost, CallCost

log = logging.getLogger(__name__)


@dataclass
class DebugConfig:
    """Global debug configuration for sub-agent execution.

    Set these flags to control how sub-agents are run:
    - interactive: Run in TUI mode (no --print flag)
    - verbose: Stream output in real-time while capturing
    """
    interactive: bool = False
    verbose: bool = False

    @classmethod
    def from_env(cls) -> "DebugConfig":
        """Load config from environment variables."""
        return cls(
            interactive=os.environ.get("SKILL_PR_INTERACTIVE", "").lower() in ("1", "true"),
            verbose=os.environ.get("SKILL_PR_VERBOSE", "").lower() in ("1", "true"),
        )


# Global debug config - can be modified by CLI
debug_config = DebugConfig()


def set_debug_mode(interactive: bool = False, verbose: bool = False) -> None:
    """Set global debug mode for sub-agent execution."""
    global debug_config
    debug_config = DebugConfig(interactive=interactive, verbose=verbose)


@dataclass
class FeedbackItem:
    """A single feedback item extracted from PR reviews (legacy format)."""

    id: str
    type: str  # change_request, suggestion, question, nitpick
    file: str | None
    line: int | None
    description: str
    priority: str  # high, medium, low
    resolved: bool
    suggested_fix: str | None = None


@dataclass
class Location:
    """A specific location in the codebase where feedback applies."""

    file: str
    line: int | None = None
    thread_id: str | None = None


@dataclass
class ActionGroup:
    """A consolidated group of similar feedback items.

    Multiple review comments requesting the same type of change
    are consolidated into a single ActionGroup with multiple locations.
    """

    id: str
    action: str  # move_to_examples, move_to_references, add_section, etc.
    description: str
    locations: list[Location]
    priority: str  # high, medium, low
    type: str  # change_request, suggestion, nitpick

    @property
    def location_count(self) -> int:
        """Number of locations this action applies to."""
        return len(self.locations)

    @property
    def thread_ids(self) -> list[str]:
        """Get all thread IDs for tracking addressed feedback."""
        return [loc.thread_id for loc in self.locations if loc.thread_id]


@dataclass
class ExecutionStep:
    """A step in the execution plan."""

    order: int
    group_id: str
    rationale: str


@dataclass
class AnalysisResult:
    """Result from analyzing PR feedback.

    Contains both the new consolidated format (action_groups) and
    legacy format (feedback_items) for backwards compatibility.
    """

    # New consolidated format
    guidance: list[str] = field(default_factory=list)
    action_groups: list[ActionGroup] = field(default_factory=list)
    execution_plan: list[ExecutionStep] = field(default_factory=list)

    # Metadata
    blocking_reviews: list[str] = field(default_factory=list)
    approved_by: list[str] = field(default_factory=list)
    summary: str = ""

    # Legacy format (populated for backwards compatibility)
    feedback_items: list[FeedbackItem] = field(default_factory=list)

    @property
    def actionable_count(self) -> int:
        """Count of action groups to process."""
        if self.action_groups:
            return len(self.action_groups)
        # Fallback to legacy format
        return sum(
            1
            for item in self.feedback_items
            if not item.resolved and item.type in ("change_request", "suggestion", "nitpick")
        )

    @property
    def has_blocking_feedback(self) -> bool:
        """Whether there's feedback that blocks the PR."""
        if self.blocking_reviews:
            return True
        if self.action_groups:
            return any(g.type == "change_request" for g in self.action_groups)
        # Fallback to legacy format
        return any(
            item.type == "change_request" and not item.resolved
            for item in self.feedback_items
        )

    @property
    def ordered_groups(self) -> list[ActionGroup]:
        """Get action groups in execution order."""
        if not self.execution_plan:
            return self.action_groups

        # Build order map
        order_map = {step.group_id: step.order for step in self.execution_plan}
        return sorted(
            self.action_groups,
            key=lambda g: order_map.get(g.id, 999)
        )

    def get_batch(self, batch_num: int, batch_size: int = 3) -> list[ActionGroup]:
        """Get a batch of action groups for processing.

        Args:
            batch_num: Zero-indexed batch number
            batch_size: Number of groups per batch

        Returns:
            List of ActionGroups for this batch
        """
        groups = self.ordered_groups
        start = batch_num * batch_size
        end = start + batch_size
        return groups[start:end]

    @property
    def batch_count(self) -> int:
        """Number of batches needed (with default batch size of 3)."""
        return (len(self.action_groups) + 2) // 3  # Ceiling division


@dataclass
class FixResult:
    """Result from fixing feedback items."""

    addressed: list[dict] = field(default_factory=list)
    skipped: list[dict] = field(default_factory=list)
    files_modified: list[str] = field(default_factory=list)
    lines_added: int = 0
    lines_removed: int = 0

    @property
    def success_rate(self) -> float:
        """Percentage of items successfully addressed."""
        total = len(self.addressed) + len(self.skipped)
        if total == 0:
            return 1.0
        return len(self.addressed) / total


@dataclass
class SubstantiveCheckResult:
    """Result from checking if pending feedback is substantive."""

    substantive_reviews: list[Review] = field(default_factory=list)
    substantive_comments: list[Comment] = field(default_factory=list)
    not_substantive_ids: list[str] = field(default_factory=list)

    @property
    def has_substantive(self) -> bool:
        """Whether any feedback was found to be substantive."""
        return len(self.substantive_reviews) > 0 or len(self.substantive_comments) > 0


def _stream_output(proc: subprocess.Popen, output_lines: list[str]) -> None:
    """Stream process output to terminal while capturing it."""
    try:
        for line in iter(proc.stdout.readline, ""):
            if not line:
                break
            print(line, end="", flush=True)
            output_lines.append(line)
    except Exception:
        pass


def run_subagent(
    agent_dir: Path,
    name: str,
    task: str,
    working_dir: Path,
    model_override: Model | None = None,
) -> tuple[SubagentResult, CallCost | None]:
    """Run a sub-agent and return result with cost tracking.

    Args:
        agent_dir: Path to the agent directory (skill-pr-addresser)
        name: Sub-agent name (e.g., "feedback-analyzer")
        task: Task description to pass to the sub-agent
        working_dir: Working directory for the sub-agent
        model_override: Optional model to use instead of config default

    Returns:
        Tuple of (SubagentResult with output and metadata, CallCost estimate)

    Debug modes (set via set_debug_mode() or environment variables):
        - interactive: Run in TUI mode for real-time watching
        - verbose: Stream output to terminal while capturing
    """
    start_time = time.time()

    subagent_dir = agent_dir / "subagents" / name
    prompt_file = subagent_dir / "prompt.md"
    config_file = subagent_dir / "config.yml"

    if not prompt_file.exists():
        return SubagentResult(
            name=name,
            model=None,
            output="",
            exit_code=1,
            duration_seconds=0,
            error=f"Sub-agent prompt not found: {prompt_file}",
        ), None

    prompt = prompt_file.read_text()
    config = yaml.safe_load(config_file.read_text()) if config_file.exists() else {}

    # Determine model
    if model_override:
        model = model_override
    elif config.get("model"):
        try:
            model = Model.from_string(config["model"])
            if model is None:
                model = Model.SONNET_4
        except ValueError:
            model = Model.SONNET_4
    else:
        model = Model.SONNET_4

    # Build full prompt
    full_prompt = f"{prompt}\n\n## Current Task\n\n{task}"

    # Build command based on debug mode
    max_turns = config.get("max_turns", 30)  # Prevent infinite loops
    cmd = [
        "claude",
        "--model",
        model.value,
        "--max-turns",
        str(max_turns),
    ]

    # In interactive mode, don't use --print (run TUI)
    # In normal/verbose mode, use --print for programmatic output
    if not debug_config.interactive:
        cmd.extend(["--print", "--output-format", "json"])

    cmd.extend(["-p", full_prompt])

    # Add allowed tools if specified
    allowed_tools = config.get("allowed_tools", [])
    if allowed_tools:
        cmd.extend(["--allowedTools", ",".join(allowed_tools)])

    log.debug(f"Running sub-agent {name} with model {model.value}")
    log.debug(f"Working directory: {working_dir}")

    if debug_config.interactive:
        log.info(f"[INTERACTIVE] Running {name} in TUI mode...")
        log.warning("[INTERACTIVE] Workflow will NOT complete - output cannot be parsed from TUI")
        log.warning("[INTERACTIVE] Use --stream instead for debugging with workflow completion")
    elif debug_config.verbose:
        log.info(f"[VERBOSE] Streaming output from {name}...")

    # Run with tracing
    with span(f"subagent.{name}", {"model": model.value}):
        try:
            # Interactive mode: run TUI, no output capture
            if debug_config.interactive:
                result = subprocess.run(
                    cmd,
                    cwd=working_dir,
                    timeout=config.get("timeout", 600),
                )
                duration = time.time() - start_time

                # In interactive mode, we don't get JSON output
                cost = estimate_call_cost(name, model.value)
                record_subagent_call(
                    name=name,
                    model=model.value,
                    duration_seconds=duration,
                    success=result.returncode == 0,
                    error=None,
                )

                return SubagentResult(
                    name=name,
                    model=model,
                    output="[Interactive mode - output shown in TUI]",
                    exit_code=result.returncode,
                    duration_seconds=duration,
                    parsed_output=None,
                    error=None if result.returncode == 0 else "Check TUI for errors",
                ), cost

            # Verbose mode: stream output while capturing
            elif debug_config.verbose:
                output_lines: list[str] = []
                stderr_lines: list[str] = []

                proc = subprocess.Popen(
                    cmd,
                    cwd=working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,  # Line buffered
                )

                # Stream stdout in a thread
                stdout_thread = Thread(target=_stream_output, args=(proc, output_lines))
                stdout_thread.start()

                # Wait for completion with timeout
                timeout = config.get("timeout", 600)
                try:
                    proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    stdout_thread.join(timeout=1)
                    raise

                stdout_thread.join()
                stderr_output = proc.stderr.read() if proc.stderr else ""

                duration = time.time() - start_time
                output_text = "".join(output_lines)

                # Parse JSON output
                parsed_output = None
                if proc.returncode == 0:
                    try:
                        json_response = json.loads(output_text)
                        output_text = json_response.get("result", output_text)
                        parsed_output = _extract_json(output_text)
                    except json.JSONDecodeError:
                        pass

                cost = estimate_call_cost(name, model.value)
                record_subagent_call(
                    name=name,
                    model=model.value,
                    duration_seconds=duration,
                    success=proc.returncode == 0,
                    error=stderr_output if proc.returncode != 0 else None,
                )

                return SubagentResult(
                    name=name,
                    model=model,
                    output=output_text,
                    exit_code=proc.returncode,
                    duration_seconds=duration,
                    parsed_output=parsed_output,
                    error=stderr_output if proc.returncode != 0 else None,
                ), cost

            # Normal mode: capture output silently
            else:
                result = subprocess.run(
                    cmd,
                    cwd=working_dir,
                    capture_output=True,
                    text=True,
                    timeout=config.get("timeout", 600),
                )

                duration = time.time() - start_time

                # Parse JSON output
                parsed_output = None
                output_text = result.stdout

                if result.returncode == 0:
                    try:
                        # Claude --output-format json wraps in {"result": ...}
                        json_response = json.loads(output_text)
                        output_text = json_response.get("result", output_text)

                        # Try to extract JSON from the response text
                        parsed_output = _extract_json(output_text)
                    except json.JSONDecodeError:
                        pass

                # Estimate cost
                cost = estimate_call_cost(name, model.value)

                # Record for tracing
                record_subagent_call(
                    name=name,
                    model=model.value,
                    duration_seconds=duration,
                    success=result.returncode == 0,
                    error=result.stderr if result.returncode != 0 else None,
                )

                return SubagentResult(
                    name=name,
                    model=model,
                    output=output_text,
                    exit_code=result.returncode,
                    duration_seconds=duration,
                    parsed_output=parsed_output,
                    error=result.stderr if result.returncode != 0 else None,
                ), cost

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            record_subagent_call(
                name=name,
                model=model.value,
                duration_seconds=duration,
                success=False,
                error=f"Timeout after {config.get('timeout', 600)}s",
            )
            return SubagentResult(
                name=name,
                model=model,
                output="",
                exit_code=1,
                duration_seconds=duration,
                error=f"Sub-agent timed out after {config.get('timeout', 600)}s",
            ), None
        except Exception as e:
            duration = time.time() - start_time
            record_subagent_call(
                name=name,
                model=model.value,
                duration_seconds=duration,
                success=False,
                error=str(e),
            )
            return SubagentResult(
                name=name,
                model=model,
                output="",
                exit_code=1,
                duration_seconds=duration,
                error=str(e),
            ), None


def _extract_json(text: str) -> dict | None:
    """Extract JSON object from text, handling markdown code fences and nested objects."""
    if not text:
        return None

    # Try direct parse first
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    # Try to find JSON in markdown code fence
    patterns = [
        r"```json\s*\n(.*?)\n```",
        r"```\s*\n(.*?)\n```",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group(1))
                if isinstance(result, dict):
                    return result
            except (json.JSONDecodeError, IndexError):
                continue

    # Try to find a JSON object by finding balanced braces
    # This handles nested objects properly
    start_idx = text.find("{")
    if start_idx == -1:
        return None

    # Find matching closing brace
    brace_count = 0
    for i, char in enumerate(text[start_idx:], start=start_idx):
        if char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1
            if brace_count == 0:
                # Found complete object
                try:
                    result = json.loads(text[start_idx : i + 1])
                    if isinstance(result, dict):
                        return result
                except json.JSONDecodeError:
                    pass
                break

    return None


def analyze_feedback(
    agent_dir: Path,
    ctx: DiscoveryContext,
) -> tuple[AnalysisResult, CallCost | None]:
    """Analyze feedback using feedback-analyzer sub-agent.

    Args:
        agent_dir: Path to the agent directory
        ctx: Discovery context with PR information

    Returns:
        Tuple of (AnalysisResult with structured feedback items, CallCost estimate)
    """
    log.info("Analyzing feedback...")

    # Build feedback data for the sub-agent
    # Use all_reviews (blocking + actionable + substantive)
    reviews_data = [
        {
            "author": r.author,
            "state": r.state,
            "body": r.body,
            "submitted_at": r.submitted_at,
        }
        for r in ctx.all_reviews
    ]

    # Use all_comments (actionable + substantive)
    comments_data = [
        {
            "id": c.id,
            "author": c.author,
            "body": c.body,
            "created_at": c.created_at,
        }
        for c in ctx.all_comments
    ]

    threads_data = [
        {
            "id": t.id,
            "path": t.path,
            "line": t.line,
            "is_resolved": t.is_resolved,
            "is_outdated": t.is_outdated,
            "author": t.author,
            "comments": t.comments,
        }
        for t in ctx.unresolved_threads
    ]

    task = f"""Analyze the following feedback for PR #{ctx.pr_number}:

## PR Information
- Title: {ctx.pr.title}
- Skill: {ctx.skill_path}
- Review Decision: {ctx.pr.review_decision}

## Reviews
{json.dumps(reviews_data, indent=2)}

## Comments
{json.dumps(comments_data, indent=2)}

## Unresolved Review Threads
{json.dumps(threads_data, indent=2)}

Consolidate similar feedback, separate guidance from actions, and create an execution plan.
"""

    result, cost = run_subagent(agent_dir, "feedback-analyzer", task, Path(ctx.worktree.path))

    if not result.success:
        log.error(f"Feedback analysis failed: {result.error}")
        return AnalysisResult(
            blocking_reviews=[r.author for r in ctx.blocking_reviews],
            summary=f"Analysis failed: {result.error}",
        ), cost

    parsed = result.parsed_output
    if not parsed:
        log.warning("Could not parse feedback analysis output")
        # Log raw output for debugging (truncated)
        raw_output = result.output[:500] if result.output else "(empty)"
        log.debug(f"Raw sub-agent output (first 500 chars): {raw_output}")
        return AnalysisResult(
            blocking_reviews=[r.author for r in ctx.blocking_reviews],
            summary="Could not parse analysis output",
        ), cost

    # Parse the new consolidated format
    action_groups = []
    for group_data in parsed.get("action_groups", []):
        try:
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
        except Exception as e:
            log.warning(f"Failed to parse action group: {e}")

    # Parse execution plan
    execution_plan = []
    for step_data in parsed.get("execution_plan", []):
        try:
            execution_plan.append(
                ExecutionStep(
                    order=step_data.get("order", 999),
                    group_id=step_data.get("group_id", ""),
                    rationale=step_data.get("rationale", ""),
                )
            )
        except Exception as e:
            log.warning(f"Failed to parse execution step: {e}")

    # Also parse legacy format for backwards compatibility
    legacy_items = []
    for item_data in parsed.get("feedback_items", []):
        try:
            legacy_items.append(
                FeedbackItem(
                    id=item_data.get("id", "unknown"),
                    type=item_data.get("type", "suggestion"),
                    file=item_data.get("file"),
                    line=item_data.get("line"),
                    description=item_data.get("description", ""),
                    priority=item_data.get("priority", "medium"),
                    resolved=item_data.get("resolved", False),
                    suggested_fix=item_data.get("suggested_fix"),
                )
            )
        except Exception as e:
            log.warning(f"Failed to parse legacy feedback item: {e}")

    log.info(
        f"Analyzed feedback: {len(action_groups)} action groups, "
        f"{len(parsed.get('guidance', []))} guidance items, "
        f"{len(execution_plan)} execution steps"
    )

    return AnalysisResult(
        guidance=parsed.get("guidance", []),
        action_groups=action_groups,
        execution_plan=execution_plan,
        blocking_reviews=parsed.get("blocking_reviews", []),
        approved_by=parsed.get("approved_by", []),
        summary=parsed.get("summary", ""),
        feedback_items=legacy_items,
    ), cost


def fix_action_group(
    agent_dir: Path,
    ctx: DiscoveryContext,
    group: ActionGroup,
    guidance: list[str],
    model: Model = Model.SONNET_4,
) -> tuple[FixResult, CallCost | None]:
    """Fix a single action group using feedback-fixer sub-agent.

    Args:
        agent_dir: Path to the agent directory
        ctx: Discovery context with worktree path
        group: Action group to fix
        guidance: List of guidance strings to include
        model: Model to use for fixing

    Returns:
        Tuple of (FixResult with addressed and skipped items, CallCost estimate)
    """
    log.info(f"Fixing action group '{group.id}' ({group.action}) with {model.value}...")

    # Build locations data
    locations_data = [
        {
            "file": loc.file,
            "line": loc.line,
            "thread_id": loc.thread_id,
        }
        for loc in group.locations
    ]

    # Build guidance section
    guidance_section = ""
    if guidance:
        guidance_section = "\n## Guidance (apply to all changes)\n"
        for g in guidance:
            guidance_section += f"- {g}\n"

    task = f"""Fix the following action group in the skill:

## Skill Path
{ctx.skill_path}

## Action Group
- **ID**: {group.id}
- **Action**: {group.action}
- **Description**: {group.description}
- **Priority**: {group.priority}

## Locations to Address ({len(group.locations)} locations)
{json.dumps(locations_data, indent=2)}
{guidance_section}
## Instructions
1. Read the relevant skill files
2. Make changes at ALL listed locations to address this action group
3. Stage your changes with `git add`
4. Return a JSON summary of what was done

Work in the current directory (this is a git worktree).
"""

    result, cost = run_subagent(
        agent_dir, "feedback-fixer", task, Path(ctx.worktree.path), model_override=model
    )

    if not result.success:
        log.error(f"Fixing action group '{group.id}' failed: {result.error}")
        return FixResult(
            skipped=[{"id": group.id, "reason": f"Fixer failed: {result.error}"}]
        ), cost

    parsed = result.parsed_output
    if not parsed:
        log.warning(f"Could not parse fix result for group '{group.id}'")
        return FixResult(
            skipped=[{"id": group.id, "reason": "Could not parse fixer output"}]
        ), cost

    return FixResult(
        addressed=parsed.get("addressed", []),
        skipped=parsed.get("skipped", []),
        files_modified=parsed.get("files_modified", []),
        lines_added=parsed.get("lines_added", 0),
        lines_removed=parsed.get("lines_removed", 0),
    ), cost


def fix_batch(
    agent_dir: Path,
    ctx: DiscoveryContext,
    analysis: AnalysisResult,
    batch_num: int = 0,
    batch_size: int = 3,
    model: Model = Model.SONNET_4,
) -> tuple[FixResult, list[CallCost]]:
    """Fix a batch of action groups.

    Args:
        agent_dir: Path to the agent directory
        ctx: Discovery context with worktree path
        analysis: Analyzed feedback with action groups
        batch_num: Which batch to process (0-indexed)
        batch_size: Number of groups per batch
        model: Model to use for fixing

    Returns:
        Tuple of (combined FixResult, list of CallCosts)
    """
    batch = analysis.get_batch(batch_num, batch_size)
    if not batch:
        log.info(f"No action groups in batch {batch_num}")
        return FixResult(), []

    log.info(f"Processing batch {batch_num + 1}/{analysis.batch_count}: {len(batch)} action groups")

    combined_result = FixResult()
    costs: list[CallCost] = []

    for group in batch:
        result, cost = fix_action_group(
            agent_dir, ctx, group, analysis.guidance, model
        )
        if cost:
            costs.append(cost)

        # Combine results
        combined_result.addressed.extend(result.addressed)
        combined_result.skipped.extend(result.skipped)
        combined_result.files_modified.extend(result.files_modified)
        combined_result.lines_added += result.lines_added
        combined_result.lines_removed += result.lines_removed

    # Deduplicate files_modified
    combined_result.files_modified = list(set(combined_result.files_modified))

    return combined_result, costs


def fix_all_batches(
    agent_dir: Path,
    ctx: DiscoveryContext,
    analysis: AnalysisResult,
    batch_size: int = 3,
    model: Model = Model.SONNET_4,
) -> tuple[FixResult, list[CallCost]]:
    """Fix all action groups in batches.

    Args:
        agent_dir: Path to the agent directory
        ctx: Discovery context with worktree path
        analysis: Analyzed feedback with action groups
        batch_size: Number of groups per batch
        model: Model to use for fixing

    Returns:
        Tuple of (combined FixResult from all batches, list of all CallCosts)
    """
    if not analysis.action_groups:
        log.info("No action groups to fix")
        return FixResult(), []

    log.info(
        f"Fixing {len(analysis.action_groups)} action groups in "
        f"{analysis.batch_count} batches (batch_size={batch_size})"
    )

    combined_result = FixResult()
    all_costs: list[CallCost] = []

    for batch_num in range(analysis.batch_count):
        result, costs = fix_batch(
            agent_dir, ctx, analysis, batch_num, batch_size, model
        )
        all_costs.extend(costs)

        # Combine results
        combined_result.addressed.extend(result.addressed)
        combined_result.skipped.extend(result.skipped)
        combined_result.files_modified.extend(result.files_modified)
        combined_result.lines_added += result.lines_added
        combined_result.lines_removed += result.lines_removed

    # Deduplicate files_modified
    combined_result.files_modified = list(set(combined_result.files_modified))

    log.info(
        f"Completed all batches: {len(combined_result.addressed)} addressed, "
        f"{len(combined_result.skipped)} skipped"
    )

    return combined_result, all_costs


def fix_feedback(
    agent_dir: Path,
    ctx: DiscoveryContext,
    analysis: AnalysisResult,
    model: Model = Model.SONNET_4,
) -> tuple[FixResult, CallCost | None]:
    """Fix feedback items using feedback-fixer sub-agent.

    This function supports both the new action_groups format and
    the legacy feedback_items format for backwards compatibility.

    Args:
        agent_dir: Path to the agent directory
        ctx: Discovery context with worktree path
        analysis: Analyzed feedback to fix
        model: Model to use for fixing

    Returns:
        Tuple of (FixResult with addressed and skipped items, CallCost estimate)
    """
    # Use new batched processing if action_groups are available
    if analysis.action_groups:
        result, costs = fix_all_batches(agent_dir, ctx, analysis, model=model)
        # Return first cost for backwards compatibility (or None if empty)
        total_cost = costs[0] if costs else None
        return result, total_cost

    # Legacy path: use feedback_items directly
    log.info(f"Fixing feedback (legacy mode) with {model.value}...")

    # Filter to unresolved, fixable items (includes nitpicks)
    items_to_fix = [
        item
        for item in analysis.feedback_items
        if not item.resolved and item.type in ("change_request", "suggestion", "nitpick")
    ]

    if not items_to_fix:
        log.info("No actionable items to fix")
        return FixResult(), None

    # Build task for sub-agent
    items_data = [
        {
            "id": item.id,
            "type": item.type,
            "file": item.file,
            "line": item.line,
            "description": item.description,
            "priority": item.priority,
            "suggested_fix": item.suggested_fix,
        }
        for item in items_to_fix
    ]

    task = f"""Fix the following feedback items in the skill:

## Skill Path
{ctx.skill_path}

## Feedback Items to Address ({len(items_to_fix)} items)
{json.dumps(items_data, indent=2)}

## Instructions
1. Read the relevant skill files
2. Make changes to address each feedback item
3. Stage your changes with `git add`
4. Return a JSON summary of what was done

Work in the current directory (this is a git worktree).
"""

    result, cost = run_subagent(
        agent_dir, "feedback-fixer", task, Path(ctx.worktree.path), model_override=model
    )

    if not result.success:
        log.error(f"Feedback fixing failed: {result.error}")
        return FixResult(
            skipped=[
                {"id": item.id, "reason": f"Fixer failed: {result.error}"}
                for item in items_to_fix
            ]
        ), cost

    parsed = result.parsed_output
    if not parsed:
        log.warning("Could not parse fix result output")
        return FixResult(
            skipped=[
                {"id": item.id, "reason": "Could not parse fixer output"}
                for item in items_to_fix
            ]
        ), cost

    return FixResult(
        addressed=parsed.get("addressed", []),
        skipped=parsed.get("skipped", []),
        files_modified=parsed.get("files_modified", []),
        lines_added=parsed.get("lines_added", 0),
        lines_removed=parsed.get("lines_removed", 0),
    ), cost


def fix_with_escalation(
    agent_dir: Path,
    ctx: DiscoveryContext,
    analysis: AnalysisResult,
) -> tuple[FixResult, list[CallCost]]:
    """Fix feedback with automatic model escalation.

    Uses Haiku for simple fixes, escalates to Sonnet for complex ones.

    Args:
        agent_dir: Path to the agent directory
        ctx: Discovery context
        analysis: Analyzed feedback

    Returns:
        Tuple of (FixResult from the best attempt, list of CallCosts from all attempts)
    """
    costs: list[CallCost] = []

    # Determine if this is a simple fix case
    is_simple = False

    if analysis.action_groups:
        # New format: check if all groups are low priority nitpicks
        is_simple = (
            len(analysis.action_groups) <= 2
            and all(g.type == "nitpick" or g.priority == "low" for g in analysis.action_groups)
        )
    elif analysis.feedback_items:
        # Legacy format: check for simple nitpicks
        is_simple = (
            analysis.actionable_count <= 2
            and all(
                item.type == "nitpick"
                for item in analysis.feedback_items
                if not item.resolved
            )
        )

    # Try Haiku first for simple fixes
    if is_simple:
        log.info("Using Haiku for simple fixes")
        result, cost = fix_feedback(agent_dir, ctx, analysis, Model.HAIKU_35)
        if cost:
            costs.append(cost)
        if result.addressed and result.success_rate >= 0.8:
            log.info(f"Haiku fixed {len(result.addressed)} items successfully")
            return result, costs
        log.info("Haiku incomplete, escalating to Sonnet")

    # Use Sonnet for complex fixes
    log.info("Using Sonnet for feedback fixes")
    result, cost = fix_feedback(agent_dir, ctx, analysis, Model.SONNET_4)
    if cost:
        costs.append(cost)
    return result, costs


def check_substantive_feedback(
    agent_dir: Path,
    pending_reviews: list[Review],
    pending_comments: list[Comment],
) -> tuple[SubstantiveCheckResult, CallCost | None]:
    """Check if pending feedback is substantive using LLM.

    Evaluates reviews and comments that don't have checkboxes
    to determine if they contain actionable feedback.

    Args:
        agent_dir: Path to the agent directory
        pending_reviews: Reviews needing substantive check
        pending_comments: Comments needing substantive check

    Returns:
        Tuple of (SubstantiveCheckResult, CallCost estimate)
    """
    if not pending_reviews and not pending_comments:
        log.debug("No pending feedback to check")
        return SubstantiveCheckResult(), None

    log.info(
        f"Checking substantive feedback: {len(pending_reviews)} reviews, "
        f"{len(pending_comments)} comments"
    )

    # Build input data for the sub-agent
    items_to_check = []

    for review in pending_reviews:
        items_to_check.append({
            "id": review.id or f"review-{review.author}-{review.submitted_at}",
            "type": "review",
            "author": review.author,
            "state": review.state,
            "body": review.body or "",
        })

    for comment in pending_comments:
        items_to_check.append({
            "id": comment.id,
            "type": "comment",
            "author": comment.author,
            "body": comment.body,
        })

    task = f"""Evaluate whether each of the following feedback items contains substantive actionable feedback.

## Items to Check ({len(items_to_check)} items)
{json.dumps(items_to_check, indent=2)}

Classify each item as either "substantive" (requires code changes) or "not_substantive" (acknowledgement, question, discussion only).
"""

    # Run the substantive checker sub-agent
    # Note: working_dir isn't really needed since we're not doing file ops
    result, cost = run_subagent(
        agent_dir, "substantive-checker", task, agent_dir
    )

    if not result.success:
        log.warning(f"Substantive check failed: {result.error}")
        # On failure, assume all pending items are substantive to be safe
        return SubstantiveCheckResult(
            substantive_reviews=pending_reviews,
            substantive_comments=pending_comments,
        ), cost

    parsed = result.parsed_output
    if not parsed:
        log.warning("Could not parse substantive check output, treating all as substantive")
        return SubstantiveCheckResult(
            substantive_reviews=pending_reviews,
            substantive_comments=pending_comments,
        ), cost

    # Parse results and match back to original objects
    substantive_ids = {
        item.get("id") for item in parsed.get("substantive", [])
    }
    not_substantive_ids = [
        item.get("id") for item in parsed.get("not_substantive", [])
    ]

    # Filter reviews
    substantive_reviews = []
    for review in pending_reviews:
        review_id = review.id or f"review-{review.author}-{review.submitted_at}"
        if review_id in substantive_ids:
            substantive_reviews.append(review)

    # Filter comments
    substantive_comments = []
    for comment in pending_comments:
        if comment.id in substantive_ids:
            substantive_comments.append(comment)

    log.info(
        f"Substantive check: {len(substantive_reviews)} reviews, "
        f"{len(substantive_comments)} comments are actionable"
    )

    return SubstantiveCheckResult(
        substantive_reviews=substantive_reviews,
        substantive_comments=substantive_comments,
        not_substantive_ids=not_substantive_ids,
    ), cost
