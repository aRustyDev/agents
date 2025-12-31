import json
import sys
import uuid

from models import AgentSession, Stage
from orchestrator import Orchestrator


def resume_session(
    orchestrator: Orchestrator,
    session_id: str,
    stages: list[Stage] | None = None,
    verbose: bool = False,
) -> AgentSession:
    """Resume an existing session."""
    session_file = orchestrator.sessions_dir / session_id / "session.json"

    if not session_file.exists():
        print(f"Session {session_id} not found", file=sys.stderr)
        sys.exit(1)

    session = AgentSession.load(session_file)

    if verbose:
        print(f"Resuming session {session.session_id}")
        print(f"  Previous stage: {session.stage.value}")

    result = orchestrator.run_pipeline(session, stages)

    return result


def generate_session_id() -> str:
    """Generate a short unique session ID."""
    return str(uuid.uuid4())[:8]


def list_sessions(orchestrator: Orchestrator):
    """List all sessions."""
    sessions_dir = orchestrator.sessions_dir

    if not sessions_dir.exists():
        print("No sessions found")
        return

    sessions = []
    for session_dir in sessions_dir.iterdir():
        if session_dir.is_dir():
            session_file = session_dir / "session.json"
            if session_file.exists():
                with open(session_file) as f:
                    data = json.load(f)
                sessions.append(data)

    if not sessions:
        print("No sessions found")
        return

    # Sort by started_at
    sessions.sort(key=lambda s: s.get("started_at", ""), reverse=True)

    print(f"{'ID':<10} {'Stage':<20} {'Skill':<40} {'Cost':<10}")
    print("-" * 80)

    for s in sessions:
        print(
            f"{s['session_id']:<10} {s['stage']:<20} {s['skill_path']:<40} ${s['estimated_cost_usd']:.4f}"
        )
