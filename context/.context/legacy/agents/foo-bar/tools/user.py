from dataclasses import dataclass

from langchain.tools import ToolRuntime, tool

from ..utils.context import Context


@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """Retrieve user information based on user ID."""
    user_id = runtime.context.user_id
    return "Florida" if user_id == "1" else "SF"
