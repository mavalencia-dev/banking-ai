import asyncio

from app.ai.mcp_agent import MCPBankingAgent


async def main():

    agent = MCPBankingAgent()

    questions = [
        "What is my balance?",
        "Show me my recent transactions.",
        "What is a bank account?",
    ]

    for question in questions:

        print()
        print("=" * 60)
        print(f"USER: {question}")

        response = await agent.run(question)

        print(f"AGENT: {response}")


if __name__ == "__main__":
    asyncio.run(main())