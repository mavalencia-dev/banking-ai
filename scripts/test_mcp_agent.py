import asyncio

from app.ai.mcp_agent import MCPBankingAgent


async def main():

    agent = MCPBankingAgent()

    print("\n--- STEP 1 ---")

    response = await agent.run(
        "I want to transfer PHP 5000 to Juan."
    )

    print(response)

    print("\n--- STEP 2 ---")

    response = await agent.run(
        "Yes, please confirm the transfer."
    )

    print(response)


if __name__ == "__main__":
    asyncio.run(main())