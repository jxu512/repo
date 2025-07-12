#!/usr/bin/env python3
"""
FastMCP Server for Multiplying Two Numbers

This script creates a FastMCP server that exposes a multiply_numbers tool
for integration with Anthropic's Claude via the Model Context Protocol.
Runs on HTTP at localhost:8181
"""

import fastmcp

def multiply_numbers(a: int, b: int) -> int:
    """
    Multiply two numbers together.
    
    Args:
        a: First number to multiply
        b: Second number to multiply
        
    Returns:
        Product of a and b
    """
    return a * b

# Create FastMCP server
app = fastmcp.FastMCP("Multiply Numbers Server")

# Register the multiply_numbers function as a tool
@app.tool()
def multiply_numbers_tool(a: int, b: int) -> str:
    """
    Multiply two numbers together.
    
    Args:
        a: First number to multiply
        b: Second number to multiply
        
    Returns:
        A string describing the result of multiplying the two numbers
    """
    result = multiply_numbers(a, b)
    return f"The product of {a} and {b} is {result}"

if __name__ == "__main__":
    # Run the server on HTTP at localhost:8181 with SSE transport
    app.run(transport="sse", host="localhost", port=8181)
