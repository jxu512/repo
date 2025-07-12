from fastmcp import Client
from pydantic import BaseModel

class MCPRequest(BaseModel):
    a: int
    b: int

async def call_mcp_tool(a: int, b: int) -> str:
    """
    Call the FastMCP tool to multiply two numbers.
    
    Args:
        a: First number to multiply
        b: Second number to multiply
        
    Returns:
        A string describing the result of multiplying the two numbers
    """
    request = MCPRequest(a=a, b=b)
    
    async with Client("http://localhost:8181/sse") as client:
        print(f"Client connected: {client.is_connected()}")
        tools = await client.list_tools()
        print("Available tools:", tools)
        response = await client.call_tool("multiply_numbers_tool", {"a": 6, "b": 6})
        response = await client.call_tool("multiply_numbers_tool", request.model_dump())

    return response

if __name__ == "__main__":
    import asyncio
    
    # Example usage
    a = 16
    b = 7
    result = asyncio.run(call_mcp_tool(a, b))
    print(result)  # Output: The product of 6 and 7 is 42
