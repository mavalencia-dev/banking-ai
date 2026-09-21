import logging
import re

from app.ai.ollama_client import OllamaClient
from app.ai.tools.registry import execute_tool

logger = logging.getLogger(__name__)


class BankingAgent:

    def __init__(self):
        self.llm = OllamaClient()

    def run(self, message: str) -> str:

        logger.info("Agent request received")

        decision_prompt = f"""
You are a banking assistant.

Available tools:

get_account_balance(account_id)

get_account_transactions(account_id)

The demo checking account ID is 1.
The demo savings account ID is 2.

User request:
{message}

If a tool is required, respond EXACTLY in this format:

TOOL: <tool_name>
ARGUMENT: <account_id>

If no tool is required, respond:

NO_TOOL

Do not invent account IDs.
"""

        decision = self.llm.chat(decision_prompt).strip()

        logger.info(
            "LLM tool decision: %s",
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
            logger.warning(
                "Invalid tool decision: %s",
                decision,
            )

            return (
                "I could not determine which banking "
                "operation is required."
            )

        tool_name = tool_match.group(1)
        account_id = int(argument_match.group(1))

        logger.info(
            "Executing tool=%s account_id=%s",
            tool_name,
            account_id,
        )

        tool_result = execute_tool(
            tool_name,
            account_id,
        )

        logger.info(
            "Tool result: %s",
            tool_result,
        )

        if not tool_result.get("success"):
            return tool_result.get(
                "error",
                "Banking operation failed.",
            )

        final_prompt = f"""
You are a banking assistant.

Answer the user's question using the banking data below.

User:
{message}

Banking data:
{tool_result}

Rules:

- Use only the supplied banking data.
- Do not invent information.
- Be concise.
- Include currency.
- Never expose internal tool names.
"""

        return self.llm.chat(final_prompt)