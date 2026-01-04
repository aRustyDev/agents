"""Main orchestrator for skill review pipeline."""

import subprocess
import json
import os
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Callable

from .models import (
    AgentSession,
    SubagentConfig,
    SubagentResult,
    Model,
    Stage
)
from .config import PipelineConfig, load_config
from .headers import create_subagent_headers
from .pipeline import DeterministicPipeline, PipelineContext
from .worktree import get_worktree_status


class Orchestrator:
    """Orchestrates the skill review pipeline using specialized sub-agents.

    Architecture:
    - Deterministic operations (GitHub, worktree, PR) use DeterministicPipeline
    - LLM operations (validation, analysis, fixing) use sub-agents via claude CLI
    """

    def __init__(self, agent_dir: Path, config: PipelineConfig | None = None):
        self.agent_dir = agent_dir
        self.subagents_dir = agent_dir / "subagents"
        self.data_dir = agent_dir / "data"
        self.sessions_dir = self.data_dir / "sessions"

        self.data_dir.mkdir(exist_ok=True)
        self.sessions_dir.mkdir(exist_ok=True)

        self.config = config or load_config(self.data_dir / "config.json")
        self.repo_path = self._find_repo_root()

        # Deterministic pipeline for GitHub/git operations
        self.pipeline = DeterministicPipeline(self.config, self.repo_path)

    def _find_repo_root(self) -> Path:
        """Find the git repository root."""
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
        return Path.cwd()

    def load_subagent(self, name: str) -> tuple[str, SubagentConfig]:
        """Load a sub-agent's prompt and config."""
        subagent_dir = self.subagents_dir / name

        prompt = (subagent_dir / "prompt.md").read_text()
        config = SubagentConfig.load(subagent_dir / "config.yml")

        return prompt, config

    def run_subagent(
        self,
        name: str,
        task: str,
        session: AgentSession,
        model_override: Model | None = None,
        working_dir: Path | None = None
    ) -> SubagentResult:
        """Execute a sub-agent with given task.

        Args:
            name: Sub-agent name
            task: Task description/instructions
            session: Current session context
            model_override: Override the sub-agent's default model
            working_dir: Working directory for the sub-agent

        Returns:
            SubagentResult with output and metadata
        """
        prompt, config = self.load_subagent(name)

        # Determine model
        model = model_override or config.get_model()

        # Build full prompt with context
        full_prompt = f"""{prompt}

{session.get_context_for_subagent()}

## Current Task
{task}
"""

        # Build CLI command
        cmd = [
            "claude",
            "--model", model.value,
            "--print",
            "--output-format", "json",  # Get token usage in response
            "-p", full_prompt,
        ]

        if config.allowed_tools:
            cmd.extend(["--allowedTools", ",".join(config.allowed_tools)])

        # Determine working directory
        cwd = working_dir or (
            Path(session.worktree_path) if session.worktree_path
            else self.repo_path
        )

        # Create headers for sub-agent tracking (content-based UUIDs)
        headers = create_subagent_headers(self.agent_dir, name)
        env = headers.get_env()

        # Execute
        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            duration = time.time() - start_time
            raw_output = result.stdout
            error = result.stderr if result.returncode != 0 else None

            # Parse JSON response from claude CLI
            input_tokens = 0
            output_tokens = 0
            actual_cost = 0.0
            text_output = raw_output
            parsed = None

            try:
                response = json.loads(raw_output)
                # Extract text result from JSON response
                text_output = response.get("result", "")

                # Extract token usage
                usage = response.get("usage", {})
                input_tokens = (
                    usage.get("input_tokens", 0) +
                    usage.get("cache_creation_input_tokens", 0) +
                    usage.get("cache_read_input_tokens", 0)
                )
                output_tokens = usage.get("output_tokens", 0)
                actual_cost = response.get("total_cost_usd", 0.0)

                # Try to extract structured JSON from the result text
                parsed = self._extract_json(text_output)

            except json.JSONDecodeError:
                # Fallback: output wasn't JSON, use as-is
                parsed = self._extract_json(raw_output)

            return SubagentResult(
                name=name,
                model=model,
                output=text_output,
                exit_code=result.returncode,
                duration_seconds=duration,
                subagent_id=headers.subagent_id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                parsed_output=parsed,
                error=error
            )

        except subprocess.TimeoutExpired:
            return SubagentResult(
                name=name,
                model=model,
                output="",
                exit_code=-1,
                duration_seconds=600,
                error="Sub-agent timed out after 10 minutes"
            )
        except Exception as e:
            return SubagentResult(
                name=name,
                model=model,
                output="",
                exit_code=-1,
                duration_seconds=time.time() - start_time,
                error=str(e)
            )

    def _extract_json(self, text: str) -> dict | None:
        """Extract JSON from sub-agent output."""
        # Try to find JSON block
        json_patterns = [
            r'```json\s*(.*?)\s*```',  # Markdown code block
            r'\{[^{}]*\}',  # Simple object
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in reversed(matches):  # Prefer last match
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue

        return None

    def _create_pipeline_context(self, session: AgentSession) -> PipelineContext:
        """Create a PipelineContext from an AgentSession."""
        return PipelineContext(
            session_id=session.session_id,
            issue_number=session.issue_number,
            skill_path=session.skill_path,
            repo_owner=self.config.repo_owner,
            repo_name=self.config.repo_name,
            project_number=self.config.project_number,
        )

    def run_pipeline(
        self,
        session: AgentSession,
        stages: list[Stage] | None = None,
        progress_callback: Callable | None = None,
        force_recreate: bool = False,
    ) -> AgentSession:
        """Run the full review pipeline.

        Args:
            session: Session to run pipeline for
            stages: Optional subset of stages to run
            progress_callback: Optional callback(stage, message) for progress updates
            force_recreate: If True, delete existing branch before creating

        Returns:
            Updated session
        """
        all_stages = [
            Stage.SETUP,              # Deterministic: worktree, estimate, status update
            Stage.VALIDATION,         # LLM: validator sub-agent
            Stage.COMPLEXITY_ASSESSMENT,  # LLM: complexity-assessor sub-agent
            Stage.ANALYSIS,           # LLM: analyzer sub-agent
            Stage.FIXING,             # LLM: fixer sub-agent
            Stage.TEARDOWN,           # Deterministic: commit, push, PR, status update
        ]

        stages_to_run = stages or all_stages
        total_stages = len(stages_to_run)

        def emit_progress(stage: Stage, message: str, step: int = 0):
            if progress_callback:
                progress_callback(stage, message, step, total_stages)

        # Create pipeline context
        ctx = self._create_pipeline_context(session)

        try:
            for i, stage in enumerate(stages_to_run, 1):
                emit_progress(stage, f"Starting {stage.value}...", i)

                if stage == Stage.SETUP:
                    self._run_setup(session, ctx, force_recreate)
                elif stage == Stage.VALIDATION:
                    self._run_validation(session)
                elif stage == Stage.COMPLEXITY_ASSESSMENT:
                    self._run_complexity_assessment(session)
                elif stage == Stage.ANALYSIS:
                    self._run_analysis(session)
                elif stage == Stage.FIXING:
                    self._run_fixing(session)
                elif stage == Stage.TEARDOWN:
                    self._run_teardown(session, ctx)

                # Emit completion for this stage
                if session.stage == Stage.FAILED:
                    emit_progress(stage, f"Failed at {stage.value}", i)
                else:
                    emit_progress(stage, f"Completed {stage.value}", i)

                # Save after each stage
                session.save(self.sessions_dir)

                # Check for fatal errors
                if session.stage == Stage.FAILED:
                    break

            if session.stage != Stage.FAILED:
                session.update_stage(Stage.COMPLETE)
                session.save(self.sessions_dir)
                emit_progress(Stage.COMPLETE, "Pipeline complete", total_stages)

        except Exception as e:
            session.add_error(f"Pipeline failed: {e}")
            session.update_stage(Stage.FAILED)
            session.save(self.sessions_dir)
            emit_progress(Stage.FAILED, f"Pipeline error: {e}", 0)

        return session

    def _run_setup(
        self,
        session: AgentSession,
        ctx: PipelineContext,
        force_recreate: bool = False
    ):
        """Run deterministic setup (worktree, status update, token estimate)."""
        session.update_stage(Stage.SETUP)

        # Run deterministic setup
        success = self.pipeline.setup(ctx, force_recreate=force_recreate)

        if not success:
            for error in ctx.errors or []:
                session.add_error(error)
            session.update_stage(Stage.FAILED)
            return

        # Update session with context info
        if ctx.worktree:
            session.worktree_path = str(ctx.worktree.path)
            session.branch_name = ctx.branch_name

        if ctx.token_estimate:
            session.estimated_cost_usd = ctx.token_estimate.cost_mixed

    def _run_validation(self, session: AgentSession):
        """Run skill validation."""
        session.update_stage(Stage.VALIDATION)

        result = self.run_subagent(
            "validator",
            f"Validate skill at {session.skill_path}. Check pillar coverage and token budget.",
            session
        )

        session.add_result(result)

        if not result.success:
            session.add_error(f"Validation failed: {result.error}")

    def _run_complexity_assessment(self, session: AgentSession):
        """Assess complexity to determine analysis depth."""
        session.update_stage(Stage.COMPLEXITY_ASSESSMENT)

        validation_results = session.results.get("validator", {})

        result = self.run_subagent(
            "complexity-assessor",
            f"""Assess complexity based on validation results.

Validation output:
{json.dumps(validation_results, indent=2)}
""",
            session
        )

        session.add_result(result)

    def _run_analysis(self, session: AgentSession):
        """Run deep analysis with model based on complexity."""
        session.update_stage(Stage.ANALYSIS)

        # Determine model from complexity assessment
        complexity_result = session.results.get("complexity-assessor", {})
        parsed = complexity_result.get("parsed", {})
        recommended_model_str = parsed.get("recommended_model", "claude-sonnet-4-20250514")

        model_map = {
            "claude-3-5-haiku-20241022": Model.HAIKU_35,
            "claude-sonnet-4-20250514": Model.SONNET_4,
            "claude-opus-4-5-20251101": Model.OPUS_45,
        }
        model = model_map.get(recommended_model_str, Model.SONNET_4)

        result = self.run_subagent(
            "analyzer",
            f"""Perform deep analysis of skill at {session.skill_path}.

Identify all gaps and create detailed improvement plan.
""",
            session,
            model_override=model
        )

        session.add_result(result)

    def _run_fixing(self, session: AgentSession):
        """Apply fixes based on analysis."""
        session.update_stage(Stage.FIXING)

        analysis_result = session.results.get("analyzer", {})

        result = self.run_subagent(
            "fixer",
            f"""Apply improvements based on analysis.

Analysis plan:
{json.dumps(analysis_result, indent=2)}

Work in the worktree at {session.worktree_path}.
Stage changes but don't commit yet.
""",
            session
        )

        session.add_result(result)

        # Check if any changes were made
        if session.worktree_path:
            status = get_worktree_status(Path(session.worktree_path))
            if status["clean"]:
                session.add_error("No changes were made by fixer")

    def _run_teardown(self, session: AgentSession, ctx: PipelineContext):
        """Run deterministic teardown (commit, push, PR, status update)."""
        session.update_stage(Stage.TEARDOWN)

        # Sync context with session
        if session.worktree_path:
            from .worktree import WorktreeInfo
            ctx.worktree = WorktreeInfo(
                path=Path(session.worktree_path),
                branch=session.branch_name or ""
            )
            ctx.branch_name = session.branch_name

        # Gather results for PR/commit
        results = {
            "description": "improve skill documentation",
            "summary": ["Addressed skill review feedback"],
            "added": [],
            "changed": [],
            "fixed": [],
        }

        # Extract from fixer results if available
        fixer_result = session.results.get("fixer", {})
        if fixer_result.get("parsed"):
            parsed = fixer_result["parsed"]
            results["files_modified"] = len(parsed.get("files_modified", []))
            results["lines_added"] = sum(
                c.get("lines_added", 0)
                for c in parsed.get("changes_summary", [])
            )
            for change in parsed.get("changes_summary", []):
                if change.get("action") == "created":
                    results["added"].append(change.get("description", "New file"))
                elif change.get("action") == "modified":
                    results["changed"].append(change.get("description", "Updated file"))

        # Run deterministic teardown
        success = self.pipeline.teardown(ctx, results, success=True)

        if not success:
            for error in ctx.errors or []:
                session.add_error(error)
            session.update_stage(Stage.FAILED)

        # Update session with PR info
        if ctx.pr_url:
            session.pr_url = ctx.pr_url

    def cleanup_session(self, session: AgentSession):
        """Clean up resources after session completes."""
        if session.worktree_path:
            from .worktree import remove_worktree
            remove_worktree(
                self.repo_path,
                Path(session.worktree_path)
            )
