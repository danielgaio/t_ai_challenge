import asyncio
import json
import sys
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.openai = AsyncOpenAI()  # uses OPENAI_API_KEY from env

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None,
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using OpenAI and available MCP tools"""
        # Start conversation history
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        # Fetch available MCP tools
        response = await self.session.list_tools()
        available_tools = [
            {
                "type": "function",
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
            for tool in response.tools
        ]

        final_text = []

        # First model call
        response = await self.openai.responses.create(
            model="gpt-4.1",
            input=messages,
            tools=available_tools,
            max_output_tokens=1000
        )

        while True:
            tool_called = False

            for item in response.output:
                # Normal assistant text
                if item.type == "message":
                    for content in item.content:
                        if content.type == "output_text":
                            final_text.append(content.text)

                # Tool call
                elif item.type == "function_call":
                    tool_called = True
                    tool_name = item.name
                    tool_args = json.loads(item.arguments)

                    # Execute MCP tool
                    result = await self.session.call_tool(tool_name, tool_args)
                    final_text.append(f"[Tool {tool_name} called with args {tool_args}]")

                    # Append tool call + result to messages
                    messages.append({
                        "role": "assistant",
                        "content": [{
                            "type": "function_call",
                            "id": item.id,
                            "name": tool_name,
                            "arguments": tool_args
                        }]
                    })

                    messages.append({
                        "role": "user",
                        "content": [{
                            "type": "function_call_result",
                            "function_call_id": item.id,
                            "content": result.content[0].text if result.content else ""
                        }]
                    })

                    # Ask model again with tool result
                    # TODO: error here
                    response = await self.openai.responses.create(
                        model="gpt-4.1",
                        input=messages,
                        tools=available_tools,
                        max_output_tokens=1000
                    )
                    break  # process follow-up

            if not tool_called:
                break  # stop if no tools were requested

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

# Running the client:# python mcp/my_client.py path/to/mcp_server.py
# python mcp/my_client.py /Users/danielgaio/dev_projects/GitHub/t_ai_challenge/mcp/weather_server.py