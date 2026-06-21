from ollama import chat

MODEL = "qwen3:8b"


def ask_ai(question):
    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": question
            }
        ]
    )

    return response["message"]["content"]
