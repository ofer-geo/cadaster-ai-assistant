from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from backend.agent.prompt import SYSTEM_PROMPT
from backend.llm.model import get_model
from backend.tools.parcel_tools import (
    get_current_parcel,
    get_parcel_statistics_tool,
    get_parcel_history_tool,
    get_parcels_by_area,
    get_parcel_overlaps_tool,
)


def create_cadaster_agent():
    """
    Create and return the configured cadastral LangChain agent.

    A new in-memory checkpointer is created for this agent instance.
    Conversations are stored only while the Python process is running.
    """

    model = get_model()

    tools = [
        get_current_parcel,
        get_parcel_statistics_tool,
        get_parcel_history_tool,
        get_parcels_by_area,
        get_parcel_overlaps_tool,
    ]

    checkpointer = InMemorySaver()

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )