import logging
import re

from app.ai.mcp_client import BankingMCPClient
from app.ai.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class MCPBankingAgent:

    def __init__(self):
        self.llm = OllamaClient()
        self.mcp = BankingMCPClient()

    async def run(self, message: str) -> str:

        await self.mcp.connect()

        try:
            tools = await self.mcp.list_tools()

            tool_descriptions = "\n".join(
                f"- {tool.name}: {tool.description}"
                for tool in tools
            )

            prompt = f"""
You are a banking assistant.

You have access to these MCP tools:

{tool_descriptions}

The demo checking account ID is 1.
The demo savings account ID is 2.

User request:
{message}

If a tool is required, respond EXACTLY:

TOOL: <tool_name>
ARGUMENT: <integer>

If no tool is required:

NO_TOOL

Do not invent banking information.
"""

            decision = self.llm.chat(prompt).strip()

            logger.info(
                "MCP agent decision: %s",
                decision,
            )

            if decision == "NO_TOOL":
                return self.llm.chat(message)

            tool_match = re.search(
                r"TOOL:\s*(\w+)",
                decision,
            )

            argument_match = re.search(
                r"ARGUMENT:\s*(\d+)",
                decision,
            )

            if not tool_match or not argument_match:
                return (
                    "I could not determine the "
                    "required banking operation."
                )

            tool_name = tool_match.group(1)
            argument = int(argument_match.group(1))

            result = await self.mcp.call_tool(
                tool_name,
                {
                    "account_id": argument,
                },
            )

            final_prompt = f"""
You are a banking assistant.

Answer the user's question using ONLY
the following banking information.

User:
{message}

Banking information:
{result}

Rules:

- Do not invent information.
- Do not expose internal tool names.
- Be concise.
- Include currency where appropriate.
"""

            return self.llm.chat(final_prompt)

        finally:
            await self.mcp.close()