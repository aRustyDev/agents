# src/hashing.py
"""Content hashing utilities for delta detection.

Stage 8 implementation for #796: detect updated comments after addressing.
"""

import hashlib


def hash_content(content: str | None) -> str:
    """Generate SHA-256 hash of content.

    Args:
        content: Text content to hash

    Returns:
        Hash string prefixed with "sha256:"
    """
    if not content:
        return "sha256:empty"

    # Normalize whitespace for consistent hashing
    normalized = " ".join(content.split())
    digest = hashlib.sha256(normalized.encode()).hexdigest()
    return f"sha256:{digest[:16]}"  # Truncate for readability


def hashes_match(hash1: str, hash2: str) -> bool:
    """Compare two content hashes.

    Args:
        hash1: First hash
        hash2: Second hash

    Returns:
        True if hashes match
    """
    return hash1 == hash2


def hash_file(file_path: str) -> str:
    """Generate SHA-256 hash of a file's content.

    Args:
        file_path: Path to file

    Returns:
        Hash string prefixed with "sha256:"
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        return hash_content(content)
    except (OSError, FileNotFoundError):
        return "sha256:error"


def hash_lines(content: str, start_line: int, end_line: int) -> str:
    """Generate hash of specific lines from content.

    Args:
        content: Full text content
        start_line: Starting line (1-indexed)
        end_line: Ending line (1-indexed, inclusive)

    Returns:
        Hash of the specified lines
    """
    lines = content.splitlines()
    if start_line < 1 or end_line > len(lines):
        return "sha256:out_of_range"

    selected = "\n".join(lines[start_line - 1 : end_line])
    return hash_content(selected)
