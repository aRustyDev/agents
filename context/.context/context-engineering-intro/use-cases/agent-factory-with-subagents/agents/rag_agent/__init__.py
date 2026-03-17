"""Semantic Search Agent Package."""

from agent import search_agent
from dependencies import AgentDependencies
from providers import get_embedding_model, get_llm_model

from settings import Settings, load_settings

__version__ = "1.0.0"

__all__ = [
    "AgentDependencies",
    "Settings",
    "get_embedding_model",
    "get_llm_model",
    "load_settings",
    "search_agent",
]
