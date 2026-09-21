import asyncio

from app.ai.mcp_client import BankingMCPClient


async def main():

    client = BankingMCPClient()

    try:
        await client.connect()

        tools = await client.list_tools()

        print("Available MCP tools:")
        for tool in tools:
            print(f"- {tool.name}")

        print()
        print("Calling get_account_balance...")

        result = await client.call_tool(
            "get_account_balance",
            {
                "account_id": 1,
            },
        )

        print(result)

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())