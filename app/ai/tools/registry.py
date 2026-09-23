from app.ai.tools.banking_tools import (
    get_account_balance,
    get_account_transactions,
)


TOOLS = {
    "get_account_balance": get_account_balance,
    "get_account_transactions": get_account_transactions,
}


def execute_tool(
    tool_name: str,
    argument: int,
) -> dict:

    tool = TOOLS.get(tool_name)

    if tool is None:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}",
        }

    return tool(argument)