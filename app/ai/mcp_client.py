import asyncio
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class BankingMCPClient:

    def __init__(self):
        self.session = None
        self.exit_stack = AsyncExitStack()

    async def connect(self):
        server_params = StdioServerParameters(
            command="uv",
            args=[
                "run",
                "python",
                "-m",
                "app.mcp.server",
            ],
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        self.stdio, self.write = stdio_transport

        self.session = await self.exit_stack.enter_async_context(
            ClientSession(
                self.stdio,
                self.write,
            )
        )

        await self.session.initialize()

    async def list_tools(self):
        if self.session is None:
            raise RuntimeError("MCP client is not connected")

        response = await self.session.list_tools()

        return response.tools

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict,
    ):
        if self.session is None:
            raise RuntimeError("MCP client is not connected")

        return await self.session.call_tool(
            tool_name,
            arguments,
        )

    async def close(self):
        await self.exit_stack.aclose()