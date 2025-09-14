import asyncio
from fastmcp import Client

client = Client("http://127.0.0.1:8000")

async def call_tool(width, height, length, mass):
    async with client:
        result = await client.call_tool("sort", {"width": width, "height": height, "length": length, "mass": mass})
        print(result)

asyncio.run(call_tool(10, 10, 10, 1))