"""Main orchestrator for skill review pipeline."""

import subprocess
import json
import time
import re
from pathlib import Path
from typing import Any

from .models import (
    AgentSession,
    SubagentConfig,
    SubagentResult,
    Model,
    Stage
)
from .config import PipelineConfig, load_config
from .worktree import create_worktree, remove_worktree, get_worktree_status
from .github_ops import (
    update_issue_labels,
    add_issue_comment,
    create_pull_request,
    get_issue_details
)


class Orchestrator:
    """Orchestrates the skill review pipeline using specialized sub-agents."""

    def __init__(self, agent_dir: Path, config: PipelineConfig | None = None):
        self.agent_dir = agent_dir
        self.subagents_dir = agent_dir / "subagents"
        self.data_dir = agent_dir / "data"
        self.sessions_dir = self.data_dir / "sessions"

        self.data_dir.mkdir(exist_ok=True)
        self.sessions_dir.mkdir(exist_ok=True)

        self.config = config or load_config(self.data_dir / "config.json")
        self.repo_path = self._find_repo_root()

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
            "-p", full_prompt,
        ]

        if config.allowed_tools:
            cmd.extend(["--allowedTools", ",".join(config.allowed_tools)])

        # Determine working directory
        cwd = working_dir or (
            Path(session.worktree_path) if session.worktree_path
            else self.repo_path
        )

        # Execute
        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            duration = time.time() - start_time
            output = result.stdout
            error = result.stderr if result.returncode != 0 else None

            # Try to parse JSON output
            parsed = self._extract_json(output)

            return SubagentResult(
                name=name,
                model=model,
                output=output,
                exit_code=result.returncode,
                duration_seconds=duration,
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

    def run_pipeline(
        self,
        session: AgentSession,
        stages: list[Stage] | None = None
    ) -> AgentSession:
        """Run the full review pipeline.

        Args:
            session: Session to run pipeline for
            stages: Optional subset of stages to run

        Returns:
            Updated session
        """
        all_stages = [
            Stage.GITHUB_UPDATE_START,
            Stage.VALIDATION,
            Stage.COMPLEXITY_ASSESSMENT,
            Stage.ANALYSIS,
            Stage.FIXING,
            Stage.PR_CREATION,
            Stage.GITHUB_UPDATE_END,
        ]

        stages_to_run = stages or all_stages

        try:
            # Setup worktree
            if session.worktree_path is None:
                self._setup_worktree(session)

            for stage in stages_to_run:
                if stage == Stage.GITHUB_UPDATE_START:
                    self._run_github_start(session)
                elif stage == Stage.VALIDATION:
                    self._run_validation(session)
                elif stage == Stage.COMPLEXITY_ASSESSMENT:
                    self._run_complexity_assessment(session)
                elif stage == Stage.ANALYSIS:
                    self._run_analysis(session)
                elif stage == Stage.FIXING:
                    self._run_fixing(session)
                elif stage == Stage.PR_CREATION:
                    self._run_pr_creation(session)
                elif stage == Stage.GITHUB_UPDATE_END:
                    self._run_github_end(session)

                # Save after each stage
                session.save(self.sessions_dir)

                # Check for fatal errors
                if session.stage == Stage.FAILED:
                    break

            if session.stage != Stage.FAILED:
                session.update_stage(Stage.COMPLETE)
                session.save(self.sessions_dir)

        except Exception as e:
            session.add_error(f"Pipeline failed: {e}")
            session.update_stage(Stage.FAILED)
            session.save(self.sessions_dir)

        return session

    def _setup_worktree(self, session: AgentSession):
        """Create worktree for the session."""
        skill_name = Path(session.skill_path).name
        branch_name = f"feat/fix-{skill_name}-{session.issue_number}"

        worktree = create_worktree(
            repo_path=self.repo_path,
            worktree_base=Path(self.config.worktree_base),
            branch_name=branch_name,
            base_branch=self.config.base_branch
        )

        session.worktree_path = str(worktree.path)
        session.branch_name = branch_name

    def _run_github_start(self, session: AgentSession):
        """Update GitHub issue to in-progress."""
        session.update_stage(Stage.GITHUB_UPDATE_START)

        result = self.run_subagent(
            "github-updater",
            f"""Set issue #{session.issue_number} to 'in-progress':
1. Add label '{self.config.in_progress_label}'
2. Add comment indicating review has started with session ID {session.session_id}
""",
            session,
            working_dir=self.repo_path
        )

        session.add_result(result)

        if not result.success:
            session.add_error(f"Failed to update GitHub: {result.error}")

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
        recommended_model_str = parsed.get("recommended_model", "claude-3-5-sonnet-latest")

        model_map = {
            "claude-3-5-haiku-latest": Model.HAIKU_35,
            "claude-3-5-sonnet-latest": Model.SONNET_35,
            "claude-opus-4-5-20251101": Model.OPUS_45,
        }
        model = model_map.get(recommended_model_str, Model.SONNET_35)

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

    def _run_pr_creation(self, session: AgentSession):
        """Create PR with changes."""
        session.update_stage(Stage.PR_CREATION)

        fixer_result = session.results.get("fixer", {})

        result = self.run_subagent(
            "pr-creator",
            f"""Create PR for skill improvements.

Changes made:
{json.dumps(fixer_result, indent=2)}

Issue to link: #{session.issue_number}
Branch: {session.branch_name}
""",
            session
        )

        session.add_result(result)

    def _run_github_end(self, session: AgentSession):
        """Update GitHub issue to in-review."""
        session.update_stage(Stage.GITHUB_UPDATE_END)

        pr_result = session.results.get("pr-creator", {})
        pr_url = pr_result.get("parsed", {}).get("pr_url", "")

        result = self.run_subagent(
            "github-updater",
            f"""Update issue #{session.issue_number}:
1. Remove label '{self.config.in_progress_label}'
2. Add label '{self.config.in_review_label}'
3. Add comment with PR link: {pr_url}
4. Add summary of changes made
""",
            session,
            working_dir=self.repo_path
        )

        session.add_result(result)

    def cleanup_session(self, session: AgentSession):
        """Clean up resources after session completes."""
        if session.worktree_path:
            remove_worktree(
                self.repo_path,
                Path(session.worktree_path)
            )
