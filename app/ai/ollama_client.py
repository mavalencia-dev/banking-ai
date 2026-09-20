import ollama
import os
from dotenv import load_dotenv

load_dotenv()

class OllamaClient:

    def __init__(self):
        self.host=os.getenv(
            "OLLAMA_HOST",
            "http://localhost:11434",
        )

        self.model= os.getenv(
            "OLLAMA_MODEL",
            "llama3.2",
        )

        self.client=ollama.Client(
            host=self.host,
        )

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