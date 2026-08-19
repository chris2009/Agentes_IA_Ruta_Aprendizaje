import asyncio
from fastmcp import Client

client = Client("http://localhost:8000/mcp")
async def call_tool(name: str):
    async with client:
        result = await client.call_tool("SaludoFeliz", {"name": name})
        print(result.content)
        print(result)

asyncio.run(call_tool("Juan"))