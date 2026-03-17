"""Main agent implementation for Semantic Search."""

from dependencies import AgentDependencies
from prompts import MAIN_SYSTEM_PROMPT
from providers import get_llm_model
from pydantic_ai import Agent
from tools import hybrid_search, semantic_search

# Initialize the semantic search agent
search_agent = Agent(
    get_llm_model(),
    deps_type=AgentDependencies,
    system_prompt=MAIN_SYSTEM_PROMPT
)

# Register search tools
search_agent.tool(semantic_search)
search_agent.tool(hybrid_search)
