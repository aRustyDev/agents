from dataclasses import dataclass


@dataclass
class Context:
    """Custom runtime context schema."""

    user_id: str
