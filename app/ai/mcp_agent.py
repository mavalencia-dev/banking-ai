import logging
import uuid

from app.ai.mcp_client import BankingMCPClient
from app.ai.ollama_client import OllamaClient
from app.ai.tool_adapter import mcp_tools_to_ollama_tools

logger = logging.getLogger(__name__)


class MCPBankingAgent:

    def __init__(self):
        self.llm = OllamaClient()
        self.mcp = BankingMCPClient()

        # Learning implementation only.
        # This will eventually move to persistent/session storage.
        self.pending_transfer = None

    async def run(self, message: str) -> str:

        await self.mcp.connect()

        try:
            mcp_tools = await self.mcp.list_tools()
            ollama_tools = mcp_tools_to_ollama_tools(mcp_tools)

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a banking assistant.\n"
                        "\n"
                        "Rules:\n"
                        "1. Never invent banking data.\n"
                        "2. Use banking tools when required.\n"
                        "3. Never execute a financial transfer without "
                        "explicit user confirmation.\n"
                        "4. A transfer must first be prepared.\n"
                        "5. Only call confirm_transfer after the user "
                        "explicitly confirms a pending transfer.\n"
                    ),
                },
                {
                    "role": "user",
                    "content": message,
                },
            ]

            response = self.llm.chat(
                messages=messages,
                tools=ollama_tools,
            )

            assistant_message = response["message"]

            tool_calls = assistant_message.get("tool_calls")

            if not tool_calls:
                return assistant_message["content"]

            messages.append(assistant_message)

            for tool_call in tool_calls:

                function = tool_call["function"]

                tool_name = function["name"]
                arguments = function.get("arguments", {})

                logger.info(
                    "Executing MCP tool: %s arguments=%s",
                    tool_name,
                    arguments,
                )

                # ----------------------------------------
                # Financial confirmation protection
                # ----------------------------------------

                if tool_name == "confirm_transfer":

                    if self.pending_transfer is None:
                        return (
                            "There is no pending transfer to confirm."
                        )

                    pending_transfer_id = (
                        self.pending_transfer["transfer_id"]
                    )

                    requested_transfer_id = arguments.get(
                        "transfer_id"
                    )

                    if (
                        requested_transfer_id
                        != pending_transfer_id
                    ):
                        return (
                            "The requested transfer does not match "
                            "the pending confirmation."
                        )

                # ----------------------------------------
                # Execute MCP tool
                # ----------------------------------------

                result = await self.mcp.call_tool(
                    tool_name,
                    arguments,
                )

                # ----------------------------------------
                # Track prepared transfer
                # ----------------------------------------

                if tool_name == "prepare_transfer":

                    if result.content:

                        result_text = result.content[0].text

                        import json

                        result_data = json.loads(result_text)

                        if result_data.get(
                            "confirmation_required"
                        ):
                            self.pending_transfer = {
                                "transfer_id": result_data[
                                    "transfer_id"
                                ],
                                "reference": result_data[
                                    "reference"
                                ],
                            }

                # ----------------------------------------
                # Clear pending transfer after execution
                # ----------------------------------------

                if tool_name == "confirm_transfer":

                    self.pending_transfer = None

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