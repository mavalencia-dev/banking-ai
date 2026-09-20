from fastapi import FastAPI
from pydantic import BaseModel

from app.ai.ollama_client  import OllamaClient

app = FastAPI(
    title="Banking AI",
    description="AI-powered banking assistant",
    version="0.1.0",
)

ollama_client = OllamaClient()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/health")
def health():
    return {
        "status": "UP"
    }

@app.get("/ready")
def ready():
    try:
        ollama_client.health_check()
        return {
            "status": "READY",
            "ollama": "UP",
        }
    except Exception:
        return {
            "status": "NOT_READY",
            "ollama": "DOWN",
        }

@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    response = ollama_client.chat(request.message)
    return ChatResponse(response=response)