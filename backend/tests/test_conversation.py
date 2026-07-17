from uuid import uuid4

from backend.agent.agent_factory import create_cadaster_agent


from uuid import uuid4

from backend.agent.assistant import CadasterAssistant


def run_conversation() -> None:
    """Run an interactive terminal conversation with the assistant."""

    print("Creating cadastral assistant...")
    assistant = CadasterAssistant()
    print("Assistant created successfully.\n")

    # One thread ID represents one conversation.
    thread_id = str(uuid4())

    print("Cadaster Assistant")
    print("Type 'exit' to finish the conversation.")
    print(f"Conversation ID: {thread_id}\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("Conversation ended.")
            break

        try:
            response = assistant.chat(
                message=user_input,
                thread_id=thread_id,
            )

            print(f"\nAgent: {response.answer}\n")

        except Exception as exc:
            print(f"\nError: {exc}\n")


if __name__ == "__main__":
    run_conversation()