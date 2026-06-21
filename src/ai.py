from ollama import chat
from errors import OllamaError

MODEL = "qwen3:8b"


def ask_ai(question):
    try:
        response = chat(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ]
        )
    except Exception as error:
        raise OllamaError(
            f"Nepodarilo sa spojit s Ollama (model {MODEL}). Skontroluj, ze Ollama bezi."
        ) from error

    return response["message"]["content"]
