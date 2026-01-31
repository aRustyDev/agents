#!/usr/bin/env python3
"""CLI entry point for skill-pr-addresser."""

import sys
from pathlib import Path

# Add the agent directory to path for imports
agent_dir = Path(__file__).parent
if str(agent_dir) not in sys.path:
    sys.path.insert(0, str(agent_dir))

from src.app import SkillPRAddresser


def main():
    """Run the skill-pr-addresser CLI."""
    with SkillPRAddresser() as app:
        app.run()


if __name__ == "__main__":
    main()
