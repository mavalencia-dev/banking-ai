import logging

from app.ai.mcp_client import BankingMCPClient
from app.ai.ollama_client import OllamaClient
from app.ai.tool_adapter import (
    mcp_tools_to_ollama_tools,
)

logger = logging.getLogger(__name__)


class MCPBankingAgent:

    def __init__(self):
        self.llm = OllamaClient()
        self.mcp = BankingMCPClient()

    async def run(self, message: str) -> str:

        await self.mcp.connect()

        try:
            mcp_tools = await self.mcp.list_tools()

            ollama_tools = mcp_tools_to_ollama_tools(
                mcp_tools
            )

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a banking assistant. "
                        "Use banking tools when required. "
                        "Never invent banking data."
                    ),
                },
                {
                    "role": "user",
                    "content": message,
                },
            ]

            logger.info(
                "Available MCP tools: %s",
                [
                    tool.name
                    for tool in mcp_tools
                ],
            )

            response = self.llm.chat(
                messages=messages,
                tools=ollama_tools,
            )



            assistant_message = response["message"]

            logger.info(
                "LLM response: %s",
                assistant_message,
            )

            tool_calls = assistant_message.get(
                "tool_calls"
            )

            if not tool_calls:
                return assistant_message["content"]

            messages.append(assistant_message)

            for tool_call in tool_calls:

                function = tool_call["function"]

                tool_name = function["name"]
                arguments = function.get(
                    "arguments",
                    {},
                )

                logger.info(
                    "MCP tool call | name=%s | arguments=%s",
                    tool_name,
                    arguments,
                )

                result = await self.mcp.call_tool(
                    tool_name,
                    arguments,
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_name": tool_name,
                        "content": str(result),
                    }
                )

            final_response = self.llm.chat(
                messages=messages,
                tools=ollama_tools,
            )

            return final_response["message"]["content"]

        finally:
            await self.mcp.close()