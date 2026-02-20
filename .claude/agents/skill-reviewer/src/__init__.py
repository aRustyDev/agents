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

from .config import PipelineConfig, load_config, save_config
from .github_projects import (
    ProjectItem,
    find_backlog_issues,
    set_issue_status,
)
from .graphql import (
    execute_query,
    execute_raw_query,
    list_queries,
    load_query,
)
from .headers import (
    AgentHeaders,
    create_agent_headers,
    create_subagent_headers,
    generate_agent_uuid,
    generate_subagent_uuid,
    hash_directory,
)
from .models import AgentSession, Model, Stage, SubagentConfig, SubagentResult
from .orchestrator import Orchestrator
from .pipeline import DeterministicPipeline, PipelineContext
from .templates import TemplateEngine, get_template_engine, render_inline
from .tokens import TokenEstimate, estimate_batch, estimate_tokens
from .worktree import (
    WorktreeInfo,
    create_worktree,
    get_project_id,
    remove_worktree,
    set_project_id,
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
    # Headers
    "AgentHeaders",
    "generate_agent_uuid",
    "generate_subagent_uuid",
    "create_agent_headers",
    "create_subagent_headers",
    "hash_directory",
]
