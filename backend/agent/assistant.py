from dataclasses import dataclass
from typing import Any

from backend.agent.agent_factory import create_cadaster_agent


@dataclass
class ChatResponse:
    """Represents the result of a single chat request."""
    answer: str
    thread_id: str


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

        return ChatResponse(
            answer=self._extract_answer(result),
            thread_id=thread_id,
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