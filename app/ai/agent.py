import asyncio
import logging

from app.ai.mcp_agent import MCPBankingAgent

logger = logging.getLogger(__name__)


class BankingAgent:
    """Compatibility wrapper around the current MCP-backed banking agent."""

    def __init__(self):
        self._agent = MCPBankingAgent()

    def run(self, message: str) -> str:
        logger.info("Agent request received")
        return asyncio.run(self._agent.run(message))