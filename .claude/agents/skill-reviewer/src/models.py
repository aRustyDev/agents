"""Data models for skill reviewer agent."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
import json


class Model(Enum):
    """Available Claude models."""
    HAIKU_35 = "claude-3-5-haiku-latest"
    SONNET_35 = "claude-3-5-sonnet-latest"
    SONNET_4 = "claude-sonnet-4-20250514"
    OPUS_45 = "claude-opus-4-5-20251101"

    @classmethod
    def from_string(cls, s: str) -> "Model":
        """Parse model from string, handling 'dynamic' specially."""
        if s == "dynamic":
            return None  # Orchestrator will determine
        for model in cls:
            if model.value == s:
                return model
        raise ValueError(f"Unknown model: {s}")


class Stage(Enum):
    """Pipeline stages."""
    INIT = "init"
    SETUP = "setup"                        # Deterministic: worktree, status, estimate
    VALIDATION = "validation"              # LLM: validator sub-agent
    COMPLEXITY_ASSESSMENT = "complexity_assessment"  # LLM: complexity-assessor
    ANALYSIS = "analysis"                  # LLM: analyzer sub-agent
    FIXING = "fixing"                      # LLM: fixer sub-agent
    TEARDOWN = "teardown"                  # Deterministic: commit, push, PR, status
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class SubagentConfig:
    """Configuration for a sub-agent."""
    name: str
    description: str
    model: str  # String to allow "dynamic"
    allowed_tools: list[str]
    included_skills: list[str] = field(default_factory=list)
    max_input_tokens: int = 50000
    max_output_tokens: int = 10000
    output_format: str = "text"
    output_schema: dict | None = None

    @classmethod
    def load(cls, config_path: Path) -> "SubagentConfig":
        """Load config from YAML file."""
        import yaml
        with open(config_path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def get_model(self, override: Model | None = None) -> Model:
        """Get the model to use, with optional override."""
        if override:
            return override
        if self.model == "dynamic":
            return Model.SONNET_35  # Default for dynamic
        return Model.from_string(self.model)


@dataclass
class SubagentResult:
    """Result from a sub-agent execution."""
    name: str
    model: Model
    output: str
    exit_code: int
    duration_seconds: float
    subagent_id: str | None = None  # UUIDv4 for tracking
    input_tokens: int = 0  # If tracking available
    output_tokens: int = 0
    parsed_output: dict | None = None
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.exit_code == 0 and self.error is None


@dataclass
class AgentSession:
    """Shared context across all sub-agents in a pipeline run."""
    session_id: str
    skill_path: str
    issue_number: int
    repo_owner: str = "aRustyDev"
    repo_name: str = "ai"

    # Runtime state
    stage: Stage = Stage.INIT
    worktree_path: str | None = None
    branch_name: str | None = None

    # Timestamps
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str | None = None
    completed_at: str | None = None

    # Accumulated results from sub-agents
    results: dict[str, Any] = field(default_factory=dict)

    # Token tracking
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    estimated_cost_usd: float = 0.0

    # Error tracking
    errors: list[str] = field(default_factory=list)

    def update_stage(self, stage: Stage):
        """Update the current stage and timestamp."""
        self.stage = stage
        self.updated_at = datetime.utcnow().isoformat()

    def add_result(self, result: SubagentResult):
        """Add a sub-agent result to the session."""
        self.results[result.name] = {
            "output": result.output,
            "parsed": result.parsed_output,
            "model": result.model.value if result.model else None,
            "subagent_id": result.subagent_id,
            "duration": result.duration_seconds,
            "success": result.success,
        }
        self.total_input_tokens += result.input_tokens
        self.total_output_tokens += result.output_tokens
        self._update_cost_estimate(result)
        self.updated_at = datetime.utcnow().isoformat()

    def _update_cost_estimate(self, result: SubagentResult):
        """Update estimated cost based on model and tokens."""
        if not result.model:
            return

        # Pricing per million tokens
        pricing = {
            Model.HAIKU_35: (0.25, 1.25),
            Model.SONNET_35: (3.0, 15.0),
            Model.SONNET_4: (3.0, 15.0),
            Model.OPUS_45: (15.0, 75.0),
        }

        if result.model in pricing:
            input_rate, output_rate = pricing[result.model]
            cost = (result.input_tokens * input_rate / 1_000_000 +
                    result.output_tokens * output_rate / 1_000_000)
            self.estimated_cost_usd += cost

    def add_error(self, error: str):
        """Record an error."""
        self.errors.append(f"[{datetime.utcnow().isoformat()}] {error}")

    def save(self, sessions_dir: Path):
        """Save session to disk."""
        session_dir = sessions_dir / self.session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        with open(session_dir / "session.json", "w") as f:
            json.dump(self._to_dict(), f, indent=2)

    def _to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "skill_path": self.skill_path,
            "issue_number": self.issue_number,
            "repo_owner": self.repo_owner,
            "repo_name": self.repo_name,
            "stage": self.stage.value,
            "worktree_path": self.worktree_path,
            "branch_name": self.branch_name,
            "started_at": self.started_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "results": self.results,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "estimated_cost_usd": self.estimated_cost_usd,
            "errors": self.errors,
        }

    @classmethod
    def load(cls, session_file: Path) -> "AgentSession":
        """Load session from disk."""
        with open(session_file) as f:
            data = json.load(f)

        # Convert stage string back to enum
        data["stage"] = Stage(data["stage"])

        return cls(**data)

    def get_context_for_subagent(self) -> str:
        """Generate context string for sub-agents."""
        return f"""## Session Context
- Session ID: {self.session_id}
- Skill: {self.skill_path}
- Issue: #{self.issue_number}
- Repository: {self.repo_owner}/{self.repo_name}
- Current Stage: {self.stage.value}
- Worktree: {self.worktree_path or 'Not created'}
- Branch: {self.branch_name or 'Not created'}

## Previous Results
{json.dumps(self.results, indent=2)}
"""
