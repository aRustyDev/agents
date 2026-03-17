"""Pytest configuration for skill-pr-addresser tests."""

import sys
from pathlib import Path

# Add the agents directory to path for skill_agents_common imports
_agents_dir = Path(__file__).parent.parent.parent
if str(_agents_dir) not in sys.path:
    sys.path.insert(0, str(_agents_dir))

# Add the agent src directory to path
_agent_dir = Path(__file__).parent.parent
if str(_agent_dir) not in sys.path:
    sys.path.insert(0, str(_agent_dir))
