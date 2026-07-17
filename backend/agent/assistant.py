import re
import json
from dataclasses import dataclass
from typing import Any

from backend.agent.agent_factory import create_cadaster_agent
from backend.database.repository import get_parcels_geojson



@dataclass
class ChatResponse:
    """Represents the result of a single chat request."""
    answer: str
    thread_id: str
    parcel_version_ids: list[int]
    geojson: dict[str, Any]


class CadasterAssistant:
    """Application-level interface for the cadastral AI assistant."""

    def __init__(self) -> None:
        self._agent = create_cadaster_agent()

    def chat(self, message: str, thread_id: str) -> ChatResponse:
        """
        Send a message to the assistant within a specific conversation.

        Args:
            message: The user's message.
            thread_id: Identifier used to preserve conversation memory.

        Returns:
            A structured chat response.

        Raises:
            ValueError: If the message or thread ID is empty.
        """

        message = message.strip()
        thread_id = thread_id.strip()

        if not message:
            raise ValueError("Message cannot be empty.")

        if not thread_id:
            raise ValueError("Thread ID cannot be empty.")

        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        result = self._agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": message,
                    }
                ]
            },
            config=config,
        )

        parcel_version_ids = self._extract_parcel_version_ids(result)

        geojson = get_parcels_geojson(parcel_version_ids)

        return ChatResponse(
            answer=self._extract_answer(result),
            thread_id=thread_id,
            parcel_version_ids=parcel_version_ids,
            geojson=geojson,
        )

    @staticmethod
    def _extract_answer(result: dict[str, Any]) -> str:
        """Extract readable text from the final LangChain message."""

        messages = result.get("messages", [])

        if not messages:
            return "The assistant returned no response."

        final_message = messages[-1]
        content = getattr(final_message, "content", "")

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            text_parts: list[str] = []

            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = block.get("text", "")

                    if isinstance(text, str) and text.strip():
                        text_parts.append(text.strip())

                elif isinstance(block, str) and block.strip():
                    text_parts.append(block.strip())

            if text_parts:
                return "\n".join(text_parts)

        return str(content).strip()

    @staticmethod
    def _extract_parcel_version_ids(
        result: dict[str, Any],
    ) -> list[int]:
        """Extract parcel version IDs from the latest agent turn only."""

        messages = result.get("messages", [])
        parcel_version_ids: set[int] = set()

        def inspect_value(value: Any) -> None:
            if isinstance(value, dict):
                for key, nested_value in value.items():
                    if (
                        key in {
                            "parcel_version_id",
                            "parcel_version_id_1",
                            "parcel_version_id_2",
                        }
                        and isinstance(nested_value, int)
                    ):
                        parcel_version_ids.add(nested_value)

                    inspect_value(nested_value)

            elif isinstance(value, list):
                for item in value:
                    inspect_value(item)

        # Find the latest human message.
        latest_human_index = -1

        for index in range(len(messages) - 1, -1, -1):
            if getattr(messages[index], "type", "") == "human":
                latest_human_index = index
                break

        # Only inspect messages generated after the latest user message.
        current_turn_messages = messages[latest_human_index + 1:]

        for message in current_turn_messages:
            if getattr(message, "type", "") != "tool":
                continue

            content = getattr(message, "content", None)

            if isinstance(content, str):
                try:
                    parsed_content = json.loads(content)
                    inspect_value(parsed_content)
                    continue

                except json.JSONDecodeError:
                    pass

                matches = re.findall(
                    r"""['"](?:parcel_version_id|parcel_version_id_1|parcel_version_id_2)['"]\s*:\s*(\d+)""",
                    content,
                )

                for match in matches:
                    parcel_version_ids.add(int(match))

            else:
                inspect_value(content)

        return sorted(parcel_version_ids)