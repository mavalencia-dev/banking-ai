import ollama

from app.config.settings import settings


class OllamaClient:

    def __init__(self):
        self.model = settings.ollama_model

        self.client = ollama.Client(
            host=settings.ollama_host
        )

    def health_check(self):
        self.client.list()

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ):
        kwargs = {
            "model": self.model,
            "messages": messages,
        }

        if tools:
            kwargs["tools"] = tools

        return self.client.chat(**kwargs)