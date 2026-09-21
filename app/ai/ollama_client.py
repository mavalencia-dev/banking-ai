import ollama

from app.config.settings import settings


class OllamaClient:

    def __init__(self):
        self.model = settings.ollama_model
        self.client = ollama.Client(
            host=settings.ollama_host,
        )

    def health_check(self):

        self.client.list()


    def chat(self, message: str) -> str:
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user", 
                    "content": message
                }
            ],
        )
        return response["message"]["content"]