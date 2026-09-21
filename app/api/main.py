import logging
from fastapi import FastAPI
from pydantic import BaseModel

from app.ai.ollama_client  import OllamaClient
from app.config.settings import settings
from app.core.logging import configure_logging
from app.api.middleware import CorrelationIdMiddleware
from app.api.routes import accounts, customers

configure_logging()

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="AI-powered banking assistant",
    version=settings.app_version,
)


app.add_middleware(
    CorrelationIdMiddleware
)

app.include_router(customers.router)
app.include_router(accounts.router)

ollama_client = OllamaClient()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/health")
def health():
    logger.info("Health check requested")
    return {
        "status": "UP"
    }

@app.get("/ready")
def ready():
    try:
        ollama_client.health_check()
        logger.info("Readiness check successful")

        return {
            "status": "READY",
            "ollama": "UP",
        }
    except Exception:
        logger.exception("Readiness check failed")
        return {
            "status": "NOT_READY",
            "ollama": "DOWN",
        }

@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    logger.info(
        "Chat request received"
    )

    response = ollama_client.chat(request.message)

    logger.info(
        "Chat response generated"
    )
    return ChatResponse(
        response=response
    )