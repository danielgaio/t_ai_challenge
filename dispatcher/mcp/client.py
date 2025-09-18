import asyncio
import json
import sys
# from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI
from dotenv import load_dotenv


load_dotenv()  # load environment variables from .env


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.sessions = {}  # Dictionary to store multiple sessions
        self.exit_stack = AsyncExitStack()
        self.openai = AsyncOpenAI()  # uses OPENAI_API_KEY from env


    # async def connect_to_server(self, server_script_path: str):
    #     """Connect to an MCP server

    #     Args:
    #         server_script_path: Path to the server script (.py or .js)
    #     """
    #     is_python = server_script_path.endswith(".py")
    #     is_js = server_script_path.endswith(".js")
    #     if not (is_python or is_js):
    #         raise ValueError("Server script must be a .py or .js file")

    #     command = sys.executable if is_python else "node"  # Use current Python interpreter path
    #     server_params = StdioServerParameters(
    #         command=command,
    #         args=[server_script_path],
    #         env=None,
    #     )

    #     stdio_transport = await self.exit_stack.enter_async_context(
    #         stdio_client(server_params)
    #     )
    #     stdio, write = stdio_transport
    #     session = await self.exit_stack.enter_async_context(
    #         ClientSession(stdio, write)
    #     )

    #     await session.initialize()

    #     # List available tools
    #     response = await session.list_tools()
    #     tools = response.tools
        
    #     # Store session with its script path as key
    #     self.sessions[server_script_path] = {
    #         'session': session,
    #         'tools': tools
    #     }
        
    #     print(f"\nConnected to server {server_script_path} with tools:", [tool.name for tool in tools])


    async def connect_to_server(self, server_identifier: str):
        """Connect to an MCP server

        Args:
            server_identifier: Python module path (e.g. "dispatcher.mcp.servers.dispatcher_server")
                            or a JS script path (.js file).
        """
        is_module = not server_identifier.endswith((".py", ".js"))
        is_python = server_identifier.endswith(".py") or is_module
        is_js = server_identifier.endswith(".js")

        if not (is_python or is_js):
            raise ValueError("Server must be a Python module, .py file, or .js file")

        if is_module:
            # Run as Python module
            command = sys.executable
            args = ["-m", server_identifier]
        elif is_python:
            # Run as Python script file
            command = sys.executable
            args = [server_identifier]
        else:
            # Run as Node.js script
            command = "node"
            args = [server_identifier]

        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=None,
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        stdio, write = stdio_transport
        session = await self.exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )

        await session.initialize()

        # List available tools
        response = await session.list_tools()
        tools = response.tools

        # Store session with its identifier (module or file path) as key
        self.sessions[server_identifier] = {
            "session": session,
            "tools": tools,
        }

        print(
            f"\nConnected to server {server_identifier} with tools:",
            [tool.name for tool in tools],
        )


    async def process_query(self, query: str) -> str:
        """Process a query using OpenAI and available MCP tools from all connected servers"""
        # Start conversation history
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        # Collect tools from all connected servers
        available_tools = []
        for server_path, server_info in self.sessions.items():
            for tool in server_info['tools']:
                available_tools.append({
                    "type": "function",
                    "function": {
                        "name": f"{server_path}::{tool.name}",  # Prefix with server path to make tool names unique
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })

        final_text = []

        # First model call
        response = await self.openai.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
            tools=available_tools,
            max_tokens=1000
        )

        while True:
            tool_called = False

            message = response.choices[0].message
            
            # Normal assistant text
            if message.content:
                final_text.append(message.content)
                
            # Tool call
            if message.tool_calls:
                tool_called = True
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # Parse server path and tool name
                    server_path, actual_tool_name = tool_name.split("::", 1)
                    session = self.sessions[server_path]['session']
                    
                    # Execute MCP tool
                    result = await session.call_tool(actual_tool_name, tool_args)
                    final_text.append(f"[Tool {actual_tool_name} from server {server_path} called with args {tool_args}]")

                    # Append tool call + result to messages
                    messages.append({
                        "role": "assistant",
                        "content": f"I'll check that using the {tool_name} tool."
                    })
                    
                    messages.append({
                        "role": "function",
                        "name": tool_name,
                        "content": result.content[0].text if result.content else ""
                    })

                    # Ask model again with tool result
                    response = await self.openai.chat.completions.create(
                        model="gpt-4-1106-preview",
                        messages=messages,
                        tools=available_tools,
                        max_tokens=1000
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
        print("Usage: python client.py <path_to_server_script1> [path_to_server_script2 ...]")
        sys.exit(1)

    client = MCPClient()
    try:
        # Connect to all provided servers
        for server_path in sys.argv[1:]:
            await client.connect_to_server(server_path)
            
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())


# python mcp/client.py /Users/danielgaio/dev_projects/GitHub/t_ai_challenge/mcp/servers/dispatcher_server.py /Users/danielgaio/dev_projects/GitHub/t_ai_challenge/mcp/servers/weather_server.py