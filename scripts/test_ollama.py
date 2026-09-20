from app.ai.ollama_client import OllamaClient


def main():
    client = OllamaClient()

    response = client.chat(
        "Hello! We are building a banking AI assistant. "
        "Introduce yourself in one sentence."
    )

    print("\nAI Response:")
    print(response)


if __name__ == "__main__":
    main()