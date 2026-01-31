from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

from tools.user import get_user_location
from tools.weather import get_weather, get_weather_for_location
from utils.context import Context
from utils.response import ResponseFormat

checkpointer = InMemorySaver()

model = init_chat_model(
    "claude-sonnet-4-5-20250929", temperature=0.5, timeout=10, max_tokens=1000
)

# Define system prompt
SYSTEM_PROMPT = """You are an expert weather forecaster, who speaks in puns.

You have access to two tools:

- get_weather_for_location: use this to get the weather for a specific location
- get_user_location: use this to get the user's location

If a user asks you for the weather, make sure you know the location. If you can tell from the question that they mean wherever they are, use the get_user_location tool to find their location."""


agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_weather, get_user_location, get_weather_for_location],
    context_schema=Context,
    response_format=ResponseFormat,
    checkpointer=checkpointer,
    # middleware: Sequence[AgentMiddleware[StateT_co, ContextT]] = (),
    # state_schema: type[AgentState[ResponseT]] | None = None,
    # store: BaseStore | None = None,
    # interrupt_before: list[str] | None = None,
    # interrupt_after: list[str] | None = None,
    # debug: bool = False,
    # name: str | None = None,
    # cache: BaseCache | None = None,
)


# `thread_id` is a unique identifier for a given conversation.
config = {"configurable": {"thread_id": "1"}}


# Run the agent
agent.invoke({"messages": [{"role": "user", "content": "what is the weather in sf"}]})
