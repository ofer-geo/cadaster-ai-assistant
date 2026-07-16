from backend.agent.agent import agent

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "What is the current state of parcel PAR-003?",
            }
        ]
    }
)

final_message = result["messages"][-1]

content = final_message.content

if isinstance(content, str):
    print(content)

elif isinstance(content, list):
    text_parts = [
        block["text"]
        for block in content
        if isinstance(block, dict)
        and block.get("type") == "text"
        and "text" in block
    ]

    print("\n".join(text_parts))

else:
    print(content)