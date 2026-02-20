"""GraphQL query loader and executor.

Loads queries from .graphql files in data/graphql/ directory.
"""

import json
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any

# Path to graphql directory relative to this file
GRAPHQL_DIR = Path(__file__).parent.parent / "data" / "graphql"


@lru_cache(maxsize=32)
def load_query(name: str) -> str:
    """Load a GraphQL query from file.

    Args:
        name: Query name (without .graphql extension)

    Returns:
        Query string

    Raises:
        FileNotFoundError: If query file doesn't exist
    """
    query_path = GRAPHQL_DIR / f"{name}.graphql"
    if not query_path.exists():
        raise FileNotFoundError(f"GraphQL query not found: {query_path}")
    return query_path.read_text()


def execute_query(
    name: str, variables: dict[str, Any] | None = None
) -> tuple[bool, dict[str, Any] | None]:
    """Execute a GraphQL query via gh CLI.

    Args:
        name: Query name (without .graphql extension)
        variables: Query variables

    Returns:
        Tuple of (success, data)
    """
    query = load_query(name)
    return execute_raw_query(query, variables)


def execute_raw_query(
    query: str, variables: dict[str, Any] | None = None
) -> tuple[bool, dict[str, Any] | None]:
    """Execute a raw GraphQL query string via gh CLI.

    Args:
        query: GraphQL query string
        variables: Query variables

    Returns:
        Tuple of (success, data)
    """
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]

    if variables:
        for key, value in variables.items():
            if isinstance(value, int):
                cmd.extend(["-F", f"{key}={value}"])
            else:
                cmd.extend(["-f", f"{key}={value}"])

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        return False, None

    try:
        data = json.loads(result.stdout)
        return True, data
    except json.JSONDecodeError:
        return False, None


def list_queries() -> list[str]:
    """List available GraphQL queries.

    Returns:
        List of query names (without .graphql extension)
    """
    if not GRAPHQL_DIR.exists():
        return []
    return [f.stem for f in GRAPHQL_DIR.glob("*.graphql")]
