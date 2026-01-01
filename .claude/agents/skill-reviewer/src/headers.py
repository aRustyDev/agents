"""Custom HTTP headers for agent and sub-agent tracking.

Sets ANTHROPIC_CUSTOM_HEADERS for Claude API calls and provides
headers for other HTTP requests.

Header format:
- Agent: <uuid>           # All requests (hash of agent code)
- SubAgent: <uuid>        # Sub-agent requests only (hash of sub-agent code)

UUIDs are content-based hashes (UUIDv5) derived from the agent/sub-agent
source code. This means:
- Same code version = same UUID
- Code changes = new UUID
"""

import hashlib
import os
import uuid
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


# Namespace UUID for generating reproducible UUIDs
NAMESPACE_AGENT = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")


def hash_directory(directory: Path, extensions: tuple[str, ...] = (".py", ".md", ".yml", ".yaml")) -> str:
    """Generate a hash of all relevant files in a directory.

    Args:
        directory: Directory to hash
        extensions: File extensions to include

    Returns:
        SHA-256 hash of concatenated file contents
    """
    if not directory.exists():
        return ""

    hasher = hashlib.sha256()

    # Sort for deterministic ordering
    files = sorted(directory.rglob("*"))

    for file_path in files:
        if file_path.is_file() and file_path.suffix in extensions:
            # Include relative path in hash for structure awareness
            rel_path = file_path.relative_to(directory)
            hasher.update(str(rel_path).encode())
            hasher.update(file_path.read_bytes())

    return hasher.hexdigest()


def generate_agent_uuid(agent_dir: Path) -> str:
    """Generate a stable UUID for the main agent based on its code.

    The UUID changes when agent code changes.
    """
    content_hash = hash_directory(agent_dir / "src")
    return str(uuid.uuid5(NAMESPACE_AGENT, f"agent:{content_hash}"))


@lru_cache(maxsize=32)
def generate_subagent_uuid(subagent_dir: Path) -> str:
    """Generate a stable UUID for a sub-agent based on its code.

    The UUID changes when sub-agent code changes.
    Cached to avoid repeated file reads.
    """
    content_hash = hash_directory(subagent_dir)
    return str(uuid.uuid5(NAMESPACE_AGENT, f"subagent:{content_hash}"))


@dataclass
class AgentHeaders:
    """Headers for agent/sub-agent tracking."""
    agent_id: str
    subagent_id: str | None = None

    def to_anthropic_header(self) -> str:
        """Format for ANTHROPIC_CUSTOM_HEADERS env var.

        Format: "Header1: value1, Header2: value2"
        """
        if self.subagent_id:
            return f"Agent: {self.agent_id}, SubAgent: {self.subagent_id}"
        return f"Agent: {self.agent_id}"

    def to_dict(self) -> dict[str, str]:
        """Convert to header dictionary for HTTP requests."""
        headers = {"Agent": self.agent_id}
        if self.subagent_id:
            headers["SubAgent"] = self.subagent_id
        return headers

    def get_env(self) -> dict[str, str]:
        """Get environment variables with ANTHROPIC_CUSTOM_HEADERS set."""
        env = os.environ.copy()
        env["ANTHROPIC_CUSTOM_HEADERS"] = self.to_anthropic_header()
        return env


def create_agent_headers(agent_dir: Path) -> AgentHeaders:
    """Create headers for the main agent (no sub-agent).

    Args:
        agent_dir: Path to the agent directory (contains src/)
    """
    return AgentHeaders(agent_id=generate_agent_uuid(agent_dir))


def create_subagent_headers(agent_dir: Path, subagent_name: str) -> AgentHeaders:
    """Create headers for a sub-agent invocation.

    Args:
        agent_dir: Path to the main agent directory
        subagent_name: Name of the sub-agent (e.g., "validator")
    """
    subagent_dir = agent_dir / "subagents" / subagent_name
    return AgentHeaders(
        agent_id=generate_agent_uuid(agent_dir),
        subagent_id=generate_subagent_uuid(subagent_dir)
    )
