"""Skill Reviewer Agent - Orchestrated skill review pipeline.

Architecture:
- Deterministic operations (pipeline.py): Issue discovery, status updates,
  worktree management, PR creation, token estimation
- LLM operations (orchestrator.py): Validation, analysis, fixing via sub-agents

The deterministic/LLM split allows:
- Predictable, testable setup/teardown
- Upfront cost estimation before LLM calls
- Clear separation of concerns
"""

from .models import AgentSession, SubagentConfig, SubagentResult, Model, Stage
from .orchestrator import Orchestrator
from .pipeline import DeterministicPipeline, PipelineContext
from .config import PipelineConfig, load_config, save_config
from .tokens import estimate_tokens, TokenEstimate, estimate_batch
from .templates import TemplateEngine, render_inline, get_template_engine
from .github_projects import (
    find_backlog_issues,
    set_issue_status,
    ProjectItem,
)
from .worktree import (
    create_worktree,
    remove_worktree,
    get_project_id,
    set_project_id,
    WorktreeInfo,
)
from .graphql import (
    load_query,
    execute_query,
    execute_raw_query,
    list_queries,
)

__all__ = [
    # Models
    "AgentSession",
    "SubagentConfig",
    "SubagentResult",
    "Model",
    "Stage",
    # Pipeline
    "DeterministicPipeline",
    "PipelineContext",
    "Orchestrator",
    # Config
    "PipelineConfig",
    "load_config",
    "save_config",
    # Tokens
    "estimate_tokens",
    "TokenEstimate",
    "estimate_batch",
    # Templates
    "TemplateEngine",
    "render_inline",
    "get_template_engine",
    # GitHub Projects
    "find_backlog_issues",
    "set_issue_status",
    "ProjectItem",
    # Worktree
    "create_worktree",
    "remove_worktree",
    "get_project_id",
    "set_project_id",
    "WorktreeInfo",
    # GraphQL
    "load_query",
    "execute_query",
    "execute_raw_query",
    "list_queries",
]
