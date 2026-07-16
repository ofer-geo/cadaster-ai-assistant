from langchain.agents import create_agent

from backend.llm.model import get_model
from backend.tools.parcel_tools import get_current_parcel


agent = create_agent(
    model=get_model(),

    tools=[
        get_current_parcel,
    ],

    system_prompt="""
You are an AI cadastral GIS assistant.

You help users explore cadastral information.

Guidelines:
- Always use the available tools to answer questions about parcels.
- Never invent parcel information.
- A parcel can have:
    • one approved current version
    • one in-process version
- Explain the information clearly.
- If no parcel is found, tell the user.
"""
)